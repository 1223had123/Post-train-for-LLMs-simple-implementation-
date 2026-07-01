from pathlib import Path

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from evaluate import evaluate_prediction
from prompt import prompt,COT_FORMAT,prompt_baseline


ROOT_DIR = Path(__file__).resolve().parents[1]

ds = load_dataset(
    "parquet",
    data_files={
        "test": str(ROOT_DIR / "data/aqua_rat/test-00000-of-00001.parquet"),
    },
    cache_dir=str(ROOT_DIR / ".cache/hf_datasets"),
)

device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained(str(ROOT_DIR / "models/Qwen3-1.7B"))
model = AutoModelForCausalLM.from_pretrained(str(ROOT_DIR / "models/Qwen3-1.7B")).to(device)
model.eval()

correct_count = 0
# for i in range(5):
#     print(ds['test']['question'][i])
#     print(ds['test']['options'][i])
#     print('-*-'*10)
#     print(ds['test']['correct'][i])
#     print('-*-'*10)
question = ds['test']['question'][5:105]
answer = ds['test']['correct'][5:105]
options = ds['test']['options'][5:105]
test_len = len(question)
print(f"数据集长度:{test_len}")

for epoch, (text, ans, option) in enumerate(zip(question, answer,options), start=1):
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": text+' '.join(option)},
    ]
    try:
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            enable_thinking=False,
        ).to(model.device)
    except TypeError:
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(model.device)

    with torch.inference_mode():
        outputs = model.generate(**inputs, max_new_tokens=512)

    out = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[-1]:],
        skip_special_tokens=True,
    )
    correct, pred, gold = evaluate_prediction(out, ans)
    if correct:
        correct_count += 1
        
        

    print(
        f"epochs:{epoch} "
        f"[pred:{pred}, gold:{gold}, correct:{correct}, acc:{correct_count / epoch}]"
    )

print(f"strategyqa(acc):{correct_count / test_len}")


