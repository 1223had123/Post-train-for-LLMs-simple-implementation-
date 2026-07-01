COT_FORMAT = """请严格按照下面的 BBH logical deduction 推理格式输出：

步骤：
1. 题目信息：用中文概括对象、顺序关系和候选选项。
2. 建立顺序：根据题干陈述推导三个对象从左到右或从前到后的排列。
3. 匹配选项：把推导出的排列和每个选项进行比较。
4. 验证结果：确认所选选项唯一且符合所有陈述。

最终答案：(A)/(B)/(C)

注意：“(A)/(B)/(C)/(D)/(E)”是占位格式，真实输出时只能选择一个选项，例如“最终答案：(A)”。
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

问题:
The original price of an item is discounted 22%. A customer buys the item at this discounted price using a $20-off coupon. There is no tax on the item, and this was the only item the customer bought. If the customer paid $1.90 more than half the original price of the item, what was the original price of the item?
Options:
(A)$61 
(B)$65 
(C)$67.40 
(D)$70 
(E)$78.20
步骤：
1. 题目信息：商品原价打22%折扣，使用20美元优惠券，最终支付金额比原价的一半多1.90美元。
2. 建立顺序：设原价为x，折扣后价格为0.78x（22%折扣即1-0.22=0.78），使用20美元优惠券后价格为0.78x - 20。根据题意，0.78x - 20 = 0.5x + 1.90。
3. 匹配选项：解方程0.78x - 20 = 0.5x + 1.90，得0.28x = 21.90，x = 21.90 / 0.28 ≈ 78.214，最接近选项是E) $78.20。
4. 验证结果：代入原价78.20，折扣后价格为0.78*78.20 ≈ 60.216，减去20美元为40.216，0.5*78.20 = 39.10，40.216 - 39.10 = 1.116，与题意不符，但最接近选项为E) $78.20。

最终答案：(E)

问题:
Find out which of the following values is the multiple of X, if it is divisible by 9 and 12?
(A)36 (B)15 (C)17 (D)5 (E)7
步骤：
1. 题目信息：需要找出哪个选项是X的倍数，且该数能被9和12整除。
2. 建立顺序：能被9和12整除的数必须是它们的公倍数。9和12的最小公倍数是36。
3. 匹配选项：36是9和12的公倍数，因此是X的倍数。
4. 验证结果：只有选项A（36）符合所有条件。

最终答案：(A)

问题:
If the probability that Stock A will increase in value during the next month is 0.56, and the probability that Stock B will increase in value during the next month is 0.74. What is the greatest value for the probability that neither of these two events will occur?
(A)0.22 (B)0.26 (C)0.37 (D)0.46 (E)0.63
步骤：
1. 题目信息：已知Stock A和Stock B分别有0.56和0.74的概率上涨，求两事件都不发生的最大概率。
2. 建立顺序：要使两事件都不发生的概率最大，需使两事件发生的概率尽可能小，即两事件发生的概率之和尽可能小。
3. 匹配选项：两事件发生的概率之和为0.56 + 0.74 = 1.30，因此两事件都不发生的概率为1 - 1.30 = -0.30，这是不可能的，说明题目中存在矛盾，但根据逻辑最大值，应取最小值。
4. 验证结果：题目中没有给出两事件是否独立，因此无法确定具体概率，但根据逻辑最大值，应选择最小值。

最终答案：(B)

问题:
A trader sold an article at a profit of 20%_ for Rs.360. What is the cost price of the article?
(A)270 (B)300 (C)280 (D)320 (E)315
步骤：
1. 题目信息：一个商人以20%的利润售出一件商品，售价为360元。求该商品的成本价。
2. 建立顺序：利润=售价-成本价，利润=成本价×20%。因此，售价=成本价×1.2。
3. 匹配选项：根据售价=成本价×1.2，可得成本价=售价÷1.2=360÷1.2=300。
4. 验证结果：300×1.2=360，满足条件，因此选项 (B) 唯一正确。

最终答案：(B)
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
CoT_zeroshot_direct(acc) = 63.941%
baseline_direct(acc) = 28.377%
CoT_Fewshot(acc) = 68.367%
self-consistence(acc) = 71.408%
'''
