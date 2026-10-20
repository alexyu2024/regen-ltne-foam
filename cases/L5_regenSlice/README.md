# L5 oscillating regenerator slice (Huang 2020, leader's parameter file)

This is a 1-D axial column holding, from hot to cold: the hot chamber, the hot HX, the 500# and 635# stainless
screen matrix, the cold HX and the cold chamber. Helium at 0.75 MPa is driven by two pistons at 23 Hz. Every input
comes from `params_L5.yaml`, used verbatim; `mkCase.py` writes all dictionaries and initial fields from it. The bars
(B1-B6 quoted unchanged, plus the self-checks) are in `docs/VERIFICATION.md`, L5, and were committed before any run.

## Running

| command | what it does |
|---|---|
| `./Allrun [cycles]` | builds the solver, writes the case, meshes, runs `cycles` cycles (default 10) |
| `./Allrun.continue <cycles>` | continues from the latest time for `cycles` more cycles |
| `./runLong.sh <outdir> [minutes]` | the full L5 job. It runs 10-cycle chunks until at least 40 cycles are done and B6 holds, then the sensitivity run, then writes the deliverables to `<outdir>`. Exit code 3 means the time budget is used and the state is kept. |
| `./Allclean` | removes everything the scripts generate |

On GitHub, `.github/workflows/run-case.yml` (input `level = L5`) runs `runLong.sh`. It uploads `L5-results`
(small CSVs) and `L5-state` (the latest time directory plus the per-cycle table). A job that hits the 6 h limit
exits 3; you then dispatch again with `restart_run_id` set to that run's id.

## How ltneFoam realises the file's physical solid properties

The file defines, per unit total volume:
- axial conduction k_eff(T) = ksFrac (1 - eps) k_ss(T), with ksFrac = 0.10;
- heat capacity (1 - eps) rho_ss c_ss(T).

ltneFoam's solid equation is

    d/dt[ epsS rhoS h_ss(Ts) ] - div( kSf grad Ts ) = hA (T - Ts),   epsS = 1 - eps,

with kSf the harmonic face interpolation of epsS * kS.

The mapping is as follows:
- **Conduction**: the per-zone keyword `ksFrac 0.10` sets kS = ksFrac k_ss(Ts) cell by cell, with k_ss taken from
  the DeltaEC 13.5 fit. The solver multiplies kS by epsS, so the realised conduction is
  (1 - eps) ksFrac k_ss(T) = k_eff(T) exactly. It is not fed (1 - eps) ksFrac k_ss, which would count (1 - eps)
  twice.
- **Heat capacity**: with `solidModel stainlessDeltaEC`, the storage term is written in enthalpy form,
  epsS rhoS [h_ss(Ts^n+1) - h_ss(Ts^n)] / dt, with h_ss(T) = integral of c_ss dT. This keeps solid energy
  conserved exactly while c_ss changes steeply below 90 K. In ltneUpdate.H the linearisation coefficient is
  C_S = epsS rhoS c_ss(Ts). So the realised heat capacity is (1 - eps) rho_ss c_ss(T), with rho_ss held at
  7990 kg/m3, which the file allows.
  - The h_ss table runs from 4 to 400 K in 0.005 K steps, integrated from the DeltaEC c_ss fit
    (`createLtneZones.H`).
  - The fit is evaluated at max(Ts, 6 K), 6 K being the fit's lower validity limit. Ts stays above 21 K in this case.
- **HX solid**: in the HX zones, Ts is fixed at 80.033 K and 21.997 K (`fixedTs`), so the HX heat capacity drops
  out. The copper conductivity 398 - 0.0567 (T - 300) (DeltaEC 13.3) is set per zone as `kSolid`, multiplied by
  epsS = 0.30 like the matrix. It only matters at the HX/matrix interfaces, where it carries the matrix's axial
  solid conduction into the fixed-temperature solid.
- **Film coefficient**: this is a live field, recomputed every outer iteration from the cell-centre U, rho, mu(T)
  and k(T).
  - Screens (Gedeon-Wood): Nu = (1 + 0.99 Pe^0.66) beta^1.79, with Pe = Re Pr and Re = rho |u_sup| d_re / mu;
    h_sf = Nu k / d_h.
  - HX (Wakao): Nu = max(2, 2 + 1.1 Re^0.6 Pr^(1/3)), with Re on d_h.
  - hA = h_sf a_sf.
- **Drag**: the file's 1/alpha and C2 (the latter fixed at the reference state) enter as Darcy-Forchheimer
  `explicitPorositySource` terms per zone, on the superficial velocity.

## Interpretations (confirmed by the leader before the runs)

- **Start-up.** Each piston follows x(t) = |x| [cos(omega t + Ph) - cos(Ph) exp(-t/T)], with T = 1/23 s. The mesh
  therefore starts at the mean position and the start is velocity-continuous. This is implemented as the
  `rampTime` option of `pistonLinear` (the Function1 value minus its t = 0 value times exp(-t/rampTime)). The
  Fluent twin uses the same formula.
- **Sensitivity bar.** The < 1 % bar is applied relative to amplitudes and as 0.5 deg absolute to phases.
## Interpretation not yet confirmed (flagged in the PR)

