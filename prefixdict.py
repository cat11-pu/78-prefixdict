"""prefixdict.py：前缀压缩字典。

按前 ``width`` 个字符把键分组：每组只存一次公共前缀，键只存去掉前缀后的
剩余部分。增量插入只落到所属分组（``rebuilds`` 恒为 0），不会整表重建。

编码口径（按字节，UTF-8）：

    encoded_size = 每组 (前缀字节 + 1 分隔) + 每键 (剩余字节 + 1 分隔)

对前 16 个字符全相同的一组 N 个键，公共前缀从 N 份压成 1 份。
"""
from __future__ import annotations

import json
import os


class KeyDict:
    def __init__(self, width: int = 2):
        self.width = width
        # group: 公共前缀 -> {剩余部分: value}
        # 公共前缀每组只存一次（dict 键），不为每个键重复保存。
        self._groups: dict[str, dict[str, str]] = {}
        self.rebuilds = 0

    # ----- 基本读写 -----------------------------------------------------
    def put(self, key: str, value: str = "") -> dict:
        """增量插入：只落到 key 所属分组，不触发整表重建。"""
        prefix, rest = key[: self.width], key[self.width :]
        group = self._groups.get(prefix)
        if group is None:
            self._groups[prefix] = {rest: value}
        else:
            group[rest] = value
        return {"size": self._count()}

    def members(self) -> list:
        """返回全部键，升序。"""
        return sorted(
            prefix + rest
            for prefix, group in self._groups.items()
            for rest in group
        )

    def _count(self) -> int:
        return sum(len(group) for group in self._groups.values())

    # ----- 编码 / 解码 --------------------------------------------------
    def encoded_size(self) -> int:
        """分组口径的字节数：前缀 + 分隔 + 每剩余部分 + 分隔。"""
        total = 0
        for prefix, group in self._groups.items():
            total += len(prefix.encode("utf-8")) + 1
            for rest in group:
                total += len(rest.encode("utf-8")) + 1
        return total

    def encode(self) -> dict:
        groups = [
            {"prefix": prefix, "rest": sorted(group)}
            for prefix, group in sorted(self._groups.items())
        ]
        payload = {"width": self.width, "groups": groups}
        blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
        group_count = len(groups)
        key_count = self._count()
        return {
            "blob": blob,
            "groups": group_count,
            "shared": key_count - group_count,
        }

    def decode(self, blob) -> list:
        """把 blob 还原为键集合（升序）。"""
        payload = _loads(blob)
        keys = [
            item["prefix"] + rest
            for item in payload.get("groups", [])
            for rest in item["rest"]
        ]
        return sorted(keys)

    # ----- 快照 / 恢复 --------------------------------------------------
    def persist(self, path: str | None = None) -> bytes:
        """落盘并返回快照字节；同时把 value 一起持久化以便无损恢复。"""
        blob = self._snapshot()
        if path is None:
            path = os.path.join(os.getcwd(), "prefixdict.snapshot")
        with open(path, "wb") as handle:
            handle.write(blob)
        return blob

    def restore(self, blob: bytes = None) -> dict:
        """从快照恢复；缺省时从默认快照文件读取。"""
        if blob is None:
            path = os.path.join(os.getcwd(), "prefixdict.snapshot")
            with open(path, "rb") as handle:
                blob = handle.read()
        snapshot = _loads(blob)
        self.width = snapshot["width"]
        self._groups = {
            item["prefix"]: {entry["rest"]: entry["value"] for entry in item["items"]}
            for item in snapshot.get("groups", [])
        }
        self.rebuilds = 0
        return {"size": self._count()}

    def _snapshot(self) -> bytes:
        groups = [
            {
                "prefix": prefix,
                "items": sorted(
                    ({"rest": rest, "value": value} for rest, value in group.items()),
                    key=lambda entry: entry["rest"],
                ),
            }
            for prefix, group in sorted(self._groups.items())
        ]
        return json.dumps(
            {"width": self.width, "groups": groups},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

    # ----- 统计 ---------------------------------------------------------
    def stats(self) -> dict:
        return {
            "size": self._count(),
            "width": self.width,
            "rebuilds": self.rebuilds,
            "raw_bytes": sum(
                len((prefix + rest).encode("utf-8")) + 1
                for prefix, group in self._groups.items()
                for rest in group
            ),
        }


def _loads(blob):
    if isinstance(blob, (bytes, bytearray)):
        return json.loads(blob.decode("utf-8"))
    return json.loads(blob)
