---
vendor: aws_bedrock
title: Innovate business logic by implementing return of control in Amazon Bedrock Agents
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/innovate-business-logic-by-implementing-return-of-control-in-amazon-bedrock-agents
date: 2025-06-16
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 5633e68f44cd
---

# 通过实现 Amazon Bedrock Agents 的 return of control 来创新业务逻辑

在分布式系统和微服务架构的语境下，协调各种组件之间的通信是一项重大挑战。然而，随着 [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) 的推出，这一局面正在改变：它为 agent 的创建提供了更简便的方式，并实现了 return of control 能力的无缝集成。在本文中，我们探讨 Amazon Bedrock Agents 如何革新 agent 创建，并展示 [return of control](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-returncontrol.html) 能力在编排多个系统之间复杂交互时的效力。

Amazon Bedrock Agents 简化了分布式系统中 agent 的创建、部署和管理。借助 [AWS Lambda](https://aws.amazon.com/lambda/) 和 [AWS Step Functions](https://aws.amazon.com/step-functions/) 的能力，Amazon Bedrock Agents 抽象掉了 agent 实现的复杂性，这意味着开发者可以专注于构建健壮且可扩展的应用，而无需担心基础设施管理。

在需要处理把控制权交还给用户或系统的各种场景中，你都可以使用 Amazon Bedrock 中的 agent。这些用例包括对话式助手、任务自动化、决策支持系统、交互式教程与引导式演练，以及虚拟助手。在这些用例中，agent 的关键之处在于它们能够处理把控制权返回给用户或系统的过程。这使得交互更自然、更及时，用户感觉自己在掌控流程，同时仍然受益于 agent 的引导和自动化能力。

## 解决方案概览

在本文中，我们演示一个使用 Amazon Bedrock Agents 的自动化个性化投资组合方案。该方案调用第三方 API 获取用户当前的投资组合，然后使用 Amazon Bedrock 上可用的[基础模型](https://aws.amazon.com/what-is/foundation-models/)（FM）对其进行分析，结合最终用户提供的输入直接产出建议，展示了与 Amazon Bedrock Agents 集成的 return of control 能力。

该方案结合同步数据检索与[生成式 AI](https://aws.amazon.com/generative-ai/)，提供与用户特定财务目标和风险承受能力相匹配的定制化投资建议。通过引入[机器学习](https://aws.amazon.com/ai/machine-learning/)（ML）和模拟技术，系统可以生成个性化投资组合并评估其潜在表现，确保推荐方案针对个人需求进行了优化。

借助 Amazon Bedrock Agents，把控制权返回给调用该 agent 的应用这一能力，可以让应用层处理外部函数和业务逻辑，而不必使用 Lambda 函数。这样一来，应用可以管理外部交互并返回响应，同时 agent 继续其编排。下图展示了这一点。

[![示意图](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/arch.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/arch.png)

返回控制权的选项在两种主要场景中特别有用：

- 从现有应用调用 API，而不是构建一个需要相应身份验证和网络配置的新 Lambda 函数
- 处理可能运行超过 15 分钟、无法通过 Lambda 函数完成的任务，这类任务需要容器、虚拟服务器或 AWS Step Functions 之类的工作流编排工具

以下示例代码在代码中处理 return of control，并使用 Amazon Bedrock Agents。借助 Amazon Bedrock Agents 功能，你可以在后端服务中管理 Amazon Bedrock Agents 的 return of control，并简化应用集成。为演示这一点，我们提供了以下四段代码：`external-bedrock-agent-api.py`、`streamlit-app-portfolio-recommender.py`、`Portfolio-Recommender-CFN-Template.yaml` 和 `requirements.txt`，以及复现该场景的详细步骤。

[external-bedrock-agent-api](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-16807/external-bedrock-agent-api.py) 代码使用 Amazon Bedrock Agents 和 [Flask](https://pypi.org/project/Flask/) 实现了一个投资组合推荐系统。以下是所用函数的高层次概览：

- **fetch_user_data**：处理用户档案信息，例如风险承受能力或投资目标
- **generate_portfolios**：创建具有不同风险等级的示例投资组合
- **fetch_custom_portfolio**：结合用户数据与投资组合生成
- **send_custom_portfolio_as_email**：使用已验证的 [Amazon Simple Email Service](https://aws.amazon.com/ses/)（Amazon SES）电子邮件身份，通过电子邮件发送投资组合建议
- **/sns-handler 端点**：该 API 端点接收携带用户投资偏好的 POST 请求，处理包含用户偏好细节的消息，调用 Amazon Bedrock agent 生成建议，并处理建议的电子邮件发送

[streamlit-app-portfolio-recommender](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-16807/streamlit-app-portfolio-recommender.py) 代码是一个用于投资组合推荐的 [Streamlit](https://pypi.org/project/streamlit/) Web 应用。该代码设置了网页的标题和配置。应用通过表单元素收集若干信息：

- **电子邮件地址** – 文本输入
- **财务目标** – 下拉菜单，选项包括退休、财富积累和被动收入
- **风险承受能力** – 下拉菜单，选项包括低、中、高
- **投资期限** – 下拉菜单，选项包括短期和长期
- **环境、社会与治理（ESG）偏好** – 用于环境、社会与治理偏好的复选框
- **电子邮件偏好** – 用于选择通过电子邮件接收建议的复选框

系统通过一个 Portfolio Generation Function 运行，该函数会主动向本地 API 端点发送 POST 请求。这个函数把用户偏好转换为 JSON 数据，并把 API 响应或错误消息回传给用户。

显示结果的流程始于用户点击 Submit 按钮，这会以其具体输入触发 `custom_portfolio` 函数。执行成功时，系统会在文本区域显示投资组合建议；如果过程中出现任何问题，则会立即用错误消息提醒用户。

## 解决方案演练

请按以下步骤在 US East (N. Virginia) us-east-1 [区域](https://docs.aws.amazon.com/glossary/latest/reference/glos-chap.html#region)中设置环境并测试该应用。

要在你的 AWS 账户中于 Amazon Bedrock 上启用 Anthropic 的 Claude 模型：

- 在 Amazon Bedrock 控制台上，在左侧导航窗格的 **Amazon Bedrock 配置**下，选择 **模型访问**
- 选择 **Claude 3 Sonnet**，如下图所示

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot123.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot123.png)

- 要创建 Amazon Bedrock agents、相关操作组、[Amazon SageMaker AI](https://aws.amazon.com/sagemaker-ai/) 域、示例用户配置和 JupyterLab 空间，请按以下步骤操作：

- 调用 [Portfolio-Recommender-CloudFormation-Template.yml](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-16807/Portfolio-Recommender-CloudFormation-Template.yml) 处的 [AWS CloudFormation](https://aws.amazon.com/cloudformation/) 模板 为堆栈指定一个名称 为 `EmailIdentityParameter` 提供一个电子邮件地址

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot223.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot223.png)

- 勾选该复选框，确认模板包含 [AWS Identity and Access Management](https://aws.amazon.com/iam/)（IAM）资源，如下图所示

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot323.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot323.png)

- 监控 AWS CloudFormation，直至其完成资源创建过程。你可以查看堆栈详情的输出选项卡来验证部署是否成功，该选项卡会显示 `AgentId` 和 `AgentAliasId` 的值，如下图所示。

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot423.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot423.png)

你会收到来自 AWS 的电子邮件地址验证请求邮件，它针对 US East (N. Virginia) 区域。请选择邮件中的链接完成验证。

创建 CloudFormation 资源后，请按以下步骤访问 Amazon SageMaker Studio：

- 在 Amazon SageMaker AI 控制台上，在左侧导航窗格的 **管理员配置**下，选择 **域**
- 选择由 CloudFormation 模板创建的 **bedrock-return-of-control-demo** 域，如下图所示

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot523.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot523.png)

- 选择 **用户配置文件** 选项卡
- 要打开 SageMaker Studio 环境，请在 **用户配置文件** 下，于右侧 **sagemakeruser** 配置文件旁选择 **启动**。在下拉菜单中选择 **Studio**，如下图所示

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot623.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot623.png)

你现在应该会看到 SageMaker Studio 主页。这个环境就是你将执行 Python 脚本以设置应用的地方。

要访问本实验的 JupyterLab 环境，请按以下步骤操作：

- 在 SageMaker Studio 控制台上，在左侧导航窗格的 **应用程序**下，选择 **JupyterLab**
- 你会找到为本实验预先配置好的 bedrock-agent-space。其 **Status** 应为 **Stopped**。在右侧 **Action** 下，选择 **Run**
- 在 30–40 秒内，JupyterLab 应用状态会从 **Starting** 变为 **Running**

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot723.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot723.png)

- 当它运行时，在 **Action** 下选择 **Open**，如下图所示

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot823.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot823.png)

三个必需的文件被复制到 `/home/sagemaker-user/scripts` 目录下：两个 Python 文件（[external-bedrock-agent-api](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-16807/external-bedrock-agent-api.py) 和 [streamlit-app-portfolio-recommender](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-16807/streamlit-app-portfolio-recommender.py)）以及一个 [requirements.txt](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-16807/requirements.txt) 文件，如下图所示。JupyterLab 应用环境位于默认目录下。

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot923.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot923.png)

- 在 **文件** 菜单中，选择 **新建**。在下拉菜单中选择 **终端**，以打开一个新的终端窗口，如下图所示。
[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot1023.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot1023.png)
- 在终端中进入存放所需文件的 scripts 目录，然后输入：  `pip install -r requirements.txt`
- 在终端中输入以下命令：  `python3 external-bedrock-agent-api.py`
- 打开一个新终端，进入 `/home/sagemaker-user/scripts` 目录，然后输入：  `streamlit run streamlit-app-portfolio-recommender.py`
- 从终端的命令执行输出中，记下端口号（8501）以及浏览器中的 studio URL。该 URL 的格式为： `https://{domainid}.studio.{region}-1.sagemaker.aws/jupyterlab/default/lab/tree/scripts`
- 要访问 Streamlit 应用，请修改 Studio URL，把 default/ lab/tree/scripts 之后的内容替换为 proxy/[PORT NUMBER]/。修改后的 Streamlit UI URL 看起来像这样： `https://{domainid}.studio.{region}.sagemaker.aws/jupyterlab/default/proxy/8501/`
- 为生成你的自定义投资组合建议，选择所有合适的输入。勾选相应的复选框，选择你希望通过电子邮件通知还是通过应用界面直接收到建议。然后选择 **Submit**。请提供本次演练前面已验证过的同一个电子邮件地址。

示例输出和电子邮件响应如下面的演示截图所示。
[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/04/TrimFullv4.gif)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/04/TrimFullv4.gif)

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot1223.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot1223.png)

