# Verification bars

Rules: the bars of a level are committed before that level's case is run, and never change
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

## L5 Oscillating regenerator slice (Huang 2020, the author's parameter file)

Committed before any L5 run, including debugging runs. The preregistered pass bars are B1-B6 in
`cases/L5_regenSlice/params_L5.yaml` (lines 376-389), quoted unchanged in the L5 PR. B1-B4 are code-to-code bars
for a comparison with a Fluent twin by the author (Qiming Yu); they are listed below as `report` rows with the values
this solver produces. The pass/fail rows below are the self-checks of this level: B5, B6, the realised
piston flow, the dt/dx sensitivity check, completion, and the crash-pattern count.

Pre-registered improvement (L4 review): the crash pattern now also matches `Floating point exception` and
`Segmentation fault`.

Interpretations, stated before any run:
- **Start-up.** `initial_conditions` asks for pistons at the mean position, and the drive phases define t = 0.
  Both pistons cannot be at mid-stroke at t = 0 with the given phases. The mesh therefore starts at the mean
  position (so the gas mass at 0.75 MPa is as specified), and each piston follows
  x(t) = |x| [cos(omega t + Ph) - cos(Ph) exp(-t / T_cycle)]. After 10 cycles the correction term is below
  5e-5 |x|, so it does not affect the analysed cycles.
- **Sensitivity check phases.** "B1/B2 quantities move < 1 %" is applied to amplitudes as a relative change. For
  phases a relative change is meaningless (they are near 0), so the phase bar is an absolute change of 0.5 deg.

Definitions:
- Cycle k spans [t_s + (k-1) T, t_s + k T], with T = 1/23 s and t_s = 0.
- Phasors come from a first-harmonic least-squares fit over one cycle, in the file's convention
  x = x_mean + |x| cos(omega t + Ph).
- Face quantities are taken on the face zones at z = 0 (hot face), z = 0.026 m (joint) and z = 0.052 m (cold face).
- H = sum over the face zone of [phi (h + K) - (eps k_g snGrad T + k_eff,s snGrad T_s) |S_f|]. <H> is its
  cycle mean.
- B5 closure = |<W_hot piston> + <W_cold piston> + <Q_hot HX -> gas> + <Q_cold HX -> gas>| over the last cycle,
  in W.
- B6a = max over the last 5 cycles of |mean T_joint(k) - mean T_joint(k-1)|, in K. B6b = max over the last 5 cycles
  of |<H_matrix>(k) - <H_matrix>(k-1)| / |<H_matrix>(k)|, with H_matrix the joint-face <H>.
- Piston check: the realised piston volume flow U_p = -sum(meshPhi) over the piston patch, fitted over the last
  cycle, against U_amp_m3_s and U_phase_deg in the file.
- Sensitivity: the sensitivity run restarts from the converged state with dt/2 and matrix dx/2 (mapped fields) and
  runs 5 cycles. Its last-cycle B1/B2 quantities (face |p|, |mdot| and their phases at both faces; the dp
  amplitude) are compared with the base run's last cycle.

