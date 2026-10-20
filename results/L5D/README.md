## How this was produced

- **Run**: GitHub Actions `run-case`, input `level = L5D`,
  [39419157331](https://github.com/alexyu2024/regen-ltne-foam/actions/runs/39419157331) at 51182a3, 2026-10-20,
  about 73 min.
  - The L5 case unchanged, from t = 0, in 50-cycle chunks.
  - It stopped at cycle 600 under the stopping rule committed before the run (150813f, `docs/VERIFICATION.md`,
    L5D).
- **The first attempt failed.**
  [39416551313](https://github.com/alexyu2024/regen-ltne-foam/actions/runs/39416551313) at d9fe79c stopped at its
  first restart, at cycle 50, with `cannot find file .../2.1739130434764/p`. OpenFOAM had written that time as
  `2.173913043476394`, more digits than the case's `timePrecision 14`. 51182a3 sets `timePrecision 17` for this
  run, which affects time names only, and the run was repeated from t = 0. No result of the failed attempt is
  used.
- **Check against L5**: this run reproduces the L5 base run. T_joint on cycle 40 is 27.865715 K in both runs.
- **Paths**: `value source` paths were rewritten from `out/L5D/` to `results/L5D/`. `STATUS.md` was regenerated with
  `tools/verify.py L5D results/L5D`.
- **Logs**: `*.trimmed` logs keep the first 200 and last 100 lines, numbered.

## Result, reported as is (no bar on r)

| quantity | value |
|---|---|
| cycles run | 600 |
| decay ratio per cycle of the cycle-mean T at the joint, r_fit (cycles 501-600) | **0.99670** |
| mean of r_k over cycles 551-600 | 0.99668 |
| change of the 50-cycle mean of r_k between the last two windows (stopping test, < 1e-4) | 4.4e-5 |
| time constant tau = -1 / ln r | 302.5 cycles = 13.2 s |
| T_joint on cycle 600 | 27.212 K |
| extrapolated periodic limit T_inf = T_k + d_k r / (1 - r) | 27.042 K |
| r_fit of H_hot (cycles 501-600) | 0.9901 |
| r_fit of H_joint (cycles 501-600) | 1.034 |

The series, k, T_k, d_k and r_k, is in `decay.csv`.

## Notes

- **The decay is not a single exponential over the whole run.**
  - From cycle 40 to about 300, T_joint drifts almost linearly: d_k stays between -1.35 and -1.50 mK per cycle,
    and r_k is close to 1.
  - Only after that does it decay geometrically, with r_k easing down: 0.99719 at cycle 400, 0.99677 at 500, 0.99667
    at 600. It is stationary by the stopping test, but it may still fall slightly.
  - T_inf assumes the decay stays geometric with r_fit from cycle 600 on, so treat it as an estimate.
- **H_joint is not decaying geometrically.** Its r_fit of 1.034 does not describe a decay. Its cycle-to-cycle change
  is tiny and nearly constant (it changed sign at cycle 510 and has been about -4e-6 W per cycle since), so the
  ratio of successive changes is not meaningful.
- **The L5 results are not the periodic limit.** At cycle 40, where L5 stopped with B6 passing, T_joint is 27.866 K.
  That is 0.65 K above its cycle-600 value and about 0.8 K above the extrapolated limit. H_hot is 1.863 W at cycle
  40 against 1.799 W at cycle 600 (-3.4 %). The L5 bars and their outcomes are unchanged; this is recorded here as a
  measured fact about how far the L5 state at 40 cycles is from the periodic state.
