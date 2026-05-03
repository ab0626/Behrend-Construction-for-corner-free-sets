# $(2,k)$-grid norm: sensitivity to $k$ (warning guide)

Upper-bound arguments in [arXiv:2504.07006](https://arxiv.org/abs/2504.07006) use **multilinear uniformity** at **finite** complexity $k$. Your **detector** (outside this repo) that estimates a $(2,k)$-style grid norm inherits the same **trade-offs**.

---

## The two failure modes

| Symptom | Likely cause | What to try |
|--------|----------------|-------------|
| **Zero signal** (Behrend lift looks “random”) | $k$ **too small** for the density $\alpha$ | Increase $k$ until multilinear averages **see** line-of-sight structure (see heuristic below). |
| **Exploding variance / unstable estimates** | $k$ **too large** for your sample size or Monte Carlo budget | Decrease $k$, increase $n$, or average more independent random parallelepiped samples. |

---

## Heuristic: $k$ vs target density $\alpha$

In uniformity programs, the **relevant scale** is often **$\log(1/\alpha)$**: detecting structure at density $\alpha$ typically requires **complexity large enough** to resolve **$1/\alpha$-scale** combinatorics, but not so large that the **variance** of each norm estimate dominates.

**Rule of thumb (not a theorem from this repo):**

- Start with  
  $$k_0 \approx \lceil \log_2(1/\alpha) \rceil \quad\text{or}\quad k_0 \approx \lceil \ln(1/\alpha) \rceil$$  
  as a **first guess**, then **binary-search** $k$ in $[k_{\min}, k_{\max}]$ on a fixed Behrend export.

- If $\alpha \sim 10^{-2}$, try $k \in \{4,5,6,7\}$.  
- If $\alpha \sim 10^{-4}$, try $k$ a few steps **larger** before giving up on signal.

**Always** validate on the **paired** experiment in [`failure_mode_random_vs_behrend.md`](failure_mode_random_vs_behrend.md): at the **same** $\alpha$, the random set should sit near the **low-norm** baseline while the Behrend lift should **separate** once $k$ is in range.

---

## Practical checklist

1. Fix $n$ and export Behrend + random grids at matched $\lvert A\rvert/n^2$.
2. Sweep $k$ on **both**; plot norm vs $k$.
3. Choose a **plateau** where Behrend $\gg$ random and variance is still tolerable.
4. Document the chosen $(n,\alpha,k)$ in your detector README so others can reproduce.

Adjust lemma/definition numbers to match **your** arXiv PDF edition when citing the paper’s precise $(2,k)$ hypotheses.
