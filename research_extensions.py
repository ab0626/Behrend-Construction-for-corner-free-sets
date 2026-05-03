"""
Research-oriented extensions: skew corners (search + **constructions**), shell density
profiling, **grid_norm_pipe_v1** export for external norm tooling, and a minimal non-abelian
(cyclic subgroup of S_n) lift — companion to arXiv:2504.07006-style discussion.

This module does not prove new bounds; it instruments constructions for experiments. See
``docs/skew_corner_free_constructions.md`` and ``docs/grid_norm_pipe_schema.md``. Functions
``search_ap_free_lift_near_density`` and ``clumpiness_proxy_row_ratio`` support
``scripts/paper_compliance_loop.py``.
"""

from __future__ import annotations

import csv
import json
import random
from collections import Counter
from typing import Iterable, Iterator, List, Optional, Sequence, Set, Tuple

import behrend_corner_free as b

Coord = Tuple[int, int]

SkewWitness = Tuple[Coord, Coord, Coord, int, int]


def find_skew_corner(points: Set[Coord]) -> Optional[SkewWitness]:
    """
    Skew axis corner: (x,y), (x+d,y), (x,y+d') all in P with d != d' and d,d' != 0.

    This relaxes the standard corner where d = d'. Finding skew corners is an
    intermediate difficulty step in some corners-theory narratives (paper §2.2 style).
    """
    if len(points) < 3:
        return None
    by_row: dict[int, Set[int]] = {}
    by_col: dict[int, Set[int]] = {}
    for x, y in points:
        by_row.setdefault(y, set()).add(x)
        by_col.setdefault(x, set()).add(y)

    for x, y in points:
        for xp in by_row.get(y, ()):
            if xp == x:
                continue
            d = xp - x
            if d == 0:
                continue
            for yp in by_col.get(x, ()):
                if yp == y:
                    continue
                dp = yp - y
                if dp != 0 and d != dp:
                    return ((x, y), (xp, y), (x, yp), d, dp)
    return None


def is_skew_corner_free(points: Set[Coord]) -> bool:
    """True iff no triple (x,y),(x+d,y),(x,y+d') with d,d'≠0 and d≠d' (see `find_skew_corner`)."""
    return find_skew_corner(points) is None


def construct_skew_corner_free_permutation(m: int, rng: random.Random) -> Set[Coord]:
    """
    Graph of a permutation: P = {(i, π(i)) : 1 ≤ i ≤ m} with π a uniform random permutation.

    **Lemma.** P has **no skew corner** and **no axis corner**.

    *Proof.* At most one point of P lies in each horizontal line y = const (given i, unique y = π(i)),
    so there are no two distinct points (x,y) and (x+d,y) with d ≠ 0 on the same row. Both skew and
    axis corners require such a pair on the bottom edge of the L, hence impossible. ∎

    Density |P|/m² = 1/m on [m]² — a trivial high-asymmetry regime compared to Behrend-type lifts.
    """
    if m < 1:
        raise ValueError("m must be >= 1")
    ys = list(range(1, m + 1))
    rng.shuffle(ys)
    return {(i, ys[i - 1]) for i in range(1, m + 1)}


def construct_skew_corner_free_greedy(m: int, rng: random.Random) -> Set[Coord]:
    """
    Greedy absorption: visit cells of [1,m]² in random order; add a cell iff it creates **no** skew
    corner with the set so far.

    The output is **maximal** skew-corner-free (under this order) but need **not** be maximum-cardinality,
    and it may still contain **axis** corners (same horizontal and vertical step): skew detection ignores d=d'.

    **Complexity:** Each trial calls `find_skew_corner` — fine for benchmark sizes m ≲ 80; avoid huge m.
    """
    if m < 1:
        raise ValueError("m must be >= 1")
    cells = [(x, y) for x in range(1, m + 1) for y in range(1, m + 1)]
    rng.shuffle(cells)
    out: Set[Coord] = set()
    for c in cells:
        trial = set(out)
        trial.add(c)
        if find_skew_corner(trial) is None:
            out.add(c)
    return out


def clumpiness_proxy_row_ratio(points: Set[Coord], grid_n: int) -> float:
    """
    Informal diagnostic: max over rows of (occupancy) divided by mean occupancy |P|/n.
    Behrend paper lifts concentrate on lines x+2y = const → mass on sparse rows → ratio ≫ 1.
    Not a Gowers norm; use your detector JSON pipe for quantitative uniformity.
    """
    if not points or grid_n < 1:
        return 1.0
    by_y = Counter(y for _x, y in points)
    mean = len(points) / grid_n
    if mean <= 0:
        return 1.0
    return max(by_y.values()) / mean


