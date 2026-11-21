---
vendor: aws_bedrock
title: 让 AI agent 借助 Amazon Bedrock AgentCore payments 为 AWS Marketplace 的 x402 商品付款
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/enable-ai-agents-to-pay-for-aws-marketplace-x402-products-with-amazon-bedrock-agentcore-payments
date: 2026-11-19
lang: zh
captured: 2026-11-20
extractor: readability-v1
translator: llm
status: translated
body_sha: 9b4b9b3ef38c
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# 让 AI agent 通过 Amazon Bedrock AgentCore payments 为 AWS Marketplace 的 x402 产品付款

当 Amazon Bedrock AgentCore payments 在 2026 年 8 月[正式可用](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-payments-is-now-generally-available-enabling-agents-to-transact-safely-and-autonomously-at-scale/)时，agent 已经可以通过 x402、MPP 等开放协议自主为付费 API、MCP server 和网页内容付款，并带有支付限额和完整的可观测性。今天，我们把这种自主能力扩展到 [AWS Marketplace](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-process-payment.html#payments-process-payment-aws-billing)，让 agent 能够发现并购买支持 x402 的软件、API、数据和内容，并以美元计入 agent 开发者的 AWS 账单，无需 stablecoin 钱包或 API key。

图 1：AgentCore payments 概览，展示了用于在 AWS Marketplace 上购买的新 AWS Billing 集成

开发者还可以通过 [AgentCore Gateway 中的 AWS Marketplace connector](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-connector-aws-marketplace.html) 配置并自动化发现流程。现有护栏机制继续沿用，开发者可以使用 AgentCore policy 设置支出限额和已批准的卖家，支付会话上限由 AgentCore payments 强制执行，因此 agent 无法超支。交易可在 [AWS CloudTrail](https://aws.amazon.com/cloudtrail/) 和 [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/) 中审计。由于 agent 的购买在买卖双方都通过 AWS 账户进行，agentic purchasing 满足企业对安全性和可审计性的预期。

AWS Marketplace 上的 x402 目录正在扩大，可信且经过验证的卖家阵容不断增长。面向 agentic commerce 的实时搜索提供商 Tavily 就是其中之一：

> Agentic commerce 不仅仅是让 agent 具备支付能力，更是让企业有信心允许它们这样做。
>         正是这一信念推动 Tavily 与 AWS 团队在 Agentic Commerce 的设计上展开合作。通过将安全的、由 x402 驱动的交易引入 AWS Marketplace，并将 agent 与可信、经过 KYC 验证的提供商连接起来，AWS 正在为生产规模的自主商业奠定基础。
>         这就是企业级 agentic commerce 的样子。

— Rotem Weiss，Tavily 创始人兼 CEO

## 今天发布的内容

今天的发布将 AWS Billing 添加为 AgentCore payments 中的一种支付选项。Agent 现在可以按请求以美元向支持 x402 的 AWS Marketplace 卖家付款，并结算到其 AWS 账单上。

当 AWS Marketplace 卖家返回 402 Payment Required 时，其响应中包含一份签名的购买报价。使用 AWS Billing 时，agent 可以将卖家的 x402 响应转发给 AgentCore payments。AgentCore payments 检查会话预算，然后返回 payment token。Agent 携带 payment token 重试向卖家的请求，并获得成功响应。AWS 将费用计入设置 Payment Manager 的 AWS 账户，该费用会出现在该账户的 AWS 账单上。

要设置 AWS Marketplace 购买，开发者需要创建一个带有 AWS Billing connector 的 Payment Manager。该 connector 仅要求你设置一个[服务关联角色](https://docs.aws.amazon.com/marketplace/latest/buyerguide/buyer-service-linked-role-agentic-commerce.html)以访问 AWS Marketplace。然后，对于每个任务，开发者可以创建一个带有支出限额的 payment session，并将 session ID 交给 agent。

Agent 首次向某个卖家购买时，会为该 AWS 账户与该卖家创建一份协议，AWS Marketplace 会自动依据该协议跟踪后续购买。每个产品随后会显示为一条 AWS Marketplace 明细项。如果你的组织使用 [Private Marketplace](https://aws.amazon.com/marketplace/features/privatemarketplace)，agent 只能购买其允许的产品。

此外，为了发现新卖家，我们推出了新的 [AgentCore Gateway 中的 AWS Marketplace connector](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-connector-aws-marketplace.html)。这一可选集成帮助 agent 查找产品及其 endpoint。发布之初，AWS Billing 支持 x402 的 *exact* 方案，即卖家为每个请求报出固定价格。

在本文中，我们将演示一个研究 agent：它发现一个工具，通过 AWS Billing 为单次请求付费，并给出带来源的回答，而事先无需任何设置。我们还提供了配套的 GitHub 示例，你可以在自己的 AWS 账户中评估该设置。

## 示例演示

假设一位金融分析师问 agent，本周关于 agentic payments 公布了什么。模型没有在本周新闻上训练过，因此 agent 会寻找一个搜索工具。通过 AgentCore Gateway，它搜索 AWS Marketplace，读取 AWS Marketplace 卖家 Tavily 的 listing，并请求该 listing 的 x402 endpoint。

Agent 调用该 endpoint，收到带有价格详情的 x402 负载。Agent 随后将 x402 负载转发给 AgentCore payments。AgentCore payments 根据会话剩余预算进行检查，并返回 payment token。检查通过后，agent 携带 token 再次发送请求，获得搜索结果。它的回答包含来源，并说明它购买了什么、花费多少。

在此工作流中，agent 可以运用其推理来决定使用哪个 AWS Marketplace 工具。

### 工作原理

图 2：使用 Strands agent 的示例解决方案端到端流程

**1. 发现。** Agent 依次调用三个只读 gateway 工具：搜索 listing、获取 listing、列出其履约选项。搜索 listing 工具只返回接受 x402 的 endpoint。最后一次调用返回卖家的 endpoint URL 及其接受的支付协议。

**2. 获取报价。** Agent 在不附带支付的情况下调用该 endpoint。卖家返回 HTTP 402，并在 `PAYMENT-REQUIRED` header 中放入一份签名报价。AWS Marketplace 根据卖家注册的密钥校验签名，这意味着价格被篡改的报价会被拒绝。

**3. 支付。** Agent 将报价传给 `ProcessPayment` API，支付类型为 `AWS_BILLING_X402`。如果会话中仍有预算，AgentCore payments 会签发 payment token。如果没有，调用失败，开发者不会被收费。

**4. 兑换。** Agent 再次发送请求，这次在 `PAYMENT-SIGNATURE` header 中携带 token，卖家返回内容。Payment token 有效期约为五分钟，因此 agent 在一次流程中完成步骤 2 到 4。

**5. 结算。** 开发者首次向某个卖家购买时，AWS Marketplace 会与该卖家创建协议。之后，它会将每笔费用计量到开发者的 AWS 账单上。结算异步进行，并每月出现在其 AWS 账单中。

### 前提条件

要创建 AWS Billing connector，开发者的 AWS 账户必须拥有 AWS Marketplace 服务关联角色 [AWSServiceRoleForMarketplaceAgenticCommerce](https://docs.aws.amazon.com/marketplace/latest/buyerguide/buyer-service-linked-role-agentic-commerce.html)。AWS Marketplace 使用该角色将 agent 进行的 AWS Marketplace 购买计入其 AWS 账户。详情请参阅[文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-prerequisites.html#payments-prereq-aws-billing)。

### 动手实践

`agentcore-samples` 仓库中的[开源 GitHub 示例](https://github.com/awslabs/agentcore-samples/tree/main/01-features/08-agents-that-transact/02-use-cases/pay-for-x402-aws-marketplace)演示了新功能。它可以帮助你为 AWS Marketplace 配置 AgentCore payments、连接 Tavily、运行 agent 并检查交易。详情请参阅[文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-process-payment.html#payments-process-payment-aws-billing)。

#### 步骤 1：配置 AgentCore payments

`setup_aws_billing.py` 创建一个带有 AWS Billing connector 的 payment manager，以及 [AWS Marketplace 服务关联角色](https://docs.aws.amazon.com/marketplace/latest/buyerguide/buyer-service-linked-role-agentic-commerce.html)和三个独立的 AWS Identity and Access Management (IAM) 角色。session 角色可以设置预算但不能支付。agent 角色可以支付但不能创建 session，因此 agent 无法自行提高预算。

```
python setup_aws_billing.py --region us-east-1
```

#### 步骤 2：连接 Tavily

`setup_gateway.py` 创建一个带有 AWS Marketplace connector 的 AgentCore Gateway，并为 agent 角色授予使用它的相应权限。Gateway 的角色仅限于三个只读的 AWS Marketplace 操作。如果你选择跳过此步骤，可以在环境变量中将 `SELLER_URL` 设置为卖家的 endpoint，agent 将只向该 URL 付款，而不使用 AgentCore Gateway 发现。

```
python setup_gateway.py --region us-east-1
```

#### 步骤 3：运行 agent

该脚本以 session 角色创建 payment session，然后以 agent 角色运行 agent。默认会话预算为 $0.05，单次请求上限为 $0.02。

```
python strands_marketplace_agent.py "What was announced about agentic payments this week? Cite sources."
```

Agent 进行搜索、查看 listing、获取 endpoint，并支付一次。在针对 $0.01 卖家的这次测试运行中，它比较了两个 listing 后才购买：

```
Tool calls: search_marketplace -> get_remaining_budget -> search_marketplace -> search_marketplace -> get_listing -> get_listing -> get_seller_endpoints -> get_seller_endpoints -> fetch_paid_api -> get_remaining_budget
Payments this run: 1, total $0.01
```

#### 步骤 4：检查交易

运行结束后，示例会打印支付信息，包括金额、AWS Marketplace 产品 ID 和 `processPaymentId`。AWS Marketplace 异步计量费用，因此 Tavily 明细项需要稍等片刻才会出现在你的账单上。Agent 的购买也会显示在 AWS CloudTrail 和 AWS Cost Explorer 中。

#### 步骤 5：清理

运行 `cleanup.py` 删除资源。请务必验证删除，以避免产生额外的资源费用。

## 结论

[AgentCore payments 和 AWS Marketplace](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-process-payment.html#payments-process-payment-aws-billing) 为能够进行交易的 agent 提供了基础设施。本文中的研究 agent 从“我需要实时网页搜索”出发，自行获取答案来源，通过工具发现付费高级内容，并为结算到开发者 AWS 账单的请求付费。

借助 AgentCore payments，开发者可以使用 x402 等开放协议进行构建，这为他们打开了不断增长的可信、经过验证的 AWS Marketplace 卖家目录。这赋予 agent 更多自主性，也赋予开发者更多控制权。治理内置于其中：使用 AgentCore policy 的按会话支出上限和已批准卖家列表，以及使其可在 AWS CloudTrail 和 AWS Cost Explorer 中审计的 IAM 身份。Agent 为任务选择合适的工具，开发者可以保留他们已经信任的相同计费、预算和控制。

## 资源

- [AgentCore payments 文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-process-payment.html#payments-process-payment-aws-billing)。
- [GitHub 示例](https://github.com/awslabs/agentcore-samples/tree/main/01-features/08-agents-that-transact/02-use-cases/pay-for-x402-aws-marketplace)。
- [AWS Marketplace 卖家文档](https://docs.aws.amazon.com/marketplace/latest/userguide/agentic-commerce-products.html)。
- [AWS Marketplace 中支持 x402 的产品](https://aws.amazon.com/marketplace/solutions/ai-agents-and-tools?ams%23interactive-card-vertical%23pattern-data-843993407.filters=((id:GLOBAL%23local-tags-aws-marketplace-agentic-ai-x402-support.and,value:(x402-support))))。
- [AWS Marketplace 发布博客文章](https://aws.amazon.com/blogs/awsmarketplace/aws-marketplace-helps-humans-and-agents-buy-deploy-and-transact/)。

## 关于作者
