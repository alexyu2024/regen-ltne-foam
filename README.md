# regen-ltne-foam

`ltneFoam`: an OpenFOAM solver for compressible, oscillating (piston-driven) helium flow through porous media with
local thermal non-equilibrium (LTNE). It is `rhoPimpleFoam` plus porosity-weighted storage terms, a solid-matrix
energy equation coupled to the gas by `h_sf a_sf (T_s - T_g)`, and a prescribed piston motion. Darcy-Forchheimer
drag uses the standard `explicitPorositySource`. Reference model: Tew et al. 2006, NASA/TM (Fluent porous-media LTNE).
Task: `docs/TASK.md`. Acceptance bars: `docs/VERIFICATION.md`.

## Distribution: OpenFOAM v2512 (openfoam.com, OpenCFD/ESI), apt package `openfoam2512-dev` 2512.0-2

- `rhoPimpleFoam` is still a classic, self-contained application in this distribution, so the solver is a short
  diff against a standard solver (`src/ltneFoam`). In openfoam.org v11+ the solvers are modules of `foamRun`, and the
  API changes between yearly versions.
- The Darcy-Forchheimer model (`d` = 1/permeability, `f` = C2) takes the same coefficients as Fluent's porous zone,
  which helps the leader's comparison with the Fluent results.
- Official binary packages for Ubuntu 22.04/24.04 with a pinned version make `tools/install.sh` reproducible, and
  one six-monthly release is supported for years.

## Piston motion

`src/pistonMotion` (`motionSolver pistonLinear`) moves the mesh points between each piston face and a fixed plane
linearly along the axis. Nothing moves outside the piston spaces, so porous zones stay stationary, and there is no
topology change or field mapping. This is used instead of layer addition/removal. It is valid while the stroke is
small compared with the piston-space length; the cells there are stretched by at most `stroke / length`. Works for
1-D and 2-D axisymmetric (wedge) meshes with an axial piston.

## Install and build (Ubuntu 22.04 or 24.04)

    sudo tools/install.sh
    source /usr/lib/openfoam/openfoam2512/etc/bashrc     # in every new shell

`tools/install.sh` adds the openfoam.com apt repository, installs `openfoam2512-dev=2512.0-2` and runs
`src/Allwmake`.

## Run a level

    tools/run_level.sh L0 results/L0    # Allclean, Allrun, extract metrics, Allclean, check bars

Or by hand: `cases/<level>_*/Allrun`, `cases/<level>_*/Allclean`. `tools/verify.py` compares
`<outdir>/results.csv` (every value with its file and line) with the bars and writes `<outdir>/STATUS.md`. CI
(`.github/workflows/verify.yml`) does the same on every pull request for each level in `tools/ci_levels.txt`.

## Status

| level | case | status |
|---|---|---|
| L0 build + smoke | `cases/L0_smoke` | in review |
| L1 closed tube, piston | | not started |
| L2 porous plug, steady | | not started |
| L3 LTNE relaxation | | not started |
| L4 LTNE with flow | | not started |
| L5 regenerator slice | | not started |
