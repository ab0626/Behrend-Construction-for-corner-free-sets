"""
Behrend sphere-slice sets and the paper-aligned lift to a corner-free subset of [N]×[N].

**1D construction (Behrend regime).** Integers are written in base d with k fixed digits.
We keep x with sum_i x_i^2 = S_fixed. Shells with fixed sum of squares are the usual
"sphere surface" picture behind Behrend-type bounds (density ~ exp(-Theta(sqrt(log N))) in
the full construction). A given shell need not be 3-AP-free by itself: maximizing |shell|
over S can yield a shell that still contains a 3-term AP. For the paper lift below, this
module defaults to choosing **sum_sq** among shells that pass a brute-force 3-AP check, so
the hypothesis "S is 3-AP-free" matches the script's output.

**Paper-aligned 2D lift (projection equivalence).** For S ⊆ [N] (as integers), define
    A = { (x, y) ∈ [N] × [N] : x + 2y ∈ S }.
If A contained a corner (x,y), (x+d,y), (x,y+d), then
    x+2y,  (x+d)+2y = (x+2y)+d,  x+2(y+d) = (x+2y)+2d
would be a 3-term AP in S. So if S is 3-AP-free, A is corner-free.

**Contrast.** A naive digit-split map (u,v) from digit blocks is only a visualization of
the sphere slice; it does not encode this AP–corner implication and can contain corners.

**Density / “clumpiness”.** `best_S_for_count` picks the sphere slice with the most points—
a concrete analogue of seeking a high-density structured piece (as in Roth-type arguments).
For the default **paper** mode, `best_S_ap_free_max_count` instead maximizes |shell| subject to
no 3-term AP (verified brute-force), matching the hypothesis needed for the lift.

**Verification (Section 2 projection).** The corners theorem implies Roth’s theorem via a
standard projection; the lift `A = {(x,y) : x+2y ∈ S}` reverses the direction: a corner in
`A` would force a 3-term AP in `S`. So for `S` from a genuine AP-free construction, `A` is
corner-free—the multidimensional pattern controlled is the same one Szemerédi-type theorems
address, with corners as the minimal 2D case.

**Presentation (before / after).** For slides or a live demo, compare CLI modes:
  * ``--mode paper`` (default): the rigorous lift ``A = {(x,y) : x+2y ∈ S}``; when ``S`` is
    3-AP-free, ``brute_corner_check`` / ``find_corner_smart`` should find no axis corner.
  * ``--mode digit-split``: the same 1D shell embedded by digit blocks; corners may appear,
    illustrating that the projection argument is nontrivial—naive 2D coordinates need not
    preserve the AP–corner obstruction.

**Code ↔ paper (informal map for reports).** Section numbers refer to arXiv:2504.07006-style
discussion of Behrend-type inputs and projections; adjust if your edition differs.

  paper_lift_from_set / build_paper_lift_grid … Section 2, projection / lift ``x+2y``
  best_S_ap_free_max_count … structured shell: dense but 3-AP-free (hypothesis for the lift)
  digits_base_d, iter_sphere_slice, build_behrend_sphere_slice … Behrend-type ``(log N)^c``
    regime (sphere / digit shell)
  brute_corner_check, find_corner_smart … empirical oracle: axis ``L``-corner in ``A``?
  default_grid_n_for_lift … scale ``n`` so ``x+2y`` can reach ``max(S)`` (here ``3n ≳ max``)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Set, Tuple


Coord = Tuple[int, int]


def digits_base_d(x: int, k: int, d: int) -> Tuple[int, ...]:
    """Least-significant digit first: x = sum_i x_i * d^i, each 0 <= x_i < d."""
    if x < 0:
        raise ValueError("x must be nonnegative")
    out: list[int] = []
    t = x
    for _ in range(k):
        out.append(t % d)
        t //= d
    if t != 0:
        raise ValueError(f"x={x} needs more than k={k} base-{d} digits")
    return tuple(out)


def from_digits_base_d(digits: Iterable[int], d: int) -> int:
    """LSF order: digits[0] + digits[1]*d + ..."""
    s = 0
    p = 1
    for dig in digits:
        s += dig * p
        p *= d
    return s


def sum_sq_digits(x: int, k: int, d: int) -> int:
    return sum(z * z for z in digits_base_d(x, k, d))


def iter_sphere_slice(max_value: int, k: int, d: int, S: int) -> Iterator[int]:
    """All x in [0, max_value] with sum of squared base-d digits (k digits) equal to S."""
    for x in range(max_value + 1):
        if sum_sq_digits(x, k, d) == S:
            yield x


def grid_map_from_digits(x: int, k: int, d: int, k1: int) -> Coord:
    """
    Legacy visualization: split k digits (LSF) into first k1 digits -> u, rest -> v.
    Does not preserve corner-freeness; prefer paper_lift_from_set for the paper lift.
    """
    if not 1 <= k1 < k:
        raise ValueError("need 1 <= k1 < k")
    digs = digits_base_d(x, k, d)
    u = from_digits_base_d(digs[:k1], d)
    v = from_digits_base_d(digs[k1:], d)
    return (u, v)


def build_behrend_sphere_slice(
    d: int,
    k: int,
    sum_sq: int,
    max_x: Optional[int] = None,
) -> frozenset[int]:
    """1D Behrend-type set: x in [0, max_x] with k base-d digits and sum_i x_i^2 = sum_sq."""
    if max_x is None:
        max_x = d**k - 1
    return frozenset(iter_sphere_slice(max_x, k, d, sum_sq))


def paper_lift_from_set(one_d: Set[int], n: int) -> frozenset[Coord]:
    """
    Paper lift L(x,y) = x + 2y: grid points in [1,n]×[1,n] with x+2y ∈ one_d.
    If one_d ⊆ ℤ has no 3-term AP, this set has no axis corner (x,y),(x+d,y),(x,y+d).
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    out: Set[Coord] = set()
    for x in range(1, n + 1):
        for y in range(1, n + 1):
            if x + 2 * y in one_d:
                out.add((x, y))
    return frozenset(out)


