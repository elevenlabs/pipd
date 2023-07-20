from typing import Callable

from .map import Map


class MapKey(Map):
    def __init__(self, key: str, fn: Callable, **kwargs) -> None:
        def fn_key(x: dict):
            msg = f"MapKey input must be dict with key '{key}'"
            assert isinstance(x, dict) and key in x, msg
            x[key] = fn(x[key])
            return x

        super().__init__(fn_key, **kwargs)
