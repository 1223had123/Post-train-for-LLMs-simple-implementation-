import re


def normalize_option(answer):
    match = re.search(r"\(?\s*([A-Za-z])\s*\)?", str(answer))
    if not match:
        return None
    return f"({match.group(1).upper()})"


def extract_gold(answer):
    return normalize_option(answer)


def extract_pred(output):
    patterns = [
        r"最终答案[:：]\s*\(?\s*([A-Za-z])\s*\)?\s*(?:[。.!！\n\r]|$)",
        r"答案[:：]\s*\(?\s*([A-Za-z])\s*\)?\s*(?:[。.!！\n\r]|$)",
        r"final answer[:：]\s*\(?\s*([A-Za-z])\s*\)?\s*(?:[。.!！\n\r]|$)",
        r"选项[:：]?\s*\(?\s*([A-Za-z])\s*\)?\s*(?:[。.!！\n\r]|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, output, flags=re.IGNORECASE)
        if match:
            return normalize_option(match.group(1))

    matches = []
    for line in output.splitlines():
        if "/" not in line:
            matches.extend(re.findall(r"\(([A-Za-z])\)", line))
    if matches:
        return normalize_option(matches[-1])
    return None


def evaluate_prediction(output, gold_answer):
    pred = extract_pred(output)
    gold = extract_gold(gold_answer)
    return pred == gold, pred, gold


def is_correct(output, gold_answer):
    correct, _, _ = evaluate_prediction(output, gold_answer)
    return correct
