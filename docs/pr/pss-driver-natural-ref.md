# L5P 1/4: cycle-map driver and natural reference for the periodic steady state

**Branch**: `pss/driver-natural-ref`. Merged into main by the author's instruction once the reference passed
(3e5d0e2), because the real-gas session reuses the tools.

## What this adds

- **The cycle-map driver** `cases/L5P_periodicState/pss/`: one ltneFoam cycle per map evaluation, from a
  cycle-boundary state, with the solver unchanged. `ltneFoam` itself is untouched.
  - State x = [matrix Ts (120 cells), gas T (172 cells)].
  - After every jump, the pressure is shifted uniformly so that the gas mass equals the inventory M0, and rho is
    recomputed by the solver from p and T. Mean pressure, mass and temperature field stay consistent.
  - Every cycle is counted, and every evaluation's log is scanned for crashes.
- **The three registered methods**: Newton-Picard p = 1-3, BRR p = 3 and 6, and Graves-Morris m = 0 and 3. There is
  a synthetic self-test that needs no solver, and a scheduler (`pss/runall.py`).
- **The natural reference run** with restart points: `runNatural.sh`, `results/L5P/natural/`.
- **Registration** `docs/VERIFICATION.md`, L5P:
  - committed before any number was read (b2984ed);
  - Amendment A1 before any method run;
  - Amendment A2, post hoc, decided by the author after the cycle-4000 data.
- **Design page**: `docs/L5P_PERIODIC_STATE.md`.

## Results (`results/L5P/README.md`, `STATUS.md`: 5/5 PASS)

- **L5P.1 build check**: T_joint(40) differs by 1.1e-7 K (bar 1e-5). PASS.
- **L5P.3 reference**:
  - **FAIL under the registered rule** at the 4000-cycle cap. Worst R_q/tol = 0.2088 (dT_seg1). The earlier
    extensions gave 1.477, 0.907, 0.556 and 0.341.
  - **PASS under Amendment A2 at cycle 4900**: worst R_q/tol = 0.1927 (dT_seg1).
  - r fitted at 4900: 0.998813 over 100 cycles and 0.998794 over 200 cycles; r_A2 = 0.998813.
- **L5P.7 gas-mass drift**: 3.5e-11 over 4900 cycles. PASS.
- **Natural marching**: k_nat = 4145, so the **natural total is 4195 cycles**. It is within tolerance from cycle 4156.
- **Noise of the map**: identical repeats; the restart rounding is 1.7e-7 K and a jump write-back 1.1e-9 K. Along the
  slow direction the finite-difference product has about 1 % truncation error at 0.05 K.
- **Crash scan and Allclean**: PASS.

## Finding: the slow multiplier is 0.99878 (time constant about 820 cycles), not 0.9967

- Every quantity late in the natural run decays with the same ratio, r ≈ 0.99878 per cycle: a time constant of about
  820 cycles, or 36 s.
- The slow mode sits at the **hot end** of the matrix, where the stainless heat capacity is large. The hot-end
  segment differences and Q_hot converge last; T_joint does not.
- L5D's 0.99670 (cycles 501-600) was transitional.
- This changes the run length every method is compared against: natural marching needs **4195** cycles under the
  registered tolerances, not the roughly 1500 that r = 0.9967 suggests.
- It is also why the registered reference test and drift tolerance (both built on 0.9967) were too weak, and why
  Amendment A2 was needed.

## Container restarts

- The container was reclaimed three times during the natural run.
- Each time the run resumed from the latest restart point, and the replayed cycles were bit-for-bit identical to
  the originals.
- 176 discarded cycles are counted.

## Size of this PR's work

- About 120 rounds, most of them monitor events and checkpoint confirmations.
- **5157 cycles**: 4900 natural, 176 replayed after container restarts, 40 for the methods' start state, 22 noise
  tests, and 19 trials and checks.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01VmevXLRq7SmGut51MTYG7i
