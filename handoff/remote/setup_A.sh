set -e
cd /workspace
export UV_LINK_MODE=copy
echo "$(date -u +%H:%M:%S) venv"
uv venv -q --python 3.12 venv
. venv/bin/activate
uv pip install -q --index-url https://download.pytorch.org/whl/cu130 "torch==2.12.1+cu130" "torchvision==0.27.1+cu130"
uv pip install -q "diffusers==0.35.1" "transformers==4.57.6" "accelerate==1.10.1" "numpy==2.5.2" "scipy==1.16.2" \
  "pillow==12.3.0" "safetensors==0.6.2" "huggingface-hub==0.36.0" "tokenizers==0.22.1" "ftfy==6.3.1" "regex==2026.9.10" \
  "scikit-image==0.26.0" "tqdm==4.70.1" "lpips==0.1.4" "jsonschema==4.26.0" "PyYAML==6.0.3"
uv pip install -q --no-deps "git+https://github.com/openai/CLIP.git@d05afc436d78f1c48dc0dbf8e5980a9d471f35f6"
python -c "import torch; print('torch', torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
echo "$(date -u +%H:%M:%S) assets"
A=/workspace/assets/a6; mkdir -p "$A"
HF=https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main
bad=0
while read -r sha size path; do
  dest="$A/$path"; mkdir -p "$(dirname "$dest")"
  case "$path" in
    clip/ViT-B-32.pt) url="https://openaipublic.azureedge.net/clip/models/40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af/ViT-B-32.pt";;
    alexnet/*) url="https://download.pytorch.org/models/alexnet-owt-7be5be79.pth";;
    sd15-fp16/*) url="$HF/${path#sd15-fp16/}";;
  esac
  curl -sSL --retry 3 -o "$dest" "$url"
  [ "$(sha256sum "$dest" | cut -d' ' -f1)" = "$sha" ] || { echo "MISMATCH $path"; bad=1; }
done < /root/asset-lock.txt
[ $bad = 0 ] && echo "assets: 17/17 hashes match"
echo SETUP_A_DONE
