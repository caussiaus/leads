#!/usr/bin/env python3
"""
download_models.py

Downloads all Hugging Face models listed in models/manifest.json
using huggingface_hub.snapshot_download, pulling full safetensors.

Usage:
    pip install huggingface-hub python-dotenv
    python scr/utils/download_models.py
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import snapshot_download

# --------------------------------------------------
# Load HF_HUB_TOKEN from a project-local .env
# --------------------------------------------------
root = Path(__file__).resolve().parents[2]  # ~/leads
env_path = root / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded environment variables from {env_path}")
else:
    print(f"Warning: .env file not found at {env_path}, proceeding without it.")

HF_TOKEN = os.getenv("HF_HUB_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("Missing HF_HUB_TOKEN in environment or .env file")


def hf_snapshot(repo_id: str, target_dir: Path):
    """
    Download the full contents of a HF repo (weights + tokenizer)
    into the given target_dir using snapshot_download.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n🧠 Downloading {repo_id} → {target_dir}")
    snapshot_download(
        repo_id=repo_id,
        local_dir=str(target_dir),
        # local_dir_use_symlinks is deprecated and ignored by HF Hub
        allow_patterns=[
            "*.safetensors",
            "*.bin",
            "*.pt",
            "*.json",
            "*.txt",
            "*.model",
        ],
        use_auth_token=HF_TOKEN,
    )
    print(f"✅ Finished {repo_id}")


def main():
    manifest_path = root / "models" / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Cannot find manifest at {manifest_path}")

    manifest = json.loads(manifest_path.read_text())

    for key, meta in manifest.items():
        repo_id = meta["name"]
        local_path = root / meta["local_path"]
        hf_snapshot(repo_id, local_path)

    print("\n🎉 All models have been fully downloaded.")


if __name__ == "__main__":
    main()
