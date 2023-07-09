from __future__ import annotations

import re
import traceback
from typing import Any, Callable, Dict, Iterator, Optional, Type


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
    functions: Dict[str, Type[Function]] = {}

    def __init__(
        self,
        *iterable,
        function: Optional[Callable] = identity,
        handler: Optional[Callable] = log_traceback_and_continue,
    ):
        if len(iterable) == 1 and is_iterable(iterable[0]):
            iterable = iterable[0]
        self.iterable = iterable
        self.function = function
        self.handler = handler

    def __iter__(self):
        for item in self.function(iter(self.iterable)):
            try:
                yield item
            except Exception as e:
                self.handler(e)

    def close(self):
        # Necessary to use `yield from` on a Pipe object
        pass

    def list(self):
        return list(self)

    def __getattr__(self, name):
        def method(*args, **kwargs):
            cls = self.__class__
            function = self.functions[name](*args, **kwargs)
            return cls(self.iterable, function=compose(self.function, function))

        return method

    def __call__(self, *iterable):
        return self.__class__(*iterable, function=self.function)

    @classmethod
    def add_fn(cls, fn: Type[Function], name: Optional[str] = None):
        fn_name = camelcase_to_snakecase(fn.__name__) if name is None else name
        cls.functions[fn_name] = fn
