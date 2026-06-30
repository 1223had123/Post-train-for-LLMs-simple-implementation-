import re

def normalize_number(s: str):
    s = s.strip()
    s = s.replace(",", "")
    s = s.replace("，", "")
    if s.endswith("."):
        s = s[:-1]
    try:
        x = float(s)
        if x.is_integer():
            return str(int(x))
        return str(x)
    except ValueError:
        return s

def extract_gold(answer: str):
    answer = str(answer)
    # GSM8K 标准答案格式：... #### 72
    m = re.search(r"####\s*([-+]?\d[\d,]*(?:\.\d+)?)", answer)
    if m:
        return normalize_number(m.group(1))

    # SVAMP 的 Answer 字段通常就是裸数字，例如 "27"。
    m = re.search(r"[-+]?\d[\d,]*(?:\.\d+)?", answer)
    return normalize_number(m.group(0)) if m else None

def extract_pred(output: str):
    # 优先抽取“最终答案：数字”
    patterns = [
        r"最终答案[:：]\s*([-+]?\d[\d,]*(?:\.\d+)?)",
        r"答案[:：]\s*([-+]?\d[\d,]*(?:\.\d+)?)",
        r"####\s*([-+]?\d[\d,]*(?:\.\d+)?)",
    ]
    for p in patterns:
        m = re.search(p, output)
        if m:
            return normalize_number(m.group(1))

    # 兜底：取输出中的最后一个数字
    nums = re.findall(r"[-+]?\d[\d,]*(?:\.\d+)?", output)
    return normalize_number(nums[-1]) if nums else None

def evaluate_prediction(output: str, gold_answer: str):
    pred = extract_pred(output)
    gold = extract_gold(gold_answer)
    return pred == gold, pred, gold

def is_correct(output: str, gold_answer: str):
    correct, _, _ = evaluate_prediction(output, gold_answer)
    return correct