def find_three_term_ap(S: Set[int]) -> Optional[Tuple[int, int, int]]:
    """Return (a, a+d, a+2d) in S with d > 0, or None if no 3-term AP."""
    if len(S) < 3:
        return None
    lst = sorted(S)
    for i, a in enumerate(lst):
        for b in lst[i + 1 :]:
            c = 2 * b - a
            if c > b and c in S:
                return (a, b, c)
    return None


@dataclass(frozen=True)
class PaperLiftGrid:
    """Behrend sphere slice S_1d ⊆ [0, d^k-1] lifted to A ⊆ [n]×[n] via x+2y ∈ S_1d."""

    d: int
    k: int
    sum_sq: int
    one_d_set: frozenset[int]
    grid_n: int
    points: frozenset[Coord]

    @property
    def size(self) -> int:
        return len(self.points)


def default_grid_n_for_lift(one_d: Set[int], cap: int) -> int:
    """
    Smallest n such that max_{x,y in [1,n]} (x+2y) = 3n can reach max(one_d).
    Capped by cap (e.g. d^k-1).
    """
    if not one_d:
        return 1
    hi = max(one_d)
    n_need = (hi + 2) // 3 + 1
    return min(cap, max(1, n_need))


def build_paper_lift_grid(
    d: int,
    k: int,
    sum_sq: int,
    grid_n: Optional[int],
    max_x: Optional[int] = None,
) -> PaperLiftGrid:
    """1D sphere slice then A = {(x,y) ∈ [1,grid_n]^2 : x+2y in slice}."""
    if max_x is None:
        max_x = d**k - 1
    s1 = build_behrend_sphere_slice(d, k, sum_sq, max_x=max_x)
    if grid_n is None:
        grid_n = default_grid_n_for_lift(s1, max_x)
    pts = paper_lift_from_set(s1, grid_n)
    return PaperLiftGrid(
        d=d,
        k=k,
        sum_sq=sum_sq,
        one_d_set=s1,
        grid_n=grid_n,
        points=pts,
    )


@dataclass(frozen=True)
class BehrendGridSet:
    """Legacy digit-split visualization (may contain corners)."""

    d: int
    k: int
    k1: int
    S: int
    points: frozenset[Coord]
    raw_x_values: tuple[int, ...]

    @property
    def size(self) -> int:
        return len(self.points)


