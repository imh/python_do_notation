# python_do_notation
A reckless implementation of monadic do notation in python, to see if I can.

In `do_notation.py`, defines a decorator `with_do_notation` that rewrites statements like

```python
with do(Maybe) as y:
        a = Maybe(just=x) if x > 0 else Maybe()
        b = Maybe(just=x*a)
        mreturn(a+b)
```

into

```python
y = (Maybe(just=x) if x > 0 else Maybe()).bind(lambda a:
     Maybe(just=x*a)                     .bind(lambda b:
     Maybe.mreturn(a+b)))
```

**Usage examples:** In a `maybe_examply.py`, `list_example.py`, and `parser_example.py` defines the Maybe monad, a List monad, and a monadic parser, showing usage in each.

Just use it like any other decorator, and you can use this magical new syntax.
All it does is rewrite newlines and assignments into a chain of binds, and changes `mreturn` into the specific mreturn needed for the monad in use within that do block.

```python
@with_do_notation
def decrement_positives(x):
    with do(Maybe) as y:
        a = Maybe(just=x) if x > 0 else Maybe()
        mreturn(a-1)
    return y
```

It's great as long as you don't care much about poor performance, occasional exceptions coming from the lack of tail call optimization in python, and what amounts to a mystery step in your tracebacks:

![mystery step](https://i.imgur.com/EXmmL.jpg)
