from do_notation import with_do_notation

# instance Monad [] where
#   return x       = Just x
#   (Just x) >>= f = f x
#   Nothing  >>= _ = Nothing
class Maybe(object):
    def __init__(self, just=None):
        self.just = just
    def bind(self, f):
        if self.just is None:
            return Maybe()
        return f(self.just)
    @staticmethod
    def mreturn(x):
        return Maybe(just=x)
    def __repr__(self):
        if self.just is None:
            return 'Nothing'
        return 'Just {}'.format(self.just)


@with_do_notation
def decrement_positives(x):
    with do(Maybe) as y:
        a = Maybe(just=x) if x > 0 else Maybe()
        mreturn(a-1)
    return y


def plain_decrement_positives(x):
    with do(Maybe) as y:
        a = Maybe(just=x) if x > 0 else Maybe()
        mreturn(a-1)
    return y


print decrement_positives(0)  # Nothing
print decrement_positives(1)  # Just 0
print decrement_positives(2)  # Just 1
