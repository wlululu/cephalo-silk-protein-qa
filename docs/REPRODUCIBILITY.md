# Benchmark reproducibility and provenance

## Saved-prediction benchmark

The repository includes six historical evaluation CSV files: zero-shot and fine-tuned predictions for spider-only, general-only and General → Spider adaptation profiles. For every profile, records are matched one-to-one using `(protein_name, question)` with identical reference labels. `scripts/score_benchmark.py` reconstructs strict categorical accuracy, per-question results, format compliance, and paired bootstrap 95% confidence intervals resampled by protein.

Run from the repository root:

```bash
python -m unittest discover -s tests -v
python scripts/score_benchmark.py --input-dir data/evaluations --out results/reproduced
```

The historical held-out protein IDs for the three evaluation profiles appear in `data/splits/`. The spider-only and staged evaluation groups are distinct, so their reported accuracy difference is not a paired test of staged training superiority.

## Data and labels

Source datasets, associated image–QA records and model adapters are linked in the root README. The study represents seven categorical QA tasks per protein. The reference helper `scripts/build_qa_from_properties.py` accepts precomputed DSSP fractions and ProtParam sequence descriptors and implements the reported categorical thresholds. It is a transparent utility, not a claim that every historical preprocessing step has been reproduced byte-for-byte.

The VMD reference helper `scripts/render_pdb_isometric.py` illustrates the protein-rendering settings. Differences in source coordinates, graphics versions or image preprocessing may affect output images.

## What the scores establish

The scoring script validates stored model outputs using strict, whole-response label matching. It does not rerun the foundation model or LoRA adapters. Normalization allows case differences and terminal punctuation but does not extract a correct answer embedded in a longer sentence. As a result, improvements can partly reflect adherence to the expected answer format rather than changes in image-grounded reasoning.

Secondary-structure annotations and sequence-derived physicochemical categories have different evidential relationships to a structural image. These results do not directly validate experimental protein stability, hydrophobicity or mechanical properties.

## Model checkpoint lineage

The spider-only and general-only LoRA adapters use the original Cephalo vision-language checkpoint as their base. The staged adapter uses the **merged general-protein model** as its base; that dependency is recorded in `models/adapter_manifest.json` and [MODEL_RELEASE.md](MODEL_RELEASE.md). Reproducing live inference requires the corresponding model, image preprocessing and generation settings in addition to the saved prediction tables.

## Extended reproducibility

For research extending these results, recommended checks include pinned model/dataset revisions, source-processing provenance, training and testing split integrity, sequence-similarity overlap controls, and image-ablation tests. These controls should be distinguished from the exact saved-prediction scoring reproduced by this repository.
