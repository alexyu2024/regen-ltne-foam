// Porous-medium and solid-matrix fields.
// Without constant/ltneProperties (or with active false) the solver is
// rhoPimpleFoam with an optional porosity field.

Info<< "Reading porous-medium fields\n" << endl;

// Porosity (void fraction); 1 in open gas regions
const volScalarField eps
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
const volScalarField asf
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
auto readSolid = [&](const word& name, const dimensionSet& dims)
{
    return
        solidActive
      ? dimensionedScalar(name, dims, ltneProperties)
      : dimensionedScalar(name, dims, 1);
};
const dimensionedScalar rhoS(readSolid("rhoS", dimDensity));
const dimensionedScalar CpS(readSolid("CpS", dimSpecificHeatCapacity));
const dimensionedScalar kS(readSolid("kS", dimPower/dimLength/dimTemperature));
// Film coefficient between gas and matrix
const dimensionedScalar hsf
(
    solidActive
  ? dimensionedScalar("hsf", dimPower/dimArea/dimTemperature, ltneProperties)
  : dimensionedScalar("hsf", dimPower/dimArea/dimTemperature, Zero)
);

if (solidActive)
{
    Info<< "LTNE solid matrix: rhoS = " << rhoS.value()
        << ", CpS = " << CpS.value() << ", kS = " << kS.value()
        << ", hsf = " << hsf.value() << nl << endl;
}

// Volumetric exchange coefficient [W/m3/K]
const volScalarField hA("hA", hsf*asf);

// 1 in cells that contain solid, 0 in open gas cells
const volScalarField solidMask("solidMask", pos(1 - eps - 1e-6));

// Solid volume fraction, floored so the solid equation stays regular in open
// cells. There hA = 0 and conduction is cut by harmonic interpolation, so the
// solid equation has no effect; Ts is reset to T in open cells for output.
const volScalarField epsS("epsS", max(1 - eps, dimensionedScalar(dimless, 1e-6)));

// Solid heat capacity per unit total volume [J/m3/K]
const volScalarField CS("CS", epsS*rhoS*CpS);

// Solid effective conductivity on faces (harmonic: series conduction)
const surfaceScalarField kSf("kSf", harmonic(mesh).interpolate(epsS*kS));

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
