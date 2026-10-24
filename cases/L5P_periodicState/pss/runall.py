"""Run the registered L5P methods concurrently on a fixed core budget, score each as it ends.

  python3 -m pss.runall <start run> <work> <out> [names...]     (default: all seven)

A method costs as many cores as it runs cycles at the same time: Newton-Picard p runs p + 1 (Phi and p
finite-difference products), BRR and Graves-Morris run one. Methods start in the order given whenever enough cores
are free (L5P_CORES, default 4). Each one is scored against <out>/reference.json when it ends, and $L5P_METHOD_HOOK
<name> is called if set. The cycle counts do not depend on the scheduling; only the wall time does.
"""
import os, subprocess, sys, time

ORDER = ['np3', 'np2', 'np1', 'brr3', 'brr6', 'gm0', 'gm3']


def cost(name):
    return int(name[2:]) + 1 if name.startswith('np') else 1


def main(start_run, work, out, names):
    cores = int(os.environ.get('L5P_CORES', '4'))
    todo, running, failed = list(names), {}, []
    while todo or running:
        free = cores - sum(cost(n) for n in running)
        for n in list(todo):
            if cost(n) <= free:
                env = dict(os.environ, L5P_WORKERS=str(cost(n)))
                log = open(os.path.join(out, f'{n}_run.log'), 'w')
                running[n] = subprocess.Popen([sys.executable, '-m', 'pss.study', 'method', n, start_run, work, out],
                                              stdout=log, stderr=subprocess.STDOUT, env=env)
                print(f'{time.strftime("%H:%M:%S")} start {n} ({cost(n)} cores)', flush=True)
                todo.remove(n)
                free -= cost(n)
        for n, p in list(running.items()):
            if p.poll() is None:
                continue
            del running[n]
            rc = p.returncode
            if rc == 0:
                rc = subprocess.call([sys.executable, '-m', 'pss.study', 'score', out, n])
            print(f'{time.strftime("%H:%M:%S")} end {n} rc={rc}', flush=True)
            if rc:
                failed.append(n)
            if os.environ.get('L5P_METHOD_HOOK'):
                subprocess.call([os.environ['L5P_METHOD_HOOK'], n])
        time.sleep(10)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:] or ORDER))
