# L5P 3/4: methods (b) Broyden Rank Reduction and (c) Graves-Morris, compared with (a) and natural marching

**Branch**: `pss/methods-bc`, from main at eab2432. Results are in `results/L5P/methods/{brr3,brr6,gm0,gm3}_*`,
written as each run finished.

**Outcome: all four runs FAIL by the registered rule.** Each reached the 600-cycle budget (total 640) without
meeting its own stop rule (residual <= 1.5e-5 K), so none entered verification. The two Graves-Morris runs missed
narrowly. Their residuals fell smoothly to 1.9e-5 K (m = 0) and 2.9e-5 K (m = 3), and their end states are as close
to the reference as natural marching is at cycles 3302 and 2822. Together with PR 2, **all seven registered
configurations FAIL.** Natural marching needs 4195 cycles.

Protocol: `docs/VERIFICATION.md`, L5P, as registered, with Amendments A1 and A2. All runs start from the cycle-40
state. Total = 40 + method cycles + verification cycles. A run that does not end within 600 cycles after cycle 40 is
FAIL at 640.

**Natural marching to compare against: 4195 cycles** (k_nat = 4145 + 50).

## Results (all seven configurations)

| run | status | total cycles (honest) | E | D | NR | M | result | natural-equivalent cycle of the end state* |
|---|---|---|---|---|---|---|---|---|
| brr3 | budget reached, never stopped on its own (600 iterations) | 640 | - | - | - | yes (3.1e-11; jumps <= 4.7e-16) | **FAIL** | 1112 |
| brr6 | budget reached, never stopped on its own (600 iterations) | 640 | - | - | - | yes (3.0e-11; jumps <= 4.7e-16) | **FAIL** | 2925 |
| gm0 | budget reached, never stopped on its own (300 rounds) | 640 | - | - | - | yes (3.1e-11; jumps <= 4.7e-16) | **FAIL** | 3302 |
| gm3 | budget reached, never stopped on its own (120 rounds) | 640 | - | - | - | yes (3.1e-11; jumps <= 4.7e-16) | **FAIL** | 2822 |
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

## brr6 (`brr6_hist.csv`)

- **End state**, in tolerances: Ts_seg1_mean 1.9, dT_seg1 1.8, dT_seg2 1.4, Ts_seg2_mean 1.0, Q_hot 0.4, T_joint 0.3,
  Q_cold 0.2, p_mean 0.1. Natural marching first gets this close at cycle 2925. It is the closest end state of all
  runs so far, but it is still outside E (tolerance 1 on every quantity) and the run never met its stop rule, so it
  is a FAIL by the registered rule.
- **The residual is erratic, not steadily converging.**

  | iteration | 100 | 200 | 300 | 400 | 500 | 550 | 575 | 600 |
  |---|---|---|---|---|---|---|---|---|
  | max residual, K | 1.9e-3 | 9.0e-4 | 4.2e-3 | 3.3e-4 | 1.5e-4 | 6.4e-3 | 4.5e-2 | 6.7e-5 |

  - 26 steps hit the 2 K cap, in bursts spread over the whole run (iterations 9, 69-70, 138-174, 231-255, 292,
    333-336, 436-437 and 566-567). After each burst the residual jumps up and is worked down again.
  - The good end state is partly a matter of where the budget cut the run. With a larger budget it might have met
    the stop rule (1.5e-5 K), or it might have hit another burst first. The data do not say which.
- **Consistency.** Gas mass after every jump matched M0 to 4.7e-16, the solver drift stayed at most 3.0e-11, and no
  crash pattern was found.

## gm0 (`gm0_hist.csv`): the closest end state

- **End state**, in tolerances: dT_seg1 1.1, dT_seg2 0.9, Ts_seg2_mean 0.8, Ts_seg1_mean 0.7, Q_hot 0.4, Q_cold 0.3,
  T_joint 0.1, p_mean 0.1. Only dT_seg1 is outside E, and only just (1.1 > 1).
- **The residual falls smoothly.** No step was capped.

  | round | 1 | 25 | 75 | 150 | 225 | 300 |
  |---|---|---|---|---|---|---|
  | max residual, K | 4.6e-3 | 1.4e-3 | 6.5e-4 | 2.2e-4 | 4.2e-5 | **1.9e-5** |

  The stop rule needs 1.5e-5 K.
- **The extrapolation ratio wanders.** (x2 - x1).(x1 - x0)/|x1 - x0|^2 rises from 0.984 to 0.9974 by round 75. Late
  in the run it fluctuates around 1 (0.9996-1.004), as the successive differences become small and are no longer
  dominated by a single mode. The extrapolation steps stay small (corrections 7e-6 K at round 300), so this does
  no harm, but it means the method has stopped extrapolating effectively and is close to plain cycling.

## gm3 (`gm3_hist.csv`)

- **End state**, in tolerances: dT_seg1 2.1, dT_seg2 1.7, Ts_seg2_mean 1.5, Ts_seg1_mean 1.4, Q_hot 0.7, Q_cold 0.5,
  T_joint 0.2.
- **The residual falls smoothly and monotonically.** No step was capped.

  | round | 1 | 10 | 30 | 60 | 90 | 120 |
  |---|---|---|---|---|---|---|
  | max residual, K | 3.9e-3 | 1.5e-3 | 4.4e-4 | 2.0e-4 | 8.6e-5 | **2.9e-5** |

- **The extrapolation ratio converges** towards the true slow multiplier: 0.9865, then 0.99835 (round 10), 0.99858
  (round 60) and 0.99868 (round 120), against 0.99878.
- **Projection, not a result.** Over rounds 90-120 the residual fell by 0.9645 per round, which would reach
  1.5e-5 K in about 18 more rounds (about 90 cycles), and verification would then take 50 more. The registered
  budget did not allow it. That gm3 would then have passed E, D and NR is not known.

## Comparison (registered outcome and post hoc distance)

| run | cycles | registered result | worst distance at the end, tol | natural-equivalent cycle |
|---|---|---|---|---|
| natural marching | **4195** | reference (V holds from 4145) | - | - |
| gm0 | 640 | FAIL | 1.1 | **3302** |
| brr6 | 640 | FAIL | 1.9 | 2925 |
| gm3 | 640 | FAIL | 2.1 | 2822 |
| brr3 | 640 | FAIL | 18.4 | 1112 |
| np2 | 639 | FAIL | 32.0 | 625 |
| np3 | 639 | FAIL | 33.8 | 568 |
| np1 | 639 | FAIL | 39.0 | 391 |

- **What the comparison shows.** The derivative-free methods (Graves-Morris, and BRR with memory 6) moved the
  state about 4.4-5.2 times further along the natural trajectory than their cost. Graves-Morris did so smoothly, BRR
  erratically.
- **Newton-Picard** with p <= 3 did not beat natural marching. Its finite-difference subspace could not resolve the
  cluster of slow multipliers (PR 2).
- **No method met its registered stop rule within the registered budget.** So, honestly counted, no method reached
  the periodic state faster than natural marching under the registered protocol.

## Size of this PR's work

- **2400 cycles of method runs**: four runs of 600 method cycles each, plus the shared 40-cycle start, which was
  counted in PR 1. No verification cycles.
- About 20 rounds.
- The runs used one core each, over about 4.5 h of wall time, overlapping with PR 2.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01VmevXLRq7SmGut51MTYG7i
