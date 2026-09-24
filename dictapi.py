"""dictapi.py：对外门面（老接口 put/members 不能改）。"""
from __future__ import annotations

from prefixdict import KeyDict


class Index:
    def __init__(self, width: int = 2):
        self.dict = KeyDict(width)

    def put(self, key: str, value: str = "") -> dict:
        return self.dict.put(key, value)

    def members(self) -> list:
        return self.dict.members()

    def encoded_size(self) -> int:
        return self.dict.encoded_size()

    def encode(self) -> dict:
        return self.dict.encode()

    def decode(self, blob) -> list:
        return self.dict.decode(blob)

    def snapshot(self) -> bytes:
        return self.dict.persist()

    def rebuild(self, blob: bytes = None) -> dict:
        return self.dict.restore(blob)
