# Corner-Free Set Generator (Behrend Construction)

## Description

**Corner-Free Set Generator** is a small Python **research demo** tied to Behrend-type constructions and the corners problem. It builds a **1D digit-shell** set $S$ (integers whose base-$d$ digits lie on a fixed “sphere” $\sum_i x_i^2 = \mathrm{const}$), optionally chooses a shell with **no 3-term arithmetic progression**, then forms the paper-style **2D lift** $A = \{(x,y) \in [n]^2 : x+2y \in S\}$. A corner $(x,y),(x+d,y),(x,y+d)$ in $A$ would force a 3-AP in $S$; the script **searches for such corners** so you can contrast the rigorous lift with a **naive digit-split** embedding (which need not stay corner-free). Stdlib-only **SVG figures** illustrate the projection, density intuition, heatmaps, and an NOF sketch for talks.

**Run**

```bash
python behrend_corner_free.py --help
python behrend_corner_free.py --demo
python behrend_corner_free.py --mode paper
python behrend_corner_free.py --mode digit-split
```

**Figures (optional, stdlib-only)** — regenerates every chart in a few seconds:

```bash
python figures/generate_figures.py
```

**Requirements:** Python **3.9+** (stdlib only for `behrend_corner_free.py` and `figures/generate_figures.py`).

**CLI (main script):** `python behrend_corner_free.py` defaults to **`--mode paper`** (AP-free shell + `x+2y` lift). Useful flags: `--mode digit-split`, `--d`, `--k`, `--S`, `--grid-n`, `--dense-shell`, `--list`, `--demo`. See `--help`.

**Tests:** `python -m unittest discover -s tests -p "test_*.py" -v` (stdlib only; covers digit shell, 3-AP check, paper lift, digit-split corner, corner oracles).

**Mathematical notation (GitHub):** Inline math uses `$...$`; display uses `$$` on its own lines ([GitHub math docs](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions)). In markdown **tables**, avoid raw `|` inside formulas—use `\lvert`, `\rvert`, or `\lVert`/`\rVert` for cardinality/norms.

## Visual gallery (inline)

| Lift schematic | Density comparison | Heatmap (random vs lift) | NOF sketch |
|:---:|:---:|:---:|:---:|
| ![Lift: 3-AP to corner](figures/lift_projection.svg) | ![Density vs N](figures/density_comparison.svg) | ![Heatmaps](figures/heatmap_lift_vs_random.svg) | ![NOF players](figures/nof_sketch.svg) |

*Regenerate before exporting: `python figures/generate_figures.py`.*

## Formal proofs (where they live)

