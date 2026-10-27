#!/bin/bash
# LRG driver (docs/VERIFICATION.md, LRG): real- against ideal-gas helium on the L5 slice, from the accepted L5P
# ideal-gas reference. Inputs pinned in source.env. Usage: runLong.sh <outdir> [minutes]
#   1. fetch the L5P tools (pss/), the reference tables and json, and the restart point N_R, at pinned commits
#   2. ideal gas N_R -> N_REF, checked against the reference tables (LRG.1)
#   3. switch the gas model only (mkCase.py --gas real files; rho removed; equal initial mean pressure)
#   4. real gas in 100-cycle chunks; Amendment A2 test from N_REF + 400 after every chunk; cap N_REF + 6000
#   5. lrg.py final
# Restart across jobs: the run directories are kept. Exit 0: done (accepted, or the cap reached: then LRG.4 is
# FAIL in the verified table); 3: time budget used, state kept; other: failure.
out=$(realpath -m "${1:?outdir}")   # relative to the caller's directory
cd "${0%/*}" || exit 1
. "${WM_PROJECT_DIR:?}/bin/tools/RunFunctions"
. ./source.env
[ -n "${LRG_SOURCE_ENV:-}" ] && . "$LRG_SOURCE_ENV"   # dry runs: another pinned set
budget=$(( ${2:-330} * 60 ))
t0=$(date +%s)
chunk=${LRG_CHUNK:-100}
first=${LRG_FIRST_TEST:-400}
[ -f A3.env ] && . ./A3.env            # Amendment A3: committed only if the run continues past N_REF + 6000
cap=${LRG_CAP:-6000}
L5=../L5_regenSlice
for v in L5P_ACCEPT_SHA L5P_REF_JSON L5P_RESTART_SHA N_R N_REF; do
    [ -n "${!v}" ] || { echo "source.env: $v is not set (the L5P reference has not been pinned)"; exit 1; }
done

../../src/Allwmake > log.build 2>&1 || { echo "build failed"; exit 1; }
echo "ltneFoam binary: $(command -v ltneFoam)" >> log.build

# 1. L5P inputs at the pinned commits
top=$(git rev-parse --show-toplevel)
git -C "$top" cat-file -e "$L5P_ACCEPT_SHA^{commit}" 2>/dev/null && git -C "$top" cat-file -e "$L5P_RESTART_SHA^{commit}" 2>/dev/null \
    || git -C "$top" fetch -q --no-tags origin "$L5P_ACCEPT_SHA" "$L5P_RESTART_SHA" || { echo "cannot fetch the L5P commits"; exit 1; }
rm -rf pss && mkdir -p l5p_ref
git -C "$top" archive "$L5P_ACCEPT_SHA" cases/L5P_periodicState/pss | tar -x --strip-components=2 -C . || exit 1
for f in per_cycle.csv cycles.csv; do
    git -C "$top" show "$L5P_ACCEPT_SHA:results/L5P/natural/$f" > l5p_ref/$f || exit 1
done
git -C "$top" show "$L5P_ACCEPT_SHA:$L5P_REF_JSON" > l5p_ref/reference.json || exit 1
# LRG_ALLOW_UNACCEPTED=1 is for dry runs of this script only (no LRG result may come from such a run)
if [ "${LRG_ALLOW_UNACCEPTED:-0}" != 1 ]; then
    python3 -c "import json,sys; j=json.load(open('l5p_ref/reference.json')); sys.exit(0 if j['accepted'] and j['ref_cycles']==$N_REF else 1)" \
        || { echo "the pinned L5P reference is not accepted at N_REF = $N_REF"; exit 1; }
fi

# 2. ideal gas N_R -> N_REF
if [ ! -f restartcheck.json ]; then
    if [ ! -d run_ideal/constant ]; then
        git -C "$top" show "$L5P_RESTART_SHA:results/L5P/natural/restart/state.tgz" > l5p_ref/state_Nr.tgz || exit 1
        [ "$(git -C "$top" show "$L5P_RESTART_SHA:results/L5P/natural/restart/cycle")" = "$N_R" ] || { echo "restart point is not cycle $N_R"; exit 1; }
        rm -rf run_ideal && mkdir run_ideal && tar xzf l5p_ref/state_Nr.tgz -C run_ideal || exit 1
        rm -f run_ideal/per_cycle.csv run_ideal/cycles.csv      # tables of this run start at N_R + 1
        rm -f run_ideal/log.*                                    # the reference's own logs stay in the L5P record
    fi
    cp $L5/Allrun.continue run_ideal/   # every job: the run-case state archive leaves Allrun.continue out
    while :; do
        python3 $L5/results.py summarise run_ideal 2400 > /dev/null || exit 1
        python3 lrg.py extract run_ideal || exit 1
        k=$(python3 -c "import csv; print(max([int(r['cycle']) for r in csv.DictReader(open('run_ideal/cycles.csv'))] or [$N_R]))" 2>/dev/null || echo $N_R)
        [ "$k" -ge "$N_REF" ] && break
        (cd run_ideal && ./Allrun.continue $(( N_REF - k < chunk ? N_REF - k : chunk ))) || exit 1
        grep -q "^End" "$(ls -t run_ideal/log.ltneFoam* | head -1)" || { echo "ltneFoam (ideal) did not finish"; exit 1; }
    done
    python3 lrg.py restartcheck run_ideal l5p_ref $N_R $N_REF restartcheck.json || exit 1
fi
python3 -c "import json,sys; sys.exit(0 if json.load(open('restartcheck.json'))['restart_check_rel'] <= 1e-9 else 1)" \
    || { echo "LRG.1 FAIL: the ideal-gas continuation does not reproduce the L5P reference"; exit 1; }

# 3. switch
[ -f run_real/switch.json ] || python3 lrg.py switch run_ideal run_real $N_REF || exit 1

# 4. real gas
cp $L5/Allrun.continue run_real/   # every job: the run-case state archive leaves Allrun.continue out
while :; do
    python3 $L5/results.py summarise run_real 2400 > /dev/null || exit 1
    python3 lrg.py extract run_real || exit 1
    dirs=$(ls -d run_real/postProcessing/ltneDiagnostics/*/ 2>/dev/null | sort -t/ -k4 -g)
    n=$(echo "$dirs" | wc -w)
    [ "$n" -gt 1 ] && echo "$dirs" | head -n $((n - 1)) | xargs rm -rf
    k=$(python3 -c "import csv; print(max([int(r['cycle']) for r in csv.DictReader(open('run_real/cycles.csv'))] or [$N_REF]))" 2>/dev/null || echo $N_REF)
    if [ $(( k - N_REF )) -ge "$first" ]; then
        python3 lrg.py accept run_real accept && break
    fi
    if [ $(( k - N_REF )) -ge "$cap" ]; then
        echo "LRG.4: cap N_REF + $cap reached without acceptance (recorded as FAIL by verify)"
        break   # the acceptance json of this chunk is already written
    fi
    if [ $(( $(date +%s) - t0 )) -gt "$budget" ]; then echo "time budget used at cycle $k; state kept"; exit 3; fi
    (cd run_real && ./Allrun.continue "$chunk") || exit 1
    grep -q "^End" "$(ls -t run_real/log.ltneFoam* | head -1)" || { echo "ltneFoam (real gas) did not finish"; exit 1; }
done

# 5. deliverables
python3 lrg.py final . "$out" || exit 1
exit 0
