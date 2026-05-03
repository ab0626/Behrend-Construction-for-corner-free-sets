# `grid_norm_pipe_v1` — export schema for grid-norm tooling

This document describes the JSON (and optional CSV) format produced by `research_extensions.export_grid_norm_pipe_v1` and `export_grid_norm_pipe_csv`, so the **Grid Norm / clumpiness detector** (or any consumer) can load Behrend-lift or benchmark grids without an ad-hoc parser per run.

**Primary reference in code:** `research_extensions.py` — functions `export_grid_norm_pipe_v1`, `export_grid_norm_pipe_csv`.

**CLI:** `python behrend_corner_free.py ... --export-grid-norm-json out.json` and/or `--export-grid-norm-csv out.csv`

---

## Versioning

| Field | Value |
|--------|--------|
| `format` | Always the string `grid_norm_pipe_v1` |
| `schema_reference` | Repository path `docs/grid_norm_pipe_schema.md` (stable pointer for tooling) |

Breaking field renames or semantic changes should bump to `grid_norm_pipe_v2` and add a short migration note here.

---

## Top-level JSON object

| Key | Type | Meaning |
|-----|------|--------|
| `format` | `string` | `grid_norm_pipe_v1` |
| `schema_reference` | `string` | Path to this file |
| `coordinate_system` | `object` | How to interpret `x`, `y` (see below) |
| `bounding_box` | `object` | Axis-aligned box covering all points (min/max inclusive) |
| `grid_hint` | `object` | Optional ambient grid size (Behrend paper lift on `[1,n]^2`) |
| `occupancy` | `object` | Count and density inside the bounding box |
| `packed_xy` | `object` | `xs` and `ys` **parallel arrays** (same length, row-major sort order: sort by `(x,y)`) |
| `cells` | `array` | Redundant list of `{"x":int,"y":int}` (convenient for small sets; use `packed_xy` for large) |
| `provenance` | `object` | `generator`, `construction`, `parameters` |

### `coordinate_system`

- **`indexing`:** `one_based_inclusive` — first row/column index is `1`, not `0` (matches `behrend_corner_free.paper_lift_from_set` on `[1,n]×[1,n]`).
- **`x` / `y`:** `horizontal_increasing` and `vertical_increasing` in the usual Cartesian sense for the integer grid.
- **`notes`:** For consumers that use NumPy or image buffers with origin top-left, map explicitly: e.g. `i = x - 1`, `j = y - 1` in a 0-based `n×n` array, with care for your `y` convention.

### `occupancy.density_in_bounding_box`

$\text{density} = \lvert P \rvert \big/ \big( (x_{\max}-x_{\min}+1)(y_{\max}-y_{\min}+1) \big)$.

This is **not** always $1/n^2$ for the full ambient $[1,n]^2$ unless you also pass `grid_hint.nominal_side_n` and recompute externally.

### `provenance.construction`

Example values:

| Value | Meaning |
|--------|--------|
| `paper_lift` | Set $A=\{(x,y): x+2y \in S\}$ from Behrend shell |
| `digit_split` | Legacy digit-block map |
| `skew_free_permutation` | Permutation graph `(i,π(i))` |
| `skew_free_greedy` | Greedy maximal skew-corner-free set |

---

## CSV companion format (`export_grid_norm_pipe_csv`)

1. **Line 1:** `# ` followed by a single-line JSON object with at least `format`, `construction`, and `parameters`.
2. **Line 2:** Header `x,y`
3. **Remaining lines:** one occupied cell per row, integers separated by comma.

Tools that only accept CSV can parse line 1 as metadata and load coordinates from the body.

---

## Relation to `behrend_corner_free_grid_v1`

`export_run_json` uses format id `behrend_corner_free_grid_v1` (lighter provenance, optional `one_d_shell`). Use **`grid_norm_pipe_v1`** when you need **bounding box**, **packed arrays**, and **explicit coordinate conventions** for uniformity / grid-norm code paths.
