---
vendor: aws_bedrock
title: Build an intelligent eDiscovery solution using Amazon Bedrock Agents
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-an-intelligent-ediscovery-solution-using-amazon-bedrock-agents
date: 2025-07-25
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 8d2cb74e7b92
---

# 使用 Amazon Bedrock Agents 构建智能 eDiscovery 解决方案

法务团队在 eDiscovery 过程中把大量时间花在人工审阅文档上。这一过程涉及为法律诉讼分析电子邮件、合同、财务记录和协作系统中的电子存储信息。这种人工方式造成了严重的瓶颈：律师必须在每宗案件的数千份文档中识别受特权保护的通信、评估法律风险、提取合同义务并保持监管合规。该过程不仅耗费资源、耗时漫长，而且在处理大体量文档时容易发生人为错误。

[Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) 配合[多 agent 协作](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-multi-agent-collaboration.html)可直接应对这些挑战，帮助组织部署专门的 AI agent，并行处理文档，同时在复杂的法律工作流中保持上下文。多个 agent 同时工作，取代顺序式人工审阅——一个提取合同条款，另一个识别受特权保护的通信，全部由中央 orchestrator 协调。这种方式可将文档审阅时间缩短 60–70%，同时保持法律诉讼所要求的准确性和人工监督，不过实际表现会因文档复杂度和基础模型（FM）的选择而有所不同。

本文中，我们演示如何用 Amazon Bedrock Agents 构建一套智能 eDiscovery 解决方案，用于实时文档分析。我们展示如何为文档分类、合同分析、电子邮件审阅和法律文档处理部署专门的 agent，并通过多 agent 架构协同工作。我们梳理实现细节、部署步骤和最佳实践，帮助组织搭建一个可扩展的基础，以适配各自具体的 eDiscovery 需求。

## 解决方案概览

本方案演示了一套使用 Amazon Bedrock Agents 及其多 agent 协作功能的智能文档分析系统。系统使用多个专门的 agent 来分析法律文档、对内容分类、评估风险并提供结构化洞察。下图展示了解决方案架构。

![端到端的 AWS 法律文档处理架构，包含 Bedrock AI agents、S3 存储和多用户访问工作流](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/15/ML-18253-1.jpeg)

该架构图展示了 eDiscovery 文档分析的三条主要工作流：

