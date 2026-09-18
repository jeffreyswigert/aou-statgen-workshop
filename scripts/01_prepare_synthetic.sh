#!/usr/bin/env bash
# 01_prepare_synthetic.sh -- REGENERATE the synthetic dataset from scratch.
# You do NOT need to run this for the lab: data/ ships ready to use. It exists
# so the whole dataset is reproducible from code (fixed seed), and so you can
# read exactly how the planted problems and the five PCs were made.
source "$(dirname "$0")/common.sh"
[[ "$DATA_MODE" == synthetic ]] || { echo 'Synthetic preparation requires DATA_MODE=synthetic' >&2; exit 1; }
python3 scripts/make_synthetic.py
p2 --vcf data/toy.vcf --make-pgen --out data/toy
# PCs are prepared before class. QC for the PCA marker panel follows the lab rules.
p2 --pfile data/toy --var-filter --snps-only just-acgt --max-alleles 2 --autosome --make-pgen --out results/prep_sites
p2 --pfile results/prep_sites --mind 0.05 --make-pgen --out results/prep_samples
p2 --pfile results/prep_samples --geno 0.02 --maf 0.05 --mac 20 --make-pgen --out results/prep_qc
p2 --pfile results/prep_qc --indep-pairwise 200kb 0.2 --out results/prep_prune
# Compute on ALL independent synthetic samples so covariates match the raw file.
p2 --pfile data/toy --extract results/prep_prune.prune.in --pca 5 --out results/prep_pca
python3 scripts/merge_covariates.py
printf 'Synthetic data and five PCs ready. Run the lab scripts next.\n'
