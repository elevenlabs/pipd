from __future__ import annotations

import re
import traceback
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Type


def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def log_traceback_and_continue(exception: Exception):
    message = "Exception in Pipe, logging trace and continuing:\n"
    message += "".join(
        traceback.format_exception(type(exception), exception, exception.__traceback__)
    )
    print(message)


def camelcase_to_snakecase(name):
    return re.sub(r"([a-z])([A-Z])", r"\1_\2", name).lower()


def identity(x: Any) -> Any:
    return x


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    def composed(arg: Any) -> Any:
        for func in funcs:
            arg = func(arg)
        return arg

    return composed


class Function:
    def __call__(self, items) -> Iterator:
        raise NotImplementedError


class PipeMeta(type):
    def __getattr__(cls, name):
        def method(*args, **kwargs):
            return cls().__getattr__(name)(*args, **kwargs)

        return method


class Pipe(metaclass=PipeMeta):
    _functions: Dict[str, Type[Function]] = {}

    def __init__(
        self,
        *iterable,
        function: Callable = identity,
        handler: Callable = log_traceback_and_continue,
    ):
        if len(iterable) == 1 and is_iterable(iterable[0]):
            iterable = iterable[0]
        self._iterable: Iterable = iterable
        self._function = function
        self._handler = handler

    def __iter__(self):
        for item in self._function(iter(self._iterable)):
            try:
                yield item
            except Exception as e:
                self._handler(e)

    def _new_pipe(
        self,
        iterable: Optional[Iterable] = None,
        function: Optional[Callable] = None,
        functions: Optional[Dict[str, Type[Function]]] = None,
        handler: Optional[Callable] = None,
    ):
        # This is for composition intead of init so that init can be customized
        pipe = self.__class__()
        pipe._iterable = iterable or self._iterable
        pipe._function = function or self._function
        pipe._functions = functions or self._functions
        pipe._handler = handler or self._handler
        return pipe

    def __getattr__(self, name):
        def method(*args, **kwargs):
            return self._new_pipe(
                function=compose(self._function, self._functions[name](*args, **kwargs))
            )

        return method

    def __call__(self, *iterable):
        if len(iterable) == 1 and is_iterable(iterable[0]):
            iterable = iterable[0]
        return self._new_pipe(iterable=iterable)

    def close(self):
        # Necessary to use `yield from` on a Pipe object
        pass

    def list(self):
        return list(self)

    @classmethod
    def add_fn(cls, fn: Type[Function], name: Optional[str] = None):
        fn_name = camelcase_to_snakecase(fn.__name__) if name is None else name
        cls._functions[fn_name] = fn
