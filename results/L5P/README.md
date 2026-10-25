## How this was produced

- **Runs**: locally, in a Claude Code cloud container (4 cores, Ubuntu 24.04), with OpenFOAM `openfoam2512-dev`
  2512.0-2. This is the same package CI uses, installed with `tools/install.sh`.
  - The natural run used one core, about 9-15 s per cycle depending on the container.
  - The method runs are listed in their own result directories (branches `pss/method-a`, `pss/methods-bc`).
- **Bars**: committed in b2984ed, before any L5P number was read, except the agreed L5P.1 build check.
  - Amendment A1 (residual stop rule for the methods) was committed in 51a573d, before any method run.
  - Amendment A2 (measured decay ratio in the reference test, cap 6000) was decided by the author after the
    cycle-4000 data had been read, and committed in 7672a59 before any further cycle ran.
- **Build check (L5P.1)**: cycle 40 of the natural run gives T_joint = 27.865715114 K. That is 1.1e-7 K from the
  registered 27.865715 and 1.2e-8 K from the full-precision value in `results/L5`, which restarted every 10 cycles.
- **Natural run** (`cases/L5P_periodicState/runNatural.sh`):
  - The L5 case unchanged, from t = 0, in 100-cycle chunks, one time directory per cycle boundary.
  - The tables `natural/per_cycle.csv` (face and HX terms, L5 `results.py`) and `natural/cycles.csv` (segment Ts,
    gas mass, mean pressure) were committed every 100 cycles.
  - A restart point (`natural/restart/state.tgz`) was written every 200 cycles.
- **Container restarts**: the container was reclaimed three times. Each time the run resumed from the latest
  restart point, and the replayed cycles reproduced the originals bit for bit:
  - from 800 (the lost run had reached 925): tables of cycles 801-900 identical;
  - from 800 again (lost run at 837);
  - from 1400 (lost run at 1414): states of cycles 1401-1414 identical;
  - from 4000 for Amendment A2: every field file of cycle 4001 byte-identical to a continuation of the original
    run directory.
  The 176 discarded cycles are counted below.
- **Logs**: each `natural/*.trimmed` log keeps the first 200 and last 100 lines, prefixed with their line numbers.
- **Merge with main**: after the reference passed, main (real-gas helium 1/3, PR #19) was merged in. Its default
  ideal-gas path and the L5 case are unchanged. The rebuilt `ltneFoam` has a different binary because the H-monitor
  code changed, but one cycle from cycle 40 is bit-for-bit identical to the pre-merge binary, so the methods run on
  an equivalent solver.

## Result: 5/5 PASS (L5P.3 under Amendment A2)

| quantity | reference (cycle 4900) | tolerance | remaining distance R_q / tol (A2) |
|---|---|---|---|
| Q_hot (hot HX heat into gas + matrix), W | -12.189233 | 0.005 | 0.136 |
| Q_cold (cold HX heat into gas + matrix), W | 1.854556 | 0.0005 | 0.092 |
| dT_seg1 (matrix quarter 1, hot end), K | 33.227206 | 0.02 | **0.193** |
| dT_seg2, K | 19.270069 | 0.02 | 0.157 |
| dT_seg3, K | 3.749077 | 0.02 | 0.042 |
| dT_seg4 (cold end), K | 1.024882 | 0.02 | 0.002 |
| Ts_seg1..4 mean, K | 62.88186 / 34.57085 / 24.36220 / 22.68587 | 0.02 | 0.126 / 0.132 / 0.007 / 0.001 |
| T_joint, K | 26.982416 | 0.02 | 0.040 |
| p_mean (cycle boundary), Pa | 802519.0 | 802.5 | 0.017 |

**Reference acceptance, as it happened**:
- Under the registered rule, with r = 0.99670 from L5D, max R_q/tol was:

  | cycle | 2400 | 2800 | 3200 | 3600 | 4000 |
  |---|---|---|---|---|---|
  | max R_q/tol | 1.477 | 0.907 | 0.556 | 0.341 | **0.2088** |

  Every one is a FAIL against the bar of 0.2 (`reference_c*.json`). **L5P.3 under the registered rule stays on
  record as FAIL at the 4000-cycle cap, worst R_q 0.2088 (dT_seg1).**
- Under Amendment A2, max R_q/tol was 0.501 at 4100, 0.466, 0.411, 0.364, 0.310, 0.279, 0.248 and 0.217, then
  **0.1927 at 4900: PASS**.

**Finding: the slowest multiplier is r = 0.99878, not 0.9967**:
- From about cycle 2000 on, every quantity whose per-cycle change keeps one sign decays with the same ratio,
  r ≈ 0.99878 per cycle. That is a time constant of about 820 cycles, or 36 s at 23 Hz.
  - Table: `natural_decay_c2400.csv`.
  - Fits at 4900: 0.998767-0.998813 over 100 cycles, 0.998767-0.998794 over 200 cycles. r_A2 = 0.998813.
- The slow mode sits at the hot end of the matrix. The hot-end segment differences, segment temperatures and Q_hot
  are the last to converge; T_joint is not, since the stainless heat capacity is far larger at 60-80 K than at 25 K.
- L5D's r = 0.99670 (cycles 501-600) was a transitional value: the ratio was still rising, not settling.
- Every comparison against natural marching depends on this number. With r = 0.9967 natural marching would look
  about 2.7 times faster than it is.

**Natural marching count** (A2 drift tolerance 0.45 tol (1 - r_A2) per cycle):
- k_nat = 4145: V(4145) holds, so the natural total is **4195 cycles**.
- Natural marching is within every tolerance from cycle 4156 on.
- This is the number each method's total is compared with.

**Mass and pressure**:
- The gas mass drifts by at most 3.5e-11 (relative) over 4900 cycles.
- The mean pressure at the cycle boundary is consistent with the temperature field through the solver's own
  continuity. It rose from 0.791 MPa at cycle 1 and reached 802519 Pa at cycle 4900.

**Noise of the map** (from the cycle-40 state):

| test | what | result |
|---|---|---|
| N1 | the same cycle twice | identical (0.0 K) |
| N2 | two cycles continuous vs 1 + 1 with a restart | 1.7e-7 K: the restart rounding of the carried fields |
| N3 | x written back unchanged (mass shift, rho recomputed) vs plain cycle | 1.1e-9 K |
| N4 | finite-difference M v, along the first natural difference | relative change <= 1e-3 from 1e-2 to 1e-5 K; floor 7e-5. At the registered 0.05 K the truncation error is about 1 %. Along a random direction the response is nonlinear above 0.03 K (14 %) |

## Cycles run for this result (honest count)

| item | cycles |
|---|---|
| natural run, t = 0 to 4900 | 4900 |
| discarded by container restarts and replayed (925-800, 837-800, 1414-1400) | 176 |
| common start state of the methods (t = 0 to 40, separate run) | 40 |
| noise tests N1-N4 | 22 |
| driver trials, restart test, plumbing smoke test, binary checks (pre/post merge), continuation for the cycle-4001 check | 7 + 9 + 2 + 1 |
| **total** | **5157** |
