from __future__ import annotations

import itertools
import random
import re
from typing import Any, Dict, Iterator, Optional, Sequence, Type


def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def camelcase_to_snakecase(name):
    return re.sub(r"([a-z])([A-Z])", r"\1_\2", name).lower()


class Function:
    def __call__(self, items) -> Iterator:
        raise NotImplementedError


def merge_rand(
    *iterators: Iterator[Any], weights: Optional[Sequence[float]] = None
) -> Iterator[Any]:
    iterator_list = list(iterators)
    weights = [1] * len(iterator_list) if weights is None else weights
    while iterator_list:
        next_iter: Iterator = random.choices(iterator_list, weights=weights)[0]
        try:
            yield next(next_iter)
        except StopIteration:
            break


class Pipe:
    functions: Dict[str, Type[Function]] = {}

    def __init__(self, *items):
        if len(items) == 1 and is_iterable(items[0]):
            items = items[0]
        self.items: Iterator = iter(items)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.items)

    def __getattr__(self, name):
        def method(*args, **kwargs) -> Pipe:
            return self.__class__(self.functions[name](*args, **kwargs)(self.items))  # type: ignore # noqa

        return method

    def __add__(self, other: Pipe) -> Pipe:
        if not isinstance(other, Pipe):
            raise TypeError("Both objects must be of type 'Pipe'")
        return self.__class__(itertools.chain(self.items, other.items))

    def __call__(self):
        return list(self)

    def list(self):
        return list(self)

    @classmethod
    def merge(cls, *pipes, weights: Optional[Sequence[float]] = None) -> Pipe:
        return cls(merge_rand(*pipes, weights=weights))

    @classmethod
    def add_fn(cls, fn: Type[Function], name: Optional[str] = None):
        fn_name = camelcase_to_snakecase(fn.__name__) if name is None else name
        cls.functions[fn_name] = fn
