---
vendor: aws_bedrock
title: Orchestrate an intelligent document processing workflow using tools in Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/orchestrate-an-intelligent-document-processing-workflow-using-tools-in-amazon-bedrock
date: 2025-02-21
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 1145e0a43150
---

# 使用 Amazon Bedrock 中的工具编排智能文档处理工作流

[生成式 AI](https://aws.amazon.com/ai/generative-ai/) 正在革新企业自动化，让 AI 系统能够理解上下文、做出决策并独立行动。生成式 AI 基础模型（FM）具备理解上下文和做出决策的能力，正成为解决复杂业务问题的强大伙伴。在 AWS，我们利用 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 中模型的能力，推动那些传统上难以理顺的复杂流程实现自动化。

本文聚焦其中一个复杂工作流：文档处理。它展示了生成式 AI 如何简化涉及多种数据类型与格式的运营工作。

## 文档处理的挑战

文档处理通常涉及三大类文档：

- 结构化——例如字段固定的表单
- 半结构化——具有可预测的信息集合，但布局或呈现方式可能不同的文档
- 非结构化——例如成段的文本或笔记

传统上，处理这些多样的文档类型一直是许多组织的痛点。基于规则的系统或专门的机器学习（ML）模型往往难以应对真实文档的多样性，尤其是在处理半结构化和非结构化数据时。

我们演示了生成式 AI 连同[外部工具使用](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html)如何为这一挑战提供更灵活、适应性更强的解决方案。通过医生诊室处理患者健康资料包这一实用用例，你将看到该技术如何从全部三类文档中提取并综合信息，从而有望提升数据准确性和运营效率。

## 解决方案概览

该智能文档处理解决方案使用 Amazon Bedrock FM 来编排一个复杂工作流，处理内容类型混合的多页医疗文档。方案使用 FM 的工具使用能力，通过 Amazon Bedrock [Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html) 访问。这使 FM 不仅能处理文本，还能主动与各种外部工具和 API 交互，以完成复杂的文档分析任务。

该方案采用战略性的多模型方法，通过为每项任务选择最合适的模型来同时优化性能与成本：

- [Anthropic 的 Claude 3 Haiku](https://aws.amazon.com/blogs/aws/upgraded-claude-3-5-sonnet-from-anthropic-available-now-computer-use-public-beta-and-claude-3-5-haiku-coming-soon-in-amazon-bedrock/) – 因其低延迟和高成本效益而担任工作流编排器。该模型强大的推理和工具使用能力使其非常适合以下工作：协调整个文档处理 pipeline；为不同文档类型做出路由决策；调用合适的处理函数；管理工作流状态
- [Anthropic 的 Claude 3.5 Sonnet (v2)](https://aws.amazon.com/blogs/aws/upgraded-claude-3-5-sonnet-from-anthropic-available-now-computer-use-public-beta-and-claude-3-5-haiku-coming-soon-in-amazon-bedrock/) – 因其先进的推理能力而被采用，尤其是强大的视觉处理能力，在解读图表方面尤为出色。其关键优势包括：解读复杂的文档布局与结构；从表格和表单中提取文本；处理医疗图表和手写笔记；把非结构化的视觉信息转换为结构化数据

通过 Amazon Bedrock Converse API 标准化的工具使用（函数调用）接口，这些模型可以无缝协作，调用文档处理函数、调用外部 API 进行数据校验、触发存储操作并执行内容转换任务。该 API 是这一智能工作流的基础，为模型通信提供统一接口，并在整个处理 pipeline 中保持会话状态。该 API 对工具定义和函数调用的标准化方式，为不同处理阶段提供了一致的交互模式。关于工具使用如何工作的更多细节，请参阅[完整的工具使用工作流](https://github.com/aws-samples/prompt-engineering-with-anthropic-claude-v-3/blob/main/10_2_3_Complete_Tool_Use_Workflow.ipynb)。

该方案引入 [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 来实施健壮的内容过滤策略与敏感信息检测，通过自动检测和掩码能力确保个人健康信息（PHI）和个人可识别信息（PII）得到恰当保护，同时在整个文档处理工作流中维持行业标准合规。

## 前提条件

在推进该解决方案之前，你需要以下前提条件。本文使用 `us-west-2` AWS 区域。关于可用区域的详细信息，请参阅 [Amazon Bedrock 端点与配额](https://docs.aws.amazon.com/general/latest/gr/bedrock.html)。

- 一个 [AWS 账户](https://signup.aws.amazon.com/billing/signup)，其 [AWS Identity and Access Management](https://aws.amazon.com/iam)（IAM）角色具有访问 Amazon Bedrock 和 [Amazon SageMaker Studio](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated.html) 的权限。
- 在 Amazon Bedrock 中访问 Anthropic 的 Claude 3.5 Sonnet (v2) 和 Claude 3 Haiku 模型的权限。相关说明请参阅[访问 Amazon Bedrock 基础模型](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)和 [CreateInferenceProfile](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_CreateInferenceProfile.html)。
- 创建 Amazon Bedrock guardrail 的权限。更多信息请参阅[创建 guardrail](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-create.html)。

## 用例与数据集

在我们的示例用例中，我们考察一家医疗机构的新患者入院流程。该工作流处理一个包含三种不同文档类型的患者健康信息资料包：

- 结构化文档——一份带有标准化字段的新患者入院登记表，字段涵盖个人信息、病史和当前症状。该表采用一致的布局，字段和复选框定义清晰，是结构化文档的理想示例。
- 半结构化文档——一张包含关键承保信息的健康保险卡。尽管保险卡通常包含相似信息（保单号、团体 ID、承保日期），但它们来自不同提供商，布局和格式各异，体现了这类文档的半结构化特性。
- 非结构化文档——一份初诊时的手写医生笔记，包含自由形式的观察、初步诊断和治疗建议。这代表了非结构化文档中最具挑战性的一类，其中的信息不受任何预定格式或结构约束。

示例文档可从以下 [GitHub 仓库](https://github.com/aws-samples/anthropic-on-aws/blob/main/medical-idp/docs/new-patient-registration.pdf)下载。

这个医疗用例尤其贴切，因为它涵盖文档处理中的常见挑战：对高准确性的需求、对医疗数据隐私要求的合规，以及在单一工作流中处理多种文档格式的能力。该患者资料包中文档的多样性说明，现代智能文档处理解决方案必须足够灵活，能在处理不同结构化程度的文档时保持一致性和提取准确性。

下图展示了解决方案工作流。

![使用外部工具调用的 IDP 流程](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/02/11/blog.drawio-3-980x1024.png)

这个自编排工作流展示了现代生成式 AI 解决方案如何在改造医疗场景中传统文档处理工作流时，兼顾能力、性能与成本效益。

## 部署解决方案

- 创建一个 Amazon SageMaker 域。相关说明请参阅“Amazon SageMaker AI 快速设置”。
- 启动 SageMaker Studio，然后创建并启动一个 JupyterLab 空间。相关说明请参阅“创建空间”。
- 创建一个 guardrail。重点是添加会掩码 PII 或 PHI 的敏感信息过滤器。
- 从 GitHub 仓库克隆代码：`git clone https://github.com/aws-samples/anthropic-on-aws.git`
- 切换目录到克隆仓库的根目录：`cd medical-idp`
- 安装依赖：`pip install -r requirements.txt`
- 用你在第 3 步创建的 guardrail ID 更新 setup.sh。然后设置 ENV 变量：`source setup.sh`
- 最后，启动 Streamlit 应用：`streamlit run streamlit_app.py`

现在你可以开始探索使用 Amazon Bedrock 的智能文档处理工作流了。

## 技术实现

该方案围绕 Amazon Bedrock Converse API 和工具使用框架构建，由 Anthropic 的 Claude 3 Haiku 担任主编排器。当文档通过 Streamlit 界面上传后，Haiku 分析请求，并通过查阅 `ToolConfig` 中的工具定义来确定所需的工具调用顺序。这些定义包括以下工具：

- 文档处理 pipeline——处理初始的 PDF 处理和分类
- 文档笔记处理——从医疗笔记中提取信息
- 新患者信息处理——处理患者入院登记表
- 保险表单处理——处理保险卡信息

以下代码是用于提取问诊笔记的示例工具定义。这里 `extract_consultation_notes` 表示编排工作流将要调用的函数名称，`document_paths` 定义了将传给该函数的输入参数 schema。FM 会结合上下文从文档中提取信息并传给该方法。每一步都会定义类似的 `toolspec`。完整的 `toolspec` 定义请参阅 [GitHub 仓库](https://github.com/aws-samples/anthropic-on-aws/blob/4c2365cc6d763b0a48d253da2e67beef7f702f16/medical-idp/utils/constants.py#L107)。

```
{
            "toolSpec": {
                "name": "extract_consultation_notes",
                "description": "Extract diagnostics information from a doctor's consultation notes. Along with the extraction include the full transcript in a <transcript> node",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "document_paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Paths to the files that were classified as DOC_NOTES"
                            }
                        },
                        "required": ["document_paths"]
                    }
                }
            }
        }
```

当 PDF 文档通过 Streamlit 界面上传后，它会被临时存储，并连同工具规范和用户 prompt 一起传给 FileProcessor 类：

```
prompt = ("1. Extract 2. save and 3. summarize the information from the patient information package located at " + tmp_file + ". " +
                          "The package might contain various types of documents including insurance cards. Extract and save information from all documents provided. "
                          "Perform any preprocessing or classification of the file provided prior to the extraction." + 
                          "Set the enable_guardrails parameter to " + str(enable_guardrails) + ". " + 
                          "At the end, list all the tools that you had access to. Give an explantion on why each tool was used and if you are not using a tool, explain why it was not used as well" + 
                          "Think step by step.")
                processor.process_file(prompt=prompt, 
toolspecs=toolspecs,...
```

`BedrockUtils` 类通过 Amazon Bedrock Converse API 管理与 Anthropic 的 Claude 3 Haiku 的会话。它维护会话状态并处理工具使用工作流：

```
# From bedrockutility.py
def invoke_bedrock(self, message_list, system_message=[], tool_list=[],
                  temperature=0, maxTokens=2048, guardrail_config=None):
    response = self.bedrock.converse(
        modelId=self.model_id,
        messages=message_list,
        system=system_message,
        inferenceConfig={
            "maxTokens": maxTokens,
            "temperature": temperature
        },
        **({"toolConfig": {"tools": tool_list}} if tool_list else {})
    )
```

当处理器收到文档时，它会与 Anthropic 的 Claude 3 Haiku 启动一个会话循环，由后者分析文档并根据内容确定使用哪些工具。该模型充当智能编排器，就以下事项做出决策：

- 调用哪些文档处理工具
- 处理步骤的顺序
- 如何处理同一资料包中的不同文档类型
- 何时进行总结并结束处理

这种编排通过一个持续的会话循环来管理，该循环处理工具请求及其结果，直到整个文档资料包处理完毕。

工作流中的第一个关键决策是启动文档分类过程。通过 `DocumentClassifier` 类，方案使用 Anthropic 的 Claude 3.5 Sonnet 分析上传文档的每一页，并将其归入三种主要类型：入院登记表、保险卡和医生笔记：

```
# from document_classifier.py
class DocumentClassifier:
    def __init__(self, file_handler):
        self.sonnet_3_5_bedrock_utils = BedrockUtils(
            model_id=ModelIDs.anthropic_claude_3_5_sonnet
        )
        
    def categorize_document(self, file_paths):
        # Convert documents to binary format for model processing
        binary_data_array = []
        for file_path in file_paths:
            binary_data, media_type = self.file_handler.get_binary_for_file(file_path)
            binary_data_array.append((binary_data[0], media_type))

        # Prepare message for classification
        message_content = [
            {"image": {"format": media_type, "source": {"bytes": data}}}
            for data, media_type in binary_data_array
        ]
        
        # Create classification request
        message_list = [{
            "role": 'user',
            "content": [
                *message_content,
                {"text": "What types of document is in this image?"}
            ]
        }]
        
        # Define system message for classification
        system_message = [{
            "text": '''You are a medical document processing agent. 
                      Categorize images as: INTAKE_FORM, INSURANCE_CARD, or DOC_NOTES'''
        }]
        
        # Get classification from model
        response = self.sonnet_3_5_bedrock_utils.invoke_bedrock(
            message_list=message_list,
            system_message=system_message
        )
        return [response['output']['message']]
```

根据分类结果，FM 决定下一个要调用的工具。工具的描述和输入 schema 精确定义了需要提取哪些信息。延续前面的示例，假设下一页要处理的是问诊笔记。工作流将调用 `extract_consultation_notes` 函数。该函数处理文档以提取详细的医疗信息。与前面讨论的分类过程一样，它首先把文档转换为适合模型处理的二进制格式。准确提取的关键在于图像和 system message 的组合方式：

```
def extract_info(self, file_paths):
    # Convert documents to binary data
    # This will follow the same pattern to as in the classification function
    message_content = [
        {"image": {"format": media_type, "source": {"bytes": data}}}
        for data, media_type in binary_data_array
    ]

    message_list = [{
        "role": 'user',
        "content": [
            *message_content,  # Include the processed document images
            {"text": '''Extract all information from this file
                       If you find a visualization
                           - Provide a detailed description in natural language
                           - Use domain specific language for the description
                    '''}
        ]
    }]
    
    system_message = [{
        "text": '''You are a medical consultation agent with expertise in diagnosing and treating various health conditions.
                   You have a deep understanding of human anatomy, physiology, and medical knowledge across different specialties.
                   During the consultation, you review the patient's medical records, test results, and documentation provided.
                   You analyze this information objectively and make associations between the data and potential diagnoses.
Associate a confidence score to each extracted information. This should reflect how confident the model in the extracted value matched the requested entity.
        '''}
    ]
    
    response = self.bedrock_utils.invoke_bedrock(
        message_list=message_list,
        system_message=system_message
    )
    return [response['output']['message']]
```

system message 有三个关键作用：

- 建立医学领域专业知识，以便准确解读。
- 为处理不同类型的信息（文本和可视化内容）提供指导。
- 提供自评的置信度。尽管这不是一个独立的评分机制，但该分数在方向上能指示模型对自身提取结果的置信程度。

按照同样的模式，FM 会使用 `toolspec` 定义中的其他工具来保存并汇总结果。

使用多模态 FM 完成提取任务的一个独特优势，在于它能深入理解自己所提取的文本。例如，以下代码是我们要求作为 `save_consultation_notes` 函数输入的数据 schema 摘要。完整定义请参阅 [constants.py](https://github.com/aws-samples/anthropic-on-aws/blob/main/medical-idp/utils/constants.py#L133) 中的代码。模型不仅需要转录文本，还要理解它，才能从非结构化文档中提取出这样的结构化数据。这大大减少了下游应用消费这些数据所需的后处理工作。

```
"consultation": {
                            "type": "object",
                            "properties": {
                            "date": {"type": "string"},
                            "concern": {
                                "type": "object",
                                "properties": {
                                    "primaryComplaint": {
                                        "type": "string",
                                        "description": "Primary medical complaint of the patient. Only capture the medical condition. no timelines"
                                    },
                                    "duration": {"type": "number"},
                                    "durationUnit": {"type": "string", "enum": ["days", "weeks", "months", "years"]},
                                    "associatedSymptoms": {
                                        "type": "object",
                                        "additionalProperties": {
                                            "type": "boolean"
                                        },
                                        "description": "Key-value pairs of symptoms and their presence (true) or absence (false)"
                                    },
                                    "absentSymptoms": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                },
                                "required": ["primaryComplaint", "duration", "durationUnit"]
                            }
```

这些文档包含大量个人可识别信息（PII）和个人健康信息（PIH）。要对这些信息进行脱敏，你可以把 enable_guardrails 传为 true。这会在信息提取过程中使用你之前设置的 guardrail，并掩码被识别为 PII 或 PIH 的信息。

```
processor.process_file(prompt=prompt, 
                                        enable_guardrails=True,
                                        toolspecs=toolspecs,
      …
)
```

最后，跨文档校验对于维持医疗场景中的数据准确性与合规至关重要。尽管当前实现通过[摘要 prompt](https://github.com/aws-samples/anthropic-on-aws/blob/main/medical-idp/utils/constants.py#L35)运行基本的一致性检查，组织仍可通过实现一个与自身特定业务规则和合规要求集成的专用校验工具来扩展该框架。这样的工具可以执行复杂的校验逻辑，例如保险单核验、预约日期一致性检查，或任何其他领域特定的校验要求，从而在整个文档资料包范围内提供完整的数据完整性。

## 未来考虑

随着 Amazon Bedrock 不断演进，多项强大功能可以集成到这个文档处理工作流中，以提升其企业就绪度、性能与成本效率。下面我们探讨这些先进能力如何把该方案提升到新层次：

- Amazon Bedrock 中的[推理配置文件](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html)为路由调用请求定义模型及其关联区域，从而支持用量跟踪、成本监控和跨区域推理等任务。这些配置文件帮助用户通过 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch) 日志跟踪指标、用成本分配标签监控成本，并通过把请求分散到多个区域来提高吞吐量。
- [Prompt caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) 适用于那些包含冗长重复上下文、且会被多次查询反复使用的工作负载。工作流无需为每份文档重新处理整个上下文，而是可以复用缓存的 prompt，这在跨不同工具工作流使用同一张图像时尤其有益。该功能支持多个缓存检查点，可在保持工作流智能编排能力的同时显著缩短处理时间并降低推理成本。
- [智能 prompt 路由](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html)可以根据性能与成本要求，为每项任务动态选择最合适的模型。工作流不必再显式指定 Anthropic 的 Claude 3 Haiku 负责编排、Anthropic 的 Claude 3.5 Sonnet 负责文档分析，而是可以用智能路由为每个请求自动选择 Anthropic 家族内的最优模型。这种方式简化了模型管理，同时通过单一端点对从简单结构化表单到复杂手写笔记的不同文档类型提供高性价比的处理。

## 结论

该智能文档处理解决方案展示了把 Amazon Bedrock FM 与工具使用能力结合、构建复杂的自编排工作流的威力。通过使用 Anthropic 的 Claude 3 Haiku 负责编排、Anthropic 的 Claude 3.5 Sonnet 负责复杂视觉任务，该方案能有效处理结构化、半结构化和非结构化文档，同时保持高准确性与合规标准。

这种方法的主要好处包括：

- 通过智能自动化减少人工处理
- 通过专用模型选择提升准确性
- 借助 guardrail 内置对敏感数据的合规能力
- 可适应多种文档类型的灵活架构
- 通过战略性的模型使用实现高性价比处理

随着组织持续推进数字化，这样的解决方案展示了生成式 AI 如何改造传统文档处理工作流。Amazon Bedrock 中强大的 FM 与工具使用框架相结合，为跨行业构建智能、可扩展的文档处理解决方案提供了坚实基础。

关于 Amazon Bedrock 及其能力的更多信息，请访问 [Amazon Bedrock 用户指南](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)。

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/02/13/raju-rangan-ml-blog-profile.png)

**Raju Rangan** 是 AWS 的高级解决方案架构师。他与政府资助的机构合作，帮助他们使用 AWS 构建 AI/ML 解决方案。不折腾云方案的时候，你会看到他和家人待在一起，或者与朋友打一场热闹的羽毛球。
