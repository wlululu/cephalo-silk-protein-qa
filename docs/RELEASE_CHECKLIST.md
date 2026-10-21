# Reproducibility verification checklist

This checklist is an internal verification aid for maintaining the published research artifacts, not a statement that linked data or models are unavailable.

- [x] Save historical zero-shot and fine-tuned evaluation predictions and three held-out test-ID manifests.
- [x] Supply strict categorical scoring scripts and benchmark regression tests.
- [x] Document three LoRA adapter repositories and the staged merged-base dependency.
- [x] Link both protein image–QA datasets and all model resources.
- [ ] Pin exact model and dataset revision IDs in the manuscript's data/code availability record.
- [ ] Audit published HF dataset schemas, IDs, labels and image/example counts against study records.
- [ ] Verify adapter weights and reproduce representative GPU inference for each of the three checkpoints.
- [ ] Document image preprocessing and generation configuration for independently repeated live inference.
- [ ] Check exact/near-homologous protein sequence overlap and consider image-ablation controls.
- [ ] Confirm source attribution, licensing and upstream redistribution terms before assigning formal software, data or model licenses.
