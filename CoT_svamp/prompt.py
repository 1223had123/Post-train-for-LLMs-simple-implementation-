COT_FORMAT = """请严格遵循下面的 CoT 步骤要求完成解答,详细参考示例，不要增删标题，不要改变最后一行格式：

步骤：
1. 题目信息：用中文概括题目给出的关键条件。
2. 建立关系：说明要求什么，以及已知条件之间的数量关系。
3. 分步计算：逐步列出计算过程，每一步只做一个主要推导或计算。
4. 验证结果：简单检查计算是否符合题意。

最终答案：<数字>

注意：<数字> 是占位符，真实输出时只保留数字。
"""

promt_CoT_oneshot = """示例：
题目：Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day?

解题步骤：
1. **Janet’s ducks lay 16 eggs per day.**  
   所以，每天她有 16 个鸡蛋。

2. **She eats three for breakfast every morning.**  
   每天她吃 3 个鸡蛋。

3. **She bakes muffins for her friends every day with four.**  
   每天她用 4 个鸡蛋做 muffins。

4. **She sells the remainder at the farmers' market daily for $2 per fresh duck egg.**  
   她每天卖出剩余的鸡蛋，每个鸡蛋卖 $2。

---

现在我们计算她每天卖出的鸡蛋数量：

- 总鸡蛋数：16  
- 吃掉的鸡蛋：3  
- 用于做 muffins 的鸡蛋：4  
- 剩余的鸡蛋 = 16 - 3 - 4 = 9

---

她每天卖出 9 个鸡蛋，每个卖 $2，所以她每天的收入是：

$$
9 * 2 = 18
$$

---

最终答案: 18
"""
prompt_CoT_Few_shot = """
示例1:
问题:
Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
步骤:
1. Natalia sold clips to 48 of her friends in April.  
   所以，她四月份卖了 48 个剪贴簿。

2. She sold half as many clips in May.  
   五月份她卖了 48 的一半，即 48 / 2 = 24 个剪贴簿。

3. We need to find the total number of clips she sold in April and May.  
   总销售量 = 四月份销售量 + 五月份销售量 = 48 + 24 = 72

---

最终答案: 72
-----------------------------------------
示例2:

问题:
Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?
步骤:
1. **Weng earns $12 an hour for babysitting.**  
   所以，她每小时赚 12 美元。

2. **Yesterday, she just did 50 minutes of babysitting.**  
   她昨天做了 50 分钟的 babysitting。

3. **We need to convert 50 minutes to hours.**  
   50 分钟等于 50/60 小时。

4. **Calculate her earnings for 50 minutes of babysitting.**  
   她的收入 = 12 * (50/60) = 10 美元。

---

最终答案: 10

----------------------------------------------------
示例3:

问题:
Betty is saving money for a new wallet which costs $100. Betty has only half of the money she needs. Her parents decided to give her $15 for that purpose, and her grandparents twice as much as her parents. How much more money does Betty need to buy the wallet?
步骤:
1. **Betty is saving money for a new wallet which costs $100.**  
   所以，她需要 $100 来购买钱包。

2. **Betty has only half of the money she needs.**  
   她目前有 $50。

3. **Her parents decided to give her $15 for that purpose.**  
   父母给她 $15。

4. **Her grandparents twice as much as her parents.**  
   奶奶给她 $15 * 2 = $30。

5. **Total money Betty has now:**  
   $50（她自己） + $15（父母） + $30（奶奶） = $50 + $15 + $30 = $95。

6. **Money needed to buy the wallet:**  
   $100。

7. **Money Betty still needs:**  
   $100 - $95 = $5。

最终答案：5
------------------------------------
示例4:
问题:
Julie is reading a 120-page book. Yesterday, she was able to read 12 pages and today, she read twice as many pages as yesterday. If she wants to read half of the remaining pages tomorrow, how many pages should she read?
步骤:
步骤：
1. Julie is reading a 120-page book.  
   所以，这本书共有 120 页。

2. Yesterday, she was able to read 12 pages.  
   昨天她读了 12 页。

3. Today, she read twice as many pages as yesterday.  
   今天她读了 12 * 2 = 24 页。

4. Total pages read so far: 12 + 24 = 36 页。  
   剩余的页数 = 120 - 36 = 84 页。

5. She wants to read half of the remaining pages tomorrow.  
   她想明天读剩余页数的一半，即 84 / 2 = 42 页。

---

最终答案: 42
-------------------------------------
示例5:
问题:
Mark has a garden with flowers. He planted plants of three different colors in it. Ten of them are yellow, and there are 80% more of those in purple. There are only 25% as many green flowers as there are yellow and purple flowers. How many flowers does Mark have in his garden?
步骤:
1. **Mark has a garden with flowers. He planted plants of three different colors in it.**  
   所以，Mark 的花园里有三种颜色的花。

2. **Ten of them are yellow.**  
   黄色花有 10 个。

3. **There are 80% more of those in purple.**  
   紫色花比黄色花多 80%，即 10 + (0.8 of 10) = 10 + 8 = 18 个。

4. **There are only 0.25 as many green flowers as there are yellow and purple flowers.**  
   绿色花的数量是黄色和紫色花的 25%，即 (10 + 18) * 25% = 28 * 0.25 = 7 个。

---

现在我们计算总花数：

- 黄色花：10  
- 紫色花：18  
- 绿色花：7  
- 总花数 = 10 + 18 + 7 = 35

---

最终答案: 35
----------------------------------------
示例6:
问题:
Albert is wondering how much pizza he can eat in one day. He buys 2 large pizzas and 2 small pizzas. A large pizza has 16 slices and a small pizza has 8 slices. If he eats it all, how many pieces does he eat that day?
步骤:
1. **Albert is wondering how much pizza he can eat in one day.**  
   所以，Albert 买了 2 个大披萨和 2 个小披萨。

2. **A large pizza has 16 slices and a small pizza has 8 slices.**  
   每个大披萨有 16 片，每个小披萨有 8 片。

3. **He buys 2 large pizzas and 2 small pizzas.**  
   所以，总共有 2 * 16 + 2 * 8 = 32 + 16 = 48 片。

---

现在我们计算他每天吃掉的披萨片数：

- 大披萨总片数：2 * 16 = 32  
- 小披萨总片数：2 * 8 = 16  
- 总片数：32 + 16 = 48

---

最终答案：48
---------------------------------------------------
示例7:
问题:
Ken created a care package to send to his brother, who was away at boarding school.  Ken placed a box on a scale, and then he poured into the box enough jelly beans to bring the weight to 2 pounds.  Then, he added enough brownies to cause the weight to triple.  Next, he added another 2 pounds of jelly beans.  And finally, he added enough gummy worms to double the weight once again.  What was the final weight of the box of goodies, in pounds?
步骤:
1. **Ken placed a box on a scale, and then he poured into the box enough jelly beans to bring the weight to 2 pounds.**  
   所以，初始重量是 2 磅。

2. **He added enough brownies to cause the weight to triple.**  
   重量变为 2 * 3 = 6 磅。

3. **He added another 2 pounds of jelly beans.**  
   重量变为 6 + 2 = 8 磅。

4. **He added enough gummy worms to double the weight once again.**  
   重量变为 8 * 2 = 16 磅。

最终答案：16

"""


