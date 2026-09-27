/*---------------------------------------------------------------------------*\
    regen-ltne-foam, for OpenFOAM v2512 (www.openfoam.com). GPL-3.0-or-later.
\*---------------------------------------------------------------------------*/

#include "pistonLinearMotionSolver.H"
#include "addToRunTimeSelectionTable.H"

namespace Foam
{
    defineTypeNameAndDebug(pistonLinearMotionSolver, 0);
    addToRunTimeSelectionTable
    (
        motionSolver,
        pistonLinearMotionSolver,
        dictionary
    );
}


Foam::pistonLinearMotionSolver::pistonLinearMotionSolver
(
    const polyMesh& mesh,
    const IOdictionary& dict
)
:
    points0MotionSolver(mesh, dict, typeName),
    axis_(normalised(coeffDict().get<vector>("axis")))
{
    const dictionary& pistonsDict = coeffDict().subDict("pistons");
    const wordList names(pistonsDict.toc());

    piston_.setSize(names.size());
    fixed_.setSize(names.size());
    displacement_.setSize(names.size());
    rampTime_.setSize(names.size());

    forAll(names, i)
    {
        const dictionary& d = pistonsDict.subDict(names[i]);
        piston_[i] = d.get<scalar>("piston");
        fixed_[i] = d.get<scalar>("fixed");
        rampTime_[i] = d.getOrDefault<scalar>("rampTime", 0);
        displacement_.set
        (
            i,
            Function1<scalar>::New("displacement", d, &mesh)
        );

        Info<< "pistonLinear: " << names[i] << " face at " << piston_[i]
            << ", fixed plane at " << fixed_[i] << endl;
    }
}


Foam::tmp<Foam::pointField>
Foam::pistonLinearMotionSolver::curPoints() const
{
    const scalar t = mesh().time().value();

    auto tpoints = tmp<pointField>::New(points0_);
    pointField& points = tpoints.ref();

    forAll(piston_, i)
    {
        scalar d = displacement_[i].value(t);
        if (rampTime_[i] > 0)
        {
            d -= displacement_[i].value(0)*Foam::exp(-t/rampTime_[i]);
        }

        forAll(points0_, pointi)
        {
            const scalar s = points0_[pointi] & axis_;
            const scalar w = (fixed_[i] - s)/(fixed_[i] - piston_[i]);

            if (w > 0)
            {
                points[pointi] += min(w, scalar(1))*d*axis_;
            }
        }
    }

    return tpoints;
}
