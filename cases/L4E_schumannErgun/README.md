# L4E single blow with Ergun drag (Schumann 1929, Ergun 1952)

A packed bed of 0.5 mm spheres (eps = 0.4) initially at 300 K fills a 1-D channel. From t = 0, helium enters at
310 K with a fixed superficial velocity of 0.1 m/s. The gas and solid temperatures at mid-bed and at the bed end are
compared with the Schumann solution, and the bed pressure drop with the Ergun equation, whose coefficients set the
Darcy-Forchheimer drag (`constant/fvOptions`). Properties and the volumetric heat transfer coefficient
hA = 1.8e5 W/m3/K are constant. Bars, formulas and sources: `docs/VERIFICATION.md`, L4E.

| command | what it does |
|---|---|
| `./Allrun` | builds the solver, meshes (200 cells) and runs 150 s (30000 steps) |
| `python3 results.py <outdir>` | writes the metrics; `tools/run_level.sh L4E <outdir>` does both and checks the bars |
| `python3 plot.py <outdir> <png>` | the breakthrough figure (needs matplotlib; not used by CI) |
| `./Allclean` | removes everything the scripts generate |
