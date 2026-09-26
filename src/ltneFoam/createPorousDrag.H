// Darcy-Forchheimer coefficients, applied on faces in pEqn.H (see
// docs/L2_FIX_DESIGN.md). They are read from the explicitPorositySource /
// DarcyForchheimer entries of constant/fvOptions, which are therefore not
// added to the momentum matrix by fvOptions.

volScalarField porousD
(
    IOobject("porousD", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar(dimless/dimArea, Zero)
);
volScalarField porousF
(
    IOobject("porousF", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar(dimless/dimLength, Zero)
);

const fv::optionList& fvOptionList = fvOptions;
forAll(fvOptionList, optioni)
{
    const fv::option& source = fvOptionList[optioni];

    if (source.applyToField(U.name()) < 0)
    {
        continue;
    }
    if (source.type() != "explicitPorositySource")
    {
        FatalErrorInFunction
            << "fvOption " << source.name() << " of type " << source.type()
            << " acts on " << U.name() << "; ltneFoam only supports"
            << " explicitPorositySource (DarcyForchheimer) there"
            << exit(FatalError);
    }

    const dictionary& coeffs =
        static_cast<const dictionary&>(fvOptions).subDict(source.name()).optionalSubDict
        (
            "explicitPorositySourceCoeffs"
        );
    const vector d(coeffs.get<vector>("d"));
    const vector f(coeffs.get<vector>("f"));

    if
    (
        coeffs.get<word>("type") != "DarcyForchheimer"
     || cmptMin(d) < 0 || cmptMin(f) < 0
     || cmptMax(d) - cmptMin(d) > SMALL*cmptMax(d)
     || cmptMax(f) - cmptMin(f) > SMALL*cmptMax(f)
    )
    {
        FatalErrorInFunction
            << "fvOption " << source.name() << ": ltneFoam supports only an"
            << " isotropic DarcyForchheimer model with d, f >= 0"
            << exit(FatalError);
    }

    const word zoneName(coeffs.get<word>("cellZone"));
    const label zonei = mesh.cellZones().findZoneID(zoneName);
    if (zonei < 0)
    {
        FatalErrorInFunction
            << "cellZone " << zoneName << " not found" << exit(FatalError);
    }
    for (const label celli : mesh.cellZones()[zonei])
    {
        porousD[celli] = d.x();
        porousF[celli] = f.x();
    }

    Info<< "Porous drag (on faces) in zone " << zoneName << ": d = " << d.x()
        << ", f = " << f.x() << nl << endl;
}
porousD.correctBoundaryConditions();
porousF.correctBoundaryConditions();
