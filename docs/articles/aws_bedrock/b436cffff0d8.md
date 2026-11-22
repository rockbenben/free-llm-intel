---
vendor: aws_bedrock
title: Build visibility for Codex on Amazon Bedrock with OpenTelemetry and Amazon CloudWatch
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-visibility-for-codex-on-amazon-bedrock-with-opentelemetry-and-amazon-cloudwatch
date: 2026-08-06
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 7d80b3dc8614
---

# 使用 OpenTelemetry 与 Amazon CloudWatch 为 Amazon Bedrock 上的 Codex 构建可见性

随着各组织从试用编码 agent 转向在整个工程团队中推广，领导层的问题也随之改变。它不再只是「这个工具能帮到某个开发者吗？」，而变成「我们如何理解采用情况、管理消耗、维持可靠性，并负责任地扩展访问权限？」。Codex 可以发出关于其活动的 OpenTelemetry（OTel）指标。当本地 Codex 客户端通过 Amazon Bedrock 使用 OpenAI 模型、并用 AWS IAM Identity Center 做认证时，你可以把这些指标经本地 OTel collector 路由到 Amazon CloudWatch。结果是得到一个 AWS 原生的 Codex 使用视图，可按用户、团队、部门、组织或成本中心组织。

这种方法不会在模型请求路径上增加集中式代理。开发者继续在本地使用 Codex。运行在每个开发者工作站上的 collector 在本地主机上接收指标，用组织上下文对其加以丰富，然后使用 AWS Signature Version 4（SigV4）把它们发送到区域性的 CloudWatch OpenTelemetry Protocol（OTLP）端点。参考部署只创建一块 CloudWatch 仪表板，而不是 Amazon Elastic Container Service（Amazon ECS）服务、负载均衡器、虚拟私有云（VPC）或公共摄取端点。

