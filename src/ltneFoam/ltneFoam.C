/*---------------------------------------------------------------------------*\
    ltneFoam: rhoPimpleFoam (OpenFOAM v2512, www.openfoam.com) extended with a
    porous medium in local thermal non-equilibrium (LTNE).

    Copyright (C) 2011-2017 OpenFOAM Foundation
    Copyright (C) 2019 OpenCFD Ltd.
    Modifications for LTNE: regen-ltne-foam contributors.

    This file is derived from OpenFOAM and is distributed under the GNU General
    Public License v3 or later (see <http://www.gnu.org/licenses/>).

Application
    ltneFoam

Description
    Transient compressible solver for gas flow through a porous matrix with a
    separate solid energy equation, with optional mesh motion (moving piston).

    Superficial-velocity formulation, as in Tew et al. (2006) / Fluent:
      eps d(rho)/dt + div(rho U) = 0
      d(rho U)/dt + div(rho U U) = -grad(p) + div(tau) - (mu/K + C2 rho|U|/2) U
      eps [d(rho h)/dt - dp/dt] + div(rho U h) = div(eps k grad T)
                                               + hA (Ts - T)
      (1-eps) rhoS cS dTs/dt = div((1-eps) kS grad Ts) + hA (T - Ts)

    eps (field "porosity") is 1 in open gas regions. hA = hsf*asf where
    asf (field "asf", 1/m) is the interfacial area per unit total volume.
    The Darcy-Forchheimer coefficients (d = 1/K, f = C2) are read from the
    explicitPorositySource entries of constant/fvOptions and the drag is
    balanced on faces in the pressure equation (docs/L2_FIX_DESIGN.md).
    Porosity does not appear in the momentum inertia terms (Fluent default).

\*---------------------------------------------------------------------------*/

#include "fvCFD.H"
#include "dynamicFvMesh.H"
#include "fluidThermo.H"
#include "turbulentFluidThermoModel.H"
#include "pimpleControl.H"
#include "pressureControl.H"
#include "CorrectPhi.H"
#include "fvOptions.H"
#include "harmonic.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    argList::addNote
    (
        "Transient compressible solver for porous media in local thermal"
        " non-equilibrium, with optional mesh motion."
    );

    #include "postProcess.H"

    #include "addCheckCaseOptions.H"
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createDynamicFvMesh.H"
    #include "createDyMControls.H"
    #include "initContinuityErrs.H"
    #include "createFields.H"
    #include "createFieldRefs.H"
    #include "createLtneFields.H"
    #include "createPorousDrag.H"
    #include "createRhoUfIfPresent.H"

    turbulence->validate();

    #include "compressibleCourantNo.H"
    #include "setInitialDeltaT.H"

    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    Info<< "\nStarting time loop\n" << endl;

    #include "ltneDiagnostics.H"

    while (runTime.run())
    {
        #include "readDyMControls.H"

        // Store divrhoU from the previous mesh so that it can be mapped
        // and used in correctPhi to ensure the corrected phi has the
        // same divergence
        autoPtr<volScalarField> divrhoU;
        if (correctPhi)
        {
            divrhoU.reset
            (
                new volScalarField
                (
                    "divrhoU",
                    fvc::div(fvc::absolute(phi, rho, U))
                )
            );
        }

        #include "compressibleCourantNo.H"
        #include "setDeltaT.H"

        ++runTime;

        Info<< "Time = " << runTime.timeName() << nl << endl;

        // --- Pressure-velocity PIMPLE corrector loop
        while (pimple.loop())
        {
            if (pimple.firstIter() || moveMeshOuterCorrectors)
            {
                // Store momentum to set rhoUf for introduced faces.
                autoPtr<volVectorField> rhoU;
                if (rhoUf.valid())
                {
                    rhoU.reset(new volVectorField("rhoU", rho*U));
                }

                // Do any mesh changes
                mesh.controlledUpdate();

                if (mesh.changing())
                {
                    if (correctPhi)
                    {
                        // Calculate absolute flux
                        // from the mapped surface velocity
                        phi = mesh.Sf() & rhoUf();

                        #include "correctPhi.H"

                        // Make the fluxes relative to the mesh-motion
                        fvc::makeRelative(phi, rho, U);
                    }

                    if (checkMeshCourantNo)
                    {
                        #include "meshCourantNo.H"
                    }
                }
            }

            if (pimple.firstIter() && !pimple.SIMPLErho())
            {
                #include "rhoEqn.H"
            }

            #include "UEqn.H"
            #include "EEqn.H"
            #include "TsEqn.H"

            // --- Pressure corrector loop
            while (pimple.correct())
            {
                #include "pEqn.H"
            }

            if (pimple.turbCorr())
            {
                turbulence->correct();
            }
        }

        rho = thermo.rho();

        #include "ltneDiagnostics.H"

        runTime.write();

        runTime.printExecutionTime(Info);
    }

    Info<< "End\n" << endl;

    return 0;
}


// ************************************************************************* //
