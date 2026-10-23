"""One cycle = one map: x_(k+1) = Phi(x_k), with ltneFoam unchanged as the black box.

A State is a cycle-boundary time directory (t = k T) of a run: every field ltneFoam reads on a restart (p, T, Ts,
U, phi, rhoUf, dpdt, meshPhi, the moving mesh points, the fieldAverage state). Evaluating the map from a State
with a new state vector x (case.py: Ts on the matrix cells, T on all cells):

1. copy the State's time directory, constant/ and system/ into a fresh directory;
2. write x into T and Ts (Ts of the open gas cells is set to T there, as the solver does; the HX cells keep their
   fixed Ts);
3. shift the pressure field by a uniform dp so that the gas mass sum eps p / (R T) V equals the inventory M0 of the
   run (the solver conserves it to ~1e-11 per cycle); remove rho so that ltneFoam recomputes it from p and T
   (createFields.H: rho is READ_IF_PRESENT, else thermo.rho()). U, phi, rhoUf and dpdt are carried unchanged:
   they belong to the fast (acoustic, in-cycle) part of the state, which one cycle re-establishes;
4. run ltneFoam for exactly one cycle (2400 steps) and return the new cycle-boundary State.

Every call to run() is one cycle of the honest count; the caller (methods.py) counts them.
"""
import concurrent.futures as cf
import os, shutil, subprocess

import numpy as np

from . import case as C
from . import foamio
from .cycles import l5_results

L5R = l5_results()

LOG_FILTER = ['grep', '-v', '-E', r'^(Time = |PIMPLE: iteration|Courant Number|time step continuity|ExecutionTime|'
              r'fieldAverage cycleMean write:|    Calculating averages|    Writing average fields)|^$']


class State:
    """A cycle-boundary time directory of a case directory."""

    def __init__(self, case_dir, time):
        self.case, self.time = case_dir, time
        self.x, self.fields = C.read_state(case_dir, time)
        self.mass, self.V = C.gas_mass(case_dir, time, self.fields['p'], self.fields['T'])
        self.p_mean = float(np.sum(C.EPS * self.fields['p'] * self.V) / np.sum(C.EPS * self.V))

    @property
    def cycle(self):
        return int(round(float(self.time) * C.F))

    @property
    def dir(self):
        return os.path.join(self.case, self.time)

    def quantities(self):
        """The registered per-cycle quantities (docs/VERIFICATION.md, L5P) of the cycle that ended at this State;
        the face and HX terms come from the L5 results.py on the run's monitor files."""
        if getattr(self, '_q', None) is None:
            L5R.summarise(self.case, C.STEPS)
            rows = [r for r in L5R.load_per_cycle(self.case) if int(r['cycle']) == self.cycle]
            q = {'cycle': self.cycle, 'p_mean': self.p_mean, 'mass': self.mass}
            if rows:
                r = rows[0]
                q.update(Q_hot=r['Qhot_gas'] + r['Qhot_solid'], Q_cold=r['Qcold_gas'] + r['Qcold_solid'],
                         T_joint=r['Tjoint_mean'], H_hot=r['H_hot'], H_cold=r['H_cold'])
            q.update(C.segment_quantities(self.case, self.time))
            self._q = q
        return self._q


def mass_consistent_p(p, T, V, M0):
    """Uniform shift of p so that sum eps p / (R T) V = M0 (perfectGas)."""
    w = C.EPS * V / (C.R_GAS * T)
    dp = (M0 - float(np.sum(w * p))) / float(np.sum(w))
    return p + dp, dp


class CycleMap:
    def __init__(self, work, M0, workers=1):
        self.work, self.M0 = work, M0
        self.count = 0          # cycles run through this map (the honest count)
        self.log = []           # (count, tag, start time, max|x_in - x_start|, dp shift)
        self.pool = cf.ThreadPoolExecutor(max_workers=workers)
        os.makedirs(work, exist_ok=True)

    def prepare(self, start, x, tag):
        """Write the start directory of one map evaluation; returns (dir, |dp|)."""
        d = os.path.join(self.work, tag)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
        for sub in ('constant', 'system'):
            shutil.copytree(os.path.join(start.case, sub), os.path.join(d, sub))
        shutil.copytree(start.dir, os.path.join(d, start.time))
        dp = 0.0
        if x is not None:
            C.check_eos(d)
            Tm, Tg = C.split(np.asarray(x, dtype=float))
            T = Tg.copy()
            Ts = start.fields['Ts'].copy()
            Ts[C.MATRIX] = Tm
            solid = np.zeros(C.N, bool)
            solid[C.ZONE['hot_hx']] = solid[C.ZONE['cold_hx']] = True
            solid[C.MATRIX] = True
            Ts[~solid] = T[~solid]
            p, dp = mass_consistent_p(start.fields['p'], T, start.V, self.M0)
            self.jump_mass_err = max(getattr(self, 'jump_mass_err', 0.0), abs(
                float(np.sum(C.EPS * p / (C.R_GAS * T) * start.V)) - self.M0) / self.M0)
            td = os.path.join(d, start.time)
            foamio.write_internal(os.path.join(td, 'T'), T)
            foamio.write_internal(os.path.join(td, 'Ts'), Ts)
            foamio.write_internal(os.path.join(td, 'p'), p)
            if os.path.exists(os.path.join(td, 'rho')):
                os.remove(os.path.join(td, 'rho'))
        k = int(round(float(start.time) * C.F))
        end = repr((k + 1) / C.F)
        cd = os.path.join(d, 'system', 'controlDict')
        txt = open(cd).read().splitlines()
        out = []
        for l in txt:
            for key, val in (('startFrom', 'latestTime'), ('endTime', end), ('writeInterval', str(C.STEPS)),
                             ('purgeWrite', '0'), ('timePrecision', '17')):
                if l.startswith(key + ' '):
                    l = f'{key:<16}{val};'
            out.append(l)
        open(cd, 'w').write('\n'.join(out) + '\n')
        return d, abs(dp)

    def _run(self, d):
        with open(os.path.join(d, 'log.ltneFoam'), 'w') as log:
            p1 = subprocess.Popen(['ltneFoam', '-case', d], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p2 = subprocess.Popen(LOG_FILTER, stdin=p1.stdout, stdout=log)
            p1.stdout.close()
            rc = p1.wait()
            p2.wait()
        text = open(os.path.join(d, 'log.ltneFoam')).read()
        if rc != 0 or '\nEnd' not in text:
            raise RuntimeError(f'ltneFoam failed in {d} (exit {rc})')
        times = [t for t in foamio.time_dirs(d)]
        return State(d, times[-1])

    def run(self, start, x=None, tag=None):
        return self.run_many([(start, x, tag)])[0]

    def run_many(self, jobs):
        """Evaluate several maps concurrently; jobs = [(start State, x or None, tag)]. Each one counts one cycle."""
        dirs = []
        for start, x, tag in jobs:
            self.count += 1
            tag = tag or f'e{self.count:05d}'
            d, dp = self.prepare(start, x, f'{self.count:05d}_{tag}')
            dx = 0.0 if x is None else float(np.max(np.abs(np.asarray(x) - start.x)))
            self.log.append((self.count, tag, start.time, dx, dp))
            dirs.append(d)
        return list(self.pool.map(self._run, dirs))

    def cleanup(self, keep):
        """Remove evaluation directories except those holding the States in keep."""
        keep = {os.path.abspath(s.case) for s in keep}
        for n in os.listdir(self.work):
            p = os.path.abspath(os.path.join(self.work, n))
            if os.path.isdir(p) and p not in keep:
                shutil.rmtree(p)
