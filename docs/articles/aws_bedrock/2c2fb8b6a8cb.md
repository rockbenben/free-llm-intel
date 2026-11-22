---
vendor: aws_bedrock
title: Accelerating software delivery with agentic QA automation using Amazon Nova Act
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/accelerating-software-delivery-with-agentic-qa-automation-using-amazon-nova-act
date: 2026-03-31
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: c6b85041f442
---

# 使用 Amazon Nova Act 实现 agentic QA 自动化，加速软件交付

质量保证（QA）自动化对现代软件交付至关重要。它能在进入生产前拦截回归问题、规模化验证用户旅程，并让功能发布更有把握。但传统的 QA 自动化方案脆弱，且要求专门的编程知识，反而拖慢了软件交付。

自动化框架依赖实现细节来在应用中导航，包括 UI 选择器、元素标识符和结构引用。当开发者重构 UI 代码或设计师调整布局时，即使功能仍然完好，测试也会失败。这种维护负担源于团队协作方式的错位：产品经理用业务语言定义验收标准，开发团队实现功能，然后由开发者编写自动化代码。这让测试与真正理解用户需求的人之间产生了距离，迫使软件团队把精力花在维护测试上，而不是交付功能。

Amazon Nova Act 正是为解决这些挑战而生——这是一项 AWS 服务，用于构建可靠的 agent 集群，以规模化方式自动化生产环境的 UI 工作流。它自有的 computer use 模型以与用户相同的方式与应用交互：通过自然语言与视觉理解，而不是检查代码。这消除了依赖代码的选择器与技术门槛，使 agentic QA 自动化得以实现，从而降低测试维护开销、让测试管理更普惠，并加快软件交付周期。

本文演示如何通过 QA Studio 实现 agentic QA 自动化——这是用 Amazon Nova Act 构建的参考解决方案。你将看到如何用自然语言定义测试并让其自动适应 UI 变化，了解可在规模化下可靠执行测试的无服务器架构，并获得针对你的 AWS 环境的分步部署指引。

### **QA Studio 概览**

QA Studio 提供用于管理 QA 自动化的 Web 前端、API 与 CLI，构建在无服务器 AWS 基础设施之上，并由 Amazon Nova Act 提供 agentic UI 自动化能力。你可以按需运行测试、自动排程，或将其作为持续集成与持续交付（CI/CD）pipeline 的一部分来触发。

图 1 – Nova QA Studio 测试用例执行演示

### **自然语言测试管理**

Amazon Nova Act 会把自然语言指令转换为浏览器交互，包括导航、数据抽取与断言。团队可以借此用描述产品需求时的同一套语言来定义测试，形成统一的规范，使需求变更可直接流入测试定义。

