## How this was produced

- **Runs**: GitHub Actions `run-case`, input `level = LRG`, chained through `restart_run_id`:
  - [40143489532](https://github.com/alexyu2024/regen-ltne-foam/actions/runs/40143489532) at 068b872, 2026-10-24/25:
    ideal-gas continuation from the L5P restart point (cycle 4800) to N_ref = 4900, switch to real gas, real gas to
    cycle 8400 (time budget used, exit 3).
  - [40166756237](https://github.com/alexyu2024/regen-ltne-foam/actions/runs/40166756237) at 068b872 stopped before
    any cycle: the run-case state archive leaves `Allrun.continue` out. Fixed in cb20dde (driver only). No result of
    it is used.
  - [40176130265](https://github.com/alexyu2024/regen-ltne-foam/actions/runs/40176130265) at cb20dde, 2026-10-25:
    cycle 8400 to the registered cap N_ref + 6000 = 10900.
- **Inputs**: pinned in `cases/LRG_realGasL5/source.env` (L5P acceptance 462de28, restart point acafb87).
- **Paths**: `value source` paths were rewritten from `out/LRG/` to `results/LRG/`; container paths in logs were
  replaced by `<clone>` and `<WM_PROJECT_USER_DIR>`, line counts unchanged. `STATUS.md` was regenerated with
  `tools/verify.py LRG results/LRG`.
- **Logs**: `*.trimmed` logs keep the first 200 and last 100 lines, numbered. They are the logs of the last job.

## Outcome: FAIL at the registered cap

The real-gas run did not pass the A2 test by the registered cap: max_q R_q / tol_q = 0.271 at cycle 10900, against
a bar of 0.2 (LRG.4 FAIL). LRG.1, LRG.5, LRG.15 and LRG.16 pass. The reported values (LRG.6-LRG.14) are those at
cycle 10900. Under Amendment A3 (`docs/VERIFICATION.md`, LRG) the run continues from this state; its result is
in `results/LRG_A3`.

All differences are at equal initial mean pressure: the real gas holds 0.72 % less helium (LRG.2).
