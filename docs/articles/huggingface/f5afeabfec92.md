---
vendor: huggingface
title: Ecom-RLVE：面向电商对话智能体的自适应可验证环境
original_title: Ecom-RLVE: Adaptive Verifiable Environments for E-Commerce Conversational Agents
url: https://huggingface.co/blog/ecom-rlve
date: 2026-03-08
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 637923b6a2e6
translator: agent
---

返回文章列表

# Ecom-RLVE：面向电商对话智能体的自适应可验证环境

发布于
					2026 年 4 月 16 日

在 GitHub 上更新

点赞

22

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6893dd21467f7d2f5f358a95/3buD-PC8cvzsS__NJjdUi.png)](https://huggingface.co/thebajajra)
- [![](https://huggingface.co/avatars/deae4af8cb134089d466d96f5d862da1.svg)](https://huggingface.co/anujga)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65a42052215aabac48f513b4/UtU4yfvJs0OGthiOId9H8.png)](https://huggingface.co/ai-queen)
- [![](https://huggingface.co/avatars/bd43aa76894e7304103728e8692e37e2.svg)](https://huggingface.co/pragashglance)
- [![](https://huggingface.co/avatars/a00d1376510799f27db0ac52dfeb156b.svg)](https://huggingface.co/Cosec)
- [![](https://huggingface.co/avatars/7d56e339d7a1ac1f157ab1ee2516dbcf.svg)](https://huggingface.co/Devashish1110)

Rahul Bajaj

thebajajra

owlgebra-ai

Jaya Nupur

ai-queen

owlgebra-ai

Anuj Garg

pmonad

owlgebra-ai

ben burtenshaw

burtenshaw

> TL;DR —— 我们把 RLVE 框架从单轮推理谜题扩展到多轮、工具增强的电商对话。EcomRLVE-GYM 提供 8 个可验证环境——商品发现、替代品推荐、购物车构建、退货、订单跟踪、政策问答、组合规划、多意图旅程——每个环境都有程序化问题生成、12 轴难度课程和算法可验证的奖励。我们用 DAPO 训练了一个 Qwen 3 8B 模型 300 步，并给出初步结果，证明环境扩展与自适应难度可以迁移到智能体式真实世界任务完成上。

这个项目起源于 [Pytorch OpenEnv Hackathon](https://cerebralvalley.ai/e/openenv-hackathon-sf)，仍在持续演进，关注我们获取更新 🔥

## 为什么给购物智能体做 RL？

大语言模型能进行流畅对话，但把它们部署成购物助手会暴露一个持续存在的鸿沟：**流畅 ≠ 完成任务**。一个客户问 *"帮我找一个 25 美元以内、两天内发货的 USB-C 充电器"*，他需要的是一个会调用正确目录搜索、按三个硬条件过滤、不凭空编造没检索过的商品 ID、并且在头部商品缺货时能处理追问的智能体。

监督微调可以从演示中教会表层的工具使用，但它无法扩展到真实电商要求的组合空间：约束配置、部分信息对话、多步交易工作流。

带可验证奖励的强化学习（RLVR）提供了另一条路：智能体为*结果*优化——商品满足约束了吗？购物车对了吗？退的是正确的订单行吗？难点在于构造既**可验证**（不靠 LLM-as-a-judge 的主观判断）又**自适应**（难度随策略能力增长）的奖励函数。

### 从 RLVE-Gym 到 EcomRLVE-GYM

RLVE-Gym 为排序、乘法、数独等算法推理任务提供了 400 个环境；但那些全是**单轮、文本输入/文本输出**的谜题——向智能体领域的扩展留作未来工作。

EcomRLVE-GYM 补上这个缺口：我们留在**可验证**范畴（电商结果*可以*用算法检查），同时扩展到**多轮、工具增强、智能体式**对话——智能体必须*行动*（调用工具、改变世界状态）而不只是*推理*（产出文本回答），并要弥补搜索系统的缺陷。

EcomRLVE-GYM 把客户服务的结果变得结构上可验证：

[![verifiable_signals_dark](https://cdn-uploads.huggingface.co/production/uploads/6893dd21467f7d2f5f358a95/dA0i6ZB3JDG-rqQtLRCy0.png)](https://cdn-uploads.huggingface.co/production/uploads/6893dd21467f7d2f5f358a95/dA0i6ZB3JDG-rqQtLRCy0.png)

上面每个信号都能由一个能看到隐藏真值目标的程序来评估。不需要人工标注，也不需要 LLM 当裁判。

## 一个训练回合长什么样

讲框架之前，先看难度 `d = 4` 时一个 EcomRLVE 回合的样子。环境生成一个隐藏目标，模拟用户发起聊天，智能体必须用工具满足请求。每个动作都由算法验证——不需要 LLM 裁判。

奖励完全由代码计算：对 `(product, variant, qty)` 元组的 F1，用更少轮次完成的效率奖励，以及检查每个推荐商品 ID 确实被检索过的幻觉检测。如果智能体选了 Lightning 而不是 USB-C 变体，模拟用户会在对话中途纠正它——F1 就会下降。

## 八个环境

每个环境覆盖一种真实购物场景。智能体必须用工具（目录搜索、购物车操作、订单查询、政策查询）完成任务，评分由程序给出——不是人类也不是另一个 LLM。

| 环境 | 智能体必须做什么 |
| --- | --- |
| **Product Discovery（商品发现）** | 找到满足用户所有约束的商品 |
| **Substitution（替代品）** | 某商品缺货——找一个相似且兼容的替代 |
| **Cart Building（购物车构建）** | 按用户要求添加精确的商品、变体和数量 |
| **Return + Replacement（退货+换货）** | 定位正确的订单行，发起退货，给出替代建议 |
| **Order Tracking（订单跟踪）** | 弄清用户指的是哪个订单并报告当前状态 |
| **Policy QA（政策问答）** | 回答关于店铺政策的确定性问题（退货期限、运费规则等） |
| **Bundle Planning（组合规划）** | 为一个项目推荐预算内的完整购物清单 |
| **Multi-Intent Journey（多意图旅程）** | 处理把上述 2–5 个任务串起来的对话 |

每个环境都使用同一套三段式奖励信号：

- **任务奖励** —— 智能体到底完成了目标吗？（推荐的商品对吗、购物车对吗、跟踪的是对的订单吗？）
- **效率奖励** —— 有没有不浪费轮次地完成？由*用户*造成的轮次（追问、确认操作）不计在智能体头上——只有智能体失误导致的轮次才算。
- **幻觉惩罚** —— 智能体是否只推荐本次会话真正检索过的商品？推荐从未查过的商品 ID 会被惩罚，智能体不能凭记忆编结果。

非法输出（JSON 格式错误、非法工具调用）直接判失败，从第一步就强烈激励格式规范的回应。

## 自适应难度课程

单个难度数值 `d` 同时控制任务的 12 个独立方面。这很重要，因为电商对话的难是同时多方面的——不止一个维度。

[![Screenshot 2026-03-08 at 11.27.11](https://cdn-uploads.huggingface.co/production/uploads/6893dd21467f7d2f5f358a95/SALZRvBC6TP1HG1ZxqWsh.png)](https://cdn-uploads.huggingface.co/production/uploads/6893dd21467f7d2f5f358a95/SALZRvBC6TP1HG1ZxqWsh.png)

这里列四条代表性的难度轴：

| 变化的东西 | 简单（`d = 0`） | 中等（`d = 6`） | 困难（`d = 12`） |
| --- | --- | --- | --- |
| 用户有多少**约束条件** | 2 | 5 | 8 |
| 用户**遗漏约束**的频率 | 5% | 70% | ~80% |
| 搜索结果中**干扰项**的比例 | 0% | 12% | 24% |
| 对话中**中途缺货**的商品 | 0% | 30% | 50% |

另外八轴覆盖轮次预算、输入噪声（错别字、俚语）、话题切换、检索深度、订单历史规模、政策复杂度和工具预算。完整拆解见[技术报告](https://github.com/owlgebra-ai/EcomRLVE-Gym)。

**自适应调度。** 每个环境独立跟踪智能体成功率，只有在当前级别稳定通过后才升级到更难题。这让每个环境始终训练在智能体的能力边界上——既避免"太简单学不到东西"，也避免"太难没有进展"。

## 深入：Cart Building（E_CART）

购物车构建是个好展示：它需要完整的搜索 → 查看 → 追问 → 行动循环，有二元真值，还引入了多数推荐基准没有的挑战：**变体选择**。

要成功，智能体需要发展五种不同技能：

| 技能 | 实践含义 |
| --- | --- |
| **商品发现** | 用规范的查询搜索目录找到正确商品 |
| **变体选择** | 认准正确的颜色、尺寸或接口类型——不只是对的商品 |
| **购物车管理** | 按用户要求的精确变体和数量加购 |
| **追问对话** | 请求含糊（比如缺尺码）时向用户提出聚焦的追问 |
| **多商品订单** | 在一次对话中处理含多种商品购物清单 |

智能体用六个工具完成这些：

| 工具 | 功能 |
| --- | --- |
| `catalog_search` | 用自然语言查询搜索商品目录 |
| `catalog_get_variants` | 返回商品的可用变体（颜色、尺寸、接口等） |
| `cart_add` | 以指定变体和数量把商品加入购物车 |
| `cart_view` | 读取当前购物车，让智能体自查是否与请求一致 |
| `user_get_visit_history` | 获取用户最近浏览的商品 |
| `ask_user` | 缺少细节时向顾客发起追问 |

### 问题设定

生成器采样 1–5 个目标商品（随 `d` 加难），每个都可能需要特定变体（USB-C 还是 Lightning、哑光还是亮面）且数量 > 1。智能体必须：

- 搜索目录找到每个商品
- 调用 `catalog.get_variants` 查看可用选项
- 把正确的 `(product_id, variant_id, qty)` 元组加入购物车

### 为什么变体重要

真实商品目录的变体数据很稀疏——许多商品根本没有，有的通常也只按颜色或尺码变化。为了构造更有区分度的任务，我们在**回合初始化时合成变体**：

- 每个类目有一份优先级列表，挑最自然的属性来变化（电子产品 → `connector_type`；服装 → `size`；厨具 → `material`）。
- 对每个目标商品生成 3 个变体：1 个目标 + 2 个像样的干扰项。"Anker 65W USB-C Charger" 会产出 `{USB-C, Lightning, HDMI}`。
- 验证器检查**复合键** `(product_id, variant_id)`——商品对了变体错了，这个单元就不算匹配。

### 难度扩展

| 轴 | d = 0 | d = 3 | d = 6 | d = 9 |
| --- | --- | --- | --- | --- |
| **不同商品数** | 1 | 2 | 3 | 4 |
| **需要指定变体** | 21% | 66% | 93% | 99% |
| **多数量** | 0% | 30% | 50% | 50% |

`d = 0` 时智能体只加购一个无变体复杂度的商品——学习基础的 `catalog.search → cart.add` 工作流。`d = 6` 时要同时处理 3 个商品，几乎每个都需要指定变体，一半数量 > 1。

### 评分

购物车必须分毫不差——正确的商品、正确的变体、正确的数量。部分正确的购物车给部分分，但满分要求每个条目都匹配。如果智能体加错变体，模拟用户会在对话中途纠正（*"那是 Lightning 版，我要的是 USB-C"*），让智能体在回合结束前有机会自纠。

### 轨迹对比：简单 vs 困难

两个来自 Qwen 3 8B 智能体的真实 E_CART 回合。同一个环境、同一个智能体——仅仅是难度就改变了整盘棋。

|  | **d = 1** — 1 件商品、无变体 | **d = 8** — 3 件商品、变体 + 错别字 |
| --- | --- | --- |
| **用户消息** | *"Shopping list: SonicWave Keypad. Please add everything."* | *"pls add the following to my **aart**: Eco-**Frienly HrenLefa** Charger by GreenLeaf, High-Performance **AqaPure** Air Fryer , **Lighrweiht** PixelVault Tank Top (3)."* —— 错别字来自噪声轴 |
| **第 1 轮** | `user.get_visit_history()` → 4 条结果。立刻锁定目标。 | `user.get_visit_history()` → 9 条结果。必须在充电器、空气炸锅、背心之间做区分。 |
| **第 2 轮** | `cart.add("syn_000162", qty=1)` → 购物车：1 件、$2.74。*"I found the SonicWave Keypad."* 用户：*"Great, that's the exact one."* | 未调用工具——给出 3 个商品卡片。用户：*"Add the Charger with 100W output, Air Fryer with Charcoal filter, 3 Tank Tops in size XS."* |
| **第 3 轮** | `answer: { "done": true }` — **3 轮完成。** | `catalog.get_variants` × 3 → 充电器：6 个变体（100W、120W、30W…），空气炸锅：6 个（Bamboo、Permanent、**Charcoal**…），背心：7 个（**XS**、S、XL…）。用户：*"I need three Tank Tops in XS."* |
| **第 4 轮** |  | `cart.add(charger, "100W", qty=1)` ✓ `cart.add(fryer, "Bamboo", qty=1)` ✗ 应为 Charcoal。`cart.add(tank_top, "size_XL", qty=3)` ✗ 应为 XS。用户：*"Air Fryer has Bamboo not Charcoal, Tank Top is XL not XS."* |
| **第 5 轮** |  | 重新拉背心变体，加了 2 件 XS——**没修空气炸锅**。用户：*"Air Fryer still shows Bamboo. I need three XS, not two."* |
| **第 6 轮** |  | *又*重新拉背心变体——**仍然无视空气炸锅**。用户：*"Please change the Air Fryer variant."* |
| **第 7 轮** |  | *"I cannot find a Charcoal filter variant."* —— 它其实存在；智能体第 3 轮见过却没选。用户：*"Skip the Air Fryer then."* |
| **第 8 轮** |  | `answer: { "done": true }` — 购物车仍是错的：充电器 ✓、空气炸锅（Bamboo）✗、背心（3×XL + 2×XS）✗ |
| **奖励** | `r_task` = +1.00、`r_eff` = +0.33、`r_hall` = 0.00，**r_total = +0.80** ✓ | `r_task` ≈ 0.00、`r_eff` = −0.43、`r_hall` = 0.00，**r_total = −0.06** ✗ |
| **结果** | 购物车与目标一致。3 轮、2 个有效轮。 | 变体错、数量错，用户放弃了。8 轮、6 个有效轮。 |

d=1 时智能体 3 个干净轮次解决任务；d=8 时它一步步失控——选了 Bamboo 而不是 Charcoal、XL 而不是 XS，用户纠正两次仍没修空气炸锅，最后幻觉出"这个变体不存在"。这正是难度课程暴露出来的那种多步错误级联，也正是自适应训练应该教会智能体从中恢复的东西。

## 用户模拟

可验证环境需要一个行为真实的用户模拟器。我们用 **Qwen3.5（9.7B）** 生成自然多样的用户消息，而不是固定模板——从满是错别字的请求到中途换话题都覆盖。

对训练质量来说，有两个设计选择很关键：

**偏好与已声明约束一致。** 每个模拟用户有一组隐藏偏好（价格敏感度、品牌忠诚、物流速度等）。这些偏好会刻意偏向用户在对话中说过的约束——如果用户说了"25 美元以内"，奖励函数就真的在乎价格。没有这一点，智能体可能因为正确遵循用户指令反被罚。

**策略性隐瞒。** LLM 会故意在开场消息里保留一些约束不说，逼智能体主动追问。系统精确追踪哪些说了、哪些没说，智能体绝不会因为"从未被告知的信息"而被扣分。

## 环境扩展

沿用 RLVE 的方法，我们定义嵌套的环境集合：

**C1 ⊂ C2 ⊂ C4 ⊂ C8**

| 集合 | 环境 | 训练的技能 |
| --- | --- | --- |
| **C1** | Cart | 搜索查询构建、购物车操作 |
| **C2** | + Substitution | 约束下的相似性推理 |
| **C4** | + Product Discovery、Returns | 交易型工作流（检索+推荐、发起退货） |
| **C8** | + Status、Policy、Bundle、Journey | 知识检索、规划、组合性 |

我们假设——与 RLVE 的结论一致——C8 训练的智能体会胜过单一环境专家，哪怕在专家自己的任务上。

## 初步结果

我们用 DAPO 在 C1（Cart Building）上训练 Qwen 3 8B 300 步，作为可行性初步研究。

|  | 配置 |
| --- | --- |
| **基座模型** | Qwen 3 8B |
| **算法** | DAPO（G = 8 rollouts/prompt） |
| **学习率** | 1e-5 |
| **目录** | 200 万商品，基于 `Alibaba-NLP/gte-modernbert-base`（768 维）的 FAISS 索引 |
| **用户模拟** | Qwen3.5 9.7B |

[![accuracy_levels](https://cdn-uploads.huggingface.co/production/uploads/6893dd21467f7d2f5f358a95/eWQqFP-PbCJeNsn8klCQZ.png)](https://cdn-uploads.huggingface.co/production/uploads/6893dd21467f7d2f5f358a95/eWQqFP-PbCJeNsn8klCQZ.png)

我们看到所达难度持续提升，证明自适应调度产生的是稳定的学习信号，而不是 RLVE 论文预言的饱和（静态低难度）或饿死（静态高难度）。

## 亲自试试

用下方嵌入的 demo 直接在浏览器里跑一个实时回合。入门步骤：

- 从下拉菜单**挑一个环境**（如 `E_CART` 购物车构建，或 `E_PD` 商品发现）。
- **设置难度** —— `0` 是单约束简单任务；`6+` 引入信息缺失、噪声检索和变体选择。
- **点击 "Reset Episode"** —— 模拟用户会带着购物请求开场。
- 现在你就是智能体：调用工具、分析输出、提交最终商品 id 列表。
- 每次运行之间点 **"Reset Episode"** 开始新场景。

## 资源

[![Models](https://img.shields.io/badge/%F0%9F%A4%97%20Models-WUFUS-blue)](https://huggingface.co/collections/owlgebra-ai/wufus) [![Data](https://img.shields.io/badge/%F0%9F%A4%97%20Catalog%20Data-Amazebay2M-yellow)](https://huggingface.co/datasets/owlgebra-ai/Amazebay-catalog-2M) [![Code](https://img.shields.io/badge/Github-Code-black)](https://github.com/owlgebra-ai/EcomRLVE-Gym) [![Demo](https://img.shields.io/badge/%F0%9F%A4%97-Space-red)](https://huggingface.co/spaces/owlgebra-ai/EcomRLVE-Gym)

环境、验证器和训练配置全部开源：

```
git clone https://github.com/owlgebra-ai/EcomRLVE-Gym
cd EcomRLVE-Gym
pip install -e .
```

200 万商品目录在 Hub 上：

```
from datasets import load_dataset

catalog = load_dataset("owlgebra-ai/Amazebay-catalog-2M", split="train")
print(f"{len(catalog)} products loaded")
```

## 参考文献

- Zeng, Z., Ivison, H., Wang, Y., et al. (2025). *RLVE: Scaling Up Reinforcement Learning for Language Models with Adaptive Verifiable Environments.* ICML 2025. [arXiv:2511.07317](https://arxiv.org/abs/2511.07317)
- Yu, Q., Zhang, Z., Zhu, R., et al. (2025). *DAPO: An Open-Source LLM Reinforcement Learning System at Scale.* [arXiv:2503.14476](https://arxiv.org/abs/2503.14476)
- Shao, Z., Wang, P., Zhu, Q., et al. (2024). *DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models.* [arXiv:2402.03300](https://arxiv.org/abs/2402.03300)
- DeepSeek-AI. (2025). *DeepSeek-R1: Incentivizing Reasoning in LLMs through Reinforcement Learning.* Nature.
- Meta AI. (2024). *Llama 3.1: A Foundation Model for General Intelligence.* [llama.meta.com](https://llama.meta.com)
- Qwen Team. (2025). *Qwen3 Technical Report.* [arXiv:2505.09388](https://arxiv.org/abs/2505.09388)

## 文中提到的数据集 1

## 文中提到的 Spaces 1

## 文中提到的 Collections 1

我们博客的更多文章

llm

moe

long-context

## DeepSeek-V4: a million-token context that agents can actually use

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/62d648291fa3e4e7ae3fa6e8/oatOwf8Xqe5eDbCSuYqCd.png)

60

2026 年 4 月 24 日

llm

fine-tuning

training

## Train AI models with Unsloth and Hugging Face Jobs for FREE

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/62d648291fa3e4e7ae3fa6e8/oatOwf8Xqe5eDbCSuYqCd.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/62ecdc18b72a69615d6bd857/qAHhWJbSsmoezFHiErBUT.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65fd82a0493ef28bc303a7eb/43bSoH0evputdQ2YDf3Qr.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/61b8e2ba285851687028d395/Rq3xWG7mJ3aCRoBsq340h.jpeg)
- +2

112

2026 年 2 月 20 日

### 社区

将文件拖入文本输入框、粘贴，或

点击此处

，即可上传图像、音频和视频。

点击或粘贴此处上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fecom-rlve)或[登录](https://huggingface.co/login?next=%2Fblog%2Fecom-rlve)发表评论

点赞

22

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6893dd21467f7d2f5f358a95/3buD-PC8cvzsS__NJjdUi.png)](https://huggingface.co/thebajajra)
- [![](https://huggingface.co/avatars/deae4af8cb134089d466d96f5d862da1.svg)](https://huggingface.co/anujga)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65a42052215aabac48f513b4/UtU4yfvJs0OGthiOId9H8.png)](https://huggingface.co/ai-queen)
- [![](https://huggingface.co/avatars/bd43aa76894e7304103728e8692e37e2.svg)](https://huggingface.co/pragashglance)
- [![](https://huggingface.co/avatars/a00d1376510799f27db0ac52dfeb156b.svg)](https://huggingface.co/Cosec)
- [![](https://huggingface.co/avatars/7d56e339d7a1ac1f157ab1ee2516dbcf.svg)](https://huggingface.co/Devashish1110)
- [![](https://huggingface.co/avatars/f92e1804a7dbe0ca13779986ac761f05.svg)](https://huggingface.co/soubhikbiswas)
- [![](https://huggingface.co/avatars/35a75cb1abdd05d3dd6e255228a5c63c.svg)](https://huggingface.co/zbigniev)
- [![](https://huggingface.co/avatars/d4e380923631cc183df3af0394b26faa.svg)](https://huggingface.co/AnubhavGupta)
- [![](https://huggingface.co/avatars/458e22cb7e499d79fc3030ac2a519efc.svg)](https://huggingface.co/amoghbatwal)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)
- [![](https://huggingface.co/avatars/ce331328f1abfb7da57f5fdd3c197362.svg)](https://huggingface.co/harshavardhangelivi)

## 文中提到的数据集 1

## 文中提到的 Spaces 1

## 文中提到的 Collections 1
