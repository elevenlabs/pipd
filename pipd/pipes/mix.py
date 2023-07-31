from random import choices
from typing import Callable, Iterable, Iterator, Optional, Sequence, TypeVar

from pipd import Pipe

T = TypeVar("T")


class Mix(Pipe):
    def __init__(
        self,
        *iters,
        repeat: bool = False,
        repeat_callback: Optional[Callable] = None,
        random: bool = False,
        weights: Optional[Sequence[float]] = None,
        **kwargs,
    ):
        assert weights is None or random, "weights only works with random=True"
        self.iters = iters
        self.repeat = repeat
        self.repeat_callback = repeat_callback
        self.random = random
        self.weights = weights

    def __iter__(self):
        return self(*self.iters)

    def __call__(self, *iterators: Iterable[T]) -> Iterator[T]:  # type: ignore
        iters = [iter(it) for it in iterators]
        ids = list(range(len(iterators)))

        while True:
            # Choose random iter ids if random=True
            ids_curr = (
                choices(
                    ids, k=len(iterators), weights=self.weights or [1] * len(iterators)
                )
                if self.random
                else ids
            )

            for i in ids_curr:
                try:
                    yield next(iters[i])
                except StopIteration:
                    if self.repeat:
                        # Reset iterator and add item
                        iters[i] = iter(iterators[i])
                        yield next(iters[i])
                        # Notify callback with pipe index
                        if self.repeat_callback is not None:
                            self.repeat_callback(i)
                    else:
                        return
