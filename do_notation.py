import inspect
from ast import Assign, Attribute, Call, Load, Store, Lambda, Name, \
   Param, arguments, parse, fix_missing_locations, NodeTransformer, \
   FunctionDef, With
from textwrap import dedent


class RewriteDoBody(NodeTransformer):
    def __init__(self, monad):
        self.monad = monad
        super(RewriteDoBody, self).__init__()
    def visit_Call(self, node):
        self.generic_visit(node)
        if not (isinstance(node.func, Name) and
                node.func.id == 'mreturn'):
            return node
        node.func = Attribute(value=Name(id=self.monad, ctx=Load()), attr='mreturn', ctx=Load())
        return node
    # TODO allow let bindings in do block


def rewrite_with_to_binds(body, monad):
    new_body = []
    # Construct a transformer for this specific monad's mreturn
    rdb = RewriteDoBody(monad)
    # This is the body of the lambda we're about to construct
    last_part = body[-1].value
    # Rewrite mreturn
    rdb.visit(last_part)
    # Iterate in reverse, making each line the into a lambda whose body is the
    # rest of the lines (which are each lambdas), and whose names are the
    # bind assignments.
    for b in reversed(body[:-1]):
        rdb.visit(b)
        if isinstance(b, Assign):
            name = b.targets[0].id
            value = b.value
        else :
            # If there was no assignment to the bind, just use a random name, eek
            name = '__DO_NOT_NAME_A_VARIABLE_THIS_STRING__'
            value = b.value
        # last part = value.bind(lambda name: last_part)
        last_part = Call(func=Attribute(value=value, attr='bind', ctx=Load()),
                         args=[Lambda(args=arguments(args=[Name(id=name, ctx=Param()),],
                                                     vararg=None, kwarg=None, defaults=[]),
                                      body=last_part),],
                         keywords=[], starargs=None, kwargs=None)
    return last_part


class RewriteWithDo(NodeTransformer):
    def visit_With(self, node):
        self.generic_visit(node)
        # Make sure its context expression is a function called "do"
        if not (hasattr(node.context_expr, 'func') and
                node.context_expr.func.id == 'do'):
            return node
        name = node.optional_vars.id
        # The argument of the "do" function is the name of the monad class.
        monad = node.context_expr.args[0].id
        bind_chain = rewrite_with_to_binds(node.body, monad)
        # Assign the result of the bind chain to the name in
        # with do(...) as name:
        return Assign(targets=[Name(id=name, ctx=Store())],
                      value=bind_chain)


def with_do_notation(f):
    # Get the context for the function we're calling this from
    frame = inspect.stack()[1][0]
    # Get the function's source
    src = dedent(inspect.getsource(f))
    # Parse it into an AST
    module = parse(src)
    function_def = module.body[0]
    function_name = function_def.name
    assert(isinstance(module.body[0], FunctionDef))
    # Rewrite any `with do(MyMonadInstance) as my_name:` blocks
    RewriteWithDo().visit(module)
    # Remove the with_do_notation decorator, so it doesn't recurse infinitely
    # when we compile it
    function_def.decorator_list = [d for d in function_def.decorator_list
                               if not (isinstance(d, Name) and d.id=='with_do_notation')]
    # Define the function in the scope it was originally defined, with its
    # original name and new body
    exec(compile(fix_missing_locations(module),
                 filename='<ast>', mode='exec'), frame.f_globals, frame.f_locals)
    # Return the new function
    return eval(function_name, frame.f_globals, frame.f_locals)