## 清理

完成后，请删除不再需要的资源，以避免持续产生费用。请按以下步骤操作：

- 进入 SageMaker AI JupyterLab 环境，[停止 Amazon SageMaker Studio 应用或正在运行的实例](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated-running-stop.html)
- 通过删除 CloudFormation 堆栈来删除所创建的资源。

下面的截图演示如何查看并停止 SageMaker AI JupyterLab 环境中正在运行的实例。更多信息请参阅[从 CloudFormation 控制台删除堆栈](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html)。

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot1323.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot1323.png)

## Amazon Bedrock Agents return of control 的注意事项

在实施 return of control 时，请考虑以下方面：

- **return of control 的性能考量** – 在实施 return of control 时，开发者应专注于优化操作执行时间和响应处理。每个操作都应设计为在合理的时间范围内完成，以保持对话流畅。考虑为频繁访问的数据实现缓存机制，并在各个 return of control 周期之间高效地管理状态。应用应设计为能够有效处理并发的用户会话，同时保持响应性。
- **return of control 的限制** – 操作必须使用清晰的输入和输出 schema 定义。每个操作都应是原子的，并聚焦于特定任务，以保持简单和可靠。要考虑请求和响应的负载大小，因为可能存在大小限制。操作按顺序执行，系统需要在整个交互周期中维护对话上下文。
- **安全建议** – 安全实施需要为所有操作提供恰当的身份验证和授权机制，在定义权限时遵循最小权限原则。输入参数必须在处理前经过验证，并具备完善的错误处理。应实施速率限制和请求验证以防止滥用，敏感数据的处理必须符合安全要求，并包含用于审计记录的恰当日志机制。此外，实施输入过滤以防止 prompt injection 攻击，配置响应过滤器以保护敏感信息，并对输入和输出都设置内容扫描。部署基于正则表达式的响应过滤，以帮助防止个人可识别信息（PII）泄露，并建立内容审核过滤器来拦截不当内容。
- **监控与可观测性** – 为所有操作的执行和响应实施全面的日志记录。监控操作执行时间、成功率和错误率等关键指标。为异常模式或失败设置告警。使用 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) 监控系统健康和性能。考虑实施追踪，以跟踪请求在系统不同组件之间的流转。定期审查指标和日志有助于发现潜在问题和优化机会。

