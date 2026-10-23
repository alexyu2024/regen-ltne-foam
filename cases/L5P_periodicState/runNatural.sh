#!/bin/bash
# L5P natural reference: the L5 case unchanged, from t = 0, natural cycle-by-cycle marching, in chunks, with one
# time directory per cycle boundary folded into per-cycle tables (pss/cycles.py, ../L5_regenSlice/results.py).
#
# Usage: runNatural.sh <outdir> <cycles> [chunk]
#   Runs (or continues) run_natural/ until <cycles> cycles are done. After each chunk it writes the tables to
#   <outdir> and calls $L5P_HOOK <cycles done> if that is set (used to commit the tables). Every
#   $L5P_RESTART_EVERY cycles (default 200) it writes the restart point <outdir>/restart/state.tgz.
#   If run_natural/ is missing and <outdir>/restart/state.tgz exists, it continues from there.
# Exit 0: done; other: failure.
out=$(realpath -m "${1:?outdir}")
target=${2:?cycles}
chunk=${3:-100}
every=${L5P_RESTART_EVERY:-200}
cd "${0%/*}" || exit 1
here=$(pwd)
. "${WM_PROJECT_DIR:?}/bin/tools/RunFunctions"
L5=../L5_regenSlice
run=run_natural
mkdir -p "$out/restart"

../../src/Allwmake > log.build 2>&1 || { echo "build failed"; exit 1; }
echo "ltneFoam binary: $(command -v ltneFoam)" >> log.build

if [ ! -d $run/constant/polyMesh ]; then
    if [ -f "$out/restart/state.tgz" ]; then
        rm -rf $run && mkdir $run && tar xzf "$out/restart/state.tgz" -C $run || exit 1
        echo "continuing from $out/restart/state.tgz (cycle $(cat $run/restart_cycle))"
    else
        rm -rf $run && mkdir -p $run/system || exit 1
        cp $L5/system/controlDict $L5/system/fvSchemes $L5/system/fvSolution $run/system/
        python3 $L5/mkCase.py $run > $run/log.mkCase || exit 1
        (cd $run && restore0Dir > /dev/null && runApplication blockMesh && runApplication topoSet) || exit 1
        # one time directory per cycle boundary (2400 steps), none purged here: pss/cycles.py removes the
        # folded ones. timePrecision 17 keeps restart time names exact (results/L5D/README.md).
        sed -i 's/^writeInterval .*/writeInterval   2400;/; s/^purgeWrite .*/purgeWrite      0;/;
                s/^timePrecision .*/timePrecision   17;/' $run/system/controlDict
    fi
fi

done_cycles() { python3 - "$run" <<'PY'
import csv, os, sys
p = os.path.join(sys.argv[1], 'per_cycle.csv')
print(sum(1 for _ in csv.DictReader(open(p))) if os.path.exists(p) else 0)
PY
}

while :; do
    python3 $L5/results.py summarise $run 2400 || exit 1
    python3 -m pss.cycles extract $run --keep-states || exit 1
    # monitor files of folded chunks are no longer needed
    dirs=$(ls -d $run/postProcessing/ltneDiagnostics/*/ 2>/dev/null | sort -t/ -k4 -g)
    n=$(echo "$dirs" | wc -w)
    [ "$n" -gt 1 ] && echo "$dirs" | head -n $((n - 1)) | xargs rm -rf
    k=$(done_cycles)
    cp $run/per_cycle.csv $run/cycles.csv "$out/"
    for f in log.build $run/log.*; do
        [ -f "$f" ] || continue
        m=$(wc -l < "$f")
        awk -v n="$m" 'NR<=200 || NR>n-100 {printf "%7d  %s\n", NR, $0}' "$f" > "$out/$(basename "$f").trimmed"
    done
    if [ "$k" -gt 0 ] && [ $((k % every)) -eq 0 ] && [ "$(cat $out/restart/cycle 2>/dev/null)" != "$k" ]; then
        echo "$k" > $run/restart_cycle
        latest=$(cd $run && foamListTimes -latestTime | tail -1)
        tar czf "$out/restart/state.tgz.tmp" -C $run constant system 0.orig "$latest" per_cycle.csv cycles.csv \
            cellCentresZ.txt restart_cycle $(cd $run && ls log.* 2>/dev/null) || exit 1
        mv "$out/restart/state.tgz.tmp" "$out/restart/state.tgz"
        echo "$k" > "$out/restart/cycle"
    fi
    [ -n "${L5P_HOOK:-}" ] && $L5P_HOOK "$k"
    [ "$k" -ge "$target" ] && break
    n=$(( target - k < chunk ? target - k : chunk ))
    (cd $run && cp "$here/$L5/Allrun.continue" . && ./Allrun.continue "$n") || exit 1
    grep -q "^End" "$(ls -t $run/log.ltneFoam* | head -1)" || { echo "ltneFoam did not finish"; exit 1; }
done
