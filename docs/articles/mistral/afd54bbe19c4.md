---
vendor: mistral
title: Agentic Search：让你的 AI 系统获得更准确、更高效的检索结果
original_title: Agentic Search. More accurate and efficient results from your AI systems.
url: https://mistral.ai/news/agentic-search
date: 2026-08-20
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Agentic Search：让你的 AI 系统获得更准确、更高效的检索结果

Mistral Agentic Search 在 FinanceBench 与 OfficeQA Pro 基准上交付更准确的搜索结果，同时减少轮次、token 消耗与延迟。Agentic Search 是一层检索基础设施，使 AI 系统能够在最复杂的文档内部进行导航、阅读与验证信息。它通过 Mistral Search Toolkit 和 Libraries 提供。

Mistral Agentic Search 让模型能够搜索并浏览组织内最复杂的数据与文档，从而帮助企业从 AI 系统中获得更好的结果。Agentic Search 引入了一个多步检索循环，用于在各个数据源中查找、检查并验证信息，无论数据存储在何处。Agentic Search 通过 [Mistral Search Toolkit](https://docs.mistral.ai/studio/search-toolkit) 提供，并内置于 [Studio](https://mistral.ai/products/studio/) 和 [Vibe](https://mistral.ai/products/vibe/) 的 [Libraries](https://docs.mistral.ai/studio/libraries) 中，为你带来：

- **支持敏感的行业专用数据**。Mistral 可移植、开放的工具帮助你从数据中释放价值，同时不跨越云端或本地部署的隔离边界。
- **更好的搜索结果。**你的模型可以在检索到的文本块之外搜索并导航数据——深入冗长密集的文档内部，或跨多个来源。
- **复用现有索引。**Agentic Search 在你现有的搜索索引之上构建，使用五个工具：`search`、`open`、`navigate`、`read` 和 `grep`。
- **更高准确率。**基于 FinanceBench，Agentic Search 将金融申报文件的**正确率提升至 3 倍**，从 26.7% 提升到 86%。在 OfficeQA Pro 基准中以表格为主、跨多文档的问题上，我们测得 **+45.6 个百分点**的提升（从 6.3% 到 51.9%）。
- **更低延迟与 token 消耗。**定向导航使 Agentic Search 将 p90 **延迟最多降低 39.6%**。更少的重复搜索使 token 消耗最多减少三分之一。

## **数据构筑竞争优势**

竞争优势建立于多年真实运营之上——你的数据、你的流程与你的领域专业知识。专有知识对你的成功至关重要，同时也高度机密，这意味着它们存放在隔离边界、分段部署与自托管平台之后。它们积累在金融申报文件、法律合同、内部资料和政务记录中——这些冗长、密集的文档是传统搜索方法无法有效导航的。

能够持续学习与改进的 Agent 可以帮助你复利式地扩大竞争优势，但出于安全原因，这些 Agent 往往与机密数据和专有知识隔离。要让 AI 产生真正的影响，就需要把前沿推理能力与安全触达最敏感材料检索工具结合起来。

## **传统 RAG 力不从心**

传统的一次性 RAG 检索一组固定文本块，然后让模型一次性给出答案。当答案恰好出现在靠前的检索结果中时，这种方式有效；但当模型必须浏览长篇报告、追踪引用、对比多份文档或验证底层证据时，它就会失灵。

在密集、复杂的数据和文档上，这一局限更加明显。回答问题所需的信息可能分散在多份文档中，或隐藏在某个表格、脚注或条款里。基于一次性 RAG 的搜索之所以无法发挥前沿 AI 的全部能力、无法给出可靠答案，原因有三：

- **无推理的检索：**模型只能基于初始检索选中的文本块作答，即使它们不完整或不相关。模型无法判断自己在回答前需要换一份文档、另一个章节或更多上下文，这限制了模型推理能力的发挥。
- **文本块级别的限制：**关键数据往往存于复杂的多模态文档中。当被问到"*该公司第三季度的有效税率是多少？*"时，索引可能找到了正确的文档，却无法打开它、导航到表格、阅读周边上下文或验证答案。
- **没有迭代：**许多问题需要不止一轮检索才能得到正确答案。模型可能需要细化搜索、检查某份有希望的文档、追踪一条引用、对比多个来源、记住已见过的内容，并在首轮结果不足时尝试新路径。一次性 RAG 无法迈出这些后续步骤。

没有 Agentic Search（一次性检索）

> 仅使用 1953 年各个日历月份实际报告的数值，美国国防及相关活动这些支出数值之和是多少（以百万名义美元计）？

轨迹：1 次 tool_call（仅 search）

`search("national defense expenditures monthly 1953")` → 10 条命中：零散的月度公告（Table 3），每份按财年编排，只覆盖 1953 年的部分月份。

> 我找到了 1953 年 1—6 月的数据。但我需要 1953 年 7—12 月的月度数值才能计算出答案。

使用 Agentic Search

> 仅使用 1953 年各个日历月份实际报告的数值，美国国防及相关活动这些支出数值之和是多少（以百万名义美元计）？

轨迹：3 次 tool_calls（2× search → read）

`search("national defense expenditures monthly 1953")` → 按月公告（不完整年份）

`search("…1953 November December 1954 to date")` → 找到 `treasury_bulletin_1954_02.pdf` 第 15 页（Table 3，含 1953 年全部 12 个月）

`read(treasury_bulletin_1954_02.pdf, p.15)` → 拉取完整的 Table 3

1953 年月度数值

Table 3，单位：百万美元

| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3,632 | 3,501 | 3,789 | 3,891 | 3,746 | 4,056 | 3,890 | 3,519 | 3,787 | 3,647 | 3,540 | 3,465 |

总和 = 44,463。

## **Agentic Search 如何工作**

[Mistral Search Toolkit](https://docs.mistral.ai/en/studio/search-toolkit) 提供开源模块，用于在云端或本地对关键、复杂数据进行摄取、嵌入与索引。Agentic Search 在该索引之上构建，为模型提供五个类似常见文件系统操作的工具：

- `search` 利用现有索引在整个语料库中找到相关文档。
- `open` 打开指定文档。
- `navigate` 在文档内跳转到某个页面、章节或区域。
- `read` 获取该位置的内容。
- `grep` 在已打开的文档中查找某个模式。

模型不再只基于初始 top-*k* 结果作答，而是可以检查检索到的内容、细化搜索、打开相关文档、导航到特定章节，并在回答前阅读原始材料。索引负责找出可能的来源；Agentic Search 决定在这些来源之内与之间进一步检查什么。

### **一次性 RAG**

![None](https://mistral.ai/_astro/pasted-image-4_INqkQ.webp?dpl=6abbd11780b53c00082eea6f)

### **Agentic Search**

![None](https://mistral.ai/_astro/pasted-image-5_Z1Id2ck.webp?dpl=6abbd11780b53c00082eea6f)

这些工具不需要微调或针对特定模型的训练。随着模型在推理和工具使用上变得更强，检索质量也会随之提升，而无需改动基础设施。这是一个关键特性：检索质量随模型能力扩展，而不是被你的分块策略封顶。

## **适合使用 Agentic Search 的场景**

- **长文档。**申报文件、合同、手册、技术规格书和报告，答案可能出现在某一页或某个特定的表格、条款、图或脚注中。
- **跨多个来源的问题。**需要模型先从多份文档中查找、对比或调和证据，然后才能得出结论的研究任务。
- **必须可验证的答案。**财务数字、法律条款、监管引用和运营数据——回答可以引用到稳定、具体的文档位置。
- **表格与结构化文档。**财务报表、政务记录和扫描件 PDF，其含义取决于行列、页面位置或周边上下文，而不只是叙述性文本。

## **索引检索适合以下场景作为起点**

- **直接查找。**简短干净的文档，答案很可能出现在最先检索到的文本块之一中。
- **大批量搜索。**关键词或语义查找，只需返回相关段落，无需对其推理或导航。
- **简单、可预期的问题。**答案的可能来源和位置可以提前预知、额外检索步骤不太可能改善结果的用例。

对于这些搜索，一次性 RAG 通常已经足够。当问题需要模型超越初始结果、深入调查原始材料时，再加上 Agentic Search。无论哪种情况，配置良好的索引始终是正确的基础。

## **更相关的结果，更快的速度**

我们使用开箱即用的 Mistral Search Toolkit 技术栈（默认分块、默认排序、零调优），在两个业界标准评测上对 Agentic Search 进行了基准测试。这些结果是下限而非上限，意味着你可以通过面向具体用例的调优进一步提升结果质量。

在这些基准中，我们用 Mistral Search Toolkit 测试了两个模型：**Mistral Medium 3.5**（MM 3.5）和 **Z.ai GLM-5.2**（GLM-5.2），分别展示较小模型（MM 3.5）与较大模型（GLM-5.2）的表现。

基准结果一致：Agentic 循环带来显著的质量提升，而导航工具在提高准确率的同时减少了浪费的 token、轮次和延迟。我们在自研与第三方模型上观察到相同的性能模式，这表明 Agentic Search 与模型无关，搜索质量应随新模型的推出而持续提升。

### **FinanceBench：368 份 SEC 申报文件，150 个问题**

FinanceBench（Islam 等，2023）测试针对 368 份 SEC 申报文件（10-K / 10-Q / 8-K）的金融问答，平均每份约 147 页，总计约 53,900 页：冗长、表格密集的金融文档。答案由经过人工标注校准的 LLM 评审打分。

我们发现：

- **仅搜索的 Agentic 循环是最大的质量杠杆。**从一次性 RAG 升级到仅搜索的 Agentic 循环，使 MM 3.5 的准确率提升 **+47.3 个百分点**、GLM-5.2 提升 **+52.6 个百分点**——两个模型都约提升 3 倍。因为模型可以迭代搜索，它们能从较差的首轮结果中恢复、细化查询，并把索引当作主动工具使用。
- **导航进一步增加准确率。**加上 open、navigate、read 和 grep 后，准确率再次提升（MM 3.5 **+8.7 个百分点**，GLM-5.2 **+6.7 个百分点**）。这意味着在复杂文档中，定向深入搜索胜过反复的宽泛搜索。
- **检索工具越好，token 与性能效率越高。**带导航的完整循环比仅搜索的循环答对更多问题，且使用更少 token（MM 3.5：**token 用量 -23.9%**，GLM-5.2：**-33.7%**）。这些检索工具不是额外开销——它们用精确导航取代了浪费的重复搜索。
- **关键位置的延迟下降。**在整个 FinanceBench 上，加入导航检索工具改善了延迟：p90 从 **255 秒降至 154 秒**，平均延迟从 **108 秒降至 71 秒**。总体而言，我们看到仅搜索的循环会反复执行宽泛搜索，而导航帮助模型更快地锁定证据。

### **OfficeQA Pro：696 份 Treasury Bulletin，133 个问题**

OfficeQA Pro 是一个基于历史美国财政部公告（Treasury Bulletin）的可验证数值基准：扫描版、表格密集的政府财政 PDF，语料库共 696 份文档、约 89,000 页。我们报告 133 题"pro"子集的首轮通过结果。

我们发现：

- **Agentic Search 与 Agentic 循环 + 导航在更难、可验证的基准上依然有效。**OfficeQA Pro 的答案是数值型的，文档是扫描 PDF，且需要深层表格查找。即便如此，完整 Agentic 循环相对一次性 RAG 仍显著提升准确率：GLM-5.2 达到 **51.9%**（**+45.6 个百分点**），MM 3.5 提升 **+27.1 个百分点**。
- **导航在提升质量的同时减少浪费。**使用完整循环（Agentic 循环 + 导航）使准确率提升**最多 35.6%**（**+7.5 个百分点**，MM 3.5；**+8.3 个百分点、达 19.0%**，GLM-5.2），同时降低 token 消耗。轮次减少**最多 7.0%**（MM 3.5，GLM-5.2 为 **2.3%**）。
- **基准越难，检索循环越重要。**OfficeQA Pro 围绕扫描、表格密集文档中的数值答案构建。一次性 RAG 几乎无从下手，而 Agentic 循环允许模型迭代搜索、检查证据，带来大幅准确率提升。
- **工具栈对文档智能与搜索性能有实质影响。**根据 [Kimi 的研究](https://www.kimi.ai/blog/kimi-k3)，GLM-5.2 在 Claude Code harness 下的 OfficeQA Pro 得分为 41.4%，而在 Mistral harness 下为 51.9%——同一底层模型相差 +10.5 个百分点。

## **开始使用**

在[文档](https://docs.mistral.ai/studio/search/agentic-search)中了解 Agentic Search 的更多信息。你可以跨云端和本地部署，通过以下任一方式上手：

- [Mistral Search Toolkit](https://docs.mistral.ai/studio/search/search-toolkit)。将 Agentic Search 集成到你自己的 Agent、工作流与客户部署中。
- [Libraries](https://docs.mistral.ai/studio/libraries)。在 Studio 和 Vibe 中开箱即用地使用 Agentic Search，无需自建检索系统。

测试 Search Toolkit 最快的方式是 [Search Starter App](https://github.com/mistralai/search-starter-app/tree/main)。它用默认配置为你的语料库创建本地索引，让你无需成为搜索专家即可尝试 Agentic Search。当你准备好配置自己的用例时，可以：

- [设置数据摄取](https://docs.mistral.ai/studio/search/search-toolkit/ingestion)。为你的数据和文件类型选择解析器、分块策略、嵌入模型与抽取器。
- [调优索引与排序](https://docs.mistral.ai/studio/search/search-toolkit/search-index)。管理 Vespa schema、索引行为与相关性配置。
- [扩展检索](https://docs.mistral.ai/studio/search/search-toolkit/retrieval)。在搜索管线中加入查询改写、重排序或混合检索。
