"""Periodic-state methods on the cycle map (docs/VERIFICATION.md, L5P; docs/L5P_PERIODIC_STATE.md).

A point is (base, x): a state vector x placed into the fast fields of the cycle-boundary State base (x = None:
base.x unchanged, i.e. a plain cycle). Every map evaluation is one counted cycle (CycleMap.count). The parameters
are those registered in docs/VERIFICATION.md, L5P.
"""
import numpy as np

STOP = 0.005        # K: stop iterating when the proposed correction is at most this, max norm,
RES = 1.5e-5        # K: and the residual Phi(x) - x at the current iterate is at most this, max norm
CAP = 2.0           # K: corrections are scaled down to at most this, max norm
FD_EPS = 0.05       # K: finite-difference perturbation, max norm
NV, SKIP = 50, 10   # verification cycles, of which the first SKIP are not tested
BUDGET = 600        # cycles after the start state


class Budget(Exception):
    pass


def cap(c):
    m = float(np.max(np.abs(c)))
    return (c * (CAP / m), True) if m > CAP else (c, False)


class Run:
    """Book-keeping shared by the methods: the map, the start count and the iteration history."""

    def __init__(self, cmap, name):
        self.cmap, self.name = cmap, name
        self.start = cmap.count
        self.hist = []

    def used(self):
        return self.cmap.count - self.start

    def need(self, n):
        if self.used() + n > BUDGET:
            raise Budget()

    def phi(self, pt, tag):
        self.need(1)
        return self.cmap.run(pt[0], pt[1], tag=f'{self.name}_{tag}')

    def phis(self, pts, tag):
        self.need(len(pts))
        return self.cmap.run_many([(b, x, f'{self.name}_{tag}{i}') for i, (b, x) in enumerate(pts)])

    def note(self, **kw):
        kw.setdefault('count', self.used())
        self.hist.append(kw)


def x_of(pt):
    return pt[0].x if pt[1] is None else pt[1]


def ritz(H):
    ev = np.linalg.eigvals(np.atleast_2d(H))
    return ';'.join(f'{z.real:.6f}' + (f'{z.imag:+.1e}j' if abs(z.imag) > 1e-12 else '') for z in ev)


# ---------------------------------------------------------------- (a) Newton-Picard / RPM
def newton_picard(run, pt, p, verify):
    """Lust et al. 1998: Newton on the p-dimensional dominant subspace of M = dPhi/dx, one Picard step on the
    complement, the subspace re-estimated at the current state every iteration (one subspace-iteration step)."""
    xs = [x_of(pt)]
    for i in range(p):
        s = run.phi(pt, f'init{i}')
        pt = (s, None)
        xs.append(s.x)
    V, _ = np.linalg.qr(np.diff(np.array(xs), axis=0).T)
    it = 0
    while True:
        it += 1
        base, x = pt[0], x_of(pt)
        hs = [FD_EPS / float(np.max(np.abs(V[:, j]))) for j in range(p)]
        out = run.phis([pt] + [(base, x + hs[j] * V[:, j]) for j in range(p)], f'it{it}_')
        phi = out[0]
        r = phi.x - x
        W = np.column_stack([(out[j + 1].x - phi.x) / hs[j] for j in range(p)])
        H = V.T @ W
        rv = V.T @ r
        c, capped = cap(V @ (np.linalg.solve(np.eye(p) - H, rv) - rv))
        run.note(it=it, res_max=float(np.max(np.abs(r))), corr_max=float(np.max(np.abs(c))), capped=capped,
                 ritz=ritz(H))
        V, _ = np.linalg.qr(W)
        if float(np.max(np.abs(c))) <= STOP and float(np.max(np.abs(r))) <= RES:
            done, pt = verify(run, (phi, None))
            if done:
                return pt
            continue
        pt = (phi, phi.x + c)


