#!/usr/bin/env python3
import json
from pathlib import Path
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    AutoModel
)
from transformers.utils import logging

logging.set_verbosity_error()  # suppress verbose HF logs

# --------------------------------------------------
# Define model type → HF loader mapping
# --------------------------------------------------
MODEL_LOADERS = {
    "token-classification": AutoModelForTokenClassification,
    "causal-lm": AutoModelForCausalLM,
    "sequence-classification": AutoModelForSequenceClassification,
    "sentence-embedding": AutoModel,
    "chat": AutoModelForCausalLM,
}

# --------------------------------------------------
# Start download process
# --------------------------------------------------
def main():
    root = Path(__file__).resolve().parent.parent.parent  # ~/leads
    manifest_path = root / "models" / "manifest.json"
    manifest = json.loads(manifest_path.read_text())

    for key, meta in manifest.items():
        name       = meta["name"]
        local_path = root / meta["local_path"]
        mtype      = meta.get("type", "").lower()

        print(f"\n🧠 [{key}] Downloading {name} → {local_path} (type={mtype})")
        local_path.mkdir(parents=True, exist_ok=True)

        model_cls = MODEL_LOADERS.get(mtype)
        if not model_cls:
            print(f"⚠️ Skipping unknown model type '{mtype}' for {key}")
            continue

        # For some causal models, tokenizer saving fails (tiktoken/blobfile issue)
        skip_tokenizer = "mistral" in name.lower() or mtype in {"causal-lm", "chat"}

        # Try downloading tokenizer (if not skipped)
        if not skip_tokenizer:
            try:
                tokenizer = AutoTokenizer.from_pretrained(name)
                tokenizer.save_pretrained(local_path)
                print(f"✅ Tokenizer saved.")
            except Exception as e:
                print(f"⚠️ Tokenizer download failed: {e}")

        # Try downloading model
        try:
            model = model_cls.from_pretrained(name)
            model.save_pretrained(local_path)
            print(f"✅ Model saved.")
        except Exception as e:
            print(f"❌ Model download failed: {e}")

    print("\n🎉 Done downloading all models.")

if __name__ == "__main__":
    main()
