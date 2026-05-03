"""Tests for research_extensions (skew corners, shell counts)."""

from __future__ import annotations

import json
import os
import random
import sys
import tempfile
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


class TestSkewFreeConstruct(unittest.TestCase):
    def test_permutation_skew_free_all_m(self) -> None:
        rng = random.Random(0)
        for m in range(1, 15):
            p = rex.construct_skew_corner_free_permutation(m, rng)
            self.assertEqual(len(p), m)
            self.assertTrue(rex.is_skew_corner_free(p))

    def test_greedy_skew_free(self) -> None:
        rng = random.Random(42)
        p = rex.construct_skew_corner_free_greedy(12, rng)
        self.assertTrue(rex.is_skew_corner_free(p))


class TestLiftDensitySearch(unittest.TestCase):
    def test_search_returns_valid_lift(self) -> None:
        d, k, _sq, pl, alpha = rex.search_ap_free_lift_near_density(
            0.04,
            max_d=8,
            max_k=4,
            max_universe=12_000,
        )
        self.assertEqual(pl.d, d)
        self.assertEqual(pl.k, k)
        self.assertGreater(alpha, 0.0)
        self.assertLess(alpha, 1.0)

    def test_row_proxy_on_uniform_singleton(self) -> None:
        self.assertAlmostEqual(rex.clumpiness_proxy_row_ratio({(1, 1)}, 5), 5.0)


class TestGridNormPipe(unittest.TestCase):
    def test_json_schema_fields(self) -> None:
        pts = {(1, 2), (3, 1)}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            path = f.name
        try:
            rex.export_grid_norm_pipe_v1(
                path,
                list(pts),
                construction="test",
                parameters={"m": 5},
                grid_side_n=5,
            )
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["format"], "grid_norm_pipe_v1")
            self.assertEqual(data["packed_xy"]["xs"], [1, 3])
            self.assertEqual(data["packed_xy"]["ys"], [2, 1])
            self.assertEqual(len(data["cells"]), 2)
            self.assertEqual(data["provenance"]["construction"], "test")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
