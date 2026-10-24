/*---------------------------------------------------------------------------*\
  regen-ltne-foam: ltneRealGas library. GPL-3.0-or-later.

Description
    Registers the tabulated real-gas thermo for heRhoThermo:
        heRhoThermo<pureMixture<tabulated2D<species::thermo<hConst<
            tabulatedRealGas<specie>>, sensibleEnthalpy>>>>
    Load with  libs (ltneRealGas);  in system/controlDict.

\*---------------------------------------------------------------------------*/

#include "rhoThermo.H"
#include "makeThermo.H"

#include "specie.H"
#include "thermo.H"
#include "sensibleEnthalpy.H"
#include "hConstThermo.H"
#include "tabulatedRealGas.H"
#include "tabulated2DTransport.H"

#include "heRhoThermo.H"
#include "pureMixture.H"

namespace Foam
{
    makeThermos
    (
        rhoThermo,
        heRhoThermo,
        pureMixture,
        tabulated2DTransport,
        sensibleEnthalpy,
        hConstThermo,
        tabulatedRealGas,
        specie
    );
}
