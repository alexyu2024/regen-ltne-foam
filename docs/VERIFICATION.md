# Verification bars

Rules (from `docs/TASK.md`): the bars of a level are committed before that level's case is run, and never change
afterwards. A miss is reported as FAIL with a diagnosis.

Machine-readable format. `tools/verify.py` reads every table row of the form

    | <id> | <metric> | <op> | <bar> | <description> |

where `<id>` is `L<level>.<n>`, `<metric>` is the key the level's `results.py` writes, `<op>` is one of
`==`, `<=`, `>=`, `<`, `>` (pass/fail) or `report` (measured, not pass/fail), and `<bar>` is a number. `==` means `|value - bar| <= 1e-9 * max(1, |bar|)`.
A metric that `results.py` could not read is "not read" and counts as FAIL.

## L0 Build and smoke run

Committed before the L0 smoke case (`cases/L0_smoke`) was run for the first time.

The smoke case is a 1-D closed helium tube with a sinusoidal piston (mesh motion), a Darcy-Forchheimer porous plug with
LTNE (solid initially 10 K warmer than the gas), run for a short time. It checks that the code runs; it is not a
physics check.

| id | metric | op | bar | description |
|----|--------|----|-----|-------------|
| L0.1 | solver_built | == | 1 | `ltneFoam` is on `PATH` after `src/Allwmake`, as printed by `Allrun` into `log.build` |
| L0.2 | end_line_count | == | 1 | `log.ltneFoam` contains exactly one line `End` (normal termination) |
| L0.3 | final_time | == | 0.001 | last `Time = ` in `log.ltneFoam` equals `endTime` 0.001 s |
| L0.4 | fatal_or_nan_count | == | 0 | lines matching `FOAM FATAL`, `nan` or `inf` (whole word, any case) over all `log.*` of the case |
| L0.5 | p_min | > | 0 | minimum of `min(p)` over all written `fieldMinMax` rows |
| L0.6 | T_min | > | 0 | minimum of `min(T)` over all written `fieldMinMax` rows |
| L0.7 | Ts_min | > | 0 | minimum of `min(Ts)` over all written `fieldMinMax` rows |
| L0.8 | allclean_leftover | == | 0 | files under the case directory that `git status --porcelain --ignored` lists after `Allclean` |

Clean clone: the recorded L0 result is produced from a fresh `git clone` of the branch, and CI runs from a fresh
checkout on every pull request.

## L1 Closed tube with a piston, no porous medium

Committed before any L1 case (`cases/L1_closedTube`) was run.

Rows with op `report` are measured and reported but not pass/fail; the number in the bar column is the interpretation
threshold stated in advance.

Setup (all runs): helium as in L0, p0 = 2 MPa, T0 = 300 K, 1-D tube of length L = 0.1 m (no side walls, so no wall
friction or wall heat transfer; end walls adiabatic), closed at x = L. Piston at x = 0 with displacement x_p(t) = x_a sin(2 pi f t),
f = 50 Hz, three cycles (endTime 0.06 s). Mesh motion `pistonLinear`, piston space [0, 5 mm]. The undeformed mesh is
the mean piston position.

| run | mesh | x_a | dt | acoustic CFL c dt / dx (c = 1019 m/s) | steps per cycle |
|---|---|---|---|---|---|
| a | 100 cells of 1 mm | 0.1 mm | 2e-5 s | 20.4 | 1000 |
| b | as a | 0.1 mm | 8e-5 s | 81.5 | 250 |
| c | as a | 0.1 mm | 4e-4 s | 408 | 50 |
| d | 50 cells of 0.1 mm in [0, 5 mm] + 95 cells of 1 mm | 2.44 mm (x_a / piston space = 0.488, as in L5) | 2e-6 s | 20.4 on the 0.1 mm cells | 10000 |

