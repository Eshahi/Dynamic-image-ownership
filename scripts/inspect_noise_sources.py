"""Read only pinned public text sources; never acquire weights or execute upstream code."""
import hashlib
import json
import urllib.request

DIFFUSERS = "https://raw.githubusercontent.com/huggingface/diffusers/0f252be0ed42006c125ef4429156cb13ae6c1d60/"
MODEL = "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/raw/451f4fe16113bff5a5d2269ed5ad43b0592e9a14/"
SOURCES = {
    "ddim": (DIFFUSERS + "src/diffusers/schedulers/scheduling_ddim.py", [(180, 270), (290, 530)]),
    "vae": (MODEL + "vae/config.json", None),
    "unet": (MODEL + "unet/config.json", None),
    "scheduler": (MODEL + "scheduler/scheduler_config.json", None),
    "model_card": (MODEL + "README.md", [(1, 150)]),
}


def main():
    for name, (url, ranges) in SOURCES.items():
        with urllib.request.urlopen(url, timeout=30) as response:
            raw = response.read(200001)
        if len(raw) > 200000:
            raise ValueError("Text response exceeds inspection limit")
        print(json.dumps({"source": name, "url": url, "bytes": len(raw),
                          "sha256": hashlib.sha256(raw).hexdigest()}))
        lines = raw.decode("utf-8").splitlines()
        for start, end in ranges or [(1, len(lines))]:
            for index in range(start - 1, min(end, len(lines))):
                print(f"{index + 1}: {lines[index]}")


if __name__ == "__main__":
    main()
