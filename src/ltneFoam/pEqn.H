// Pressure equation of rhoPimpleFoam with porosity-weighted storage,
//   eps d(rho)/dt + div(phi) = 0,
// and the Darcy-Forchheimer drag balanced on faces (docs/L2_FIX_DESIGN.md):
//   u_f = kf (HbyA_f - rAU_f grad_f p),  kf = 1/(1 + rAU_f Df)

if (!pimple.SIMPLErho())
{
    rho = thermo.rho();
}

// Thermodynamic density needs to be updated by psi*d(p) after the
// pressure solution
const volScalarField psip0(psi*p);

volScalarField rAU(1.0/UEqn.A());
surfaceScalarField rhorAUf("rhorAUf", fvc::interpolate(rho*rAU));
volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));

// Face drag coefficient: rho|u| on a face is the face mass flux
const surfaceScalarField kf
(
    "kf",
    1.0
   /(
        1.0
      + fvc::interpolate(rAU)
       *(
            fvc::interpolate(porousD*thermo.mu())
          + 0.5*fvc::interpolate(porousF)*mag(phi)/mesh.magSf()
        )
    )
);

if (pimple.nCorrPISO() <= 1)
{
    tUEqn.clear();
}

surfaceScalarField phiHbyA
(
    "phiHbyA",
    kf
   *(
        fvc::interpolate(rho)*fvc::flux(HbyA)
      + rhorAUf*fvc::ddtCorr(rho, U, phi, rhoUf)
    )
);
rhorAUf *= kf;

fvc::makeRelative(phiHbyA, rho, U);

// Update the pressure BCs to ensure flux consistency
constrainPressure(p, rho, U, phiHbyA, rhorAUf);

if (pimple.transonic())
{
    FatalErrorInFunction
        << "transonic is not supported by ltneFoam" << exit(FatalError);
}

fvScalarMatrix pDDtEqn
(
    eps()*(fvc::ddt(rho) + psi*correction(fvm::ddt(p)))
  + fvc::div(phiHbyA)
 ==
    fvOptions(psi, p, rho.name())
);

while (pimple.correctNonOrthogonal())
{
    fvScalarMatrix pEqn(pDDtEqn - fvm::laplacian(rhorAUf, p));

    pEqn.solve(p.select(pimple.finalInnerIter()));

    if (pimple.finalNonOrthogonalIter())
    {
        phi = phiHbyA + pEqn.flux();
    }
}

// Explicitly relax pressure for momentum corrector
p.relax();


// Cell velocity reconstructed from the (absolute) face fluxes, so that the
// interpolated cell velocities in the next Rhie-Chow flux match the face
// velocities (docs/L2_FIX_DESIGN.md, revision 2)
U = fvc::reconstruct(fvc::absolute(phi, rho, U)/fvc::interpolate(rho));
U.correctBoundaryConditions();
fvOptions.correct(U);
K = 0.5*magSqr(U);

if (pressureControl.limit(p))
{
    p.correctBoundaryConditions();
}

thermo.correctRho(psi*p - psip0, rhoMin, rhoMax) ;

#include "rhoEqn.H"
#include "compressibleContinuityErrs.H"

rho = thermo.rho();

// Correct rhoUf if the mesh is moving
fvc::correctRhoUf(rhoUf, rho, U, phi);

if (thermo.dpdt())
{
    dpdt = fvc::ddt(p);

    if (mesh.moving())
    {
        dpdt -= fvc::div(fvc::meshPhi(rho, U), p);
    }
}
