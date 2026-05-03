"""Tests for research_extensions (skew corners, shell counts)."""

from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import research_extensions as rex


class TestSkewCorner(unittest.TestCase):
    def test_skew_found(self) -> None:
        pts = {(0, 0), (2, 0), (0, 3)}
        w = rex.find_skew_corner(set(pts))
        self.assertIsNotNone(w)
        self.assertNotEqual(w[3], w[4])

    def test_axis_corner_not_skew_sample(self) -> None:
        pts = {(0, 0), (1, 0), (0, 1)}
        self.assertIsNone(rex.find_skew_corner(set(pts)))


class TestShellProfile(unittest.TestCase):
    def test_shell_counts_sum(self) -> None:
        rows = rex.shell_density_rows(5, 3, max_x=5**3 - 1)
        total = sum(c for _, c in rows)
        self.assertEqual(total, 5**3)


class TestCyclicSn(unittest.TestCase):
    def test_perm_length(self) -> None:
        self.assertEqual(len(rex.cyclic_permutation_from_integer(7, 5)), 5)


if __name__ == "__main__":
    unittest.main()
