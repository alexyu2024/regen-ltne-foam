## How this was produced

- **Run**: the `verify` workflow on PR #23, run
  [41900496350](https://github.com/alexyu2024/regen-ltne-foam/actions/runs/41900496350) at 96b6f8d (the commit that
  registered the bars), `tools/run_level.sh L4E`, 2026-11-04. The whole `verify` job (L0-L4, LP and L4E) took about 4 min.
- **Paths**: `value source` paths were rewritten from `ci-out/L4E/` to `results/L4E/`; container paths were replaced
  by `<clone>` and `<WM_PROJECT_USER_DIR>`. `STATUS.md` was regenerated with `tools/verify.py L4E results/L4E`.
- **Log**: `log.ltneFoam.trimmed` keeps the first 200 and last 100 of its 433600 lines, numbered.
- **Figure**: `docs/figures/L4E_breakthrough.png`, from `cases/L4E_schumannErgun/plot.py results/L4E <png>`.

## Result: 6/6 PASS

| check | value | bar |
|---|---|---|
| gas breakthrough, max \|theta_g - Schumann\| (mid-bed and bed end, t >= 2 s) | 0.0023 (bed end, t = 81.5 s) | <= 0.03 |
| solid breakthrough, max \|theta_s - Schumann\| (same probes) | 0.0024 (bed end, t = 87.7 s) | <= 0.03 |
| bed pressure drop, max \|dp / dp_Ergun - 1\| (t >= 2 s) | 0.25 % (t = 150 s) | <= 2 % |
| dp and dp_Ergun at t = 150 s | 769.8 Pa and 771.7 Pa | report |
| Re_p | 7.81 | report |

The errors are an order of magnitude below the bars. The bars were set before the run and are not tightened after
it.
