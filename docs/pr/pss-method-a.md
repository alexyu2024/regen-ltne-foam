# L5P 2/4: method (a) Newton-Picard / RPM, p = 1-3

**Branch**: `pss/method-a`, from main at eab2432 (L5P tools and the reference already merged). Results are in
`results/L5P/methods/np{1,2,3}_*`, written as each run finished.

**Outcome: all three Newton-Picard runs FAIL.** Each reached the 600-cycle budget (total 639) without meeting its
own stop rule. None got closer to the reference than natural marching does at the same cost.

Protocol: `docs/VERIFICATION.md`, L5P, as registered, with Amendment A1 (residual stop rule) and Amendment A2 (drift
tolerance from r_A2 = 0.998813). All runs start from the cycle-40 state. Total = 40 + method cycles + verification
cycles. The budget is 600 cycles after cycle 40, so a run that does not end is FAIL at 640.

**Natural marching to compare against: 4195 cycles** (k_nat = 4145 + 50; within tolerance from cycle 4156).

## Results

| run | status | total cycles (honest) | E | D | NR | M | result |
|---|---|---|---|---|---|---|---|
| np3 | budget reached, never stopped on its own (149 iterations) | 639 | - | - | - | yes (3.1e-11; jumps <= 4.7e-16) | **FAIL** |
| np2 | budget reached, never stopped on its own (199 iterations) | 639 | - | - | - | yes (3.0e-11; jumps <= 4.7e-16) | **FAIL** |
| np1 | budget reached, never stopped on its own (299 iterations) | 639 | - | - | - | yes (3.1e-11; jumps <= 6.2e-16) | **FAIL** |

The total for np3 is 639 rather than 640: the next iteration needs 4 cycles at once, and only 599 + 4 > 600 was
checked, so the run stopped at 599 method cycles.

Distance of the last unperturbed iterate (the last Phi evaluation, not a finite-difference perturbation) from the
reference, in tolerances:

| state | worst quantity | dT_seg1 | dT_seg2 | T_joint | Q_hot | Q_cold |
|---|---|---|---|---|---|---|
| start (natural cycle 40) | Ts_seg2_mean 54.5 | 45.6 | 1.1 | 44.2 | 38.1 | 30.4 |
| np3, last iterate (639 cycles) | dT_seg1 33.8 | 33.8 | - | 8.6 | 20.8 | 17.4 |
| np2, last iterate (639 cycles) | dT_seg2 32.0 | - | 32.0 | 1.8 | 16.7 | 11.6 |
| np1, last iterate (639 cycles) | dT_seg2 39.0 | 28.3 | 39.0 | 10.0 | 12.2 | 1.9 |
| **natural, cycle 639 (same cost)** | dT_seg1 31.5 | 31.5 | 21.6 | 10.5 | 21.7 | 17.2 |

The worst quantity is listed; `final_dist` in the summary JSON uses the last evaluation, which for a budget-stopped
Newton-Picard run is a +0.05 K finite-difference perturbation, so it differs slightly from these numbers.

Natural-equivalent cycle of each end state (post hoc, not registered: the first natural cycle whose worst
distance is no larger): np1 391, np2 625, np3 568, against a cost of 639 each. For comparison, BRR p = 3 (PR 3)
reaches 1112 for a cost of 640.

At equal cost the Newton-Picard end states are no better than natural marching: worst 32-39 tol against 31.5. They
pull some quantities closer (np2: T_joint 1.8 tol; np1: Q_cold 1.9 tol) and push others further away (dT_seg2).

**np1** (`np1_hist.csv`): its single Ritz value settles at 0.99781, below the true slow multiplier 0.99878. The max
residual falls from 0.019 K (iteration 2) to 0.0037 K (iteration 150) and 0.0014 K (iteration 299).

**np2** (`np2_hist.csv`) behaves like np3. The Ritz values reach 0.9978 and 0.9905 around iteration 100, then
collapse into a complex pair at 0.9964 +- 0.002i by iteration 199. The max residual plateaus at about 3.7e-3 K
from iteration 100 on.

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

## Size of this PR's work

- **1917 cycles of method runs**: np3, np2 and np1 each 599 method cycles plus the shared 40-cycle start, which was
  counted in PR 1. No verification cycles: no run met its stop rule.
- About 15 rounds, mostly monitor events.
- The runs used 4, 3 and 2 cores concurrently, about 2 h 45 min of wall time.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01VmevXLRq7SmGut51MTYG7i
