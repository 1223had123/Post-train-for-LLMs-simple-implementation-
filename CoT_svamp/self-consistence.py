import argparse
from collections import Counter

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from evaluate import extract_gold, extract_pred
from prompt import promt


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", default="./models/Qwen3-1.7B")
    
    parser.add_argument("--test-file", default="./data/svamp/test.parquet")
    parser.add_argument("--cache-dir", default=".cache/hf_datasets")
    parser.add_argument("--split", choices=["test"], default="test")
    parser.add_argument("--sample-size", type=int, default=100)
    parser.add_argument("--num-samples", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--max-new-tokens", type=int, default=1000)
    parser.add_argument("--print-samples", action="store_true")
    return parser.parse_args()


def build_inputs(tokenizer, question, device):
    messages = [
        {"role": "system", "content": promt},
        {"role": "user", "content": question},
    ]
    try:
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            enable_thinking=False,
        )
    except TypeError:
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        )
    return inputs.to(device)


def load_model_and_tokenizer(model_path):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=dtype,
    ).to(device)
    model.eval()
    return model, tokenizer, device


def generate_samples(model, tokenizer, question, device, args):
    inputs = build_inputs(tokenizer, question, device)
    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=True,
            temperature=args.temperature,
            top_p=args.top_p,
            num_return_sequences=args.num_samples,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    input_len = inputs["input_ids"].shape[-1]
    return tokenizer.batch_decode(
        outputs[:, input_len:],
        skip_special_tokens=True,
    )


def majority_vote(outputs):
    preds = [extract_pred(output) for output in outputs]
    valid_preds = [pred for pred in preds if pred is not None]
    if not valid_preds:
        return None, preds, 0

    pred, votes = Counter(valid_preds).most_common(1)[0]
    return pred, preds, votes


def main():
    args = parse_args()
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    ds = load_dataset(
        "parquet",
        data_files={"test": args.test_file},
        cache_dir=args.cache_dir,
    )
    dataset = ds[args.split].shuffle(seed=args.seed)
    if args.sample_size > 0:
        dataset = dataset.select(range(min(args.sample_size, len(dataset))))

    model, tokenizer, device = load_model_and_tokenizer(args.model_path)
    print(model.device)
    print(f"split={args.split}, size={len(dataset)}, num_samples={args.num_samples}")

    correct_count = 0
    total = 0

    for item in dataset:
        question = item["question_concat"]
        answer = item["Answer"]
        outputs = generate_samples(model, tokenizer, question, device, args)
        voted_pred, preds, votes = majority_vote(outputs)
        gold = extract_gold(answer)
        correct = voted_pred == gold

        total += 1
        correct_count += int(correct)
        acc = correct_count / total

        print(
            f"[{total}/{len(dataset)}] correct={correct} "
            f"vote={voted_pred}({votes}/{args.num_samples}) gold={gold} acc={acc:.4%}"
        )
        
        if args.print_samples:
            print(f"question: {question}")
            for idx, (pred, output) in enumerate(zip(preds, outputs), start=1):
                print(f"sample {idx}: pred={pred}")
                print(output)
                print("-" * 40)

    final_acc = correct_count / total if total else 0.0
    print(f"final total={total}, correct={correct_count}, acc={final_acc:.4%}")


if __name__ == "__main__":
    main()
