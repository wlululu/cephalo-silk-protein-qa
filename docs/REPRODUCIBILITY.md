# Reproducibility and provenance

## What can be reproduced without GPUs

The CSV predictions in `data/evaluations/` were assembled from the three historical fine-tuned evaluation outputs and three matched zero-shot runs. For each strategy, records were matched one-to-one by `(protein_name, question)` with identical reference labels. The code in `scripts/score_benchmark.py` reproduces the strict-label results, format compliance, per-question scores and protein-resampled paired-bootstrap confidence intervals. See `results/`.

The three held-out test-ID manifests are historical test membership only. Training-ID manifests and sequence-homology grouping are **not** available in the public GitHub snapshot. In particular, the spider-only and staged test sets differ, so the numerical difference between those two profiles must **not** be interpreted as a paired experimental estimate of an advantage from staged adaptation.

Strict accuracy scores **whole responses** only after case/trailing-punctuation normalization. A longer explanation that contains a correct label may be marked wrong; thus the improvements partially capture response-format compliance. This benchmark alone does not validate image dependence, semantic protein-property inference or experimentally measured protein mechanics.

## Original-data and code provenance

The privately retained historical notebooks and archives include upstream PDB/protein resources, processing examples and model training outputs. This GitHub repository deliberately excludes notebooks, input protein sequences, source PDB files, full model weights, high-volume training files and any embedded credentials.

- `scripts/build_qa_from_properties.py` is a newly curated **label-rule reference utility** taking *already computed* DSSP fractions and ProtParam values. It is not a verified reconstruction of the archived dataset generation process.
- `scripts/render_pdb_isometric.py` is a newly curated **VMD rendering reference utility** based on archived render settings. The original coordinates, graphics environment and actual output images have not been jointly validated for pixel identity.
- `docs/training_config.json` summarizes reported settings from the manuscript's Supplementary Information and is not a fully verified historical environment lock file.

## External artifacts

Two curated image–QA datasets are hosted privately at `wlululu/spidrion_image_QA.hf` and `wlululu/forcegen_image_QA.hf` on Hugging Face; three LoRA adapter repos are separately hosted at `wlululu/cephalo-silk-{spider,general,staged}-lora`. See the full links and the staged merged-base dependency in [`MODEL_RELEASE.md`](MODEL_RELEASE.md) and the root README.

The dataset cards describe study-intended counts (2,177 spider-silk and 7,024 general proteins), **not** an independently completed verification of all current HF records. Before publication, audit actual HF dataset contents, IDs, labels, file permissions and exact revisions.

## Pending for an end-to-end reproducible release

- Confirm public redistribution rights for source structures/images, processed datasets, predictions and derived model adapters; select software/data licenses with PI approval.
- Verify input image/QA record mapping, source-data counts and historical train/test splits against the HF snapshots.
- Sanitize and test genuine historical seven-QA generation, image rendering, data-split, fine-tuning and inference scripts; document versions/seeds/decoding and relevant compute environment.
- Independently check model loading, original adapter weight hashes and inference for all three paths; validate availability or deterministic reconstruction of the staged merged-base model.
- Audit exact-sequence and near-homology overlaps and, when feasible, evaluate image-ablated/shuffled-image controls.
- Record immutable GitHub commit and Hugging Face revision SHAs for the manuscript archive.
