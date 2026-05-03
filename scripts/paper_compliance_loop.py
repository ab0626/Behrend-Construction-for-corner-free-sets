#!/usr/bin/env python3
"""
Master validation loop: build a paper lift near a target density, export grid_norm_pipe_v1,
optionally invoke an external Grid Norm detector, and write a Paper Compliance Report.

This repo does not ship the detector; pass --detector-cmd to pipe JSON into your tooling.

Usage (from repo root):
  python scripts/paper_compliance_loop.py --target-alpha 0.02 --write-dir reports/run1
  python scripts/paper_compliance_loop.py --d 7 --k 5 --no-search --write-dir out \\
      --detector-cmd "python -m your_grid_norm --json {json_path}"
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import behrend_corner_free as b
import research_extensions as rex


def run_detector_subprocess(cmd_template: str, json_path: str) -> dict[str, Any]:
    """Replace {json_path} in cmd_template; capture stdout/stderr; try JSON-parse stdout."""
    cmd = cmd_template.format(json_path=json_path)
    proc = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    out: dict[str, Any] = {
        "exit_code": proc.returncode,
        "stderr_tail": (proc.stderr or "")[-4000:],
    }
    raw = (proc.stdout or "").strip()
    if raw:
        try:
            out["parsed_json"] = json.loads(raw)
        except json.JSONDecodeError:
            out["stdout_text"] = raw[:8000]
    return out


def write_report(
    write_dir: str,
    *,
    pl: b.PaperLiftGrid,
    alpha: float,
    alpha_target: Optional[float],
    detector_result: Optional[dict[str, Any]],
    proxy: float,
    reference: str,
) -> None:
    os.makedirs(write_dir, exist_ok=True)
    corner = b.brute_corner_check(pl.points)
    ap = b.find_three_term_ap(set(pl.one_d_set))

    payload = {
        "reference": reference,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "construction": "paper_lift",
        "target_density_alpha": alpha_target,
        "achieved_density_alpha": alpha,
        "parameters": {
            "d": pl.d,
            "k": pl.k,
            "sum_sq": pl.sum_sq,
            "grid_n": pl.grid_n,
            "|S|": len(pl.one_d_set),
            "|A|": pl.size,
        },
        "verification": {
            "axis_corner_in_A": corner is not None,
            "three_term_ap_in_shell": ap is not None,
        },
        "diagnostics": {
            "row_clumpiness_proxy_max_over_mean": proxy,
            "note": "Proxy is informal; use your grid-norm detector for uniformity metrics.",
        },
        "grid_norm_detector": detector_result,
        "compliance_narrative": [
            "Lift A = {(x,y) in [n]^2 : x+2y in S} with S a 3-AP-free sphere slice.",
            "If S has no 3-term AP, axis corners in A are ruled out (projection equivalence).",
            "Upper-bound / grid-norm detection is external: pass --detector-cmd to attach your tool.",
        ],
    }

    json_path = os.path.join(write_dir, "paper_compliance_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    md_path = os.path.join(write_dir, "paper_compliance_report.md")
    lines = [
        "# Paper Compliance Report",
        "",
        f"- **Reference:** {reference}",
        f"- **UTC:** {payload['generated_utc']}",
        "",
        "## Construction",
        "",
        f"- Density $|A|/n^2$ = **{alpha:.6g}** (grid side $n={pl.grid_n}$).",
    ]
    if alpha_target is not None:
        lines.append(f"- Target density $\\alpha$ was **{alpha_target:.6g}**.")
    lines.extend(
        [
            f"- Parameters: $d={pl.d}$, $k={pl.k}$, $\\sum_i x_i^2={pl.sum_sq}$, $|S|={len(pl.one_d_set)}$, $|A|={pl.size}$.",
            "",
            "## Verification",
            "",
            f"- Axis corner in $A$: **{'YES — FAIL' if corner else 'no'}**.",
            f"- 3-term AP in shell $S$: **{'YES — lift guarantee fails' if ap else 'no'}**.",
            f"- Row clumpiness proxy (max/mean column count along $y$): **{proxy:.3f}**.",
            "",
            "## Detector",
            "",
        ]
    )
    if detector_result:
        lines.append("```json")
        lines.append(json.dumps(detector_result, indent=2)[:6000])
        lines.append("```")
    else:
        lines.append("*No external detector run (`--detector-cmd` omitted).*")
    lines.extend(["", "## Narrative checklist", ""])
    for item in payload["compliance_narrative"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"Machine-readable: `{os.path.basename(json_path)}`.")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    p = argparse.ArgumentParser(
        description="Behrend lift → grid_norm JSON → optional detector → compliance report"
    )
    p.add_argument(
        "--target-alpha",
        type=float,
        default=None,
        help="Pick AP-free lift whose density is closest to this value (used unless --no-search).",
    )
    p.add_argument(
        "--no-search",
        action="store_true",
        help="Use explicit --d, --k, --S/--dense defaults instead of density search.",
    )
    p.add_argument("--d", type=int, default=7)
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--S", type=int, default=None, metavar="SUM_SQ")
    p.add_argument("--grid-n", type=int, default=None)
    p.add_argument("--write-dir", type=str, required=True, metavar="DIR")
    p.add_argument(
        "--detector-cmd",
        type=str,
        default=None,
        help='Shell command; use placeholder {json_path} for grid_norm_pipe JSON file.',
    )
    p.add_argument("--max-d", type=int, default=14)
    p.add_argument("--max-k", type=int, default=7)
    p.add_argument(
        "--reference",
        type=str,
        default="arXiv:2504.07006 (Jaber–Liu–Lovett–Ostuni–Sawhney)",
    )
    args = p.parse_args()

    if args.no_search:
        if args.S is None:
            sum_sq, _ = b.best_S_ap_free_max_count(args.d, args.k)
        else:
            sum_sq = args.S
        max_x = args.d**args.k - 1
        pl = b.build_paper_lift_grid(
            args.d, args.k, sum_sq, grid_n=args.grid_n, max_x=max_x
        )
        alpha = pl.size / (pl.grid_n * pl.grid_n)
        alpha_target = None
    else:
        tgt = 0.03 if args.target_alpha is None else args.target_alpha
        _d, _k, _sq, pl, alpha = rex.search_ap_free_lift_near_density(
            tgt,
            max_d=args.max_d,
            max_k=args.max_k,
        )
        alpha_target = tgt

    proxy = rex.clumpiness_proxy_row_ratio(set(pl.points), pl.grid_n)

    os.makedirs(args.write_dir, exist_ok=True)
    json_grid = os.path.join(args.write_dir, "grid_norm_pipe_export.json")
    rex.export_grid_norm_pipe_v1(
        json_grid,
        list(pl.points),
        construction="paper_lift",
        parameters={
            "d": pl.d,
            "k": pl.k,
            "sum_sq": pl.sum_sq,
            "grid_n": pl.grid_n,
            "density_alpha": alpha,
            "target_alpha": alpha_target,
        },
        grid_side_n=pl.grid_n,
    )

    detector_result: Optional[dict[str, Any]] = None
    if args.detector_cmd:
        detector_result = run_detector_subprocess(args.detector_cmd, json_grid)

    write_report(
        args.write_dir,
        pl=pl,
        alpha=alpha,
        alpha_target=alpha_target,
        detector_result=detector_result,
        proxy=proxy,
        reference=args.reference,
    )

    print(f"Wrote grid export: {json_grid}")
    print(
        f"Density |A|/n^2 = {alpha:.6g}  (n={pl.grid_n}, |A|={pl.size}, d={pl.d}, k={pl.k}, sum_sq={pl.sum_sq})"
    )
    print(f"Compliance report: {os.path.join(args.write_dir, 'paper_compliance_report.md')}")


if __name__ == "__main__":
    main()
