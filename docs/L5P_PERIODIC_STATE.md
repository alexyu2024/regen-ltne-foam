# L5P: the periodic steady state of the L5 slice by cycle-map acceleration

The registered criteria, methods and counting rules are in `docs/VERIFICATION.md`, L5P (committed before any run
was read; Amendment A1 before any method run). This page describes how the driver works. The solver physics, the L5
case and every input are unchanged: L5P only runs `ltneFoam` one cycle at a time and decides where the next cycle
starts. The case is `cases/L5P_periodicState`; the results are in `results/L5P`.

## Why

The slow thermal relaxation of the matrix decays by r = 0.9967 per cycle (L5D, time constant about 300 cycles).
Natural marching therefore needs well over a thousand cycles to come within a few hundredths of a kelvin of the
periodic state. Two shortcuts tried earlier did not hold up, and L5P does not use them:
- a single-exponential extrapolation of one scalar;
- a projection on a fixed slow-mode shape taken from a long natural run. Shapes taken early still contain faster
  modes, and the slow mode changes as the temperature field changes, because c_ss(T) is steep below 90 K.

## The map

A cycle-boundary state is a time directory at t = k T, the same phase every cycle. It holds every field ltneFoam
reads on a restart.

Phi(x) is one cycle from that state (`pss/cyclemap.py`). It works on the state vector
x = [Ts on the 120 matrix cells, T on all 172 cells], in K. When a method proposes an x that no cycle produced, the
driver places it into the latest cycle-boundary state:
1. T and Ts are written. In the open gas cells Ts = T, as the solver sets it; the HX solid cells keep their fixed Ts.
2. **Mass and mean pressure.** The pressure field is shifted by a uniform dp so that the gas mass
   sum eps p / (R T) V equals the run's inventory M0. The case is perfectGas, and the driver refuses any other
   equation of state. rho is then deleted, so ltneFoam recomputes it from p and T (rho is READ_IF_PRESENT). The mean
   pressure, the gas mass and the temperature field are therefore consistent after every jump. The jump's mass error
   and the solver's mass drift are both recorded (bar L5P.7 and the M check, <= 1e-9).
3. U, phi, rhoUf and dpdt are carried unchanged. They are the fast, acoustic part of the state, which one cycle
   re-establishes. The first 10 cycles of every verification are not tested for this reason.

The piston start-up term exp(-t/T) is below 1e-17 after cycle 40, so the map does not depend on the absolute time.

**Noise.** The map is deterministic. Its noise comes from writing the fields to ascii at 14 digits on a restart, and
from the fixed number of PIMPLE and linear-solver iterations. Tests N1-N4 (`pss/study.py noise`) measure it from the
cycle-40 state, for the same-phase state and for the cycle-mean fields. The finite-difference perturbation of method
(a), 0.05 K, was fixed before N4 was run.

## Methods (`pss/methods.py`)

All three are black-box: they see only Phi.
- **(a) Newton-Picard / RPM** (Lust, Roose, Spence, Champneys 1998).
  - Each iteration evaluates Phi(x_k) and the p products M V at x_k by finite differences, all from the current state.
    These p + 1 cycles run concurrently.
  - The p x p matrix H = V^T M V gives a Newton step on the slow subspace. The complement gets one Picard step:
    x_(k+1) = Phi(x_k) + V[(I - H)^-1 - I] V^T (Phi(x_k) - x_k).
  - V = orth(M V) is one subspace iteration per Newton step. The basis therefore follows the slow subspace as the
    temperature field changes, instead of keeping a fixed shape.
- **(b) Broyden Rank Reduction** (van de Rotten, Verduyn Lunel, Bliek 2006).
  - Broyden's good method on g(x) = Phi(x) - x, starting from B0 = -I, so the first step is a plain cycle.
  - B = -I + C D^T is kept at rank <= p. Before each update that would exceed p, an SVD of C D^T drops the smallest
    singular direction.
  - One cycle per iteration.
- **(c) Graves-Morris vector extrapolation** (eq. 6 of Subraveti, Karimi, Gazzani, Anantharaman 2024, the method of
  Subraveti, Karimi, Gazzani 2026).
  - Each round runs m plain cycles, then x_(n+1) = Phi(x_n) and x_(n+2) = Phi(x_(n+1)).
  - The extrapolated state is x_(n+1) - [(x_(n+1) - x_n).(x_(n+2) - 2x_(n+1) + x_n) / |x_(n+2) - 2x_(n+1) + x_n|^2]
    (x_(n+2) - x_(n+1)).
  - No Jacobian. Rounds alternate with plain cycles, as published.

**Shared safeguards.**
- Every correction is scaled down to at most 2 K in max norm.
- A method stops iterating when its correction is <= 0.005 K and its residual is <= 1.5e-5 K (A1).
- It then runs 50 natural verification cycles. If its own drift test fails, it continues iterating from their end;
  every cycle is counted.
- `pss/selftest.py` checks all seven configurations on a synthetic map, without the solver.

Glover, Papathanasiou, Pini (2026, arXiv:2606.21523) obtain the Newton Jacobian of one cycle exactly, by automatic
differentiation of a JAX model. That is not available for an OpenFOAM solver. Method (a) is the black-box analogue,
with the Jacobian restricted to the slow subspace. Andersen, Thomsen, Carlsen (2007) apply single and multiple
shooting to a Stirling regenerator model. Method (b) is the closest black-box counterpart that needs one cycle per
iteration.

## Running

    cd cases/L5P_periodicState
    ./runNatural.sh ../../results/L5P/natural 2400          # natural reference (about 9 s per cycle, one core)
    L5P_RUN=run_c40 ./runNatural.sh <scratch> 40 40         # the common start state (cycle 40)
    python3 -m pss.study noise run_c40 work ../../results/L5P
    python3 -m pss.study method np2 run_c40 work ../../results/L5P
    python3 -m pss.study reference ../../results/L5P/natural ../../results/L5P
    python3 -m pss.study score ../../results/L5P np1 np2 np3

**Continuing the natural run** (for example after the container that ran it was reclaimed):
- `results/L5P/natural/restart/state.tgz` is written every 200 cycles, and `results/L5P/natural/restart/cycle`
  names its cycle.
- Run the first command again with the same target. If `run_natural/` is missing, it unpacks the restart point and
  continues from there: the case, the latest cycle-boundary time directory and the per-cycle tables up to it.
- The per-cycle tables (`per_cycle.csv`, `cycles.csv`) are written every 100 cycles. A restart point is
  deterministic: the cycles after it are reproduced bit for bit.
