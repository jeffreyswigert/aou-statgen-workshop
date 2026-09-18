#!/usr/bin/env bash
# common.sh -- shared setup, sourced by every lab script. Three jobs:
#
# 1. "set -euo pipefail" makes bash strict: stop at the FIRST failing command
#    (-e), treat an unset variable as an error instead of empty text (-u), and
#    let a failure inside a pipeline fail the whole pipeline (pipefail).
#    Without this, a script can sail past an error and produce plausible
#    nonsense downstream -- the most expensive kind of bug in this field.
set -euo pipefail

# 2. cd to the package root, so every script works no matter where you ran it
#    from, and all paths in the scripts can be written relative to the root.
cd "$(dirname "${BASH_SOURCE[0]}")/.."

# 3. Load the settings. WORKSHOP_CONFIG lets you point at a different config
#    (the real-data variant does: export WORKSHOP_CONFIG=config.aou.sh).
source "${WORKSHOP_CONFIG:-config.sh}"

mkdir -p results

# p2 = "plink2 with our compute settings attached". Every lab script calls p2
# so that threads and memory are set once, consistently, instead of being
# copy-pasted (and eventually mistyped) into every command. "$@" forwards
# whatever arguments you gave p2 straight to plink2.
p2() { "$PLINK2" --threads "$THREADS" --memory "$MEMORY_MB" "$@"; }
