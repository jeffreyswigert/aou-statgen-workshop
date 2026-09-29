# All of Us statistical genetics: archived sessions

> **This repository is an archive.** The workshop is
> **[github.com/jeffreyswigert/aou-statgen-lab](https://github.com/jeffreyswigert/aou-statgen-lab)**:
> clone that one for class. Everything here is draft material for possible
> later sessions, kept for reference. The Lab 1 materials that used to live
> here have been removed; the current slides, scripts, and cheat sheet are in
> `aou-statgen-lab`.

## What's here

- A **synthetic self-study track** (below): slides, handouts, and scripts that
  run on any machine with simulated data.
- A **stretch exercise** that summarizes more real phenotypes from the CDR.
- `scripts/check_disclosure.py`, the disclosure check also used in the lab.
- `docs/SOURCES.md`: readings and platform/software references.

## Self-study: the synthetic track

Two fully synthetic modules for practice without Controlled Tier
access, on any machine. **No All of Us
participant records are involved** in this track, and none of its results
have biological meaning.

**A. First workflow** (`lab_handout.pdf`, `aou_cli_workshop.pdf`): inspect a
PLINK fileset, run sequential QC, fit a covariate-adjusted association scan,
save a reproducible run.

```bash
bash scripts/00_preflight.sh && bash scripts/02_qc.sh
bash scripts/03_association.sh && bash scripts/04_save.sh
```

Expected: 600 samples / 2,400 variants → 588 / 2,330 after QC; top hit
`SIMV001201` (allele G, beta ≈ 0.93, N = 587). Match `expected/` and it worked.

**B. PGIs on synthetic data** (`lab2_handout.pdf`, `aou_pgi_workshop.pdf`):
score deliberately imperfect consortium-style weights (`data/pgi_weights.txt`),
then compare the PGI across a randomized group (balanced, −0.01 SD) and a
self-selected one (shifted, +0.46 SD — selection and structure, not biology).

```bash
ls results/qc.pgen || bash scripts/02_qc.sh
bash scripts/07_score_pgi.sh && bash scripts/08_pgi_eda.sh
```

## Stretch exercise: summarize more real phenotypes

Requires Controlled Tier access, with `CDR_DATASET` and `BILLING_PROJECT`
filled in `config.sh`. `data/pheno_menu.tsv` offers nine real
phenotypes spanning program measurements, EHR labs, surveys, and EHR
conditions, each annotated with its source type's trap:

```bash
bash scripts/06_pheno_summary.sh            # show the menu
bash scripts/06_pheno_summary.sh ldl        # aggregates only, byte-capped
```

The script resolves and prints concept names first (an ID is a claim until
the name confirms it) and suppresses counts of 1–20. Find the same phenotype
in the public [Data Browser](https://databrowser.researchallofus.org) to see
where concept IDs come from.

## The disclosure check

**Compliance as a default.** `scripts/check_disclosure.py` runs inside every
save: it lists participant-level files that must stay in the workspace and
flags participant counts of 1–20 — direct, or derivable by subtraction between
reported numbers — which the AoU Data and Statistics Dissemination Policy
restricts. In AoU mode a finding blocks the save until fixed or explicitly
acknowledged after review. Adapt it to your own pipelines; it complements
manual review of text, figures, and percentages, never replaces it.
