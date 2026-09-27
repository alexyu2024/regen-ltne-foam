# L4 first run: crash at start (solver bug), kept as a record

The run at 85b4e55 stopped before the first time step with a floating-point exception (`log.ltneFoam`, stack trace
at the end): `Foam::divide` inside the construction of `kSf`. L4 is the first case with `kS 0` (no solid
conduction, as Schumann assumes). The harmonic interpolation of (1 - eps) kS divides by zero for kS = 0.

Fix (next commit): kSf = 0 when kS = 0, harmonic interpolation otherwise. The case and the bars are unchanged.

Bar-definition gap noticed here: the crash message "Floating point exception" is not matched by the L0-L4 pattern
`FOAM FATAL|nan|inf`, so L4.2 read 0. The crash is caught by L4.1 (final_time "not read" = FAIL). The pattern is
left unchanged because bars do not move; the leader may add `Floating point exception` to future levels' bars.
