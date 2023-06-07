import asyncio
import glob
import os
import random
from typing import Iterable, Iterator, Optional, Sequence, TypeVar

from pipd import Function, Pipe

from .read_lines import read_lines
from .write_lines import write_lines

T = TypeVar("T")
U = TypeVar("U")


def watchdir(
    path: str, changes: Sequence[int] = [1]  # default to watchgod.Change.added == 1
) -> Iterator[str]:
    try:
        from watchgod import awatch
    except ImportError:
        raise ImportError("watchgod is required to use watch")
    loop = asyncio.get_event_loop()
    async_generator = awatch(path)
    while True:
        for change, filepath in loop.run_until_complete(async_generator.__anext__()):
            if change in changes:
                yield filepath


class ReadFiles(Function):
    def __init__(
        self,
        cache_filepath: Optional[str] = None,
        watch: bool = False,
        shuffle: bool = False,
    ) -> None:
        self.cache_filepath = cache_filepath
        self.watch = watch
        self.shuffle = shuffle

    def __call__(self, items: Iterable[str]) -> Iterator[str]:
        for filepath in items:
            files = []
            if self.cache_filepath is not None:
                if os.path.exists(self.cache_filepath):
                    files = list(read_lines(filepath=self.cache_filepath))
                else:
                    files = glob.glob(filepath)
                    list(write_lines(files, filepath=self.cache_filepath))
            else:
                files = glob.glob(filepath)

            if self.shuffle:
                random.shuffle(files)

            for file in files:
                yield file
            if self.watch:
                yield from watchdir(os.path.dirname(filepath))


Pipe.add_fn(ReadFiles)
