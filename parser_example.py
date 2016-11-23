from do_notation import with_do_notation
import itertools


# instance Monad Parser where
#   return t = Parser $ \s -> [(t, s)]
#   m >>= k  = Parser $ \s -> [(x, y) | (u, v) <- parse m s, (x, y) <- parse (k u) v]
class Parser(object):
    def __init__(self, parse):
        # f :: Iterable -> [(value, Iterable)]
        self.parse = parse
    def bind(self, f):
        return Parser(lambda xs: list(itertools.chain(*[f(u).parse(v) for (u, v) in self.parse(xs)])))
    @staticmethod
    def mreturn(x):
        return Parser(lambda xs: [(x, xs)])


parser_zero = Parser(lambda xs: [])


def parse_either(p1, p2):
    def inner(xs):
        return list(p1.parse(xs)) + list(p2.parse(xs))
    return Parser(inner)


def parse_first(p1, p2):
    def inner(xs):
        combo = list(p1.parse(xs)) + list(p2.parse(xs))
        if len(combo) > 0:
            return [combo[0]]
        return []
    return Parser(inner)


item = Parser(lambda xs: [(xs[0], xs[1:])] if len(xs) > 0 else [])


@with_do_notation
def sat(proposition):
    with do(Parser) as p:
        c = item
        mreturn(c) if proposition(c) else parser_zero
    return p


def char(c):
    return sat(lambda x: x == c)


digit = sat(lambda x: x in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])


@with_do_notation
def parse_string(string):
    if string == "":
        return Parser.mreturn("")
    if len(string) > 0:
        with do(Parser) as x:
            x = char(string[0])
            parse_string(string[1:])
            mreturn(string)
        return x

    return parser_zero


def many(p):
    return parse_first(many1(p), Parser.mreturn(''))


@with_do_notation
def many1(p):
    with do(Parser) as p2:
        x = p
        xs = many(p)
        mreturn(x + xs)
    return p2


def sepby(p, sep):
    return parse_first(sepby1(p, sep), Parser.mreturn(''))


@with_do_notation
def sepby1(p, sep):
    with do(Parser) as throwaway_a_sep:
        sep
        p
    with do(Parser) as p2:
        x = p
        xs = many(throwaway_a_sep)
        mreturn(x + xs)
    return p2


@with_do_notation
def parser_example():
    with do(Parser) as p:
        i = item
        char('b')  # pop a 'b', or fail otherwise
        rest = parse_string('cde')
        mreturn(i+rest)
    # match [('acde', 'fg')]
    print p.parse('abcdefg')
    # match [('xcde', 'fg')]
    print p.parse('xbcdefg')
    # no match
    print p.parse('xbcfefg')
    # match [('aaa', 'bcde')]
    print many(char('a')).parse('aaabcde')
    # match [('12345', 'abc')]
    print sepby1(digit, char(',')).parse('1,2,3,4,5abc')
    # match [('0123456789', ',')]
    print (sepby1(digit,
                  char(','))
           .parse('0,1,2,3,4,5,6,7,8,9,'))
    # RuntimeError: maximum recursion depth exceeded
    # print (sepby1(digit,
    #               char(','))
    #        .parse('0,1,2,3,4,5,6,7,8,9,' * 100))

parser_example()
# [('acde', 'fg')]
# [('xcde', 'fg')]
# []
# [('aaa', 'bcde')]
# [('12345', 'abc')]
# [('0123456789', ',')]
