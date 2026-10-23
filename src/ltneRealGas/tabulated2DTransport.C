/*---------------------------------------------------------------------------*\
  regen-ltne-foam: ltneRealGas library. GPL-3.0-or-later.
\*---------------------------------------------------------------------------*/

#include "tabulated2DTransport.H"

template<class Thermo>
Foam::tabulated2DTransport<Thermo>::tabulated2DTransport(const dictionary& dict)
:
    Thermo(dict),
    file_(dict.subDict("transport").get<fileName>("file")),
    table_(realGasTable::New(file_))
{}


template<class Thermo>
void Foam::tabulated2DTransport<Thermo>::write(Ostream& os) const
{
    os.beginBlock(this->name());
    Thermo::write(os);
    os.beginBlock("transport");
    os.writeEntry("file", file_);
    os.endBlock();
    os.endBlock();
}


template<class Thermo>
Foam::Ostream& Foam::operator<<
(
    Ostream& os,
    const tabulated2DTransport<Thermo>& pt
)
{
    pt.write(os);
    return os;
}
