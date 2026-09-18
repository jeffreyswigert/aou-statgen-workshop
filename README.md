# Statistical genetics on All of Us: a first workflow in the VM terminal

Materials for a one-hour workshop: 40 minutes of instruction and a 20-minute
hands-on lab. You will inspect a genotype file set, run sequential QC, fit a
covariate-adjusted association model, interpret one result, and save a
reproducible run to a workspace bucket.

**All data in this repository are synthetic.** No All of Us participant
records are included, and none of the results have biological meaning.

## Quick start (on your AoU Workbench VM)

Open a Terminal from the JupyterLab Launcher, then:

```bash
git clone https://github.com/jeffreyswigert/aou-statgen-workshop.git aou_cli_workshop
cd aou_cli_workshop
bash scripts/00_preflight.sh
bash scripts/02_qc.sh
bash scripts/03_association.sh
bash scripts/04_save.sh     # needs WORKSHOP_BUCKET in config.sh
```

Follow along in `lab_handout.pdf` — it explains what to inspect after each
command and contains the reference answers. `aou_cli_workshop.pdf` is the
slide deck for review afterward.

Preflight checks your environment and stops with a clear message if PLINK 2
or an input is missing. Your instructor stages PLINK 2 before class; if you
need it yourself later, see `scripts/install_plink2.sh`.

## What's here

- `lab_handout.pdf` — lab instructions, interpretation questions, answers.
- `aou_cli_workshop.pdf` — the slides.
- `scripts/` — short, readable Bash and Python; read each one before running it.
- `data/` — synthetic genotypes, phenotype, covariates, and provenance.
- `expected/` — reference outputs, for comparison or if your VM misbehaves.
- `docs/SOURCES.md` — the readings and every platform/software reference used.
- `config.sh` — workshop settings; fill `WORKSHOP_BUCKET` with your authorized
  workspace bucket before the save step.

## Expected results

QC takes 600 samples and 2,400 variants to 588 and 2,330. The top association
is `SIMV001201` (counted allele G, beta ≈ 0.93, N = 587). If you match
`expected/`, your run worked.

## Two habits this workshop teaches

**Compliance as a default.** `scripts/check_disclosure.py` runs inside every
save: it lists participant-level files that must stay in the workspace and
flags participant counts of 1–20 — direct, or derivable by subtraction between
reported numbers — which the AoU Data and Statistics Dissemination Policy
restricts. With real data (`DATA_MODE=aou`) a finding blocks the save until
fixed or explicitly acknowledged after review. Adapt it to your own pipelines;
it complements manual review of text, figures, and percentages, never replaces
it.

**Test the plumbing before you pay for a VM.** The whole pipeline, including
the cloud save, also runs on your laptop against a local All of Us sandbox
that mirrors the platform's paths, file names, and environment variables with
fake data. Source its `env.sh`, run the same four commands unchanged, and the
save lands in a fake local bucket. Ask your instructor for the sandbox
repository.

## Stretch exercise: a real phenotype

With Controlled Tier access and `CDR_DATASET` + `BILLING_PROJECT` set in
`config.sh`, you can summarize a real AoU phenotype from a curated menu
spanning program measurements, EHR labs, surveys, and EHR conditions:

```bash
bash scripts/06_pheno_summary.sh            # show the menu
bash scripts/06_pheno_summary.sh height     # aggregates only, byte-capped
```

The script resolves and prints the concept names first (an ID is a claim until
the name confirms it), queries aggregates only, and suppresses counts of 1–20.
Each menu row notes the trap its source type is known for. Find the same
phenotype in the public [Data Browser](https://databrowser.researchallofus.org)
to see where the concept IDs come from. Real summaries stay in the workspace
unless they clear dissemination review.

## After the workshop

These scripts demonstrate a workflow, not a complete AoU GWAS protocol:
ordinary regression does not account for relatives, the QC thresholds are
teaching choices, and real phenotype definitions need release-specific care.
The readings in `docs/SOURCES.md` are the next step.
