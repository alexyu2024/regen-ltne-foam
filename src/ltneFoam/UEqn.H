// Solve the Momentum equation (superficial velocity; porosity does not enter
// the inertia terms). The Darcy-Forchheimer drag Dc U is not part of UEqn:
// it is applied on faces in pEqn.H and only added here for the predictor.

tmp<fvVectorMatrix> tUEqn
(
    fvm::ddt(rho, U) + fvm::div(phi, U)
  + turbulence->divDevRhoReff(U)
);
fvVectorMatrix& UEqn = tUEqn.ref();

UEqn.relax();

fvOptions.constrain(UEqn);

// Cell drag coefficient [kg/m3/s]
const volScalarField Dc
(
    "Dc",
    porousD*thermo.mu() + 0.5*porousF*rho*mag(U)
);

if (pimple.momentumPredictor())
{
    solve(UEqn + fvm::Sp(Dc, U) == -fvc::grad(p));

    fvOptions.correct(U);
    K = 0.5*magSqr(U);
}
