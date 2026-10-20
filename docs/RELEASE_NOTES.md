# Release notes: v1.0.0

Tag: `v1.0.0`. The repository stays private; the owner sets its visibility and links Zenodo, and the DOI is then
added to `CITATION.cff` and `README.md`.

## What this release is

`ltneFoam` is an OpenFOAM v2512 (ESI, openfoam.com) solver for compressible, oscillating, piston-driven helium flow
through porous media with local thermal non-equilibrium. Main features:
- porosity-weighted gas equations derived from `rhoPimpleFoam`;
- a solid-matrix energy equation coupled to the gas by hA (Ts - T);
- face-consistent Darcy-Forchheimer drag;
- moving pistons (`pistonLinear`);
- per-zone porous properties, live film-coefficient correlations (Gedeon-Wood screens, Wakao), and a
  temperature-dependent stainless-steel solid;
- fixed-temperature heat-exchanger zones;
- energy and enthalpy-flow monitors.

## What "verified" means in this release

Each level has acceptance bars that were written into `docs/VERIFICATION.md` and committed before the level's runs.
Every number in a results table cites its file and line, and a miss is recorded as FAIL. "Verified" here means the
numerics were checked against those bars, with the outcomes below. **It does not mean validated:**
- nothing has been compared with experiments;
- the code-to-code comparison with ANSYS Fluent for the regenerator slice (L5 bars B1-B4) has not been done.

| level | case | reference | result |
|---|---|---|---|
| L0 | build + smoke | runs to completion from a clean clone | 8/8 PASS |
| L1 | closed tube, piston | lumped isentropic pressure amplitude, mass conservation, acoustic-CFL sensitivity | 15/15 PASS |
| L2 | porous plug, steady | closed-form Darcy-Forchheimer pressure drop | 16/16 PASS after the face-consistent drag fix; the first run's 12/16 FAIL is kept in `results/L2_run1` |
| L3 | LTNE relaxation, no flow | exact two-temperature ODE solution | 10/10 PASS |
| L4 | LTNE single blow | Schumann (Anzelius) solution | 6/6 PASS; the first run crashed on a k_s = 0 bug, kept in `results/L4_run1` |
| L5 | oscillating regenerator slice (Huang 2020 parameters) | self-consistency: energy closure, periodicity, piston flow, dt/dx sensitivity | 11/12 PASS as preregistered (L5.7 FAIL); supplementary check L5.7a PASS (Amendment A1) |
| L6 | grid, time-step and periodicity study of L5 | Celik et al. (2008) GCI | 17/21 PASS as preregistered; the apparent-order check fails for 4 of 5 QoIs |

The `verify` CI job re-runs L0-L4 on every pull request and checks their bars. L5 and L6 run through the
`run-case` workflow; their recorded results are in `results/L5` and `results/L6`.

## Known limitations and open points

- **L5.7 FAIL.** The four-term energy-closure formula registered before the runs (0.397 W against a bar of
  0.15 W) leaves out the conduction from the fixed-temperature HX solid into the matrix solid. The six-term closure
  (L5.7a) gives 0.020 W. See `docs/VERIFICATION.md`, Amendment A1.
- **The interface conduction is not grid-converged** (L6). That HX-solid to matrix-solid conduction grows with
  refinement (0.32, 0.48 and 0.66 W) because the solid layer sqrt(k_eff / hA), about 16-30 um, is unresolved on
  every grid tested (217-867 um cells). It should not be read as a converged physical quantity.
- **Apparent order** (L6).
  - H_joint and H_cold converge oscillatorily, within the periodic residual, so their order is not meaningful.
  - dp_amp and Qgs_abs converge below second order (p = 0.62 and 0.24). This was not isolated by a separate test.
  - All five GCI_fine values are below 3 %.
- **Cold-piston direction** (L5): the reading taken (+z, away from the matrix) was not confirmed by the leader.
- **dp amplitude**: the L5 dp amplitude is 23 % below the DeltaEC context value. The parameter file's drag is used
  verbatim; this was not investigated.
- **Closure checks**: they cannot detect heat losses that the model does not contain, such as the outer wall or the
  end faces.
- **Scope of the cases**: the cases are 1-D columns run on a single core. Multi-dimensional and parallel runs have
  not been tested.

## Requirements and reproduction

- **Software**: Ubuntu 22.04 or 24.04 and OpenFOAM v2512 from the ESI apt repository (`openfoam2512-dev`).
  `tools/install.sh` installs it and builds the solver.
- **Short levels** (L0-L4): `tools/run_level.sh <level> <outdir>`.
- **Long levels** (L5, L6): `cases/<level>_*/runLong.sh <outdir>`, or the `run-case` workflow.

## Data provenance

The cases use published, public data only:
- the closed-form benchmarks of L1-L4;
- Huang et al., Int. J. Refrigeration 111 (2020) 29-38, Table 1, for the L5 geometry and screens;
- the Sage v13 and DeltaEC Users Guide correlations and property fits;
- CoolProp helium property tables.

The DeltaEC face values in `params_L5.yaml` are context only, from the leader's DeltaEC replica of that published
machine; they are not a pass criterion.

Release preparation also included a confidentiality scan:
- no credentials or keys were found;
- container paths in recorded OpenFOAM logs were replaced by `<clone>` and `<WM_PROJECT_USER_DIR>`, with line numbers
  unchanged, so every `file:line` citation still holds.

## Licence, citation, authorship

- **Licence**: GPL-3.0-or-later (`LICENSE`). Copyright (C) 2026 Qiming Yu.
- **Citation**: `CITATION.cff` and README "How to cite".
- **Authorship**: developed with AI assistance (Anthropic Claude) under the author's direction.
- **Trademarks**: not approved or endorsed by OpenCFD Limited, owner of the OPENFOAM(R) trade mark.
