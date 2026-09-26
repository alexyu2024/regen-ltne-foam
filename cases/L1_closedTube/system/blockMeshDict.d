/*--------------------------------*- C++ -*----------------------------------*\
  regen-ltne-foam, OpenFOAM v2512
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

// Run d: 1-D tube, x in [0, 0.1] m, cross-section 0.01 m x 0.01 m; piston at x = 0
scale   1;

vertices
(
    (0     0 0) (0.005 0 0) (0.005 0.01 0) (0     0.01 0)
    (0     0 0.01) (0.005 0 0.01) (0.005 0.01 0.01) (0     0.01 0.01)
    (0.1   0 0) (0.1   0.01 0) (0.1   0 0.01) (0.1   0.01 0.01)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) pistonSpace (50 1 1) simpleGrading (1 1 1)   // 0.1 mm cells
    hex (1 8 9 2 5 10 11 6) (95 1 1) simpleGrading (1 1 1)
);

boundary
(
    piston
    {
        type wall;
        faces ((0 4 7 3));
    }
    endWall
    {
        type wall;
        faces ((8 9 11 10));
    }
    sides
    {
        type empty;
        faces
        (
            (0 1 5 4) (3 7 6 2) (0 3 2 1) (4 5 6 7)
            (1 8 10 5) (2 6 11 9) (1 2 9 8) (5 10 11 6)
        );
    }
);
