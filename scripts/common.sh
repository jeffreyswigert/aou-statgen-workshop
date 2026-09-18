#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source "${WORKSHOP_CONFIG:-config.sh}"
mkdir -p results
p2() { "$PLINK2" --threads "$THREADS" --memory "$MEMORY_MB" "$@"; }
