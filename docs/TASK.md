# TASK: an OpenFOAM LTNE porous-media solver for oscillating-flow cryocooler regenerators

## The user's words (verbatim, 2026-09-26)
"一个多月，目前有没有耗时久、Token 吞吐量巨大、需要反复跑测试的繁重任务全甩给云端，比如python；用得着/用不着跟我说"
(Context: the leader answered that the planned OpenFOAM LTNE solver is exactly such a task. The user's group runs the
same regenerator problem in ANSYS Fluent today; a licence-free solver is the route after the current HPC access ends.)

## Goal
A small, readable OpenFOAM application for **compressible, oscillating (piston-driven) flow of helium through porous
media with local thermal non-equilibrium (LTNE)**: a separate solid-matrix energy equation coupled to the gas by
h_sf * a_sf * (T_s - T_g), Darcy-Forchheimer drag, 1-D and 2-D axisymmetric, with moving pistons (dynamic mesh with
layering, or an equivalent you justify). Reference model: Tew et al. 2006, "An Initial Non-Equilibrium Porous-Media
Model for CFD Simulation of Stirling Regenerators" (NASA/TM). Prefer extending a standard OpenFOAM solver over writing
one from scratch; keep the code minimal.

## Hard rules
1. Public information only. Do not ask for, fetch or store any unpublished design, experimental data or proprietary
   file. No ANSYS software or files are available or needed.
2. Pick ONE OpenFOAM distribution (openfoam.com ESI or openfoam.org Foundation) and version, say why in `README.md`, and
   make the install reproducible with a script (`tools/install.sh`), so the leader can rebuild it on a Linux machine.
3. Every level below has acceptance bars. Write them into `docs/VERIFICATION.md` and COMMIT them BEFORE running that
   level's case. The bars never move afterwards. A miss is reported as FAIL with a diagnosis, never re-read as a pass.
4. Every number you report carries its source: the file and line (or file and row range) it was read from. A value
   you did not read is written "not read". Never fill a table cell from expectation.
5. One level = one pull request: code + case (`Allrun`/`Allclean`) + a results table (status table first:
   check | bar | value | PASS/FAIL) + the raw logs the table cites. Do not start level N+1 until level N passes, unless
   the leader says so in a PR comment.
6. When a result looks wrong, run the smallest experiment that separates the hypotheses, changing one factor at a time,
   before explaining it. A story whose numbers happen to fit is not evidence.
7. Name the characteristic numbers (acoustic CFL c*dt/dx, Womersley, thermal penetration depth vs pore size, Re) for
   every case before running it. Use them to choose dt and dx.
8. Re-read this file before starting each level. It is the leader's text; do not edit it. Questions and proposed
   changes go in a PR description or an issue.

## Levels
- **L0 Build**: install, compile the solver, a tiny smoke case runs to completion, `Allrun` works from a clean clone.
  Add a GitHub Actions workflow (`.github/workflows/verify.yml`) that installs OpenFOAM, builds the solver and, on
  every pull request, re-runs every level that has passed so far and checks its bars from `docs/VERIFICATION.md`
  mechanically (a script that reads the results and exits non-zero on a miss). Keep each CI case small (minutes).
  CI is the independent check of every PASS you claim.
- **L1 Closed tube, piston, no porous medium**: an adiabatic closed tube with a sinusoidal piston at one end, small
  amplitude. Compare the pressure amplitude with the lumped isentropic result p1 = gamma * p_m * dV / V (and state
  when that lumped result is valid: tube length << wavelength). Also report the mass conservation per cycle and the
  sensitivity of the pressure amplitude to the acoustic CFL (e.g. about 20, 86 and 400). The last one is a known failure
  mode in pressure-based solvers; show whether yours has it.
- **L2 Porous plug, steady flow**: the pressure drop through a Darcy-Forchheimer plug against the closed form
  dp = L * (mu/alpha * u + C2 * rho * u^2 / 2), over at least 3 velocities spanning the Darcy and Forchheimer regimes.
- **L3 LTNE relaxation, no flow**: a closed porous block with the gas and the solid at different initial temperatures.
  Compare T_g(t), T_s(t) and the conserved total energy with the exact two-temperature ODE solution.
- **L4 LTNE with flow**: a steady or single-blow case with a closed-form or well-documented published solution; you
  propose the case, with its source, in the PR description BEFORE running it.
- **L5 Oscillating regenerator slice**: the leader provides the parameter file (geometry, porosity, screen correlations,
  drive) when L4 passes. The comparison with the Fluent results is done by the leader locally from your PR.

## Where the computing runs (added 2026-09-26 by the leader)
This session's container is for writing code, compiling and SHORT checks (minutes). Any case that runs longer than
about 15 minutes runs as a GitHub Actions job instead (the account has GitHub Pro education minutes): a
`workflow_dispatch` workflow (`.github/workflows/run-case.yml`) that takes the case name, runs it, and uploads only
small result files (CSV summaries, logs trimmed to the lines the results table cites) as artifacts. A single job has a
time limit (6 h on GitHub-hosted runners, per GitHub's documentation), so long oscillating runs must write restart
data and continue across jobs. Trigger it, stop, and read the artifacts when the job has finished; do not keep the
container waiting on it.

## Reporting
Open each PR with the status table. Keep `README.md` short: what it is, how to install, how to run each level, the
current level status. No marketing text, no filler.

## L6 (added 2026-09-29 by the leader, leader-gen8; relayed by the owner, text verbatim)
L6 = verification of the L5 oscillating regenerator slice (Huang 2020 public parameters only). New branch stacked on
PR #10, one draft PR.
1. Add an "L6" section to docs/TASK.md with these pre-registered criteria BEFORE running anything; commit it first.
2. Periodic steady state: run until cycle-averaged QoIs (net enthalpy flow, gas-solid heat exchange, pressure-drop
   amplitude) change < 0.1 % between consecutive cycles; report the cycle count.
3. Grid convergence: three grids, refinement ratio >= 1.3, Celik et al. (2008) GCI on the same QoIs; pass = GCI_fine
   < 3 % and apparent order within 0.5 of the formal order, or state why not.
4. Time-step convergence: two time steps (ratio 2); pass = QoI change < 1 %.
5. Energy ledger: report both the registered four-term closure and the six-term closure per cycle; explain physically
   which terms the four-term form omits. Do not move the L5.7 bar.
6. Cost: ESI prebuilt, coarse grids first, each long run launched once without polling; stop after the draft PR; first
   line of the PR description = DONE/BLOCKED + one sentence.
L7 (later, not now) will be the full Huang 2020 low-temperature stage.
