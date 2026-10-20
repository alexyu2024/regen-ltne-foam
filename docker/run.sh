#!/bin/bash
# Run one verification level in the OpenFOAM v2512 container (Linux, macOS, Windows via WSL2).
# Usage: docker/run.sh <level> [outdir]      e.g.  docker/run.sh L3      (results in out/<level>)
# The first call builds the image regen-ltne-foam:2512 from docker/Dockerfile. The repository is
# mounted at /work and the run uses your user id, so the results belong to you on the host.
set -euo pipefail
repo=$(cd "$(dirname "$0")/.." && pwd)
level=${1:?usage: docker/run.sh <level> [outdir]}
out=${2:-out/$level}
image=regen-ltne-foam:2512
docker image inspect "$image" > /dev/null 2>&1 || docker build -t "$image" "$repo/docker"
docker run --rm -v "$repo":/work -w /work --user "$(id -u):$(id -g)" -e HOME=/tmp "$image" bash -c '
    source /usr/lib/openfoam/openfoam2512/etc/bashrc
    level=$1 out=$2
    case_dir=$(ls -d cases/"$level"_* 2>/dev/null | head -1)
    if [ -n "$case_dir" ] && [ -x "$case_dir/runLong.sh" ]; then
        # long levels (L5, L6): no time budget locally; then the same steps as .github/workflows/run-case.yml
        "$case_dir/runLong.sh" "$out" 100000 || exit 1
        for f in "$case_dir"/log.*; do
            n=$(wc -l < "$f")
            awk -v n="$n" '"'"'NR<=200 || NR>n-100 {printf "%7d  %s\n", NR, $0}'"'"' "$f" > "$out/$(basename "$f").trimmed"
        done
        "$case_dir/Allclean"
        git config --global --add safe.directory /work
        git status --porcelain --ignored -- "$case_dir" > "$out/log.allclean-check"
        python3 -c "
import os, sys
sys.path.insert(0, \"tools\")
from resultslib import Results
out = sys.argv[1]
lines = open(os.path.join(out, \"log.allclean-check\")).read().splitlines()
r = Results(out)
r.add(\"allclean_leftover\", len(lines), \"log.allclean-check\", f\"1-{len(lines)}\" if lines else \"empty file\")
r.write(mode=\"a\")
" "$out" && python3 tools/verify.py "$level" "$out"
    else
        tools/run_level.sh "$level" "$out"
    fi' _ "$level" "$out"
