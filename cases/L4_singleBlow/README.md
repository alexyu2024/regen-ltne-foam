# L4 single-blow transient (Schumann 1929)

A porous bed of stainless steel initially at 300 K fills a 1-D channel. From t = 0, helium enters at 310 K with a fixed
superficial velocity of 0.1 m/s. The outlet breakthrough curve and the stored solid energy are compared with the
Schumann (Anzelius) solution. Bars, formulas and source: `docs/VERIFICATION.md`, L4.

## Characteristic numbers (from the inputs, before the first run)

| quantity | value |
|---|---|
| G = rho(310 K) u | 0.3106 kg/m2/s |
| NTU of the bed, xi_L = hA L / (G c_p) | 9.92 |
| xi per cell | 0.050 |
| hA / C_s | 0.1350 1/s (eta_end = 20.3 at 150 s) |
| thermal wave speed G c_p / C_s | 1.36e-3 m/s |
| gas / solid heat capacity, eps rho c_p / C_s | 0.0095 |
| gas transit time eps rho L / G | 0.70 s |
| axial Peclet number G c_p L / (eps k_g), k_g = 0.155 W/m/K | 1487 (gas conduction is not switched off; expected effect of order xi_L / Pe = 0.7 %) |
| convective CFL (u / eps) dt / dx | 1.43 |
| acoustic CFL c dt / dx | 1.0e4 (L1 run c showed no amplitude failure at 408; here the pressure is nearly uniform) |
| steps | 30000 |
| pore Reynolds number | not used: the drag is off, and the film coefficient is an input, not a correlation |
