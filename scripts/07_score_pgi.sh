#!/usr/bin/env bash
# 07_score_pgi.sh (session 2) -- build a polygenic index with PLINK.
#
# A PGI is a weighted sum: for each person, over the variants we have weights
# for,   PGI_i = sum_j  weight_j * (count of effect-allele copies).
# The weights come from data/pgi_weights.txt, which plays the role of a
# published external discovery GWAS (real life: the PGI Repository). We score
# the QC'd genotypes from session 1.
# After running, open results/pgi.sscore and results/pgi.log.
source "$(dirname "$0")/common.sh"

# Session 2 builds on session 1's QC output. If it is not there, say exactly
# what to do rather than failing mysteriously three lines later.
[[ -s results/qc.pgen ]] || { echo 'No QC output found. Run session 1 first: bash scripts/02_qc.sh' >&2; exit 1; }

# The weights and group files ship with the repo; regenerate only if missing.
[[ -s data/pgi_weights.txt && -s data/groups.tsv ]] || python3 scripts/make_session2.py

# The scoring command. Flag by flag:
#   --score FILE 1 3 5   read weights from FILE, taking the variant ID from
#                        column 1, the EFFECT ALLELE from column 3, and the
#                        weight from column 5. Naming the effect allele is
#                        what makes allele orientation a non-issue: ~500 of
#                        our weight rows name the other allele (sign flipped)
#                        and score identically. Count the columns yourself:
#                        head -n 2 data/pgi_weights.txt
#   header               the first line is column names, not a variant
#   cols=+scoresums      also report the raw SUM (SCORE1_SUM), not only the
#                        per-allele average -- sums are easier to reason about
#   list-variants        write results/pgi.sscore.vars: exactly which
#                        variants entered the score. Provenance for free.
p2 --pfile results/qc \
  --score data/pgi_weights.txt 1 3 5 header cols=+scoresums list-variants \
  --out results/pgi

# Read the log's match report -- these numbers ARE the coverage story:
# of 2,001 weight rows, ~1,922 matched (the rest: variants QC removed, plus
# 15 rsIDs our data never had -- a different ID scheme, a classic real trap).
grep -E 'variants processed|skipped' results/pgi.log || true

printf 'Scored. Now: bash scripts/08_pgi_eda.sh\n'

# What --score quietly did with MISSING genotypes: by default plink2
# mean-imputes them (a missing call contributes the variant's average allele
# count). Defensible at low missingness -- ours is ~0 after QC -- but it is a
# choice, and papers state it.
#
# TRY IT: score WITHOUT the QC (against the raw input) and compare:
#   bash -c 'source scripts/common.sh; p2 --pfile data/toy \
#     --score data/pgi_weights.txt 1 3 5 header cols=+scoresums --out results/pgi_raw'
#   grep -E "variants processed|skipped" results/pgi_raw.log
# More variants match (no QC exclusions) -- is that better? What did QC
# protect the score from?
