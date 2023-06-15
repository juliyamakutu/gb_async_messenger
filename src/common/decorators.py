import inspect
import traceback
from functools import wraps


def log(logger):
    def _log(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(
                f'Вызов функции {func.__name__} c параметрами {args}, {kwargs}'
                f' из модуля {func.__module__}.'
                f' Вызов из функции {traceback.format_stack()[0].strip().split()[-1]}.'
                f' Вызов из функции {inspect.stack()[1][3]}.',
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return _log