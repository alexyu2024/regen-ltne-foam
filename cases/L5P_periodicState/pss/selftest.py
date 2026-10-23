"""Self-test of the three methods on a synthetic linear-plus-quadratic map with the L5D slow multiplier 0.9967
and two near-slow modes (0.97, 0.9); no solver. Run from the case directory: python3 -m pss.selftest
Exit 1 if a method ends farther than 0.005 from the fixed point."""
import sys

import numpy as np

from . import methods as MT

n = 60
rng = np.random.default_rng(1)
Q, _ = np.linalg.qr(rng.standard_normal((n, n)))
lam = np.concatenate([[0.9967, 0.97, 0.9], 0.6 * rng.random(n - 3)])
M = Q @ np.diag(lam) @ Q.T
xstar = 20 + rng.random(n)
def nonlin(x):   # mild nonlinearity
    return 0.002 * (x - xstar) ** 2
class S:
    def __init__(s, x): s.x = x
class FakeMap:
    count = 0
    def run(s, base, x, tag=None): return s.run_many([(base, x, tag)])[0]
    def run_many(s, jobs):
        out = []
        for b, x, t in jobs:
            s.count += 1
            x = b.x if x is None else x
            out.append(S(xstar + M @ (x - xstar) + nonlin(x)))
        return out
def verify(run, pt):
    rows = []
    for j in range(MT.NV):
        s = run.phi(pt, 'v'); pt = (s, None); rows.append({'q': float(np.max(np.abs(s.x - xstar)))})
    return True, pt
x0 = xstar + 0.8 * Q[:, 0] / np.max(np.abs(Q[:, 0])) + 0.3 * Q[:, 1] + 0.2 * rng.standard_normal(n)
# fixed point of nonlinear map near xstar: iterate many times
xf = x0.copy()
for _ in range(20000): xf = xstar + M @ (xf - xstar) + nonlin(xf)
bad = False
for name, fn, p in [('np1', MT.newton_picard, 1), ('np2', MT.newton_picard, 2), ('np3', MT.newton_picard, 3),
                    ('brr3', MT.brr, 3), ('brr6', MT.brr, 6), ('gm0', MT.graves_morris, 0), ('gm3', MT.graves_morris, 3)]:
    cm = FakeMap(); run = MT.Run(cm, name)
    try:
        pt = fn(run, (S(x0.copy()), None), p, verify)
        err = np.max(np.abs(MT.x_of(pt) - xf))
    except MT.Budget:
        err = float('nan')
    bad = bad or not err <= 0.005
    print(f'{name}: cycles {cm.count} (incl. {MT.NV} verify), final err {err:.2e}, iters {len(run.hist)}')
nat = x0.copy(); k = 0
while np.max(np.abs(nat - xf)) > 0.005:
    nat = xstar + M @ (nat - xstar) + nonlin(nat); k += 1
print('natural cycles to 0.005:', k)
sys.exit(1 if bad else 0)
