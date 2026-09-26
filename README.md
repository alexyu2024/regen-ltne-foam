# regen-ltne-foam

OpenFOAM implementation of a **local thermal non-equilibrium (LTNE) porous-media solver**
for **oscillating-flow cryocooler regenerators**, with validation against
**public benchmark cases**.

## Scope

- Solve coupled fluid/solid energy equations under LTNE assumptions in porous media.
- Support oscillating-flow operating conditions representative of regenerative cryocoolers.
- Provide reproducible benchmark cases and comparison guidance for verification.

## Planned repository layout

- `applications/solvers/`: LTNE porous solver source code.
- `tutorials/`: benchmark and verification cases.
- `docs/`: model assumptions, equations, and verification notes.

## Verification target

Each benchmark case should include:

1. Case setup and boundary conditions.
2. Run instructions.
3. Reference data source (publicly accessible).
4. Quantitative comparison metrics (for example, temperature profile and pressure drop errors).
