# LoRA adapter publication (not stored in GitHub)

The archive `Archive(2).zip` contains three saved PEFT LoRA adapters. The
minimal deployable files for each adapter are `adapter_model.safetensors`
and `adapter_config.json`; full Trainer optimizer/scheduler/RNG states are not
necessary to load the adapter for inference.

| Adapter | Checkpoint | Base in actual adapter_config.json |
|---|---|---|
| spider_only | checkpoint-13720 | lamm-mit/Cephalo-Llama-3.2-11B-Vision-Instruct-128k |
| general_only | checkpoint-44252 | lamm-mit/Cephalo-Llama-3.2-11B-Vision-Instruct-128k |
| spider_staged | checkpoint-13720 | wlululu/Cephalo_protein_predict_all_losstrack50_splitbyProtein_general-merged_Epoch4 |

**Staged dependency:** The staged LoRA adapter is not directly based on the
original checkpoint. It was trained atop the general-protein-adapted model
whose LoRA was merged into base weights; the model is currently private.
To reproduce the staged inference path, release or deterministically rebuild
that merged general-protein checkpoint before loading the staged adapter.
Do not silently replace the dependency with the unadapted base checkpoint.

Recommended: 3 separate HF model repositories, each with only the two PEFT
adapter files and a model card. For the staged adapter, describe the base
merge/reconstruction dependency. No 90MB weights belong in a normal Git repo.
Weights have not been verified by a fresh model-loading/inference test here.
See `models/adapter_manifest.json` for source paths and SHA-256 hashes.
