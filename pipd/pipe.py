from __future__ import annotations

import re
import traceback
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Type, TypeVar

T = TypeVar("T")


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


def compose(source: Callable, target: Callable):
    def composed(*args):
        return target(source(*args))

    return composed


def unpack_iterable(*iterable: Any) -> Iterable[T]:
    if len(iterable) == 1 and is_iterable(iterable[0]):
        iterable = iterable[0]
    return iterable


class PipeMeta(type):
    def __getattr__(cls, name):
        def method(*args, **kwargs):
            return cls().__getattr__(name)(*args, **kwargs)

        return method


class Pipe(metaclass=PipeMeta):
    _pipes: Dict[str, Type[Pipe]] = {}

    def __init__(self, *iterable, handler: Callable = log_traceback_and_continue):
        self._iterable: Iterable = unpack_iterable(*iterable)
        self._function = identity
        self._handler = handler or log_traceback_and_continue

    def __call__(self, iterable: Iterable[Any]) -> Iterator[Any]:
        return self._function(iterable)

    def __iter__(self):
        for item in self(iter(self._iterable)):
            try:
                yield item
            except Exception as e:
                self._handler(e)

    def new(self):
        return Pipe()

    def __getattr__(self, name):
        def method(*args, **kwargs):
            pipe_fn = self._pipes[name](*args, **kwargs)
            pipe = pipe_fn.new()
            pipe._function = compose(self, pipe_fn)
            pipe._iterable = self._iterable
            pipe._handler = self._handler
            return pipe

        return method

    def close(self):
        # Necessary to use `yield from` on a Pipe object
        pass

    def list(self):
        return list(self)

    @classmethod
    def register(cls, pipe_type: Type[Pipe], name: Optional[str] = None):
        pipe_name = camelcase_to_snakecase(pipe_type.__name__) if name is None else name
        cls._pipes[pipe_name] = pipe_type
