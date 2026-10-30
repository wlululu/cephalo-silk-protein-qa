# General-protein structure-conditioned scientific analysis

Scientific follow-up to the archived [semantic-label evaluation](../semantic_evaluation/README.md), focused on **702 held-out general proteins** (seven categorical QA tasks per protein). This folder contains new analyses of physicochemical prediction by reference predominant secondary-structure group, including class-aware uncertainty and conditional randomization. It adds no model training, inference, new labels, or modifications to the frozen semantic parser.

## Key findings

- The fine-tuned model recovers hydrophobic positives in **22/29** beta-sheet-predominant proteins, versus **1/24** alpha-helix-predominant and **0/30** coil-predominant proteins. Aggregate hydrophobicity accuracy (91.17%) is dominated by the prevalent non-hydrophobic class; minority recall is 23/83.
- Basic-class recall for pI in alpha-helix-predominant proteins is **10/53 (18.9%)**.
- Accuracy exceeds the *observed held-out majority-class reference* by **8.26 pp** (stability), **2.99 pp** (hydrophobicity), and **11.82 pp** (pI). These are descriptive class-frequency references, **not independently trained baselines**.
- Within-predominant-structure conditional randomization indicates association beyond the three coarse structure groups' label/prediction class counts; it **does not prove image dependence**.
- The archive contains no verified sequence/family split or image-ablation controls. No coil-negative or neutral-pI reference cases are present.

Results are exploratory, with pointwise uncertainty and no correction for unknown homology, parser uncertainty, training variation or all subgroup tests. The grouping variable is the **gold predominant structure**, not a family label or a prediction. Sequence-derived ProtParam categories are not experimentally measured properties.

## Contents

- `results/scientific_summary.csv`, `Scientific_Summary_Table.csv`: overall performance, majority references, bootstrap uncertainty and class recall.
- `results/subgroup_metrics.csv`, `subgroup_class_recall.csv`, `subgroup_confusion_counts.csv`: conditional performance by gold structural group, including per-class support.
- `results/prevalence_by_structure.csv`, `prevalence_contrasts.csv`, `structure_label_associations.csv`: prevalence, confidence intervals and structural-label association tests.
- `results/conditional_prediction_associations.csv`: conditional randomization against within-structure class marginals, with bootstrap CIs.
- `results/protein_level_existing_labels.csv`: compact derived 702-protein reference and frozen prediction table needed for auditing; no new biochemical labels.
- `results/reused_general_paired_intervals.csv`: original general-only fine-tuned vs zero-shot intervals, reused unchanged.
- `figures/*.svg`, `figures/*.png`: two publication-quality figures (editable vector SVG and 300 dpi PNG), no PDF/duplicate formats committed.
- `scripts/analyze_structure.py`: original statistical analysis script from the Work package, unchanged.
- `scripts/build_deliverables.py`: reproduces figures and a local PDF report (PDF is **not** committed).
- `scripts/validate_new_results.py`: independent count/association and input-hash validation.
- `scripts/prepare_inputs.py`: copies verified, already-extracted semantic annotation CSVs and summary metrics into ignored local `inputs/` for exact script reproduction.
- `SOURCE_INPUT_SHA256.json`: original input SHA-256 checksums for provenance.

## Reproduce from repository root

Python >=3.11. This workflow uses archived results only and requires no GPU or credentials.

```bash
python3 -m pip install -r analysis/general_protein_scientific_analysis/requirements.txt
# If semantic results/*_annotated.csv were not retained locally, regenerate
# them according to analysis/semantic_evaluation/README.md first:
python3 analysis/semantic_evaluation/scripts/analyze.py --source .
# Then prepare the verified four inputs for the statistical script:
python3 analysis/general_protein_scientific_analysis/scripts/prepare_inputs.py
python3 analysis/general_protein_scientific_analysis/scripts/analyze_structure.py
python3 analysis/general_protein_scientific_analysis/scripts/validate_new_results.py
# Optional: regenerate figures (and a local, untracked PDF report)
python3 analysis/general_protein_scientific_analysis/scripts/build_deliverables.py
```

The semantic `analyze.py` command above is needed **only if** the locally generated annotated CSVs do not exist. It re-scores **saved predictions**, not GPU inference, and verifies the frozen extraction hashes. The scientific-analysis script does not run the semantic parser. `prepare_inputs.py` requires unchanged source hashes; it will stop rather than silently accept different annotations. Temporary inputs and generated PDFs are ignored by Git.

From the repository root, inspect changes before committing:

```bash
git status --short
```

## Scientific interpretation

The original score comparisons between fine-tuned and zero-shot responses remain separate from the new descriptive majority-reference, structure-conditional and randomization analyses. Strong secondary-structure label accuracy does not establish that image features causally drive physicochemical predictions. Future evidence would require controlled image-ablation/shuffle tests and reliable train-test sequence/family separation.

**Provenance:** Original saved prediction source commit `ef4f2945b8673d98b77f8fbfca862175b0c87a3d`; frozen semantic follow-up committed in `ea81fa7d44bb57463e65ad904fbc4b76b225e8a8`. The figures, scripts, tables and subgroup statistics in this directory were taken from the independently validated 2026-10-30 Work package; the source input copies and full report PDF were intentionally excluded from this GitHub-facing release.