def build_behrend_grid_set(
    d: int,
    k: int,
    k1: int,
    S: int,
    max_x: Optional[int] = None,
) -> BehrendGridSet:
    """
    Enumerate all x with k base-d digits and digit-square sum S, map to 2D via k1 split.
    max_x defaults to d^k - 1 (full digit range).
    """
    if max_x is None:
        max_x = d**k - 1
    xs = tuple(iter_sphere_slice(max_x, k, d, S))
    pts: Set[Coord] = set()
    for x in xs:
        pts.add(grid_map_from_digits(x, k, d, k1))
    return BehrendGridSet(
        d=d, k=k, k1=k1, S=S, points=frozenset(pts), raw_x_values=xs
    )


def find_corner_smart(points: Set[Coord]) -> Optional[Tuple[Coord, Coord, Coord, int]]:
    """
    Same as find_corner but O(n * average line hits): for each (x,y), scan d such that
    (x+d,y) and (x,y+d) are in P. We iterate d by walking along row and column in P.
    """
    P = points
    # Group by row and column for faster neighbor lookup
    by_row: dict[int, set[int]] = {}
    by_col: dict[int, set[int]] = {}
    for x, y in P:
        by_row.setdefault(y, set()).add(x)
        by_col.setdefault(x, set()).add(y)

    for x, y in P:
        row = by_row.get(y, set())
        col = by_col.get(x, set())
        for xp in row:
            if xp == x:
                continue
            d = xp - x
            if (y + d) in col:
                return ((x, y), (x + d, y), (x, y + d), d)
    return None


def brute_corner_check(points: Iterable[Coord]) -> Optional[Tuple[Coord, Coord, Coord, int]]:
    """
    Find A=(x,y), B=(x+d,y), C=(x,y+d) with d != 0 and all three in P.
    For each apex A, try every B on the same row; d = B_x - x.
    """
    P: Set[Coord] = set(points)
    by_row: dict[int, list[int]] = {}
    for x, y in P:
        by_row.setdefault(y, []).append(x)
    for ys in by_row.values():
        ys.sort()

    for x, y in P:
        for xb in by_row.get(y, ()):
            if xb == x:
                continue
            d = xb - x
            if (x, y + d) in P:
                return ((x, y), (x + d, y), (x, y + d), d)
    return None


def best_S_for_count(d: int, k: int, max_x: Optional[int] = None) -> tuple[int, int]:
    """Pick sum_sq in [0, k*(d-1)^2] maximizing |{x on shell}| (may contain 3-term APs)."""
    if max_x is None:
        max_x = d**k - 1
    best_S, best_n = 0, -1
    max_S = k * (d - 1) ** 2
    for S in range(max_S + 1):
        n = sum(1 for _ in iter_sphere_slice(max_x, k, d, S))
        if n > best_n:
            best_n, best_S = n, S
    return best_S, best_n


def best_S_ap_free_max_count(
    d: int, k: int, max_x: Optional[int] = None
) -> tuple[int, int]:
    """
    Among sphere shells with no 3-term AP, maximize population (including |shell|<=2).
    Returns (best_sum_sq, |shell|).
    """
    if max_x is None:
        max_x = d**k - 1
    best_S, best_n = 0, -1
    max_S = k * (d - 1) ** 2
    for S in range(max_S + 1):
        shell = frozenset(iter_sphere_slice(max_x, k, d, S))
        if find_three_term_ap(set(shell)):
            continue
        n = len(shell)
        if n > best_n:
            best_n, best_S = n, S
    return best_S, best_n


def demo() -> None:
    d, k, sum_sq = 5, 4, 8
    n = 30
    pl = build_paper_lift_grid(d, k, sum_sq, grid_n=n)
    print("Paper lift A = {(x,y) in [n]x[n] : x+2y in S} (Behrend sphere slice S)")
    print(f"  d={d}, k={k}, sum_sq={sum_sq}, n={n}")
    print(f"  |S|={len(pl.one_d_set)}, |A|={pl.size}")
    ap = find_three_term_ap(set(pl.one_d_set))
    print(f"  3-term AP in S: {ap if ap else 'none'}")
    corner = brute_corner_check(pl.points)
    print(f"  corner in A: {corner if corner else 'none'}")

    print()
    k1 = 2
    bg = build_behrend_grid_set(d, k, k1, sum_sq)
    print("Legacy digit-split map (same S, different 2D embedding — may have corners)")
    print(f"  |grid points| = {bg.size}")
    c_legacy = brute_corner_check(bg.points)
    print(f"  corner: {c_legacy if c_legacy else 'none'}")

    d2, k2 = 7, 5
    sum2, _ = best_S_ap_free_max_count(d2, k2)
    pl2 = build_paper_lift_grid(d2, k2, sum2, grid_n=None, max_x=d2**k2 - 1)
    print()
    print(f"Larger (3-AP-free shell): d={d2}, k={k2}, sum_sq={sum2}, grid_n={pl2.grid_n}")
    print(f"  |S|={len(pl2.one_d_set)}, |A|={pl2.size}, AP in S: {find_three_term_ap(set(pl2.one_d_set))}")
    print(f"  corner in A: {brute_corner_check(pl2.points) or find_corner_smart(set(pl2.points))}")


