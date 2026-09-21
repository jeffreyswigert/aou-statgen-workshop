#!/usr/bin/env bash
# 13_score_real_pgi.sh (session 3) -- build a PGI on REAL AoU genotypes.
#
# Same mechanics as session 2's synthetic run, now with real files and real
# match-counting: fetch the instructor-staged weight file, score the staged
# chromosome, then join with the phenotype and ancestry predictions for EDA.
source "$(dirname "$0")/common.sh"
[[ -s "lab_data/chr${CHROM}_filtered.bed" ]] || { echo 'No genotypes staged. Run: bash scripts/10_fetch_aou_genotypes.sh' >&2; exit 1; }
[[ -s results/aou_pheno.tsv ]] || { echo 'No phenotype. Run: bash scripts/11_build_phenotype.sh' >&2; exit 1; }

# --- Resolve the weight file -----------------------------------------------
# Real path: the instructor stages rsID-keyed weights (from a public GWAS or
# the PGI Repository) in the workshop bucket. Format: header line, then
# columns  rsid  effect_allele  weight.
# Rehearsal path: DEMO_WEIGHTS=1 fabricates weights from the staged .bim --
# CLEARLY LABELED noise, for testing plumbing only (in the sandbox there is
# no instructor bucket to fetch from).
weights=lab_data/height_weights.txt
if [[ ! -s "$weights" ]]; then
  if [[ "${DEMO_WEIGHTS:-}" == 1 ]]; then
    echo 'DEMO_WEIGHTS=1: fabricating STUB weights from the .bim (plumbing test only).'
    awk 'BEGIN{print "rsid\teffect_allele\tweight"; srand(20260921)}
         {printf "%s\t%s\t%.5f\n", $2, $5, (rand()-0.5)/50}' \
        "lab_data/chr${CHROM}_filtered.bim" > "$weights"
  elif [[ -n "${WEIGHTS_URI:-}" ]]; then
    gflags=(); [[ -z "${BILLING_PROJECT:-}" ]] || gflags=(--billing-project="$BILLING_PROJECT")
    gcloud "${gflags[@]}" storage cp "$WEIGHTS_URI" "$weights" \
      || { echo "Could not fetch $WEIGHTS_URI -- ask the instructor, or rehearse with DEMO_WEIGHTS=1." >&2; exit 1; }
  else
    echo 'No weights: set WEIGHTS_URI in your config (instructor-staged), or DEMO_WEIGHTS=1 to rehearse.' >&2; exit 1
  fi
fi
head -n 2 "$weights"

# --- Score -----------------------------------------------------------------
# Columns 1 2 3: rsid, EFFECT ALLELE, weight. The .bim here is rsID-keyed, so
# rsID weights match directly; scoring AoU's ACAF filesets instead would need
# the VAT rsID->variant-ID mapping first -- a real, documented extra step.
p2 --bfile "lab_data/chr${CHROM}_filtered" \
  --score "$weights" 1 2 3 header cols=+scoresums list-variants \
  --out results/aou_pgi

# The match count is the whole harmonization story: read it, every time.
grep -E 'variants processed|skipped' results/aou_pgi.log || true

python3 scripts/aou_pgi_eda.py

# TRY IT: how sensitive is the PGI to coverage? Re-score with a different
# chromosome (CHROM=21 bash scripts/10_fetch_aou_genotypes.sh, then re-run
# this script with CHROM=21) -- a one-chromosome PGI is a deliberately partial
# index either way; real studies score all 22 and sum the per-chromosome
# results (plink's .sscore SUM columns add across filesets).
