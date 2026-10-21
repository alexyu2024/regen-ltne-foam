# Release notes v1.0.2

A maintenance release. The solver physics and the recorded verification results are unchanged.

**Changes:**
- **Diagnostics in parallel runs.** `src/ltneFoam/ltneDiagnostics.H` now skips processor-patch contributions to the
  boundary work, performs the energy and pressure reductions collectively on every rank, and builds the cell-zone
  diagnostic columns from a name-keyed union of the per-rank zones. A decomposed case now writes the same
  diagnostic rows as a serial run instead of desynchronising or deadlocking.
- **Citation.** `CITATION.cff` and `README.md` now point to the Zenodo concept DOI
  [10.5281/zenodo.23499221](https://doi.org/10.5281/zenodo.23499221), which resolves to all versions.
  `CITATION.cff` is version 1.0.2.
- **L5D decay ratio.** The measured ratio of the slow mode of the L5 slice is r = 0.99670 per cycle
  (PR #16); see `results/L5D`.
- **Results figures.** `README.md` now shows the LTNE gas/matrix fields and the axial profile against the
  reference (PR #17).
