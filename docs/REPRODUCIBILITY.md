# Reproducibility and provenance

## Files inspected

- `Archive(1).zip` provided multiple data-construction notebooks and a VMD
  `test_render.tcl` example. Original notebooks include unrelated MD tasks,
  intermediate exploratory cells, large embedded outputs and credentials.
  **They have NOT been uploaded to this repository.**
- `Archive(2).zip` provided three fine-tuned evaluation CSVs and LoRA PEFT
  checkpoints. Only sanitized predictions and safe configuration/metadata were
  extracted for the GitHub package.
- The three zero-shot prediction files originate from the earlier matched
  zero-shot evaluation package. Predictions were matched one-to-one to each
  corresponding fine-tuned run by `(protein_name, question)`.

## Scope of code

Primary numbers are recovered directly from stored predictions using the
same strict-label normalization for each model. The published benchmark
has two distinct target types: DSSP-derived, visually encoded structural
annotations and sequence-derived ProtParam labels.

`build_qa_from_properties.py` is a new, transparent utility implementing
paper-defined thresholds for metadata that already exists. The original
notebooks do **not** establish that this utility recreates every historical
QA record and ordering. `render_pdb_isometric.py` follows the archived VMD
NewCartoon/structure color/white background/isometric scripts, but without
access to the original input coordinates/precise graphics environment it
cannot establish identical pixel values.

## Score interpretation

Three profiles each have exactly seven QA records per held-out protein.
Zero-shot uses the unadapted Cephalo checkpoint on the historical per-profile
holdout records; fine-tuned outputs use saved historical predictions.
Strict categorical whole-label scoring is not equal to a validated semantic
interpretation of long answers. Missing an explicit short-label response
counts as incorrect, even if a later reviewer might extract a category.

The spider-only and staged evaluation holdouts are *different*, so the
1.4-pp historical difference between those two fine-tuned models is not
an apples-to-apples estimate of staging benefit.

## Remaining gaps before public reproducibility claims

- Validate licensing/redistribution for images, PDB structures, sequences,
  third-party ForceGen materials and model adapters.
- Publish/freeze HF dataset revisions and document source QC/cross-domain overlap.
- Obtain a verified source for the exact historical seven-QA construction and
  the final rendering settings used to upload both HF datasets.
- Publish the source training/inference code **after** credential sanitization
  and environment version verification; determine evaluation generation settings.
- Publish three adapters on HF and make staged base availability explicit.
- Preserve raw data splits (training membership) and fixed seed/provenance.