def search_ap_free_lift_near_density(
    alpha_target: float,
    *,
    max_d: int = 14,
    max_k: int = 7,
    max_universe: int = 800_000,
) -> Tuple[int, int, int, b.PaperLiftGrid, float]:
    """
    Search AP-free sphere shells and paper lifts for (d,k) with d^k ≤ max_universe, minimizing
    | |A|/n^2 − alpha_target | over the default lift grid side.

    Used by ``scripts/paper_compliance_loop.py`` for benchmark targeting (not an inverse theorem).
    """
    if not (0.0 < alpha_target < 1.0):
        raise ValueError("alpha_target must lie in (0,1)")
    best_err = float("inf")
    best: Optional[Tuple[int, int, int, b.PaperLiftGrid, float]] = None
    for d in range(3, max_d + 1):
        for k in range(3, max_k + 1):
            max_x = d**k - 1
            if max_x > max_universe:
                continue
            sum_sq, _ = b.best_S_ap_free_max_count(d, k, max_x=max_x)
            pl = b.build_paper_lift_grid(d, k, sum_sq, grid_n=None, max_x=max_x)
            alpha = pl.size / (pl.grid_n * pl.grid_n)
            err = abs(alpha - alpha_target)
            if err < best_err:
                best_err = err
                best = (d, k, sum_sq, pl, alpha)
    if best is None:
        raise RuntimeError("no (d,k) found; widen max_d/max_k or raise max_universe")
    return best


def iter_shell_counts(
    d: int, k: int, max_x: Optional[int] = None
) -> Iterator[Tuple[int, int]]:
    """Yield (sum_sq, population count) for each shell."""
    if max_x is None:
        max_x = d**k - 1
    max_sum_sq = k * (d - 1) ** 2
    for sum_sq in range(max_sum_sq + 1):
        n = sum(1 for _ in b.iter_sphere_slice(max_x, k, d, sum_sq))
        yield sum_sq, n


def shell_density_rows(d: int, k: int, max_x: Optional[int] = None) -> List[Tuple[int, int]]:
    return list(iter_shell_counts(d, k, max_x=max_x))


def write_shell_profile_csv(path: str, d: int, k: int, max_x: Optional[int] = None) -> None:
    """CSV columns: sum_sq, count, density_fraction (relative to d^k universe)."""
    if max_x is None:
        max_x = d**k - 1
    denom = max_x + 1
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sum_sq", "count", "density_fraction"])
        for sum_sq, cnt in iter_shell_counts(d, k, max_x=max_x):
            w.writerow([sum_sq, cnt, cnt / denom])


def export_sparse_grid_csv(points: Iterable[Coord], path: str, meta: Optional[dict] = None) -> None:
    """One row per occupied cell: x,y. Optional JSON sidecar if meta ends with .csv → .meta.json."""
    pts = sorted(points)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["x", "y"])
        for x, y in pts:
            w.writerow([x, y])
    if meta is not None:
        side = path.rsplit(".", 1)[0] + ".meta.json"
        with open(side, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)


