#!/usr/bin/env bash
# 08_pgi_eda.sh (session 2) -- explore the PGI before modeling with it:
# summary table, group comparisons, and three figures. Read pgi_eda.py --
# that is where the analysis lives; this wrapper only checks the environment.
source "$(dirname "$0")/common.sh"

[[ -s results/pgi.sscore ]] || { echo 'No PGI found. Run: bash scripts/07_score_pgi.sh' >&2; exit 1; }

# Session 2 needs numpy and matplotlib (both preinstalled on AoU Workbench
# VMs). Check now, with a clear message, rather than mid-analysis.
python3 -c 'import numpy, matplotlib' 2>/dev/null || {
  echo 'Session 2 needs python3 with numpy and matplotlib (preinstalled on the AoU VM).' >&2; exit 1; }

python3 scripts/pgi_eda.py
