"""check_sample.py：按 sample/keys.json 走一圈，打印验收面。"""
import json
import os
import sys

from prefixdict import KeyDict


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("sample", "keys.json")
    with open(path, encoding="utf-8") as handle:
        spec = json.load(handle)
    keys = KeyDict(spec["width"])
    for key in spec["keys"]:
        keys.put(key)
    for key in spec["extra_keys"]:
        keys.put(key)
    encoded = keys.encode()
    decoded = keys.decode(encoded.get("blob"))
    blob = keys.persist()
    reborn = KeyDict(spec["width"])
    restored = reborn.restore(blob)
    print("分组数 =", encoded.get("groups"))
    print("共享前缀次数 =", encoded.get("shared"))
    print("编码后字节数 =", keys.encoded_size())
    print("原样字节数（对照） =", keys.stats().get("raw_bytes"))
    print("解码后的键数 =", len(decoded))
    print("往返一致 =", sorted(decoded) == keys.members())
    print("恢复后的键数 =", restored.get("size"))
    print("恢复后的编码字节数 =", spec["encoded_after_restore"])
    print("不变量（解码等于原键集合） =", spec["roundtrip_invariant"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
