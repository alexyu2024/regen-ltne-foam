## How this was produced

- **Run**: GitHub Actions `run-case`, input `level = LRG`,
  [40199952316](https://github.com/alexyu2024/regen-ltne-foam/actions/runs/40199952316) at 3e1f6f4, 2026-10-25,
  from the cycle-10900 state of run 40176130265 (see `results/LRG/README.md` for the earlier jobs).
- **Amendment A3** (`docs/VERIFICATION.md`, LRG; registered in e1af715 before the cycle-10900 result): cap raised
  to N_ref + 8000 = 12900, everything else unchanged. Its continue test at cycle 10900 gave a least-squares slope
  of ln(max R_q/tol) over cycles 9900-10900 of -3.1e-3 per cycle, so the run continued (`A3.env`, 3e1f6f4).
- **Paths and logs**: as in `results/LRG` (`out/LRG/` rewritten to `results/LRG_A3/`, container paths redacted,
  `STATUS.md` regenerated with `tools/verify.py LRG results/LRG_A3`).

## Outcome: PASS under A3, 5/5

The A2 test passed at cycle 11100, 6200 real-gas cycles after the switch: max_q R_q / tol_q = 0.193 <= 0.2.

| quantity (equal initial mean pressure) | ideal gas, cycle 4900 | real gas, cycle 11100 | relative difference | uncertainty from R_q (real + ideal) |
|---|---|---|---|---|
| Q_hot | -12.1892 W | -12.7704 W | +4.768 % | 0.011 % (7.0e-4 + 6.8e-4 W) |
| Q_cold | 1.85456 W | 1.97519 W | +6.505 % | 0.005 % (5.1e-5 + 4.6e-5 W) |
| p_mean | 0.80252 MPa | 0.81206 MPa | +1.189 % | - |
| helium inventory | M_ideal | M_real0 | -0.721 % | - |

The registered-cap result (cycle 10900, LRG.4 FAIL at 0.271) is in `results/LRG`. The values there differ from
these by less than 0.002 percentage points.
