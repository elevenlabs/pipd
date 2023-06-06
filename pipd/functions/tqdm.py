from typing import Iterable, Iterator, TypeVar

from pipd import Function, Pipe

T = TypeVar("T")


class Tqdm(Function):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, items: Iterable[T]) -> Iterator[T]:
        try:
            from tqdm import tqdm as progressbar
        except ImportError:
            raise ImportError("tqdm is required to use tqdm")

        for item in progressbar(items, *self.args, **self.kwargs):
            yield item


Pipe.add_fn(Tqdm)
