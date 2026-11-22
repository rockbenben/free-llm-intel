---
vendor: aws_bedrock
title: How BQA streamlines education quality reporting using Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-bqa-streamlines-education-quality-reporting-using-amazon-bedrock
date: 2025-01-13
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 57fa7e62a308
---

# BQA 如何借助 Amazon Bedrock 简化教育质量报告流程

鉴于当今数据的价值，各行各业的组织都在处理跨多种格式的海量数据。人工审查和处理这些信息是一项有挑战且耗时的任务，还可能存在出错的空间。正是在这里，智能文档处理（IDP）结合[生成式 AI](https://aws.amazon.com/generative-ai/) 的力量，成为一种颠覆性的解决方案。

生成式 AI 的集成进一步增强了 IDP 的能力，它利用大语言模型（LLM）和生成技术来理解并生成类人文本。这种集成使组织不仅能够从文档中提取数据，还能对提取出的信息进行解读、总结并生成洞见，从而实现更智能、更自动化的文档处理工作流。

[教育与培训质量管理局（BQA）](https://www.bqa.gov.bh/en/pages/home.aspx) 在提升巴林王国教育与培训服务质量方面发挥着关键作用。BQA 审查所有教育与培训机构的绩效，包括学校、大学和职业院校，从而促进该国人力资本的专业发展。

BQA 负责监督一套全面的质量保证流程，其中包括制定绩效标准，并对教育与培训机构开展客观审查。该流程涉及收集和分析大量文档，包括自我评估报告（SER）、支撑材料，以及受审机构提供的各种媒体格式文件。

BQA 与 AWS 的合作通过 [Cloud Innovation Center](https://aws.amazon.com/government-education/cloud-innovation-centers/)（CIC）计划促成，该计划由 AWS、[Tamkeen](https://www.tamkeen.bh/en/) 以及巴林的多所领先大学（包括 [Bahrain Polytechnic](https://cic.polytechnic.bh/) 和 [University of Bahrain](https://cic.uob.edu.bh/)）共同发起。CIC 计划旨在通过提供协作环境，让政府机构能够与 AWS 顾问和大学生紧密合作，利用最新的云技术开发前沿解决方案，从而促进公共部门的创新。

作为 CIC 计划的一部分，BQA 构建了一个概念验证解决方案，充分利用 AWS 服务和生成式 AI 能力。该概念验证的主要目的是测试并验证所提出的技术，展示其在简化 BQA 报告与数据管理流程方面的可行性和潜力。

本文探讨 BQA 如何借助 [Amazon Bedrock](https://aws.amazon.com/bedrock/?gclid=Cj0KCQjwwuG1BhCnARIsAFWBUC03_InmY_quI5NznbN0QZdSz2CSo13J-rH0N48_ALkNHbrvfRG25m4aArV6EALw_wcB&trk=a9c05117-53bb-40a3-89b2-a3ee2d23e7d2&sc_channel=ps&ef_id=Cj0KCQjwwuG1BhCnARIsAFWBUC03_InmY_quI5NznbN0QZdSz2CSo13J-rH0N48_ALkNHbrvfRG25m4aArV6EALw_wcB:G:s&s_kwcid=AL!4422!3!691967569326!e!!g!!amazon%20bedrock!21054971690!157173594137)、[Amazon SageMaker JumpStart](https://aws.amazon.com/sagemaker/jumpstart/) 和其他 AWS 服务的力量，简化整体报告工作流。

## 挑战：简化自我评估报告流程

在审查流程中，BQA 历来会向教育与培训机构提供 SER 模板。机构须提交一份审查材料包，其中包含填写完成的 SER 以及作为证据的支撑材料，而这些材料有时并未完全符合既定的报告标准。

原有流程存在一些挑战：

- **提交不准确或不完整** —— 机构在提交的报告和支撑证据中可能提供不完整或不准确的信息，导致全面审查所需的数据出现缺口。
- **支撑证据缺失或不足** —— 机构作为证据提供的支撑材料常常无法佐证其报告中的说法，这给评估过程带来困难。
- **耗时且资源开销大** —— 该流程需要投入大量时间和资源来人工审查提交材料，并在需要时跟进机构索取补充信息以修正提交内容，导致整体审查流程变慢。

这些挑战凸显了在提交与审查流程中采用更精简、更高效方法的必要性。

## 解决方案概览

所提出的解决方案使用 Amazon Bedrock 和 Amazon Titan Express 模型来实现 IDP 功能。该架构把多个 AWS 服务与 Amazon Bedrock 无缝集成，实现高效的数据提取与比对。

Amazon Bedrock 是一项全托管服务，通过统一的 API 提供来自领先 AI 初创公司和 Amazon 的高性能[基础模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)（FM）。它提供范围广泛的 FM，让你可以选择最适合自己特定用例的模型。

下图展示了解决方案架构。

![解决方案架构图](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/10/ml-17266-arch-diag-2.jpg)

该解决方案包括以下步骤：

- 相关文档被上传并存储在 [Amazon Simple Storage Service](https://aws.amazon.com/pm/serv-s3/?gclid=Cj0KCQjwwuG1BhCnARIsAFWBUC3J-Yduiyiq9oLppu44jUYJ1XG0W8lLG6z69mWHML3hlur_Zdo9LO0aAgyuEALw_wcB&trk=518a7bef-5b4f-4462-ad55-80e5c177f12b&sc_channel=ps&ef_id=Cj0KCQjwwuG1BhCnARIsAFWBUC3J-Yduiyiq9oLppu44jUYJ1XG0W8lLG6z69mWHML3hlur_Zdo9LO0aAgyuEALw_wcB:G:s&s_kwcid=AL!4422!3!645186213484!e!!g!!amazon%20s3!19579892800!143689755565)（Amazon S3）存储桶中。
- 事件通知会发送到 [Amazon Simple Queue Service](https://aws.amazon.com/sqs/)（Amazon SQS）队列，以便为每个文件排队等待后续处理。Amazon SQS 充当缓冲区，让各组件能够以可靠的方式发送和接收消息而无需直接耦合，从而提升系统的可扩展性与容错能力。
- 文本提取 [AWS Lambda](https://aws.amazon.com/lambda/) 函数由 SQS 队列调用，处理队列中的每个文件，并使用 [Amazon Textract](https://aws.amazon.com/textract/) 从文档中提取文本。
- 提取出的文本数据被放入另一个 SQS 队列，等待下一个处理步骤。
- 文本摘要 Lambda 函数由这个包含提取文本的新队列调用。该函数向 SageMaker JumpStart 发送请求，那里部署了一个 Meta Llama 文本生成模型，根据所提供的 prompt 对内容进行摘要。
- 同时，InvokeSageMaker Lambda 函数被调用来执行比对与评估。它把提取出的文本与模型训练所依据的 BQA 标准进行比对，评估文本的合规性、质量和其他相关指标。
- 摘要数据和评估结果存储在 [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) 表中
- 收到请求时，InvokeBedrock Lambda 函数调用 Amazon Bedrock 生成式 AI 摘要和评论。该函数会构造一个详细的 prompt，用于引导 [Amazon Titan Express 模型](https://aws.amazon.com/bedrock/amazon-models/titan/) 评估该大学提交的材料。

## 使用 Amazon Bedrock 进行 prompt 工程

为了利用 Amazon Bedrock 的能力，并确保生成的输出符合所期望的结构与格式要求，我们按照以下指引精心设计了一个 prompt：

- **证据提交** —— 在相关指标下呈现机构提交的证据，为模型提供评估所需的上下文
- **评估标准** —— 概述评估证据时应依据的具体标准
- **评估指令** —— 按以下方式指示模型：  如果证据与该指标无关，则标明 N/A 根据标准评估该大学的自我评估 为每条评论给出 1–5 分，并直接引用内容中的证据
- **响应格式** —— 指定响应为要点形式，聚焦相关分析与证据，字数限制为 100 词

要使用这个 prompt 模板，你可以在项目中创建一个自定义 Lambda 函数。该函数应负责获取所需数据，例如指标名称、大学提交的证据以及评分标准。在函数内部包含该 prompt 模板，并用获取到的数据动态填充占位符 `(${indicatorName}, ${JSON.stringify(allContent)}` 和 `${JSON.stringify(c.comment)})`。

随后，Amazon Titan Text Express 模型将根据所提供的 prompt 指令生成评估响应，并遵循指定的格式与指引。你可以在函数中处理和分析模型的响应，提取合规评分、相关分析和证据。

以下是一个示例 prompt 模板：

```
for (const c of comments) {
        const prompt = `
        Below is the evidence submitted by the university under the indicator "${indicatorName}":
        ${JSON.stringify(allContent)}
    
         Analyze and Evaluate the university's eviedence based on the provided rubric criteria:
        ${JSON.stringify(c.comment)}

        - If the evidence does not relate to the indicator, indicate that it is not applicable (N/A) without any additional commentary.
        
       Choose one from the below compliance score based on evidence submitted:
       1. Non-compliant: The comment does not meet the criteria or standards.
        2.Compliant with recommendation: The comment meets the criteria but includes a suggestion or recommendation for improvement.
        3. Compliant: The comment meets the criteria or standards.

        THE END OF THE RESPONSE THERE SHOULD BE EITHER SCORE: [SCORE: COMPLIANT OR NON-COMPLIANT OR COMPLIANT WITH RECOMMENDATION]
        Write your response in concise bullet points, focusing strictly on relevant analysis and evidence.
        **LIMIT YOUR RESPONSE TO 100 WORDS ONLY.**

        `;

        logger.info(`Prompt for comment ${c.commentId}: ${prompt}`);

        const body = JSON.stringify({
          inputText: prompt,
          textGenerationConfig: {
            maxTokenCount: 4096,
            stopSequences: [],
            temperature: 0,
            topP: 0.1,
          },
        });
```

以下截图展示了 Amazon Bedrock 生成响应的示例。

![Amazon Bedrock 生成的响应](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/10/ml-17266-bedrock-response.png)

## 成果

Amazon Bedrock 的实施为机构带来了变革性收益。通过自动化和简化对大量文档（包括 SER、支撑证据和各种媒体格式）的收集与分析，机构可以在报告流程和审查准备方面获得更高的准确性与一致性。这不仅减少了人工数据处理相关的时间与成本，还提升了对质量期望的符合度，从而增强机构的公信力与质量。

对 BQA 而言，该实施帮助其实现了以简化报告流程为重点的一项战略目标，并在多项关键指标上取得显著改善，大幅提升了其运营的整体效率与效果。

预期的主要成功指标包括：

- 生成 70% 准确且符合标准的自我评估报告所需的时间更短，从而提升整体效率。
- 降低报告流程中出错或不合规的风险，强化对既定准则的遵循。
- 能够把冗长的提交材料概括为简洁的要点，让 BQA 审查人员快速分析和理解最关键的信息，把证据分析时间减少 30%。
- 更准确的合规反馈功能，使审查人员能够依据既定标准与准则有效评估提交材料，同时通过流程优化把运营成本降低 30%。
- 通过无缝交互增强透明度与沟通，使用户能够轻松地索取补充文档或澄清说明。
- 实时反馈，让机构能够及时做出必要调整。这对保持提交材料准确与完整尤为有用。
- 通过对数据提供洞见来增强决策。这帮助大学识别改进领域，并做出数据驱动的决策以改进其流程与运营。

以下截图展示了使用 Amazon Bedrock 生成新评估的示例

![使用 Amazon Bedrock 生成新评估](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/10/ml-17266-generate-comments.png)

## 结论

本文概述了在教育与培训质量管理局（BQA）实施 Amazon Bedrock 的情况，展示了生成式 AI 在革新教育与培训领域质量保证流程方面的变革潜力。如果希望进一步探索技术细节，本次实施的完整代码可在以下 [GitHub 仓库](https://github.com/bahrain-bp/bqa-genai-challenge/tree/main) 中获取。如果你有兴趣与我们开展类似的概念验证，请把你的挑战设想提交到 [Bahrain Polytechnic](https://cic.polytechnic.bh/) 或 [University of Bahrain](https://cic.uob.edu.bh/uob-cic-challenge-submission-form/) 的 CIC 网站。

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/11/ml-17266-headshot-1.jpg)Maram AlSaegh** 是 Amazon Web Services（AWS）的云基础设施架构师，她支持 AWS 客户加速上云之旅。目前，她专注于为公共部门机构开发利用生成式 AI 和机器学习（ML）的创新解决方案。
