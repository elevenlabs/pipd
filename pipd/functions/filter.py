from typing import Callable, Iterable, Iterator, TypeVar

from pipd import Function, Pipe

from .map import Map

T = TypeVar("T")


class Filter(Function):
    def __init__(self, fn: Callable[[T], bool], *args, **kwargs) -> None:
        self.fn = lambda x: (x, fn(x))
        self.args = args
        self.kwargs = kwargs

    def __call__(self, items: Iterable[T]) -> Iterator[T]:
        for item, keep in Map(self.fn, *self.args, **self.kwargs)(items):  # type: ignore
            if keep:  # type: ignore
                yield item  # type: ignore


Pipe.add_fn(Filter)
