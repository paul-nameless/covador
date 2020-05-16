import ast
from covador.compat import COROUTINE, ASYNC_AWAIT, PY2


def get_fn_param(name):
    return name[len('__async__'):]


def get_await_param(name):
    return name[len('__await__'):]


class AsyncTransformer(ast.NodeTransformer):
    def __init__(self, params):
        self.params = params

    def visit_FunctionDef(self, node):
        args = node.args.args
        if PY2:  # pragma: no py3 cover
            first_arg_name = args and args[0].id
        else:  # pragma: no py2 cover
            first_arg_name = args and args[0].arg

        if first_arg_name and first_arg_name.startswith('__async__'):
            if self.params[get_fn_param(first_arg_name)]:  # pragma: no py2 cover
                if ASYNC_AWAIT:  # pragma: no coro cover
                    node = ast.AsyncFunctionDef(**vars(node))
                else:  # pragma: no async cover
                    node.decorator_list.append(ast.Name(id='coroutine', ctx=ast.Load(),
                                                        lineno=node.lineno-1, col_offset=node.col_offset))
            args.pop(0)
        return self.generic_visit(node)

    def visit_Call(self, node):
        if type(node.func) is ast.Name and node.func.id.startswith('__await__'):
            if self.params[get_await_param(node.func.id)]:  # pragma: no py2 cover
                if ASYNC_AWAIT:  # pragma: no coro cover
                    return ast.Await(value=node.args[0], lineno=node.lineno, col_offset=node.col_offset)
                else:  # pragma: no async cover
                    return ast.YieldFrom(value=node.args[0], lineno=node.lineno, col_offset=node.col_offset)
            else:
                return node.args[0]
        return node


def get_ast(module):
    fname = module.__file__.rstrip('c')
    with open(fname) as f:
        return fname, ast.parse(f.read(), fname)


def transform(module, params):
    fname, tree = get_ast(module)
    transformed = AsyncTransformer(params).visit(tree)
    if COROUTINE and not ASYNC_AWAIT:  # pragma: no cover
        transformed.body.insert(0, ast.ImportFrom(
            module='asyncio',
            lineno=1,
            col_offset=0,
            names=[ast.alias(name='coroutine', asname=None)]))

    return compile(transformed, fname, 'exec')
