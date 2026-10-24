/*---------------------------------------------------------------------------*\
  regen-ltne-foam: ltneRealGas library. GPL-3.0-or-later.

Class
    Foam::tabulatedRealGas

Description
    Real-gas equation of state from a (T, p) property table (realGasTable).
    Returns the density and the departures from the ideal gas that OpenFOAM's
    thermo classes add to the ideal-gas part (use with hConst, whose Cp must
    be the table's ideal-gas cp0):
        rho(p, T)            from the table
        H, Cp, E, Cv         real minus ideal-gas values
        S                    -R ln(p/Pstd) + entropy departure
        psi = rho/p, Z = p/(rho R T), CpMCv = cp - cv

    Dictionary (in the species entry of thermophysicalProperties):
        equationOfState
        {
            file    "<constant>/helium_CoolProp.dat";
        }

\*---------------------------------------------------------------------------*/

#ifndef tabulatedRealGas_H
#define tabulatedRealGas_H

#include "autoPtr.H"
#include "realGasTable.H"

namespace Foam
{

template<class Specie> class tabulatedRealGas;

template<class Specie>
Ostream& operator<<(Ostream& os, const tabulatedRealGas<Specie>&);

template<class Specie>
class tabulatedRealGas
:
    public Specie
{
    // Private Data

        fileName file_;
        std::shared_ptr<const realGasTable> table_;

public:

    // Constructors

        explicit tabulatedRealGas(const dictionary& dict);

        inline tabulatedRealGas(const word& name, const tabulatedRealGas&);

        inline autoPtr<tabulatedRealGas> clone() const;

        inline static autoPtr<tabulatedRealGas> New(const dictionary& dict);

    // Member Functions

        static word typeName()
        {
            return "tabulatedRealGas<" + word(Specie::typeName_()) + '>';
        }

        // Fundamental properties

            static const bool incompressible = false;
            static const bool isochoric = false;

            inline scalar rho(scalar p, scalar T) const;
            inline scalar H(const scalar p, const scalar T) const;
            inline scalar Cp(scalar p, scalar T) const;
            inline scalar E(const scalar p, const scalar T) const;
            inline scalar Cv(scalar p, scalar T) const;
            inline scalar S(const scalar p, const scalar T) const;
            inline scalar psi(scalar p, scalar T) const;
            inline scalar Z(scalar p, scalar T) const;
            inline scalar CpMCv(scalar p, scalar T) const;

        // IO

            void write(Ostream& os) const;

    // Ostream Operator

        friend Ostream& operator<< <Specie>
        (
            Ostream&,
            const tabulatedRealGas&
        );
};

} // End namespace Foam

#include "tabulatedRealGasI.H"

#ifdef NoRepository
    #include "tabulatedRealGas.C"
#endif

#endif
