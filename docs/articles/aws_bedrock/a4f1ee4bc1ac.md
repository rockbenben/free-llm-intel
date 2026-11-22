---
vendor: aws_bedrock
title: How DiDi built intelligent contact center QA with Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-didi-built-intelligent-contact-center-qa-with-amazon-bedrock
date: 2026-09-08
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 0764f332c687
---

# 滴滴如何用 Amazon Bedrock 构建智能联络中心 QA

滴滴（DiDi）与 AWS 合作，为其国际业务集团的客户体验（CX）部门在 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 上构建了一套智能联络中心质量保证（QA）系统。该系统覆盖西班牙语和葡萄牙语，横跨三条业务线（网约车、外卖和金融服务），并把 QA 能力从一套不透明的第三方方案迁移到透明、自有的 AI 架构上。它由三条核心 pipeline 组成：意图验证、合规评估和客户之声（VOC）分析。在滴滴的生产验证中，意图验证准确率从 38% 提升到 86%，合规评分准确率超过 90%，VOC 分析则把原本需要数小时的人工汇总压缩到几分钟。

本文介绍滴滴国际业务集团与 AWS 如何在 Amazon Bedrock 上构建一套自有、透明的联络中心 QA 系统，取代原先不透明的第三方方案。我们会描述支撑该系统的三条核心 pipeline：意图验证、合规评估和客户之声（VOC）分析，并解释每条 pipeline 背后的设计思路。在过程中，我们会展示一条单一原则——精确的上下文管理（即精确控制每次调用中模型能看到哪些信息）——如何驱动了关键成果，以及 VOC 趋势分析如何把数小时的人工工作压缩到几分钟。

## 滴滴国际业务集团简介

滴滴国际业务集团（IBG）是滴滴全球的海外业务部门，业务覆盖 14 个国家和地区，拥有三条业务线：网约车、外卖和金融服务，服务数千万用户。CX 部门每月要在在线聊天和电话渠道上处理大量西班牙语和葡萄牙语工单，而服务质量直接影响用户留存与品牌信任。

## 挑战

随着业务扩张、QA 标准快速演进，现有的第三方 QA 方案缺乏透明度和灵活性。滴滴 IBG CX 团队面临四个核心挑战：

- **QA 判断缺乏可追溯性。** QA 判断会影响合规审计结果和服务改进的优先级。然而现有系统是一个不透明的封闭系统，看不到推理过程；而人工抽查又受制于处理量和成本。两种方式都无法为过去的决策留下审计轨迹。
- **服务场景的组合复杂度。** 客服运营横跨多种语言与多条业务线，每种组合都受各自的合规标准和 QA 规则约束。随着组合数量成倍增长，规则维护成本不断攀升，一致性也越来越难以保证。
- **对 QA 标准变化响应缓慢。** 随着业务演进，QA 标准频繁变动。每次变更都需要重新培训 QA 分析师或更新执行规范，于是出现新旧标准并存的过渡期，产生不一致的结果。
- **缺乏主动的趋势发现能力。** 当某一类问题在短时间窗口内激增时，运营团队只能逐条阅读工单并人工统计才能发现。早期识别趋势并及时干预几乎不可能。

为应对这些挑战，滴滴 IBG CX 团队与 AWS 合作，在 Amazon Bedrock 上构建了一套自有的智能 QA 系统。团队选择 Amazon Bedrock 有三个原因。第一，它通过单一 API 提供与模型无关的广泛基础模型访问，团队可以为每条 pipeline 选择最合适的模型，而无需重新设计架构。第二，它内置的治理与安全控制能把敏感的客服数据留在滴滴的网络边界之内，并提供此前第三方方案所缺乏的透明度与可管控性。这些控制包括通过由 AWS PrivateLink 驱动的 Amazon Virtual Private Cloud（Amazon VPC）端点建立私有连接、传输中与静态加密，以及通过 AWS Identity and Access Management（IAM）实现的细粒度访问控制。第三，Amazon Bedrock Guardrails 提供可配置的防护措施，例如内容过滤和敏感信息脱敏，为团队按照负责任的 AI 实践构建 QA 系统奠定了基础。

## 解决方案概览

