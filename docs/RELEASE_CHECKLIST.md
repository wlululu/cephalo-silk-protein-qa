# Release checklist (pending author/PI and source-data review)

## Already prepared

- [x] Publish a GitHub *review snapshot* with six sanitized saved-prediction files, held-out test IDs, evaluation code and unit tests.
- [x] Create three distinct **private** Hugging Face LoRA repositories and record their URLs in the project documentation.
- [x] Preserve the staged adapter's **general-only merged-base** dependency in its original PEFT configuration and repository manifest.
- [x] Maintain two **private** Hugging Face image–QA dataset repositories with draft Dataset Cards.

## Before public scientific release

- [ ] Rotate/revoke credentials embedded in historical notebooks; inspect Git history for accidental credentials.
- [ ] Verify third-party redistribution rights and obtain author/PI approval for GitHub predictions and both datasets; check model-base license obligations.
- [ ] Choose and document a source-code license, and appropriate separate data/model licenses where permitted.
- [ ] Independently verify all three HF adapter files, stored SHA-256 hashes, model cards, loading and short-answer inference.
- [ ] Verify the staged merged-general model is available or a faithful merge reconstruction is documented and tested.
- [ ] Audit both HF dataset snapshots against actual curated 2,177/7,024 protein populations and seven QA records per protein; confirm images and label mappings.
- [ ] Publish or link the complete train/test membership, precise dataset-generation and rendering code only after historical validation and credential sanitization.
- [ ] Pin GitHub commit and all Hugging Face dataset/model revision IDs in this repository and manuscript Data and Code Availability.
- [ ] Decide when to make GitHub and selected HF resources public following review; do **not** assume temporarily public access means the work is licensed for redistribution.

## Additional scientific controls

- [ ] Check protein exact-sequence and near-homology overlaps between domains and split partitions.
- [ ] Consider no-image/shuffled-image controls to assess visual grounding and mitigate format-compliance confounding.
