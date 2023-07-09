from random import choices
from typing import Callable, Optional, Sequence

from pipd import Pipe


def merge_pipes(
    pipes: Sequence[Pipe],
    repeat: bool = False,
    repeat_callback: Optional[Callable] = None,
    random: bool = False,
    weights: Optional[Sequence[float]] = None,
):
    assert weights is None or random, "weights only works with random=True"

    iters = [iter(pipe) for pipe in pipes]
    ids = list(range(len(pipes)))

    while True:
        # Choose random iter ids if random=True
        ids_curr = (
            choices(ids, k=len(pipes), weights=weights or [1] * len(pipes))
            if random
            else ids
        )

        for i in ids_curr:
            try:
                yield next(iters[i])
            except StopIteration:
                if repeat:
                    # Reset iterator and add item
                    iters[i] = iter(pipes[i])
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
        **kwargs
    ):
        super().__init__(
            merge_pipes(
                pipes=pipes,
                repeat=repeat,
                repeat_callback=repeat_callback,
                random=random,
                weights=weights,
            ),
            **kwargs
        )