Definitions (all read from `postProcessing/ltneDiagnostics/0/ltne.dat` of each run, last cycle = the last
steps-per-cycle rows, t in (0.04, 0.06] s):
- p1, V1: first-harmonic amplitudes at f of the gas-volume-averaged pressure `pAvg` and of the gas volume `gasVolume`;
  p_m, V_m: their means over the last cycle.
- Lumped isentropic result (linear): p1_lumped = gamma p_m V1 / V_m, gamma = Cp / (Cp - R) = 1.66669. Valid when the
  tube is much shorter than the wavelength (k L = 2 pi f L / c = 0.031 here) and x_a << L. In linear acoustics the
  volume average of the standing-wave pressure equals this lumped value, so no k L correction applies to `pAvg`.
- Lumped isentropic result (nonlinear, for run d): p_iso(t) = C / V(t)^gamma with C = cycle mean of pAvg V^gamma;
  p1_iso is its first harmonic.
- mass closure per cycle: |m(0.06) - m(0.04)| / m(0.04), m = `gasMass`.
- energy closure per cycle: |[E(0.06) - E(0.04)] - [W(0.06) - W(0.04)]| / (p_m V1), E = `gasInternalEnergy` +
  `gasKineticEnergy`, W = `boundaryWork` (work done on the gas by the piston, accumulated from -p_b * meshPhi_b * dt).
- piston-space cell height: cell volume / cross-section (1e-4 m2), min and max over the `pistonSpace` zone and over
  the last cycle; ratio = max / min.

| id | metric | op | bar | description |
|----|--------|----|-----|-------------|
| L1.1 | a_final_time | == | 0.06 | run a reaches endTime (last `Time = ` in its log) |
| L1.2 | b_final_time | == | 0.06 | run b reaches endTime |
| L1.3 | c_final_time | == | 0.06 | run c reaches endTime |
| L1.4 | d_final_time | == | 0.06 | run d reaches endTime |
| L1.5 | fatal_or_nan_count | == | 0 | lines matching `FOAM FATAL`, `nan` or `inf` over all logs of all runs |
| L1.6 | a_p1_rel_err | <= | 0.005 | run a: abs(p1 / p1_lumped - 1) |
| L1.7 | a_mass_cycle | <= | 1e-8 | run a: mass closure over the last cycle |
| L1.8 | a_energy_cycle | <= | 1e-3 | run a: energy closure over the last cycle |
| L1.9 | b_p1_rel_err | <= | 0.01 | run b (CFL 81.5): abs(p1 / p1_lumped - 1) |
| L1.10 | b_mass_cycle | <= | 1e-8 | run b: mass closure over the last cycle |
| L1.11 | b_energy_cycle | report | 1e-3 | run b: energy closure over the last cycle |
| L1.12 | c_p1_rel_err | report | 0.01 | run c (CFL 408): abs(p1 / p1_lumped - 1); above 0.01 means the solver shows the large-CFL amplitude failure |
| L1.13 | c_p1_vs_a | report | 0.01 | abs(p1(c) / p1(a) - 1) |
| L1.14 | c_mass_cycle | report | 1e-8 | run c: mass closure over the last cycle |
| L1.15 | c_energy_cycle | report | 1e-3 | run c: energy closure over the last cycle |
| L1.16 | d_p1_iso_rel_err | <= | 0.01 | run d: abs(p1 / p1_iso - 1) |
| L1.17 | d_p1_rel_err | report | 0.01 | run d: abs(p1 / p1_lumped - 1) (linear formula at x_a / L = 0.0244) |
| L1.18 | d_mass_cycle | <= | 1e-8 | run d: mass closure over the last cycle |
| L1.19 | d_energy_cycle | <= | 1e-3 | run d: energy closure over the last cycle |
| L1.20 | d_hmin_mm | > | 0 | run d: minimum piston-space cell height over the last cycle, mm |
| L1.21 | d_hmax_mm | report | 0 | run d: maximum piston-space cell height over the last cycle, mm |
| L1.22 | d_h_ratio | report | 0 | run d: max / min piston-space cell height over the last cycle |
| L1.23 | allclean_leftover | == | 0 | files under the case directory that `git status --porcelain --ignored` lists after `Allclean` |

