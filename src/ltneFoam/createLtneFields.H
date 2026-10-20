// Porous-medium and solid-matrix fields.
// Without constant/ltneProperties (or with active false) the solver is
// rhoPimpleFoam with an optional porosity field.

Info<< "Reading porous-medium fields\n" << endl;

// Porosity (void fraction); 1 in open gas regions
volScalarField eps
(
    IOobject
    (
        "porosity",
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT,
        IOobject::NO_WRITE
    ),
    mesh,
    dimensionedScalar(dimless, 1)
);

// Interfacial area per unit total volume [1/m]; 0 outside the matrix
volScalarField asf
(
    IOobject
    (
        "asf",
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT,
        IOobject::NO_WRITE
    ),
    mesh,
    dimensionedScalar(dimless/dimLength, Zero)
);

IOdictionary ltneProperties
(
    IOobject
    (
        "ltneProperties",
        runTime.constant(),
        mesh,
        IOobject::READ_IF_PRESENT,
        IOobject::NO_WRITE
    )
);

const bool solidActive = ltneProperties.getOrDefault<bool>("active", false);

// Solid properties (intrinsic; the matrix volume fraction is 1 - eps).
// Required when active; placeholders otherwise.
const word solidModel
(
    ltneProperties.getOrDefault<word>("solidModel", "constant")
);
const bool variableSolid = (solidModel == "stainlessDeltaEC");
if (solidModel != "constant" && !variableSolid)
{
    FatalErrorInFunction
        << "solidModel " << solidModel
        << " unknown; use constant or stainlessDeltaEC" << exit(FatalError);
}
const bool zonesActive = solidActive && ltneProperties.found("zones");

auto readSolid = [&](const word& name, const dimensionSet& dims)
{
    // CpS and kS are not needed for a temperature-dependent solid model
    const bool optional = variableSolid && name != "rhoS";
    return
        solidActive && !optional
      ? dimensionedScalar(name, dims, ltneProperties)
      : dimensionedScalar(name, dims, 1);
};
const dimensionedScalar rhoS(readSolid("rhoS", dimDensity));
const dimensionedScalar CpS(readSolid("CpS", dimSpecificHeatCapacity));
const dimensionedScalar kS(readSolid("kS", dimPower/dimLength/dimTemperature));
// Film coefficient between gas and matrix
const dimensionedScalar hsf
(
    solidActive && !zonesActive
  ? dimensionedScalar("hsf", dimPower/dimArea/dimTemperature, ltneProperties)
  : dimensionedScalar("hsf", dimPower/dimArea/dimTemperature, Zero)
);

if (solidActive)
{
    Info<< "LTNE solid matrix: rhoS = " << rhoS.value()
        << ", CpS = " << CpS.value() << ", kS = " << kS.value()
        << ", hsf = " << hsf.value() << nl << endl;
}

#include "createLtneZones.H"

// Volumetric exchange coefficient [W/m3/K]
volScalarField hA("hA", hsf*asf);

// 1 in cells that contain solid, 0 in open gas cells
volScalarField solidMask("solidMask", pos(1 - eps - 1e-6));

// Solid volume fraction, floored so the solid equation stays regular in open
// cells. There hA = 0 and conduction is cut by harmonic interpolation, so the
// solid equation has no effect; Ts is reset to T in open cells for output.
volScalarField epsS("epsS", max(1 - eps, dimensionedScalar(dimless, 1e-6)));

// Solid heat capacity per unit total volume [J/m3/K]
volScalarField CS("CS", epsS*rhoS*CpS);

// Solid effective conductivity on faces (harmonic: series conduction; the
// harmonic mean is undefined for kS = 0, which then means no conduction)
surfaceScalarField kSf
(
    IOobject("kSf", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar(kS.dimensions(), Zero)
);
if (kS.value() > 0)
{
    kSf = harmonic(mesh).interpolate(epsS*kS);
}

Info<< "Reading field Ts\n" << endl;
autoPtr<volScalarField> TsPtr;
if (solidActive)
{
    TsPtr.reset
    (
        new volScalarField
        (
            IOobject
            (
                "Ts",
                runTime.timeName(),
                mesh,
                IOobject::MUST_READ,
                IOobject::AUTO_WRITE
            ),
            mesh
        )
    );
}
else
{
    // Unused placeholder so that diagnostics need no special case
    TsPtr.reset
    (
        new volScalarField
        (
            IOobject
            (
                "Ts",
                runTime.timeName(),
                mesh,
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            thermo.T()
        )
    );
}
volScalarField& Ts = TsPtr();
Ts.oldTime();   // store the old-time level (enthalpy form of the solid equation)

#include "ltneUpdate.H"
#include "createLtneMonitors.H"

// Diagnostics file (see ltneDiagnostics.H)
scalar boundaryWork = 0;
autoPtr<OFstream> diagFile;
if (Pstream::master())
{
    const fileName dir
    (
        runTime.globalPath()/"postProcessing"/"ltneDiagnostics"
       /runTime.timeName()
    );
    mkDir(dir);
    diagFile.reset(new OFstream(dir/"ltne.dat"));
    diagFile().precision(15);
    diagFile()
        << "# time gasMass gasInternalEnergy gasKineticEnergy solidEnergy"
        << " gasVolume pAvg boundaryWork";
    for (const cellZone& zone : mesh.cellZones())
    {
        diagFile() << ' ' << zone.name() << "_Vmin " << zone.name() << "_Vmax";
    }
    diagFile() << endl;
}
