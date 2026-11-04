# L5P-X1c: Graves-Morris m = 3, corrected cycle mean, start at cycle 400: PASS

Registration: `docs/L5P_accel/2026-10-27_gm3_c400.md` (df7a5cf, pushed before any cycle ran). This was a
robustness check of X1b approved by the author, and the last configuration; nothing further is run.

| item | value |
|---|---|
| status | ended (stop rule met), 2 verification rounds |
| **total cycles (honest)** | **970** = 400 natural cycles to the start state + 520 method + 50 verification (round 2); round 1's 50 verification cycles are inside the 520 |
| E / D / NR / M | True / True / True / True |
| **result** | **PASS** |
| natural marching | 4195 cycles; 4195 / 970 = **4.3 times fewer cycles** |
| worst distance to the reference, verification cycles 11-50 | dT_seg1 0.180 tol, dT_seg2 0.147, Q_hot 0.126 |
| gas mass after jumps / over the run | 3.1e-16 / 3.6e-11 |
| crashes; capped steps | 0; 0 of 94 rounds |

**How the run went**:
- Rounds 1-92: 3 plain cycles and 2 extrapolation cycles each; stop rule met after count 460.
- Verification round 1 (counts 461-510): the method's own drift test failed on dT_seg1 and dT_seg2, so the
  iteration continued.
- Round 94, after count 520: residual 1.1e-6 K. Verification round 2 (counts 521-570): self-test passed.
- Scored on the last 50 cycles.

**Start state**:
- Made from `run_c40` by 360 natural cycles in one run.
- Against the natural reference's own table for cycles 41-400:
  - T_joint agrees to 3.3e-8 K, within the 1.7e-7 K the registration expected (not a criterion);
  - other columns differ by up to 8.9e-6 W (Q_hot gas, 7e-7 relative) and 1.8e-5 Pa (hot-end pressure amplitude,
    3e-10 relative);
  - the largest differences are at cycles 101 and 201, where the natural reference itself restarted between
    chunks.
- `start_per_cycle.csv` holds the table.

## X1b against X1c

| | X1b (start 40) | X1c (start 400) |
|---|---|---|
| cycles to the start state | 40 | 400 |
| method cycles, including round 1's verification | 735 | 520 |
| final verification | 50 | 50 |
| **total** | **825** | **970** |
| result | PASS | PASS |
| worst final distance (dT_seg1) | 0.179 tol | 0.180 tol |

- Both starts reach the same end state: worst distances agree to 0.001 tol.
- The pass is not tied to the cycle-40 start.
- Starting later saves 215 method cycles but costs 360 more natural cycles, so the total is 145 cycles higher.
  The cheaper start of the two tried is the earlier one.
- In both runs, the first verification failed on the hot-end segment differences, and one more extrapolation
  round was needed.

**Caveats** (as for X1b):
- Two starts, one method configuration.
- The 50-cycle verification limits the drift, not a slow-mode error that would only show over about 820 cycles;
  the natural reference was accepted by the same test.
