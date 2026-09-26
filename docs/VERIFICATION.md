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

## L3 LTNE relaxation, no flow

Committed before any L3 case (`cases/L3_ltneRelax`) was run.

Setup: closed 1-D block of 10 cells of 1 mm, cross-section 1e-4 m2, all walls adiabatic and closed, no mesh motion,
no drag entries. Helium as in L0 (Cp = 5193 J/kg/K, M = 4.0026), p0 = 2 MPa, gas T_g0 = 300 K, solid T_s0 = 320 K,
uniform porosity eps = 0.7, a_sf = 24000 1/m, h_sf = 1000 W/m2/K (hA = 2.4e7 W/m3/K), rho_s = 7900 kg/m3, k_s = 15
W/m/K. Two runs:
- r: c_s = 500 J/kg/K (stainless steel). C_s/C_g = 169.
- b: c_s = 5 J/kg/K, an artificial value chosen so that both temperatures move (C_s/C_g = 1.69).

Exact solution. The gas is at constant density, so C_g = eps rho c_v per unit volume, with c_v = Cp - R. Then
eps rho c_v dT_g/dt = hA (T_s - T_g) and (1 - eps) rho_s c_s dT_s/dt = hA (T_g - T_s), which give
- T_eq = (C_g T_g0 + C_s T_s0) / (C_g + C_s);
- T_g(t) = T_eq + (T_g0 - T_eq) exp(-t/tau) and T_s(t) = T_eq + (T_s0 - T_eq) exp(-t/tau);
- 1/tau = hA (1/C_g + 1/C_s).

From the inputs: tau = 2.899e-4 s (r) and 1.833e-4 s (b); T_eq = 319.883 K (r) and 312.573 K (b).

Time step dt = 2.9e-6 s (r) and 1.8e-6 s (b), about tau/100; 500 steps (about 5 tau). Implicit Euler gives an
expected maximum error of about (dt/tau)/2 * exp(-1) = 0.2 % of |T_s0 - T_g0|.

Definitions (every row of `postProcessing/ltneDiagnostics/0/ltne.dat`):
- T_g = (gasInternalEnergy / gasMass + Cp 298.15) / c_v, from the sensible-enthalpy reference of hConst; the field is
  uniform. c_v = 5193 - 8314.462618 / 4.0026.
- T_s = solidEnergy / (C_s V), with V = gasVolume / eps.
- C_g and C_s in the exact solution come from the inputs, with rho = gasMass / gasVolume from the first row.
- err_g = max over rows of |T_g - T_g,exact| / |T_s0 - T_g0|, and err_s likewise.
- energy = max over rows of |E(t) - E(0)| / Q, with E = gasInternalEnergy + gasKineticEnergy + solidEnergy and
  Q = C_g V |T_g0 - T_eq| (the energy exchanged).

| id | metric | op | bar | description |
|----|--------|----|-----|-------------|
| L3.1 | r_final_time | == | 0.00145 | run r reaches endTime |
| L3.2 | b_final_time | == | 0.0009 | run b reaches endTime |
| L3.3 | fatal_or_nan_count | == | 0 | lines matching `FOAM FATAL`, `nan` or `inf` over all logs |
| L3.4 | r_err_g | <= | 0.01 | run r: gas temperature against the exact solution |
| L3.5 | r_err_s | <= | 0.01 | run r: solid temperature against the exact solution |
| L3.6 | r_energy | <= | 1e-3 | run r: total energy conservation |
| L3.7 | b_err_g | <= | 0.01 | run b: gas temperature against the exact solution |
| L3.8 | b_err_s | <= | 0.01 | run b: solid temperature against the exact solution |
| L3.9 | b_energy | <= | 1e-3 | run b: total energy conservation |
| L3.10 | r_Teq | report | 0 | run r: T_g at endTime, K |
| L3.11 | b_Teq | report | 0 | run b: T_g at endTime, K |
| L3.12 | allclean_leftover | == | 0 | files under the case directory that `git status --porcelain --ignored` lists after `Allclean` |

## L4 LTNE with flow: single-blow transient (Schumann solution)

Committed before any L4 case (`cases/L4_singleBlow`) was run. The case and its source are proposed in the L4 PR
description.

