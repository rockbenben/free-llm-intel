---
vendor: aws_bedrock
title: Building age-responsive, context-aware AI with Amazon Bedrock Guardrails
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/building-age-responsive-context-aware-ai-with-amazon-bedrock-guardrails
date: 2026-03-26
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: dc39c852a2ee
---

# 使用 Amazon Bedrock Guardrails 构建响应年龄、感知上下文的 AI

在向不同用户群体部署生成式 AI 应用时，你可能会面临一个影响用户安全与应用可靠性的重大挑战：验证每一条 AI 响应对接收它的具体用户而言是否恰当、准确且安全。适合成年人的内容对儿童可能不合适或令人困惑，而为初学者设计的解释对领域专家可能不够充分。随着 AI 在各行业加速采用，让响应用户的年龄、角色和领域知识相匹配，已成为生产部署的必要条件。

你可能会尝试通过 prompt engineering 或应用级逻辑来解决这一问题。然而，这些方法可能带来重大挑战。基于 prompt 的安全控制可能被操纵技术绕过，诱使模型忽略安全指令。随着个性化需求增长，应用代码会变得复杂而脆弱，不同 AI 应用之间的治理也会变得不一致。此外，当 AI 系统与弱势用户交互，或在教育和医疗健康等敏感领域运行时，不安全内容、幻觉信息和不当响应的风险会被放大。缺乏集中、可执行的安全策略会造成运营效率低下和合规风险。

为应对这些挑战，我们使用 Amazon Bedrock Guardrails 及其他契合现代 AI 安全与合规需求的 AWS 服务，实现了一套全 serverless、guardrail 优先的解决方案。该架构提供三个主要组件：基于用户上下文的动态 guardrail 选择、通过 Amazon Bedrock Guardrails 实现的集中式策略执行，以及面向认证访问的更安全 API。你可以利用这一 serverless 设计，在无需复杂应用代码的情况下，更高效、更安全、大规模地交付个性化且安全的 AI 响应。

在本文中，我们将带你了解如何使用 AWS 上的 serverless 架构实现一套全自动、上下文感知的 AI 解决方案。我们将演示如何设计和部署一个可扩展的系统，它能够：

- 根据用户年龄、角色和行业智能调整 AI 响应
- 在 inference 时执行安全策略，帮助防止通过 prompt 操纵进行绕过
- 为不同用户群体（儿童、青少年、医疗健康专业人员、患者和普通成年人）提供五个专用 guardrail
- 通过集中治理和极少的人工干预提升运营效率
- 随用户增长和不断变化的安全要求而扩展

该解决方案帮助希望部署负责任 AI 系统的组织，满足针对弱势群体的合规要求，并在不影响性能或治理的前提下，帮助在多样化用户群体中保持适当且可信的 AI 响应。

## 解决方案概览

