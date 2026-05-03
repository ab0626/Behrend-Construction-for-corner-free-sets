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


def write_quantitative_saving_arc_svg(path: str, w: int = 820, h: int = 420) -> None:
    """
    Schematic "quantitative arc": three *illustrative* density-savings shapes vs log N.
    Not literal theorem constants—pedagogical comparison for talks (see figure disclaimer).
    """
    pad_l, pad_r, pad_t, pad_b = 78, 160, 45, 52
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b

    def x_pix(log_n: float) -> float:
        lo, hi = math.log(20), math.log(2e6)
        t = (log_n - lo) / (hi - lo)
        return pad_l + max(0.0, min(1.0, t)) * iw

    def y_pix(v: float) -> float:
        return pad_t + (1.0 - max(0.0, min(1.0, v))) * ih

    Ns = [20 * (2e6 / 20) ** (i / 199) for i in range(200)]
    shk: list[float] = []
    jab: list[float] = []
    beh: list[float] = []
    for N in Ns:
        log_n = math.log(max(N, math.e))
        shk.append(1.0 / math.log(max(math.log(N), 2.0)))
        jab.append(math.exp(-(log_n**0.38)))
        beh.append(math.exp(-math.sqrt(log_n)))

    def norm(xs: list[float]) -> list[float]:
        lo, hi = min(xs), max(xs)
        if hi <= lo:
            return [0.5] * len(xs)
        return [(v - lo) / (hi - lo) for v in xs]

    s1, s2, s3 = norm(shk), norm(jab), norm(beh)
    p1 = [(x_pix(math.log(N)), y_pix(v)) for N, v in zip(Ns, s1)]
    p2 = [(x_pix(math.log(N)), y_pix(v)) for N, v in zip(Ns, s2)]
    p3 = [(x_pix(math.log(N)), y_pix(v)) for N, v in zip(Ns, s3)]

    def polyline_pts(pts: list[tuple[float, float]]) -> str:
        return " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)

    tex_log = r"$\log N$"
    tex_sim_ll = r"$\sim 1/\log\log N$"
    tex_jab = r"$\exp(-(\log N)^{0.38})$"
    tex_beh = r"$\exp(-\sqrt{\log N})$"

    parts = [
        _svg_header(w, h),
        '<rect width="100%" height="100%" fill="#fafafa"/>',
        f'<text x="{(pad_l + w - pad_r)//2}" y="26" text-anchor="middle" font-size="15" fill="#222">'
        f"Quantitative arc (schematic): savings / density scales vs {tex_log}</text>",
        f'<text x="{(pad_l + w - pad_r)//2}" y="44" text-anchor="middle" font-size="10" fill="#666">'
        "Illustrative normalization only — not literal constants from any single theorem</text>",
        f'<polyline fill="none" stroke="#888" stroke-width="2.2" points="{polyline_pts(p1)}"/>',
        f'<polyline fill="none" stroke="#b9770e" stroke-width="2.2" points="{polyline_pts(p2)}"/>',
        f'<polyline fill="none" stroke="#1a5276" stroke-width="2.2" points="{polyline_pts(p3)}"/>',
        f'<text x="{pad_l}" y="{h-22}" font-size="11" fill="#555">Horizontal: {tex_log}</text>',
        f'<text x="{pad_l}" y="{h-8}" font-size="10" fill="#888">Vertical: min–max normalized curves for readability</text>',
        f'<text x="{w - pad_r + 8}" y="{pad_t + 22}" font-size="11" fill="#888">Shkredov-type scale</text>',
        f'<text x="{w - pad_r + 8}" y="{pad_t + 40}" font-size="11" fill="#b9770e">Jaber et al. (2025) regime</text>',
        f'<text x="{w - pad_r + 8}" y="{pad_t + 58}" font-size="11" fill="#1a5276">Behrend lower-bound scale</text>',
        f'<text x="{w - pad_r + 8}" y="{pad_t + 76}" font-size="9" fill="#999">{tex_sim_ll}</text>',
        f'<text x="{w - pad_r + 8}" y="{pad_t + 90}" font-size="9" fill="#999">{tex_jab}</text>',
        f'<text x="{w - pad_r + 8}" y="{pad_t + 104}" font-size="9" fill="#999">{tex_beh}</text>',
        "</svg>",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def _downsample_grid(
    points: set[tuple[int, int]], n_src: int, n_dst: int
) -> list[list[float]]:
    """Map [1,n_src]^2 occupancy into n_dst×n_dst bins (linear binning)."""
    m = [[0.0] * n_dst for _ in range(n_dst)]
    if n_src < 1 or n_dst < 1:
        return m
    for x, y in points:
        if not (1 <= x <= n_src and 1 <= y <= n_src):
            continue
        xd = min(n_dst - 1, (x - 1) * n_dst // n_src)
        yd = min(n_dst - 1, (y - 1) * n_dst // n_src)
        m[yd][xd] = 1.0
    return m


def write_heatmap_svg(path: str, max_display: int = 56) -> None:
    """
    Paper lift vs matched-density Bernoulli mask.

    Important: the grid side must be large enough that x+2y can hit values in S.
    Previously we wrongly used min(64, n_needed), which forced n=64 while S could
    require n≈800 — then x+2y≤192 never reached large shell elements, giving an
    empty lift and p=0 (blank figure).
    """
    import behrend_corner_free as b

    d, k = 7, 4
    max_x = d**k - 1
    sum_sq, _ = b.best_S_ap_free_max_count(d, k, max_x=max_x)
    s1 = b.build_behrend_sphere_slice(d, k, sum_sq, max_x=max_x)

    n_full = b.default_grid_n_for_lift(s1, max_x)
    lift = set(b.paper_lift_from_set(s1, n_full))
    # Fallback if shell has only unreachable residues (e.g. pathological small instance)
    if not lift:
        d, k = 5, 4
        max_x = d**k - 1
        sum_sq, _ = b.best_S_ap_free_max_count(d, k, max_x=max_x)
        s1 = b.build_behrend_sphere_slice(d, k, sum_sq, max_x=max_x)
        n_full = b.default_grid_n_for_lift(s1, max_x)
        lift = set(b.paper_lift_from_set(s1, n_full))

    n_cells = n_full * n_full
    p = len(lift) / n_cells if n_cells else 0.0

    disp = min(max_display, n_full)
    if disp < 1:
        disp = 1
    if n_full <= disp:
        m_lift = [[0.0] * n_full for _ in range(n_full)]
        for x, y in lift:
            m_lift[y - 1][x - 1] = 1.0
    else:
        m_lift = _downsample_grid(lift, n_full, disp)

    rand = [[0.0] * disp for _ in range(disp)]
    seed = 12345
    for i in range(disp):
        for j in range(disp):
            seed = (1103515245 * seed + 12345) % (2**31)
            rand[i][j] = 1.0 if (seed / 2**31) < p else 0.0

    # Readable cell size in README / new-tab preview (tiny rects looked blank until zoomed)
    cell = max(7, min(14, 720 // (2 * disp + 20)))
    gap = 16
    bw = disp * cell + gap + disp * cell + 48
    bh = disp * cell + 88

    parts = [
        _svg_header(bw, bh),
        "<desc>Side-by-side occupancy: Bernoulli noise vs paper lift x+2y in S</desc>",
        '<rect width="100%" height="100%" fill="#eceff4"/>',
        '<g shape-rendering="crispEdges">',
    ]

    def rect_color(v: float) -> str:
        if v <= 0.001:
            return "#d8dee9"
        return "#bf616a"

    def draw_grid_rle(
        data: list[list[float]], ox: int, oy: int, title: str
    ) -> None:
        """Horizontal run-length merge: fewer DOM nodes, faster GitHub/raw SVG view."""
        parts.append(
            f'<text x="{ox + disp*cell//2}" y="{oy-12}" text-anchor="middle" '
            f'fill="#2e3440" font-size="12">{title}</text>'
        )
        ch = cell - 1
        for i in range(disp):
            row = data[i]
            j = 0
            while j < disp:
                v = row[j]
                k = j + 1
                while k < disp and row[k] == v:
                    k += 1
                w = (k - j) * cell - 1
                c = rect_color(v)
                parts.append(
                    f'<rect x="{ox+j*cell}" y="{oy+i*cell}" width="{w}" height="{ch}" '
                    f'fill="{c}" stroke="#b9c3d6" stroke-width="0.25"/>'
                )
                j = k

    sub = f"display {disp}x{disp}" if disp < n_full else f"{n_full}x{n_full}"
    draw_grid_rle(
        rand,
        24,
        56,
        f"random Bernoulli(p), p={p:.4f} (same density as right)",
    )
    draw_grid_rle(
        m_lift,
        24 + disp * cell + gap,
        56,
        f"paper lift (|A|={len(lift)}, |S|={len(s1)}, grid n={n_full}; {sub})",
    )
    parts.append("</g>")
    parts.append(
        f'<text x="{bw//2}" y="{bh-18}" text-anchor="middle" fill="#4c566a" font-size="11">'
        "Heatmaps — diagonal stripes: structured lift vs noise (open raw SVG if preview is small)</text>"
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


def write_shell_profile_svg(path: str) -> None:
    """Shell-density histogram (small d,k for speed)."""
    import research_extensions as rex

    rex.write_shell_density_svg(path, d=5, k=4, max_x=5**4 - 1)


def write_skew_vs_axis_corner_svg(path: str, w: int = 640, h: int = 280) -> None:
    """
    Two small grids: axis corner (d = d') vs skew corner (d ≠ d').
    y increases downward in SVG for readability.
    """
    cell = 36
    pad = 24
    # Left panel: axis (0,0),(2,0),(0,2) in local 0..3 coords
    ox, oy = pad, pad
    def cell_rect(gx: int, gy: int) -> str:
        cx = ox + gx * cell
        cy = oy + gy * cell
        return (
            f'<rect x="{cx}" y="{cy}" width="{cell-2}" height="{cell-2}" '
            f'fill="#e8e8e8" stroke="#bbb"/>'
        )

    lines = [
        _svg_header(w, h),
        '<rect width="100%" height="100%" fill="#fafafa"/>',
        f'<text x="{w//2}" y="20" text-anchor="middle" font-size="14" fill="#222">'
        "Axis corner (d = d′) vs skew corner (d ≠ d′)</text>",
    ]
    for gx in range(4):
        for gy in range(4):
            lines.append(cell_rect(gx, gy))
    # axis corner points at (0,0), (2,0), (0,2) — circles
    pts_axis = [(0, 0), (2, 0), (0, 2)]
    for gx, gy in pts_axis:
        cx = ox + gx * cell + cell // 2
        cy = oy + gy * cell + cell // 2
        lines.append(
            f'<circle cx="{cx}" cy="{cy}" r="10" fill="#c0392b" stroke="#922b21"/>'
        )
    lines.append(
        f'<text x="{ox}" y="{oy + 4 * cell + 22}" font-size="11" fill="#444">'
        r"Standard corner: (x,y), (x+d,y), (x,y+d)</text>"
    )

    # Right panel
    ox2 = w // 2 + 20
    for gx in range(4):
        for gy in range(4):
            cx = ox2 + gx * cell
            cy = oy + gy * cell
            lines.append(
                f'<rect x="{cx}" y="{cy}" width="{cell-2}" height="{cell-2}" '
                f'fill="#e8e8e8" stroke="#bbb"/>'
            )
    pts_skew = [(0, 0), (2, 0), (0, 3)]
    for gx, gy in pts_skew:
        cx = ox2 + gx * cell + cell // 2
        cy = oy + gy * cell + cell // 2
        lines.append(
            f'<circle cx="{cx}" cy="{cy}" r="10" fill="#1a5276" stroke="#0e3a52"/>'
        )
    lines.append(
        f'<text x="{ox2}" y="{oy + 4 * cell + 22}" font-size="11" fill="#444">'
        r"Skew corner: (x,y), (x+d,y), (x,y+d′), d ≠ d′</text>"
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
        ("shell_density_profile.svg", write_shell_profile_svg),
        ("skew_vs_axis_corner.svg", write_skew_vs_axis_corner_svg),
        ("quantitative_saving_arc.svg", write_quantitative_saving_arc_svg),
    ]
    for name, fn in paths:
        p = os.path.join(out_dir, name)
        fn(p)
        print("Wrote:", p)


if __name__ == "__main__":
    main()