| id | metric | op | bar | description |
|----|--------|----|-----|-------------|
| L5.1 | cycles_run | >= | 40 | base run: completed cycles (params: at least 40, then until B6 holds) |
| L5.2 | crash_count | == | 0 | log lines matching `FOAM FATAL`, `nan`, `inf`, `Floating point exception` or `Segmentation fault` over all logs of all runs |
| L5.3 | piston_hot_amp_err | <= | 0.005 | realised hot piston volume-flow amplitude, relative error |
| L5.4 | piston_hot_phase_err_deg | <= | 0.5 | realised hot piston volume-flow phase, abs error, deg |
| L5.5 | piston_cold_amp_err | <= | 0.005 | realised cold piston volume-flow amplitude, relative error |
| L5.6 | piston_cold_phase_err_deg | <= | 0.5 | realised cold piston volume-flow phase, abs error, deg |
| L5.7 | B5_closure_W | < | 0.15 | B5: last-cycle boundary energy-flow closure, W |
| L5.8 | B6a_dTjoint_K | < | 0.1 | B6: last-5-cycle change of cycle-mean T at the joint, K per cycle |
| L5.9 | B6b_dH_rel | < | 0.02 | B6: last-5-cycle relative change of the matrix <H>, per cycle |
| L5.10 | sens_amp_max_rel | < | 0.01 | sensitivity: max relative change of the B1/B2 amplitudes (6 values) |
| L5.11 | sens_phase_max_deg | <= | 0.5 | sensitivity: max abs change of the B1 phases (4 values), deg |
| L5.12 | hot_p_amp_Pa | report | 0 | B1: hot face |p| (context: DeltaEC 67505.9) |
| L5.13 | hot_p_ph_deg | report | 0 | B1: hot face p phase (DeltaEC -0.30) |
| L5.14 | hot_mdot_amp | report | 0 | B1: hot face |mdot|, kg/s (DeltaEC 0.00214156) |
| L5.15 | hot_mdot_ph_deg | report | 0 | B1: hot face mdot phase (DeltaEC 25.54, the U phase) |
| L5.16 | cold_p_amp_Pa | report | 0 | B1: cold face |p| (DeltaEC 52775.8) |
| L5.17 | cold_p_ph_deg | report | 0 | B1: cold face p phase (DeltaEC -1.89) |
| L5.18 | cold_mdot_amp | report | 0 | B1: cold face |mdot| (DeltaEC 0.00260769) |
| L5.19 | cold_mdot_ph_deg | report | 0 | B1: cold face mdot phase |
| L5.20 | dp_amp_Pa | report | 0 | B2: fitted dp amplitude across the matrix (DeltaEC 14730.2) |
| L5.21 | H_hot_W | report | 0 | B3: <H> at the hot face (DeltaEC 1.8275) |
| L5.22 | H_joint_W | report | 0 | B3: <H> at the joint |
| L5.23 | H_cold_W | report | 0 | B3: <H> at the cold face |
| L5.24 | Tjoint_mean_K | report | 0 | B4 context: cycle-mean T at the joint (DeltaEC 28.036) |
| L5.25 | allclean_leftover | == | 0 | files under the case directory that `git status --porcelain --ignored` lists after `Allclean` |

### Amendment A1 (2026-09-28, by the author; added after the L5 runs)

The table above and the B5 definition above are unchanged. This amendment records how L5.7 is read and adds one
supplementary check.

**L5.7 is a FAIL as registered.**
- The registered B5 formula was committed in 1c929126 before any L5 run. Quoted from the definitions above:
  "B5 closure = |<W_hot piston> + <W_cold piston> + <Q_hot HX -> gas> + <Q_cold HX -> gas>| over the last cycle,
  in W."
- Its value on cycle 40 of the base run is 0.396531 W, against a bar of < 0.15 W.
- Why it fails: the four-term formula leaves out the conduction between each fixed-temperature HX solid and the
  neighbouring matrix solid. The parameter file's B5 (`cases/L5_regenSlice/params_L5.yaml`, "piston work in, HX solid
  heat out") covers heat leaving through the fixed-temperature HX solid, and that heat takes two paths: convection to
  the gas and conduction to the matrix solid. The defect is in the bar's formula, not in the solver.
- Order of events:
  1. The four-term bar was registered in 1c929126.
  2. A 10-cycle local test then missed it by 0.39 W.
  3. The six-term formula entered `cases/L5_regenSlice/results.py` in 7521e0df, before the first CI `run-case` job.
  4. From 7521e0df up to this amendment, `results.py` reported the six-term value under L5.7.

**L5.7a, a supplementary check.** It was added after the runs, so it is not a preregistered bar.
- Formula: the four terms of L5.7 plus the conduction from each HX solid into the matrix solid:
  |<W_hot> + <W_cold> + <Q_hot HX -> gas> + <Q_cold HX -> gas> + <Q_hot HX solid -> matrix solid> +
  <Q_cold HX solid -> matrix solid>| over the last cycle, in W.
- On the sensitivity run (cycle 45), the same six-term closure is 0.041609 W and the four-term value is 0.508583 W.
  This shows the same definition holding at dt/2 and dx/2. It is not an independent verification.
- Neither B5 nor L5.7a can detect heat losses that the model does not contain, such as the outer wall or the end faces.

| id | metric | op | bar | description |
|----|--------|----|-----|-------------|
| L5.7a | B5_closure6_W | < | 0.15 | supplementary (Amendment A1, after the runs): six-term last-cycle closure including HX solid -> matrix solid conduction, W |

