#!/usr/bin/env python3
"""L5 post-processing. Definitions: docs/VERIFICATION.md, L5.

  results.py summarise <case>      fold new monitor rows into <case>/per_cycle.csv (run after each chunk);
                                   the raw monitor files of finished chunks can then be deleted
  results.py b6 <case>             exit 0 if B6 holds over the last 5 cycles and >= 40 cycles are done
  results.py final <case> <out>    write the deliverable CSVs and results.csv into <out>
"""
import csv, glob, math, os, re, shutil, sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
P = yaml.safe_load(open(os.path.join(HERE, 'params_L5.yaml')))
F = P['operating_point']['frequency_Hz']
W = 2 * math.pi * F
T = 1.0 / F
AREA = P['layout']['area_m2']
R = P['gas']['R_J_kgK']
FIELDS = ['cycle', 'n_steps', 'Tjoint_mean', 'H_hot', 'H_joint', 'H_cold',
          'dp_amp', 'dp_ph', 'p_hot_amp', 'p_hot_ph', 'mdot_hot_amp', 'mdot_hot_ph',
          'p_cold_amp', 'p_cold_ph', 'mdot_cold_amp', 'mdot_cold_ph',
          'W_hot', 'W_cold', 'Qhot_gas', 'Qhot_solid', 'Qcold_gas', 'Qcold_solid', 'closure',
          'Up_hot_amp', 'Up_hot_ph', 'Up_cold_amp', 'Up_cold_ph']


def monitor_rows(case):
    """All monitor rows (dicts), from every restart, time-ordered, duplicates and t = 0 removed."""
    rows, seen = [], set()
    files = glob.glob(os.path.join(case, 'postProcessing', 'ltneDiagnostics', '*', 'monitors.dat'))
    for path in sorted(files, key=lambda p: float(p.split(os.sep)[-2])):
        cols = open(path).readline()[1:].split()
        for l in open(path):
            if l.startswith('#') or not l.strip():
                continue
            v = dict(zip(cols, map(float, l.split())))
            key = round(v['time'] * F * 1e6)
            if v['time'] <= 0 or key in seen:
                continue
            seen.add(key)
            rows.append(v)
    rows.sort(key=lambda v: v['time'])
    return rows


def fit(rows, key):
    """Mean, first-harmonic amplitude and phase (deg) of x = mean + |x| cos(w t + Ph) over the rows."""
    n = len(rows)
    c = sum(r[key] * complex(math.cos(W * r['time']), -math.sin(W * r['time'])) for r in rows) * 2 / n
    return sum(r[key] for r in rows) / n, abs(c), math.degrees(math.atan2(c.imag, c.real))


def cycle_of(t):
    return math.ceil(t * F - 1e-6)


def summarise_cycle(k, rows):
    for r in rows:
        r['dp'] = r['hotFace_p'] - r['coldFace_p']
    m = lambda key: sum(r[key] for r in rows) / len(rows)
    d = {'cycle': k, 'n_steps': len(rows), 'Tjoint_mean': m('joint_T'),
         'H_hot': m('hotFace_H'), 'H_joint': m('joint_H'), 'H_cold': m('coldFace_H')}
    for key, name in (('dp', 'dp'), ('hotFace_p', 'p_hot'), ('hotFace_mdot', 'mdot_hot'),
                      ('coldFace_p', 'p_cold'), ('coldFace_mdot', 'mdot_cold'), ('hotPiston_Up', 'Up_hot')):
        _, a, ph = fit(rows, key)
        d[name + '_amp'], d[name + '_ph'] = a, ph
    # the cold piston's specified phasor is its volume flow along +z = -(volume swept into the column)
    for r in rows:
        r['coldPiston_Uz'] = -r['coldPiston_Up']
    _, d['Up_cold_amp'], d['Up_cold_ph'] = fit(rows, 'coldPiston_Uz')
    d['W_hot'], d['W_cold'] = m('hotPiston_Wrate'), m('coldPiston_Wrate')
    d['Qhot_gas'], d['Qhot_solid'] = m('hot_hx_Qgas'), m('hot_hx_Qsolid')
    d['Qcold_gas'], d['Qcold_solid'] = m('cold_hx_Qgas'), m('cold_hx_Qsolid')
    d['closure'] = d['W_hot'] + d['W_cold'] + d['Qhot_gas'] + d['Qhot_solid'] + d['Qcold_gas'] + d['Qcold_solid']
    return d