def export_run_json(
    path: str,
    *,
    mode: str,
    params: dict,
    points: Sequence[Coord],
    one_d_sorted: Optional[Sequence[int]] = None,
) -> None:
    """Pipe-friendly JSON for external grid-norm / detection tooling."""
    payload = {
        "format": "behrend_corner_free_grid_v1",
        "mode": mode,
        "parameters": params,
        "grid_points": [{"x": x, "y": y} for x, y in sorted(points)],
        "cardinality": len(points),
    }
    if one_d_sorted is not None:
        payload["one_d_shell"] = list(one_d_sorted)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def export_grid_norm_pipe_v1(
    path: str,
    points: Sequence[Coord],
    *,
    construction: str,
    parameters: dict,
    grid_side_n: Optional[int] = None,
) -> None:
    """
    **Grid Norm Clumpiness Detector**–oriented export: one JSON object with explicit coordinates,
    bounding box, and `packed_xy` for fast array consumers (no nested `{"x":..,"y":..}` per point required).

    Schema id: `grid_norm_pipe_v1`. Full field list and consumer notes: `docs/grid_norm_pipe_schema.md`.
    """
    pts = sorted(points)
    if not pts:
        xs: list[int] = []
        ys = []
        x_min = x_max = y_min = y_max = 1
    else:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
    span_x = x_max - x_min + 1
    span_y = y_max - y_min + 1
    area = span_x * span_y
    npts = len(pts)
    payload = {
        "format": "grid_norm_pipe_v1",
        "schema_reference": "docs/grid_norm_pipe_schema.md",
        "coordinate_system": {
            "indexing": "one_based_inclusive",
            "x": "horizontal_increasing",
            "y": "vertical_increasing",
            "notes": "Same convention as behrend_corner_free paper lift on [1,n]×[1,n]. "
            "For 0-based arrays, use x-1 and y-1 per cell.",
        },
        "bounding_box": {
            "x_min": x_min,
            "x_max": x_max,
            "y_min": y_min,
            "y_max": y_max,
            "width": span_x,
            "height": span_y,
        },
        "grid_hint": {
            "nominal_side_n": grid_side_n,
            "description": "If set, the intended ambient grid was [1,n]×[1,n] (e.g. Behrend lift).",
        },
        "occupancy": {
            "num_points": npts,
            "density_in_bounding_box": (npts / area) if area else 0.0,
        },
        "packed_xy": {"xs": xs, "ys": ys},
        "cells": [{"x": x, "y": y} for x, y in pts],
        "provenance": {
            "generator": "behrend_corner_free",
            "construction": construction,
            "parameters": parameters,
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def export_grid_norm_pipe_csv(
    path: str,
    points: Sequence[Coord],
    *,
    construction: str,
    parameters: dict,
) -> None:
    """
    Two-line header: schema tag + JSON parameters; then `x,y` data rows. Pairs with
    `export_grid_norm_pipe_v1` for loaders that only accept CSV.
    """
    pts = sorted(points)
    meta = {"format": "grid_norm_pipe_v1", "construction": construction, "parameters": parameters}
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write("# " + json.dumps(meta, separators=(",", ":")) + "\n")
        w = csv.writer(f)
        w.writerow(["x", "y"])
        for x, y in pts:
            w.writerow([x, y])


def cyclic_permutation_from_integer(x: int, n: int) -> List[int]:
    """
    Image of x in the cyclic subgroup of S_n generated by (0 1 ... n-1):
    position i maps to (i + x) mod n as labels 0..n-1.

    This is a concrete non-abelian setting (n>=3) alongside abelian Z/nZ lifts.
    Section 1.1-style reductions to all finite groups are proved in the paper;
    this helper is only a pedagogical embedding.
    """
    if n < 2:
        raise ValueError("n must be >= 2")
    r = x % n
    return [(i + r) % n for i in range(n)]


def lift_shell_to_symmetric_group_json(
    shell_values: Sequence[int],
    n_perm: int,
    path: str,
    *,
    extra: Optional[dict] = None,
) -> None:
    """Write JSON list of {value, permutation} for each element of the shell."""
    rows = []
    for v in shell_values:
        rows.append(
            {
                "value": int(v),
                "cyclic_permutation_S_n": cyclic_permutation_from_integer(v, n_perm),
            }
        )
    out = {"lift": "cyclic_subgroup_S_n", "n_perm": n_perm, "elements": rows}
    if extra:
        out["extra"] = extra
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


def write_shell_density_svg(
    path: str,
    d: int,
    k: int,
    max_x: Optional[int] = None,
    w: int = 820,
    h: int = 320,
) -> None:
    """Bar-style SVG of shell population vs sum_sq (stdlib only)."""
    if max_x is None:
        max_x = d**k - 1
    rows = shell_density_rows(d, k, max_x=max_x)
    counts = [c for _, c in rows]
    max_c = max(counts) if counts else 1
    pad_l, pad_r, pad_t, pad_b = 50, 30, 35, 55
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b
    nbar = len(rows) if rows else 1

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="system-ui,sans-serif">',
        '<rect width="100%" height="100%" fill="#fafafa"/>',
        f'<text x="{w//2}" y="22" text-anchor="middle" font-size="14" fill="#222">'
        f"Shell density |{{x : Σ x_i² = S}}| vs S (d={d}, k={k})</text>",
    ]
    bw = max(0.8, iw / nbar - 0.4)
    for i, (_S_val, cnt) in enumerate(rows):
        if cnt == 0:
            continue
        bh_bar = (cnt / max_c) * ih
        x0 = pad_l + i * (iw / nbar)
        y0 = pad_t + ih - bh_bar
        parts.append(
            f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{bw:.2f}" height="{bh_bar:.2f}" '
            f'fill="#5e81ac" opacity="0.85"/>'
        )
    parts.append(
        f'<text x="{pad_l}" y="{h-18}" font-size="11" fill="#555">S (sum of squared digits)</text>'
    )
    parts.append(
        f'<text x="{w//2}" y="{h-8}" text-anchor="middle" font-size="10" fill="#888">'
        f"max count per shell = {max_c}</text>"
    )
    parts.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
