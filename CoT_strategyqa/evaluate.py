import re


def normalize_answer(answer):
    if isinstance(answer, bool):
        return "是" if answer else "否"

    text = str(answer).strip().lower()
    yes_values = {"yes", "y", "true", "t", "1", "是", "对", "正确"}
    no_values = {"no", "n", "false", "f", "0", "否", "不", "错误"}

    if text in yes_values:
        return "是"
    if text in no_values:
        return "否"
    return None


def extract_gold(answer):
    return normalize_answer(answer)


def extract_pred(output):
    patterns = [
        r"最终答案[:：]\s*(是|否|yes|no|true|false)\s*(?:[。.!！\n\r]|$)",
        r"答案[:：]\s*(是|否|yes|no|true|false)\s*(?:[。.!！\n\r]|$)",
        r"final answer[:：]\s*(yes|no|true|false|是|否)\s*(?:[。.!！\n\r]|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, output, flags=re.IGNORECASE)
        if match:
            return normalize_answer(match.group(1))

    candidates = []
    for line in output.splitlines():
        if "/" in line:
            continue
        candidates.extend(
            re.findall(
                r"(?<![A-Za-z])(?:yes|no|true|false)(?![A-Za-z])|[是否]",
                line,
                flags=re.IGNORECASE,
            )
        )
    for candidate in reversed(candidates):
        normalized = normalize_answer(candidate)
        if normalized is not None:
            return normalized
    return None


def evaluate_prediction(output, gold_answer):
    pred = extract_pred(output)
    gold = extract_gold(gold_answer)
    return pred == gold, pred, gold


def is_correct(output, gold_answer):
    correct, _, _ = evaluate_prediction(output, gold_answer)
    return correct
