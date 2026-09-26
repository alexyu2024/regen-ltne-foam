#!/bin/bash
# Install OpenFOAM v2512 (openfoam.com / OpenCFD, package 2512.0-2) on Ubuntu 22.04/24.04
# from the official apt repository, then build ltneFoam.
# Usage: sudo tools/install.sh      (the build step runs as the invoking user)
set -euo pipefail
FOAM_PKG=openfoam2512-dev
FOAM_VER=2512.0-2

if [ "$(id -u)" -ne 0 ]; then
    echo "run with sudo" >&2
    exit 1
fi

apt-get update
apt-get install -y curl ca-certificates python3
curl -fsSL https://dl.openfoam.com/add-debian-repo.sh | bash
# The .deb files are served through SourceForge mirrors, which sometimes return an
# HTML page instead of the package ("File has unexpected size"); retry.
for attempt in 1 2 3 4; do
    DEBIAN_FRONTEND=noninteractive apt-get install -y -o Acquire::Retries=3 \
        "$FOAM_PKG=$FOAM_VER" && break
    [ "$attempt" -eq 4 ] && { echo "apt-get install failed 4 times" >&2; exit 1; }
    sleep $((attempt * 20))
    apt-get clean
    apt-get update
done

repo="$(cd "$(dirname "$0")/.." && pwd)"
build="source /usr/lib/openfoam/openfoam2512/etc/bashrc && $repo/src/Allwmake"
if [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != root ]; then
    sudo -u "$SUDO_USER" bash -c "$build"
else
    bash -c "$build"
fi
echo
echo "Done. In each new shell: source /usr/lib/openfoam/openfoam2512/etc/bashrc"
