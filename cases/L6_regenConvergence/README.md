# L6 verification of the L5 regenerator slice

This level is a grid, time-step and periodicity study of the L5 case (`cases/L5_regenSlice`, Huang 2020 public
parameters via `params_L5.yaml`). The definition is by the author (Qiming Yu). The bars are in
`docs/VERIFICATION.md`, L6, and were committed before any L6 run.

- **What stays fixed**: the model, inputs, schemes and start-up are those of L5.
- **What varies**: only the mesh and the time step, in four runs.

| run | mesh (every block) | dt |
|---|---|---|
| G1 | x 0.5 of L5 (matrix 30 + 30 cells) | L5 dt (2400 steps/cycle) |
| G2 | the L5 mesh (60 + 60) | L5 dt |
| G3 | x 2 (120 + 120) | L5 dt |
| T2 | the L5 mesh | dt/2 (4800 steps/cycle) |

## Running

| command | what it does |
|---|---|
| `./runLong.sh <outdir> [minutes]` | builds the solver and runs G1, G2, G3 and T2 in parallel (one core each) |
| `./Allclean` | removes the run directories and logs |

- **Stopping rule**: each run proceeds in 10-cycle chunks until the periodic criterion holds, or until 300 cycles.
- **Deliverables**: then `l6.py final` writes them to `<outdir>`.
- **Restarts**: a run that is interrupted continues from its latest time; exit code 3 means the time budget is used.
- **On GitHub**: `.github/workflows/run-case.yml` with `level = L6` runs the same driver.

`l6.py` reuses the L5 per-cycle definitions (`cases/L5_regenSlice/results.py`) and adds two things:
- the four-term closure;
- the matrix gas-solid exchange, net and gross, from two new solver monitor columns (`matrix_Qgs`,
  `matrix_Qgs_abs`, summed over the cells outside the fixed-temperature HX zones).

`mkCase.py` (L5) takes `--grid-refine F` for the three grids. F = 1 writes exactly the L5 case.

## QoIs and why these

| QoI | what it measures |
|---|---|
| `H_hot`, `H_joint`, `H_cold` | the net enthalpy flow <H> at the three stations (the L5 definition) |
| `Qgs_abs` | the gas-solid heat exchange in the matrix: the cycle mean of sum \|hA (Ts - T)\| V |
| `dp_amp` | the pressure-drop amplitude across the matrix |

The net exchange `Qgs_net` is reported alongside. It has no bar because in a periodic state it only balances the
small axial solid conduction, so a relative criterion on it would be ill-posed.

## Formal order

- **Space**: 2. Linear interpolation and gradients; `limitedLinear` TVD convection for h and U, which falls to first
  order locally at extrema.
- **Time**: 1 (Euler). dt is the same on G1-G3, so the temporal error is common to the three grids.