def load_per_cycle(case):
    path = os.path.join(case, 'per_cycle.csv')
    if not os.path.exists(path):
        return []
    return [{k: float(v) for k, v in r.items()} for r in csv.DictReader(open(path))]


def summarise(case, steps_per_cycle):
    have = {int(r['cycle']) for r in load_per_cycle(case)}
    rows = monitor_rows(case)
    by = {}
    for r in rows:
        by.setdefault(cycle_of(r['time']), []).append(r)
    new = [summarise_cycle(k, v) for k, v in sorted(by.items())
           if k not in have and len(v) == steps_per_cycle]
    path = os.path.join(case, 'per_cycle.csv')
    exists = os.path.exists(path)
    with open(path, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists:
            w.writeheader()
        for d in new:
            w.writerow({k: (repr(d[k]) if isinstance(d[k], float) else d[k]) for k in FIELDS})
    return len(new)


def b6(pc):
    """(B6a, B6b) over the last 5 cycles, or None if fewer than 6 cycles."""
    if len(pc) < 6:
        return None
    last = pc[-6:]
    a = max(abs(last[i]['Tjoint_mean'] - last[i - 1]['Tjoint_mean']) for i in range(1, 6))
    b = max(abs(last[i]['H_joint'] - last[i - 1]['H_joint']) / abs(last[i]['H_joint']) for i in range(1, 6))
    return a, b


def latest_mean_field(case, name):
    times = [d for d in os.listdir(case) if re.fullmatch(r'[0-9.e+-]+', d) and os.path.exists(os.path.join(case, d, name))]
    if not times:
        return None, None
    t = max(times, key=float)
    s = open(os.path.join(case, t, name)).read()
    body = s.split('internalField', 1)[1]
    n = int(re.search(r'nonuniform List<scalar>\s*(\d+)', body).group(1))
    vals = body.split('(', 1)[1].split(')', 1)[0].split()
    return t, [float(v) for v in vals[:n]]


def final(case, out):
    from resultslib import Results, last_match
    os.makedirs(out, exist_ok=True)
    pc = load_per_cycle(case)
    shutil.copy(os.path.join(case, 'per_cycle.csv'), os.path.join(out, 'per_cycle.csv'))
    r = Results(out)
    r.add('cycles_run', len(pc), 'per_cycle.csv', f'2-{len(pc) + 1}')
    last = pc[-1]
    src_last = f'{len(pc) + 1} (cycle {int(last["cycle"])})'

    # piston check (last cycle)
    dr = P['drive']
    with open(os.path.join(out, 'piston_check.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['piston', 'spec_amp_m3_s', 'spec_ph_deg', 'realised_amp_m3_s', 'realised_ph_deg', 'amp_rel_err', 'ph_err_deg'])
        for name, key in (('hot', 'hot_piston'), ('cold', 'cold_piston')):
            sa, sp = dr[key]['U_amp_m3_s'], dr[key]['U_phase_deg']
            ra, rp = last[f'Up_{name}_amp'], last[f'Up_{name}_ph']
            ea, ep = abs(ra / sa - 1), abs((rp - sp + 180) % 360 - 180)
            w.writerow([name, sa, sp, ra, rp, ea, ep])
            r.add(f'piston_{name}_amp_err', ea, 'piston_check.csv', 2 if name == 'hot' else 3)
            r.add(f'piston_{name}_phase_err_deg', ep, 'piston_check.csv', 2 if name == 'hot' else 3)

    r.add('B5_closure_W', abs(last['closure']), 'per_cycle.csv', src_last)
    b = b6(pc)
    r.add('B6a_dTjoint_K', None if b is None else b[0], 'per_cycle.csv', f'{len(pc) - 4}-{len(pc) + 1}')
    r.add('B6b_dH_rel', None if b is None else b[1], 'per_cycle.csv', f'{len(pc) - 4}-{len(pc) + 1}')
    for key, col in (('hot_p_amp_Pa', 'p_hot_amp'), ('hot_p_ph_deg', 'p_hot_ph'), ('hot_mdot_amp', 'mdot_hot_amp'),
                     ('hot_mdot_ph_deg', 'mdot_hot_ph'), ('cold_p_amp_Pa', 'p_cold_amp'), ('cold_p_ph_deg', 'p_cold_ph'),
                     ('cold_mdot_amp', 'mdot_cold_amp'), ('cold_mdot_ph_deg', 'mdot_cold_ph'), ('dp_amp_Pa', 'dp_amp'),
                     ('H_hot_W', 'H_hot'), ('H_joint_W', 'H_joint'), ('H_cold_W', 'H_cold'), ('Tjoint_mean_K', 'Tjoint_mean')):
        r.add(key, last[col], 'per_cycle.csv', src_last)

    # final cycle, every step, at both faces
    rows = [v for v in monitor_rows(case) if cycle_of(v['time']) == int(last['cycle'])]
    with open(os.path.join(out, 'final_cycle_faces.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['t', 'p_hot', 'u_sup_hot', 'mdot_hot', 'Tg_hot', 'p_cold', 'u_sup_cold', 'mdot_cold', 'Tg_cold'])
        for v in rows:
            row = [repr(v['time'])]
            for fz in ('hotFace', 'coldFace'):
                rho = v[fz + '_p'] / (R * v[fz + '_T'])
                row += [v[fz + '_p'], v[fz + '_mdot'] / (rho * AREA), v[fz + '_mdot'], v[fz + '_T']]
            w.writerow(row)

    # cycle-mean profiles at the 121 nodes
    zc = [float(z) for z in open(os.path.join(case, 'cellCentresZ.txt'))]
    tg_t, tg = latest_mean_field(case, 'TMean')
    ts_t, ts = latest_mean_field(case, 'TsMean')
    nodes = [z for z, _ in P['initial_conditions']['T_matrix_profile_z_m__T_K']]

    def at(vals, z):
        for i in range(len(zc) - 1):
            if zc[i] <= z <= zc[i + 1]:
                return vals[i] + (vals[i + 1] - vals[i]) * (z - zc[i]) / (zc[i + 1] - zc[i])
    with open(os.path.join(out, 'profiles.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['z_m', 'Tg_mean_K', 'Ts_mean_K'])
        for z in nodes:
            w.writerow([z, at(tg, z) if tg else 'not read', at(ts, z) if ts else 'not read'])

    # sensitivity run (dt/2, matrix dx/2), last cycle against the base last cycle
    sens = os.path.join(case, 'sens')
    spc = load_per_cycle(sens) if os.path.isdir(sens) else []
    if spc:
        shutil.copy(os.path.join(sens, 'per_cycle.csv'), os.path.join(out, 'per_cycle_sensitivity.csv'))
        s = spc[-1]
        amps = ['p_hot_amp', 'mdot_hot_amp', 'p_cold_amp', 'mdot_cold_amp', 'dp_amp']
        phs = ['p_hot_ph', 'mdot_hot_ph', 'p_cold_ph', 'mdot_cold_ph']
        amax = max(abs(s[a] / last[a] - 1) for a in amps)
        pmax = max(abs((s[p] - last[p] + 180) % 360 - 180) for p in phs)
        src = f'per_cycle_sensitivity.csv:{len(spc) + 1} vs per_cycle.csv:{len(pc) + 1}'
        r.add('sens_amp_max_rel', amax, 'per_cycle_sensitivity.csv', src)
        r.add('sens_phase_max_deg', pmax, 'per_cycle_sensitivity.csv', src)
        r.add('sens_cycles', len(spc), 'per_cycle_sensitivity.csv', f'2-{len(spc) + 1}')
    else:
        r.add('sens_amp_max_rel', None, 'per_cycle_sensitivity.csv', None)
        r.add('sens_phase_max_deg', None, 'per_cycle_sensitivity.csv', None)

    # crash patterns over all logs (base and sensitivity)
    bad = re.compile(r'FOAM FATAL|\bnan\b|\binf\b|Floating point exception|Segmentation fault', re.IGNORECASE)
    hits = []
    for path in sorted(glob.glob(os.path.join(case, 'log.*')) + glob.glob(os.path.join(sens, 'log.*'))):
        for i, l in enumerate(open(path, errors='replace')):
            if bad.search(l):
                hits.append(f'{os.path.relpath(path, case)}:{i + 1}')
    r.add('crash_count', len(hits), 'log.*', hits if hits else 'all lines of all logs (base and sens)')
    r.write()


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
    mode, case = sys.argv[1], sys.argv[2]
    if mode == 'summarise':
        n = summarise(case, int(sys.argv[3]) if len(sys.argv) > 3 else 2400)
        print(f'summarise: {n} new cycles')
    elif mode == 'b6':
        pc = load_per_cycle(case)
        b = b6(pc)
        ok = b is not None and len(pc) >= 40 and b[0] < 0.1 and b[1] < 0.02
        print(f'b6: cycles {len(pc)}, B6a {b[0] if b else None}, B6b {b[1] if b else None}, holds {ok}')
        sys.exit(0 if ok else 1)
    elif mode == 'final':
        final(case, sys.argv[3])
