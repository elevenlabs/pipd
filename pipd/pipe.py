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


class Chain:
    def __init__(self, *iterables):
        self.iterables = iterables

    def __iter__(self):
        for iterable in self.iterables:
            yield from iterable


def unpack_iterable(*iterable: Any) -> Iterable[T]:
    if len(iterable) == 1 and is_iterable(iterable[0]):
        iterable = iterable[0]
    return iterable


class PipeMeta(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name != "Pipe":
            cls.register()

    def __getattr__(cls, name):
        """Allows to use meta pipe with no iterable: e.g. Pipe.map"""

        def method(*args, **kwargs):
            return cls().__getattr__(name)(*args, **kwargs)

        return method


class Pipe(metaclass=PipeMeta):
    _iterable: Iterable = []
    _function: Callable = identity
    _handler: Callable = log_traceback_and_continue
    _pipes: Dict[str, Type[Pipe]] = {}

    def __init__(self, *iterable, handler: Optional[Callable] = None):
        self._iterable = unpack_iterable(*iterable)
        self._handler = handler or self._handler  # type: ignore
        self._function = identity  # type: ignore

    def __call__(self, iterable: Iterable[Any]) -> Iterator[Any]:
        return self._function(iterable)

    def __iter__(self):
        for item in self(self._iterable):
            try:
                yield item
            except Exception as e:
                self._handler(e)

    def new(self):
        return Pipe()

    def __or__(self, other: Pipe):
        new = other.new()
        new._function = compose(self, other)
        new._iterable = Chain(self._iterable, other._iterable)
        new._handler = self._handler
        return new

    def __getattr__(self, name):
        def method(*args, **kwargs):
            other = self._pipes[name](*args, **kwargs)
            return self | other

        return method

    def close(self):
        # Necessary to use `yield from` on a Pipe object
        pass

    @classmethod
    def register(cls, target: Optional[Type] = None, name: Optional[str] = None):
        pipe_name = name or camelcase_to_snakecase(cls.__name__)
        target = target or Pipe
        target._pipes[pipe_name] = cls