团队可以用 QA Studio，以自然语言定义测试步骤来创建并执行测试。用户可以通过由 [Amazon Bedrock AgentCore Browser,](https://aws.amazon.com/bedrock/agentcore/) 驱动的实时浏览器预览来创建测试套件，可以借助 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 从用户旅程描述生成测试，也可以通过 [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) 安全录入数据，还可使用其他能力。Amazon Nova Act 把这些测试定义转换为浏览器动作，QA Studio 则提供界面，因此测试作者无需编写或维护代码即可创建和管理测试。

图 2 – 使用 User Journey Wizard 创建测试

### **可自适应的视觉导航**

Amazon Nova Act 的 computer use 模型依据应用的外观与上下文来导航，而非依赖与代码绑定的选择器。当设计师调整按钮位置或开发者重构组件结构时，测试会自动适应。这消除了传统框架中产生维护开销的脆弱性，使测试作者可以专注于应用应当做什么，而不是如何在代码中定位元素。QA Studio 提供界面供用户执行和监控测试，利用 Amazon Nova Act 的视觉导航完成 UI 自动化、数据抽取与状态校验。团队可以借此专注于交付功能，而不是维护测试基础设施。

图 3 – QA Studio 中的测试与等效的传统测试自动化代码对比

### **端到端测试可见性**

Amazon Nova Act 提供轨迹日志（trajectory log），记录其在每一步的视觉推理与决策过程，清楚展示 agent 看到了什么、以及为何采取特定动作。这种透明度把调试从解析技术栈追踪，转变为通过自然语言描述与视觉上下文理解测试行为。

QA Studio 在整个测试生命周期中呈现这些洞察。在测试创建阶段，用户可通过实时浏览器预览各步骤。测试执行时，团队会收到实时状态更新，并可跨测试套件监控进度。测试完成后，QA Studio 提供测试录制、结果以及带截图的 Nova Act 轨迹日志，使团队无需调试代码级错误即可定位问题。

## **技术架构**

QA Studio 使用以下 AWS 服务：

- [**Amazon Nova Act**](https://aws.amazon.com/nova/act/) – agentic UI 自动化
- [**Amazon CloudFront**](https://aws.amazon.com/cloudfront/) 与 [**Amazon Simple Storage Service（Amazon S3）**](https://aws.amazon.com/s3/) – 使用 AWS Cloudscape Design System 构建的 React 前端交付
- [**Amazon API Gateway**](https://aws.amazon.com/api-gateway/) – API 端点与请求路由
- [**AWS Lambda**](https://aws.amazon.com/pm/lambda/) – 后端 API 与应用逻辑
- [**Amazon Cognito**](https://aws.amazon.com/cognito/) – 用户与机器对机器（machine-to-machine）身份验证
- [**Amazon DynamoDB**](https://aws.amazon.com/dynamodb/) – 使用单表设计（single-table design）存储测试定义、执行历史与结果
- [**Amazon Elastic Container Service（Amazon ECS）**](https://aws.amazon.com/ecs/) 与 [**AWS Fargate**](https://aws.amazon.com/fargate/) – 使用 [Nova Act SDK](https://github.com/aws/nova-act) 的容器化测试执行工作负载
- [**Amazon Bedrock**](https://aws.amazon.com/bedrock/) – 为测试用例生成提供基础模型访问，并提供用于托管远程浏览器的 [**AgentCore Browser**](https://aws.amazon.com/bedrock/agentcore/)
- [**Amazon Simple Queue Service（Amazon SQS）**](https://aws.amazon.com/sqs/) – 通过基于队列的处理实现可靠的测试执行
- [**Amazon S3**](https://aws.amazon.com/s3/) – 存储测试录制、截图、日志与追踪
- [**Amazon EventBridge**](https://aws.amazon.com/eventbridge/) – 自动化测试运行排程

图 4 – QA Studio AWS 架构

这种无服务器架构在所有 AWS 服务上提供自动扩缩容，并按使用量计费，具备基于消费的经济性。你仍然掌控安全策略、合规要求与定制需求。

## **开始使用 QA Studio**

QA Studio 以 [GitHub 仓库](https://github.com/aws-samples/sample-qa-studio)的形式提供，你可以使用 [AWS Cloud Development Kit（AWS CDK）](https://aws.amazon.com/cdk/) 将其部署到自己的 AWS 账户。这样你对测试基础设施、安全策略与合规要求拥有完全控制——所有测试数据、录制与日志都留在你的安全边界之内。你可以按组织要求配置 VPC 设置与访问控制。

在你的 AWS 账户中部署 QA Studio 的步骤如下：

- 克隆 [GitHub 仓库](https://github.com/aws-samples/sample-qa-studio)。
- 按照 README 指南使用 AWS CDK 部署基础设施。
- 配置通知与 CI/CD 集成（可选）。

完整部署说明请参阅 [QA Studio GitHub 仓库](https://github.com/aws-samples/sample-qa-studio)。该仓库包含 AWS CDK 模板以及在你自己的 AWS 环境中部署 QA Studio 所需的全部组件、指南与文档。

## **清理资源**

如果你出于评估目的部署了 QA Studio，请记得删除相关 AWS 资源，以免产生后续费用。完整删除说明请参阅该 GitHub 仓库的 README。

对在你的环境中实施 QA Studio 有疑问？欢迎留言——我们很想了解你遇到的测试挑战，以及你打算如何用 AI 驱动的测试来加速软件交付。

## **结语**

本文展示了基于 Amazon Nova Act 的 agentic QA 自动化如何通过自然语言测试管理与视觉导航来加速软件交付。QA Studio 是一个参考解决方案，它清除了 QA 自动化的技术门槛，并通过视觉理解消除脆弱性，使团队能够专注于交付功能，而不是维护测试基础设施。

在[下一篇](https://aws.amazon.com/blogs/machine-learning/accelerating-software-delivery-with-agentic-qa-automation-using-amazon-nova-act-part-2/)中，我们将在此基础上进一步演示 QA Studio 如何通过组织与并行执行测试的测试套件，以及把 agentic 测试带入自动化 CI/CD pipeline 的命令行界面，来应对批量回归测试与 pipeline 集成。

## 关于作者
