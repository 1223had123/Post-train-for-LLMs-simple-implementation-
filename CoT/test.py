import argparse
import json
from pathlib import Path

import torch
from datasets import load_dataset
from torch.utils.data import DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer

from evaluate import evaluate_prediction
from prompt import prompt_baseline, promt


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", default="./models/Qwen3-1.7B")
    parser.add_argument("--train-file", default="./data/gsm8k/main/train-00000-of-00001.parquet")
    parser.add_argument("--test-file", default="./data/gsm8k/main/test-00000-of-00001.parquet")
    parser.add_argument("--cache-dir", default=".cache/hf_datasets")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--sample-size", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--max-input-tokens", type=int, default=2048)
    parser.add_argument("--prompt-type", choices=["baseline", "cot"], default="cot")
    parser.add_argument("--print-wrong", action="store_true")
    parser.add_argument("--save-path", default="")
    return parser.parse_args()


def collate_fn(batch):
    return {
        "question": [item["question"] for item in batch],
        "answer": [item["answer"] for item in batch],
    }


def build_prompt(tokenizer, question, system_prompt):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    try:
        return tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False,
            enable_thinking=False,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False,
        )


def load_model_and_tokenizer(model_path):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=dtype,
    ).to(device)
    model.eval()
    return model, tokenizer, device


def main():
    args = parse_args()
    torch.manual_seed(args.seed)

    ds = load_dataset(
        "parquet",
        data_files={"train": args.train_file, "test": args.test_file},
        cache_dir=args.cache_dir,
    )
    test_ds = ds["test"]

    generator = torch.Generator()
    generator.manual_seed(args.seed)
    dataloader = DataLoader(
        test_ds,
        batch_size=args.batch_size,
        shuffle=True,
        generator=generator,
        num_workers=args.num_workers,
        collate_fn=collate_fn,
    )

    model, tokenizer, device = load_model_and_tokenizer(args.model_path)
    system_prompt = prompt_baseline if args.prompt_type == "baseline" else promt

    save_file = None
    if args.save_path:
        save_path = Path(args.save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_file = save_path.open("w", encoding="utf-8")

    total = 0
    correct_count = 0
    max_samples = args.sample_size if args.sample_size > 0 else len(test_ds)

    try:
        for batch_idx, batch in enumerate(dataloader, start=1):
            questions = batch["question"]
            answers = batch["answer"]

            remaining = max_samples - total
            if remaining <= 0:
                break
            if len(questions) > remaining:
                questions = questions[:remaining]
                answers = answers[:remaining]

            prompts = [build_prompt(tokenizer, q, system_prompt) for q in questions]
            inputs = tokenizer(
                prompts,
                padding=True,
                truncation=True,
                max_length=args.max_input_tokens,
                return_tensors="pt",
            ).to(device)

            with torch.inference_mode():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=args.max_new_tokens,
                    do_sample=False,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )

            input_len = inputs["input_ids"].shape[1]
            decoded_outputs = tokenizer.batch_decode(
                outputs[:, input_len:],
                skip_special_tokens=True,
            )

            for question, answer, output in zip(questions, answers, decoded_outputs):
                correct, pred, gold = evaluate_prediction(output, answer)
                total += 1
                correct_count += int(correct)

                if save_file:
                    save_file.write(
                        json.dumps(
                            {
                                "question": question,
                                "output": output,
                                "pred": pred,
                                "gold": gold,
                                "correct": correct,
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

                if args.print_wrong and not correct:
                    print(f"[wrong] pred={pred}, gold={gold}")
                    print(output)
                    print("-" * 40)

            accuracy = correct_count / total if total else 0.0
            print(
                f"batch={batch_idx}, total={total}/{max_samples}, "
                f"correct={correct_count}, acc={accuracy:.4%}"
            )

    finally:
        if save_file:
            save_file.close()

    accuracy = correct_count / total if total else 0.0
    print(f"final total={total}, correct={correct_count}, acc={accuracy:.4%}")


if __name__ == "__main__":
    main()