该系统在 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 上实现了三条专用 pipeline，每条针对不同的 QA 维度，并在每个判断之外同时产出一套完整的推理链。意图 pipeline 验证客服代表所标注的接触原因是否正确；评估 pipeline 审计服务合规性并提取业务洞察；VOC pipeline 聚合大量相似工单，以显现系统性问题趋势。

下图展示了端到端的系统架构：从双渠道数据接入，经预处理进入由 Amazon Bedrock 驱动的三条 pipeline。

![双渠道接触数据经预处理流入 Amazon Bedrock 上的意图、评估和 VOC pipeline](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/31/ML-21371-1.png)

图 1：系统架构。双渠道数据经预处理流入由 Amazon Bedrock 驱动的三条并行 pipeline，产出带有完整推理的结构化输出

预处理层接入在线聊天和电话数据，将其归一化为统一的 schema，再分发到三条并行 pipeline。整体流程如下：

- **数据接入与预处理。** 在线聊天和电话转写文本（通过语音转文字）经过各渠道专属的预处理，产出供下游消费的统一对话格式。
- **意图 pipeline。** 验证客服代表标注的接触原因（CR、Sub-CR）是否准确，并在不正确时推荐替代分类。它还会独立分析标记为「Other」的工单（即无法归入现有分类体系的工单），以识别分类体系的覆盖缺口。
- **评估 pipeline。** 在单次大语言模型（LLM）调用中，同时对每张工单执行多项合规评分和业务洞察（BI）分析。
- **VOC pipeline。** 由运营团队按需触发，对特定时间窗口内的一批相似工单执行聚合分析，产出结构化的分析报告。
- **输出。** 交付各 pipeline 的结构化结果，供运营团队查询和可视化。

由于该系统要在大规模上对真实客户对话进行评分和分类，负责任 AI 控制被内置其中。我们使用 Amazon Bedrock Guardrails 在敏感信息（例如个人身份信息 PII）到达模型之前进行遮蔽，并应用上下文接地（grounding）检查，对缺乏依据的回答打上标记，从而减少幻觉式判断。除 Guardrails 之外，系统并不把模型输出当作最终结果：对于规则可判定的标准，一个程序化的后校验层会拿模型的判断与原始对话重新核对。例如，报告的拼写错误只在客服代表自己的消息中核对，通过与否的阈值也按核对后的数量来判定，而不是用模型自己的计数。可计算的事实（例如客服响应等待时长）在代码中确定性地推导出来再注入 prompt，而不是留给模型去推断。这些控制措施，再加上每个评分都附带完整推理链供人工审阅，使系统的合规决策在生产环境中保持可审计、可靠。

## 意图 pipeline：用信息隔离实现准确分类

在工单处理过程中，客服代表会标注接触原因标签。滴滴的接触原因分类体系（CR Tree）从宽泛的类别出发，在多个层级上逐级细分出越来越精细的子类。层级越深，区分越细微，因此在规模化场景下误标不可避免。系统必须自动验证这些标签是否准确，并在错误时推荐替代项。它还会反向审计 CR Tree：识别覆盖缺口、建议新标签，并把 QA 与分类体系维护之间的闭环打通。

最直接的做法是把完整的 CR Tree 连同对话一起，在单次调用中喂给 LLM。这种做法的准确率远低于预期。我们找到了根本原因：当 LLM 看到完整的选项列表时，它会自动逐项比较。即便原始标签完全合理，只要找到一个*稍微更精确*的替代项，就会触发「当前标签是错的」这一判断。多轮 prompt 调优都无法改变这一行为。问题出在上下文管理，而不是 prompt 措辞。

团队从两个方面重新设计了这条 pipeline：

- **任务隔离。** 接触原因验证和「Other」标签分析在本质上是两类不同的任务，因此被拆分为独立路径。标记为「Other」的工单会走一条专门的三级分析：系统先检查同级类别中是否存在更合适的标签；如果没有找到，再检索完整的 CR Tree；如果仍然不匹配，就说明存在覆盖缺口，系统会建议新增标签。
- **信息隔离。** 对于标准接触原因，流程进一步拆分为验证阶段和分类阶段。在验证阶段，LLM 只收到当前接触原因标签，并仅依据对话内容判断当前标签是否合理。只有当验证判定为失败时，系统才进入分类阶段。此时 LLM 会收到完整的 CR Tree 以及验证阶段的推理，并推荐一个替代分类，同时给出置信度评分和理由。

