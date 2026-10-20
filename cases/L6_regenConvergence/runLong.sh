#!/bin/bash
# L6 driver (used by .github/workflows/run-case.yml, also runnable locally).
# Usage: runLong.sh <outdir> [minutes]
#   Runs the four L6 variants of the L5 case in parallel, one core each (docs/VERIFICATION.md, L6):
#   G1/G2/G3 = every block's cells x 0.5/1/2 at the L5 dt, T2 = G2 at dt/2. Each proceeds in 10-cycle
#   chunks until the periodic criterion holds (or 300 cycles), and continues from its latest time if the
#   case has been run before (restart across jobs). Then l6.py writes the deliverables into <outdir>.
#   Exit 0: done; 3: time budget used, state kept for the next job; other: failure.
out=$(realpath -m "${1:?outdir}")   # relative to the caller's directory
cd "${0%/*}" || exit 1
. "${WM_PROJECT_DIR:?}/bin/tools/RunFunctions"
budget=$(( ${2:-330} * 60 ))
t0=$(date +%s)
L5=../L5_regenSlice

../../src/Allwmake > log.build 2>&1 || { echo "build failed"; exit 1; }
echo "ltneFoam binary: $(command -v ltneFoam)" >> log.build

setup() {  # <run> <grid factor> <steps per cycle>
    local run=$1 grid=$2 steps=$3
    rm -rf "$run" && mkdir -p "$run/system" || return 1
    cp $L5/system/controlDict $L5/system/fvSchemes $L5/system/fvSolution "$run/system/"
    cp $L5/Allrun.continue "$run/"
    python3 $L5/mkCase.py "$run" --grid-refine "$grid" > "$run/log.mkCase" || return 1
    sed -i "s/^deltaT .*/deltaT          $(python3 -c "print(repr(1/(23.0*$steps)))");/" "$run/system/controlDict"
    sed -i "s/^writeInterval .*/writeInterval   $((10 * steps));/" "$run/system/controlDict"
    (cd "$run" && restore0Dir > /dev/null && runApplication blockMesh && runApplication topoSet)
}

prune() {  # keep only the newest raw monitor chunk once it is summarised
    local dirs n
    dirs=$(ls -d "$1"/postProcessing/ltneDiagnostics/*/ 2>/dev/null | sort -t/ -k4 -g)
    n=$(echo "$dirs" | wc -w)
    [ "$n" -gt 1 ] && echo "$dirs" | head -n $((n - 1)) | xargs rm -rf
}

variant() {  # <run> <grid factor> <steps per cycle>
    local run=$1 grid=$2 steps=$3 rc
    [ -f "$run/periodic.txt" ] || [ -f "$run/capped" ] && return 0
    [ -d "$run/constant/polyMesh" ] || setup "$run" "$grid" "$steps" || return 1
    while :; do
        python3 l6.py summarise "$run" "$steps" || return 1
        prune "$run"
        python3 l6.py periodic "$run"; rc=$?
        [ $rc -eq 0 ] && return 0
        [ $rc -eq 2 ] && { touch "$run/capped"; return 0; }
        [ $(( $(date +%s) - t0 )) -gt "$budget" ] && return 3
        "$run/Allrun.continue" 10 || return 1
        grep -q "^End" "$(ls -t "$run"/log.ltneFoam* | head -1)" || { echo "$run: ltneFoam did not finish"; return 1; }
    done
}

variant G1 0.5 2400 > log.G1 2>&1 & p1=$!
variant G2 1 2400 > log.G2 2>&1 & p2=$!
variant G3 2 2400 > log.G3 2>&1 & p3=$!
variant T2 1 4800 > log.T2 2>&1 & p4=$!
status=0
for p in $p1 $p2 $p3 $p4; do
    wait $p; rc=$?
    [ $rc -eq 3 ] && [ $status -eq 0 ] && status=3
    [ $rc -ne 0 ] && [ $rc -ne 3 ] && status=1
done
tail -n 3 log.G1 log.G2 log.G3 log.T2
if [ $status -eq 3 ]; then echo "time budget used; state kept for the next job"; exit 3; fi
[ $status -eq 0 ] || exit 1

python3 l6.py final . "$out" || exit 1
exit 0
