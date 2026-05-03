# Diagonal drop and asymmetric directions (§7.1 narrative)

This note is a **reader’s guide** to one structural idea in *Quasipolynomial bounds for the corners theorem* ([arXiv:2504.07006](https://arxiv.org/abs/2504.07006)): handling the **diagonal** direction in $G \times G$ differently from the **horizontal** and **vertical** coordinate directions so that certain multilinearity / uniformity estimates do not incur **tower-type** (iterated logarithm) losses.

**Disclaimer.** This repository does **not** reimplement the proof. Section numbers refer to the arXiv PDF you maintain locally (the Cursor workspace path is not portable). Cross-check §7.1 and Definition 6.3 in your copy.

---

## Why “symmetric corners” intuition is incomplete

The geometric picture of a corner $(x,y),(x+d,y),(x,y+d)$ is symmetric under swapping the two arms. In **analysis** on $G \times G$, however, the representation theory / Fourier side distinguishes:

- **coordinate** bilinear forms tied to $x$ and $y$ separately, and  
- **diagonal-type** expressions where $x$ and $y$ enter **together** (e.g. along a homomorphism $G \times G \to G$ like $(x,y) \mapsto x+y$ or related “diagonal” subobjects).

If one treats all directions identically, bookkeeping can force losses that accumulate like **towers** in $\log$. The paper’s **diagonal drop** is (informally) the design choice to **not** let diagonal fluctuations propagate through the same estimates as the pure $X$– and $Y$–type fluctuations—so the iteration yields **quasipolynomial** savings rather than doubly-logarithmic relics of older uniformity programs.

---

## $D$ vs $X$ and $Y$ (informal)

Think of three families of “structured directions” in data on $G \times G$:

| Direction flavor | Verbal role | Why it matters here |
|------------------|-------------|---------------------|
| $X$-type | Mass biased along vertical fibers / first coordinate | Matches one arm of a corner |
| $Y$-type | Mass biased along horizontal fibers / second coordinate | Matches the other arm |
| **Diagonal $D$** | Mass biased along **diagonal-type** phase relations (e.g. $x+y$ or dual pairing patterns in your normalization) | Can dominate unless **controlled separately** from $X$ and $Y$ |

**Algebraic spread** (control on approximate subgroups / Fourier mass not concentrated on low-complexity cosets) is the usual language for $X$ and $Y$. **$\ell_1$-spread** or analogous **metric** control on the diagonal is the informal gloss for why $D$ is “different”: diagonal fluctuations can be **large in $\ell_1$ mass** while still compatible with **algebraic** pseudorandomness in the side directions—so estimates that merge $D$ with $X,Y$ can **overcount** and lose efficiency.

---

## How this repo relates

- **Behrend lift** $A = \{(x,y): x+2y \in S\}$ is already **anisotropic**: mass lies on **lines** $x+2y=t$—a diagonal-type fiber **in coordinate space**, while corner detection is **axis-aligned**. That mismatch is why naive digit-split embeddings can break the AP–corner obstruction even when the 1D shell is structured.
- **Grid Norm pipe** exports treat coordinates explicitly so your **detector** repo can assign multilinear forms along $X$, $Y$, and any diagonal channel you define—**mirroring** the paper’s separation of diagonal vs coordinate uniformity (implementation lives in your detector, not here).

---

## For Exactly-$N$ / NOF applications

When you reduce corners bounds to **communication** lower bounds, the cost of a protocol often scales with **dimension of Bohr sets** or related parameters. **Diagonal drop** is the proof-side reason those dimensions stay polynomial rather than tower-sized—link your slides’ “regularity” statements to **Definition 6.3** and §7.1 in the paper when attributing the quantitative saving.

---

## Suggested citation for presentations

> Jaber–Liu–Lovett–Ostuni–Sawhney (2025), arXiv:2504.07006 — **diagonal vs coordinate** uniformity (§7.1); compare Behrend **lift anisotropy** in the companion code.