通过这一两级设计，在滴滴的生产验证中，意图验证准确率从 38% 提升到 86%。

## 评估 pipeline：面向多语言、多业务线覆盖的动态组装

评估 pipeline 对每张工单一次性完成多个合规项的评分并提取业务洞察。考虑到语言与业务线的组合复杂度以及频繁变化的 QA 标准，为每种组合单独维护一份 prompt 是不可持续的。

解决方案是一套统一 prompt 模板加动态变量注入。语言上下文、业务线上下文，以及每条标准的定义与判定规则都以外部配置的形式存在。调用时，系统根据工单元数据把它们组装成一份完整的 prompt。新增一个评估项、一种语言或一条业务线，只需要更新配置。一份模板就在单次 LLM 调用中覆盖所有组合。

下图展示了评估 pipeline 如何把外部配置组装成统一 prompt，并产出结构化输出。

![评估 pipeline 在 Amazon Bedrock 上把外部配置组装成统一 prompt，产出结构化的合规评分与业务洞察](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/31/ML-21371-2.png)

图 2：评估 pipeline。外部配置被动态组装为统一 prompt，由 Amazon Bedrock 处理，产出结构化的合规评分与业务洞察

下面的示例经过简化，用来说明两种机制如何协同工作：从外部配置动态组装 prompt，以及 Amazon Bedrock 的 Tool Use 能力强制模型返回通过 schema 校验的 JSON。

```
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

MODEL_ID = "<your-bedrock-model-id>"

def build_output_schema(num_criteria):
    """Derive the JSON schema from the checklist size — adding a new
    compliance item requires only a config change, not a code change."""
    criteria = {
        f"criteria_{i}": {
            "type": "object",
            "properties": {
                "reasoning": {"type": "string"},
                "score": {"type": "integer"},  # 0 = pass, 1 = fail
            },
            "required": ["reasoning", "score"],
        }
        for i in range(1, num_criteria + 1)
    }
    return {
        "type": "object",
        "properties": {"scoring": {"type": "object", "properties": criteria}},
        "required": ["scoring"],
    }

def assemble_prompt(criteria_config, language, business_line):
    """Dynamic assembly: one template covers every language x business-line
    combination. Context lives in external config, injected at call time."""
    criteria_block = "\n".join(
        f"CRITERIA_{i}:\n- {c['parameter']}\n- PASS: {c['pass']}\n- FAIL: {c['fail']}"
        for i, c in enumerate(criteria_config, 1)
    )
    return (
        f"You are a customer service quality auditor for DiDi.\n"
        f"LANGUAGE CONTEXT: the conversation is in {language}.\n"
        f"BUSINESS CONTEXT: this is a {business_line} service interaction.\n\n"
        f"SCORING CRITERIA TO EVALUATE:\n{criteria_block}"
    )

def evaluate(transcript, criteria_config, language, business_line):
    system_prompt = assemble_prompt(criteria_config, language, business_line)
    schema = build_output_schema(len(criteria_config))
    response = bedrock.converse(
        modelId=MODEL_ID,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": transcript}]}],
        # Tool Use with a forced tool choice constrains the model to emit
        # schema-valid JSON — every score carries its own reasoning chain.
        toolConfig={
            "tools": [{
                "toolSpec": {
                    "name": "output_result",
                    "description": "Output the structured evaluation result",
                    "inputSchema": {"json": schema},
                }
            }],
            "toolChoice": {"tool": {"name": "output_result"}},
        },
        inferenceConfig={"maxTokens": 8192, "temperature": 0.0},
    )
    for block in response["output"]["message"]["content"]:
        if "toolUse" in block:
            return block["toolUse"]["input"]
```

Amazon Bedrock 的 Tool Use 能力把输出约束为结构化 JSON，每个评分都同时包含判断本身和它的推理链。对于规则可判定的指标，系统会应用程序化的后校验，用确定性逻辑校准模型的语义判断。

