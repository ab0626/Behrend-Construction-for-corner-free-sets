# Skew-corner-free constructions (benchmark modes)

This repo implements **pattern avoidance** for **skew corners** in $\mathbb{Z}^2$ (discrete grid), as an intermediate “easier” pattern relative to the full **axis corner** (same step on both arms), in the spirit of §2.2-style discussion in [Jaber et al., arXiv:2504.07006](https://arxiv.org/abs/2504.07006).

---

## Definitions

Fix a finite set $P \subseteq \mathbb{Z}^2$.

### Axis corner (standard)

Three distinct points

$$
(x,y),\quad (x+d,y),\quad (x,y+d)
$$

with $d \neq 0$. (Equivalently, a right isosceles “L” with equal leg length $|d|$.)

### Skew corner

Three distinct points

$$
(x,y),\quad (x+d,y),\quad (x,y+d')
$$

with $d, d' \neq 0$ and $d \neq d'$ (legs of different lengths in the $x$ and $y$ directions in the sign pattern used in `find_skew_corner`).

**Implementation note:** `research_extensions.find_skew_corner` matches the same geometric pattern; see code for the exact sign / ordering convention on the grid.

---

## Construction 1: Permutation graph (built-in)

For $m \ge 1$, pick a permutation $\pi$ of $\{1,\dots,m\}$ and set

$$
P_\pi = \{\, (i,\pi(i)) : 1 \le i \le m \,\} \subseteq [1,m]^2.
$$

### Lemma 1

$P_\pi$ contains **no skew corner** and **no axis corner**.

*Proof.* In any skew or axis corner, the first two points share the same $y$-coordinate. But for each $y$ there is **at most one** $i$ with $\pi(i)=y$ in a permutation’s graph, so a horizontal line $y=\text{const}$ contains **at most one** point of $P_\pi$. Thus the bottom edge of the “L” cannot be formed, and neither pattern occurs. ∎

**Density.** $|P_\pi| / m^2 = 1/m$. This is far sparser than Behrend-type lifts at comparable scales—it illustrates how skew avoidance alone does **not** encode the same density phenomenon as the corners problem for dense sets.

**Code:** `construct_skew_corner_free_permutation`.

---

## Construction 2: Greedy maximal set (built-in)

Visit every cell of $[1,m]^2$ in a **random order**. Maintain a set $P$, initially empty; **add** a cell iff the enlarged set still has **no skew corner** (checked by `find_skew_corner`).

### Properties

- Output is **skew-corner-free** by construction.
- Output is **maximal** skew-corner-free **with respect to the chosen traversal order** (no omitted cell can be added without creating a skew corner).
- **Need not** avoid axis corners: greedy filters only $d \neq d'$ patterns, so a triple with $d=d'$ could slip through.
- **Need not** be maximum possible cardinality over all skew-corner-free subsets of $[1,m]^2$.

**Code:** `construct_skew_corner_free_greedy`. Intended for small/medium $m$ (the inner check is not tuned for huge grids).

---

## CLI

```text
python behrend_corner_free.py --skew-free permutation --skew-free-m 40 --skew-free-seed 1 --skew-check
python behrend_corner_free.py --skew-free greedy --skew-free-m 16 --skew-free-seed 0 --export-grid-norm-json perm_grid.json
```

When `--skew-free` is not `none`, the Behrend $d,k$ run is **skipped**; use exports and checks as with the paper lift.

---

## Figure

Comparing axis vs skew “L” shapes (equal vs unequal leg lengths): see `figures/skew_vs_axis_corner.svg` (regenerate via `figures/generate_figures.py`).
