---
vendor: aws_bedrock
title: Migrate to Amazon Bedrock Managed Knowledge Base with your coding agent
original_title: Migrate to Amazon Bedrock Managed Knowledge Base with your coding agent
url: https://aws.amazon.com/blogs/machine-learning/migrate-to-amazon-bedrock-managed-knowledge-base-with-your-coding-agent
date: 2026-11-12
lang: en
captured: 2026-11-13
extractor: readability-v1
status: ok
body_sha: 79285db4795d
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# Migrate to Amazon Bedrock Managed Knowledge Base with your coding agent

With a customer-managed knowledge base on [Amazon Bedrock](https://aws.amazon.com/bedrock/), you provision and scale the vector store, tune the embedding model and index settings, and plan capacity for each new data source. The migration guide in the Agent Toolkit for AWS helps you migrate to [Amazon Bedrock Managed Knowledge Base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-build-managed.html). Managed Knowledge Base takes over that work and adds new retrieval capabilities, and your team keeps control of the content and the application that uses it.

Moving a production knowledge base means your team maps its configuration, creates the replacement, ingests content, updates the application’s retrieval call, and validates retrieval before switching traffic. To help, we added a knowledge base migration guide to the `amazon-bedrock` skill in the [Agent Toolkit for AWS](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/skills.html). The guide gives your coding agent the context to plan the migration with you, starting with read-only discovery and a plan you review line by line. On your approval, the agent creates the new knowledge base and its data sources alongside the original, or writes a migrated infrastructure as code (IaC) template for your pipeline. Ingestion and updating your application’s `Retrieve` calls stay with you, and your agent can walk you through both.

In this post, we explain why we recommend the move and how the migration guide works, review the prerequisites, install the skill, plan a migration, update the application’s retrieval call, and validate retrieval before cutover.

## Why move to Managed Knowledge Base

We recommend Managed Knowledge Base because it balances ease of use, retrieval accuracy, and cost.

### AWS runs the store

With a Managed Knowledge Base, Amazon Bedrock handles ingestion, storage, indexing, and retrieval, and the store scales automatically as your content grows. Hybrid search, which combines keyword and semantic matching, is always on, with no index to configure. The knowledge base includes a managed embedding model, a managed reranker, and a built-in parser for multimodal file types.

You can still bring your own Amazon Bedrock embedding model when you create the knowledge base. On each retrieval request, you choose the managed reranker, an Amazon Bedrock reranking model, or no reranking. The managed reranker requires the managed embedding model.

### Built-in capabilities

Managed Knowledge Base includes capabilities you’d otherwise build yourself:

- **Native connectors** ingest content directly from sources such as Amazon Simple Storage Service (Amazon S3), Microsoft SharePoint, and Atlassian Confluence. For the current list, see [supported connectors](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-create.html#kb-managed-connectors). After the first full sync, later syncs pick up only changes, on demand or on a schedule. The Managed Knowledge Base includes a deletion safeguard to help protect against accidental bulk removal of indexed content.
- [**Access control list (ACL) awareness**](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-acl.html) ingests document permissions with the content, so retrieval returns only what the signed-in user can access. For connectors that support it, such as Microsoft SharePoint and Atlassian Confluence, a real-time check against the source also catches permission changes since the last sync. ACL awareness doesn’t authenticate users, so your application must verify and pass the user’s identity.
- [**Agentic retrieval**](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-agentic-retrieve.html) answers questions that a single search can’t by handling multi-part questions and retrieving iteratively. It can search more than one knowledge base in a single request.
- [**Integration with AgentCore Gateway**](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-gateway-target.html), a capability of Amazon Bedrock AgentCore, exposes your knowledge base as a target. Any client that supports the Model Context Protocol (MCP) can then query the knowledge base, and the gateway handles authentication.
- [**Resource-based policies**](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-cross-account.html) let applications in other AWS accounts use one team’s knowledge base. Scope each policy to the specific roles that call the knowledge base, and grant only the actions they use, such as `bedrock:Retrieve`.

Agentic retrieval, AgentCore Gateway integration, and resource-based policies are not available on customer-managed knowledge bases. For the AWS Regions where managed knowledge bases are available, and the features that AWS GovCloud (US-West) doesn’t support, see [Supported AWS Regions](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-regions.html).

### Higher quotas

As of this writing, higher default quotas change how you can organize content. With 200 data sources per knowledge base, you can group related content in one knowledge base. With 10,000 knowledge bases per account, per Region, each team or product line can use a separate knowledge base.

| **Default quota** | **Customer-managed** | **Managed** |
| --- | --- | --- |
| Knowledge bases per account, per Region | 100 | 10,000 |
| Data sources per knowledge base | 5 | 200 |
| Concurrent ingestion jobs per knowledge base | 1 | 50 |
| Query input characters | 1,000 | 10,000 |

For current values, see [Amazon Bedrock endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html#limits_bedrock) and [Service quotas for managed knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-quotas.html).

### Pay for what you store and retrieve

Cost is one of three things teams weigh when they consider this move, alongside customizability and direct control of the vector store. On a [customer-managed knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-build-managed.html), you choose, provision, scale, and update the vector and text stores, and pay separately for the infrastructure you select. On a Managed Knowledge Base, those stages are part of the service, and storage and retrieval are metered directly.

The pricing models can differ too. With a customer-managed knowledge base, storage and retrieval charges depend on the vector store you choose. Some stores charge for provisioned or minimum capacity, and others, such as Amazon S3 Vectors, a capability of Amazon S3, charge only for what you use. A Managed Knowledge Base is priced on what you store and retrieve, so cost follows real usage. Usage-based pricing can fit enterprise question-answering, policy, and support knowledge bases that run at low utilization. For current rates, see [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/). For the parsers available on a customer-managed knowledge base and how each is billed, see [Parsing options for your data source](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-advanced-parsing.html).

| **Cost driver** | **Customer-managed knowledge base** | **Managed Knowledge Base** |
| --- | --- | --- |
| **Vector storage** | Priced separately by your chosen store. A provisioned retrieval service can have a minimum idle cost even at low volume | Included in the base storage rate of $5 per GB per month |
| **Multimodal document parsing** | Requires Amazon Bedrock Data Automation, billed by page or image, or a foundation model, billed by token. Text-only parsing is free. | Included |
| **Embedding generation** | Billed separately at your embedding model’s rate | Included with the default model. Charges apply only if you choose a custom model |
| **Ingestion, sync, and re-sync compute** | Re-embedding, orchestration code, and indexing compute spikes on each sync add recurring cost | Included, with incremental sync that processes only new and changed content |
| **Connectors** | Building and running custom connectors can add compute cost | Native connectors are included |
| **Standard retrieval** | No Amazon Bedrock charge per query. Your vector store can charge per query, as Amazon S3 Vectors does. | $1 per 1,000 retrieval requests |
| **Reranking** | Amazon Rerank is charged at $1 per 1,000 queries. A custom reranking model is billed at its own rate | Included in the $1 per 1,000 retrieval requests |
| **Agentic retrieval** | You build the agentic workflow on a Bedrock model, which can cost roughly $18 to $24 per 1,000 queries before development and maintenance. Because model usage is billed by token, the price per query varies. | Agentic retrieval costs an additional $4 per 1,000 queries on top of the underlying retrieval calls, including multi-shot retrieval, reranking, and answer generation. Depending on the number of underlying retrieval calls, the total can range from roughly $6 to $9 per 1,000 queries. |

Rates are only part of the total cost of ownership. On a customer-managed knowledge base, your team provisions, scales, and operates each stage as a separate resource. A Managed Knowledge Base consolidates them into one resource, with a default embedding model, foundation model, and reranker, and with per-knowledge-base rate limits by default. You manage the content and the application that uses it, and Amazon Bedrock operates the managed storage, embedding model, foundation model, and reranker.

## Solution overview

A customer-managed knowledge base uses the `VECTOR` type, with a vector store you configure. A Managed Knowledge Base uses the `MANAGED` type. The migration guide directs your agent to create a new `MANAGED` knowledge base alongside the original without modifying or deleting the original during migration. Using the guide’s map, your agent writes a plan that lists which settings remain unchanged, which Managed handles differently, and which application changes you need to make. As Figure 1 shows, the original keeps serving every request while your team ingests content, validates, and cuts over.

![Flow diagram of a coding agent creating a MANAGED knowledge base alongside the original VECTOR knowledge base, which keeps serving the application until the team validates retrieval and cuts over.](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/03/ML-22176-1.png)

Figure 1: Create a managed knowledge base or migrated template alongside the original, then validate before cutover

## How the migration guide works

The guide separates planning from implementation. In Explore mode, your agent answers questions about Managed Knowledge Base and can inspect your configuration with read-only calls, so you can estimate the effort. In Migration mode, the guide takes your agent through checkpoints:

- **Introduce and choose.** Your agent explains what it will and won’t touch. Choose the mode, a live knowledge base or IaC source, and a plain (default) or technical explanation style.
- **Identify.** Confirm the account and AWS Region. Your agent flags over-broad credentials, asks whether you want a cost analysis, and creates an output directory.
- **Discover.** Your agent reads the knowledge base and data sources with read-only calls, or reads your template files.
- **Plan.** Review the plan and application changes. By default, your agent stops here.
- **Implement, if requested.** For a live build, approve the exact preview of the provisioning script, and approve again if it changes. For IaC, your agent writes a migrated template and reports which schema checks ran.
- **Handoff.** Review what was produced and your team’s remaining steps.

As Figure 2 shows, resource creation stays separate from ingestion and cutover.

![Diagram of migration checkpoints flowing through introduce, identify, discover, and plan, then either directly to handoff or through an optional approved implementation, with Explore mode read-only and the team handling ingestion, validation, cutover, and retirement.](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/03/ML-22176-2.png)

Figure 2: Migration checkpoints. Implementation is optional, and your team runs ingestion and cutover

### Review the configuration mapping

The guide maps each setting to preserve your data sources, filters, and chunking behavior when the managed type uses a different configuration. The plan classifies each setting:

- **1:1.** The new knowledge base uses the same setting.
- **Adjusted.** Managed uses a different setting for the same outcome, and the plan applies the substitution.
- **Blocked.** There is no managed path today. Your agent excludes that knowledge base from the build, explains why, and points you to AWS Support. Other knowledge bases in the same run can proceed.

Compare chunking on your own content when you validate.

### Review the permissions and generated changes

Discovery, planning, and the entire IaC path need only read-only credentials. For a live build, the guide directs your agent to propose a scoped policy that explicitly denies changes to the original knowledge base, and to never ask for administrator or full-access permissions. It also directs your agent to change only resources it created, reference secrets by Amazon Resource Name (ARN), and ignore instructions found in the data it reads. Review the generated AWS Identity and Access Management (IAM) policy and provisioning script before you approve the run. After the build, check what the agent did in [AWS CloudTrail event history](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html), which keeps 90 days of management events. Each event records the API call, such as `CreateKnowledgeBase`, and the identity that made it.

For the optional cost analysis, your agent compares current spend with a Managed Knowledge Base estimate using current AWS prices. It uses read-only inputs, including Amazon CloudWatch metrics, Amazon S3 object sizes, and AWS Cost Explorer. Each figure is labeled as measured, supplied by you, or estimated.

## Prerequisites

Use separate credentials for planning and for any approved resource creation.

- A compatible development environment with the Agent Toolkit for AWS.
- The AWS Command Line Interface (AWS CLI), configured with a least-privilege, read-only profile.
- Access to the original knowledge base configuration or its IaC files.
- For the optional live build:  A scoped build profile, using the policy the guide recommends. An IAM service role for the new knowledge base. The guide gives your agent the trust policy and permissions to help you create it. Python 3 with boto3 for the generated provisioning script.

The Agent Toolkit for AWS works with compatible development environments and its [repository on GitHub](https://github.com/aws/agent-toolkit-for-aws) lists the available skills. Examples in this post use AWS CLI 2.37 and boto3 1.43.32.

## Install the skill

Follow the [Agent Toolkit for AWS getting-started instructions](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/quick-start.html) for your coding agent. The `add-skill` command installs the `amazon-bedrock` skill to the coding agents it detects. Add `--agent` to target one, for example `--agent kiro`.

```
aws agent-toolkit add-skill \
    --skill-name amazon-bedrock
```

After installation, your agent loads the migration guide when you describe a migration task. The following prompts are illustrative inputs, not transcripts.

## Plan the migration

Choose the path that matches how you maintain the source.

| **Path** | **What your agent reads** | **What it produces** | **AWS changes** |
| --- | --- | --- | --- |
| Explore | Documentation, and optionally your knowledge base (read-only) | Answers in the conversation | None |
| Live knowledge base | Your knowledge base and data sources (read-only) | A plan, and optionally a new Managed Knowledge Base alongside the original | Only after you approve the exact preview |
| Infrastructure as code | Your AWS CloudFormation template, AWS Cloud Development Kit (AWS CDK) synthesized template, or Terraform configuration | A migrated template in the same format | None. Your pipeline deploys it |

To start in Explore mode, ask a question:

```
What would change if I moved knowledge base <your-kb-name>
in <your-region> to a Managed Knowledge Base? Use Explore mode.
```

When you’re ready, choose the live or IaC path.

### Migrate a live knowledge base

Ask for a plan before authorizing resource creation:

```
Plan a migration of knowledge base <your-kb-name> in <your-region>
to a Managed Knowledge Base. Stop after the plan.
```

Confirm the account and Region, then review the plan’s mappings and application changes. By default, the new knowledge base takes the original’s name with a `-managed` suffix. To build it, confirm the service role exists, switch to the build profile, inspect the provisioning script and its preview, and approve. Your agent runs the script, which creates the knowledge base and data sources, and reports their status.

### Migrate infrastructure as code

Point your agent at the source template or configuration:

```
Review <path-to-source-template> and plan a migration to a
Managed Knowledge Base.
```

Your agent writes the migrated file to the output directory, deploys nothing, and shows you the diff. To keep the diff, ask your agent to save it. Run `terraform init -backend=false` and `terraform validate` before deployment. Your agent can walk you through both commands, but the guide leaves these checks to you because `terraform init` downloads the large AWS provider. Before you apply the deployment plan, check that it keeps the original resources you need for rollback.

### Example conversation

The migration runs as a conversation. Before reading anything, your agent states its scope and asks how to proceed:

```
It never changes or deletes <your-kb-id>, never starts ingestion,
and never cuts your application over; every AWS change is shown to
you and approved first. Nothing has run against your KB yet.

1. Mode: Explore (read-only Q&A about Managed KBs and your KB, no
   plan or build) or Migration (run the phases: identify, discover,
   plan, and optionally build)?
2. Target type, if Migration: migrate the live KB <your-kb-id> (kb
   path, which can build a new Managed KB on approval), or migrate
   the Terraform/CloudFormation that defines it (iac path, which
   only emits a migrated file and provisions nothing)?
3. Explanation style: plain or technical. I'll use plain unless
   you say otherwise.
```

The plan summary shows each mapping, the caller changes, and the decisions you need to make:

```
Phase 3, Plan: written (plan.md)
- Mapping:
  - Vector store becomes auto-provisioned (adjusted, Yes).
  - SEMANTIC chunking is dropped for the managed default
    (adjusted, Partly).
  - Parsing becomes SMART_PARSING (adjusted, Yes).
  - The S3 prefix and metadata sidecars carry over 1:1.
- Changes for callers:
  - New KB id.
  - managedSearchConfiguration replaces vectorSearchConfiguration.
  - overrideSearchType: SEMANTIC can't be sent; search is hybrid.
Your input needed before this can go further.
- D1 embeddingModelType: MANAGED (recommended): keeps the managed
  reranker. CUSTOM Titan v2 1024/FLOAT32: turns off the managed
  reranker.
- D2 aclEnabled: recommend false, since the source has no ACLs.
  On S3 this can't be changed after create.
- Next step: stop with this plan (the default), or opt into Phase 4?
```

For a live build, your agent stops at a preview, and the approval command requires the plan’s hash:

```
If you approve, the command to run is the following. It is MUTATING:
  AWS_PROFILE=build-profile AWS_REGION=<your-region> \
    python3 provision_managed_kb.py --execute \
    --expect-plan-sha256 <plan-sha256>
--execute refuses to start unless it is given --expect-plan-sha256
and the hash matches.
What the preview would create:
- Knowledge base (CreateKnowledgeBase, MANAGED): support-docs-managed
- Data source (CreateDataSource, managed connector, deletion
  protection ENABLED/15): support-docs-s3-managed
The script never calls StartIngestionJob, Retrieve, Update*,
Delete*, or a standalone TagResource.
```

*Example exchanges are lightly edited, with identifiers replaced.*

## Update the application’s retrieval call

Your application uses the same `Retrieve` operation for both types. The managed request targets the new knowledge base ID and replaces `vectorSearchConfiguration` with `managedSearchConfiguration`. Passing `vectorSearchConfiguration` to a managed knowledge base returns a validation error. Managed retrieval always uses hybrid search, so the managed request shape has no `overrideSearchType` field. Metadata filters keep the same syntax, except that managed knowledge bases don’t support the `startsWith` and `stringContains` operators. For the full syntax, see the [Retrieve API reference](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Retrieve.html).

The example assumes both knowledge bases contain the `locale` metadata used by the filter.

```
# Illustrative: the managed request shape was checked with boto3 1.43.32; adapt the IDs and filter to your knowledge base.
import boto3

client = boto3.client("bedrock-agent-runtime")
query = {"text": "How do I return an online order?"}
locale_filter = {"equals": {"key": "locale", "value": "en-US"}}

# Customer-managed (VECTOR) knowledge base.
original_response = client.retrieve(
    knowledgeBaseId="<original-kb-id>",
    retrievalQuery=query,
    retrievalConfiguration={
        "vectorSearchConfiguration": {
            "numberOfResults": 5,
            "overrideSearchType": "SEMANTIC",
            "filter": locale_filter,
        }
    },
)

# Managed target: different ID and search configuration.
managed_response = client.retrieve(
    knowledgeBaseId="<managed-kb-id>",
    retrievalQuery=query,
    retrievalConfiguration={
        "managedSearchConfiguration": {
            "numberOfResults": 5,
            "filter": locale_filter,
        }
    },
)
```

## Validate retrieval and cut over

Evaluate the new knowledge base while the application still uses the original.

- If using IaC, review and deploy the target configuration through your pipeline.
- Sync each data source and review any failures. See [Sync your data](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-sync-ingest.html).
- Grant your application’s runtime IAM role `bedrock:Retrieve` on the new knowledge base ARN, and keep its access to the original knowledge base so you can roll back.
- Run representative queries against both knowledge bases with `Retrieve`, using that role. The two types use different score scales. Managed scores also depend on `rerankingModelType`, which defaults to `MANAGED` with the managed embedding model and to `NONE` with a custom one. Tune thresholds per mode, and hold the mode constant while comparing.
- Test metadata filters and permission-aware retrieval where used, including content the signed-in user shouldn’t receive. On an ACL-enabled data source, requests without `userContext.userId` (the user’s email) return no results.
- After acceptance, deploy the new knowledge base ID and request shape. Keep the original knowledge base, with current content, and application configuration through your rollback period.

For each query, check whether both return the same top document and how much results overlap. A short script can report pass or fail against criteria such as a matching top document on at least 90 percent of queries and no zero-result queries on the managed knowledge base. Tune that threshold for your workload. For other retrieval quality measures, such as context relevance and context coverage, see [Use metrics to understand RAG system performance](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-eval-retrieve.html).

Watch for these differences when you compare results:

- **Normalize source locations before comparison.** A customer-managed knowledge base can return `s3://bucket/key` in `location.s3Location.uri`, and a managed knowledge base can return an `https://` URL. Compare by object key.
- **Compare the top result instead of assuming equal result counts.** The two knowledge base types can return different numbers of results, and `numberOfResults` sets a maximum rather than a guarantee. Compare the top document, and review each query where it changes. For details, see [Configure and customize queries for managed knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-test-config.html).
- **Map renamed system metadata keys.** For example, replace `x-amz-bedrock-kb-data-source-id` with `_data_source_id` in comparison code. Your own metadata attributes keep their names. For details, see [Configure and customize queries for managed knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-test-config.html).

## Clean up

If you complete the migration, retire the original only after the rollback period and a dependency review. Keep the source documents and buckets the managed knowledge base ingests from, and storage that other workloads use. Clean up IaC-managed resources through their owning template.

If you end the evaluation instead, keep the original and delete what you created in this order:

- Delete each managed data source and wait until it’s gone.
- Delete the managed knowledge base and wait until it’s gone.
- If you created the service role only for this evaluation, delete its inline policy, then the role.
- With a customer managed key, check `aws kms list-grants` for grants Amazon Bedrock created, which can remain after the knowledge base is deleted.
- Keep any S3 bucket that another knowledge base still reads.

Deletion protection on a managed data source limits how much a sync can delete, not whether you can delete the data source. Deleting the original knowledge base doesn’t delete its vector store, which continues to incur charges until you remove it. See [Delete an Amazon Bedrock knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-delete.html).

## Conclusion

With Amazon Bedrock Managed Knowledge Base, your team no longer runs a vector store or manages the underlying retrieval infrastructure. With the migration guide in the `amazon-bedrock` skill, you ask your agent for a plan, review it, and approve only the resources you want built.

To get started, set up the [Agent Toolkit for AWS](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/quick-start.html) and ask your agent for a read-only assessment of your knowledge base. After migration, explore [agentic retrieval](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-agentic-retrieve.html) for multi-part questions. To learn more, see [Build enterprise search for agents with Amazon Bedrock Managed Knowledge Base](https://aws.amazon.com/blogs/machine-learning/build-enterprise-search-for-agents-with-amazon-bedrock-managed-knowledge-base/) on the AWS Machine Learning Blog.

## About the authors
