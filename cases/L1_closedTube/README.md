# L1 closed tube with a piston

1-D closed helium tube, L = 0.1 m, piston at x = 0, closed end at x = L, no porous medium. Four runs (`run_a` to
`run_d`, created by `Allrun`): a, b, c differ only in the time step (acoustic CFL about 20, 81 and 408); d uses the
L5 ratio of stroke amplitude to piston-space length (2.44 mm / 5 mm) with 0.1 mm cells in the piston space. Setup,
definitions and bars: `docs/VERIFICATION.md`, L1. Metrics: `results.py`.

## Characteristic numbers (from the inputs, before the first run)

| quantity | value |
|---|---|
| sound speed c = sqrt(gamma R T), gamma = 1.6667, R = 2077.3 J/kg/K, T = 300 K | 1019 m/s |
| wavelength c / f at 50 Hz | 20.4 m |
| k L = 2 pi f L / c; lumped model valid for k L << 1 | 0.031 |
| first tube resonance c / (2 L) | 5.1 kHz (100 x the drive frequency) |
| acoustic CFL c dt / dx, runs a / b / c (dx = 1 mm) | 20.4 / 81.5 / 408 |
| acoustic CFL, run d (dx = 0.1 mm in the piston space; 1 mm elsewhere) | 20.4 (2.0 in the 1 mm cells) |
| steps per cycle, runs a / b / c / d | 1000 / 250 / 50 / 10000 |
| x_a / L, runs a-c and d | 1e-3 and 0.0244 |
| expected p1 = gamma p0 x_a / L, runs a-c and d | 3.33 kPa and 81.3 kPa |
| piston velocity amplitude omega x_a, Mach number, runs a-c and d | 0.031 m/s, 3e-5; 0.77 m/s, 7.5e-4 |
| piston-space cell height range expected from the motion, run d: 0.1 mm (5 - x_p) / 5, x_p in [-2.44, 2.44] mm | 0.0512 to 0.1488 mm |

Womersley number, Reynolds number and thermal penetration depth relative to a pore or wall do not apply: the 1-D
model has no side walls (no wall friction or wall heat transfer), and the end walls are adiabatic. The drive starts
with the piston at its mean position moving at full velocity, which excites the tube's acoustic modes. The last of the
three cycles is analysed; the first two let that start-up transient decay.
