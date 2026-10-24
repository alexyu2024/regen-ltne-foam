/*---------------------------------------------------------------------------*\
  regen-ltne-foam: ltneRealGas library. GPL-3.0-or-later.
\*---------------------------------------------------------------------------*/

#include "tabulatedRealGas.H"

template<class Specie>
Foam::tabulatedRealGas<Specie>::tabulatedRealGas(const dictionary& dict)
:
    Specie(dict),
    file_(dict.subDict("equationOfState").get<fileName>("file")),
    table_(realGasTable::New(file_))
{
    // The ideal-gas part must match the table's: same molar mass, and (hConst)
    // the same cp0, otherwise the real-gas departures would not add up
    if (mag(this->W()/table_->molWeight() - 1) > 1e-6)
    {
        FatalIOErrorInFunction(dict)
            << "molWeight " << this->W() << " differs from the table's "
            << table_->molWeight() << " (" << table_->file() << ")"
            << exit(FatalIOError);
    }
    const dictionary* thermoDict = dict.findDict("thermodynamics");
    if (thermoDict && thermoDict->found("Cp"))
    {
        const scalar Cp = thermoDict->get<scalar>("Cp");
        if (mag(Cp/table_->cp0() - 1) > 1e-6)
        {
            FatalIOErrorInFunction(dict)
                << "thermodynamics Cp " << Cp << " must equal the table's "
                << "ideal-gas cp0 " << table_->cp0() << " ("
                << table_->file() << ")" << exit(FatalIOError);
        }
    }
}


template<class Specie>
void Foam::tabulatedRealGas<Specie>::write(Ostream& os) const
{
    Specie::write(os);
    os.beginBlock("equationOfState");
    os.writeEntry("file", file_);
    os.endBlock();
}


template<class Specie>
Foam::Ostream& Foam::operator<<
(
    Ostream& os,
    const tabulatedRealGas<Specie>& eos
)
{
    eos.write(os);
    return os;
}
