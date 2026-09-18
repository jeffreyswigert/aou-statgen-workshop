# Source notes

Public documentation checked 18 September 2026. All numerical lab results are generated from the included synthetic data, not extracted from AoU.

## Supplied readings

Mills, Melinda C., Nicola Barban, and Felix C. Tropf. 2020. *An Introduction to Statistical Genetic Data Analysis*. MIT Press.

- Chapter 7, “Genetic Data and Analytical Challenges,” supplied as a text PDF. Sections 7.5 and 7.7 anchor file formats and computing/storage.
- Chapter 8, “Working with Genetic Data, Part I: Data Management, Descriptive Statistics, and Quality Control,” supplied as the 33-page scanned PDF `statgendataanalysus_20260918-1156.pdf`. Sections 8.2-8.5 anchor terminal use, PLINK, descriptive reports, and QC. OCR and selected rendered pages were used to inspect it.
- The workshop paraphrases concepts and creates new examples. It does not redistribute either supplied chapter. PLINK 2 syntax and report names replace the older PLINK examples. Ancestry/relatedness/HWE interpretation is contextualized for AoU.

## All of Us and Workbench

- [Data Browser](https://databrowser.researchallofus.org): public, aggregate-only exploration of surveys, physical measurements, and EHR domains; the source of the concept IDs in `data/pheno_menu.tsv`.

- [CDR v9 announcement](https://support.researchallofus.org/hc/en-us/articles/50653909888788-Our-Largest-Genomic-Dataset-Curated-Data-Repository-version-9): v9 availability in the updated Workbench.
- [Data Dictionaries](https://support.researchallofus.org/hc/en-us/articles/360033200232-Data-Dictionaries): current release references and data collection resources.
- [Genomic and multi-omic data organization](https://support.researchallofus.org/hc/en-us/articles/49999549117588-How-the-All-of-Us-Genomic-and-multi-omics-data-are-organized): Controlled Tier, file types, auxiliary data. Includes a release-specific PDF.
- [Smaller callsets](https://support.researchallofus.org/hc/en-us/articles/14929793660948-Smaller-Callsets-for-Analyzing-Short-Read-WGS-SNP-Indel-Data-with-Hail-MT-VCF-and-PLINK): useful format/filtering distinctions; this article contains v8-specific counts and should not be treated as v9's full specification.
- [Getting started with genomic analyses](https://support.researchallofus.org/hc/en-us/articles/30914634409876-Getting-Started-with-Genomic-Analyses-on-the-Researcher-Workbench): small pilot datasets, modular workflows, and avoiding full-callset densification.
- [JupyterLab in AoU](https://support.researchallofus.org/hc/en-us/articles/360039690191-JupyterLab-Notebooks-and-programming): current links to JupyterLab resources.
- [Verily JupyterLab apps](https://support.workbench.verily.com/docs/guides/cloud_apps/cloud_app_types/jupyterlab/): local disks, workspace buckets, and gcloud storage.
- [Publication/presentation checklist](https://support.researchallofus.org/hc/en-us/articles/22344017910804-All-of-Us-Researcher-Publication-Presentation-and-Poster-Checklist): dissemination policy context, including small participant/incident counts.

## Software

- [PLINK 2 downloads](https://www.cog-genomics.org/plink/2.0/)
- [PLINK 2 input filtering](https://www.cog-genomics.org/plink/2.0/filter)
- [PLINK 2 association](https://www.cog-genomics.org/plink/2.0/assoc)
- [PLINK 2 file formats](https://www.cog-genomics.org/plink/2.0/formats)
- [PLINK 2 PCA](https://www.cog-genomics.org/plink/2.0/strat)
- [PLINK 2 LD](https://www.cog-genomics.org/plink/2.0/ld)
- [BigQuery COLUMNS metadata](https://cloud.google.com/bigquery/docs/information-schema-columns)
- [bq CLI reference](https://cloud.google.com/bigquery/docs/reference/bq-cli-reference)
- [USC colors](https://identity.usc.edu/identity/color/): HEX #990000 and #FFCC00. No official seal or logo is reproduced.

## Repository limitation

The requested URL was interpreted as `https://github.com/JonJala/aou_sandbox` (the word “and” was attached to the end in the prompt). The GitHub connector returned 404 for the repository and contents; repository search found no accessible match; a public raw README request also returned 404. No contents were inferred. This draft does not claim to use or modify Jon's repository.
