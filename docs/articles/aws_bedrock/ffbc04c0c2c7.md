---
vendor: aws_bedrock
title: Exploring the zero operator access design of Mantle
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/exploring-the-zero-operator-access-design-of-mantle
date: 2025-12-23
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 433d143ce9e7
---

# 探索 Mantle 的零操作员访问设计

在 Amazon，我们的文化建立在坦诚、透明地讨论成长机会之上，这使我们能够专注于投入与创新，不断提升为客户交付价值的能力标准。本月早些时候，我们有机会分享了一个体现这一过程如何在 Mantle 中运作的实例——Mantle 是我们为 [Amazon Bedrock](https://aws.amazon.com/bedrock) 打造的新一代推理引擎。随着生成式 AI 推理与微调工作负载持续演进，我们也需要以更优化的方式演进为客户提供推理服务的方式，Mantle 的开发正源于此。

当我们着手重新构想新一代推理引擎的架构时，把安全标准提得更高成为我们的首要任务。AWS 与客户一样，对安全与数据隐私保持着毫不动摇的关注。这一点从我们业务创立之初就是核心，在 Amazon Bedrock 最早的时期更是格外受重视。我们从一开始就明白，生成式 AI 推理工作负载为客户提供了前所未有的机会，去释放其数据中蕴含的潜在价值；但伴随这一机会而来的是，当客户构建处理其最敏感数据、并与其最关键系统交互的生成式 AI 系统时，我们必须确保安全、隐私与合规方面的最高标准。

作为基线，Amazon Bedrock 按照与整个 AWS 相同的运营安全标准设计。AWS 一贯在运营中采用最小权限模型：每位 AWS 操作员只能访问完成其指定任务所需的最小系统集合，且权限仅限于需要该权限的时段。对存储或处理客户数据或元数据的系统的任何访问都会被记录、进行异常监控并接受审计。AWS 防范任何会禁用或绕过这些控制措施的行为。此外，在 Amazon Bedrock 上，你的数据绝不会被用于训练任何模型。模型提供方没有任何机制访问客户数据，因为推理只在 Amazon Bedrock 拥有的账户内完成，而模型提供方无权访问该账户。这种强健的安全态势一直是帮助客户为其敏感数据释放生成式 AI 应用潜力的关键使能因素。

借助 Mantle，我们把标准提得更高。遵循 [AWS Nitro System](https://docs.aws.amazon.com/whitepapers/latest/security-design-of-aws-nitro-system/no-aws-operator-access.html) 的做法，我们从底层开始就把 Mantle 设计为零操作员访问（zero operator access，ZOA），也就是刻意排除 AWS 操作员访问客户数据的任何技术手段。取而代之的是，系统与服务通过自动化以及可保护客户数据的安全 API 来管理。在 Mantle 中，任何 AWS 操作员都没有机制登录底层计算系统，也无法访问任何客户数据，例如推理 prompt 或补全结果。诸如 Secure Shell（SSH）、[AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html) 和串行控制台这类交互式通信工具，均未安装在 Mantle 的任何位置。此外，所有推理软件更新在部署到服务之前都必须经过签名与验证，确保只有经批准的代码在 Mantle 上运行。

Mantle 使用近期发布的 [EC2 instance attestation 能力](https://aws.amazon.com/about-aws/whats-new/2025/09/aws-announces-ec2-instance-attestation/)，为处理客户数据配置一个加固、受限且不可变的计算环境。Mantle 中负责处理模型权重、对客户 prompt 执行推理操作的服务，进一步由 [Nitro Trusted Platform Module（NitroTPM）](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/nitrotpm.html) 提供的密码学签名证明度量所支撑，具备高保障性。

当客户调用 Mantle 端点（例如 `bedrock-mantle.[regions].api.aws`），比如 Amazon Bedrock 上为 [Responses API](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-mantle.html) 提供服务的那些端点时，客户数据（prompt）通过 TLS 离开客户环境，并一路加密直至 Mantle 服务，而该服务以 ZOA 方式运行。在整个流程中以及在 Mantle 内部，任何操作员——无论来自 AWS、客户还是模型提供方——都无法访问客户数据。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/23/ML-20238-image-1.jpeg)

## 展望未来

Mantle 的 ZOA 设计体现了 AWS 对客户数据安全与隐私的长期承诺。正是这种专注，使 AWS 各团队能够投入资源，进一步提升安全标准。与此同时，我们已将 Amazon 内部使用的基础机密计算能力（例如 NitroTPM Attestation）开放给所有客户，供其在 [Amazon Elastic Compute Cloud（Amazon EC2）](https://aws.amazon.com/ec2) 上使用。

我们不会止步于此；我们承诺持续投入，增强你的数据安全，并就我们如何做到这一点为你提供更多透明度与保障。

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/04/08/aliguori.jpeg)**Anthony Liguori** 是 Amazon Bedrock 的 AWS 副总裁兼杰出工程师（Distinguished Engineer），也是 Mantle 的首席工程师。
