# L5P 3/4: methods (b) Broyden Rank Reduction and (c) Graves-Morris, compared with (a) and natural marching

**Branch**: `pss/methods-bc`, from main at eab2432. Results are in `results/L5P/methods/{brr3,brr6,gm0,gm3}_*`,
written as each run finished. This draft is updated as runs end.

Protocol: `docs/VERIFICATION.md`, L5P, as registered, with Amendments A1 and A2. All runs start from the cycle-40
state. Total = 40 + method cycles + verification cycles. A run that does not end within 600 cycles after cycle 40 is
FAIL at 640.

**Natural marching to compare against: 4195 cycles** (k_nat = 4145 + 50).

## Results so far

| run | status | total cycles (honest) | E | D | NR | M | result | natural-equivalent cycle of the end state* |
|---|---|---|---|---|---|---|---|---|
| brr3 | budget reached, never stopped on its own (600 iterations) | 640 | - | - | - | yes (3.1e-11; jumps <= 4.7e-16) | **FAIL** | 1112 |
| brr6 | running | | | | | | | |
| gm0 | running | | | | | | | |
| gm3 | running | | | | | | | |
| np1 / np2 / np3 (PR 2) | budget | 639 each | - | - | - | yes | **FAIL** | 391 / 625 / 568 |

\* Post hoc, not registered. It is the first natural cycle whose worst distance to the reference, max over q of
|q - q_ref| / tol_q, is no larger than that of the method's last iterate. It says how far a failed run got for its
cost, and nothing more.

## brr3 (`brr3_hist.csv`)

- **Start.** The first step is a plain cycle (B0 = -I). Rank 3 is reached at iteration 4 and reduced by SVD from then
  on.
- **The residual floors at about 8e-4 to 1e-3 K** (minimum 8.0e-4 K) from about iteration 300 to the end. The A1
  stop rule needs 1.5e-5 K.
- **Large jumps.** 26 of the 600 steps hit the 2 K cap. The secant model of M - I is near singular along the slow
  directions (1 - r ≈ 0.0012), so single steps occasionally blow up and are capped.
- **End state**, in tolerances: dT_seg2 18.4, dT_seg1 11.6, Ts_seg1_mean 11.9, Q_hot 6.7, T_joint 2.0, Q_cold 1.6,
  p_mean 0.3. Natural marching at the same cost (cycle 640) is at dT_seg1 31.5, Q_hot 21.7, Q_cold 17.2 and T_joint
  10.5. So BRR p = 3 got about as close as natural marching does by cycle 1112, but it did not converge.
- **Consistency.** Gas mass after every jump matched M0 to 4.7e-16, the solver drift stayed at most 3.1e-11, and no
  crash pattern was found.