Reference: T. E. W. Schumann, "Heat transfer: a liquid flowing through a porous prism", J. Franklin Inst. 208 (1929)
405-416. The same solution appears as the Anzelius-Schumann J-function in the regenerator literature (e.g. Schmidt &
Willmott, *Thermal Energy Storage and Regeneration*, 1981).

Model assumptions of the solution:
- 1-D plug flow at constant mass flux G;
- constant properties;
- no axial conduction in either phase;
- gas storage represented by the transport delay.

With xi = hA x / (G c_p) and eta = (hA / C_s) (t - eps rho x / G), where C_s = (1 - eps) rho_s c_s, and with a
step of the inlet gas temperature from T_0 to T_1 into a bed at T_0, the solution for theta = (T - T_0) / (T_1 - T_0)
is (derived by Laplace transform in eta):
- g(xi, tau) = exp(-xi - tau) I_0(2 sqrt(xi tau));
- theta_s(xi, eta) = integral from 0 to eta of g(xi, tau) d tau;
- theta_g(xi, eta) = g(xi, eta) + theta_s(xi, eta).

Setup:
- porous bed filling the whole 1-D channel, x in [0, 0.1] m, 200 cells of 0.5 mm, cross-section 1e-4 m2;
- helium as in L0 at 2 MPa; eps = 0.7, a_sf = 8000 1/m, h_sf = 20 W/m2/K (hA = 1.6e5 W/m3/K);
- rho_s = 7900 kg/m3, c_s = 500 J/kg/K, k_s = 0; no drag entries;
- initial gas and solid at T_0 = 300 K, U = 0.1 m/s everywhere;
- inlet: fixed U = 0.1 m/s and T = T_1 = 310 K; outlet: fixed p = 2 MPa;
- dt = 5e-3 s, run to t = 150 s (30000 steps).

Resulting numbers:
- G = rho(310 K) u = 0.31058 kg/m2/s;
- xi at the outlet = 9.920;
- hA / C_s = 0.13502 1/s, so eta at endTime = 20.25;
- gas transit time eps rho L / G = 0.70 s.

Definitions:
- theta_out(t) = (areaAverage(T) on the outlet patch - 300) / 10, from `postProcessing/outletT/0/surfaceFieldValue.dat`.
- out_err = max over rows with t >= 2 s of |theta_out - theta_g(9.920, eta(L, t))|.
- Es_err = max over every 100th row of `ltne.dat` (every 0.5 s) of
  |solidEnergy(t) - solidEnergy(0) - C_s A 10 K int_0^L theta_s dx| / (C_s V 10 K), with V = 1e-5 m3. The integral
  is evaluated with Simpson's rule on 400 intervals.
- Evaluation of the solution: with Poisson probabilities p_a(k) = exp(-a) a^k / k!, the integral form is equivalent
  to theta_s = sum_k p_xi(k) (1 - sum_{j<=k} p_eta(j)) and g = sum_k p_xi(k) p_eta(k). This follows from the series
  of I_0 and the incomplete gamma function. The sums are truncated when the terms fall below 1e-16.
- energy_err: the energy balance over the whole run, E(t_end) - E(0) against the net enthalpy inflow
  sum over rows of G A c_p (T_1 - T_out) dt, normalised by C_s V 10 K. E = gasInternalEnergy + gasKineticEnergy +
  solidEnergy. The inflow is integrated with the trapezoid rule over the outlet rows, which are written every
  20 steps.
- t_half: the first time at which theta_out reaches 0.5, by linear interpolation between rows.

| id | metric | op | bar | description |
|----|--------|----|-----|-------------|
| L4.1 | final_time | == | 150 | run reaches endTime |
| L4.2 | fatal_or_nan_count | == | 0 | lines matching `FOAM FATAL`, `nan` or `inf` over all logs |
| L4.3 | out_err | <= | 0.02 | outlet gas temperature (breakthrough curve) against Schumann, fraction of the step |
| L4.4 | Es_err | <= | 0.01 | solid energy stored against Schumann, fraction of the full-charge energy |
| L4.5 | energy_err | <= | 0.01 | whole-run energy balance, fraction of the full-charge energy |
| L4.6 | t_half | report | 0 | time when theta_out = 0.5, s |
| L4.7 | t_half_exact | report | 0 | the same from the Schumann solution, s |
| L4.8 | allclean_leftover | == | 0 | files under the case directory that `git status --porcelain --ignored` lists after `Allclean` |
