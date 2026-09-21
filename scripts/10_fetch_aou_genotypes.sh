#!/usr/bin/env bash
# 10_fetch_aou_genotypes.sh (session 3) -- stage REAL genotype data on the VM.
#
# Copies one chromosome of the HapMap3-filtered PLINK filesets from the shared
# SSGAC bucket (about 1-2 GB: a couple of minutes inside Google's network),
# plus AoU's genetic-ancestry predictions from the v9 controlled bucket.
# Cloud files must be copied to the VM disk before PLINK can read them --
# nothing streams from gs:// on its own.
#
# The same script runs against the local sandbox: source the sandbox's env.sh
# and these gs:// URIs resolve to local fixture files instead.
source "$(dirname "$0")/common.sh"
mkdir -p lab_data

# Requester-pays buckets (the v9 controlled bucket is one) refuse anonymous
# billing: the flag must name who pays. It is a LEADING global flag -- putting
# it after the paths does not work everywhere. Empty BILLING_PROJECT is fine
# for buckets that are not requester-pays.
gflags=()
[[ -z "${BILLING_PROJECT:-}" ]] || gflags=(--billing-project="$BILLING_PROJECT")

echo "Staging chr${CHROM} HapMap3-filtered fileset from $GENO_SRC ..."
for ext in bed bim fam; do
  gcloud "${gflags[@]}" storage cp "$GENO_SRC/chr${CHROM}_filtered.$ext" "lab_data/" \
    || { echo "Fetch failed. Check GENO_SRC, bucket access, and BILLING_PROJECT in your config." >&2; exit 1; }
done

echo "Staging ancestry predictions from $ANC_SRC ..."
gcloud "${gflags[@]}" storage cp "$ANC_SRC" "lab_data/ancestry_preds.tsv" \
  || { echo "Ancestry fetch failed (requester-pays: BILLING_PROJECT must be set)." >&2; exit 1; }

# Never trust a transfer you have not counted. Real fetches fail in silent
# ways (truncation, wrong path matching an empty prefix); sizes and line
# counts are the ten-second insurance.
ls -lh lab_data/chr${CHROM}_filtered.* lab_data/ancestry_preds.tsv
n_samples=$(wc -l < "lab_data/chr${CHROM}_filtered.fam")
n_variants=$(wc -l < "lab_data/chr${CHROM}_filtered.bim")
echo "chr${CHROM}: $n_samples samples x $n_variants variants staged."

# Two conventions to notice while the files are fresh (both differ across
# real AoU resources, and both have burned real projects):
#   head -n 2 lab_data/chr${CHROM}_filtered.fam   # FID convention (here FID=IID)
#   head -n 2 lab_data/chr${CHROM}_filtered.bim   # ID scheme (here rsIDs)
printf 'Staged. Next: bash scripts/11_build_phenotype.sh\n'
