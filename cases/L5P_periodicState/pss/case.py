"""The L5 slice as seen by the periodic-state driver: cell layout, the state vector, cycle quantities.

State at a cycle boundary t = k T (same phase every cycle):
  x = [Ts on the 120 matrix cells, T on all 172 gas cells], in K.
The pressure, velocity and flux fields are carried along with x (see cyclemap.py); the mean pressure is slaved to
x by the gas mass inventory, which the solver conserves.
"""
import math, os

import numpy as np
import yaml

from . import foamio

HERE = os.path.dirname(os.path.abspath(__file__))
L5 = os.path.normpath(os.path.join(HERE, '..', '..', 'L5_regenSlice'))
P = yaml.safe_load(open(os.path.join(L5, 'params_L5.yaml')))
F = P['operating_point']['frequency_Hz']
T_CYCLE = 1.0 / F
STEPS = 2400
AREA = P['layout']['area_m2']
R_GAS = P['gas']['R_J_kgK']
ORDER = ['hot_chamber', 'hot_hx', 'matrix_500', 'matrix_635', 'cold_hx', 'cold_chamber']
NCELLS = {'hot_chamber': 24, 'hot_hx': 10, 'matrix_500': 60, 'matrix_635': 60, 'cold_hx': 10, 'cold_chamber': 8}
N = sum(NCELLS.values())
_start = np.cumsum([0] + [NCELLS[n] for n in ORDER])
ZONE = {n: slice(_start[i], _start[i + 1]) for i, n in enumerate(ORDER)}
MATRIX = slice(ZONE['matrix_500'].start, ZONE['matrix_635'].stop)
NM = MATRIX.stop - MATRIX.start
NX = NM + N

# matrix segments for the registered temperature differences: quarters of the matrix, z in m
Z = P['layout']['zones']
Z0, ZJ, Z1 = Z['matrix_500']['z'][0], Z['matrix_635']['z'][0], Z['matrix_635']['z'][1]
SEG_NODES = [Z0, 0.5 * (Z0 + ZJ), ZJ, 0.5 * (ZJ + Z1), Z1]


def porosity():
    eps = np.ones(N)
    for n in ORDER:
        if n in ('hot_hx', 'cold_hx'):
            eps[ZONE[n]] = P['porous_hx']['porosity']
    eps[ZONE['matrix_500']] = P['porous_matrix']['screen_500']['porosity']
    eps[ZONE['matrix_635']] = P['porous_matrix']['screen_635']['porosity']
    return eps


EPS = porosity()


def read_state(case, time):
    """x, and the raw fields {T, Ts, p} at a time directory."""
    d = os.path.join(case, time)
    T = foamio.read_field(os.path.join(d, 'T'), N)
    Ts = foamio.read_field(os.path.join(d, 'Ts'), N)
    p = foamio.read_field(os.path.join(d, 'p'), N)
    return np.concatenate([Ts[MATRIX], T]), {'T': T, 'Ts': Ts, 'p': p}


def split(x):
    return x[:NM], x[NM:]


def gas_mass(case, time, p, T):
    """sum eps rho V, rho = p / (R T): the case's equation of state is perfectGas (mkCase.py)."""
    _, V = foamio.cell_geometry(case, time, N, AREA)
    return float(np.sum(EPS * p / (R_GAS * T) * V)), V


def check_eos(case):
    txt = open(os.path.join(case, 'constant', 'thermophysicalProperties')).read()
    if 'perfectGas' not in txt:
        raise NotImplementedError('the mass-consistent pressure update assumes equationOfState perfectGas')


def cycle_mean_profiles(case, time):
    """Cycle-mean T and Ts (fieldAverage, restarted every cycle) at a cycle-boundary write time."""
    d = os.path.join(case, time)
    return (foamio.read_field(os.path.join(d, 'TMean'), N), foamio.read_field(os.path.join(d, 'TsMean'), N))


def segment_quantities(case, time):
    """Cycle-mean matrix Ts at the five segment nodes, the four segment differences and the four segment means."""
    zc, _ = foamio.cell_geometry(case, time, N, AREA)
    _, TsM = cycle_mean_profiles(case, time)
    zm, tm = zc[MATRIX], TsM[MATRIX]
    # end nodes: the end cell value (the matrix faces lie half a cell outside the first and last cell centre)
    nodes = [float(np.interp(z, zm, tm)) for z in SEG_NODES]
    d = {f'Ts_node{i}': v for i, v in enumerate(nodes)}
    for i in range(4):
        d[f'dT_seg{i + 1}'] = nodes[i] - nodes[i + 1]
        sel = (zm >= SEG_NODES[i]) & (zm < SEG_NODES[i + 1])
        d[f'Ts_seg{i + 1}_mean'] = float(np.mean(tm[sel]))
    return d
