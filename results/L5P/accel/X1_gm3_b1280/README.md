# L5P-X1: Graves-Morris m = 3, budget 1280: FAIL (registered result)

Registration: `docs/L5P_accel/2026-10-25_gm3_b1280.md` (ba9d742, pushed before the run).

## Result as registered

| item | value |
|---|---|
| status | ended (stop rule met), 3 verification rounds |
| total cycles (honest) | **880** (40 + 840) |
| E / D / NR / M | **False** / True / True / True |
| result | **FAIL** (E) |
| first 600 cycles against L5P gm3 | 600 of 600 evaluations identical, bit for bit |
| gas mass after jumps / over the run | 4.7e-16 / 3.6e-11 |
| crashes | 0 |

The stop rule was met three times (after counts 675, 735 and 790), with residual 1e-7 to 1e-5 K. The method's
own drift test failed twice (rounds 1 and 2, on dT_seg1-3 and Ts_seg1-2 mean), so the iteration continued. It
passed in round 3 (counts 791-840). E failed in round 3 because dT_seg1 was 1.09-1.13 tol from the reference in
verification cycles 11-21 (counts 801-811).

## Finding: the driver's cycle mean was wrong for the method runs

dT_seg1..4 and Ts_seg1..4 mean are computed from the cycle-mean matrix temperature `TsMean`. That field comes from
the L5 case's `fieldAverage` with `periodicRestart`.
- In the method runs every cycle is a separate `ltneFoam` run, restarted from the time directory written at the
  end of the previous one.
- On a restart, `fieldAverage` sets its restart counter from the start time. The written start time carries
  rounding of order 1e-10 s, and the restart period 0.0434782608695652 is truncated. For long stretches the start
  time falls just above the boundary. The counter then points one period ahead, the average is never restarted,
  and `TsMean` becomes a running mean over all chained evaluations.
- Seen in the run directories: `totalIter 410400` (171 cycles) at the end of the L5P gm0, gm3 and brr runs, 331200
  for np3, instead of 2400. In X1, the mean restarted again at count 812 (cycle 852): dT_seg1 jumped by 0.025 K in
  one natural cycle, and its per-cycle change fell from 6.8e-5 K to 3e-8 K.
- Not affected:
  - the state vector (instantaneous T and Ts), so every iteration, jump and stop decision of every method;
  - Q_hot, Q_cold and T_joint (face and HX monitors) and p_mean.
- The **natural reference** is not affected: `totalIter` is 2400 in its restart points. Its per-cycle tables show
  the same glitch only on the first cycle of six 100-cycle chunks (cycles 101, 201, 501, 601, 701, 801; |error|
  <= 3.2e-4 K). None of them falls in the acceptance window (4850-4900), the A2 fits (4700-4900) or the V(4145)
  window.
- **L5P verdicts**: no L5P method ever reached its stop rule, so the seven FAILs (by budget) stand. Their post hoc
  "natural-equivalent cycle" figures (`docs/L5P_CONCLUSION.md`) used the wrong segment values and are unreliable.
- **X1**:
  - Verification rounds 1 and 2 and the E failure in round 3 were decided on running means, not cycle means.
  - In counts 812-840, where the mean was again a true cycle mean, every registered quantity was within 0.18 tol
    of the reference, and the drift was below 1e-7 per cycle.
  - That is a post hoc observation, not a PASS. **The registered result stays FAIL.**

**Fix** (commit after this result, before any further run):
- The map runs now use `restartOnRestart true` and no periodic restart, so the mean covers exactly the one cycle
  of each run.
- Each evaluation checks `totalIter == 2400` and stops with an error otherwise.
- Check: two cycles from cycle 40 give dT_seg1 within 3e-9 K of the natural run (restart noise 1.7e-7 K).