在生产验证中，合规评分达到超过 90% 的平均准确率。该 pipeline 还会输出业务洞察（例如问题解决率和客户满意度）。由于每个判断都附带推理链，QA 变成了一种双向的改进机制：客服代表可以理解评分从何而来，并据此调整自己的服务。

## VOC pipeline：用多阶段处理主动发现趋势

VOC pipeline 按需触发，用于分析特定时间窗口内的大批接触记录，显现那些值得采取系统性措施的高频问题。挑战在于如何高效地从数以千计的对话中提取结构化洞察。把它们一次性全部喂给 LLM，会产出过于粗糙的类别，并把关键细节淹没掉。

VOC pipeline 采用三阶段方法：**并行提取** → **问题聚类** → **报告生成**，每个阶段都精确控制 LLM 可见的信息范围。

- **并行提取。** 每个对话独立调用 LLM 提取结构化字段：问题类型、用户情绪、解决结果、根本原因等。这一阶段的工单天然可以并行处理。
- **问题聚类。** 用 embedding 模型计算提取出的问题类型标签之间的语义相似度，把同义表述合并（例如「未付取消费」和「取消费未支付」），然后按工单频次排序，显现影响最大的问题。由于这一阶段使用 embedding 距离和统计排序，而不是 LLM 生成，结果具有确定性和可复现性。
- **报告生成。** LLM 基于高频簇生成分析报告，涵盖摘要、痛点分析和可执行的改进建议。

**示例：** 当取消费投诉在短时间内于拉美多个市场激增时，运营团队触发了一次 VOC 分析。几分钟内，系统就从多语言对话中识别出主要根本原因和高频触发场景，并产出一份带有可执行建议的结构化报告。这项工作此前需要数小时的人工阅读与汇总。

## 结论

回顾这次合作，滴滴团队既总结了可量化的成果，也总结了项目带来的更深层经验：

> 「在国际业务中，多语言、多业务的客服 QA 是一个规模化难题——原有方案不仅不透明，而且随着业务标准变化也很难快速迭代。用 Amazon Bedrock 重建这套系统之后，我们实现了 QA 判断的完全透明：意图验证准确率从 38% 提升到 86%，合规评分准确率超过 90%，对大量工单的趋势分析从数小时压缩到几分钟。这个项目教给我们一件根本性的事：构建可靠的 LLM 应用，关键不在于工具本身，而在于团队对上下文管理和数据定义的深入掌握。这种能力无法外包——而它正是本次合作最有价值的成果。」

——Raphael Hua，滴滴国际业务集团数据分析团队

滴滴基于 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 构建的智能 QA 系统，通过三条 pipeline 完成了从第三方不透明系统到透明、可控的质量保证的转变：

- **意图验证准确率从 38% 提升到 86%。** 两级隔离设计缓解了 LLM 过度纠偏的倾向，提升了意图判断的可靠性。
- **合规评分准确率超过 90%。** 动态 prompt 组装用一份模板覆盖了所有「语言 × 业务线」组合。系统为每个判断输出完整推理链，使 QA 决策可追溯、可执行。
- **VOC pipeline 把数小时的人工工作压缩到几分钟。** 三阶段 pipeline 自动从大量多语言对话中提取结构化洞察，让运营团队能够快速识别系统性趋势。

核心结论是：LLM 应用的性能瓶颈往往不在 prompt 措辞，而在上下文管理。精确控制模型在每次调用中能看到哪些信息，比如何表述指令更为重要。这一原则贯穿三条 pipeline：意图验证中的信息隔离、评估中的动态组装，以及 VOC 分析中的多阶段处理。

滴滴计划把该系统扩展到更多业务线和语言，探索跨 pipeline 的数据整合，并在现有基础上构建更深入的分析能力。

要了解更多本文所用服务的信息，请参阅 [Amazon Bedrock 用户指南](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)。关于在 AWS 上构建 LLM 应用和联络中心 AI 的相关指引，请参阅 [AI | AWS Contact Center](https://aws.amazon.com/blogs/contact-center/tag/ai/)。如果你有兴趣构建类似的智能 QA 系统，可以了解 [Amazon Bedrock](https://aws.amazon.com/bedrock/)，或联系 [AWS Generative AI Innovation Center](https://aws.amazon.com/ai/generative-ai/innovation-center/)。

## 关于作者
