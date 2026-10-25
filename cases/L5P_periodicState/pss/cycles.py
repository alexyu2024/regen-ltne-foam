"""Per-cycle tables of a run directory written with one time directory per cycle boundary.

  python3 -m pss.cycles extract <run> [--keep-states]
      for every cycle-boundary time directory not yet in <run>/cycles.csv: append the registered cycle quantities
      (segment Ts differences and means from the cycle-mean Ts, gas mass, mean pressure, state norm), optionally save
      the state vector to <run>/states/c<k>.npy, then delete every time directory except the latest
      (and the 0 directory).
The face quantities (H, HX heat, phasors) are folded into <run>/per_cycle.csv by the L5 results.py.
"""
import csv, importlib.util, os, shutil, sys

import numpy as np

from . import case as C
from . import foamio

FIELDS = ['cycle', 'time', 'gas_mass_kg', 'p_mean_Pa'] + [f'Ts_node{i}' for i in range(5)] \
    + [f'dT_seg{i}' for i in range(1, 5)] + [f'Ts_seg{i}_mean' for i in range(1, 5)] + ['x_rms_K']


def l5_results():
    spec = importlib.util.spec_from_file_location('l5results', os.path.join(C.L5, 'results.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def cycle_of_time(t):
    return int(round(float(t) * C.F))


def row_for(run, t):
    x, f = C.read_state(run, t)
    m, V = C.gas_mass(run, t, f['p'], f['T'])
    d = {'cycle': cycle_of_time(t), 'time': t, 'gas_mass_kg': m,
         'p_mean_Pa': float(np.sum(C.EPS * f['p'] * V) / np.sum(C.EPS * V)),
         'x_rms_K': float(np.sqrt(np.mean(x ** 2)))}
    d.update(C.segment_quantities(run, t))
    return d, x


def load(run, name='cycles.csv'):
    path = os.path.join(run, name)
    if not os.path.exists(path):
        return []
    return list(csv.DictReader(open(path)))


def extract(run, keep_states=False):
    have = {int(r['cycle']) for r in load(run)}
    times = [t for t in foamio.time_dirs(run) if float(t) > 0]
    new = []
    for t in times:
        k = cycle_of_time(t)
        if k in have or not os.path.exists(os.path.join(run, t, 'TsMean')):
            continue
        d, x = row_for(run, t)
        new.append(d)
        if keep_states:
            os.makedirs(os.path.join(run, 'states'), exist_ok=True)
            np.save(os.path.join(run, 'states', f'c{k:05d}.npy'), x)
    path = os.path.join(run, 'cycles.csv')
    exists = os.path.exists(path)
    with open(path, 'a', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if not exists:
            w.writeheader()
        for d in sorted(new, key=lambda r: r['cycle']):
            w.writerow({k: (repr(v) if isinstance(v, float) else v) for k, v in d.items()})
    for t in times[:-1]:
        shutil.rmtree(os.path.join(run, t))
    return len(new)


if __name__ == '__main__':
    if sys.argv[1] == 'extract':
        print(f'cycles: {extract(sys.argv[2], "--keep-states" in sys.argv)} new cycle(s)')
    else:
        sys.exit(__doc__)
