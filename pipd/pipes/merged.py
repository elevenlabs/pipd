from typing import Callable, Optional, Sequence

from pipd import Pipe


def merge_pipes(
    pipes: Sequence[Pipe],
    repeat: bool = False,
    repeat_callback: Optional[Callable] = None,
):
    iters = [iter(pipe) for pipe in pipes]

    while True:
        items = []

        for it in iters:
            try:
                items.append(next(it))
            except StopIteration:
                if repeat:
                    # Reset iterator and add item
                    idx = iters.index(it)
                    iters[idx] = iter(pipes[idx])
                    items.append(next(iters[idx]))
                    # Notify callback
                    if repeat_callback is not None:
                        repeat_callback(pipes[idx])
                else:
                    return

        yield items


class MergedPipe(Pipe):
    def __init__(
        self,
        *pipes,
        repeat: bool = False,
        repeat_callback: Optional[Callable] = None,
    ):
        super().__init__(merge_pipes(pipes, repeat, repeat_callback))
