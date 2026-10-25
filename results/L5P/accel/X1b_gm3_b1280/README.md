# L5P-X1b: Graves-Morris m = 3, budget 1280, corrected cycle mean: PASS

Registration: `docs/L5P_accel/2026-10-25_gm3_b1280_fixedmean.md` (ce875ed, pushed before the run). The run was
decided after reading X1, whose cycle mean was defective; X1 stays FAIL on record.

| item | value |
|---|---|
| status | ended (stop rule met), 2 verification rounds |
| **total cycles (honest)** | **825** = 40 + 735 method + 50 verification (round 2); round 1's 50 verification cycles included |
| E / D / NR / M | True / True / True / True |
| **result** | **PASS** |
| natural marching | 4195 cycles |
| ratio | 4195 / 825 = **5.1 times fewer cycles** |
| worst distance to the reference in verification cycles 11-50 | dT_seg1 0.179 tol, dT_seg2 0.146, Q_hot 0.125 |
| gas mass after jumps / over the run | 4.7e-16 / 3.6e-11 |
| crashes; capped steps | 0; 0 of 137 rounds |

How the run went:
- Rounds 1 to 135 of extrapolation: 3 plain cycles, then two cycles for the extrapolation. The stop rule was met
  after count 675 (round 135), with residual 1.3e-5 K and correction under 0.005 K.
- **Verification round 1** (counts 676-725): the method's own drift test failed on dT_seg1 alone, so the iteration
  continued.
- **Round 137**, after count 735: residual 1.1e-6 K. **Verification round 2** (counts 736-785): self-test passed.
- **Scoring against the reference**: E, D, NR and M all hold over the last 50 cycles (cycles 776-825 of the honest
  count).

Checks:
- Up to the first verification (counts 1-725), Q_hot, Q_cold, T_joint and p_mean equal X1's bit for bit. The state
  vector does not depend on the cycle mean.
- Every evaluation's cycle mean covered exactly 2400 steps; the driver stops otherwise.

Caveats:
- One configuration, one start state (cycle 40).
- The verification is 50 natural cycles after the stop. With the slow multiplier 0.99878, the A2 drift test bounds
  the drift, not the distance that a remaining slow-mode error would cover over about 820 cycles. The same test
  accepted the natural reference.
- A PASS under the registered criteria, not a proof of periodicity beyond them.
