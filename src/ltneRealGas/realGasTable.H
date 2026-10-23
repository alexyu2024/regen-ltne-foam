/*---------------------------------------------------------------------------*\
  regen-ltne-foam: ltneRealGas library. GPL-3.0-or-later.

Class
    Foam::realGasTable

Description
    Real-gas property table on a uniform (T, p) grid, read from a dictionary
    file written by tools/heliumRealGas/genHeliumTable.py (CoolProp). Fields:
    rho, hDep, cp, cv, sDep, mu, kappa; value(T_i, p_j) at index i*np + j.
    Values are interpolated bilinearly. A point outside the table is a fatal
    error (no extrapolation). Tables are read once per file and shared.

\*---------------------------------------------------------------------------*/

#ifndef realGasTable_H
#define realGasTable_H

#include "scalarList.H"
#include "fileName.H"
#include <memory>

namespace Foam
{

class dictionary;

class realGasTable
{
    // Private Data

        fileName file_;
        scalar Tmin_, dT_, pMin_, dp_;
        label nT_, np_;
        scalar molWeight_, cp0_;
        scalarList rho_, hDep_, cp_, cv_, sDep_, mu_, kappa_;

    // Private Member Functions

        void readField(const dictionary& dict, const word& name, scalarList& f);

public:

    //- Read the table from an (already expanded) file name
    explicit realGasTable(const fileName& file);

    //- The shared table for a file name as written in a dictionary
    //  (expanded, e.g. <constant>/...); read on first use
    static std::shared_ptr<const realGasTable> New(const fileName& file);

    // Access

        const fileName& file() const { return file_; }
        scalar molWeight() const { return molWeight_; }
        scalar cp0() const { return cp0_; }

    // Interpolation

        //- Bilinear interpolation of field f at (p, T)
        inline scalar interpolate(const scalarList& f, scalar p, scalar T) const;

        scalar rho(scalar p, scalar T) const { return interpolate(rho_, p, T); }
        scalar hDep(scalar p, scalar T) const { return interpolate(hDep_, p, T); }
        scalar cp(scalar p, scalar T) const { return interpolate(cp_, p, T); }
        scalar cv(scalar p, scalar T) const { return interpolate(cv_, p, T); }
        scalar sDep(scalar p, scalar T) const { return interpolate(sDep_, p, T); }
        scalar mu(scalar p, scalar T) const { return interpolate(mu_, p, T); }
        scalar kappa(scalar p, scalar T) const { return interpolate(kappa_, p, T); }

        //- Fatal error for a point outside the table
        void outOfRange(scalar p, scalar T) const;
};

} // End namespace Foam

inline Foam::scalar Foam::realGasTable::interpolate
(
    const scalarList& f,
    scalar p,
    scalar T
) const
{
    const scalar x = (T - Tmin_)/dT_;
    const scalar y = (p - pMin_)/dp_;
    if (x < 0 || y < 0 || x > nT_ - 1 || y > np_ - 1)
    {
        outOfRange(p, T);
    }
    const label i = min(label(x), nT_ - 2);
    const label j = min(label(y), np_ - 2);
    const scalar wx = x - i;
    const scalar wy = y - j;
    const label k = i*np_ + j;
    return
        (1 - wx)*((1 - wy)*f[k] + wy*f[k + 1])
      + wx*((1 - wy)*f[k + np_] + wy*f[k + np_ + 1]);
}

#endif
