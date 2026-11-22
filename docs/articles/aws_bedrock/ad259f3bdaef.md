---
vendor: aws_bedrock
title: How 123RF saved over 90% of their translation costs by switching to Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-123rf-saved-over-90-of-their-translation-costs-by-switching-to-amazon-bedrock
date: 2024-11-25
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 9ddf087acc87
---

# 123RF 如何通过迁移到 Amazon Bedrock 节省超过 90% 的翻译成本

在快速演进的数字内容行业，多语言可访问性对于全球覆盖和用户参与至关重要。[123RF](https://www.123rf.com/) 是一家领先的免版税数字内容提供商，为创意素材（包括由文本生成的 AI 图像）提供在线资源。[2023 年，他们使用 Amazon OpenSearch Service，借助基于向量的语义搜索改进图像发现](https://aws.amazon.com/solutions/case-studies/123rf-gen-ai/)。在这一成功的基础上，他们现在已采用 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 和 Anthropic 的 Claude 3 Haiku，将[内容审核效率提升百倍以上，并大幅加快内容翻译](https://aws.amazon.com/solutions/case-studies/123rf-2024/)，进一步增强其全球覆盖与效率。

尽管该公司凭借基于生成式 AI 的语义搜索工具在英语用户中取得了显著成功，但由于标题和关键词只有英文，它在其他 15 种语言中面临内容发现方面的挑战。持续使用 Google Translate 翻译的成本高得令人却步，而 Anthropic 的 Claude Sonnet 和 OpenAI GPT-4o 等其他模型也不具备成本效益。虽然 OpenAI GPT-3.5 满足成本标准，但在输出质量的一致性上表现不佳。这促使 123RF 去寻找更可靠、更经济的方案来提升多语言内容发现能力。

本文探讨 123RF 如何借助 Amazon Bedrock、Anthropic 的 Claude 3 Haiku 和一个向量存储，高效翻译内容元数据、显著降低成本，并提升其全球内容发现能力。

## 挑战：在大规模翻译中平衡质量与成本

在落地基于生成式 AI 的语义搜索和文生图之后，他们看到英语用户中出现了显著增长。然而，这一成功也暴露了其全球战略中的一个关键缺口：他们庞大的数字资产库——包含数百万张图像、音频文件和动态图形——同样需要为非英语用户做类似的改造。

问题的症结在于其内容本身的性质。用户生成的标题、关键词和描述——这是数字资产世界可搜索性的命脉——大多为英文。为了真正服务全球用户并释放内容库的全部潜力，123RF 需要把这些元数据翻译成 15 种不同语言。但他们很快发现，通往多语言内容的道路上布满财务与技术上的挑战。

### 翻译难题：不止于逐字对应

习语并不总能很好地翻译

随着 123RF 深入探究这一挑战，他们发现其中的复杂性远超简单的逐字翻译。上图展示了一个特别困难的例子：习语。像“The early bird gets the worm”这样的短语如果被直译，就无法像西班牙语中另一句类似习语“A quien madruga, Dios le ayuda”那样传达出其含义。另一个重大障碍是命名实体识别（NER）——对于一项处理多样化视觉和音频内容的服务来说，这是至关重要的环节。

NER 涉及跨语言正确识别和处理专有名词、品牌名、特定术语以及具有文化意义的指涉。例如，一张埃菲尔铁塔的素材照片在所有语言中都应保留其名称，而不是被直译。同样，像 Coca-Cola 或 Nike 这样的品牌名，无论目标语言是什么，都应保持不变。

这一挑战在创意内容领域尤为突出。设想一张假设的素材图片，标题为“一位年轻女性在 Starbucks 使用 MacBook”。理想的翻译系统需要做到以下几点：

- 识别出 *MacBook* 和 *Starbucks* 是品牌名，不应被翻译
- 正确翻译 *Young woman*，同时保留原意与隐含意味
- 恰当处理介词 *in*，它可能会因目标语言的语法规则而变化
- 此外，系统还需要处理行业特定术语、艺术类用语以及可能在其他语言中没有直接对应概念的文化特定概念。例如，对于并不常用这一摄影术语的语言，该如何翻译 *bokeh effect*？

这些细微之处凸显了简单机器翻译工具的不足，也强调了需要一种更精细、具备上下文感知能力的方案。

### 转向语言模型：大模型与小模型的对比

在寻找解决方案的过程中，123RF 探索了一系列选项，每个选项都有各自的取舍：

- **Google Translate** —— 这一既有方案可靠且易用。然而，它的价格高得惊人。公司必须清掉 4500 万条翻译的积压。此外，客户不断生成的新内容还带来持续性的月度财务负担。尽管有效，但这一选项威胁到 123RF 的盈利能力，从长远看不可持续。
- **大语言模型** —— 接下来，123RF 转向 OpenAI GPT-4 和 Anthropic 的 Claude Sonnet 等前沿大语言模型（LLM）。这些模型在理解上下文和产出高质量翻译方面展现出令人印象深刻的能力。然而，以 123RF 的规模运行这些复杂模型的成本被证明难以承受。尽管它们在质量上出类拔萃，但对于一家要处理数百万条短文本片段的业务而言，它们在成本效益上并不达标。
- **更小的模型** —— 为了找到折中方案，123RF 试验了 OpenAI GPT-3.5 等能力较弱的模型。这些模型的价格更容易接受，也更贴合 123RF 的预算约束。然而，这种成本节省是有代价的：输出质量不稳定。这些译文虽然有时可以接受，但缺乏专业级内容描述所需的可靠性与细致度。
- **微调** —— 123RF 曾短暂考虑过微调一个更小的语言模型以进一步降低成本。但他们明白这会有若干障碍：每当模型更新时，他们都必须定期重新微调，需要雇用领域专家来训练模型并管理其维护与部署，还可能要为每一种输出语言分别管理一个模型。

这一番探索揭示了 AI 翻译领域的一个根本性挑战：成本与质量之间看似不可避免的权衡。顶级模型提供的高质量翻译在财务上不可行，而更便宜的选项又无法达到 123RF 业务所要求的准确性与一致性标准。

## 解决方案：Amazon Bedrock、Anthropic 的 Claude 3 Haiku、prompt 工程与一个向量存储

[Amazon Bedrock](https://aws.amazon.com/bedrock/) 是一项完全托管的服务，通过单一 API 提供来自 AI21 Labs、Anthropic、Cohere、Meta、Mistral AI、Stability AI 和 Amazon 等领先 AI 公司的高性能基础模型（FM）供选择，并提供构建生成式 AI 应用所需的一整套能力，兼顾安全性、隐私和负责任 AI。

在这段变革之旅中，Amazon Bedrock 被证明是 123RF 成功的基石。多个因素使它成为首选供应商：

- **模型多样性** —— Amazon Bedrock 提供多种最先进的语言模型，使 123RF 能够选择最贴合其特定需求的模型，例如 Anthropic 的 Claude 3 Haiku。
- **可扩展性** —— Amazon Bedrock 高效处理海量工作负载的能力，对于处理数百万条翻译至关重要。
- **成本效益** —— Amazon Bedrock 的定价模式结合其高效的资源利用，在实现大幅成本下降中发挥了关键作用。
- **集成能力** —— Amazon Bedrock 与其他 AWS 服务集成起来很方便，这推动了诸如用于动态 prompt 的向量数据库等高级功能的实现。
- **安全与合规** —— 123RF 处理的是用户生成内容，Amazon Bedrock 强大的安全功能让处理潜在敏感信息时更安心。
- **定制方案的灵活性** —— Amazon Bedrock 对自定义实现（例如动态 prompt 技术）的开放性，使 123RF 能够把方案精确定制到自身需求

## 破译密码：prompt 工程技术

123RF 翻译之旅的第一个突破来自与 AWS 团队的协作，借助了 Amazon Bedrock 和 Anthropic 的 Claude 3 Haiku 的能力。他们成功的关键在于对 prompt 工程技术的创新性应用——这是一套旨在从 LLM 中激发出最佳表现的策略，对于成本高效的模型尤为重要。

在使用 LLM 时，prompt 工程至关重要，因为这些模型虽然强大，却可能产生非确定性的输出——也就是说，即使输入相同，它们的响应也可能不同。通过精心设计 prompt，我们可以提供有助于缓解这种可变性的上下文与结构。此外，设计良好的 prompt 能把模型引导到当前的具体任务上，确保 LLM 聚焦于最相关的信息，并产出符合预期结果的输出。对 123RF 而言，这意味着引导模型产出准确、具备上下文感知的译文，并保留原内容的细微之处。

下面深入介绍他们采用的具体技术。

### 为模型分配角色

团队首先为 AI 模型分配了一个特定角色——AI 语言翻译助手。这个看似简单的步骤对于为模型的任务设定语境至关重要。通过界定其角色，模型被预先引导，以专业译者的思维方式来处理任务，去考虑通用语言模型可能忽略的细微之处与复杂性。

例如：

```
You are an AI language translation assistant. 
Your task is to accurately translate a passage of text from English into another specified language.
```

### 数据与 prompt 模板分离

他们在待翻译文本与翻译指令之间做了清晰划分。这种分离有两个目的：

- 让模型输入更清晰，降低混淆或误解的可能性
- 让翻译流程更易于自动化与扩展，因为同一套 prompt 模板可以搭配不同的输入文本使用

例如：

```
Here is the text to translate:
<text> {{TEXT}} </text>
Please translate the above text into this language: {{TARGET_LANGUAGE}}
```

### 思维链

该方案最具创新性的方面之一是引入了草稿区（scratchpad）。这让模型能够把思考过程外化，模仿人类译者在处理一段困难文字时可能的思路。

草稿区提示模型考虑以下内容：

- 段落整体的含义与意图
- 可能无法直译的习语和表达
- 写作的语气、正式程度和风格
- 不应翻译的专有名词，如人名和地名
- 英文与目标语言之间的语法差异
- 这一逐步思考的过程显著提升了翻译的质量与准确性，对于复杂或含细微差别的内容尤其如此。

### K-shot 示例

团队把多个高质量翻译示例直接嵌入 prompt 中。这种被称为 K-shot 学习的技术，向模型提供了若干（K 个）符合期望输出质量与风格的具体示例。

通过精心挑选能体现不同翻译难点（如习语表达、技术术语和文化指涉）的多样化示例，团队有效地训练模型处理多种内容类型。

例如：

```
Examples:
<text>The early bird catches the worm.</text>
<translated_text>El que madruga, Dios le ayuda.</translated_text>
```

### 神奇配方：把一切组合起来

这些技术最终汇聚成一个 prompt 模板，囊括了实现高质量、上下文感知翻译所需的各个要素。下面是结合前述步骤的一个示例 prompt。此处并未展示实际使用的 prompt。

```
You are an AI language translation assistant. Your task is to accurately translate a passage of text from English into another specified language. Here is the text to translate:
<text> {{TEXT}} </text>
Please translate the above text into this language: {{TARGET_LANGUAGE}}
Think carefully, in the <scratchpad> section below, think through how you will translate the text while preserving its full meaning and nuance. Consider:
- The overall meaning and intent of the passage
- Idioms and expressions that may not translate literally
- Tone, formality, and style of the writing
- Proper nouns like names and places that should not be translated
- Grammatical differences between English and {{TARGET_LANGUAGE}}
Examples:
<text>The software update is scheduled for next Tuesday.</text>
<translated_text>La actualización del software está programada para el próximo martes.</translated_text>
<text>Breaking news: Elon Musk acquires Twitter for $44 billion.</text>
<translated_text>Última hora: Elon Musk adquiere Twitter por 44 mil millones de dólares.</translated_text>
... [8 more diverse examples] ...
Now provide your final translated version of the text inside <translated_text> tags. Ensure the translation is as accurate and natural-sounding as possible in {{TARGET_LANGUAGE}}. Do not translate any names, places or other proper nouns.
<translated_text>
```

该模板提供了一个框架，可在一系列内容类型和目标语言上实现一致的高质量翻译。

## 进一步优化：用动态 prompt 为模型提供依据

尽管初始实现已取得令人印象深刻的结果，AWS 团队仍建议通过动态 prompt 技术做进一步改进。这一进阶方法旨在让模型更具适应性和上下文感知能力。他们采用了检索增强生成（RAG）技术，用与每个短语相关的 K-shot 示例（而非针对每种语言的通用示例）来构建动态 prompt 模板。这也让 123RF 能够利用其现有的高质量翻译目录，进一步对齐模型。

### 高质量翻译的向量数据库

团队提议为每种目标语言建立一个向量数据库，其中填充以往的高质量翻译。这个数据库将作为丰富的翻译示例库，捕捉细微差别和领域特定术语。

实现包含以下组成部分：

- **Embedding 生成：**  使用 Amazon Bedrock 上的 Amazon Titan 或 Cohere 等 embedding 模型，把源文本及其译文都转换成高维向量。
- **分块策略：**  为保持上下文并确保译文有意义，团队实施了细致的分块策略：  每段源文本（英文）与其在目标语言中的对应译文配对。这些配对按完整句子或逻辑短语存储，而不是按单个词或任意字符长度切分。对于段落或描述等较长内容，文本会被拆成语义上有意义的块，确保每块包含一个完整的想法或概念。每个块对（源文本与译文）都被赋予唯一标识符，以维持关联。
- **向量存储：**  源文本及其译文的向量表示被一起存入数据库。存储结构包括：  原始源文本块。对应的译文块。源文本的向量 embedding。译文的向量 embedding。内容类型、领域以及相关标签等元数据。
- **数据库组织：**  数据库按目标语言组织，为每个语言对（例如英语-西班牙语和英语-法语）设立独立的索引或集合。在每个语言对内部，向量对都被建立索引，以支持高效的相似度搜索。
- **相似度搜索：**  对于每个新的翻译任务，系统会执行混合搜索，从向量数据库中找出语义上最相近的句子：  待翻译的新文本用相同的 embedding 模型转换为向量。在向量空间中执行相似度搜索，找出源语言中最接近的匹配。随后取回这些匹配对应的译文，为翻译任务提供相关示例。

这种存取文本-译文对的结构化方法实现了高效、具备上下文感知的查找，显著提升了 LLM 产出译文的质量与相关性。

### 把一切组合起来

来自向量数据库的最佳匹配示例会被动态插入 prompt，为模型提供与当前具体翻译任务高度相关的上下文。

这带来了以下好处：

- 改善对领域特定术语和表达方式的处理
- 更好地保持与内容类型相称的风格和语气
- 增强正确解析命名实体和技术术语的能力

下面是一个动态生成 prompt 的示例：

```
[Standard prompt preamble]
...
Examples:
<text>{{Dynamically inserted similar source text 1}}</text>
<translated_text>{{Corresponding high-quality translation 1}}</translated_text>
<text>{{Dynamically inserted similar source text 2}}</text>
<translated_text>{{Corresponding high-quality translation 2}}</translated_text>
...
[Rest of the standard prompt]
```

这种动态方法让模型能够持续改进与适应，利用不断增长的高质量翻译数据库为后续任务提供依据。
下图说明了该流程的工作流。

如何借助向量存储为翻译提供依据

该流程包括以下步骤：

- 使用相同的 embedding 模型把待翻译的新文本转换为向量。
- 将文本和 embedding 与高质量既有译文数据库进行比对。
- 把相似译文与针对目标语言的通用翻译示例 prompt 模板合并。
- 把带有初始待翻译文本的新增广 prompt 发送到 Amazon Bedrock。
- 把翻译输出存入现有数据库，或保存下来供人工复核（human-in-the-loop）评估。

## 成果：翻译成本降低 95% 乃至更多

在 Amazon Bedrock 上结合 Anthropic 的 Claude 3 Haiku 实施这些进阶技术，再加上与 AWS 账户团队的合作工程投入，对 123RF 而言堪称创新。通过与 AWS 合作，123RF 实现了高达 95% 的翻译成本降幅。但收益远不止节省成本：

- **可扩展性** —— 采用 Anthropic 的 Claude 3 Haiku 的新方案使 123RF 得以快速扩展其多语言供给。他们迅速上线了 9 种语言的翻译，并计划在不久的将来覆盖全部 15 种目标语言。
- **质量提升** —— 尽管成本大幅降低，翻译质量却明显改善。LLM 的上下文感知特性配合细致的 prompt 工程，带来了更自然、更准确的译文。
- **边界情况的处理** —— 该系统在处理习语表达和技术行话等复杂情况时表现出众，而这些正是以往方案的痛点。
- **更快的上市速度** —— 新系统的效率大幅缩短了新内容以多种语言上线所需的时间，使 123RF 在快速更新其全球供给方面获得竞争优势。
- **资源重新分配** —— 节省下来的成本使 123RF 能把资源重新分配到业务的其他关键领域，促进创新与增长。

## 展望未来：持续改进与扩展

该项目的成功为 123RF 打开了新的视野，也为进一步的进阶铺平了道路：

- **扩展语言覆盖** —— 随着成本门槛大幅降低，123RF 现在计划把语言供给扩展到最初的 15 种目标语言之外，可能借此进入新的市场和用户群。
- **Anthropic 的 Claude 3.5 Haiku** —— [Anthropic 的 Claude 3.5 Haiku 的近期发布](https://www.aboutamazon.com/news/aws/amazon-bedrock-anthropic-ai-claude-3-5-sonnet) 令 123RF 倍感兴奋。这一即将推出的模型有望带来更高的智能与效率，可能使翻译质量和成本效益得到进一步提升。
- **更广泛的 AI 集成** —— 受翻译成功的鼓舞，123RF 正在探索生成式 AI 在其运营中的更多用例。潜在领域包括：  增强图像标签与分类。对用户生成图像的内容审核。面向用户的个性化内容推荐。
- **持续学习闭环** —— 团队正在构建一套反馈机制，让成功的译文自动加入向量数据库，形成持续改进的良性循环。
- **跨语言搜索增强** —— 借助改进后的译文，123RF 正在开发更精细的跨语言搜索能力，使用户无论用哪种语言搜索都能找到相关内容。
- **Prompt 目录** —— 他们可以探索新推出的 [Amazon Bedrock Prompt Management](https://aws.amazon.com/bedrock/prompt-management/)，用它来管理 prompt 模板并高效迭代。

## 结论

123RF 借助 Amazon Bedrock 和 Anthropic 的 Claude 取得的成功，不只是一个降低成本的故事——它还是一份蓝本，展示了企业如何利用前沿 AI 打破语言障碍、真正实现数字内容的全球化。这个案例研究展示了创新思维、先进 prompt 工程与恰当技术伙伴关系的变革力量。

123RF 的历程带来了以下关键启示：

- prompt 工程在从 LLM 中挖掘最佳表现方面的作用
- 上下文与领域特定知识在 AI 翻译中的重要性
- 动态、自适应的 AI 方案在解决复杂业务挑战方面的潜力
- 选择合适的技术伙伴与平台的关键作用

展望未来，云计算、生成式 AI 与创新的 prompt 工程三者的结合显然会继续重塑多语言内容管理的格局。语言的壁垒正在瓦解，为全球沟通与内容发现开辟新的可能。

对于在全球内容发现方面面临类似挑战的企业，123RF 的历程提供了宝贵的洞见和一条通往成功的路线图。它表明，只要拥有合适的技术伙伴和创新的意愿，即使最令人生畏的语言挑战也能转化为增长与全球扩张的机遇。如果你有类似的用例并希望获得实施该技术的帮助，请联系你的 AWS 账户团队，或通过我们在 [GitHub](https://github.com/aws-samples/prompt-engineering-with-anthropic-claude-v-3) 上提供的 prompt 工程工作坊来打磨你的 prompt 工程技能。

### 关于作者

![Fahim Surani picture](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/20/fahimsur-1.jpg)**Fahim Surani** 是 Amazon Web Services 的解决方案架构师，帮助客户在云上创新。他专注于机器学习和生成式 AI，与全球的数字原生企业和金融服务机构合作，在 AWS 上构建可扩展、安全且高性价比的产品与服务。加入 AWS 之前，他曾担任架构师、AI 工程师、移动游戏开发者和软件工程师。空闲时他喜欢跑步和读科幻小说。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/20/ML-15758-mark-roy.png)**Mark Roy** 是 AWS 的首席机器学习架构师，帮助客户设计和构建生成式 AI 方案。自 2023 年初以来，他专注于领导 AWS 旗舰生成式 AI 产品 Amazon Bedrock 发布期间的解决方案架构工作。他的工作覆盖广泛用例，主要兴趣在于生成式 AI、agent 以及在企业范围内扩展 ML。他曾帮助保险、金融服务、媒体与娱乐、医疗、公用事业和制造业的公司。加入 AWS 之前，Mark 有 25 年以上的架构师、开发者和技术负责人经历，其中 19 年在金融服务领域。Mark 持有六项 AWS 认证，包括 ML Specialty 认证。
