# L4 status

| check | bar | value | status | value source |
|---|---|---|---|---|
| L4.1 final_time | == 150 (docs/VERIFICATION.md:238) | 150.0 | PASS | results/L4/log.ltneFoam:424562 |
| L4.2 fatal_or_nan_count | == 0 (docs/VERIFICATION.md:239) | 0 | PASS | results/L4/log.*:all lines of all logs |
| L4.3 out_err | <= 0.02 (docs/VERIFICATION.md:240) | 0.001473263962978838 | PASS | results/L4/outletT.dat:6-1505 |
| L4.4 Es_err | <= 0.01 (docs/VERIFICATION.md:241) | 0.000538644919982398 | PASS | results/L4/ltne.dat:2-30002 (every 100th row) |
| L4.5 energy_err | <= 0.01 (docs/VERIFICATION.md:242) | 0.0005161299789159485 | PASS | results/L4/ltne.dat:2,30002 with outletT.dat:6-1505 |
| L4.6 t_half | report (docs/VERIFICATION.md:243) | 70.36896041267686 | REPORT (> 0) | results/L4/outletT.dat:6-1505 |
| L4.7 t_half_exact | report (docs/VERIFICATION.md:244) | 70.4362206670653 | REPORT (> 0) | results/L4/outletT.dat:computed from the inputs |
| L4.8 allclean_leftover | == 0 (docs/VERIFICATION.md:245) | 0 | PASS | results/L4/log.allclean-check:empty file |

6/6 PASS
## How this was produced

`tools/run_level.sh L4 results/L4` in a fresh clone at 9b31098, 2026-09-26, wall time 2 min 4 s.
- **Case and bars**: unchanged since 85b4e55, when they were committed with the proposal before any run.
- **First run**: at 85b4e55 it crashed at start with a division by zero in the kS = 0 path. Record and diagnosis:
  `results/L4_run1/`. The fix (9b31098) only touches the kS = 0 path.
- **Storage**: files ending in `.gz` are cited by their uncompressed line numbers.

## Notes on the values

- **Breakthrough curve**: the outlet curve matches Schumann within 0.0015 of the step over t = 2 to 150 s (L4.3).
  The half-point comes 0.07 s early (L4.6, L4.7), about 0.1 % of t_half.
- **Accuracy against the expectation**: the error is smaller than the ~0.7 % estimated from gas axial conduction
  (xi_L / Pe) in the case README. The measured error includes that effect and the discretisation error; they were not
  separated ("not read").
- **Energy**: the solid energy stored matches the Schumann integral within 5.4e-4 of the full charge (L4.4), and the
  whole-run energy balance closes within 5.2e-4 (L4.5).