在本文中，我们解释这一模式如何支撑受治理的采用，回顾其架构，并概述在 [Codex on AWS 指导仓库](https://github.com/openai-on-aws/guidance-codex)中的实现。

## 把遥测数据转化为业务决策

当遥测能回答一个决策时，它才最有用，而不只是又生成一块仪表板。随附的 `CodexOnBedrock` 仪表板包含活跃用户、对话轮次、API 请求和 token 用量的滚动 24 小时总计。它还提供按模型、token 类型、用户、部门、团队、成本中心、组织和会话来源划分的视图。

这些信号可以帮助技术领导者区分广泛采用与孤立试验。例如，活跃用户在多个团队中普遍增加，和消耗高度集中在少数人身上，意味着不同的赋能需求。工具调用活动可以帮助团队看到 agentic 工作流在哪些地方扎下根来。请求与耗时指标可以支撑对体验劣化问题的排查。

| **高管问题** | **可用信号** | **可支撑的决策** |
| --- | --- | --- |
| Codex 的采用是否在扩大？ | 活跃用户、会话线程、轮次和 API 请求 | 是扩大试点，还是聚焦于上手引导 |
| 消耗集中在哪些地方？ | 按用户、模型、部门、团队和成本中心统计的 token | 在哪里实施用量回摊、复核用量或调整赋能方式 |
| 团队是否在使用 agentic 能力？ | 工具调用量和会话来源 | 哪些方面的工作流指导或系统投入可能有帮助 |
| 开发者体验是否可靠？ | API 状态、请求耗时和端到端轮次耗时 | 是否需要排查模型访问、网络或客户端行为 |
| 这项服务花了多少钱？ | 带 IAM 主体数据的 AWS Cost and Usage Reports（CUR）2.0 | 账单级别的财务报告与分摊 |

最后一行中的区别很重要。CloudWatch OTel 指标反映的是用量规模与运行行为。token 计数可以支撑趋势分析，但它不是账单台账。由于定价变化、折扣、抵扣和账单调整，按标价估算可能与实际费用存在差异。要得到实际支出，请使用 AWS Cost and Usage Reports（CUR）2.0 或相应的 Amazon Bedrock 成本管理报告中的 IAM 主体成本分摊。

## 方案概览

该架构对模型访问和遥测发布使用同一个 AWS 身份。开发者通过 IAM Identity Center 登录，并以 Amazon Bedrock 作为模型提供方运行 Codex。Codex 把指标发送到只监听 `127.0.0.1` 的 collector。collector 加上身份和组织属性、对指标做批处理，并用临时 AWS 凭证为发往 CloudWatch 的请求签名。

本地 Codex 遥测经本地 collector 流向 Amazon CloudWatch，collector 以 SigV4 认证发布指标，且不进入 Amazon Bedrock 的推理路径

Codex 会发出诸如 `codex.api_request`、`codex.api_request.duration_ms`、`codex.turn.e2e_duration_ms`、`codex.turn.token_usage`、`codex.turn.tool.call`、`codex.thread.started` 和 `codex.conversation.turn.count` 等指标。当前的 [Codex 配置文档](https://developers.openai.com/codex/config-advanced)说明 OTel 为选择启用，并为日志、指标和追踪分别提供了独立的 exporter 文档。

本地 collector 把 `user.id` 和 `user.email` 作为必需的资源属性加入。可选属性包括 `department`、`team.id`、`cost_center`、`organization`、`location`、`role` 和 `manager`。参考 collector 还会把这些属性复制到每个指标数据点上。这种方法使仪表板在本地 sidecar 与其他受支持的摄取模式下保持一致的 Prometheus Query Language（PromQL）分组。

## 实现参考模式

完整命令和模板位于[原生 AWS 访问快速入门](https://github.com/openai-on-aws/guidance-codex/blob/main/docs/QUICKSTART_NATIVE_AWS_ACCESS.md#optional-add-monitoring-otel)。以下五个阶段概述了实现过程。

### 1. 启用 CloudWatch OTel 能力

参考 runbook 首先在目标区域启用遥测的 OTel 增强和资源标签：

```
aws cloudwatch start-otel-enrichment --region us-west-2
aws observabilityadmin start-telemetry-enrichment --region us-west-2
aws cloudwatch get-otel-enrichment --region us-west-2
```

当前的 [CloudWatch OTel 文档](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/metrics-otel-overview.html)描述了原生 OTLP 摄取与 PromQL 查询。`start-otel-enrichment` 操作会为受支持的 AWS 出品指标启用增强与 PromQL 访问。`start-telemetry-enrichment` 操作会启用资源标签增强。在更改之前，请确认哪些账户级设置已经启用。

### 2. 部署仪表板并构建 collector

克隆仓库，然后部署仪表板并获取 collector 二进制文件：

```
deployment/scripts/deploy-otel-stack.sh --region us-west-2
deployment/scripts/build-local-collector.sh --all
```

AWS CloudFormation 堆栈部署 `CodexOnBedrock` 仪表板。collector 运行在开发者工作站上，因此这一步不会创建集中式的 collector 计算或网络基础设施。

### 3. 为每位开发者生成配置

从开发者已通过认证的 AWS profile 生成 collector 配置：

```
deployment/scripts/generate-sidecar-config.sh \
  --region us-west-2 \
  --profile codex-bedrock \
  --auto-lookup
```

使用 `--auto-lookup` 时，脚本可以从 IAM Identity Center 身份存储中读取组织属性。命令行显式指定的值可以覆盖探测到的值。如果某个可选属性不可用，请省略它的整个配置块。不要把占位字符串作为维度发送。它们会产生低价值的时序并削弱报告质量。

若要面向整个机群推广，请通过现有的端点管理流程生成并分发这份配置。把组织元数据当作受治理的数据对待：在用于高管报告之前，先确立获准的取值、归属和更新流程。

### 4. 配置 Codex 并授予最小权限访问

把 Codex 的指标 exporter 指向本地 collector。要包含完整的 `/v1/metrics` 路径，因为 Codex 不会自行追加：

```
[otel]
environment = "production"
log_user_prompt = false

[otel.metrics_exporter]
otlp-http = { endpoint = "http://127.0.0.1:4318/v1/metrics", protocol = "binary" }
```

collector 把指标转发到[区域性 CloudWatch OTLP 指标端点](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-OTLPEndpoint.html)，例如 `https://monitoring.us-west-2.amazonaws.com/v1/metrics`。对于短期 AWS 凭证，SigV4 是推荐的认证方式。发布身份需要 `cloudwatch:PutMetricData` 权限。这条指标路径不需要日志组或 ECS 权限。

保留 `log_user_prompt = false`。本设计旨在度量运营与采用信号，不收集源代码或 prompt 内容。

### 5. 验证完整链路

用生成的配置启动服务专用的 collector，运行一个 Codex 任务，然后在 CloudWatch 控制台打开 `CodexOnBedrock` 仪表板。你也可以使用 CloudWatch Query Studio 或仓库中的 `check-otel-pipeline.sh` 脚本，确认 `codex.turn.token_usage` 正在到达。

Codex 指标会周期性刷新，并在进程正常退出时刷新。参考 runbook 记录了 60 秒的间隔，并建议把 `OTEL_METRIC_EXPORT_INTERVAL=1000` 作为可选保护措施，用于可能跳过退出刷新的错误路径。如果没有指标出现，还要确认托管配置没有设置 `[analytics] enabled = false`，因为该设置会禁用 Codex 指标 pipeline。

## 带着治理意识来运维

让仪表板有用的那些维度，如果暴露范围过宽，也可能带来隐私与治理问题。面向高管报告时，请使用聚合的团队、部门和成本中心视图。把按用户划分的仪表板限制给经批准的运维、安全或财务角色，并让访问权限与员工监控政策和数据保留政策保持一致。

扩展时要控制指标基数。统一属性名称和取值，省略不支撑已定义决策的字段，避免在没有保留与查询方案的情况下加入项目名称或临时标识符。CloudWatch OTel 指标按每 GB 摄取量计价，PromQL 查询按扫描的样本数计价。在大范围推广之前，请查阅当前的 [CloudWatch OTel 定价文档](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/metrics-otel-pricing.html)和 [Amazon CloudWatch 定价](https://aws.amazon.com/cloudwatch/pricing/)。

这一模式提供的是可见性和软性控制。你可以使用 CloudWatch 告警和 Amazon Simple Notification Service（Amazon SNS）通知，在某个用户或团队超过设定用量阈值时发出提醒。但是，IAM Identity Center 直接签发临时凭证。这条本地遥测路径无法基于 token 预算同步阻断 Amazon Bedrock 请求。如果需要硬性强制，请使用带预算控制的在路径 gateway，并权衡运维与身份归因方面的取舍。

## 分阶段推广

先从一个工程小组开始，其负责人和开发者就遥测的用途达成一致。验证身份归因准确、仪表板能回答真实的运营问题、访问控制符合你的治理政策。

接下来，加入少量受控的组织维度，并为需要采取行动的情形定义告警。只有在 collector 生命周期、身份更新和支持流程都可重复之后，再通过托管的工作站配置进行扩展。最后，把 CloudWatch 用量遥测与 CUR 2.0 报告配对，让领导者可以在审阅采用情况与运行行为的同时，一并查看账单级成本。

这样的顺序能让初始投入保持很小，并让相关方有机会同时打磨指标和指标所要支撑的决策。

## 清理资源

要移除这套监控模式，请在开发者工作站上停止 collector，并删除仪表板堆栈：

```
aws cloudformation delete-stack \
  --stack-name codex-otel-dashboard \
  --region us-west-2

aws cloudformation wait stack-delete-complete \
  --stack-name codex-otel-dashboard \
  --region us-west-2
```

如果没有其他工作负载依赖这些账户级增强功能，你可以评估用 `aws cloudwatch stop-otel-enrichment` 和 `aws observabilityadmin stop-telemetry-enrichment` 将其禁用。请先确认依赖关系。这些设置可能支撑该账户中其他 CloudWatch 可观测性用例。

## 结论

扩展 Codex 不只是一个访问决策。它是一个运营模式决策，把开发者赋能、系统可靠性、治理和财务问责连接在一起。

通过将 Codex OTel 指标、IAM Identity Center 属性、本地 collector 和 Amazon CloudWatch 结合起来，组织可以构建可直接用于决策的可见性，而不必在推理路径上新增一个集中式服务。CloudWatch 呈现 Codex 正被如何使用。CUR 2.0 提供财务上的唯一事实来源。两者结合，支撑从试点到受治理采用的稳妥路径。

使用 [Codex on AWS 原生访问快速入门](https://github.com/openai-on-aws/guidance-codex/blob/main/docs/QUICKSTART_NATIVE_AWS_ACCESS.md#optional-add-monitoring-otel)开始试点，然后按你的组织所需做出的决策，调整维度、访问模型和报告节奏。

*本文描述的是基于一个公开指导仓库的实现模式，并不意味着 AWS 的发布或背书。*

## 关于作者
