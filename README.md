# regen-ltne-foam

`ltneFoam`: an OpenFOAM solver for compressible, oscillating (piston-driven) helium flow through porous media with
local thermal non-equilibrium (LTNE). It is `rhoPimpleFoam` plus porosity-weighted storage terms, a solid-matrix
energy equation coupled to the gas by `h_sf a_sf (T_s - T_g)`, and a prescribed piston motion. Darcy-Forchheimer
drag coefficients are read from the standard `explicitPorositySource` entries and balanced on faces in the pressure
equation, with the cell velocity reconstructed from face fluxes (`docs/L2_FIX_DESIGN.md`). Reference model: Tew et al. 2006, NASA/TM (Fluent porous-media LTNE).
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
topology change or field mapping. This is used instead of layer addition/removal. Cell heights in the piston space
are h0 (1 - x_p / length), so the amplitude must stay below the piston-space length. Measured limit (L1 run d,
`results/L1`): at amplitude / piston-space length = 0.488, as in L5, the cell heights range from 0.512 to 1.488 h0. The
pressure amplitude is within 2.6e-6 of the isentropic lumped result, mass closure per cycle is 2.2e-14 and energy
closure 8.2e-6. Works for 1-D and 2-D axisymmetric (wedge) meshes with an axial piston.

## Limitations

Darcy-Forchheimer drag must be isotropic (`explicitPorositySource`, `DarcyForchheimer`); an anisotropic model, or any
other fvOption acting on U, stops with a fatal error. The transonic pressure formulation is not supported (fatal
error). Solid properties are constant.

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
| L0 build + smoke | `cases/L0_smoke` | PASS (8/8, merged) |
| L1 closed tube, piston | `cases/L1_closedTube` | PASS (15/15, merged) |
| L2 porous plug, steady | `cases/L2_porousPlug` | PASS (16/16 after the face-consistent drag fix, merged; first run FAIL 12/16 in `results/L2_run1`) |
| L3 LTNE relaxation | `cases/L3_ltneRelax` | PASS (10/10, merged) |
| L4 LTNE with flow | `cases/L4_singleBlow` | PASS (6/6, merged; first run crashed on a k_s = 0 bug, `results/L4_run1`) |
| L5 regenerator slice | | waiting for the leader's parameter file |

## License and rights

Copyright (C) 2026 Qiming Yu <qimingyu.alex@gmail.com>
Enterprise Research Fellow, University of Southampton.

This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version. It is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See [LICENSE](LICENSE).

This offering is not approved or endorsed by OpenCFD Limited, producer and distributor of the
OpenFOAM software via www.openfoam.com, and owner of the OPENFOAM(R) and OpenCFD(R) trade marks.
`ltneFoam` is an independent solver built on the OpenFOAM(R) libraries (ESI / openfoam.com
distribution).

The solver was developed with AI assistance (Anthropic Claude) under the author's direction;
every acceptance level is backed by the recorded runs and the CI in this repository. The
verification cases use published, public-domain benchmarks only. If you use this solver in
academic work, please cite this repository (a paper reference will be added when available).
