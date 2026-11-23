---
vendor: aws_bedrock
title: 让 AI agent 借助 Amazon Bedrock AgentCore payments 为 AWS Marketplace 的 x402 商品付款
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/enable-ai-agents-to-pay-for-aws-marketplace-x402-products-with-amazon-bedrock-agentcore-payments
date: 2026-11-19
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: agent
status: translated
body_sha: 4ed67e10fc55
---

# 让 AI agent 借助 Amazon Bedrock AgentCore payments 为 AWS Marketplace 的 x402 商品付款

Amazon Bedrock AgentCore payments 在 2026 年 8 月[正式可用](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-payments-is-now-generally-available-enabling-agents-to-transact-safely-and-autonomously-at-scale/)时，agent 已经能够通过 x402、MPP 这类开放协议，自主为付费 API、MCP server 和网页内容付款，既有支付限额，也有完整的可观测性。今天我们把这层自主能力延伸到 [AWS Marketplace](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-process-payment.html#payments-process-payment-aws-billing)：agent 可以自己发现并购买支持 x402 的软件、API、数据和内容，以美元记在 agent 开发者的 AWS 账单上，不再需要稳定币钱包或 API key。

图 1：AgentCore payments 概览，其中展示了用于在 AWS Marketplace 上购买的新 AWS Billing 集成

开发者还可以通过 [AgentCore Gateway 中的 AWS Marketplace connector](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-connector-aws-marketplace.html) 配置并自动化发现流程。既有 guardrails 继续生效，开发者可以用 AgentCore policy 设定支出上限和已批准的卖家，支付会话上限由 AgentCore payments 强制执行，agent 无法超支。交易可在 [AWS CloudTrail](https://aws.amazon.com/cloudtrail/) 和 [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/) 中审计。由于 agent 的购买在买卖双方都走 AWS 账户，agentic 采购满足企业对安全性和可审计性的要求。

AWS Marketplace 上的 x402 目录在扩大，可信且经过验证的卖家越来越多。面向 agentic commerce 的实时搜索提供商 Tavily 就是其中之一：

> Agentic commerce 不只是让 agent 有能力付款，更是让企业有信心放它们去付款。
>         正是这份信心，推动 Tavily 与 AWS 团队一起设计 Agentic Commerce。把安全的、由 x402 驱动的交易带进 AWS Marketplace，并把 agent 与可信、经过 KYC 验证的提供商连起来，AWS 正在为生产规模的自主商业打地基。
>         这就是企业级 agentic commerce 该有的样子。

— Rotem Weiss，Tavily 创始人兼 CEO

## 今天发布的内容

今天的发布把 AWS Billing 加为 AgentCore payments 的一种支付选项。agent 现在可以按请求、以美元向支持 x402 的 AWS Marketplace 卖家付款，结算在它的 AWS 账单上。

AWS Marketplace 卖家返回 402 Payment Required 时，响应里带有一份签名的购买报价。有了 AWS Billing，agent 可以把卖家的 x402 响应转给 AgentCore payments。AgentCore payments 先校验会话预算，然后返回 payment token。agent 带上 payment token 重发请求，拿到成功响应。AWS 把费用记到配置了 Payment Manager 的那个 AWS 账户上，费用会出现在该账户的 AWS 账单里。

要打通 AWS Marketplace 购买，开发者需要创建一个带 AWS Billing connector 的 Payment Manager。connector 只要求你配置一个[服务关联角色](https://docs.aws.amazon.com/marketplace/latest/buyerguide/buyer-service-linked-role-agentic-commerce.html)来访问 AWS Marketplace。之后针对每个任务，开发者可以创建一个带支出上限的支付会话，并把会话 ID 交给 agent。

agent 第一次向某个卖家采购，会为该 AWS 账户与这个卖家建立一份协议，此后 AWS Marketplace 自动把后续购买记在协议下。每件商品随后会作为一条 AWS Marketplace 明细项出现。如果贵组织用了 [Private Marketplace](https://aws.amazon.com/marketplace/features/privatemarketplace)，agent 只能买它允许的商品。

此外，为了方便发现新卖家，我们推出了新的 [AgentCore Gateway 中的 AWS Marketplace connector](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-connector-aws-marketplace.html)。这个可选集成帮 agent 找到商品及其端点。发布之初，AWS Billing 支持 x402 的 *exact* 方案，即卖家为每个请求报一个固定价格。

本文会走一遍一个研究 agent：它自己发现一个工具，通过 AWS Billing 为单次请求付费，最后给出带来源的回答，而事先什么都不用配。我们还提供了配套的 GitHub 示例，你可以在自己的 AWS 账户里评估这套配置。

## 示例演练

假设一位金融分析师问 agent：本周在 agentic payments 方面有什么发布。模型没有在本周的新闻上训练过，于是 agent 去找搜索工具。它通过 AgentCore Gateway 搜索 AWS Marketplace，读取 AWS Marketplace 卖家 Tavily 的商品页，并请求该商品页的 x402 端点。

agent 调用该端点，收到带价格明细的 x402 负载，然后把它转给 AgentCore payments。AgentCore payments 拿它和会话剩余预算核对，返回一个 payment token。校验通过后，agent 带上 token 重发请求，拿到搜索结果。它的回答带有来源，并说明买了什么、花了多少。

在这条工作流里，agent 可以运用自己的推理来决定用哪个 AWS Marketplace 工具。

### 工作原理

图 2：示例方案使用 Strands agent 的端到端流程

**1. 发现。** agent 依次调用三个只读的 gateway 工具：搜索商品页、获取商品页、列出其履约选项。搜索商品页的工具只返回接受 x402 的端点。最后一次调用返回卖家的端点 URL 以及它接受的支付协议。

**2. 获取报价。** agent 调用该端点时不附带支付。卖家返回 HTTP 402，并在 `PAYMENT-REQUIRED` 请求头里放一份签名报价。AWS Marketplace 用卖家注册的密钥校验签名，也就是说价格被改过的报价会被拒掉。

**3. 支付。** agent 把报价传给 `ProcessPayment` API，支付类型为 `AWS_BILLING_X402`。会话里还有预算，AgentCore payments 就签发一个 payment token；预算不够，调用就失败，开发者不会被扣费。

**4. 兑换。** agent 重发请求，这次把 token 放在 `PAYMENT-SIGNATURE` 请求头里，卖家返回内容。payment token 有效期大约五分钟，所以 agent 一趟就把第 2 到第 4 步走完。

**5. 结算。** 开发者第一次向某个卖家采购时，AWS Marketplace 会与该卖家创建协议。之后它把每笔费用计量到开发者的 AWS 账单上。结算异步进行，每月出现在其 AWS 账单中。

### 前提条件

要创建 AWS Billing connector，开发者的 AWS 账户必须拥有 AWS Marketplace 服务关联角色 [AWSServiceRoleForMarketplaceAgenticCommerce](https://docs.aws.amazon.com/marketplace/latest/buyerguide/buyer-service-linked-role-agentic-commerce.html)。AWS Marketplace 用这个角色把 agent 产生的 AWS Marketplace 购买记到开发者的 AWS 账户上。更多细节见[文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-prerequisites.html#payments-prereq-aws-billing)。

### 动手实践

`agentcore-samples` 仓库里的[开源 GitHub 示例](https://github.com/awslabs/agentcore-samples/tree/main/01-features/08-agents-that-transact/02-use-cases/pay-for-x402-aws-marketplace)完整演示了这项新功能。它能帮你为 AWS Marketplace 配置 AgentCore payments、接上 Tavily、运行 agent，并检查交易。更多细节见[文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-process-payment.html#payments-process-payment-aws-billing)。

#### 步骤 1：配置 AgentCore payments

`setup_aws_billing.py` 创建一个带 AWS Billing connector 的 payment manager，以及 [AWS Marketplace 服务关联角色](https://docs.aws.amazon.com/marketplace/latest/buyerguide/buyer-service-linked-role-agentic-commerce.html)和三个独立的 AWS Identity and Access Management (IAM) 角色。session 角色能设预算但不能付款，agent 角色能付款但不能创建支付会话，所以 agent 没有办法自己提高预算。

```
python setup_aws_billing.py --region us-east-1
```

#### 步骤 2：接入 Tavily

`setup_gateway.py` 创建一个带 AWS Marketplace connector 的 AgentCore Gateway，并给 agent 角色授予使用它的相应权限。Gateway 的角色只限于三个只读的 AWS Marketplace 操作。如果你想跳过这一步，也可以在环境变量里把 `SELLER_URL` 设为卖家的端点，agent 就只向这个 URL 付款，不走 AgentCore Gateway 的发现流程。

```
python setup_gateway.py --region us-east-1
```

#### 步骤 3：运行 agent

脚本以 session 角色创建支付会话，再以 agent 角色运行 agent。默认会话预算为 $0.05，单次请求上限为 $0.02。

```
python strands_marketplace_agent.py "What was announced about agentic payments this week? Cite sources."
```

agent 会搜索、查看商品页、拿到端点，然后付一次款。在这次针对 $0.01 卖家的测试运行中，它比较了两个商品页才下单：

```
Tool calls: search_marketplace -> get_remaining_budget -> search_marketplace -> search_marketplace -> get_listing -> get_listing -> get_seller_endpoints -> get_seller_endpoints -> fetch_paid_api -> get_remaining_budget
Payments this run: 1, total $0.01
```

#### 步骤 4：检查交易

运行结束后，示例会打印这笔支付，包含金额、AWS Marketplace 产品 ID 和 `processPaymentId`。AWS Marketplace 计量费用是异步的，所以 Tavily 这条明细项要等一会儿才出现在你的账单上。agent 的购买也会出现在 AWS CloudTrail 和 AWS Cost Explorer 中。

#### 步骤 5：清理

运行 `cleanup.py` 删除资源。务必确认删除成功，以免产生额外的资源费用。

## 结论

[AgentCore payments 与 AWS Marketplace](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-process-payment.html#payments-process-payment-aws-billing) 为能够交易的 agent 提供了基础设施。本文这个研究 agent 从「我需要实时网页搜索」开始，自己找到答案的出处，通过工具发现付费的高级内容，并为最终结算在开发者 AWS 账单上的请求付款。

借助 AgentCore payments，开发者可以用 x402 这类开放协议来构建，从而接入一个不断扩大的目录：里面都是可信、经过验证的 AWS Marketplace 卖家。agent 因此更自主，开发者的控制也更多。治理是内建的：用 AgentCore policy 设定按会话的支出上限和已批准卖家名单，IAM 身份让一切可以在 AWS CloudTrail 和 AWS Cost Explorer 中审计。agent 为任务挑选合适的工具，开发者沿用他们本来就信任的计费、预算和控制。

## 资源

- [AgentCore payments 文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-process-payment.html#payments-process-payment-aws-billing)。
- [GitHub 示例](https://github.com/awslabs/agentcore-samples/tree/main/01-features/08-agents-that-transact/02-use-cases/pay-for-x402-aws-marketplace)。
- [AWS Marketplace 卖家文档](https://docs.aws.amazon.com/marketplace/latest/userguide/agentic-commerce-products.html)。
- [AWS Marketplace 中支持 x402 的产品](https://aws.amazon.com/marketplace/solutions/ai-agents-and-tools?ams%23interactive-card-vertical%23pattern-data-843993407.filters=((id:GLOBAL%23local-tags-aws-marketplace-agentic-ai-x402-support.and,value:(x402-support))))。
- [AWS Marketplace 发布博客](https://aws.amazon.com/blogs/awsmarketplace/aws-marketplace-helps-humans-and-agents-buy-deploy-and-transact/)。

## 关于作者
