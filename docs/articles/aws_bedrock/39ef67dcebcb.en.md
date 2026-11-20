---
vendor: aws_bedrock
title: Enable AI agents to pay for AWS Marketplace x402 products with Amazon Bedrock AgentCore payments
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/enable-ai-agents-to-pay-for-aws-marketplace-x402-products-with-amazon-bedrock-agentcore-payments
date: 2026-11-19
lang: en
captured: 2026-11-20
extractor: readability-v1
status: ok
body_sha: 98c1cdf00ec9
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# Enable AI agents to pay for AWS Marketplace x402 products with Amazon Bedrock AgentCore payments

When Amazon Bedrock AgentCore payments became [generally available](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-payments-is-now-generally-available-enabling-agents-to-transact-safely-and-autonomously-at-scale/) in August 2026, agents could autonomously pay for paid APIs, MCP servers, and web content over open protocols like x402 and MPP with payment limits and full observability. Today we extend that autonomy to [AWS Marketplace](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-process-payment.html#payments-process-payment-aws-billing), so agents can discover and buy x402-enabled software, APIs, data, and content, and pay in USD on the agent developer’s AWS bill, removing the need for stablecoin wallets or API keys.

Figure 1: Overview of AgentCore payments showing the new AWS Billing integration for purchasing on AWS Marketplace

Developers can also configure and automate discovery through the [AWS Marketplace connector in AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-connector-aws-marketplace.html). Existing guardrails carry over, developers can set spending limits and approved sellers using AgentCore policy, and the payment session cap is enforced by AgentCore payments, so an agent is unable to overspend. Transactions are auditable in [AWS CloudTrail](https://aws.amazon.com/cloudtrail/) and [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/). Because agent purchases run through AWS accounts on both sides, agentic purchasing meets the security and auditability enterprises expect.

The x402 catalog on AWS Marketplace is expanding with a growing roster of trusted, verified sellers. Tavily, a live search provider for agentic commerce, is one of them:

> Agentic commerce isn’t just about giving agents the ability to pay. It’s about giving enterprises the confidence to let them.
>         That conviction is driving Tavily’s collaboration with the AWS team on the design of Agentic Commerce. By bringing secure, x402 powered transactions to AWS Marketplace and connecting agents with trusted, KYC verified providers, AWS is laying the foundation for autonomous commerce at production scale.
>         This is what enterprise ready agentic commerce looks like.

— Rotem Weiss, Founder & CEO, Tavily

## What’s launching today

Today’s launch adds AWS Billing as a payment option in AgentCore payments. An agent can now pay x402-enabled AWS Marketplace sellers per request, in USD, settling on their AWS bill.

When an AWS Marketplace seller responds with 402 Payment Required, its response includes a signed quote for the purchase. With AWS Billing, the agent can forward the seller’s x402 response to AgentCore payments. AgentCore payments checks session budgets, then returns a payment token. The agent retries the request to the seller with the payment token included and receives a successful response. AWS bills the charge to the AWS account where Payment Manager is set up, and the charge appears on that account’s AWS bill.

To set up AWS Marketplace purchasing, the developer creates a Payment Manager with an AWS Billing connector. The connector only requires you to set up a [service-linked role](https://docs.aws.amazon.com/marketplace/latest/buyerguide/buyer-service-linked-role-agentic-commerce.html) to access AWS Marketplace. Then, for each task, developers can create a payment session with a spending limit and give the agent the session ID.

An agent’s first purchase from a seller creates an agreement for the AWS account with that seller, and AWS Marketplace automatically tracks later purchases against it. Each product will then show up as an AWS Marketplace line item. If your organization uses [Private Marketplace](https://aws.amazon.com/marketplace/features/privatemarketplace), agents can only buy the products it allows.

In addition, to discover new sellers, we are launching a new [AWS Marketplace connector in AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-connector-aws-marketplace.html). This optional integration helps agents find products and their endpoints. At launch, AWS Billing supports the x402 *exact* scheme, where the seller quotes a fixed price for each request.

In this post, we walk through a research agent that discovers a tool, pays for a single request through AWS Billing, and answers with sources, with nothing set up in advance. We also provide an accompanying GitHub sample that you can use to evaluate the setup in your own AWS account.

## Sample walkthrough

Suppose a financial analyst asks the agent what was announced about agentic payments this week. The model wasn’t trained on this week’s news, so the agent looks for a search tool. Through AgentCore Gateway, it searches AWS Marketplace, reads the listing from Tavily, an AWS Marketplace seller, and requests the listing’s x402 endpoints.

The agent calls the endpoint and receives an x402 payload with price details. The agent then forwards the x402 payload to AgentCore payments. AgentCore payments checks it against the remaining session budget and returns a payment token. Once these checks are passed, the agent sends the request again with the token attached, and gets the search results. Its answer includes sources and states what it bought and what it cost.

In this workflow, agents can apply their reasoning to decide which AWS Marketplace tool to use.

### How it works

Figure 2: End-to-end flow of the sample solution using a Strands agent

**1. Discover.** The agent calls three read-only gateway tools in order: search listings, get a listing, and list its fulfillment options. Search listings tool only returns endpoints that accept x402. The last call returns the seller’s endpoint URL and the payment protocols it accepts.

**2. Get a quote.** The agent calls the endpoint with no payment attached. The seller answers with HTTP 402 and puts a signed quote in the `PAYMENT-REQUIRED` header. AWS Marketplace checks the signature against the seller’s registered key, which means a quote with an altered price gets rejected.

**3. Pay.** The agent passes the quote to the `ProcessPayment` API with the payment type `AWS_BILLING_X402`. If budget remains in the session, AgentCore payments issues a payment token. If not, the call fails and the developer is not charged.

**4. Redeem.** The agent sends the request again, this time with the token in the `PAYMENT-SIGNATURE` header, and the seller returns the content. Payment tokens are valid for about five minutes, so the agent completes steps 2 through 4 in a single pass.

**5. Settle.** On the developer’s first purchase from a seller, AWS Marketplace creates the agreement with that seller. After that it meters each charge to their AWS bill. Settlement runs asynchronously and shows up in their AWS bill monthly.

### Prerequisites

To create an AWS Billing connector, developers’ AWS accounts must have the AWS Marketplace service-linked role [AWSServiceRoleForMarketplaceAgenticCommerce](https://docs.aws.amazon.com/marketplace/latest/buyerguide/buyer-service-linked-role-agentic-commerce.html). AWS Marketplace uses this role to bill AWS Marketplace purchases that their agents make to their AWS account. Refer to the [documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-prerequisites.html#payments-prereq-aws-billing) for more details.

### Hands-on

The [open-source GitHub sample](https://github.com/awslabs/agentcore-samples/tree/main/01-features/08-agents-that-transact/02-use-cases/pay-for-x402-aws-marketplace) in the `agentcore-samples` repository runs through a demo of the new functionality. It can help you configure AgentCore payments for AWS Marketplace, connect Tavily, run the agent, and inspect the transaction. You can refer to the [documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-process-payment.html#payments-process-payment-aws-billing) for more details.

#### Step 1: Configure AgentCore payments

`setup_aws_billing.py` creates a payment manager with an AWS Billing connector, plus the [AWS Marketplace service-linked role](https://docs.aws.amazon.com/marketplace/latest/buyerguide/buyer-service-linked-role-agentic-commerce.html) and three separate AWS Identity and Access Management (IAM) roles. The session role can set budgets but can’t pay. Meanwhile the agent role can pay but can’t create sessions, so the agent has no way to raise its own budget.

```
python setup_aws_billing.py --region us-east-1
```

#### Step 2: Connect Tavily

`setup_gateway.py` creates an AgentCore Gateway with the AWS Marketplace connector and gives the agent role the appropriate permissions to use it. The gateway’s role is limited to three read-only AWS Marketplace actions. If you choose to skip this step, you can instead set `SELLER_URL` in the environment variables to the seller’s endpoint, and the agent will pay that URL only rather than using AgentCore Gateway discovery.

```
python setup_gateway.py --region us-east-1
```

#### Step 3: Run the agent

The script creates a payment session as the session role and then runs the agent as the agent role. By default the session budget is $0.05 and the per-request cap is $0.02.

```
python strands_marketplace_agent.py "What was announced about agentic payments this week? Cite sources."
```

The agent searches, looks at listings, gets an endpoint, and pays once. In this test run against a $0.01 seller, it compared two listings before buying:

```
Tool calls: search_marketplace -> get_remaining_budget -> search_marketplace -> search_marketplace -> get_listing -> get_listing -> get_seller_endpoints -> get_seller_endpoints -> fetch_paid_api -> get_remaining_budget
Payments this run: 1, total $0.01
```

#### Step 4: Inspect the transaction

When the run finishes, the sample will print the payment with its amount, AWS Marketplace product ID, and `processPaymentId`. The AWS Marketplace meters charges asynchronously, so the Tavily line item takes a moment to appear on your bill. Agent purchases will also show up in AWS CloudTrail and AWS Cost Explorer.

#### Step 5: Clean up

Run `cleanup.py` to delete resources. Make sure to validate deletion to avoid incurring additional resource charges.

## Conclusion

[AgentCore payments and AWS Marketplace](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-process-payment.html#payments-process-payment-aws-billing) provide the infrastructure for agents that can transact. The research agent in this post goes from “I need live web search” to sourcing an answer on its own, discovering premium paid content through tools, and paying for requests that settle on the developer’s AWS bill.

With AgentCore payments, developers can build with open protocols like x402, which opens them to a growing catalog of trusted, verified AWS Marketplace sellers. This gives agents more autonomy and developers more control. Governance is built in, with per-session spending caps and an approved seller list using AgentCore policy, and IAM identities that make it auditable in AWS CloudTrail and AWS Cost Explorer. The agent chooses the right tool for the task, and developers can keep the same billing, budgets, and controls they already trust.

## Resources

- [AgentCore payments documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-process-payment.html#payments-process-payment-aws-billing).
- [GitHub sample](https://github.com/awslabs/agentcore-samples/tree/main/01-features/08-agents-that-transact/02-use-cases/pay-for-x402-aws-marketplace).
- [AWS Marketplace seller documentation](https://docs.aws.amazon.com/marketplace/latest/userguide/agentic-commerce-products.html).
- [x402-enabled products in AWS Marketplace](https://aws.amazon.com/marketplace/solutions/ai-agents-and-tools?ams%23interactive-card-vertical%23pattern-data-843993407.filters=((id:GLOBAL%23local-tags-aws-marketplace-agentic-ai-x402-support.and,value:(x402-support)))).
- [AWS Marketplace launch blog post](https://aws.amazon.com/blogs/awsmarketplace/aws-marketplace-helps-humans-and-agents-buy-deploy-and-transact/).

## About the authors
