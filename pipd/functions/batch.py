from typing import Iterable, Iterator, List, TypeVar

from pipd import Function, Pipe

T = TypeVar("T")


class Batch(Function):
    def __init__(self, size: int, partial: bool = True) -> None:
        self.size = size
        self.partial = partial

    def __call__(self, items: Iterable[T]) -> Iterator[List[T]]:
        batch = []
        for item in items:
            batch.append(item)
            if len(batch) == self.size:
                yield batch
                batch = []
        if batch and self.partial:
            yield batch


Pipe.add_fn(Batch)