## L2 Porous plug, steady flow

Committed before any L2 case (`cases/L2_porousPlug`) was run.

Setup: helium as in L0 (ideal gas, Cp = 5193 J/kg/K, mu = 1.99e-5 Pa s), 1-D channel x in [0, 0.1] m, 100 cells of
1 mm, cross-section 1e-4 m2, no mesh motion, no solid energy equation (the gas is adiabatic). Porous plug x in
[0.04, 0.06] m (L = 0.02 m, 20 cells, porosity 0.7), `explicitPorositySource` DarcyForchheimer, isotropic d = 1e9 1/m2
(alpha = 1e-9 m2), f = C2 = 1e5 1/m. Inlet x = 0: fixed superficial velocity u_in, T = 300 K. Outlet x = 0.1 m: fixed
p = 2 MPa. Four runs, u_in = 0.001 (v1), 0.01 (v2), 0.1 (v3) and 1 m/s (v4), each from rest to t = 0.05 s with
dt = 1e-5 s (acoustic CFL 10).

Definitions (from the run's `postProcessing` function-object files, last written row, t = 0.05 s):
- dp = area-average p on the inlet patch - area-average p on the outlet patch. The open parts of the channel add
  only momentum-flux and viscous terms that are below 1e-5 of dp here (1-D, Mach <= 1e-3).
- G = |sum(phi)| on the inlet patch / 1e-4 m2 (mass flux); rho_p = volume-average rho over the `porous` zone;
  u = G / rho_p (superficial velocity in the plug).
- closed form: dp_cf = L (mu / alpha u + C2 rho_p u^2 / 2); rel_err = abs(dp / dp_cf - 1).
- ratio = (C2 rho_p u / 2) / (mu / alpha), Forchheimer term / Darcy term.
- steady = abs(dp(0.05) - dp(row nearest 0.045)) / dp(0.05).

| id | metric | op | bar | description |
|----|--------|----|-----|-------------|
| L2.1 | v1_final_time | == | 0.05 | run v1 reaches endTime |
| L2.2 | v2_final_time | == | 0.05 | run v2 reaches endTime |
| L2.3 | v3_final_time | == | 0.05 | run v3 reaches endTime |
| L2.4 | v4_final_time | == | 0.05 | run v4 reaches endTime |
| L2.5 | fatal_or_nan_count | == | 0 | lines matching `FOAM FATAL`, `nan` or `inf` over all logs of all runs |
| L2.6 | v1_rel_err | <= | 0.01 | run v1: dp against the closed form |
| L2.7 | v2_rel_err | <= | 0.01 | run v2: dp against the closed form |
| L2.8 | v3_rel_err | <= | 0.01 | run v3: dp against the closed form |
| L2.9 | v4_rel_err | <= | 0.01 | run v4: dp against the closed form |
| L2.10 | v1_ratio | <= | 0.1 | run v1 is in the Darcy regime |
| L2.11 | v4_ratio | >= | 1 | run v4 is in the Forchheimer regime |
| L2.12 | v2_ratio | report | 0 | run v2 Forchheimer / Darcy |
| L2.13 | v3_ratio | report | 0 | run v3 Forchheimer / Darcy |
| L2.14 | v1_steady | <= | 1e-3 | run v1 steady |
| L2.15 | v2_steady | <= | 1e-3 | run v2 steady |
| L2.16 | v3_steady | <= | 1e-3 | run v3 steady |
| L2.17 | v4_steady | <= | 1e-3 | run v4 steady |
| L2.18 | v1_dp | report | 0 | run v1 dp, Pa |
| L2.19 | v4_dp | report | 0 | run v4 dp, Pa |
| L2.20 | allclean_leftover | == | 0 | files under the case directory that `git status --porcelain --ignored` lists after `Allclean` |