| What | Where |
|------|--------|
| **Full proofs** (grid norms, relative sifting, main theorem) | **Jaber–Liu–Lovett–Ostuni–Sawhney (2025):** [arXiv:2504.07006](https://arxiv.org/abs/2504.07006). This repo is a **computational companion**, not a LaTeX rewrite. |
| **Lift-only argument** (corner in $A$ $\Rightarrow$ 3-AP in $S$ for $x+2y$) | Short proof sketch in the **module docstring** at the top of [`behrend_corner_free.py`](behrend_corner_free.py). |
| **Empirical checks** | `find_three_term_ap`, `brute_corner_check`, `find_corner_smart` in the same file—they **verify instances**, they do not replace the paper’s proofs. |

## Branches and hosting

- **This repository** tracks everything on **`main`** ([`ab0626/Behrend-Construction-for-corner-free-sets`](https://github.com/ab0626/Behrend-Construction-for-corner-free-sets)). You do **not** need extra branches unless you want a separate line of work (e.g. `slides`, `gh-pages`, or a course hand-in tag).
- On GitHub, **each branch** has its **own** `README.md` and `figures/`—merge or cherry-pick if you split work across branches.
- README images use **relative** paths (`figures/…`). If a viewer blocks inline SVG, open the files locally or export to PNG.

## How this code aligns with the paper (Jaber–Liu–Lovett–Ostuni–Sawhney)

Primary reference: **Michael Jaber, Yang P. Liu, Shachar Lovett, Anthony Ostuni, Mehtaab Sawhney**, *Quasipolynomial bounds for the corners theorem*, [arXiv:2504.07006](https://arxiv.org/abs/2504.07006). That work proves (for corner-free $A \subseteq G \times G$) an upper bound of the form $|A| \le |G|^2 \exp(-(\log|G|)^{\Omega(1)})$, and derives communication consequences in the **3-player Number-on-Forehead** model. This repository does **not** reimplement those proofs; it is a **hands-on companion** for Behrend-type **inputs** and the **$x+2y$** lift.

### 1. Curvature, sphere shells, and 3-AP freeness

Behrend’s idea is to place digits on a **high-dimensional sphere** (fixed $\sum_i x_i^2$), so “most” **linear** relations that would create a **3-term AP** fail for **geometric** reasons—often described informally as **curvature**: three collinear points in digit space typically miss the shell. In this project, the **1D** object $S$ is a **discrete** sphere slice in base $d$; when you additionally enforce **no 3-AP** among shells (`best_S_ap_free_max_count`), you make explicit the hypothesis needed for the **$x+2y$** lift to rule out **axis corners** in $A$. That is the same **Roth / corners** bridge the paper exploits via **projections** (corners $\leftrightarrow$ 3-APs).

### 2. Relative sifting and “sparse but structured”

A recurring theme in modern arguments is **relative** or **sparse** analysis: extracting structure **inside** a **sparse** set or majorant. Your lifted set $A=\{(x,y):x+2y\in S\}$ is **sparse** in $[n]^2$, yet it is **highly structured**—mass lies on **lines** $x+2y=t$. That is the **anisotropic clumpiness** the heatmap is meant to suggest: a **pseudorandom** set has **small** multilinear uniformity (order-2 **grid / box** control), while a **structured** lift produces **large** multilinear biases—exactly the kind of **signal** a **density increment** or **sifting** step must detect in a corner-free **upper-bound** proof. (The README still does **not** compute norms numerically; it only **visualizes** support.)

### 3. The Behrend regime vs older density losses

For decades, **lower bounds** for AP-free / corner-related phenomena have hovered near **Behrend’s** scale—roughly **$\exp(-\Theta(\sqrt{\log N}))$** in $\mathbb{Z}/N\mathbb{Z}$ (up to log factors in different normalizations). Many **earlier** upper-bound arguments in related areas incurred much weaker losses—often caricatured as **doubly logarithmic** ($1/\log\log N$-type savings). The 2025 corners result is significant because the **upper bound** on corner-free sets now approaches that **quasipolynomial / Behrend-type** scale from the **other side**, nearly **matching** the classical construction density in a way prior bounds did not.

> **Professor-ready one-liner:** While **Shkredov-type** bounds from the mid-2000s era often entailed only **doubly logarithmic** density savings in related uniformity programs, Behrend-type constructions instead live at density $\exp(-\Theta((\log N)^{1/2}))$. Recent breakthroughs—notably **Jaber, Liu, Lovett, Ostuni, Sawhney (2025)** on [arXiv:2504.07006](https://arxiv.org/abs/2504.07006)—prove **quasipolynomial** upper bounds for corner-free sets, bringing the **provable** obstruction much closer to the **Behrend regime** the field has used as a lower-bound benchmark for decades.

### 4. NOF communication and Exactly-$N$

The paper explains how strong **corner-free-set** bounds imply **polynomial-length** lower bounds for **nondeterministic** protocols for **Exactly-$N$** in the **3-player NOF** model. Intuitively, **large structured** sets that **avoid corners** are the **combinatorial heart** of those lower-bound arguments; your generator exposes the **same lift geometry** (Section 4 heatmap + NOF sketch) that underpins that communication story.

---

## 1. Geometry of the lift (projection equivalence)

**Tag:** `lift-diagram`

The paper uses the fact that an **axis corner** in 2D forces a **3-term arithmetic progression** in 1D under the map $L(x,y)=x+2y$.

If $(x,y), (x+d,y), (x,y+d) \in A$ and $z=x+2y$, then

$$
z,\quad (x+d)+2y = z+d,\quad x+2(y+d)=z+2d \in S.
$$

So a corner in $A$ $\Rightarrow$ a 3-AP in $S$. The **inverse** direction (start from 3-AP-free $S$, define $A$ by $x+2y\in S$) is what this repository implements.

**Suggested slide image:** a single figure with (i) a 1D line marked $z, z+d, z+2d$ and (ii) the corresponding $L$-shape $(x,y), (x+d,y), (x,y+d)$ on a grid, with arrows labeled $L=x+2y$.

![Schematic: 3-AP in S and corner in A](figures/lift_projection.svg)

**Mermaid (logic flow for handouts / GitHub preview):**

```mermaid
flowchart LR
  subgraph oneD["1D set S"]
    z["z = x+2y"]
    zd["z+d"]
    z2d["z+2d"]
    z --> zd --> z2d
  end
  subgraph twoD["2D grid A"]
    P1["(x, y)"]
    P2["(x+d, y)"]
    P3["(x, y+d)"]
    P1 --> P2
    P1 --> P3
  end
  P1 -.->|L| z
  P2 -.->|L| zd
  P3 -.->|L| z2d
```

---

## 2. Behrend regime vs stylized bounds

**Tag:** `density-chart`

The manuscript emphasizes moving from very weak **doubly logarithmic** decay toward **quasipolynomial-type** behavior $\exp(-(\log N)^c)$. Your generator lives in the **Behrend-type** digit-shell world.

**Suggested slide:** a line chart with three traces (qualitative):

| Trace | Role |
|--------|------|
| $1/\log\log N$ (normalized) | “old-scale” proxy — nearly flat for large $N$ |
| $\exp(-(\log N)^{1/2})$ (normalized) | stylized “new-scale” decay |
| **Empirical** $\lvert S\rvert/d^k$ | from `best_S_ap_free_max_count` + `build_behrend_sphere_slice` at $N=d^k$ |

![Density: stylized bounds vs shell fraction](figures/density_comparison.svg)

*Edit `figures/generate_figures.py` to change the $d,k$ sweep for the red points.*

---

## 3. NOF communication (Project 1)

**Tag:** `nof-sketch`

If your **Project 1** code uses a Number-on-Forehead (NOF) model (players see all inputs except their own), use a **three-player** sketch for the talk track:

- **Alice** sees Bob’s and Charlie’s numbers, not her own.
- **Bob** sees Alice’s and Charlie’s.
- **Charlie** sees Alice’s and Bob’s.

**Suggested slide:** stick figures with integers on foreheads and gaze arrows; caption: “local view = global input minus one coordinate.”

![NOF: each player sees the other two](figures/nof_sketch.svg)

*(This repo is Project 2–centric; wire your Player / Referee classes from Project 1 into the same deck if both are submitted together.)*

---

## 4. Grid norm “clumpiness” (heatmaps)

**Tag:** `heatmap-clumpiness`

**Intuition:** a **uniform random** subset of the same density looks **noise-like** (low structured clumping in a box norm picture); the **paper lift** of a thin shell often shows **anisotropic** structure along lines $x+2y=\mathrm{const}$.

**Suggested slide:** side-by-side heatmaps of occupancy on $[1,n]^2$:

| Panel | Content |
|--------|---------|
| Left | random Bernoulli mask with $p \approx \lvert A\rvert/n^2$ |
| Right | paper lift $A=\{(x,y): x+2y\in S\}$ |

`figures/generate_figures.py` uses the **smallest** $n$ for which $x+2y$ can reach **all** of $S$ (up to $d^k$), then **downsamples** to a fixed display size for the SVG. *Capping* $n$ at 64 (or any value **below** that minimum) made the lift **empty** and both panels black.

The heatmap SVG uses **merged rectangles** (not thousands of 2px squares) so it stays fast to open; GitHub’s README preview may **shrink** the figure—click **Open raw** or download the SVG for full size.

![Random mask vs paper lift occupancy](figures/heatmap_lift_vs_random.svg)

### Why the two panels look different (paper-style reasoning)

The manuscript’s **Gowers-type grid norms** (e.g. $(2,k)$-grid / box-type uniformity) are designed to detect **multilinear structure** in a set $A \subseteq [n]^2$. Your figure is only a **pixel picture** of support, but it matches the *direction* of that theory:

- **Left (random):** Let $\alpha = |A|/n^2$ and consider the balanced indicator $f = \mathbf{1}_A - \alpha$. For a genuinely random (Bernoulli) set at density $\alpha$, **local averages along rectangles and along lines fluctuate like noise**—there is no organized “clumpiness” for a **density increment** step to lock onto. In a cartoon of **order-2 grid / box control**, one expects $\|f\|_{\mathrm{grid}}$ to stay **small** (on the order of $\alpha^2$ in a coarse heuristic).

- **Right (paper lift):** Membership is $(x,y) \in A \iff x+2y \in S$. Every point lies on one of the **affine lines** $x+2y = t$. Even when $S$ is sparse in $\mathbb{Z}$, the lift **concentrates** $A$ on a **family of parallel lines in the plane**—visible as **stripes / ridges** in the heatmap. That **anisotropic alignment** is exactly the kind of **non-pseudorandom** pattern a **grid norm** is meant to **amplify**: heuristically $\|f\|_{\mathrm{grid}}$ is **large** (well above the $\alpha^2$ “random baseline”), signaling **hidden linear structure** compatible with the proof’s **relative sifting** / **density increment** engine (see [arXiv:2504.07006](https://arxiv.org/abs/2504.07006)).

*Caveat:* this repo does **not** compute a numerical grid norm—only the **occupancy** heatmap—so treat the table below as an **interpretive bridge** to the paper, not measured output.

### Relative / quasirandom “sifting” trade-off (interpretive)

| Metric | Random Bernoulli | Paper-aligned lift | Paper context |
|--------|------------------|--------------------|----------------|
| Grid / box-type norm (order-2 cartoon) | Very low ($\approx \alpha^2$ scale) | High ($\gg \alpha^2$ heuristically) | **Signal** that multilinear averages see structure |
| Sifting / increment step | No meaningful dense sub-rectangle | Dense structure along **line families** $x+2y=t$ | Where a **density increment** can **latch** |
| NOF / “Exactly-$N$” viewpoint (Project 1) | Near-uniform local views | Correlated local views under lift | Corners $\leftrightarrow$ **Exactly-$N$**-type obstructions (informal) |

### Suggested logic flow (for a written report)

1. **Random baseline (Von Neumann–type picture):** In a **random** dense set, corner counts are governed by **first-moment / independence** heuristics (schematically $\alpha^3$ at density $\alpha$ in the random model). There is **no** structured obstruction for a multilinear form to exploit—matching the **flat** left panel.

2. **Density increment observation:** The **paper lift** panel is **not** pseudorandom along rectangles: mass **aligns** with **$x+2y$**. Use the heatmap as **visual evidence** that your construction is in the **structured** regime the paper’s norms are built to detect.

3. **“Diagonal vs sides” (optional narrative hook):** In proof sketches, one often keeps a **diagonal** (or a structured fiber) **dense** while forcing **spread** in complementary coordinates—avoiding **tower-type** bookkeeping in communication or counting. If you use NOF material (Project 1), you can analogize: **local views stay informative** without paying an exponential **round** cost. (Phrase this to match the exact lemma you cite from your PDF.)

### Follow-up (non-abelian lifts)

> **Question:** How does the **grid-norm / uniformity** picture change if the lift is taken over a **non-abelian** group instead of $\mathbb{Z}_N$?

The paper’s opening (e.g. **Section 1.1** in many editions) explains why **abelian** quasipolynomial-type bounds can be **exported** to **all finite groups**—a natural place to start if you extend this codebase beyond $\mathbb{Z}$.

---

## Summary table (README ↔ paper story)

| Visual type | Content | Technical link |
|-------------|---------|------------------|
| Diagram | 1D 3-AP $\{z,z+d,z+2d\}$ vs 2D corner | projection / lift $x+2y$ |
| Line chart | decay / density vs $N$ | quasipolynomial-type bounds vs weak bounds |
| Logic map | Alice / Bob / Charlie NOF views | multi-party NOF / “Exactly-$N$” viewpoint (Project 1) |
| Heat map | random vs paper lift occupancy | anisotropy / **grid-norm** cartoon (structured vs pseudorandom) |

---

## File map

| File | Purpose |
|------|---------|
| `behrend_corner_free.py` | Sphere shell, `paper_lift_from_set`, AP-free shell picker, corner checks, CLI |
| `figures/generate_figures.py` | Writes `density_comparison.svg`, `heatmap_lift_vs_random.svg`, `lift_projection.svg`, `nof_sketch.svg` |
| `tests/test_behrend_corner_free.py` | `unittest` suite (sphere slice, AP detection, paper lift vs digit-split) |
| `scripts/format_readme_math.py` | Optional: normalize TeX delimiters in `README.md` |
| `README.md` | Visual proof-of-concept guide (this file) |
| `LICENSE` | MIT (see repo root) |
| `.gitignore` | Python / venv noise |

Paper context: [arXiv:2504.07006](https://arxiv.org/abs/2504.07006) (corners, Roth-type links, Behrend-type scale — adjust section citations to match your PDF edition).