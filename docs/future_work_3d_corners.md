# Future work: 3D corners and higher-party NOF (conceptual)

This repository implements the **2D** corners pattern in $[n]^2$ and the communication story at **three** players (Alice–Bob–Charlie NOF). The paper also points toward **higher-dimensional** corner configurations—see **§1.3** (wording varies by PDF revision) in [arXiv:2504.07006](https://arxiv.org/abs/2504.07006).

---

## 3D corners (combinatorial pattern)

A **3D corner** in $[n]^3$ is a tuple of four points

$$
(x,y,z),\ (x+d,y,z),\ (x,y+d,z),\ (x,y,z+d)
$$

with $d \neq 0$ (the same step along each coordinate direction away from a common “corner” vertex). This is the natural **next rung** on the ladder of **multidimensional Szemerédi-type** patterns: 2D corners ↔ **length-$2$** combinatorial square; 3D corners ↔ a **3-parameter** simultaneous shift pattern.

**Status here:** not implemented—only the **2D** lift and checks exist in code.

---

## Communication link: 4-party NOF

Just as **2D corners** in $G \times G$ interface with **3-player** Number-on-Forehead (NOF) complexity (Exactly-$N$ style reductions in the paper), the **3D** corner picture is the structural shadow of **4-party** NOF: an extra hidden coordinate ↔ an extra player whose forehead hides information the others must correlate.

**Suggested “lab” narrative for slides:**

| Geometry | NOF players (informal) |
|----------|-------------------------|
| 2D corners in $G \times G$ | 3-player |
| 3D corners in $G \times G \times G$ | 4-player |

A future codebase could export **3D occupancy** tensors or slice projections for detector experiments; this repo remains the **2D Behrend + lift** reference implementation.

---

## Copy-out

Paste this section into an **Exactly-$N$** or **NOF** repo README under **Future work** if you want a single cross-link between additive patterns and communication depth.