promt = f"""你是一个外教老师，需要通过解决英语数学题来教会用户解题。请用中文一步一步给出解法。

硬性要求：
- 必须严格遵守指定 CoT 格式。
- 只能输出一次“最终答案：数字”这一行。
- 最终答案中的数字只写计算结果，不要带单位、解释、尖括号或其他符号。
- 不要输出 Markdown 表格、代码块、分隔线或额外结束标记。
- 如果题目要求的是美元、人数、数量等，最终答案仍然只写数字。
- 每个示例之间的'-------'是分割符, 不需要输出该格式 
{COT_FORMAT}

{prompt_CoT_Few_shot}
"""

prompt = promt

prompt_baseline = """
你是一个考生，需要解决英语数学题并直接给出最终答案同时必须严格遵循下面的格式

最终答案：<数字>

注意：<数字> 是占位符，真实输出时只保留数字。

硬性要求：
- 必须严格遵守指定格式。
- 只能输出一次“最终答案：数字”这一行。
- 最终答案中的数字只写计算结果，不要带单位、解释、尖括号或其他符号。
- 不要输出 Markdown 表格、代码块、分隔线或额外结束标记。
- 如果题目要求的是美元、人数、数量等，最终答案仍然只写数字。
"""
'''
baseline_acc:38.076%
CoT_shot_Direct: 87.128%
CoT_acc(Few-shot): 90.411%
CoT_acc(self-consistence): 91.1111%
'''