# ---------------------------------------------------------------- (b) Broyden Rank Reduction
def brr(run, pt, p, verify):
    """van de Rotten, Verduyn Lunel, Bliek 2006: Broyden's good method for g(x) = Phi(x) - x = 0 with
    B = -I + C D^T of rank at most p; when the rank would exceed p, the update is reduced by an SVD of C D^T and
    the smallest singular direction is dropped."""
    n = len(x_of(pt))
    C = np.zeros((n, 0))
    D = np.zeros((n, 0))

    def solve(g):
        # (-I + C D^T) s = -g  ->  s = g + C (I - D^T C)^-1 D^T g
        if C.shape[1] == 0:
            return g.copy()
        return g + C @ np.linalg.solve(np.eye(C.shape[1]) - D.T @ C, D.T @ g)

    s_ = run.phi(pt, 'g0')
    x, g, base = x_of(pt), s_.x - x_of(pt), s_
    it = 0
    while True:
        it += 1
        step, capped = cap(solve(g))
        run.note(it=it, res_max=float(np.max(np.abs(g))), corr_max=float(np.max(np.abs(step))), capped=capped,
                 rank=C.shape[1])
        if float(np.max(np.abs(step))) <= STOP and float(np.max(np.abs(g))) <= RES:
            done, vpt = verify(run, (base, x + step))
            if done:
                return vpt
            # restart from the end of the verification cycles, keeping the Broyden matrix
            s_ = run.phi(vpt, f'g{it}r')
            x, g, base = x_of(vpt), s_.x - x_of(vpt), s_
            continue
        xn = x + step
        s_ = run.phi((base, xn), f'g{it}')
        gn = s_.x - xn
        y = gn - g
        # B s = -s + C (D^T s); good Broyden: B += (y - B s) s^T / (s^T s)
        Bs = -step + C @ (D.T @ step)
        u = (y - Bs) / float(step @ step)
        if C.shape[1] >= p:
            # rank reduction: SVD of C D^T (via QR of C and D), keep the p - 1 largest singular directions
            Qc, Rc = np.linalg.qr(C)
            Qd, Rd = np.linalg.qr(D)
            U, sig, Vt = np.linalg.svd(Rc @ Rd.T)
            C = Qc @ U[:, :p - 1] * sig[:p - 1]
            D = Qd @ Vt[:p - 1].T
        C = np.column_stack([C, u])
        D = np.column_stack([D, step])
        x, g, base = xn, gn, s_


# ---------------------------------------------------------------- (c) Graves-Morris
def graves_morris(run, pt, m, verify):
    """Subraveti et al. 2024 eq. 6 (Graves-Morris), alternating with plain cycles:
    x* = x1 - [(x1 - x0).(x2 - 2 x1 + x0) / |x2 - 2 x1 + x0|^2] (x2 - x1)."""
    rnd = 0
    while True:
        rnd += 1
        for i in range(m):
            pt = (run.phi(pt, f'r{rnd}_plain{i}'), None)
        x0 = x_of(pt)
        s1 = run.phi(pt, f'r{rnd}_x1')
        s2 = run.phi((s1, None), f'r{rnd}_x2')
        x1, x2 = s1.x, s2.x
        b = x2 - 2 * x1 + x0
        xe = x1 - float((x1 - x0) @ b) / float(b @ b) * (x2 - x1)
        c, capped = cap(xe - x2)
        run.note(it=rnd, res_max=float(np.max(np.abs(x2 - x1))), corr_max=float(np.max(np.abs(c))), capped=capped,
                 ratio=float((x2 - x1) @ (x1 - x0) / ((x1 - x0) @ (x1 - x0))))
        if float(np.max(np.abs(c))) <= STOP and float(np.max(np.abs(x2 - x1))) <= RES:
            done, pt = verify(run, (s2, None))
            if done:
                return pt
            continue
        pt = (s2, x2 + c)


# ---------------------------------------------------------------- verification
def slope(y):
    k = np.arange(len(y), dtype=float)
    return float(np.polyfit(k, np.asarray(y, dtype=float), 1)[0])


def drift_checks(rows, drift_tol):
    """D and NR over verification rows (cycles 1..NV after the end of a method); returns (ok, details)."""
    first = rows[SKIP:SKIP + (NV - SKIP) // 2]
    second = rows[SKIP + (NV - SKIP) // 2:]
    det, ok = {}, True
    for q, tol in drift_tol.items():
        s1 = slope([r[q] for r in first])
        s2 = slope([r[q] for r in second])
        d_ok = abs(s2) <= tol
        nr_ok = abs(s2) <= abs(s1) + 0.1 * tol
        det[q] = (s1, s2, d_ok, nr_ok)
        ok = ok and d_ok and nr_ok
    return ok, det
