# Qwen Post-Train Playground

一个未完成版的 post-training 学习样例项目，基于本地 Qwen 模型实现若干推理评测流程。当前仓库重点放在 prompt engineering、Chain-of-Thought、self-consistency 和多数据集评测脚手架上；SFT、PPO、DPO 等真正的训练阶段还在待实现列表中。

## Repository Description

Minimal Qwen post-training playground with CoT prompting, self-consistency, and evaluation scripts for GSM8K, SVAMP, StrategyQA, and BBH logical deduction. SFT/PPO/RLHF modules are planned but not implemented yet.

## 项目状态

这是一个学习型、实验型仓库，不是完整 post-train 框架。

已实现：

- 基于 `transformers` 加载本地 Qwen causal language model。
- 针对多个数据集的 prompt 模板、输出解析和准确率评测。
- Zero-shot / few-shot CoT 提示词工程样例。
- Self-consistency：同一问题采样多条回答，对抽取出的最终答案做多数投票。
- GSM8K 批量推理脚本：使用 `DataLoader` 随机加载测试样本，减少逐条 I/O 开销。
- 针对不同任务类型的答案解析：
  - 数学题：抽取最终数值答案。
  - StrategyQA：抽取 `是/否`。
  - BBH logical deduction：抽取 `(A)/(B)/(C)`。

未实现：

- SFT 数据构造、训练脚本和 LoRA/QLoRA 微调。
- Reward model 训练。
- PPO / RLHF 训练流程。
- DPO / IPO / KTO / GRPO 等偏好优化方法。
- 统一配置系统、实验记录、日志管理和结果可视化。
- 训练数据清洗、格式标准化和 dataset registry。
- 模型保存、checkpoint 管理和推理服务化。
- 自动化测试、CI 和完整复现实验脚本。

## 目录结构

```text
.
├── CoT/                 # GSM8K 数学推理样例
├── CoT_svamp/           # SVAMP 数学应用题样例
├── CoT_strategyqa/      # StrategyQA 是/否常识推理样例
├── CoT_bbh_logical/     # BBH logical deduction 选项推理样例
├── data/                # 本地数据文件
└── models -> ...        # 本地模型路径，通常是外部模型目录的软链接
```

每个任务目录通常包含：

```text
baseline.py             # 单次生成并计算准确率
self-consistence.py     # 多次采样 + 多数投票
prompt.py               # prompt / CoT 模板
evaluate.py             # 答案抽取和评测逻辑
```

GSM8K 目录额外包含：

```text
CoT_zero_shot.py         # zero-shot CoT 测试
test.py                  # DataLoader 批量推理测试
```

## 环境准备

建议使用 Python 3.10 和独立 conda 环境。

核心依赖：

```bash
pip install torch transformers datasets
```

项目默认从下面的路径读取本地模型：

```text
models/Qwen3-1.7B
```

当前仓库里的 `models` 可以是一个软链接，例如：

```bash
ln -s /path/to/Qwen/models models
```

不建议把模型权重直接上传到 GitHub。

## 数据准备

当前脚本默认使用本地数据文件：

```text
data/gsm8k/main/train-00000-of-00001.parquet
data/gsm8k/main/test-00000-of-00001.parquet
data/svamp/test.parquet
data/strategyqa/test.json
data/bbh_logical/test-00000-of-00001.parquet
```

如果需要从 Hugging Face Hub 重新下载数据，请注意网络、镜像和缓存路径配置。WSL 环境下建议把 Hugging Face cache 放在 Linux home 或项目内，而不是 Windows 挂载盘。

示例：

```bash
export HF_HOME=$HOME/.cache/huggingface
export HF_DATASETS_CACHE=$HF_HOME/datasets
```

## 运行示例

### GSM8K

```bash
python ./CoT/baseline.py
python ./CoT/CoT_zero_shot.py
python ./CoT/self-consistence.py --sample-size 100 --num-samples 5
```

批量推理：

```bash
python ./CoT/test.py --batch-size 4 --sample-size 32 --prompt-type cot
python ./CoT/test.py --batch-size 4 --save-path outputs/gsm8k_dense_scale.jsonl
```

### SVAMP

```bash
python ./CoT_svamp/baseline.py
python ./CoT_svamp/self-consistence.py --sample-size 100 --num-samples 5
```

### StrategyQA

```bash
python ./CoT_strategyqa/baseline.py
python ./CoT_strategyqa/self-consistence.py --sample-size 100 --num-samples 5
```

### BBH Logical Deduction

```bash
python ./CoT_bbh_logical/baseline.py
python ./CoT_bbh_logical/self-consistence.py --sample-size 100 --num-samples 5
```

如果要跑完整测试集，把 `--sample-size` 设为 `0`：

```bash
python ./CoT_strategyqa/self-consistence.py --sample-size 0 --num-samples 5
```

## 当前实现思路

### Prompt Engineering

`prompt.py` 中定义每个任务的系统提示词和 CoT 格式约束。数学任务要求输出：

```text
最终答案：数字
```

StrategyQA 要求输出：

```text
最终答案：是
```

或：

```text
最终答案：否
```

BBH logical deduction 要求输出：

```text
最终答案：(A)
```

### Evaluation

`evaluate.py` 负责从模型输出中抽取最终答案，并与标准答案归一化后比较。这个模块是评测可信度的关键，因为模型可能输出额外解释、标点、单位或中英文混合答案。

### Self-Consistency

`self-consistence.py` 对同一问题生成多条推理路径：

1. 使用 `do_sample=True` 随机采样。
2. 从每条输出中抽取最终答案。
3. 对最终答案做 `Counter` 多数投票。
4. 将投票答案与 gold answer 比较。

注意：self-consistency 应该对“最终答案”投票，而不是对整段 CoT 文本投票。

## 下一步计划

### SFT

- 统一构造 instruction / response 格式。
- 从 GSM8K、SVAMP、StrategyQA、BBH 中生成 SFT 样本。
- 增加 LoRA / QLoRA 训练脚本。
- 保存 adapter checkpoint 并提供推理加载脚本。

### Preference Optimization

- 构造 chosen / rejected 数据。
- 增加 DPO 训练脚本。
- 对比 base model、SFT model 和 DPO model 的评测结果。

### RLHF / PPO

- 训练 reward model。
- 接入 PPO trainer。
- 设计 reward shaping 和 KL penalty。
- 增加 rollout、采样、打分、更新的完整流程。

### 工程化

- 增加 `requirements.txt` 或 `environment.yml`。
- 增加统一 CLI 和配置文件。
- 增加实验结果保存、日志和可视化。
- 增加单元测试，覆盖答案抽取和评测函数。
- 整理数据下载脚本，避免手动准备数据。

## 注意事项

- 当前代码以可读性和实验验证为主，尚未做充分抽象。
- 模型路径、数据路径和 prompt 内容仍在快速迭代中。
- 不建议上传 `.cache/`、`__pycache__/`、模型权重和大规模输出文件。
- 当前仓库不能代表完整 post-training pipeline，只是一个从 prompt/eval 走向 SFT/RLHF 的起步样例。

## License

待定。
