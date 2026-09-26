#!/bin/bash
# Run one level's case from scratch and check its bars.
# Usage: tools/run_level.sh <level> <outdir>     e.g. tools/run_level.sh L0 results/L0
# Requires a sourced OpenFOAM v2512 environment. Exit status is non-zero on any miss.
set -u
cd "$(dirname "$0")/.." || exit 1
level=$1
out=$2
case=$(ls -d cases/"${level}"_* | head -1)
[ -d "$case" ] || { echo "no case for $level"; exit 1; }

rm -rf "$out" && mkdir -p "$out"
"$case"/Allclean > /dev/null 2>&1
"$case"/Allrun
echo "Allrun exit status: $?" > "$out/log.allrun-status"
python3 "$case"/results.py "$out"

# Allclean must restore the checked-in state
"$case"/Allclean
git status --porcelain --ignored -- "$case" > "$out/log.allclean-check"
python3 - "$out" <<'PY'
import os, sys
sys.path.insert(0, 'tools')
from resultslib import Results
out = sys.argv[1]
lines = open(os.path.join(out, 'log.allclean-check')).read().splitlines()
r = Results(out)
r.add('allclean_leftover', len(lines), 'log.allclean-check', f'1-{len(lines)}' if lines else 'empty file')
r.write(mode='a')
PY

python3 tools/verify.py "$level" "$out"
status=$?

# Keep the stored results small: gzip every file over 1 MB (line numbers in the
# sources refer to the uncompressed text)
find "$out" -type f -size +1M ! -name '*.gz' -exec gzip -9 {} \;
exit $status
