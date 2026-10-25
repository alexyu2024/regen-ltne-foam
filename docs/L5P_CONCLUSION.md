# L5P conclusion: fast periodic-steady-state methods on the L5 regenerator slice

One page.
- Registration and amendments: `docs/VERIFICATION.md`, L5P. Design: `docs/L5P_PERIODIC_STATE.md`.
- Results: `results/L5P` (reference), `results/L5P/methods` (methods, branches `pss/method-a` and `pss/methods-bc`).
- The solver, the L5 case and its inputs are unchanged; the methods only decide where each `ltneFoam` cycle starts.

## Question

Can a cycle-map method (one cycle = one map evaluation) reach the periodic steady state of the L5 slice in fewer
cycles than natural marching? The registered criteria, fixed before any number was read, are:
- E: hot- and cold-end heat within 5 mW and 0.5 mW, and segment temperature differences, segment means and T_joint
  within 0.02 K, all against a long natural reference;
- D and NR: no drift and no rebound over 50 further natural cycles;
- M: gas mass consistent to 1e-9.

Every cycle run is counted.

## Answer

**No, not under the registered parameters. All seven configurations FAIL. Natural marching needs 4195 cycles.**

| method | total cycles (honest) | result | natural-equivalent cycle of the end state* |
|---|---|---|---|
| natural marching | **4195** (V(4145) holds) | reference | - |
| (a) Newton-Picard p = 1 | 639 | FAIL (budget) | 391 |
| (a) Newton-Picard p = 2 | 639 | FAIL (budget) | 625 |
| (a) Newton-Picard p = 3 | 639 | FAIL (budget) | 568 |
| (b) BRR p = 3 | 640 | FAIL (budget) | 1112 |
| (b) BRR p = 6 | 640 | FAIL (budget) | 2925 |
| (c) Graves-Morris m = 0 | 640 | FAIL (budget; residual 1.9e-5 K, needs 1.5e-5) | **3302** |
| (c) Graves-Morris m = 3 | 640 | FAIL (budget; residual 2.9e-5 K) | 2822 |

\* Post hoc, not registered: the first natural cycle whose worst distance to the reference is no larger than that of
the method's last iterate. It shows how far a failed run got for its 640 cycles, nothing more.

## What was learned

1. **The slow multiplier is 0.99878, not 0.9967.**
   - The time constant is about 820 cycles (36 s), and the slow mode sits at the hot end of the matrix, where the
     stainless heat capacity is large.
   - L5D's 0.9967 was a transitional value. Every registered quantity built on it (the reference test and the
     drift tolerance) was too weak; Amendment A2, decided by the author, replaced it with the measured value.
   - Natural marching therefore costs about 4200 cycles to meet the tolerances, not about 1500.
2. **The spectrum near 1 is clustered.**
   - Newton-Picard's Ritz values settle at 0.9964-0.9978, below 0.99878, often as a complex pair.
   - One subspace-iteration step per Newton step cannot separate several multipliers between about 0.997 and
     0.9988. Each Newton step under-corrects by about 2.5 times, and the end states are no better than natural
     marching at the same cost.
3. **Secant methods get further, erratically.**
   - BRR p = 6 ended as close to the reference as natural marching is at cycle 2925, about 4.6 times ahead for its
     cost.
   - Its residual is not monotone: 26 capped 2 K steps come in bursts, because the secant model of M - I is near
     singular (1 - r ≈ 0.0012). Neither BRR run met its stop rule (residual 1.5e-5 K) within 600 cycles.
4. **Graves-Morris converges smoothly but not fast enough.**
   - Both Graves-Morris runs reduced the residual monotonically, with no capped step.
   - m = 3's extrapolation ratio converged to 0.99868, close to the true 0.99878.
   - m = 0 ended closest of all seven runs (worst 1.1 tol, natural-equivalent cycle 3302), and m = 3 at 2.1 tol
     (cycle 2822). Their residuals at the budget were 1.9e-5 K and 2.9e-5 K, against a stop rule of 1.5e-5 K.
   - m = 3 would have needed about 18 more rounds (about 90 cycles) by its own trend. That is a projection, not a
     result.
   - Relative to their cost, the derivative-free methods moved about 4.4-5.2 times further along the natural
     trajectory. None reached the periodic state within the registered budget.
5. **The map and the jumps are sound.**
   - The map is deterministic, and a restart perturbs it by 1.7e-7 K.
   - After every jump the gas mass matched the inventory to below 1e-15, and the solver kept it to 3.5e-11 over
     4900 natural cycles.
   - Mean pressure follows from mass and temperature by construction. No run crashed.
   - Every container restart was resumed from a restart point and reproduced bit for bit.

## What would be worth trying next (not run; each needs a new registration)

- Newton-Picard with a larger p (6-10) or several subspace iterations per step. The cluster near 1 needs a subspace
  that spans it.
- A state vector restricted to the matrix cells, so the non-smooth piston-face gas cell does not enter the
  finite-difference basis.
- BRR with a trust region or a line search instead of a hard 2 K cap, and a budget large enough to see whether its
  late residual (6.7e-5 K) keeps falling.
- A start from a later natural state (for example cycle 300 instead of 40), after the fast modes have decayed.

## Cost of the whole study

| item | cycles |
|---|---|
| PR 1: natural reference to 4900, replays after container restarts, start state, noise tests, checks | 5157 |
| PR 2: Newton-Picard p = 1, 2, 3 | 1797 |
| PR 3: BRR p = 3, 6; Graves-Morris m = 0, 3 | 2400 |
| **total** | **9354** |

How to cite: see `CITATION.cff`.
