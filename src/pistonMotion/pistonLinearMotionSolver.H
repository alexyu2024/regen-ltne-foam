/*---------------------------------------------------------------------------*\
    regen-ltne-foam, for OpenFOAM v2512 (www.openfoam.com). GPL-3.0-or-later.

Class
    Foam::pistonLinearMotionSolver

Description
    Prescribed piston motion without topology change. For each piston, the
    points whose axial coordinate (at rest) lies between the piston face and a
    fixed plane are displaced along the axis by w*d(t), where w goes linearly
    from 1 at the piston face to 0 at the fixed plane and d(t) is a Function1.
    Points outside every piston space do not move, so a porous zone placed
    beyond the fixed plane stays exactly stationary.

    Replaces layer addition/removal for small strokes (stroke << length of
    the piston space). Works for 1-D and axisymmetric (wedge) meshes with an
    axial piston.

Usage
    constant/dynamicMeshDict:
    \verbatim
    dynamicFvMesh    dynamicMotionSolverFvMesh;
    motionSolverLibs (ltnePistonMotion);
    motionSolver     pistonLinear;
    axis             (1 0 0);
    pistons
    {
        compression
        {
            piston       0;         // axial coordinate of the face at rest
            fixed        0.04;      // axial coordinate of the fixed plane
            rampTime    0.0434783;  // optional: d(t) - d(0) exp(-t/rampTime)
            displacement
            {
                type        sine;
                amplitude   1e-3;
                scale       1;
                level       0;
                frequency   50;
            }
        }
    }
    \endverbatim

\*---------------------------------------------------------------------------*/

#ifndef pistonLinearMotionSolver_H
#define pistonLinearMotionSolver_H

#include "points0MotionSolver.H"
#include "Function1.H"

namespace Foam
{

class pistonLinearMotionSolver
:
    public points0MotionSolver
{
    //- Unit axis of motion
    vector axis_;

    //- Axial coordinates of the piston faces and of the fixed planes
    scalarList piston_;
    scalarList fixed_;

    //- Piston displacements d(t) along the axis
    PtrList<Function1<scalar>> displacement_;

    //- Optional start-up time constants: the applied displacement is
    //  d(t) - d(0) exp(-t/rampTime), so the mesh starts at the mean position
    scalarList rampTime_;

public:

    TypeName("pistonLinear");

    pistonLinearMotionSolver(const polyMesh& mesh, const IOdictionary& dict);

    virtual ~pistonLinearMotionSolver() = default;

    //- Point positions at the current time
    virtual tmp<pointField> curPoints() const;

    //- Nothing to solve: the motion is prescribed
    virtual void solve()
    {}
};

} // End namespace Foam

#endif
