"""
Write SVG figures referenced by README.md (stdlib only; no pip install).

Run from project root:
  python figures/generate_figures.py
"""

from __future__ import annotations

import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _svg_header(w: int, h: int) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="system-ui,sans-serif">'
    )


def write_density_svg(path: str, w: int = 800, h: int = 480) -> None:
    """Stylized 1/loglog N vs exp(-sqrt(log N)) vs placeholder Behrend fractions."""
    pad_l, pad_r, pad_t, pad_b = 70, 30, 40, 50
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b

    def x_pix(log_n: float) -> float:
        lo, hi = math.log(10), math.log(1e6)
        t = (log_n - lo) / (hi - lo)
        return pad_l + t * iw

    def y_pix(v: float) -> float:
        return pad_t + (1.0 - max(0.0, min(1.0, v))) * ih

    Ns = [10 ** (1 + 5 * i / 199) for i in range(200)]
    old_raw: list[float] = []
    new_raw: list[float] = []
    for N in Ns:
        log_n = math.log(max(N, math.e))
        old_raw.append(1.0 / math.log(max(math.log(N), 2.0)))
        new_raw.append(math.exp(-(log_n**0.5)))

    def norm(xs: list[float]) -> list[float]:
        lo, hi = min(xs), max(xs)
        if hi <= lo:
            return [0.5] * len(xs)
        return [(v - lo) / (hi - lo) for v in xs]

    old_n = norm(old_raw)
    new_n = norm(new_raw)
    series_old = [(x_pix(math.log(N)), y_pix(v)) for N, v in zip(Ns, old_n)]
    series_new = [(x_pix(math.log(N)), y_pix(v)) for N, v in zip(Ns, new_n)]

    import behrend_corner_free as b

    # Small d,k only so README figure generation finishes in seconds.
    d, ks = 5, (3, 4, 5)
    dots: list[tuple[float, float]] = []
    for k in ks:
        max_x = d**k - 1
        sq, _ = b.best_S_ap_free_max_count(d, k, max_x=max_x)
        shell = b.build_behrend_sphere_slice(d, k, sq, max_x=max_x)
        frac = len(shell) / (max_x + 1)
        log_n = math.log(max_x + 1)
        dots.append((x_pix(log_n), y_pix(min(1.0, frac * 25))))

    def polyline_pts(pts: list[tuple[float, float]]) -> str:
        return " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)

    parts = [
        _svg_header(w, h),
        '<rect width="100%" height="100%" fill="#fafafa"/>',
        f'<text x="{w//2}" y="24" text-anchor="middle" font-size="16" fill="#222">'
        "Density comparison (illustrative; red = code |S|/(d^k), AP-free shell, d=5, k in 3..5)</text>",
        f'<polyline fill="none" stroke="#888" stroke-width="2" points="{polyline_pts(series_old)}"/>',
        f'<polyline fill="none" stroke="#1a5276" stroke-width="2" points="{polyline_pts(series_new)}"/>',
    ]
    for px, py in dots:
        parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#c0392b"/>')
    parts.append(
        f'<text x="{pad_l}" y="{h-12}" font-size="11" fill="#555">x-axis: log N</text>'
    )
    parts.append(
        f'<text x="{w-200}" y="{pad_t+20}" font-size="11" fill="#888">gray: 1/log log N (norm.)</text>'
    )
    parts.append(
        f'<text x="{w-200}" y="{pad_t+36}" font-size="11" fill="#1a5276">blue: exp(-(log N)^0.5) (norm.)</text>'
    )
    parts.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def write_heatmap_svg(path: str, n: int = 64) -> None:
    import behrend_corner_free as b

    d, k = 7, 4
    sum_sq, _ = b.best_S_ap_free_max_count(d, k, max_x=d**k - 1)
    s1 = b.build_behrend_sphere_slice(d, k, sum_sq, max_x=d**k - 1)
    n = min(n, b.default_grid_n_for_lift(s1, d**k - 1))
    lift = set(b.paper_lift_from_set(s1, n))
    m = [[0.0] * n for _ in range(n)]
    for x, y in lift:
        if 1 <= x <= n and 1 <= y <= n:
            m[y - 1][x - 1] = 1.0
    p = sum(sum(row) for row in m) / (n * n)
    # deterministic pseudo-random Bernoulli(p)
    rand = [[0.0] * n for _ in range(n)]
    seed = 12345
    for i in range(n):
        for j in range(n):
            seed = (1103515245 * seed + 12345) % (2**31)
            rand[i][j] = 1.0 if (seed / 2**31) < p else 0.0

    cell = 5
    gap = 8
    bw = n * cell + gap + n * cell
    bh = n * cell + 60
    parts = [_svg_header(bw, bh), '<rect width="100%" height="100%" fill="#222"/>']

    def rect_color(v: float) -> str:
        if v < 0.5:
            t = int(40 + 180 * (v * 2))
            return f"rgb({t},{t//2},{t//3})"
        t = int(200 + 55 * ((v - 0.5) * 2))
        return f"rgb({min(255,t+40)},{min(255,t//2)},{min(255,t//4)})"

    def draw_grid(data: list[list[float]], ox: int, oy: int, title: str) -> None:
        parts.append(
            f'<text x="{ox + n*cell//2}" y="{oy-8}" text-anchor="middle" '
            f'fill="#eee" font-size="12">{title}</text>'
        )
        for i in range(n):
            for j in range(n):
                c = rect_color(data[i][j])
                parts.append(
                    f'<rect x="{ox+j*cell}" y="{oy+i*cell}" width="{cell-1}" height="{cell-1}" fill="{c}"/>'
                )

    draw_grid(rand, 10, 40, f"random Bernoulli(p), p={p:.3f}")
    draw_grid(m, 10 + n * cell + gap, 40, f"paper lift (|S|={len(s1)}, n={n})")
    parts.append(
        f'<text x="{bw//2}" y="{bh-12}" text-anchor="middle" fill="#aaa" font-size="11">'
        "Heatmaps (illustrative)</text>"
    )
    parts.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def write_lift_projection_svg(path: str) -> None:
    """Schematic: 3-AP on a line maps to an axis corner under L=x+2y."""
    w, h = 720, 260
    lines = [
        _svg_header(w, h),
        '<rect width="100%" height="100%" fill="#fffef8"/>',
        '<text x="360" y="28" text-anchor="middle" font-size="15" fill="#222">'
        "Lift L(x,y) = x + 2y: a corner in A forces z, z+d, z+2d in S</text>",
        '<text x="40" y="95" font-size="13" fill="#444">1D (values in S)</text>',
        '<line x1="120" y1="110" x2="520" y2="110" stroke="#333" stroke-width="2"/>',
    ]
    xs = (180, 300, 420)
    labs = ("z", "z+d", "z+2d")
    for x, lab in zip(xs, labs):
        lines.append(f'<circle cx="{x}" cy="110" r="10" fill="#1a5276"/>')
        lines.append(
            f'<text x="{x}" y="115" text-anchor="middle" fill="white" font-size="12">{lab}</text>'
        )
    lines.append('<text x="40" y="195" font-size="13" fill="#444">2D corner in A</text>')
    # small grid: cell 40, origin (480, 150)
    ox, oy, cs = 480, 150, 36
    for i in range(4):
        for j in range(4):
            lines.append(
                f'<rect x="{ox+j*cs}" y="{oy+i*cs}" width="{cs-1}" height="{cs-1}" '
                'fill="#f5f5f5" stroke="#ccc"/>'
            )
    # L at (1,1) d=1 style: cells (0,0),(1,0),(0,1) in mini grid -> j=0 row i=0,1 col and i=0 j=0,1
    hi = [(0, 0), (1, 0), (0, 1)]
    for j, i in hi:
        lines.append(
            f'<rect x="{ox+j*cs}" y="{oy+i*cs}" width="{cs-1}" height="{cs-1}" '
            'fill="#c0392b" stroke="#922b21"/>'
        )
    lines.append(
        f'<text x="{ox+2*cs}" y="{oy+4*cs+16}" font-size="11" fill="#555">(x,y), (x+d,y), (x,y+d)</text>'
    )
    lines.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_nof_sketch_svg(path: str) -> None:
    """Three NOF players: each sees the other two inputs."""
    w, h = 640, 280
    lines = [
        _svg_header(w, h),
        '<rect width="100%" height="100%" fill="#f8f9fa"/>',
        '<text x="320" y="30" text-anchor="middle" font-size="15" fill="#222">'
        "Number-on-Forehead: each player sees all but their own value</text>",
    ]
    players = (
        (160, 140, "Alice", "#1a5276", "sees Bob, Charlie"),
        (320, 200, "Bob", "#117a65", "sees Alice, Charlie"),
        (480, 140, "Charlie", "#7d3c98", "sees Alice, Bob"),
    )
    for cx, cy, name, color, cap in players:
        lines.append(f'<circle cx="{cx}" cy="{cy}" r="44" fill="{color}" opacity="0.9"/>')
        lines.append(
            f'<text x="{cx}" y="{cy+6}" text-anchor="middle" fill="white" font-size="14">{name}</text>'
        )
    lines.append(
        f'<text x="{cx}" y="{cy+62}" text-anchor="middle" font-size="10" fill="#555">{cap}</text>'
        )
    lines.append(
        '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">'
        '<polygon points="0 0, 8 4, 0 8" fill="#666"/></marker></defs>'
    )
    lines.append(
        '<path d="M 200 120 Q 320 60 440 120" fill="none" stroke="#666" stroke-width="1.5" '
        'marker-end="url(#arr)"/>'
    )
    lines.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    out_dir = os.path.dirname(os.path.abspath(__file__))
    paths = [
        ("density_comparison.svg", write_density_svg),
        ("heatmap_lift_vs_random.svg", write_heatmap_svg),
        ("lift_projection.svg", write_lift_projection_svg),
        ("nof_sketch.svg", write_nof_sketch_svg),
    ]
    for name, fn in paths:
        p = os.path.join(out_dir, name)
        fn(p)
        print("Wrote:", p)


if __name__ == "__main__":
    main()
