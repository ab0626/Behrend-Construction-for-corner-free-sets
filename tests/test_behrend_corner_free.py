"""
Tests for behrend_corner_free (stdlib unittest).

Run from project root:
  python -m unittest tests.test_behrend_corner_free -v
"""

from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import behrend_corner_free as b


class TestDigitsAndShell(unittest.TestCase):
    def test_sum_sq_digits(self) -> None:
        self.assertEqual(b.sum_sq_digits(12, 4, 5), 8)

    def test_sphere_slice_membership(self) -> None:
        s = b.build_behrend_sphere_slice(5, 4, 8)
        self.assertIn(12, s)

    def test_best_ap_free_nonempty(self) -> None:
        sq, n = b.best_S_ap_free_max_count(5, 4, max_x=5**4 - 1)
        self.assertGreater(n, 0)
        shell = b.build_behrend_sphere_slice(5, 4, sq, max_x=5**4 - 1)
        self.assertGreater(len(shell), 0)
        self.assertIsNone(b.find_three_term_ap(set(shell)))


class TestArithmeticProgressions(unittest.TestCase):
    def test_find_ap(self) -> None:
        self.assertEqual(b.find_three_term_ap({0, 5, 10}), (0, 5, 10))

    def test_no_ap(self) -> None:
        self.assertIsNone(b.find_three_term_ap({0, 1, 3}))


class TestPaperLift(unittest.TestCase):
    def test_lift_matches_lift_formula(self) -> None:
        s1 = {3, 7, 11}
        pts = b.paper_lift_from_set(s1, n=10)
        for x, y in pts:
            self.assertIn(x + 2 * y, s1)

    def test_small_case_corner_free_when_s_ap_free(self) -> None:
        pl = b.build_paper_lift_grid(5, 4, 8, grid_n=30, max_x=5**4 - 1)
        self.assertIsNone(b.find_three_term_ap(set(pl.one_d_set)))
        self.assertIsNone(b.brute_corner_check(pl.points))


class TestDigitSplit(unittest.TestCase):
    def test_known_corner_example(self) -> None:
        bg = b.build_behrend_grid_set(5, 4, 2, 8)
        self.assertIsNotNone(b.brute_corner_check(bg.points))


class TestCornerSearch(unittest.TestCase):
    def test_empty_no_corner(self) -> None:
        self.assertIsNone(b.brute_corner_check(set()))

    def test_smart_matches_brute_small(self) -> None:
        pts = {(0, 0), (1, 0), (0, 1)}
        c1 = b.brute_corner_check(pts)
        c2 = b.find_corner_smart(set(pts))
        self.assertEqual(c1, c2)


class TestImports(unittest.TestCase):
    def test_main_exists(self) -> None:
        self.assertTrue(callable(b.main))


if __name__ == "__main__":
    unittest.main()
