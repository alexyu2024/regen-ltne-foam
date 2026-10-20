#!/bin/bash
# L5D driver: the L5 case unchanged, from t = 0, in 50-cycle chunks until the decay ratio of the slow
# matrix thermal relaxation is stationary (docs/VERIFICATION.md, L5D), then decay.py writes <outdir>.
# Usage: runLong.sh <outdir> [minutes]. Exit 0: done; 3: time budget used, state kept; other: failure.
out=$(realpath -m "${1:?outdir}")   # relative to the caller's directory
cd "${0%/*}" || exit 1
. "${WM_PROJECT_DIR:?}/bin/tools/RunFunctions"
budget=$(( ${2:-330} * 60 ))
t0=$(date +%s)
L5=../L5_regenSlice
chunk=${L5D_CHUNK:-50}

../../src/Allwmake > log.build 2>&1 || { echo "build failed"; exit 1; }
echo "ltneFoam binary: $(command -v ltneFoam)" >> log.build

if [ ! -d run/constant/polyMesh ]; then
    rm -rf run && mkdir -p run/system || exit 1
    cp $L5/system/controlDict $L5/system/fvSchemes $L5/system/fvSolution run/system/
    cp $L5/Allrun.continue run/
    python3 $L5/mkCase.py run > run/log.mkCase || exit 1
    (cd run && restore0Dir > /dev/null && runApplication blockMesh && runApplication topoSet) || exit 1
fi

while :; do
    python3 $L5/results.py summarise run 2400 || exit 1
    dirs=$(ls -d run/postProcessing/ltneDiagnostics/*/ 2>/dev/null | sort -t/ -k4 -g)
    n=$(echo "$dirs" | wc -w)
    [ "$n" -gt 1 ] && echo "$dirs" | head -n $((n - 1)) | xargs rm -rf
    python3 decay.py stop run && break
    if [ $(( $(date +%s) - t0 )) -gt "$budget" ]; then echo "time budget used; state kept"; exit 3; fi
    run/Allrun.continue "$chunk" || exit 1
    grep -q "^End" "$(ls -t run/log.ltneFoam* | head -1)" || { echo "ltneFoam did not finish"; exit 1; }
done
python3 decay.py final . "$out" || exit 1
