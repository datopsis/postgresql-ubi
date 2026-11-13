"""Run inside each pinned native UBI query container, using its real librpm."""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from vulnerability_gate import UbiQuery, at_least


class RpmVersions(unittest.TestCase):
    def test_native_epoch_version_release_order(self):
        cases = [
            ("2.37.4-28.el9_9", "2.37.4-28.el9_9", True),
            ("2.37.4-28.el9_9.1", "2.37.4-28.el9_9", True),
            ("2.37.4-28.el9_9", "2.37.4-28.el9_9.1", False),
            ("2.37.4-25.el9", "2.37.4-28.el9_9", False),
            ("1:1.0-1", "0:9.0-9", True), ("0:9.0-9", "1:1.0-1", False),
            ("1.0-1", "0:1.0-1", True), ("1.0-10", "1.0-9", True),
            ("1.0~rc1-1", "1.0-1", False), ("1.0^git1-1", "1.0-1", True),
            ("1.0^git1-1", "1.0.1-1", False),
            ("1.10-1", "1.9-1", True), ("1.01-1", "1.1-1", True),
        ]
        for available, fixed, expected in cases:
            with self.subTest(available=available, fixed=fixed):
                self.assertEqual(at_least(available, fixed), expected)

    def test_query_compares_all_versions_and_reuses_native_metadata(self):
        query = UbiQuery.__new__(UbiQuery)
        query.cache = {}
        query.architecture = "x86_64"
        query.base = Mock()
        packages = [Mock(evr="1.0-1"), Mock(evr="1.0-3")]
        query.base.sack.query.return_value.available.return_value.filter.return_value = packages
        self.assertTrue(query("example-rpm", "x86_64", ["1.0-2"])["available"])
        self.assertFalse(query("example-rpm", "x86_64", ["1.0-4"])["available"])
        query.base.sack.query.assert_called_once()
        query.base.sack.query.return_value.available.return_value.filter.assert_called_once_with(
            name="example-rpm", arch=["x86_64", "noarch"])
        with self.assertRaises(ValueError):
            query("example-rpm", "aarch64", ["1.0-2"])
        with self.assertRaises(ValueError):
            query("example-rpm", "x86_64", [">=1.0-2"])


if __name__ == "__main__":
    unittest.main()
