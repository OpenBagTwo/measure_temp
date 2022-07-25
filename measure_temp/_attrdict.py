"""Simple recipe for dicts with keys accessible via attributes"""
from typing import Dict, TypeVar

T = TypeVar("T")


class AttrDict(Dict[str, T]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattr__(self, item: str) -> T:
        return self[item]
