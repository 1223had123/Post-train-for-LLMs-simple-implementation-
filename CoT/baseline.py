from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset
from prompt import prompt_baseline,promt,COT_FORMAT
from evaluate import evaluate_prediction
import torch
ds = load_dataset(
    "parquet",
    data_files={
        "train": "./data/gsm8k/main/train-00000-of-00001.parquet",
        "test": "./data/gsm8k/main/test-00000-of-00001.parquet",
    },
)
device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained("./models/Qwen3-1.7B")
model = AutoModelForCausalLM.from_pretrained("./models/Qwen3-1.7B").to(device)
question = ds['test']['question'][:100]
answer = ds['test']['answer'][:100]
test_len = len(question)
correct_count = 0
for Q in qustion:
	print(Q)
	print('-*-'*10)
# print(model.device)
# print(f'数据集长度:{test_len}')
# for text,ans in zip(question,answer):
# 	messages = [{
# 		"role": "system", "content": prompt_baseline
# 	},
#     {		
# 		"role": "user", "content": text
# 	},
# 	]
# 	inputs = tokenizer.apply_chat_template(
# 		messages,
# 		add_generation_prompt=True,
# 		tokenize=True,
# 		return_dict=True,
# 		return_tensors="pt",
# 		enable_thinking=False,
# 	).to(model.device)

# 	outputs = model.generate(**inputs, max_new_tokens=1000)
# 	out = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
# 	correct, pred, gold = evaluate_prediction(out, ans)
# 	if correct:
# 		print(f'问题:\n{text}')
# 		print(f'步骤:\n{out}')


