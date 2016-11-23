from do_notation import with_do_notation
import itertools

# instance Monad [] where
#   return x = [x]
#   xs >>= f = [y | x <- xs, y <- f x]
class ListMonad(object):
    def __init__(self, lst):
        self.lst = lst
    def bind(self, f):
        return ListMonad(list(itertools.chain(*[f(x).lst for x in self.lst])))
    @staticmethod
    def mreturn(x):
        return ListMonad([x])
    def __repr__(self):
        return 'ListMonad({})'.format(self.lst)


@with_do_notation
def list_example():
    list1 = ListMonad([1,2,3])
    list2 = ListMonad([-1,2])
    with do(ListMonad) as z:
        x = list1
        y = list2
        mreturn(x*y)
    assert(sorted(z.lst) == sorted([x*y for x in list1.lst for y in list2.lst]))
    return z


print list_example()  # ListMonad([-1, 2, -2, 4, -3, 6])
