#!/bin/bash
# L5 driver (used by .github/workflows/run-case.yml, also runnable locally).
# Usage: runLong.sh <outdir> [minutes]
#   Continues from the latest time if the case has been run before (restart across
#   jobs), otherwise starts from the initial state. Runs 10-cycle chunks until B6
#   holds (and >= 40 cycles), then the sensitivity run (dt/2, matrix dx/2, 5 cycles)
#   and the final post-processing. Exit 0: done; 3: time budget used, state kept
#   for the next job; other: failure.
out=$(realpath -m "${1:?outdir}")   # relative to the caller's directory
cd "${0%/*}" || exit 1
. "${WM_PROJECT_DIR:?}/bin/tools/RunFunctions"
budget=$(( ${2:-330} * 60 ))
t0=$(date +%s)

latest() { foamListTimes -latestTime 2>/dev/null | tail -1; }
elapsed() { echo $(( $(date +%s) - t0 )); }

# keep only the newest raw monitor chunk once it is summarised
prune() {
    dirs=$(ls -d postProcessing/ltneDiagnostics/*/ 2>/dev/null | sort -t/ -k3 -g)
    n=$(echo "$dirs" | wc -w)
    [ "$n" -gt 1 ] && echo "$dirs" | head -n $((n - 1)) | xargs rm -rf
}

if [ -z "$(latest)" ] || [ "$(latest)" = "0" ]; then
    ./Allrun 10 || exit 1
fi

while :; do
    python3 results.py summarise . 2400 || exit 1
    prune
    python3 results.py b6 . && break
    if [ "$(elapsed)" -gt "$budget" ]; then
        echo "time budget used at t = $(latest); state kept for the next job"
        exit 3
    fi
    ./Allrun.continue 10 || exit 1
    grep -q "^End" "$(ls -t log.ltneFoam* | head -1)" || { echo "ltneFoam did not finish"; exit 1; }
done

# ---- sensitivity: restart the converged state with dt/2 and matrix dx/2, 5 cycles ----
if [ ! -f sens/per_cycle.csv ] || [ "$(wc -l < sens/per_cycle.csv)" -lt 6 ]; then
    tr=$(latest)
    rm -rf sens && mkdir -p sens/system
    cp system/controlDict system/fvSchemes system/fvSolution sens/system/
    python3 mkCase.py sens --matrix-refine 2 > sens/log.mkCase || exit 1
    (
        cd sens || exit 1
        dtf=$(python3 -c "print(repr(1/(23.0*4800)))")
        runApplication blockMesh
        runApplication topoSet
        # move the fine mesh to the piston positions at tr (pistonLinear, same formula)
        sed -i "s/^deltaT .*/deltaT          $dtf;/; s/^startFrom .*/startFrom       startTime;/" system/controlDict
        sed -i "s/^startTime .*/startTime       $(python3 -c "print(repr($tr - $dtf))");/; s/^endTime .*/endTime         $tr;/" system/controlDict
        sed -i "s/^writeInterval .*/writeInterval   1;/" system/controlDict
        runApplication moveDynamicMesh
        # the moved mesh is written under this case's own time name (timePrecision
        # may give fewer digits than the base run's name for the same time)
        ts=$(foamListTimes -latestTime -noZero 2>/dev/null | tail -1)
        [ -n "$ts" ] && [ -d "$ts/polyMesh" ] || { echo "moved mesh not written at $tr"; exit 1; }
        sed -i "s/^startTime .*/startTime       $ts;/" system/controlDict
        cp 0.orig/* "$ts"/
        runApplication mapFields .. -consistent -sourceTime "$tr"
        end=$(python3 -c "print(repr((round($tr*23) + 5)/23.0))")
        sed -i "s/^endTime .*/endTime         $end;/; s/^writeInterval .*/writeInterval   24000;/" system/controlDict
        runApplication ltneFoam
    ) || exit 1
    python3 results.py summarise sens 4800 || exit 1
fi

python3 results.py final . "$out" || exit 1
exit 0
