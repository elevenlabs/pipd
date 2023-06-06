import os
from typing import Callable, Iterable, Iterator, Optional, TypeVar

from pipd import Function, Pipe

from .read_lines import read_lines

T = TypeVar("T")


class FilterCached(Function):
    def __init__(self, filepath: str, key: Optional[Callable] = None) -> None:
        self.filepath = filepath
        self.key = key

    def __call__(self, items: Iterable[T]) -> Iterator[T]:
        cache = (
            set(read_lines(self.filepath)) if os.path.exists(self.filepath) else set()
        )
        with open(self.filepath, "a") as file:
            for item in items:
                value = str(self.key(item) if self.key is not None else item)
                if value not in cache:
                    cache.add(value)
                    file.write(value + "\n")
                    yield item


Pipe.add_fn(FilterCached)
