/*---------------------------------------------------------------------------*\
  regen-ltne-foam: ltneRealGas library. GPL-3.0-or-later.
\*---------------------------------------------------------------------------*/

template<class Specie>
inline Foam::tabulatedRealGas<Specie>::tabulatedRealGas
(
    const word& name,
    const tabulatedRealGas<Specie>& eos
)
:
    Specie(name, eos),
    file_(eos.file_),
    table_(eos.table_)
{}


template<class Specie>
inline Foam::autoPtr<Foam::tabulatedRealGas<Specie>>
Foam::tabulatedRealGas<Specie>::clone() const
{
    return autoPtr<tabulatedRealGas<Specie>>::New(*this);
}


template<class Specie>
inline Foam::autoPtr<Foam::tabulatedRealGas<Specie>>
Foam::tabulatedRealGas<Specie>::New(const dictionary& dict)
{
    return autoPtr<tabulatedRealGas<Specie>>::New(dict);
}


template<class Specie>
inline Foam::scalar Foam::tabulatedRealGas<Specie>::rho(scalar p, scalar T) const
{
    return table_->rho(p, T);
}


template<class Specie>
inline Foam::scalar Foam::tabulatedRealGas<Specie>::H(scalar p, scalar T) const
{
    return table_->hDep(p, T);
}


template<class Specie>
inline Foam::scalar Foam::tabulatedRealGas<Specie>::Cp(scalar p, scalar T) const
{
    return table_->cp(p, T) - table_->cp0();
}


template<class Specie>
inline Foam::scalar Foam::tabulatedRealGas<Specie>::E(scalar p, scalar T) const
{
    // e = h - p/rho; ideal gas: e0 = h0 - R T
    return table_->hDep(p, T) - (p/table_->rho(p, T) - this->R()*T);
}


template<class Specie>
inline Foam::scalar Foam::tabulatedRealGas<Specie>::Cv(scalar p, scalar T) const
{
    return table_->cv(p, T) - (table_->cp0() - this->R());
}


template<class Specie>
inline Foam::scalar Foam::tabulatedRealGas<Specie>::S(scalar p, scalar T) const
{
    return -this->R()*log(p/constant::thermodynamic::Pstd) + table_->sDep(p, T);
}


template<class Specie>
inline Foam::scalar Foam::tabulatedRealGas<Specie>::psi(scalar p, scalar T) const
{
    return table_->rho(p, T)/p;
}


template<class Specie>
inline Foam::scalar Foam::tabulatedRealGas<Specie>::Z(scalar p, scalar T) const
{
    return p/(table_->rho(p, T)*this->R()*T);
}


template<class Specie>
inline Foam::scalar Foam::tabulatedRealGas<Specie>::CpMCv(scalar p, scalar T) const
{
    return table_->cp(p, T) - table_->cv(p, T);
}
