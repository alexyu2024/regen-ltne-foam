# L5P 2/4: method (a) Newton-Picard / RPM, p = 1-3

**Branch**: `pss/method-a`, from main at eab2432 (L5P tools and the reference already merged). Results are in
`results/L5P/methods/np{1,2,3}_*`, written as each run finished. This draft is updated as runs end.

Protocol: `docs/VERIFICATION.md`, L5P, as registered, with Amendment A1 (residual stop rule) and Amendment A2 (drift
tolerance from r_A2 = 0.998813). All runs start from the cycle-40 state. Total = 40 + method cycles + verification
cycles. The budget is 600 cycles after cycle 40, so a run that does not end is FAIL at 640.

**Natural marching to compare against: 4195 cycles** (k_nat = 4145 + 50; within tolerance from cycle 4156).

## Results so far

| run | status | total cycles (honest) | E | D | NR | M | result |
|---|---|---|---|---|---|---|---|
| np3 | budget reached, never stopped on its own | 639 | - | - | - | yes (3.1e-11; jumps <= 4.7e-16) | **FAIL** |
| np2 | running | | | | | | |
| np1 | queued | | | | | | |

The total for np3 is 639 rather than 640: the next iteration needs 4 cycles at once, and only 599 + 4 > 600 was
checked, so the run stopped at 599 method cycles.

## What happened in np3 (`np3_hist.csv`)

- **The Ritz values of H = V^T M V stay below the true slow multiplier.**
  - Iteration 1 gives 0.9957, 0.956 and 0.731.
  - From iteration 75 on there is a complex pair near 0.9963 ± 0.003i.
  - By iteration 149 the values are 0.99696 and 0.99683 ± 0.0035i.
  - The natural run's slowest multiplier is 0.99878, and the Ritz values creep up by only about 1e-5 per iteration.
- **Why the basis does not capture the slow mode.** The spectrum near 1 is clustered: several matrix thermal modes
  lie between about 0.997 and 0.9988. One subspace-iteration step per Newton step, as registered, improves V only
  by the ratio of neighbouring multipliers, about 0.998 per step, so V does not converge to the slow mode within
  the budget.
- **The Newton step therefore under-corrects.** It amplifies the slow residual by about 1/(1 - 0.997) ≈ 330
  instead of about 820, a factor of about 2.5 short.
- **The residual falls only slowly.** Max |Phi(x) - x| went 0.0041 K at iteration 1, 0.041 K at iteration 2
  (after the first large jump), 0.011 K at iteration 75 and 0.0013 K at iteration 149. The A1 stop rule needs
  1.5e-5 K.
- **Most of the residual sits in the cold-chamber gas cell at the piston face**, where the natural run changes by
  only about 2e-8 K per cycle. Each jump puts back a few mK there: the finite-difference basis carries
  gas-cell components of the piston-face cell, whose cycle-boundary response to a 0.05 K perturbation is
  non-smooth (N4), and the Newton step multiplies them.
- **Consistency of the jumps held throughout.** Gas mass after every jump matched M0 to 4.7e-16, the solver's
  mass drift stayed at most 3.1e-11, and no crash pattern was found.

This is the failure mode named in the task, an early or estimated slow-mode shape that still contains faster
modes, in a new form: a 3-dimensional subspace, re-estimated by one subspace iteration per step, cannot resolve a
cluster of near-1 multipliers. Changing p, the subspace update or the state vector (for example the matrix cells
only) would be a new amendment. None was made.
