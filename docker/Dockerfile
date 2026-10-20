FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive FOAM_DIR=/usr/lib/openfoam/openfoam2512
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates gnupg python3 python3-yaml git procps gzip time && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://dl.openfoam.com/add-debian-repo.sh | bash && apt-get update && apt-get install -y --no-install-recommends openfoam2512-dev=2512.0-2 && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV WM_PROJECT_DIR=/usr/lib/openfoam/openfoam2512
SHELL ["/bin/bash", "-lc"]
