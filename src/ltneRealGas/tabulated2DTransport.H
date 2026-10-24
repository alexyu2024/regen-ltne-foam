/*---------------------------------------------------------------------------*\
  regen-ltne-foam: ltneRealGas library. GPL-3.0-or-later.

Class
    Foam::tabulated2DTransport

Description
    Transport from a (T, p) property table (realGasTable): mu(p, T) and
    kappa(p, T); alphah = kappa/Cp with the thermo's (real-gas) Cp.

    Dictionary (in the species entry of thermophysicalProperties):
        transport
        {
            file    "<constant>/helium_CoolProp.dat";
        }

\*---------------------------------------------------------------------------*/

#ifndef tabulated2DTransport_H
#define tabulated2DTransport_H

#include "autoPtr.H"
#include "realGasTable.H"

namespace Foam
{

template<class Thermo> class tabulated2DTransport;

template<class Thermo>
Ostream& operator<<(Ostream&, const tabulated2DTransport<Thermo>&);

template<class Thermo>
class tabulated2DTransport
:
    public Thermo
{
    // Private Data

        fileName file_;
        std::shared_ptr<const realGasTable> table_;

public:

    // Constructors

        inline tabulated2DTransport(const word&, const tabulated2DTransport&);

        explicit tabulated2DTransport(const dictionary& dict);

        inline autoPtr<tabulated2DTransport> clone() const;

        inline static autoPtr<tabulated2DTransport> New(const dictionary& dict);

    // Member Functions

        static word typeName()
        {
            return "tabulated2D<" + Thermo::typeName() + '>';
        }

        inline scalar mu(const scalar p, const scalar T) const
        {
            return table_->mu(p, T);
        }

        inline scalar kappa(const scalar p, const scalar T) const
        {
            return table_->kappa(p, T);
        }

        inline scalar alphah(const scalar p, const scalar T) const
        {
            return kappa(p, T)/this->Cp(p, T);
        }

        void write(Ostream& os) const;

    // Ostream Operator

        friend Ostream& operator<< <Thermo>
        (
            Ostream&,
            const tabulated2DTransport&
        );
};

} // End namespace Foam

template<class Thermo>
inline Foam::tabulated2DTransport<Thermo>::tabulated2DTransport
(
    const word& name,
    const tabulated2DTransport& pt
)
:
    Thermo(name, pt),
    file_(pt.file_),
    table_(pt.table_)
{}


template<class Thermo>
inline Foam::autoPtr<Foam::tabulated2DTransport<Thermo>>
Foam::tabulated2DTransport<Thermo>::clone() const
{
    return autoPtr<tabulated2DTransport<Thermo>>::New(*this);
}


template<class Thermo>
inline Foam::autoPtr<Foam::tabulated2DTransport<Thermo>>
Foam::tabulated2DTransport<Thermo>::New(const dictionary& dict)
{
    return autoPtr<tabulated2DTransport<Thermo>>::New(dict);
}

#ifdef NoRepository
    #include "tabulated2DTransport.C"
#endif

#endif
