COT_FORMAT = """请严格按照下面的 BBH logical deduction 推理格式输出：

步骤：
1. 题目信息：用中文概括对象、顺序关系和候选选项。
2. 建立顺序：根据题干陈述推导三个对象从左到右或从前到后的排列。
3. 匹配选项：把推导出的排列和每个选项进行比较。
4. 验证结果：确认所选选项唯一且符合所有陈述。

最终答案：(A)/(B)/(C)

注意：“(A)/(B)/(C)”是占位格式，真实输出时只能选择一个选项，例如“最终答案：(A)”。
"""

prompt_CoT_Few_shot = """示例：
问题：
On a shelf, there are three books: a red book, a blue book, and a green book. The red book is to the right of the blue book. The green book is to the right of the red book.
Options:
(A) The red book is the second from the left
(B) The blue book is the second from the left
(C) The green book is the second from the left

步骤：
1. 题目信息：有三本书，需要判断哪一本在左起第二个位置。
2. 建立顺序：红书在蓝书右边，绿书在红书右边，所以从左到右是蓝书、红书、绿书。
3. 匹配选项：左起第二个是红书，对应选项 (A)。
4. 验证结果：排列满足所有关系，因此选项 (A) 唯一正确。

最终答案：(A)
"""

promt = f"""你是一个擅长逻辑顺序推理的助手。请用中文一步一步推导对象顺序，并从候选项中选择正确答案。

硬性要求：
- 必须严格遵守指定格式。
- 只能输出一次“最终答案：(A)”或“最终答案：(B)”或“最终答案：(C)”。
- 最终答案只能是一个选项，不要输出额外解释。
- 不要输出 Markdown 表格、代码块、分隔线或额外结束标记。

{COT_FORMAT}

{prompt_CoT_Few_shot}
"""

prompt = promt

prompt_baseline = """你是一个 BBH logical deduction 选择题考生。请根据题干顺序关系选择正确选项。

最终答案：(A)/(B)/(C)

硬性要求：
- 只能输出一次“最终答案：(A)”或“最终答案：(B)”或“最终答案：(C)”。
- 最终答案只能是一个选项。
- 不要输出解释、代码块、表格或额外结束标记。
"""
'''
baseline(acc) = 41.837%
CoT_direct(acc) = 62.376%
CoT_Fewshot(acc) = 71.428%
self-consistence(acc) = 76.041%
'''