该解决方案使用 [Amazon Bedrock](https://aws.amazon.com/bedrock/?trk=1f887566-8561-4bf2-a30b-f383e290b094&sc_channel=ps&trk=1f887566-8561-4bf2-a30b-f383e290b094&sc_channel=ps&ef_id=Cj0KCQiAgvPKBhCxARIsAOlK_EoHffXPKugWVi002yM9QhXSt0Tn-QXr-aOIv5bEWeh4iOKdBQEPxI4aAuv6EALw_wcB:G:s&s_kwcid=AL!4422!3!785447157285!e!!g!!amazon%20bedrock&gad_campaignid=23296345364&gbraid=0AAAAADjHtp-lHu0Utl2iyCFsqTXDeg4Rs&gclid=Cj0KCQiAgvPKBhCxARIsAOlK_EoHffXPKugWVi002yM9QhXSt0Tn-QXr-aOIv5bEWeh4iOKdBQEPxI4aAuv6EALw_wcB)、[Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/)、[AWS Lambda](https://aws.amazon.com/pm/lambda/?trk=065f9330-e033-4770-bfd7-4af000a338f2&sc_channel=ps&trk=065f9330-e033-4770-bfd7-4af000a338f2&sc_channel=ps&ef_id=Cj0KCQiAgvPKBhCxARIsAOlK_Eprltaz6fmPuOFb0tjL5n6rFQ_wCIfpwLpm0drVoNirkfwyoYhXbUkaAnD0EALw_wcB:G:s&s_kwcid=AL!4422!3!785483253781!e!!g!!aws%20lambda&gad_campaignid=23300619076&gbraid=0AAAAADjHtp9frKVYj8AuDncepeIQPiJCC&gclid=Cj0KCQiAgvPKBhCxARIsAOlK_Eprltaz6fmPuOFb0tjL5n6rFQ_wCIfpwLpm0drVoNirkfwyoYhXbUkaAnD0EALw_wcB) 和 [Amazon API Gateway](https://aws.amazon.com/api-gateway/) 作为核心服务，用于智能响应生成、集中式策略执行和安全访问。[Amazon Cognito](https://aws.amazon.com/pm/cognito/?trk=abd73416-070e-4f2a-98af-e5b3ed53bd66&sc_channel=ps&trk=abd73416-070e-4f2a-98af-e5b3ed53bd66&sc_channel=ps&ef_id=Cj0KCQiAgvPKBhCxARIsAOlK_EoIq_uDIiDPt2RouEEbvIXrCFZLSPWMq3tgJ2d8hx7a-2YdFLTdYkoaAtyfEALw_wcB:G:s&s_kwcid=AL!4422!3!785574083501!e!!g!!amazon%20cognito&gad_campaignid=23300619811&gbraid=0AAAAADjHtp8bigGR8lqEjA7Xx7mFhBDv4&gclid=Cj0KCQiAgvPKBhCxARIsAOlK_EoIq_uDIiDPt2RouEEbvIXrCFZLSPWMq3tgJ2d8hx7a-2YdFLTdYkoaAtyfEALw_wcB)、[Amazon DynamoDB](https://aws.amazon.com/dynamodb/)、[AWS WAF](https://aws.amazon.com/waf/) 和 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) 等支撑组件则帮助实现用户认证、画像管理、安全性和全面的日志记录。

这一方法的独特之处在于动态 guardrail 选择：Amazon Bedrock 和 Bedrock Guardrails 会根据认证后的用户上下文（年龄、角色、行业）自动调整，帮助在 inference 时执行适当的安全策略。这种 guardrail 优先的方法与基于 prompt 的安全措施协同工作，提供分层保护，并提供五个专用 guardrail：Child Protection（[符合《儿童在线隐私保护法》或 COPPA](https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa)）、Teen Educational、Healthcare Professional、Healthcare Patient 和 Adult General。这些 guardrail 提供了一个权威的策略执行层，决定 AI 模型可以说什么，并且独立于应用逻辑运行。

该解决方案利用 serverless 的可扩展性，执行安全策略，并根据用户上下文调整响应——非常适合服务于多样化用户群体的企业 AI 部署。该解决方案可使用 Terraform 部署，实现基础设施和应用组件的可重复、端到端自动化。

如图 1 所示，Web UI 作为本地演示服务器（localhost:8080）运行，用于测试和演示。对于生产部署，组织可以将 API 端点集成到现有 Web 应用中，或者将界面部署到 AWS 服务上，例如将 [Amazon Simple Storage Service（Amazon S3）](https://aws.amazon.com/s3/?trk=3d8e0834-4a13-43d9-9142-a95c86f6929f&sc_channel=ps&trk=3d8e0834-4a13-43d9-9142-a95c86f6929f&sc_channel=ps&ef_id=Cj0KCQiA7fbLBhDJARIsAOAqhsf57t0CYmy7179BGoLov6bJSPAxpxIpAI5LNvxBjS1yJwvYWMkKU0saAognEALw_wcB:G:s&s_kwcid=AL!4422!3!785447140458!e!!g!!amazon%20s3!23291342325!188768692203&gad_campaignid=23291342325&gbraid=0AAAAADjHtp8_8G23aU2Sus8P57XjprZjZ&gclid=Cj0KCQiA7fbLBhDJARIsAOAqhsf57t0CYmy7179BGoLov6bJSPAxpxIpAI5LNvxBjS1yJwvYWMkKU0saAognEALw_wcB) 与 [Amazon CloudFront](https://aws.amazon.com/cloudfront/) 或 [AWS Amplify](https://aws.amazon.com/amplify/) 结合使用。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/19/ML-195931.png)

*图 1：Serverless *age-responsive-context-aware-ai-bedrock 架构

## 多上下文 AI 安全策略

现在你已了解架构组件，接下来看看解决方案如何根据不同的用户上下文动态调整响应。下图（图 2：使用 Amazon Bedrock Guardrails 实现响应年龄、感知上下文的 AI 工作流）展示了如何处理不同的用户画像：

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/19/ML-195932.png)
* 图 2：*age-responsive-context-aware-ai-bedrock 工作流

## 解决方案的工作原理

解决方案工作流包含以下步骤（参见图 1：使用 Amazon Bedrock Guardrails 实现响应年龄、感知上下文的 AI 解决方案架构）：

- 用户请求与 Web 界面  Web 界面：用户访问本地演示 Web 界面（运行在 localhost:8080 上，仅用于演示） 用户输入：用户通过 Web 界面输入查询 用户选择：用户选择自己的画像（Child、Teen、Adult、Healthcare 角色） 请求准备：Web 界面准备带有用户上下文的认证请求
- 用户认证  JSON Web Token（JWT）令牌生成：Amazon Cognito 用户池对用户进行认证并生成 JWT 令牌 用户身份：JWT 令牌包含用户 ID 和认证 claim 令牌验证：安全令牌随 API 请求一同传递
- AWS WAF 安全层  限流：AWS WAF 对每个 IP 施加每分钟 2,000 次请求的限制（可根据需要在 [Code repository](https://github.com/aws-samples/sample-age-responsive-context-aware-ai-bedrock-guardrails) 的 terraform/variables.tf 中调整） Open Web Application Security Project（OWASP）防护：阻止常见 Web 威胁和恶意请求 请求过滤：验证请求格式并阻断可疑流量
- API Gateway 处理  JWT 授权：API Gateway 验证来自 Cognito 的 JWT 令牌 请求路由：将认证后的请求路由到 AWS Lambda 函数 跨域资源共享（Cross-Origin Resource Sharing，CORS）：管理来自 Web 演示的跨域请求
- Lambda 函数执行  输入清理：Lambda 对用户数据进行清理和校验 用户上下文检索：查询 DynamoDB 以获取用户画像（年龄、角色、行业） 上下文分析：分析用户人口统计信息，确定合适的 guardrail
- DynamoDB 用户画像查询  画像查询：Lambda 使用 `user_id` 查询 **ResponsiveAI-Users** 表 上下文数据：返回年龄、角色、行业和设备信息 审计准备：为 **ResponsiveAI-Audit** 表准备审计日志条目
- 动态 guardrail 选择  上下文评估：AWS Lambda 评估用户的年龄、角色和行业 guardrail 映射：从五个专用 Amazon Bedrock Guardrails 中自动选择：  Child（年龄 < 13）→ Child Protection Guardrail（符合 COPPA） Teen（年龄 13–17）→ Teen Educational Guardrail（适龄内容） Healthcare Professional → Healthcare Professional Guardrail（启用临床内容） Healthcare Patient → Healthcare Patient Guardrail（屏蔽医疗建议） Default/Adult → Adult General Guardrail（标准保护）  安全性：每个请求都必须经过 guardrail——不可能绕过

有关每个 guardrail 配置的完整概览，包括内容过滤器、主题限制、PII 处理和自定义过滤器，请参阅 [Code repository](https://github.com/aws-samples/sample-age-responsive-context-aware-ai-bedrock-guardrails) 中的 [Guardrail Configuration Details](https://github.com/aws-samples/sample-age-responsive-context-aware-ai-bedrock-guardrails/tree/main#:~:text=Guardrail%20Configuration%20Details)。

- 带 guardrail 保护的 Bedrock AI 处理  模型调用：Lambda 调用 Amazon Bedrock 中的基础模型 guardrail 应用：所选 guardrail 同时过滤输入和输出 内容安全：应用自定义策略、主题限制和个人可识别信息（personally identifiable information，PII）检测 响应生成：AI 生成符合上下文、经过安全过滤的响应
- 响应处理与审计日志  内容批准：安全的响应连同 guardrail 元数据一同交付 内容拦截：不恰当内容会触发上下文感知的安全提示 CloudWatch 日志：记录交互以用于合规追踪 DynamoDB 审计：guardrail 交互记录存储在 Responsive AI-Audit 表中
- 向用户交付响应  API Gateway 响应：Lambda 通过 Amazon API Gateway 返回处理后的响应 直接响应：系统直接向用户交付响应（AWS WAF 只过滤传入请求） Web 演示展示：用户收到符合上下文、受到保护的响应 用户体验：同一查询会根据用户上下文生成不同响应

## 响应自适应示例

**1.** 对于问题“What is DNA?”，系统会根据用户上下文生成不同的响应：

**Student（13 岁）：**

“DNA 就像一本食谱，告诉你的身体如何成长、你会长成什么样！它由四个特殊的字母（A、T、G、C）组成，这些字母为你身体的一切编写指令。”

**Healthcare Professional（35 岁）：**

“DNA 由核苷酸序列组成，通过碱基互补配对编码遗传信息。其双螺旋结构包含编码区（外显子）和控制基因表达与蛋白质合成的调控序列。”

**General Adult（28 岁）：**

“DNA 是一种分子，包含用于生物体发育和功能的遗传指令。它呈双螺旋结构，决定遗传性状。”

**2.** 以下示例展示了同一道数学问题如何获得适龄的响应：

请参阅以下截图，了解对问题“How do I solve quadratic equations?”的响应。这能更清楚地说明同一问题如何根据用户上下文得到不同响应。

**Teen Student（13 岁）：**简单、循序渐进的解释，配有基础示例和适合中学水平的友好语言（参见图 3）

**For Math Teacher（39 岁）**：全面的教学方法，包括多种解法、教学策略和高等数学概念（参见图 4）

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/19/ML-195933.png)
* 图 3：Teen *Student 响应，提供循序渐进的指导

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/19/ML-195934.png)
* 图 4：*Educator 响应，采用全面的教学方法

## 前提条件

在部署该解决方案之前，请确保已安装并配置以下内容：

- **AWS 账户 **
- **所需 **[**AWS 权限**](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_permissions-required.html)：你的 AWS 用户或角色需要以下权限：  Lambda（创建函数） Amazon Bedrock（模型调用与 guardrail 管理） Cognito（用户池与身份提供方） AWS WAF（web ACL 与规则） DynamoDB（表操作） API Gateway（REST API 管理） CloudWatch
- [**Terraform**](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)** 已安装**：部署解决方案基础设施所必需

## 实施

- 克隆 GitHub 仓库：  打开终端或命令提示符。导航到想要克隆仓库的目录。运行以下命令将仓库克隆到本地系统。

```
git clone https://github.com/aws-samples/sample-age-responsive-context-aware-ai-bedrock-guardrails.git
```

- 使用 Terraform 部署基础设施：  打开终端或命令提示符并导航到代码仓库。使用 deploy.sh 部署资源和端到端解决方案。

```
$ cd sample-age-responsive-context-aware-ai-bedrock-guardrails
$ ./deploy.sh
```

## 测试解决方案

该解决方案包含一个基于 Web 的演示，可用于即时测试，并具备高级 API 测试能力。

对于生产级企业部署，可使用 AWS Amplify、Amazon S3 和 Amazon CloudFront，或 Amazon Elastic Container Service（Amazon ECS）和 Amazon Elastic Kubernetes Service（Amazon EKS）等容器服务来托管 Web 界面。有关 Amazon Bedrock Guardrails 的详细测试场景、API 示例和验证流程，请参阅克隆仓库中的 [TESTING_GUIDE.md](https://github.com/aws-samples/sample-age-responsive-context-aware-ai-bedrock-guardrails/blob/main/TESTING_GUIDE.md) 文件。

** 交互式 Web 演示**：

- 要启动交互式 Web 演示，请运行：

```
$ cd web-demo
$ ./start_demo.sh
```

- 打开浏览器并访问 [http://localhost:8080](http://localhost:8080/)
- 你可以使用演示界面来：  选择不同的用户画像（Child、Teen、Adult、Healthcare 角色） 提交查询并观察上下文感知的响应 实时查看 guardrail 的执行情况 监控基于用户上下文的响应自适应

** API 测试：**

- 对于编程式测试，生成一个 JWT 令牌：

```
$ cd utils
$ python3 generate_jwt.py student-123
```

- 测试 API 端点：

```
$ curl -X POST "$(cd ../terraform && terraform output -raw api_url)" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{"query": "What is DNA?"}'
```

## 亲手试一试

通过以下场景探索该解决方案的能力：

- **适龄响应**：对不同年龄组提交同一查询
- **基于角色的自适应**：比较专业受众与普通受众的响应
- **内容安全**：验证不同用户类型下不恰当内容的拦截情况
- **Guardrail 执行**：测试绕过安全控制的尝试
- **性能**：测量不同负载条件下的响应时间

## 已部署资源与成本估算

运行该解决方案的成本取决于使用模式和规模。以下是中等使用场景（每天 1,000 次 API 请求）的预估月度成本明细：

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/19/ML-195935.png)

**预估总计**：根据用量和模型选择，每月 $73-320

**注意**：实际成本因请求量、模型选择、数据传输和区域定价而异。可使用 [AWS Pricing Calculator](https://calculator.aws/#/) 进行定制估算。

## 成本优化注意事项

- **成本标记**：在资源上实施 AWS 成本分摊标签（例如 `Project:AgeResponsiveAI`、`Environment:Production`、`Team:AI-Platform`），以便按部门、项目或成本中心追踪支出
- **多账户部署**：对于跨多个 AWS 账户的企业部署，可考虑使用 AWS Organizations 的合并账单以及 AWS Cost Explorer，以获得集中的成本可见性
- **预留容量**：对于可预测的工作负载，可考虑 Amazon Bedrock Provisioned Throughput 以降低 inference 成本
- **DynamoDB 优化**：对波动较大的工作负载使用按需定价，对可预测的模式使用带自动扩缩的预置容量
- **Lambda 优化**：合理调整内存分配，并使用 AWS Lambda Power Tuning 帮助改善性价比
- **CloudWatch 日志保留**：配置恰当的日志保留期限，在合规需求与存储成本之间取得平衡

## 清理

为避免持续产生费用，请在不再需要时删除本次演练中创建的 AWS 资源。要移除已部署的 AWS 资源和本地文件，请运行：

```
$ cd sample-age-responsive-context-aware-ai-bedrock-guardrails
$ ./ cleanup.sh
```

## 主要收益与成果

该解决方案展示了一种 guardrail 优先的方法来构建上下文感知的 AI 应用。主要收益包括：

- **上下文感知的安全**：不同用户群体可通过专用 guardrail 获得保护，而无需部署单独的模型或应用
- **集中治理**：Amazon Bedrock Guardrails 帮助在基础设施层执行安全策略、主题限制和幻觉控制，而非依赖 prompt 逻辑
- **托管内容过滤**：Amazon Bedrock Guardrails 提供内建内容过滤器，可过滤仇恨言论、侮辱、性内容、暴力、不当行为和 prompt 注入攻击，无需自行实现
- **智能个性化**：根据用户上下文调整内容的复杂度与适当性，为儿童提供适龄解释，为医疗健康专业人员提供临床细节
- **降低绕过风险**：策略在 inference 时应用，无法被用户输入覆盖
- **运营灵活性**：新增用户群体或策略更新可通过更新 guardrail 实现，而无需修改应用代码
- **企业级就绪**：Amazon Bedrock Guardrails 提供版本控制、审计日志和合规对齐支持，职责分离清晰，便于长期维护

## 结论

在本文中，我们演示了如何实现一套全 serverless、guardrail 优先的解决方案，以交付响应年龄、感知上下文的 AI 响应。我们展示了前述 AWS 服务如何协同工作，根据上下文动态选择专用 guardrail、执行安全策略并交付个性化响应。我们使用 Terraform 部署了该架构，使其可重复且达到生产就绪。通过动态 guardrail 选择和集中式策略执行，该解决方案将 AI 响应定制到每个用户群体——从面向儿童的符合 COPPA 保护，到面向医疗健康专业人员的临床内容——同时保持企业级的安全性与可扩展性。服务于多样化用户群体的组织，可以降低绕过风险、实现集中治理，并在更新策略时无需修改应用代码，从而获得运营灵活性。

要开始使用，请克隆仓库并按照部署说明操作。通过交互式 Web 演示测试该解决方案，查看响应如何根据用户上下文自适应。要了解有关 Amazon Bedrock Guardrails 的更多信息，请访问 [Amazon Bedrock Guardrails 文档](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)。

## 关于作者
