/*---------------------------------------------------------------------------*\
  regen-ltne-foam: ltneRealGas library. GPL-3.0-or-later.
\*---------------------------------------------------------------------------*/

#include "realGasTable.H"
#include "IFstream.H"
#include "dictionary.H"
#include "HashTable.H"

void Foam::realGasTable::readField
(
    const dictionary& dict,
    const word& name,
    scalarList& f
)
{
    dict.readEntry(name, f);
    if (f.size() != nT_*np_)
    {
        FatalIOErrorInFunction(dict)
            << "field " << name << " in " << file_ << " has " << f.size()
            << " values, expected nT*np = " << nT_*np_ << exit(FatalIOError);
    }
}


Foam::realGasTable::realGasTable(const fileName& file)
:
    file_(file)
{
    IFstream is(file_);
    if (!is.good())
    {
        FatalErrorInFunction
            << "cannot read real-gas table " << file_ << exit(FatalError);
    }
    const dictionary dict(is);
    Tmin_ = dict.get<scalar>("Tmin");
    dT_ = dict.get<scalar>("dT");
    nT_ = dict.get<label>("nT");
    pMin_ = dict.get<scalar>("pMin");
    dp_ = dict.get<scalar>("dp");
    np_ = dict.get<label>("np");
    molWeight_ = dict.get<scalar>("molWeight");
    cp0_ = dict.get<scalar>("cp0");
    readField(dict, "rho", rho_);
    readField(dict, "hDep", hDep_);
    readField(dict, "cp", cp_);
    readField(dict, "cv", cv_);
    readField(dict, "sDep", sDep_);
    readField(dict, "mu", mu_);
    readField(dict, "kappa", kappa_);
    Info<< "realGasTable: " << file_ << ": T " << Tmin_ << " to "
        << Tmin_ + (nT_ - 1)*dT_ << " K, p " << pMin_ << " to "
        << pMin_ + (np_ - 1)*dp_ << " Pa, " << nT_ << " x " << np_ << endl;
}


std::shared_ptr<const Foam::realGasTable> Foam::realGasTable::New
(
    const fileName& file
)
{
    static HashTable<std::shared_ptr<const realGasTable>> cache;
    fileName f(file);
    f.expand();
    if (!cache.found(f))
    {
        cache.set(f, std::make_shared<const realGasTable>(f));
    }
    return cache[f];
}


void Foam::realGasTable::outOfRange(scalar p, scalar T) const
{
    FatalErrorInFunction
        << "state p = " << p << " Pa, T = " << T << " K is outside the table "
        << file_ << " (T " << Tmin_ << " to " << Tmin_ + (nT_ - 1)*dT_
        << " K, p " << pMin_ << " to " << pMin_ + (np_ - 1)*dp_ << " Pa)"
        << exit(FatalError);
}