def main() -> None:
    p = argparse.ArgumentParser(
        description="Behrend sphere slice + paper lift (x+2y) or legacy digit-split + corner check"
    )
    p.add_argument("--d", type=int, default=7, help="base d")
    p.add_argument("--k", type=int, default=5, help="number of base-d digits")
    p.add_argument(
        "--grid-n",
        type=int,
        default=None,
        help="grid side [1,n]×[1,n] for paper lift (default: auto from max(S) so x+2y can hit each value)",
    )
    p.add_argument(
        "--mode",
        choices=("paper", "digit-split"),
        default="paper",
        help="paper: A={(x,y):x+2y in S}; digit-split: legacy digit-block map",
    )
    p.add_argument("--k1", type=int, default=2, help="digit-split only: first k1 digits → x")
    p.add_argument(
        "--S",
        type=int,
        default=None,
        help="fixed sum of squares of digits (default: see --dense-shell)",
    )
    p.add_argument(
        "--dense-shell",
        action="store_true",
        help="paper mode: pick shell maximizing |S| even if S has a 3-term AP (breaks lift guarantee)",
    )
    p.add_argument("--list", action="store_true", help="print all grid points")
    p.add_argument("--demo", action="store_true", help="run small built-in examples after CLI output")
    p.add_argument(
        "--skew-check",
        action="store_true",
        help="also search for skew corners (x,y),(x+d,y),(x,y+d') with d≠d'",
    )
    p.add_argument(
        "--profile-shells-csv",
        metavar="PATH",
        default=None,
        help="write shell density table CSV (sum_sq, count, density) for --d/--k; then exit",
    )
    p.add_argument(
        "--profile-shells-svg",
        metavar="PATH",
        default=None,
        help="write shell density bar chart SVG for --d/--k; then exit",
    )
    p.add_argument(
        "--export-csv",
        metavar="PATH",
        default=None,
        help="export grid points as sparse CSV (x,y)",
    )
    p.add_argument(
        "--export-json",
        metavar="PATH",
        default=None,
        help="export run metadata + grid points as JSON (for external norm tools)",
    )
    p.add_argument(
        "--symmetric-lift-json",
        metavar="PATH",
        default=None,
        help="export 1D shell values as cyclic permutations in S_n (see --symmetric-n)",
    )
    p.add_argument(
        "--symmetric-n",
        type=int,
        default=6,
        help="degree n for S_n cyclic lift (default 6)",
    )
    p.add_argument(
        "--skew-free",
        dest="skew_free",
        choices=("none", "permutation", "greedy"),
        default="none",
        metavar="MODE",
        help="build a skew-corner-free set in [1,m]×[1,m] (skips Behrend d,k run); "
        "permutation = graph of π (also axis-corner-free); greedy = random-order maximal set",
    )
    p.add_argument(
        "--skew-free-m",
        type=int,
        default=32,
        metavar="M",
        help="grid side m for --skew-free (default 32)",
    )
    p.add_argument(
        "--skew-free-seed",
        type=int,
        default=0,
        help="RNG seed for --skew-free permutation / greedy (default 0)",
    )
    p.add_argument(
        "--export-grid-norm-json",
        metavar="PATH",
        default=None,
        help="export grid_norm_pipe_v1 JSON for Grid Norm / clumpiness detector tooling",
    )
    p.add_argument(
        "--export-grid-norm-csv",
        metavar="PATH",
        default=None,
        help="export x,y CSV with grid_norm_pipe_v1 header line (for CSV-only pipelines)",
    )
    args = p.parse_args()

    if args.profile_shells_csv:
        import research_extensions as rex

        rex.write_shell_profile_csv(args.profile_shells_csv, args.d, args.k)
        print(f"Wrote shell profile: {args.profile_shells_csv}")
        return
    if args.profile_shells_svg:
        import research_extensions as rex

        rex.write_shell_density_svg(
            args.profile_shells_svg, args.d, args.k, max_x=args.d**args.k - 1
        )
        print(f"Wrote shell density SVG: {args.profile_shells_svg}")
        return

    if args.skew_free != "none":
        import research_extensions as rex

        rng = __import__("random").Random(args.skew_free_seed)
        m = max(1, args.skew_free_m)
        if args.skew_free == "permutation":
            pts = rex.construct_skew_corner_free_permutation(m, rng)
            label = "skew_free_permutation"
        else:
            pts = rex.construct_skew_corner_free_greedy(m, rng)
            label = "skew_free_greedy"
        if not rex.is_skew_corner_free(pts):
            raise RuntimeError("internal error: skew construction contains a skew corner")
        print(
            f"skew-free mode={args.skew_free}  m={m}  |P|={len(pts)}  "
            f"seed={args.skew_free_seed}"
        )
        ac = brute_corner_check(pts)
        if ac:
            print(f"axis corner in P: {ac} (greedy skew-free may allow d=d' corners)")
        else:
            print("No axis corner in P.")
        if args.skew_check:
            sk = rex.find_skew_corner(pts)
            if sk:
                print(f"unexpected SKEW corner: {sk}")
            else:
                print("No skew corner in P (consistent with construction).")
        if args.symmetric_lift_json:
            print(
                "Note: --symmetric-lift-json ignored in --skew-free mode (no 1D shell)."
            )
        if args.export_csv:
            meta = {
                "skew_free": args.skew_free,
                "m": m,
                "seed": args.skew_free_seed,
            }
            rex.export_sparse_grid_csv(pts, args.export_csv, meta=meta)
            print(f"Wrote grid CSV: {args.export_csv}")
        if args.export_json:
            rex.export_run_json(
                args.export_json,
                mode=label,
                params={
                    "skew_free": args.skew_free,
                    "m": m,
                    "seed": args.skew_free_seed,
                },
                points=pts,
                one_d_sorted=None,
            )
            print(f"Wrote JSON: {args.export_json}")
        if args.export_grid_norm_json:
            rex.export_grid_norm_pipe_v1(
                args.export_grid_norm_json,
                list(pts),
                construction=label,
                parameters={
                    "skew_free": args.skew_free,
                    "m": m,
                    "seed": args.skew_free_seed,
                },
                grid_side_n=m,
            )
            print(f"Wrote grid-norm pipe JSON: {args.export_grid_norm_json}")
        if args.export_grid_norm_csv:
            rex.export_grid_norm_pipe_csv(
                args.export_grid_norm_csv,
                list(pts),
                construction=label,
                parameters={
                    "skew_free": args.skew_free,
                    "m": m,
                    "seed": args.skew_free_seed,
                },
            )
            print(f"Wrote grid-norm pipe CSV: {args.export_grid_norm_csv}")
        if args.list:
            for pt in sorted(pts):
                print(pt)
        if args.demo:
            print()
            demo()
        return

    max_x = args.d**args.k - 1
    grid_n: Optional[int] = args.grid_n

    if args.S is None:
        if args.mode == "paper" and not args.dense_shell:
            sum_sq, n_slice = best_S_ap_free_max_count(args.d, args.k, max_x=max_x)
            print(
                f"Chosen sum_sq={sum_sq} (|S|={n_slice}, largest 3-AP-free shell)"
            )
        else:
            sum_sq, n_slice = best_S_for_count(args.d, args.k, max_x=max_x)
            print(f"Chosen sum_sq={sum_sq} (max |shell|={n_slice})")
    else:
        sum_sq = args.S

    if args.mode == "paper":
        pl = build_paper_lift_grid(
            args.d, args.k, sum_sq, grid_n=grid_n, max_x=max_x
        )
        print(
            f"mode=paper  d={pl.d}, k={pl.k}, sum_sq={pl.sum_sq}, grid_n={pl.grid_n}"
        )
        print(f"|S|={len(pl.one_d_set)}, |A|={pl.size}")
        ap = find_three_term_ap(set(pl.one_d_set))
        if ap:
            print(f"WARNING: 3-term AP found in S: {ap} (corner-free lift not guaranteed)")
        else:
            print("No 3-term AP in S (slice passes brute check).")
        c = brute_corner_check(pl.points)
        if c:
            A, B, Cc, dval = c
            print(f"CORNER in A: A={A}, B={B}, C={Cc}, d={dval}")
        else:
            print("No axis-aligned L-corner in A.")
        if args.skew_check:
            import research_extensions as rex

            sk = rex.find_skew_corner(set(pl.points))
            if sk:
                p1, p2, p3, d0, dp = sk
                print(
                    f"SKEW corner: {p1}, {p2}, {p3} with d={d0}, d'={dp} (d≠d')"
                )
            else:
                print("No skew corner (d≠d') in A.")
        pts = pl.points
    else:
        bg = build_behrend_grid_set(args.d, args.k, args.k1, sum_sq, max_x=max_x)
        print(f"mode=digit-split  d={bg.d}, k={bg.k}, k1={bg.k1}, sum_sq={bg.S}")
        print(f"|integers|={len(bg.raw_x_values)}, |grid points|={bg.size}")
        c = brute_corner_check(bg.points)
        if c:
            A, B, Cc, dval = c
            print(f"CORNER: A={A}, B={B}, C={Cc}, d={dval}")
        else:
            print("No axis-aligned L-corner in this digit-split set.")
        if args.skew_check:
            import research_extensions as rex

            sk = rex.find_skew_corner(set(bg.points))
            if sk:
                p1, p2, p3, d0, dp = sk
                print(
                    f"SKEW corner: {p1}, {p2}, {p3} with d={d0}, d'={dp} (d≠d')"
                )
            else:
                print("No skew corner (d≠d') in A.")
        pts = bg.points

    if args.symmetric_lift_json:
        import research_extensions as rex

        if args.mode == "paper":
            s_sorted = sorted(pl.one_d_set)
        else:
            s_sorted = sorted(bg.raw_x_values)
        rex.lift_shell_to_symmetric_group_json(
            s_sorted,
            max(2, args.symmetric_n),
            args.symmetric_lift_json,
            extra={"d": args.d, "k": args.k, "sum_sq": sum_sq},
        )
        print(f"Wrote S_n cyclic lift: {args.symmetric_lift_json}")

    if args.export_csv:
        import research_extensions as rex

        meta = {
            "d": args.d,
            "k": args.k,
            "mode": args.mode,
            "sum_sq": sum_sq,
            "grid_n": pl.grid_n if args.mode == "paper" else None,
        }
        rex.export_sparse_grid_csv(pts, args.export_csv, meta=meta)
        print(f"Wrote grid CSV: {args.export_csv}")

    if args.export_json:
        import research_extensions as rex

        one_d = (
            sorted(pl.one_d_set)
            if args.mode == "paper"
            else sorted(frozenset(bg.raw_x_values))
        )
        pn = pl.grid_n if args.mode == "paper" else None
        rex.export_run_json(
            args.export_json,
            mode=args.mode,
            params={
                "d": args.d,
                "k": args.k,
                "sum_sq": sum_sq,
                "grid_n": pn,
                "k1": args.k1 if args.mode == "digit-split" else None,
            },
            points=pts,
            one_d_sorted=one_d,
        )
        print(f"Wrote JSON: {args.export_json}")

    if args.export_grid_norm_json or args.export_grid_norm_csv:
        import research_extensions as rex

        if args.mode == "paper":
            gparams = {
                "d": args.d,
                "k": args.k,
                "sum_sq": sum_sq,
                "grid_n": pl.grid_n,
                "mode": "paper",
            }
            gcon = "paper_lift"
            gside = pl.grid_n
        else:
            gparams = {
                "d": args.d,
                "k": args.k,
                "k1": args.k1,
                "sum_sq": sum_sq,
                "mode": "digit-split",
            }
            gcon = "digit_split"
            gside = None
        if args.export_grid_norm_json:
            rex.export_grid_norm_pipe_v1(
                args.export_grid_norm_json,
                list(pts),
                construction=gcon,
                parameters=gparams,
                grid_side_n=gside,
            )
            print(f"Wrote grid-norm pipe JSON: {args.export_grid_norm_json}")
        if args.export_grid_norm_csv:
            rex.export_grid_norm_pipe_csv(
                args.export_grid_norm_csv,
                list(pts),
                construction=gcon,
                parameters=gparams,
            )
            print(f"Wrote grid-norm pipe CSV: {args.export_grid_norm_csv}")

    if args.list:
        for pt in sorted(pts):
            print(pt)

    if args.demo:
        print()
        demo()


if __name__ == "__main__":
    main()
