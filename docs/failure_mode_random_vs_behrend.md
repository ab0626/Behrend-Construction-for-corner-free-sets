# Failure mode: same density, different structure (for Grid Norm detectors)

This note is for anyone building a **Grid Norm / clumpiness detector** who wants a **negative control** next to the Behrend paper lift—so reviewers see the **Von Neumann–type** contrast: **density alone does not determine uniformity**.

---

## Setup (matched density)

Fix a grid side $n$ and a target density $\alpha \in (0,1)$.

1. **Behrend paper lift** $A_{\mathrm{Beh}} \subseteq [n]^2$: build an AP-free sphere slice $S$, then  
   $A_{\mathrm{Beh}} = \{(x,y): x+2y \in S\}$ (with $n$ large enough that the lift is nonempty).  
   Export with [`grid_norm_pipe_v1`](grid_norm_pipe_schema.md).

2. **Random Bernoulli mask** $A_{\mathrm{rand}}$: include each cell of $[n]^2$ independently with probability $\alpha'$, where $\alpha'$ is chosen so that **$\lvert A_{\mathrm{rand}}\rvert / n^2 \approx \alpha$** (e.g. resample until within a small tolerance, or condition on the realized count).

**Lesson:** Both sets can have **nearly the same** $\lvert A\rvert / n^2$, but **very different** combinatorics.

---

## What breaks (failure mode for “density-only” thinking)

- **$A_{\mathrm{rand}}$** is (typically) **not** corner-free: axis corners appear at density $\Theta(\alpha^3)$ in the random model (first-moment heuristics). Your detector’s **combinatorial** corner oracle should return **true** (corner found) on many random samples.

- **$A_{\mathrm{Beh}}$** (with AP-free $S$) is **corner-free** by the $x+2y$ projection—your oracle should return **false**.

So: **same density class**, **opposite** outcome on the **hard pattern** (corners).

---

## What you measure in the detector (Gowers / grid norm contrast)

The paper’s **order-2 grid norms** (often discussed via $(2,k)$-type multilinear averages) are designed to see **multilinear structure**, not just sparsity.

| Set | Corners? | Heuristic grid-norm / uniformity cartoon |
|-----|----------|------------------------------------------|
| $A_{\mathrm{rand}}$ at density $\alpha$ | **Usually yes** | Norms stay near a **random baseline** (small structured signal in the “pseudorandom” regime). |
| $A_{\mathrm{Beh}}$ at similar $\alpha$ | **No** (by construction) | Mass **aligns** on lines $x+2y=t$ → **large** multilinear bias vs the random baseline—the **“clumpiness”** your heatmap already suggests. |

This is the empirical **“Aha!”**: **forbidden corners force organized anisotropy** at comparable density; a **Bernoulli** set does **not** pay that price, and instead pays in **local pattern completion** (corners exist).

**Von Neumann picture (informal):** In the random case, obstructions to uniformity are **pure fluctuation**; in the structured lift, **curvature / fiber alignment** creates a **deterministic** multilinear signal that norms amplify—exactly the tension the upper-bound proof exploits.

---

## Reproducible workflow

1. Export `grid_norm_pipe_export.json` for $A_{\mathrm{Beh}}$ (CLI or `paper_compliance_loop.py`).
2. Generate $A_{\mathrm{rand}}$ with matched $\lvert A\rvert/n^2$, export the same JSON schema.
3. Run your detector on **both** files; tabulate **norm value**, **corner flag**, and optionally **`clumpiness_proxy_row_ratio`** from this repo’s diagnostics.

Copy this file into your **Grid Norm** repo’s `docs/` if you want the failure story co-located with ingestion code.