- **Cold piston direction.** The file says x = displacement toward the matrix, with
  U_p = A dxi/dt, and that "the cold piston ABSORBS the machine's +z flow: sign -". This case takes the cold
  piston's positive displacement as +z, the machine's flow direction, i.e. away from the matrix. With that
  reading:
  - the realised cold-piston volume flow (positive = gas leaving the column through the cold piston) matches
    U_amp and U_phase in the file;
  - the cold-face |mdot| and phase match the DeltaEC context: -28.8 deg against -28.6 deg in a 10-cycle local test.

  The other reading (+x toward the matrix, i.e. -z) shifts the cold drive by 180 deg. It is checked in
  `piston_check.csv`, which compares U_p = -sum(meshPhi) on each piston against U_amp and U_phase, the cold sign
  taken per the reading above.

## Diagnostics and the energy balance

`monitors.dat` (written every step by ltneFoam) records the following on the face zones `hotFace` (z = 0), `joint`
(0.026) and `coldFace` (0.052):
- p (area-weighted mean), T, mdot;
- the total energy flow H = sum over faces of [phi (h + K) - eps alpha_eff snGrad(h) |S| - kSf snGrad(Ts) |S|].
  h is sensible enthalpy measured from 0 K, i.e. c_p T for this ideal gas. This matters because the cycle-mean
  mass flow is only zero to within the drift of the cycle, and h then fixes the reference.

On each piston it records the volume flow and the work rate W = -sum(meshPhi p), the work done on the gas. In each
fixed-Ts HX it records the heat into the gas, Q_gas = sum of hA (Ts - T) V, and the heat conducted from the fixed
HX solid into the neighbouring matrix solid, Q_solid.

**Energy closure** (`docs/VERIFICATION.md`, L5 and Amendment A1):
- **L5.7 (B5 as registered)** = |<W_hot> + <W_cold> + <Q_gas,hot> + <Q_gas,cold>| over the last cycle. It FAILs:
  0.397 W on cycle 40, against a bar of 0.15 W.
- **L5.7a (supplementary, added after the runs)** = the same four terms plus <Q_solid,hot> + <Q_solid,cold>. It
  gives 0.020 W.
- Why they differ: the HX solid's heat reaches the column two ways, through the gas and through the matrix solid.
  The registered formula leaves out the second path.
- Neither check can detect heat losses that the model does not contain, such as the outer wall or the end faces.

## Characteristic numbers (from the inputs)

Evaluated at the two matrix faces with the drive-table superficial-velocity amplitudes (0.771 and 0.258 m/s):

| quantity | hot face (500#, 80 K) | cold face (635#, 22 K) |
|---|---|---|
| gas density | 4.51 kg/m3 | 16.4 kg/m3 |
| Re on d_re (peak) | 26.6 | 54.7 |
| Pr | 0.69 | 0.71 |
| Nu (Gedeon-Wood), h_sf | 3.39, 5280 W/m2/K | 4.92, 4630 W/m2/K |
| hA | 3.3e8 W/m3/K | 3.6e8 W/m3/K |
| NTU per unit length hA / (G c_p) (peak G) | 1.8e4 1/m (7.8 per cell) | 1.65e4 1/m (7.2 per cell) |
| solid / gas heat capacity (1-eps) rho_ss c_ss / (eps rho c_p) | 40 | 1.06 |
| cycles per solid thermal time, hA / (C_s f) | 24 | 287 |
| tidal gas displacement amplitude, u / (omega eps) | 8.5 mm (33 % of the 500# section) | 2.9 mm |
| effective solid conduction k_eff vs gas k | 0.30 vs 0.063 W/m/K | 0.095 vs 0.029 W/m/K |
| convective CFL (u/eps) dt/dx | 0.051 | 0.018 |
| acoustic CFL c dt/dx | 22 (c = 526 m/s) | 11.5 (c = 276 m/s) |
| wavelength / column length (0.078 m) | 290 | 150 |

What these numbers imply:
- The column is acoustically compact, so the pressure is nearly uniform apart from the matrix drop, and the
  implicit pressure equation handles an acoustic CFL of 10-20. L1 showed amplitudes unaffected at an acoustic CFL
  of 408.
- The large NTU per cell makes the gas-solid coupling stiff. It is treated semi-implicitly
  (`Sp(hA, Ts)` / `Sp(hA, T)`).
- Near the cold face the solid and gas heat capacities are comparable (ratio 1.06). The cold end of the matrix is
  therefore where the temperature profile needs the most cycles to settle.

Mesh: 24 cells in the hot chamber, 10 in each HX, 60 + 60 in the matrix (0.4333 mm, cell faces on the file's 121
nodes), and 8 in the cold chamber. dt = 1.8115942e-5 s, 2400 steps per cycle. The sensitivity run uses dt/2 and
120 + 120 matrix cells.

## Deliverables (in `results/L5/`)

- `per_cycle.csv`: per cycle, the cycle-mean T at the joint, <H> at the three stations, the dp amplitude, the face
  phasors, the piston work, the HX heat terms, the B5 closure, and the piston phasors.
- `final_cycle_faces.csv`: every step of the last cycle, giving t, p, u_superficial, mdot and Tg at both matrix
  faces.
- `profiles.csv`: cycle-mean Tg(z) and Ts(z) of the final cycle, interpolated linearly from cell centres to the
  121 nodes.
- `piston_check.csv`: the realised piston volume-flow phasor against the file's spec.
- `per_cycle_sensitivity.csv`: per cycle of the sensitivity run.
- `results.csv`, `STATUS.md` and the trimmed logs.

The crash scan (L5.2) skips OpenFOAM's start-up banner `trapFpe: Floating point exception trapping enabled`, which
every OpenFOAM log prints and which reports a setting, not a crash. `results.csv` gives the number of skipped banner
lines.
