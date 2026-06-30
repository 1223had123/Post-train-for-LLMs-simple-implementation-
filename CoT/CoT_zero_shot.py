from pathlib import Path

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from evaluate import evaluate_prediction
from prompt import COT_FORMAT


ROOT_DIR = Path(__file__).resolve().parents[1]

ds = load_dataset(
    "parquet",
    data_files={
        "train": str(ROOT_DIR / "data/gsm8k/main/train-00000-of-00001.parquet"),
        "test": str(ROOT_DIR / "data/gsm8k/main/test-00000-of-00001.parquet"),
    },
)

device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained(str(ROOT_DIR / "models/Qwen3-1.7B"))
model = AutoModelForCausalLM.from_pretrained(str(ROOT_DIR / "models/Qwen3-1.7B")).to(device)
model.eval()

question = ds["test"]["question"][:100]
answer = ds["test"]["answer"][:100]
test_len = len(question)
correct_count = 0

print(model.device)
print(f"数据集长度:{test_len}")

for text, ans in zip(question, answer):
    messages = [
        {"role": "system", "content": COT_FORMAT},
        {"role": "user", "content": text},
    ]
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        enable_thinking=False,
    ).to(model.device)

    with torch.inference_mode():
        outputs = model.generate(**inputs, max_new_tokens=1000)

    out = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[-1]:],
        skip_special_tokens=True,
    )
    correct, pred, gold = evaluate_prediction(out, ans)
    if correct:
        print(f"问题\n {text}")
        print(f"回答\n{out}")
        correct_count += 1

print(f"CoT_zero_shot: {correct_count / test_len}")
