from functools import wraps

from .compat import PY2, ustr, urlparse


def merge_dicts(*dicts, **kwargs):
    result = {}
    for d in dicts:
        result.update(d)
    result.update(kwargs)
    return result


def parse_qs(data):
    result = urlparse.parse_qs(data, True)
    if not PY2:  # pragma: no cover py2
        result = {ustr(k): v for k, v in result.items()}
    return result


def wrap_in(key):
    return lambda val: {key: val}


def make_validator(getter, on_error, top_schema, skip_args=0):
    def validator(*args, **kwargs):
        s = top_schema(*args, **kwargs)
        def decorator(func):
            @wraps(func)
            def inner(*args, **kwargs):
                data = getter(*args[skip_args:], **kwargs)
                try:
                    data = s(data)
                except Exception as e:
                    if on_error:
                        return on_error(e)
                    else:
                        raise
                else:
                    kwargs.update(data)
                    return func(*args, **kwargs)
            return inner
        return decorator
    return validator
