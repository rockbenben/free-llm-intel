---
vendor: mistral
title: Mistral OCR
original_title: Mistral OCR
url: https://mistral.ai/news/mistral-ocr
date: 2025-03-06
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Mistral OCR

**注意：此模型已弃用**

Mistral OCR 已不再维护，已被[我们最新的、更强大的 OCR 模型](https://mistral.ai/fr/news/ocr-4/)取代。

纵观历史，信息抽象与检索能力的进步一直在推动人类前进。从象形文字到纸莎草，从印刷机到数字化，每一次飞跃都让人类知识更易获取、更可行动，进而催生更多创新。

今天，我们正站在下一次大飞跃的门槛上——释放所有数字化信息的集体智能。世界上约 [90%](https://resources.data.gov/glossary/unstructured-data/) 的组织数据以文档形式存储，为了释放这一潜力，我们推出 [Mistral OCR](https://docs.mistral.ai/studio-api/document-processing/overview)。

Mistral OCR 是一个文档理解 API，为文档理解树立了新标准。与其他模型不同，Mistral OCR 以空前的精度与理解力洞悉文档的每个元素——媒体、文本、表格、公式。它以图像和 PDF 为输入，按顺序提取交错排列的文本与图像内容。

因此，Mistral OCR 是与接收多模态文档（如幻灯片或复杂 PDF）的 RAG 系统配合使用的理想模型。

我们已把 Mistral OCR 设为 Le Chat 上服务数百万用户的默认文档理解模型，并以 *mistral-ocr-latest* 发布 API，定价 $1000 页（使用批量推理每美元可处理页数约翻倍）。API 今天即可在我们的开发者套件 [la Plateforme](http://console.mistral.ai) 上使用，并即将登陆我们的云与推理合作伙伴平台以及本地部署环境。

## 亮点

- 复杂文档理解的最先进水平
- 原生多语言与多模态
- 顶尖基准成绩
- 同类最快
- Doc-as-prompt，结构化输出
- 面向处理高度敏感或机密信息的组织，选择性地开放自托管

逐一看每一个细节。

### 复杂文档理解的最先进水平

Mistral OCR 擅长理解复杂的文档元素，包括交错图像、数学表达式、表格，以及 LaTeX 排版等高级版面。该模型能深入理解内容丰富的文档，如带有图表、图形、公式和插图的科学论文。

下面是一个示例：模型从给定 PDF 中提取文本和图像并写入 markdown 文件。你可以在[这里](https://colab.research.google.com/github/mistralai/cookbook/blob/main/mistral/ocr/structured_ocr.ipynb)访问 notebook。

下面是 PDF 与其各自 OCR 输出的并排对比。拖动滑块可在输入与输出之间切换。

表格 + 插图

![3 Exemple](https://mistral.ai/_astro/3aa243eb-f883-4676-b23a-f69f5227375c_Z1NTEaR.webp?dpl=6abbd11780b53c00082eea6f)

OCR 结果

![3 Ocr](https://mistral.ai/_astro/5ec9ef56-c72a-4f6c-bcbc-f2e344909059_2ep0b0.webp?dpl=6abbd11780b53c00082eea6f)

数学公式

![4 Exemple](https://mistral.ai/_astro/67e873eb-662a-40fd-921e-ed8ea37c20b6_Z7Eglj.webp?dpl=6abbd11780b53c00082eea6f)

OCR 结果

![4 Ocr](https://mistral.ai/_astro/e594e7b2-41c2-4a7b-90ca-e1886c477eba_ZbeaJL.webp?dpl=6abbd11780b53c00082eea6f)

印地语

![5 Exemple](https://mistral.ai/_astro/4c0ea3e0-0128-45ab-a262-cf489b8d1b1c_1kkT4o.webp?dpl=6abbd11780b53c00082eea6f)

OCR 结果

![Hindi Ocr](https://mistral.ai/_astro/2c871d1b-85e0-45a1-b9b3-053db0320ffa_ukhrk.webp?dpl=6abbd11780b53c00082eea6f)

公文

![6 Exemple](https://mistral.ai/_astro/6a2e2886-1e4e-4bfe-8673-debfff5b0d2b_2okJKV.webp?dpl=6abbd11780b53c00082eea6f)

OCR 结果

![6 Ocr](https://mistral.ai/_astro/82aba7f9-6a2f-495f-b4b7-d32e9ee4dd75_Z17FLRk.webp?dpl=6abbd11780b53c00082eea6f)

阿拉伯语

![7 Exemple](https://mistral.ai/_astro/e12333d3-1a58-4650-ae0f-d4ffe595cdfc_Fn8MW.webp?dpl=6abbd11780b53c00082eea6f)

OCR 结果

![Arabic OCR](https://mistral.ai/_astro/a51226e5-fcad-4b10-8306-d89df7013a01_Z1hMGqc.webp?dpl=6abbd11780b53c00082eea6f)

### 顶尖基准成绩

在严格的基准测试中，Mistral OCR 持续超越其他领先的 OCR 模型。它在文档分析多个维度上的卓越精度如下图所见。我们从文档中提取嵌入图像以及文本，而下文对比的其他 LLM 不具备该能力。为了公平比较，我们在内部"纯文本"测试集（包含各类发表论文与来自互联网的 PDF）上评估它们，结果如下：

| Model | Overall | Math | Multilingual | Scanned | Tables |
| --- | --- | --- | --- | --- | --- |
| Google Document AI | 83.42 | 80.29 | 86.42 | 92.77 | 78.16 |
| Azure OCR | 89.52 | 85.72 | 87.52 | 94.65 | 89.52 |
| Gemini-1.5-Flash-002 | 90.23 | 89.11 | 86.76 | 94.87 | 90.48 |
| Gemini-1.5-Pro-002 | 89.92 | 88.48 | 86.33 | 96.15 | 89.71 |
| Gemini-2.0-Flash-001 | 88.69 | 84.18 | 85.80 | 95.11 | 91.46 |
| GPT-4o-2024-11-20 | 89.77 | 87.55 | 86.00 | 94.58 | 91.70 |
| Mistral OCR 2503 | 94.89 | 94.29 | 89.55 | 98.96 | 96.12 |

### 原生多语言

自创立起，Mistral 就立志以模型服务世界，因此在全部产品中致力构建多语言能力。Mistral OCR 将其推向新高度：能够解析、理解并转写来自所有大洲的数千种文字、字体与语言。这种多面性，对处理来自不同语言背景文档的全球组织，以及服务利基市场的本地商家都至关重要。

| Model | Fuzzy Match in Generation |
| --- | --- |
| Google-Document-AI | 95.88 |
| Gemini-2.0-Flash-001 | 96.53 |
| Azure OCR | 97.31 |
| Mistral OCR 2503 | 99.02 |

按语言的基准：

| Language | Azure OCR | Google Doc AI | Gemini-2.0-Flash-001 | Mistral OCR 2503 |
| --- | --- | --- | --- | --- |
| ru | 97.35 | 95.56 | 96.58 | 99.09 |
| fr | 97.50 | 96.36 | 97.06 | 99.20 |
| hi | 96.45 | 95.65 | 94.99 | 97.55 |
| zh | 91.40 | 90.89 | 91.85 | 97.11 |
| pt | 97.96 | 96.24 | 97.25 | 99.42 |
| de | 98.39 | 97.09 | 97.19 | 99.51 |
| es | 98.54 | 97.52 | 97.75 | 99.54 |
| tr | 95.91 | 93.85 | 94.66 | 97.00 |
| uk | 97.81 | 96.24 | 96.70 | 99.29 |
| it | 98.31 | 97.69 | 97.68 | 99.42 |
| ro | 96.45 | 95.14 | 95.88 | 98.79 |

## 同类最快

Mistral OCR 比同类大多数模型更轻量，运行速度显著快于同行，单节点每分钟可处理多达 2000 页。快速处理文档的能力，确保即便在高吞吐环境中也能持续学习与改进。

### Doc-as-prompt，结构化输出

Mistral OCR 还引入了"以文档作为 prompt"的用法，支持更强大、更精确的指令。这一能力让用户可以从文档中提取特定信息，并以结构化输出（如 JSON）格式化。用户可以把提取出的输出链接到下游函数调用，构建 Agent。参见这个示例 [notebook](https://colab.research.google.com/github/mistralai/cookbook/blob/main/mistral/ocr/structured_ocr.ipynb)。

### 以选择性方式开放自托管

对有严格数据隐私要求的组织，Mistral OCR 提供自托管选项。这确保敏感或机密信息停留在你自己的基础设施内、满足监管与安全标准的合规要求。如果你想与我们探讨自托管部署，请[告诉我们](https://mistral.ai/contact)。

## 用例

我们正在赋能 beta 客户，把他们庞大的文档库转化为行动与方案，从而提升组织知识水平。技术正在产生重大影响的一些关键用例包括：

**科研数字化**：领先研究机构一直在试验用 Mistral OCR 把科学论文与期刊转换为 AI 就绪格式，供下游智能引擎使用。这让协作明显更快，加速了科学工作流。

**保存历史与文化遗产**：作为遗产守护者的组织与非营利机构在用 Mistral OCR 把历史文献与文物数字化，确保其留存并让更多人得以接触。

**简化客户服务**：客服部门正在探索用 Mistral OCR 把文档与手册转化为可索引的知识，缩短响应时间、提升客户满意度。

**让设计、教育、法律等领域的文献 AI 就绪**：Mistral OCR 也在帮助企业把技术文献、工程图纸、讲义、演示文稿、监管申报材料等转化为可索引、可直接作答的格式，在数百万文档中释放智能与生产力。

## 今天就体验

Mistral OCR 的能力可在 [le Chat](http://chat.mistral.ai) 上免费试用。要试用 API，请前往 [la Plateforme](http://console.mistral.ai)。我们期待你的反馈；未来几周该模型还会持续变得更好。作为战略合作计划的一部分，我们也将以[选择性方式](https://mistral.ai/contact)提供本地部署。