## 结论

在本文中，我们演示了 Amazon Bedrock Agents 如何简化 agent 创建，并利用 return of control 能力精简微服务之间复杂交互的编排。通过抽象掉基础设施管理并与你的应用无缝集成，Amazon Bedrock Agents 让开发者能够轻松构建有韧性、可扩展的应用。随着组织采用微服务架构和分布式系统，像 Amazon Bedrock Agents 这样的工具在加速创新和推动数字化转型方面发挥着关键作用。

## 资源

要获取最新、最具体的信息，请参阅：

- [Amazon Bedrock 文档](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [AWS Well-Architected Framework 最佳实践](https://docs.aws.amazon.com/wellarchitected/latest/framework/appendix.html)
- [AWS 安全最佳实践](https://aws.amazon.com/architecture/security-identity-compliance/)
- [AWS 可观测性最佳实践](https://docs.aws.amazon.com/wellarchitected/latest/management-and-governance-guide/observability.html)

### 关于作者

**
[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/28/vh2-1.jpg)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/vh2.jpg)Vishwanatha Handadi** 是 Global Financial Services 垂直业务部门的高级解决方案架构师，在 Amazon Web Services（AWS）工作已超过 2 年，在 IT 行业拥有超过 22 年经验，主要从事数据与分析工作。在 AWS，他通过把复杂挑战转化为面向技术受众和业务受众的可执行路线图，推动客户完成云转型之旅。他常驻印度班加罗尔。

**
[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/28/ab-1-1.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/ab-1.png)Mohammed Asadulla Baig** 是 Amazon Web Services（AWS）企业支持部门的高级技术客户经理。Asad 帮助客户设计可扩展、有韧性且安全的解决方案。凭借对创新的敏锐洞察和对客户成功的热情，Asad 已成为行业内的思想领袖，帮助企业在云转型之旅中自信而从容地前行。
