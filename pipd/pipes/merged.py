from random import choices
from typing import Callable, Iterable, Iterator, Optional, Sequence, TypeVar

from pipd import Pipe

T = TypeVar("T")


def merge_iters(
    *iterators: Iterable[T],
    repeat: bool = False,
    repeat_callback: Optional[Callable] = None,
    random: bool = False,
    weights: Optional[Sequence[float]] = None,
) -> Iterator[T]:
    assert weights is None or random, "weights only works with random=True"

    iters = [iter(it) for it in iterators]
    ids = list(range(len(iterators)))

    while True:
        # Choose random iter ids if random=True
        ids_curr = (
            choices(ids, k=len(iterators), weights=weights or [1] * len(iterators))
            if random
            else ids
        )

        for i in ids_curr:
            try:
                yield next(iters[i])
            except StopIteration:
                if repeat:
                    # Reset iterator and add item
                    iters[i] = iter(iterators[i])
                    yield next(iters[i])
                    # Notify callback with pipe index
                    if repeat_callback is not None:
                        repeat_callback(i)
                else:
                    return


class MergedPipe(Pipe):
    def __init__(
        self,
        *pipes,
        repeat: bool = False,
        repeat_callback: Optional[Callable] = None,
        random: bool = False,
        weights: Optional[Sequence[float]] = None,
        **kwargs,
    ):
        super().__init__(
            merge_iters(
                *pipes,
                repeat=repeat,
                repeat_callback=repeat_callback,
                random=random,
                weights=weights,
            ),
            **kwargs,
        )
