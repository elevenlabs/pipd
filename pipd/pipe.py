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

    def __init__(self, *iterable, handler: Callable = log_traceback_and_continue):
        self._update(*iterable, handler=handler)

    def _update(
        self,
        *iterable,
        function: Optional[Callable] = None,
        handler: Optional[Callable] = None,
    ):
        if len(iterable) == 1 and is_iterable(iterable[0]):
            iterable = iterable[0]
        self._iterable: Iterable = iterable
        self._function = function or identity
        self._handler = handler or log_traceback_and_continue
        return self

    def __iter__(self):
        for item in self._function(iter(self._iterable)):
            try:
                yield item
            except Exception as e:
                self._handler(e)

    def derive(self):
        # This can be overridden to derive to different Pipe subclass
        return Pipe()

    def _derive(
        self,
        *iterable: Iterable,
        function: Optional[Callable] = None,
        handler: Optional[Callable] = None,
    ):
        return self.derive()._update(
            *iterable or [self._iterable],
            function=function or self._function,
            handler=handler or self._handler,
        )

    def __getattr__(self, name):
        def method(*args, **kwargs):
            function = compose(self._function, self._functions[name](*args, **kwargs))
            return self._derive(function=function)

        return method

    def __call__(self, *iterable):
        return self._derive(*iterable)

    def close(self):
        # Necessary to use `yield from` on a Pipe object
        pass

    def list(self):
        return list(self)

    @classmethod
    def add_fn(cls, fn: Type[Function], name: Optional[str] = None):
        fn_name = camelcase_to_snakecase(fn.__name__) if name is None else name
        cls._functions[fn_name] = fn