- **实时文档分析工作流** – 律师与客户（已认证用户）可以上传文档，并通过移动端/Web 客户端和聊天进行交互。文档被实时处理以立即分析，不做持久化存储——上传的文档会直接传给 Amazon Bedrock Collaborator Agent 端点。
- **案件研究文档分析工作流** – 这条工作流专门面向律师（已认证用户）。它允许通过移动端/Web 客户端和聊天进行文档审阅与分析，侧重于对先前已处理文档做法律研究。
- **文档上传工作流 **– 律所客户（已认证用户）可以通过移动端/Web 客户端上传文档。文档通过 [AWS Transfer Family Web 应用](https://aws.amazon.com/aws-transfer-family/web-apps/)传输到 [Amazon Simple Storage Service](https://aws.amazon.com/s3)（Amazon S3）存储桶中存储。

虽然该架构支持全部三条工作流，但本文专门聚焦实时文档分析工作流的实现，原因有两个：它代表了为法务团队带来即时价值的核心功能，并且它提供了可以扩展以支持其他工作流的基础模式。实时处理能力展示了使这套解决方案对 eDiscovery 运营具有变革意义的多 agent 协调。

## 实时文档分析工作流

这条工作流通过协同工作的 AI agent 处理上传的文档，通常在文档上传后 1–2 分钟内完成分析。与每份文档可能要花数小时的传统人工审阅相比，系统通过立即提供结构化洞察来加速早期案件评估。该实现协调五个专门的 agent，并行处理文档的不同方面，如下表所列。

| **Agent 类型** | **主要功能** | **处理时间*** | **关键输出** |
| --- | --- | --- | --- |
| **Collaborator Agent** | 中央 orchestrator 与工作流管理器 | 2–5 秒 | 文档路由决策、汇总结果 |
| **Document Classification Agent** | 文档初步分诊与敏感度检测 | 5–10 秒 | 文档类型、置信度评分、敏感度标记 |
| **Email Analysis Agent** | 通信模式分析 | 10–20 秒 | 参与者关系图、会话线索、时间线 |
| **Legal Document Analysis Agent** | 法院提交文件与法律摘要分析 | 15–30 秒 | 案件引用、法律论点、程序性日期 |
| **Contract Analysis Agent** | 合同条款与风险评估 | 20–40 秒 | 当事方信息、关键条款、义务、风险评分 |

*处理时间是基于在 Amazon Bedrock 上使用 Anthropic 的 Claude 3.5 Haiku 进行测试的估算值，可能因文档复杂度和大小而不同。你所处环境中的实际表现可能有所差异。

我们来看一个处理示例法律和解协议的实例。该工作流由以下步骤组成：

- Collaborator Agent 判定该文档同时需要进行合同分析和法律分析。
- Contract Analysis Agent 提取当事方、付款条款和义务（40 秒）。
- Legal Document Analysis Agent 识别案件引用和先例（30 秒）。
- Document Classification Agent 标记机密等级（10 秒）。
- Collaborator Agent 把各项发现汇总成一份全面报告（15 秒）。

对这份示例文档而言，总处理时间约为 95 秒，而类似文档的人工审阅需要 2–4 小时。在接下来的章节中，我们逐步讲解如何部署完整的 eDiscovery 解决方案，包括 Amazon Bedrock Agents、Streamlit 前端以及所需的 AWS 资源。

## 前提条件

请确保已具备以下前提条件：

- 一个拥有 Amazon Bedrock、[AWS Identity and Access Management](https://aws.amazon.com/iam/)（IAM）和 [AWS CloudFormation](https://aws.amazon.com/cloudformation) 相应权限的 AWS 账户。
- 在你部署所在的 AWS Region 中，已获得 Anthropic 的 Claude 3.5 Haiku v1 的 [Amazon Bedrock 模型访问权限](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-modify.html)。你也可以为本解决方案使用自己选择的另一个[受支持模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)。如果你使用的模型不是默认的 Anthropic 的 Claude 3.5 Haiku v1，则必须在部署前修改 CloudFormation 模板，以体现所选模型的规格。撰写本文时，Anthropic 的 Claude 3.5 Haiku 可在美国东部（弗吉尼亚北部）、美国东部（俄亥俄）和美国西部（俄勒冈）使用。关于当前的模型可用性，请参见[按 AWS Region 划分的模型支持](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)。
- 已安装 [AWS Command Line Interface](https://aws.amazon.com/cli)（AWS CLI）并配置了适当的凭证。
- 已安装 Python 3.8 及以上版本。
- 可访问终端或命令提示符。

## 部署 AWS 基础设施

你可以部署以下 [CloudFormation 模板](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-18253/ML-LEGAL-Collab-CFT-Final-Haiku.yaml)，它会创建五个 Amazon Bedrock agent、推理配置文件以及配套的 IAM 资源。（所使用的 AWS 资源会产生费用。）请完成以下步骤：

- [启动](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create?stackName=EKS-Troubleshooter&templateURL=https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-18253/ML-LEGAL-Collab-CFT-Final-Haiku.yaml) CloudFormation 堆栈。

你将被重定向到 AWS CloudFormation 控制台。在堆栈参数中，模板 URL 会预先填好。

- 在 **EnvironmentName** 中填入你的部署名称（默认：`LegalBlogSetup`）。
- 检查并创建堆栈。

部署成功后，从 CloudFormation 堆栈的 **Outputs** 选项卡记下以下取值：

- `CollabBedrockAgentId`
- `CollabBedrockAgentAliasId`

![AWS CloudFormation 堆栈输出，显示 Bedrock agent 的配置详情](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/15/ML-18253-2.jpeg)

## 配置 AWS 凭证

测试 AWS 凭证是否可用：`aws sts get-caller-identity`如果你需要配置凭证，请使用以下命令：

```
aws configure
```

## 搭建本地环境

请完成以下步骤来搭建本地环境：

- 为你的项目新建一个目录：

```
mkdir bedrock-document-analyzer
cd bedrock-document-analyzer
```

- 设置 Python 虚拟环境：

```
#On macOS/Linux:
source venv/bin/activate 
#On Windows:
venv\Scripts\activate
```

- 下载 Streamlit 应用：

```
curl -O https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-18253/eDiscovery-LegalBlog-UI.py
```

- 安装依赖：

```
pip install streamlit boto3 PyPDF2 python-docx
```

## 配置并运行应用

请完成以下步骤：

- 在终端或命令提示符中执行以下命令，运行已下载的 Streamlit 前端 UI 文件 [eDiscovery-LegalBlog-UI.py](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-18253/eDiscovery-LegalBlog-UI.py)：

```
streamlit run eDiscovery-LegalBlog-UI.py
```

该命令会启动 Streamlit 服务器，并自动在你的默认 Web 浏览器中打开应用。

- 在 **Agent configuration** 下填写以下取值：  在 **AWS_REGION** 中填入你的 Region。在 **AGENT_ID** 中填入 Amazon Bedrock Collaborator Agent ID。在 **AGENT_ALIAS_ID** 中填入 Amazon Bedrock Collaborator Agent Alias ID。
- 选择 **Save Configuration**。

![Streamlit 驱动的配置界面，用于 Amazon Bedrock Agent 设置，包含 Region 选择和实现指引](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/15/ML-18253-3.jpeg)

现在你可以上传文档（TXT、PDF 和 DOCX）进行分析并与之交互。

## 测试解决方案

以下是对该应用进行测试的演示。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-18253/ML-18253-4.gif)

## 实现考量

尽管 Amazon Bedrock Agents 显著简化了 eDiscovery 工作流，组织在实施 AI 驱动的文档分析解决方案时仍应考虑几个关键因素。请考虑以下法律行业在合规与治理方面的要求：

- **律师—客户特权保护** – AI 系统必须维护保密边界，在处理过程中不得暴露受特权保护的通信
- **跨司法辖区合规** – GDPR、CCPA 以及行业特定法规会因地区和案件类型而异
- **审计轨迹要求** – 法律程序要求对所有 AI 辅助决策提供完整的处理文档记录
- **职业责任** – 律师仍需对 AI 的输出负责，并且必须对所使用的工具展现出胜任能力

你可能还会遇到技术实现上的挑战，例如文档处理的复杂度：

- **文档质量参差不齐** – 扫描版 PDF、手写批注和损坏文件都需要预处理策略
- **格式多样** – 法律文档横跨电子邮件、合同、法院提交文件和多媒体内容，需要不同的处理方式
- **规模管理** – 涉及超过 100,000 份文档的大型案件需要谨慎的资源规划和并发处理优化

系统集成也有特定要求：

- **存量系统兼容性** – 大多数律所使用既有的案件管理系统，需要无缝集成
- **认证工作流** – 多角色访问（律师、律师助理、客户）具有不同的权限级别
- **AI 置信度阈值** – 依据处理置信度评分来确定何时需要人工审阅

此外，还要考虑你的人机协作框架。最成功的 eDiscovery 实现会在关键决策点保留人工监督。尽管 Amazon Bedrock Agents 擅长自动化文档分类和元数据提取等常规任务，法律专业人士在以下方面仍然不可或缺：

- 需要结合上下文理解的复杂法律解释
- 影响案件策略的特权判定
- 对 AI 生成洞察的质量控制
- 对文档关系及案件影响的战略性分析

这种协作方式优化了 eDiscovery 流程——AI 处理耗时的数据处理工作，法律专业人士则专注于需要人类判断和专业能力的高风险决策。就你的实施策略而言，可以考虑分阶段部署的方式。组织应当实施分阶段上线，以在建立信心的同时把风险降到最低：

- 使用低风险文档类别（常规往来函件、标准合同）的试点项目
- 借助专门的 agent 和更广泛的用户群体做受控扩展
- 全量部署，在全组织范围内启用完整的多 agent 协作

最后，考虑以下成功规划的最佳实践：

- 为模型更新和版本控制建立清晰的治理框架
- 为新 agent 部署制定标准化的测试规程
- 为需要人工介入的边缘情况制定升级处理流程
- 在验证期实施并行处理以保持准确性

通过预先处理这些考量，法务团队可以促成更顺利的实施，最大化 AI 驱动文档分析带来的收益，同时保持法律程序所要求的准确性和监督。

## 清理

如果你决定不再使用该解决方案，请完成以下步骤，以移除该方案及通过 AWS CloudFormation 部署的相关资源：

- 在 AWS CloudFormation 控制台的导航窗格中选择 **Stacks**。
- 找到你在部署过程中创建的堆栈（你曾为它指定名称）。
- 选中该堆栈并选择 **Delete**。

## 成果

Amazon Bedrock Agents 把 eDiscovery 从耗时的人工流程转变为高效的 AI 驱动运营，在各类商业服务组织中带来可衡量的运营改善。借助多 agent 架构，组织可以在 1–2 分钟内处理文档，而类似文档的人工审阅需要 2–4 小时，在保持准确性和合规要求的同时实现 60–70% 的审阅时间缩减。来自金融服务行业的一个代表性实现展示了这种变革潜力：一家大型机构把其合规审阅流程从需要超过 10,000 小时、448 页的人工工作流，转变为自动化系统，将外部审计时间从 1,000 小时缩短到 300–400 小时，将内部审计从 800 小时缩短到 320–400 小时。该机构现在以现有人员每年开展 30–40 次内部审阅，同时在各次评估中取得更高的准确性和一致性。这些成果展示了在各类实现中的潜力：实施该解决方案的组织可以从试点阶段的初步效率提升，发展到全量部署时 60–70% 的审阅时间缩减。除节省时间之外，该解决方案还带来战略优势，包括资源优化，帮助法律专业人士专注于高价值分析而非常规文档处理；通过系统化地识别受特权保护的通信改善合规状况；以及适应不断演变的法律技术要求、面向未来的基础设施。

## 结论

Amazon Bedrock 多 agent 协作、实时处理能力与本文提供的可扩展架构相结合，为法务团队带来即时的运营收益，同时让他们为未来的 AI 进展做好准备——从而形成由 AI 效率与人类专业知识构成的强大协同，这也正是现代法律实践的标志。

要进一步了解 Amazon Bedrock，请参考以下资源：

- [GitHub 仓库：Amazon Bedrock Workshop](https://github.com/aws-samples/amazon-bedrock-workshop)
- [Amazon Bedrock 用户指南](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
- [工作坊：面向 AWS Cloud Operations 的 GenAI](https://catalog.workshops.aws/cloudops-genai/en-US)
- [工作坊：在 AWS 上为多种内容类型使用生成式 AI](https://catalog.us-east-1.prod.workshops.aws/genai-on-aws/)

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/08/09/puneeth.jpg)**Puneeth Ranjan Komaragiri** 是 AWS 的首席技术客户经理。他尤其热衷于监控与可观测性、云财务管理以及生成式 AI 领域。在目前的岗位上，Puneeth 乐于与客户紧密协作，凭借自己的专业能力帮助客户为其云工作负载设计与架构，以实现最佳的规模与韧性。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/17/ksainam.jpg)Pramod Krishna** 是 AWS 的高级解决方案架构师。他作为值得信赖的顾问服务客户，帮助客户在 AWS Cloud 上创新并构建架构良好的应用。工作之外，Krishna 喜欢阅读、音乐和旅行。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/17/sggifts-1.jpg)Sean Gifts** 是 AWS 的高级技术客户经理。他热衷于帮助客户实现应用现代化，尤其是使用无服务器框架的事件驱动架构。Sean 乐于用简单、可扩展的解决方案帮助客户改进架构。工作之外，他喜欢锻炼、品尝新食物和旅行。
