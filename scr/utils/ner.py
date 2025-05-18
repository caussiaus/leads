from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import torch

_hf_model = "Davlan/bert-base-multilingual-cased-ner-hrl"
_tokenizer = AutoTokenizer.from_pretrained(_hf_model)
_model     = AutoModelForTokenClassification.from_pretrained(_hf_model)
_device    = 0 if torch.cuda.is_available() else -1

ner = pipeline(
    "ner",
    model=_model,
    tokenizer=_tokenizer,
    aggregation_strategy="simple",
    device=_device
)

def extract_names(text: str):
    return [ent["word"] for ent in ner(text)
            if ent["entity_group"] in {"PER","PERSON"}]
