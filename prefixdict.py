"""prefixdict.py：前缀压缩字典（基线：普通字典）。"""
from __future__ import annotations


class KeyDict:
    def __init__(self, width: int = 2):
        self.width = width
        self.keys = {}
        self.rebuilds = 0

    def put(self, key: str, value: str = "") -> dict:
        """基线：整键存一份。"""
        self.keys[key] = value
        return {"size": len(self.keys)}

    def members(self) -> list:
        return sorted(self.keys)

    def encoded_size(self) -> int:
        raise NotImplementedError("前缀压缩还没实现")

    def encode(self) -> dict:
        raise NotImplementedError("编码还没实现")

    def decode(self, blob) -> list:
        raise NotImplementedError("解码还没实现")

    def persist(self) -> bytes:
        raise NotImplementedError("快照还没实现")

    def restore(self, blob: bytes = None) -> dict:
        raise NotImplementedError("重启恢复还没实现")

    def stats(self) -> dict:
        return {"size": len(self.keys), "width": self.width, "rebuilds": self.rebuilds,
                "raw_bytes": sum(len(key) + 1 for key in self.keys)}
