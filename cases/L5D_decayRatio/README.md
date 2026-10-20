# L5D decay ratio of the slow matrix thermal relaxation

This case measures how fast the L5 slice's matrix approaches its periodic state. The definition and the reported
values are in `docs/VERIFICATION.md`, L5D, committed before the run. It is a report-only measurement, with no bar on
r.

- **Case**: the L5 case unchanged (`cases/L5_regenSlice`, the same as L6 G2), from t = 0.
- **Chunks**: the run proceeds in 50-cycle chunks.
- **Stopping rule**: it stops once the 50-cycle mean of r_k = d_k / d_(k-1) for the cycle-mean joint temperature is
  stationary to 1e-4 (k >= 200), or at 1500 cycles.

| command | what it does |
|---|---|
| `./runLong.sh <outdir> [minutes]` | builds, runs and writes `decay.csv`, `per_cycle.csv` and `results.csv`. Exit code 3 means the time budget is used and the state is kept for a restart. |
| `./Allclean` | removes the run directory and logs |

On GitHub: `.github/workflows/run-case.yml` with `level = L5D`.