**L5.10 counting error.** "(6 values)" in the L5.10 description is a counting error. The sensitivity definition
above lists five amplitudes: |p| and |mdot| at both faces, and the dp amplitude. `results.py` has always used those
five. No quantity was added and nothing was re-run.

## L6 Verification of the L5 regenerator slice (the author's definition)

Committed before any L6 run, including debugging runs. The model, inputs and numerics are the L5 case
(`cases/L5_regenSlice`, `params_L5.yaml`, Huang 2020 public parameters) with only the mesh and the time step varied.
The L5.7 bar and every L5 row are unchanged.

Runs (each starts from the file's initial state at t = 0, with the L5 start-up):

| run | cells: hot chamber, hot HX, matrix 500#, matrix 635#, cold HX, cold chamber | matrix dx | dt (steps per cycle) |
|---|---|---|---|
| G1 coarse | 12, 5, 30, 30, 5, 4 | 0.8667 mm | 1.8115942e-5 s (2400) |
| G2 medium (= L5 mesh) | 24, 10, 60, 60, 10, 8 | 0.4333 mm | 1.8115942e-5 s (2400) |
| G3 fine | 48, 20, 120, 120, 20, 16 | 0.2167 mm | 1.8115942e-5 s (2400) |
| T2 (G2 mesh, dt/2) | 24, 10, 60, 60, 10, 8 | 0.4333 mm | 9.0579710e-6 s (4800) |

Every block is refined by the same factor, so the refinement ratio is r = 2 everywhere (>= 1.3). The face zones at
z = 0, 0.026 and 0.052 m are block boundaries on all grids.

Characteristic numbers per run, stated before the runs. The G2 values are those in the L5 case README; the other
runs scale with dx and dt. Hot face (500#, 80 K) / cold face (635#, 22 K):

| run | NTU per matrix cell | acoustic CFL c dt / dx | convective CFL (u/eps) dt / dx |
|---|---|---|---|
| G1 | 15.7 / 14.3 | 11 / 5.8 | 0.026 / 0.009 |
| G2 | 7.8 / 7.2 | 22 / 11.5 | 0.051 / 0.018 |
| G3 | 3.9 / 3.6 | 44 / 23 | 0.10 / 0.036 |
| T2 | 7.8 / 7.2 | 11 / 5.8 | 0.026 / 0.009 |

QoIs, each the cycle average over one cycle (cycle k spans [(k-1) T, k T], T = 1/23 s):
- H_hot, H_joint, H_cold: the net enthalpy flow <H> at the matrix hot face, the joint and the matrix cold face (the
  L5 definition of H).
- Qgs_abs: the gas-solid heat exchange in the matrix, as the cycle mean of sum over the matrix cells of
  |hA (Ts - T)| V, in W. The absolute value is used because the net cycle mean of hA (Ts - T) V is close to zero in
  a periodic state (it balances the small axial solid conduction), so a relative criterion on it would be
  ill-posed. The net value, Qgs_net, is reported alongside but has no bar.
- dp_amp: the first-harmonic amplitude of p(hot face) - p(cold face), in Pa (the L5 definition).

Periodic steady state (criterion 2):
- Each run proceeds in 10-cycle chunks.
- It is periodic at the first check with at least 40 cycles (the L5 minimum) at which every QoI changed by less than
  0.1 % (|q_k - q_(k-1)| / |q_k| < 0.001) over each of the last 5 consecutive cycle pairs.
- The reported cycle count is that cycle k.
- A run that is not periodic by cycle 300 stops, its row is FAIL, and its last cycle is still used below.

Grid convergence (criterion 3), after Celik et al. (2008), J. Fluids Eng. 130, 078001:
- phi1, phi2 and phi3 are the QoI on G3, G2 and G1 (fine to coarse); r = 2; e21 = phi2 - phi1, e32 = phi3 - phi2.
- Apparent order: p = |ln|e32 / e21|| / ln 2, which with a constant r needs no iteration.
- GCI_fine = 1.25 |(phi1 - phi2) / phi1| / (2^p - 1).
- Formal order 2 in space: linear interpolation and gradients; limitedLinear (TVD) convection for h and U, which is
  second order away from local extrema. Time is Euler (first order) and dt is the same on all three grids.
- Pass for each QoI: GCI_fine < 3 % and |p - 2| <= 0.5.
- If e32 / e21 < 0 (oscillatory convergence), p and GCI are still computed as above and the case is flagged in the
  results README.
- A value that cannot be computed (e21 = 0 or e32 = 0) is FAIL.

Time-step convergence (criterion 4): the relative change |q(T2) - q(G2)| / |q(T2)| for each QoI, pass < 1 %.

Energy ledger (criterion 5), per cycle for every run, in `per_cycle_<run>.csv`:
- four-term closure = <W_hot> + <W_cold> + <Q_hot HX -> gas> + <Q_cold HX -> gas> (the registered L5.7 form);
- six-term closure = the four terms + <Q_hot HX solid -> matrix solid> + <Q_cold HX solid -> matrix solid>
  (L5.7a, Amendment A1).
Both are reported for the last cycle of every run; neither has a bar here.

| id | metric | op | bar | description |
|----|--------|----|-----|-------------|
| L6.1 | cycles_G1 | <= | 300 | G1: cycle count at which the periodic criterion holds |
| L6.2 | cycles_G2 | <= | 300 | G2: cycle count at which the periodic criterion holds |
| L6.3 | cycles_G3 | <= | 300 | G3: cycle count at which the periodic criterion holds |
| L6.4 | cycles_T2 | <= | 300 | T2: cycle count at which the periodic criterion holds |
| L6.5 | gci_H_hot | < | 0.03 | GCI_fine of H_hot |
| L6.6 | gci_H_joint | < | 0.03 | GCI_fine of H_joint |
| L6.7 | gci_H_cold | < | 0.03 | GCI_fine of H_cold |
| L6.8 | gci_Qgs_abs | < | 0.03 | GCI_fine of Qgs_abs |
| L6.9 | gci_dp_amp | < | 0.03 | GCI_fine of dp_amp |
| L6.10 | p_err_H_hot | <= | 0.5 | abs(apparent order - 2), H_hot |
| L6.11 | p_err_H_joint | <= | 0.5 | abs(apparent order - 2), H_joint |
| L6.12 | p_err_H_cold | <= | 0.5 | abs(apparent order - 2), H_cold |
| L6.13 | p_err_Qgs_abs | <= | 0.5 | abs(apparent order - 2), Qgs_abs |
| L6.14 | p_err_dp_amp | <= | 0.5 | abs(apparent order - 2), dp_amp |
| L6.15 | dt_rel_H_hot | < | 0.01 | time step: relative change of H_hot, G2 vs T2 |
| L6.16 | dt_rel_H_joint | < | 0.01 | time step: relative change of H_joint, G2 vs T2 |
| L6.17 | dt_rel_H_cold | < | 0.01 | time step: relative change of H_cold, G2 vs T2 |
| L6.18 | dt_rel_Qgs_abs | < | 0.01 | time step: relative change of Qgs_abs, G2 vs T2 |
| L6.19 | dt_rel_dp_amp | < | 0.01 | time step: relative change of dp_amp, G2 vs T2 |
| L6.20 | crash_count | == | 0 | log lines matching `FOAM FATAL`, `nan`, `inf`, `Floating point exception` or `Segmentation fault` over all logs of all runs (the `trapFpe: Floating point exception trapping enabled` start-up banner excepted, as in L5) |
| L6.21 | closure4_G2_W | report | 0 | four-term closure, last cycle of G2, W |
| L6.22 | closure6_G2_W | report | 0 | six-term closure, last cycle of G2, W |
| L6.23 | closure4_G3_W | report | 0 | four-term closure, last cycle of G3, W |
| L6.24 | closure6_G3_W | report | 0 | six-term closure, last cycle of G3, W |
| L6.25 | allclean_leftover | == | 0 | files under the case directory that `git status --porcelain --ignored` lists after `Allclean` |

## L5D Decay ratio of the slow matrix thermal relaxation (L5 slice; the author's request, 2026-10-20)

Committed before the run. This is a measurement reported as is: it has no pass/fail bar on r. Only the crash scan
and Allclean have bars.

- **Run**: the L5 case unchanged (`cases/L5_regenSlice`: mesh, dt, inputs and start-up, i.e. the L6 G2 run), from
  the file's initial state at t = 0, in 50-cycle chunks.
- **Quantity**: the cycle-mean gas temperature at the 500#/635# joint, T_k (the L5 `Tjoint_mean`). It follows the
  matrix's slow thermal state. H_joint and H_hot (cycle-mean <H>, L5 definition) are evaluated the same way and
  reported alongside.
- **Per-cycle decay ratio**: d_k = T_k - T_(k-1) and r_k = d_k / d_(k-1).
- **Stopping rule**:
  - stop at the first chunk end with k >= 200 at which the mean of r_k over cycles k-49..k differs from its mean
    over k-99..k-50 by less than 1e-4;
  - otherwise stop at 1500 cycles, and report r as not yet stationary.
- **Reported values**:
  - **r_fit**: exp of the least-squares slope of ln|d_k| against k over the last 100 cycles. The window mean of r_k
    over the last 50 cycles is reported beside it.
  - **Time constant**: tau = -1 / ln(r_fit) cycles, and tau / f in seconds.
  - **Extrapolated periodic limit**: T_inf = T_k + d_k r_fit / (1 - r_fit).
  - **H_joint and H_hot**: the same r_fit.
  - **Full series**: k, T_k, d_k and r_k for every cycle, in `decay.csv`.

| id | metric | op | bar | description |
|----|--------|----|-----|-------------|
| L5D.1 | cycles_run | report | 0 | cycles run |
| L5D.2 | r_fit_Tjoint | report | 0 | decay ratio per cycle, T_joint, last 100 cycles |
| L5D.3 | r_mean50_Tjoint | report | 0 | mean of r_k over the last 50 cycles, T_joint |
| L5D.4 | r_window_change | report | 0 | change of the 50-cycle mean of r_k between the last two windows (stopping test) |
| L5D.5 | tau_cycles | report | 0 | time constant, cycles |
| L5D.6 | tau_s | report | 0 | time constant, s |
| L5D.7 | Tjoint_inf_K | report | 0 | extrapolated periodic-limit T_joint, K |
| L5D.8 | Tjoint_last_K | report | 0 | T_joint on the last cycle, K |
| L5D.9 | r_fit_H_joint | report | 0 | decay ratio per cycle, H_joint, last 100 cycles |
| L5D.10 | r_fit_H_hot | report | 0 | decay ratio per cycle, H_hot, last 100 cycles |
| L5D.11 | crash_count | == | 0 | crash patterns over all logs (as L5, trapFpe banner excepted) |
| L5D.12 | allclean_leftover | == | 0 | files left under the case directory after `Allclean` |

## LP Real-gas helium properties (ltneRealGas library; CoolProp table vs NIST)

Committed before the check program was first run. The optional real-gas model (`src/ltneRealGas`) reads a T-p
table generated from CoolProp 8.0.0 (`tools/heliumRealGas/genHeliumTable.py`) and interpolates bilinearly. The
ideal-gas model stays the default; no existing case changes.

- **Check program**: `realGasPropsCheck` builds OpenFOAM's own thermo object (`rhoThermo::New`) for the real-gas
  selection. It evaluates the density with `rhoEoS(p, T)` and c_p with `Cp(p, T)` at the points of
  `cases/LP_heliumRealGas/nist_helium.csv`.
  - The NIST values are taken from the NIST Chemistry WebBook (SRD 69), retrieved 2026-10-23.
  - Rows 1-3 are table nodes at 0.75 MPa: 22, 50 and 80 K.
  - Rows 4-6 are cell centres, 22.125, 50.125 and 80.125 K at 0.7625 MPa, where bilinear interpolation error is
    largest.
- **Relative difference**: |model / NIST - 1|.
- **Round trip**: the largest |T - T(h(T, p))| over the six points, computed with `he` and then `THE` (OpenFOAM's
  Newton iteration from enthalpy to temperature, started 5 % off).
- **Transport**: viscosity and conductivity are reported from the thermo fields at the case's cell state (50 K,
  0.75 MPa), with no bar.

| id | metric | op | bar | description |
|----|--------|----|-----|-------------|
| LP.1 | rho_rel_22 | <= | 0.001 | density, 22 K, 0.75 MPa (table node) |
| LP.2 | rho_rel_50 | <= | 0.001 | density, 50 K, 0.75 MPa (table node) |
| LP.3 | rho_rel_80 | <= | 0.001 | density, 80 K, 0.75 MPa (table node) |
| LP.4 | cp_rel_22 | <= | 0.001 | c_p, 22 K, 0.75 MPa (table node) |
| LP.5 | cp_rel_50 | <= | 0.001 | c_p, 50 K, 0.75 MPa (table node) |
| LP.6 | cp_rel_80 | <= | 0.001 | c_p, 80 K, 0.75 MPa (table node) |
| LP.7 | rho_rel_22c | <= | 0.001 | density, 22.125 K, 0.7625 MPa (cell centre) |
| LP.8 | rho_rel_50c | <= | 0.001 | density, 50.125 K, 0.7625 MPa (cell centre) |
| LP.9 | rho_rel_80c | <= | 0.001 | density, 80.125 K, 0.7625 MPa (cell centre) |
| LP.10 | cp_rel_22c | <= | 0.001 | c_p, 22.125 K, 0.7625 MPa (cell centre) |
| LP.11 | cp_rel_50c | <= | 0.001 | c_p, 50.125 K, 0.7625 MPa (cell centre) |
| LP.12 | cp_rel_80c | <= | 0.001 | c_p, 80.125 K, 0.7625 MPa (cell centre) |
| LP.13 | T_roundtrip_max_K | report | 0 | largest temperature error of h(T, p) -> T, K |
| LP.14 | mu_rel_50 | report | 0 | viscosity at 50 K, 0.75 MPa, relative difference to NIST |
| LP.15 | kappa_rel_50 | report | 0 | thermal conductivity at 50 K, 0.75 MPa, relative difference to NIST |
| LP.16 | allclean_leftover | == | 0 | files under the case directory that `git status --porcelain --ignored` lists after `Allclean` |

**LP addendum (2026-10-24, the author's request; added before the out-of-range check was first run).** A state outside
the table, 15-95 K and 0.5-1.0 MPa, must stop the run with an error: never extrapolate, never clamp silently.
`realGasPropsCheck -dict <file>` is run on four points just outside the table, each in its own run: 14.9 K and
95.1 K at 0.75 MPa, and 0.499 MPa and 1.001 MPa at 50 K. A run counts as correct if it exits non-zero and its log
contains `is outside the table`.

| id | metric | op | bar | description |
|----|--------|----|-----|-------------|
| LP.17 | out_of_range_stopped | == | 4 | of the 4 out-of-table runs, how many stop with the out-of-table error |
| LP.18 | out_of_range_values_written | == | 0 | of the 4 out-of-table runs, how many still wrote property values |

## LRG Real-gas against ideal-gas helium on the L5 slice (the author's request, 2026-10-24)

Committed before any LRG run. The real-gas run starts only after the L5P ideal-gas reference has passed L5P.3 under
L5P Amendment A2. It uses the L5P tools (`cases/L5P_periodicState/pss`) for the quantities, so it needs them on
`main` first.

**Ideal-gas side: no new run.** q_ideal is q_ref of the accepted L5P natural reference at N_ref.

**Real-gas run.** It continues the L5P reference from a restart point, with natural cycles only and no jumps.
- **Unchanged:** the mesh, dt, schemes, start-up history and every case input.
- **Changed:** only the gas model, as `mkCase.py --gas real` writes it: thermophysicalProperties, the table,
  `libs (ltneRealGas)` and `enthalpyReferenceCp`.
- **Restart check:** the restart point used is the latest L5P restart point N_r strictly before N_ref. The ideal gas
  is first continued from N_r to N_ref, and every quantity on cycles N_r+1..N_ref must reproduce the reference's
  per-cycle table (LRG.1). Only then is the gas switched, at N_ref.
- **At the switch:** the `rho` field is removed from the state, so the solver recomputes rho from p and T with the
  real-gas equation of state. U, phi and the other carried fields stay as they are.
- **Charge basis: equal initial mean pressure.** The p and T fields at N_ref are used unchanged.
  - The gas inventory then differs from the ideal-gas reference: M_real0 = sum eps rho_real(p, T) V against
    M_ideal = sum eps p / (R T) V, with R = 2077.3 J/kg/K from `params_L5.yaml`.
  - An estimate from the L5 cycle-40 profile (`results/L5/profiles.csv`) is -0.64 %: -1.2 to -1.4 % in the warm
    half, +0.04 % at the cold end. LRG.2 reports the value from the reference fields.
  - Equal mass would need p about 0.64 % higher. That run is not made.
  - Every real/ideal difference below is at equal initial mean pressure.

**Quantities and tolerances: those of L5P, unchanged.**
- The quantities are Q_hot, Q_cold, dT_seg1..4, Ts_seg1..4_mean, T_joint and p_mean, with the L5P tol_q.
- They are computed by the L5P tools, with one change: the gas mass is sum eps rho V with the solver's `rho` field,
  not p / (R T).
- p_mean, the gas-volume-weighted pressure at the cycle boundary, has no equation of state in it and is unchanged.

**Periodic acceptance: the L5P Amendment A2 rule, applied to the real-gas run itself.**
- **r_A2:** the largest valid fit of r over the last 100 and the last 200 cycles, over every quantity.
- **Remaining distance:** R_q = |q(N) - q(N - 50)| / 50 x r_A2 / (1 - r_A2). The run passes when max_q R_q / tol_q
  <= 0.2.
- **Schedule:** the first test is at N_ref + 400, so that both fit windows lie after the switch transient. Then the
  test runs after every 100-cycle chunk.
- **Cap:** N_ref + 6000 cycles, about 7.3 time constants of 820 cycles (the L5P late decay ratio r = 0.99878; slow
  mode at the hot end). If the run has not passed by the cap, LRG.4 is FAIL and the cap state is reported.
- **Expected length:** with an initial offset of order 0.1-0.5 K in the matrix temperatures, about 3000-4500 cycles.
  At about 7.5 s per cycle on a GitHub runner that is 6-10 h, or 2-3 chained `run-case` jobs; the cap is about 12.5 h.

**Reported:**
- **dQ_x_rel** = (Q_x,real - Q_x,ideal) / Q_x,ideal, for x = hot and cold. Each comes with an uncertainty
  dQ_x_unc = (R_Qx,real + R_Qx,ideal) / |Q_x,ideal|, the two remaining distances.
- **p_mean drift** relative to the reference value, (p_mean,real(N_acc) - p_mean,ideal(N_ref)) / p_mean,ideal(N_ref).
  The per-cycle series is in the results.

| id | metric | op | bar | description |
|----|--------|----|-----|-------------|
| LRG.1 | restart_check_rel | <= | 1e-09 | ideal-gas continuation N_r -> N_ref: max over quantities and cycles of abs(q - q_table) / max(abs(q_table), tol_q) |
| LRG.2 | inventory_rel | report | 0 | M_real0 / M_ideal - 1 at the switch (equal initial mean pressure) |
| LRG.3 | rg_cycles | report | 0 | real-gas cycles from the switch to acceptance (or to the cap) |
| LRG.4 | rg_remaining_max_frac | <= | 0.2 | max over q of R_q / tol_q at acceptance (A2 rule, real-gas run) |
| LRG.5 | rg_mass_drift_max | <= | 1e-09 | max over cycle boundaries of abs(M - M_real0) / M_real0 (solver's rho) |
| LRG.6 | Q_hot_ideal_W | report | 0 | Q_hot of the ideal-gas reference at N_ref, W |
| LRG.7 | Q_hot_real_W | report | 0 | Q_hot of the real-gas run at acceptance, W |
| LRG.8 | dQ_hot_rel | report | 0 | (Q_hot,real - Q_hot,ideal) / Q_hot,ideal, equal initial mean pressure |
| LRG.9 | dQ_hot_unc | report | 0 | its uncertainty from the two remaining distances |
| LRG.10 | Q_cold_ideal_W | report | 0 | Q_cold of the ideal-gas reference at N_ref, W |
| LRG.11 | Q_cold_real_W | report | 0 | Q_cold of the real-gas run at acceptance, W |
| LRG.12 | dQ_cold_rel | report | 0 | (Q_cold,real - Q_cold,ideal) / Q_cold,ideal, equal initial mean pressure |
| LRG.13 | dQ_cold_unc | report | 0 | its uncertainty from the two remaining distances |
| LRG.14 | p_mean_drift_rel | report | 0 | (p_mean,real(N_acc) - p_mean,ideal(N_ref)) / p_mean,ideal(N_ref) |
| LRG.15 | crash_count | == | 0 | crash patterns over all logs (as L5; the trapFpe banner and out-of-table checks excepted, an out-of-table stop counts) |
| LRG.16 | allclean_leftover | == | 0 | files left under the case directory after `Allclean` |
