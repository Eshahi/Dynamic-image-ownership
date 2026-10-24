#!/usr/bin/env bash
# Stage-2b server setup (amendment 2b). Written by Claude (Opus 5.5), 2026-10-24.
#
# Run inside tmux, with the log in /workspace/setup.log:
#   tmux new -d -s setup "bash scripts/encoder_transfer_server_setup_2b.sh <spent-hours> <spent-usd> '<approval>' 2>&1 | tee -a /workspace/setup.log"
# Expects the repository archive at /workspace/thesis (the GitHub repository is private, so it is shipped
# as a byte-identical git archive). It builds the exact stage-2a environment plus the two Kandinsky 3
# tokenizer packages, downloads the pinned Kandinsky 3 files, builds the stage-2b contract and runs the
# CPU tests. The contract is then copied home, committed and pushed before the driver starts.
set -euxo pipefail
SPENT_HOURS="$1"
SPENT_USD="$2"
APPROVAL="$3"
cd /workspace/thesis
git log -1 --oneline
python3 -m pip install --quiet uv 2>/dev/null || python3 -m pip install --quiet --break-system-packages uv
export UV_CACHE_DIR=/workspace/.uv-cache
python3 -m uv python install 3.11
[ -x /workspace/venv/bin/python ] || python3 -m uv venv /workspace/venv --python 3.11
V=/workspace/venv/bin/python
python3 -m uv pip install --python $V "torch==2.7.1+cu128" "torchvision==0.22.1+cu128" \
  --index-url https://download.pytorch.org/whl/cu128
# The stage-2a pins exactly (contract `packages`), plus the tokenizer packages Kandinsky 3 needs.
python3 -m uv pip install --python $V -r research/encoder-transfer-20261019/requirements-stage2.txt \
  "lightning==2.5.6" "torchmetrics==1.8.2" "av==18.1.0" sentencepiece protobuf
python3 -m uv pip install --python $V --no-deps \
  "clip @ git+https://github.com/openai/CLIP.git@d05afc436d78f1c48dc0dbf8e5980a9d471f35f6"
rm -rf /workspace/.uv-cache
$V - <<'PY'
import importlib.metadata as m, torch
print({k: m.version(k) for k in ("torch", "diffusers", "transformers", "lightning", "torchmetrics", "av", "clip", "sentencepiece", "protobuf")})
print("cuda", torch.cuda.is_available(), torch.cuda.get_device_name(0), torch.cuda.get_device_properties(0).total_memory)
PY
A=/workspace/assets
K=https://huggingface.co/kandinsky-community/kandinsky-3/resolve/bf79e6c219da8a94abb50235fdc4567eb8fb4632
get() { [ -s "$2" ] || { mkdir -p "$(dirname "$2")"; curl -L --fail --retry 3 -sS -o "$2.part" "$1" && mv "$2.part" "$2"; }; }
for f in model_index.json scheduler/scheduler_config.json text_encoder/config.json \
         text_encoder/model.safetensors.index.fp16.json \
         text_encoder/model.fp16-00001-of-00005.safetensors text_encoder/model.fp16-00002-of-00005.safetensors \
         text_encoder/model.fp16-00003-of-00005.safetensors text_encoder/model.fp16-00004-of-00005.safetensors \
         text_encoder/model.fp16-00005-of-00005.safetensors tokenizer/added_tokens.json tokenizer/special_tokens_map.json \
         tokenizer/spiece.model tokenizer/tokenizer_config.json unet/config.json unet/diffusion_pytorch_model.fp16.safetensors \
         movq/config.json movq/diffusion_pytorch_model.fp16.safetensors; do
  get "$K/$f" "$A/kandinsky3/$f"
done
SP=$($V -c 'import importlib.metadata as m; print(m.version("sentencepiece"))')
PB=$($V -c 'import importlib.metadata as m; print(m.version("protobuf"))')
$V scripts/encoder_transfer_amend_2b.py --downloads $A --package sentencepiece=$SP --package protobuf=$PB \
  --spent-hours "$SPENT_HOURS" --spent-usd "$SPENT_USD" --approval "$APPROVAL"
CUDA_VISIBLE_DEVICES= $V -m unittest discover -s tests -p "test_encoder_transfer_*.py"
echo SETUP_DONE
