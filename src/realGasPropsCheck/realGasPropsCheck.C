/*---------------------------------------------------------------------------*\
  regen-ltne-foam. GPL-3.0-or-later.

Application
    realGasPropsCheck

Description
    Evaluates the case's thermo (constant/thermophysicalProperties) at the
    (T, p) points listed in system/propsCheckDict and writes, per point,
    rho = rhoEoS(p, T), Cp(p, T), the enthalpy he(p, T) and the temperature
    THE(he, p, T0) recovered from it (Newton start T0 = 1.05 T). Also writes
    the cell-state mu and kappa. Output: propsCheck.dat in the case directory.

\*---------------------------------------------------------------------------*/

#include "fvCFD.H"
#include "rhoThermo.H"
#include "OFstream.H"

int main(int argc, char *argv[])
{
    argList::noParallel();
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    autoPtr<rhoThermo> pThermo(rhoThermo::New(mesh));
    rhoThermo& thermo = pThermo();

    const IOdictionary dict
    (
        IOobject
        (
            "propsCheckDict",
            runTime.system(),
            mesh,
            IOobject::MUST_READ,
            IOobject::NO_WRITE
        )
    );
    const List<Pair<scalar>> points(dict.get<List<Pair<scalar>>>("points"));

    const label n = points.size();
    scalarField T(n), p(n);
    forAll(points, i)
    {
        T[i] = points[i].first();
        p[i] = points[i].second();
    }
    const labelList cells(n, Zero);

    const scalarField rho(thermo.rhoEoS(p, T, cells));
    const scalarField Cp(thermo.Cp(p, T, cells));
    const scalarField h(thermo.he(p, T, cells));
    const scalarField Trec(thermo.THE(h, p, 1.05*T, cells));

    OFstream os(runTime.path()/"propsCheck.dat");
    os.precision(12);
    os  << "# thermo: " << thermo.thermoName() << nl
        << "# T p rho Cp he T_recovered" << nl;
    forAll(T, i)
    {
        os  << T[i] << ' ' << p[i] << ' ' << rho[i] << ' ' << Cp[i] << ' '
            << h[i] << ' ' << Trec[i] << nl;
    }
    const volScalarField mu(thermo.mu());
    const volScalarField kappa(thermo.kappa());
    os  << "# cell state: T p mu kappa" << nl
        << "cell " << thermo.T()[0] << ' ' << thermo.p()[0] << ' '
        << mu[0] << ' ' << kappa[0] << nl;

    Info<< "realGasPropsCheck: " << thermo.thermoName() << nl
        << "wrote " << os.name() << nl << "End" << endl;
    return 0;
}
