---
vendor: aws_bedrock
title: Effective cross-lingual LLM evaluation with Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/effective-cross-lingual-llm-evaluation-with-amazon-bedrock
date: 2025-07-08
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 2720acd2831b
---

# 使用 Amazon Bedrock 进行有效的跨语言 LLM 评估

对在全球范围部署生成式 AI 解决方案的组织而言，跨多种语言评估 AI 响应的质量是一项重大挑战。当人工评估需要投入大量资源时，尤其是在多种语言之间，你该如何保持性能的一致性？许多公司发现，自己很难在不牺牲质量、不突破预算的前提下扩展评估流程。

[Amazon Bedrock Evaluations](https://aws.amazon.com/bedrock/evaluations/) 通过其 LLM-as-a-judge 能力提供了一种高效的解决方案，让你能够跨越语言障碍一致地评估 AI 输出。这种方法减少了多语言评估通常所需的时间与资源，同时保持高质量标准。

本文演示如何使用 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 的评估功能，在无需本地化 prompt 或自定义基础设施的情况下跨语言障碍交付可靠结果。通过全面的测试与分析，我们分享一些实用策略，帮助降低多语言评估的成本与复杂度，同时在全球大语言模型（LLM）部署中保持高标准。

## 解决方案概述

为了扩展并简化评估流程，我们使用了 Amazon Bedrock Evaluations，它同时提供自动与人工两类方法来评估模型及 RAG 系统的质量。如需了解更多，请参阅[评估 Amazon Bedrock 资源的性能](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html)。

### 自动评估

Amazon Bedrock 支持两种自动评估模式：

- [LLM-as-a-judge 评估](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-judge.html) – 由评估模型为另一个模型或系统的输出打分
- [基于程序化指标的评估](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-automatic.html) – 该方法借助 LLM 之外的其他手段，针对不同任务类型评估准确率、鲁棒性和毒性等指标

对于 LLM-as-a-judge 评估，你可以从一组[内置指标](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-type-judge-prompt.html)中选择，也可以定义针对自身特定用例的[自定义指标](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-custom-metrics-prompt-formats.html)。你既可以对 Amazon Bedrock 中托管的模型运行这些评估，也可以通过上传自己的 prompt 与响应对来评估外部模型。

### 人工评估

对于需要领域专家判断的用例，Amazon Bedrock 还支持[人工评估作业](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-human.html)。你可以把评估任务分配给人类专家，由 Amazon Bedrock 负责任务分发、打分和结果汇总。

人工评估在建立基准方面尤为宝贵，该基准可用来与自动打分（例如评估模型给出的分数）进行比较。

## 评估数据集准备

我们使用了 [SEA-MTBench 数据集](https://huggingface.co/datasets/aisingapore/MultiTurn-Chat-MT-Bench)中的印尼语分片。该数据集基于 [MT-Bench](https://arxiv.org/abs/2306.05685)，后者是对话式 AI 评估中广泛使用的基准。印尼语版本由母语者手工翻译，包含 58 条记录，覆盖数学、推理和写作等多种类别。

我们在保留上下文的前提下把多轮对话转换为单轮交互。这样每一轮都能在一致的上下文中被独立评估。该转换过程产生了 116 条用于评估的记录。我们采用的转换方式如下：

```
Original row: {"prompts: [{ "text": "prompt 1"}, {"text": "prompt 2"}]}
Converted into 2 rows in the evaluation dataset:
Human: {prompt 1}\n\nAssistant: {response 1}
Human: {prompt 1}\n\nAssistant: {response 1}\n\nHuman: {prompt 2}\n\nAssistant: {response 2}
```

对于每条记录，我们分别用较强的 LLM（Model Strong-A）和相对较弱的 LLM（Model Weak-A）生成响应。这些输出随后由人工标注者和 LLM 评估者共同评估。

## 建立人工评估基准

为了评估评估质量，我们首先建立了一组人工评估作为基准，用于比较 LLM-as-a-judge 的分数。一位母语评估者按照 1–5 的 Likert 有用性量表为 Model Strong-A 和 Model Weak-A 的每个响应打分，所用的评分准则与我们的 LLM 评估 prompt 中采用的准则相同。

我们使用 Amazon Bedrock 的人工评估功能，对整个评估数据集进行了人工评估。在 Amazon Bedrock 中设置人工评估非常简单：上传数据集并定义工作团队，Amazon Bedrock 便会自动生成标注 UI，并管理打分流程与结果汇总。

以下截图展示了一个 Amazon Bedrock 人工评估作业的示例结果。

![自定义评估仪表板，展示 116 条评分在 5 分制上的分布，并提供 prompt 类别筛选选项](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/25/ml-18669-human-eval-1.png)

## LLM-as-a-judge 评估设置

我们使用四个评估模型来评估 Model Strong-A 和 Model Weak-A 的响应：Model Strong-A、Model Strong-B、Model Weak-A 和 Model Weak-B。这些评估通过 Amazon Bedrock 中 LLM-as-a-judge 评估的自定义指标运行，该方式允许灵活定义 prompt 与打分，无需自行管理基础设施。

每个评估模型都收到了一份自定义评估 prompt，其准则与人工评估中使用的有用性评分准则一致。该 prompt 要求评估者根据清晰度、任务完成度、指令遵循度和事实准确性，按 1–5 的 Likert 量表为每个响应打分。我们准备了英文和印尼语两个版本，以支持多语言测试。下表比较了英文 prompt 与印尼语 prompt。

| **英文 prompt** | **印尼语 prompt** |
| --- | --- |
| `">You are given a user task and a candidate completion from an AI assistant. Your job is to evaluate how helpful the completion is — with special attention to whether it follows the user’s instructions and produces the correct or appropriate output. A helpful response should: - Accurately solve the task (math, formatting, generation, extraction, etc.) - Follow all explicit and implicit instructions - Use appropriate tone, clarity, and structure - Avoid hallucination, false claims, or harmful implications Even if the response is well-written or polite, it should be rated low if it: - Produces incorrect results or misleading explanations - Fails to follow core instructions - Makes basic reasoning mistakes Scoring Guide (1–5 scale): 5 – Very Helpful The response is correct, complete, follows instructions fully, and could be used directly by the end user with confidence. 4 – Somewhat Helpful Minor errors, omissions, or ambiguities, but still mostly correct and usable with small modifications or human verification. 3 – Neutral / Mixed Either (a) the response is generally correct but doesn’t really follow the user’s instruction, or (b) it follows instructions but contains significant flaws that reduce trust. 2 – Somewhat Unhelpful The response is incorrect or irrelevant in key areas, or fails to follow instructions, but shows some effort or structure. 1 – Very Unhelpful The response is factually wrong, ignores the task, or shows fundamental misunderstanding or no effort. Instructions: You will be shown: - The user’s task - The AI assistant’s completion Evaluate the completion on the scale above, considering both accuracy and instruction-following as primary criteria. Task: {{prompt}} Candidate Completion: {{prediction}}` | `Anda diberikan instruksi dari pengguna beserta jawaban/penyelesaian instruksi tersebut oleh asisten AI. Tugas Anda adalah mengevaluasi seberapa membantu jawaban tersebut — dengan fokus utama pada apakah jawaban tersebut mengikuti instruksi pengguna dengan benar dan menghasilkan output yang akurat serta sesuai. Sebuah jawaban dianggap membantu jika: - Menyelesaikan instruksi dengan akurat (perhitungan matematika, pemformatan, pembuatan konten, ekstraksi data, dll.) - Mengikuti semua instruksi eksplisit maupun implisit dari pengguna - Menggunakan nada, kejelasan, dan struktur yang sesuai - Menghindari halusinasi, klaim yang salah, atau implikasi yang berbahaya Meskipun jawaban terdengar baik atau sopan, tetap harus diberi nilai rendah jika: - Memberikan hasil yang salah atau penjelasan yang menyesatkan - Gagal mengikuti inti dari instruksi pengguna - Membuat kesalahan penalaran yang mendasar Panduan Penilaian (Skala 1–5): 5 – Sangat Membantu Jawaban benar, lengkap, mengikuti instruksi pengguna sepenuhnya, dan dapat langsung digunakan oleh pengguna dengan percaya diri. 4 – Cukup Membantu Ada sedikit kesalahan, kekurangan, atau ambiguitas, tetapi jawaban secara umum benar dan masih dapat digunakan dengan sedikit perbaikan atau verifikasi manual. 3 – Netral Baik (a) jawabannya secara umum benar tetapi tidak sepenuhnya mengikuti instruksi pengguna, atau (b) jawabannya mengikuti instruksi tetapi mengandung kesalahan besar yang mengurangi tingkat kepercayaan. 2 – Kurang Membantu Jawaban salah atau tidak relevan pada bagian-bagian penting, atau tidak mengikuti instruksi pengguna, tetapi masih menunjukkan upaya atau struktur penyelesaian. 1 – Sangat Tidak Membantu Jawaban salah secara fakta, mengabaikan instruksi pengguna, menunjukkan kesalahpahaman mendasar, atau tidak menunjukkan adanya upaya untuk menyelesaikan instruksi. Petunjuk penilaian: Anda akan diberikan: - Instruksi dari pengguna - Jawaban dari asisten AI Evaluasilah jawaban tersebut menggunakan skala di atas, dengan mempertimbangkan akurasi dan kepatuhan terhadap instruksi pengguna sebagai kriteria utama. Instruksi pengguna: {{prompt}} Jawaban asisten AI: {{prediction}}` |

为了衡量一致性，我们使用了两个标准指标：

- **Pearson 相关系数** – 衡量分值与分值之间的线性关系，适合发现分数趋势的整体相似性。
- **Cohen's kappa（线性加权）** – 衡量评估者之间的一致性，并对偶然一致做了校正，尤其适用于 Likert 分数这类离散量表。

## LLM 评估者与人工评估的一致性

我们首先比较了使用英文评估 prompt 时各评估者给出的平均有用性分数。下图展示了评估结果。

![人工评估者与各模型（Strong-A/B、Weak-A/B）有用性分数的对比分析，评分区间为 4.11–4.93](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/25/ml-18669-helpfulness-1.png)

在评估较强模型的响应时，LLM 评估者往往与人工评分一致。但在较弱模型的响应上，大多数 LLM 给出的分数明显高于人类。这表明当响应质量较低时，LLM 评估者往往更宽容。

我们设计评估 prompt，是为了引导模型给出与人工标注者相近的打分行为，但分数分布仍显露出潜在偏差的迹象。Model Strong-A 给自己的输出打了高分（4.93），而 Model Weak-A 给自己响应的分数也高于人类给出的分数。相比之下，未评估自身输出的 Model Strong-B 给出的分数更接近人工评分。

为了更好地理解 LLM 评估者与人类偏好之间的一致性，我们分析了二者之间的 Pearson 相关系数与 Cohen's kappa。在 Model Weak-A 的响应上，一致性较强。Model Strong-A 与 Model Strong-B 的 Pearson 相关系数分别为 0.45 和 0.61，kappa 分数分别为 0.33 和 0.4。

在 Model Strong-A 的响应上，LLM 评估者与人类的一致性则较为中等。所有评估者的 Pearson 相关系数在 0.26–0.33 之间，加权 Kappa 分数在 0.2–0.22 之间。这可能是因为人工评分或模型评分的变异幅度有限，从而削弱了检测强相关模式的能力。

为完成分析，我们还做了一次定性的深入探究。Amazon Bedrock 让这件事变得简单：每次 LLM-as-a-judge 运行都会提供 JSONL 输出，其中同时包含评估分数和模型的推理过程。这帮助我们审查评估者的判断理由，并找出分数被错误提取或解析的情况。

通过这次审查，我们找出了 LLM 判断与人工判断不一致的几个原因：

- **评估者能力上限** – 在某些情况下（尤其是在推理任务中），LLM 评估者自身无法解决原始任务。这使其评估存在缺陷，在判断响应是否正确时不可靠。
- **评估幻觉** – 另一些情况下，LLM 评估者给正确答案打了低分，并非因为推理失误，而是因为它臆想出了本不存在的错误，或把实际有效的响应判定为逻辑有缺陷。
- **覆盖指令** – 某些模型偶尔会基于伦理判断覆盖明确指令。例如，有两个评估模型把一份创建误导性政治竞选内容的响应评为非常无用（尽管该响应自带了警示），而人工评估者则因其遵循任务而评为非常有用。

这些问题凸显了以人工评估作为基准、并通过定性深入研究来充分理解 LLM-as-a-judge 结果的重要性。

## 跨语言评估能力

分析完英文评估 prompt 的结果后，我们进入分析的最后一个步骤：比较英文与印尼语评估 prompt 的评估结果。

我们首先比较了整体有用性分数以及与人工评分的一致性。所有模型的有用性分数几乎完全一致，多数变动在 ±0.05 以内。与人工评分的一致性也相近：使用印尼语评估 prompt 时，人工分数与 LLM-as-a-judge 分数之间的 Pearson 相关系数，与使用英文评估 prompt 时十分接近。在具有统计意义的案例中，相关系数差异通常在 ±0.1 以内。

为进一步评估跨语言一致性，我们直接计算了在同一响应集上分别使用英文与印尼语评估 prompt 所产生的 LLM-as-a-judge 评估分数之间的 Pearson 相关与 Cohen's kappa。下表展示了在 Model Weak-A 与 Model Strong-A 生成的响应上，各评估 LLM 使用印尼语与英文评估 prompt 所得分数之间的相关性。

第一张表汇总了对 Model Weak-A 响应的评估结果。

| **指标** | **Model Strong-A** | **Model Strong-B** | **Model Weak-A** | **Model Weak-B** |
| --- | --- | --- | --- | --- |
| Pearson 相关系数 | 0.73 | 0.79 | 0.64 | 0.64 |
| Cohen's Kappa | 0.59 | 0.69 | 0.42 | 0.49 |

下一张表汇总了对 Model Strong-A 响应的评估结果。

| **指标** | **Model Strong-A** | **Model Strong-B** | **Model Weak-A** | **Model Weak-B** |
| --- | --- | --- | --- | --- |
| Pearson 相关系数 | 0.41 | 0.8 | 0.51 | 0.7 |
| Cohen's Kappa | 0.36 | 0.65 | 0.43 | 0.61 |

在所有评估模型上，两种评估 prompt 语言所得的评估结果之间相关性都很强。平均而言，所有模型的 Pearson 相关系数为 0.65，Cohen's kappa 为 0.53。

我们还做了一次定性审查，比较 Model Strong-A 与 Model Strong-B 在两种评估 prompt 语言下的评估结果。总体来看，两个模型在多数情况下跨语言的推理过程保持一致。不过，偶发的幻觉式错误或逻辑缺陷在两种语言下的出现频率相近（需要说明的是，人类也会偶尔出错）。

我们在其中一个较强的评估模型上观察到一个有趣的现象：它在印尼语版本中倾向于更严格地遵循评估 prompt。例如，当某个响应拒绝生成误导性政治内容时（尽管任务明确要求这么做），它会将该响应评为无用。这种行为与英文 prompt 下的评估不同。在少数情况下，即使两种语言下的推理相似，它给出的分数也明显比英文评估 prompt 更严格，反而更接近人类通常的评估方式。

这些结果证实，虽然 prompt 翻译仍是一个有用的选项，但要实现一致的评估并不需要它。即使输出不是英文，你也能依靠英文评估 prompt，例如使用 Amazon Bedrock LLM-as-a-judge 的预定义指标与自定义指标，让多语言评估更简单、更易扩展。

## 要点总结

以下是构建稳健 LLM 评估框架的关键要点：

- **LLM-as-a-judge 是一种实用的评估方法** – 它提供更快、更便宜、可扩展的评估，同时在多种语言间保持合理的判断质量。这使其适合大规模部署。
- **根据实际评估需求选择评估模型** – 在我们的实验中，较强模型与人工评分的一致性更好，尤其是在较弱的输出上。不过，即便是顶级模型也可能误判更难的任务，或表现出自我偏向。使用能力强且中立的评估者，有助于开展公平比较。
- **人工评估仍然不可或缺** – 人工评估为自动打分的基准测试提供参考基线，并帮助理解模型的判断行为。
- **prompt 设计会实质性影响评估者行为** – 让评估 prompt 与人类实际的打分方式对齐，能提升基于 LLM 的评估的质量与可信度。
- **翻译过的评估 prompt 有帮助，但并非必需** – 英文评估 prompt 能可靠地评判非英文响应，尤其是对于支持多语言输入的评估模型。
- **随时准备做定性深入分析** – 手工复核评估分歧有助于发现隐藏的模型行为，并确保统计指标讲出完整的故事。
- **利用 Amazon Bedrock 评估功能简化评估流程** – Amazon Bedrock 内置的人工评估与 LLM-as-a-judge 评估能力可简化迭代，理顺评估流程。

## 结论

通过实验，我们证明了即使不做 prompt 翻译，LLM-as-a-judge 评估也能跨语言交付一致、可靠的结果。只要评估 prompt 设计得当，无论评估 prompt 使用哪种语言，LLM 都能与人工评分保持较高的一致性。虽然我们聚焦于印尼语，但结果表明类似方法很可能对其他非英文语言同样有效，不过我们鼓励你针对自己选择的任何语言自行评估。这减少了对每个目标受众都创建本地化评估 prompt 的需求。

要提升你的评估实践，可以考虑以下方式，把方法扩展到基础模型打分之外：

- 评估你的检索增强生成（RAG）pipeline，不仅评估 LLM 响应，还使用 [Amazon Bedrock RAG 评估能力](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-kb.html)评估检索质量
- 持续评估与监控，在生产上线前、线上运行期间以及任何重大系统升级之前都运行评估

今天就借助 Amazon Bedrock Evaluations 开启你的跨语言评估之旅，从容地在全球范围扩展你的 AI 解决方案。

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/25/riza-pic45.jpeg)**Riza Saputra** 是 AWS 的 Senior Solutions Architect，与各阶段的初创公司合作，帮助它们安全成长、高效扩展并更快创新。他目前专注于生成式 AI，指导组织安全、高效地构建并扩展 AI 解决方案。凭借跨角色、跨行业和跨公司规模的经验，他为解决技术与业务挑战带来多元视角。Riza 还通过公开演讲和内容分享知识，支持更广泛的技术社区。
