# L3 status

| check | bar | value | status | value source |
|---|---|---|---|---|
| L3.1 r_final_time | == 0.00145 (docs/VERIFICATION.md:172) | 0.00145 | PASS | results/L3/r.log.ltneFoam:7058 |
| L3.2 b_final_time | == 0.0009 (docs/VERIFICATION.md:173) | 0.0009 | PASS | results/L3/b.log.ltneFoam:7058 |
| L3.3 fatal_or_nan_count | == 0 (docs/VERIFICATION.md:174) | 0 | PASS | results/L3/log.*:all lines of all logs |
| L3.4 r_err_g | <= 0.01 (docs/VERIFICATION.md:175) | 0.0018524230590713842 | PASS | results/L3/r.ltne.dat:2-502 |
| L3.5 r_err_s | <= 0.01 (docs/VERIFICATION.md:176) | 9.320147273683688e-06 | PASS | results/L3/r.ltne.dat:2-502 |
| L3.6 r_energy | <= 1e-3 (docs/VERIFICATION.md:177) | 0.0006624253040098374 | PASS | results/L3/r.ltne.dat:2-502 |
| L3.7 b_err_g | <= 0.01 (docs/VERIFICATION.md:178) | 0.0011082747087158395 | PASS | results/L3/b.ltne.dat:2-502 |
| L3.8 b_err_s | <= 0.01 (docs/VERIFICATION.md:179) | 0.0006346681022932898 | PASS | results/L3/b.ltne.dat:2-502 |
| L3.9 b_energy | <= 1e-3 (docs/VERIFICATION.md:180) | 0.0006456878334820943 | PASS | results/L3/b.ltne.dat:2-502 |
| L3.10 r_Teq | report (docs/VERIFICATION.md:181) | 319.7455433893626 | REPORT (> 0) | results/L3/r.ltne.dat:502 |
| L3.11 b_Teq | report (docs/VERIFICATION.md:182) | 312.4799024281084 | REPORT (> 0) | results/L3/b.ltne.dat:502 |
| L3.12 allclean_leftover | == 0 (docs/VERIFICATION.md:183) | 0 | PASS | results/L3/log.allclean-check:empty file |

10/10 PASS
## How this was produced

`tools/run_level.sh L3 results/L3` in a fresh clone at 074f025, the commit that added the L3 bars; no L3 case had been
run before it. 2026-09-26, same container and OpenFOAM package as before.

## Notes on the values

- **Gas temperature error** (L3.4, L3.7): 0.19 % and 0.11 % of |T_s0 - T_g0|. This matches the implicit-Euler
  estimate in `docs/VERIFICATION.md` of (dt/tau)/2 exp(-1) = 0.18 %.
- **T_g at endTime**:

  | run | computed (L3.10, L3.11) | exact at the same time | difference |
  |---|---|---|---|
  | r | 319.7455 K | 319.7487 K | 3.2e-3 K |
  | b | 312.4799 K | 312.4804 K | 5e-4 K |

  The exact values come from the formulas in `docs/VERIFICATION.md` with the tau and T_eq listed there.
- **Energy conservation** (L3.6, L3.9): the total energy drifts by at most 6.6e-4 of the exchanged energy Q, which
  uses 66 % of the 1e-3 bar. The gas and solid equations are solved one after the other within each time step, with
  3 outer correctors, so the exchange terms of the two equations are evaluated at slightly different iterates. The
  drift is that mismatch. It shrinks with more outer correctors or a smaller dt; this was not tested ("not read").
