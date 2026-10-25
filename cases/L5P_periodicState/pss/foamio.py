"""Read and write the internalField of OpenFOAM ascii volFields, and the cell geometry of the 1-D L5 column.

Only what the periodic-state driver needs: scalar and vector fields whose internalField is either uniform or a
nonuniform List, written by ltneFoam with writeFormat ascii. Boundary entries are kept as written.
"""
import os, re

import numpy as np

_NONUNI = re.compile(r'internalField\s+nonuniform\s+List<(scalar|vector)>\s*(\d+)\s*\(')
_UNI = re.compile(r'internalField\s+uniform\s+([^;]+);')


def time_dirs(case):
    """Time directory names of a case, sorted by value (0 excluded only if it is not a number)."""
    out = []
    for d in os.listdir(case):
        try:
            float(d)
        except ValueError:
            continue
        if os.path.isdir(os.path.join(case, d)):
            out.append(d)
    return sorted(out, key=float)


def read_internal(path, ncells=None):
    """(kind, array, text, span): the internalField of a field file; span is the character range of the values
    (including the enclosing List header and parentheses for nonuniform fields)."""
    text = open(path).read()
    m = _NONUNI.search(text)
    if m:
        kind, n = m.group(1), int(m.group(2))
        start = m.end()
        if kind == 'scalar':
            end = text.index(')', start)
            vals = np.array(text[start:end].split(), dtype=float)
        else:
            # vectors: n entries "(x y z)"; the List ends at the first ')' on its own line after them
            end = start
            rows = []
            for _ in range(n):
                a = text.index('(', end)
                b = text.index(')', a)
                rows.append([float(x) for x in text[a + 1:b].split()])
                end = b + 1
            end = text.index(')', end)
            vals = np.array(rows)
        if len(vals) != n:
            raise ValueError(f'{path}: {len(vals)} values, header says {n}')
        return kind, vals, text, (m.start(), end + 1)
    m = _UNI.search(text)
    if not m:
        raise ValueError(f'{path}: no internalField')
    s = m.group(1).strip()
    if ncells is None:
        raise ValueError(f'{path}: uniform internalField needs ncells')
    if s.startswith('('):
        v = np.array(s.strip('()').split(), dtype=float)
        return 'vector', np.tile(v, (ncells, 1)), text, (m.start(), m.end())
    return 'scalar', np.full(ncells, float(s)), text, (m.start(), m.end())


def read_field(path, ncells=None):
    return read_internal(path, ncells)[1]


def write_internal(path, values):
    """Replace the internalField of an existing field file with values (scalar: 1-D, vector: n x 3), keeping
    17 significant digits (exact round trip of doubles)."""
    _, _, text, (a, b) = read_internal(path, len(values))
    v = np.asarray(values, dtype=float)
    if v.ndim == 1:
        body = '\n'.join(repr(float(x)) for x in v)
        new = f'internalField   nonuniform List<scalar>\n{len(v)}\n(\n{body}\n)\n'
    else:
        body = '\n'.join('(' + ' '.join(repr(float(x)) for x in row) + ')' for row in v)
        new = f'internalField   nonuniform List<vector>\n{len(v)}\n(\n{body}\n)\n'
    # keep the ';' that followed the replaced block
    rest = text[b:]
    if not rest.lstrip().startswith(';'):
        rest = ';' + rest
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        f.write(text[:a] + new + rest)
    os.replace(tmp, path)


def points_z(case, time):
    """z of the mesh points at a time (moving mesh: <time>/polyMesh/points, else constant/polyMesh/points)."""
    p = os.path.join(case, time, 'polyMesh', 'points')
    if not os.path.exists(p):
        p = os.path.join(case, 'constant', 'polyMesh', 'points')
    text = open(p).read()
    m = re.search(r'\n(\d+)\s*\(', text)
    n = int(m.group(1))
    rows = re.findall(r'\(([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\)', text[m.end():])[:n]
    return np.array([float(r[2]) for r in rows])


def cell_geometry(case, time, ncells, area):
    """(z_centre, volume) of the cells of the 1-D column, cells ordered along +z as blockMesh writes them."""
    z = np.unique(np.round(points_z(case, time), 12))
    if len(z) != ncells + 1:
        raise ValueError(f'{len(z)} point planes for {ncells} cells')
    return 0.5 * (z[1:] + z[:-1]), np.diff(z) * area
