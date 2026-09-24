import unittest

from dictapi import Index
from prefixdict import KeyDict


class TestKeyDict(unittest.TestCase):
    def test_put_counts(self):
        self.assertEqual(KeyDict().put("abc")["size"], 1)

    def test_members_sorted(self):
        keys = KeyDict()
        keys.put("bcd")
        keys.put("abc")
        self.assertEqual(keys.members(), ["abc", "bcd"])

    def test_members_empty(self):
        self.assertEqual(KeyDict().members(), [])

    def test_stats_shape(self):
        self.assertIn("width", KeyDict().stats())

    def test_index_wraps_dict(self):
        index = Index()
        index.put("abc")
        self.assertEqual(index.dict.stats()["size"], 1)


if __name__ == "__main__":
    unittest.main()
