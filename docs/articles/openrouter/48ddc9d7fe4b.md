---
vendor: openrouter
title: 欧盟 AI 法案与科罗拉多州 ADMT 合规：AI 智能体的人工监督
original_title: EU AI Act & Colorado ADMT Compliance: Human Oversight for AI Agents
url: https://openrouter.ai/blog/tutorials/human-oversight-eu-ai-act-compliance-agent-sdk
date: 2026-06-08
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 1ae2691d3ccb
translator: agent
---

# 欧盟 AI 法案与科罗拉多州 ADMT 合规：AI 智能体的人工监督

Kenny Rogers ·6/8/2026 · 更新于 9/24/2026

AI agent 已经不只是回答问题了。它们在批贷款申请、分诊病人登记表、跑工资核算、决定谁被标记进欺诈审查。这些决定错一次，责任落在部署方身上。

监管机构已经跟上了。第一个硬性期限在 2026 年 8 月落地。如果你构建的 agent 触及金融服务、医疗、招聘，或任何"输出错了会对真实的人产生真实后果"的领域，合规时钟已经在走。

三项法规汇到同一条义务上：必须有人能够监督、介入并推翻影响人的 AI 驱动决策。[Agent SDK](https://openrouter.ai/docs/sdks/typescript/call-model/overview)里的原语，今天就够把这些控制接进你的 agent。

| 法规 | 生效时间 | 适用于谁 | 核心要求 |
| --- | --- | --- | --- |
| [欧盟 AI 法案第 14 条](https://artificialintelligenceact.eu/article/14/) | 2026 年 8 月（高风险义务） | 向欧盟居民提供服务的高风险 AI 系统的任何提供者或部署者，无论公司总部在哪。 | 具备介入和推翻能力的人工监督；监督动作的审计轨迹。 |
| [科罗拉多州 ADMT 法（SB26-189）](https://leg.colorado.gov/bills/sb26-189) | 2027 年 1 月 | 在科罗拉多州开展业务的任何开发者或部署者，包括身处外州但对科罗拉多居民做重大决定的公司。 | 受覆盖的开发者/部署者须提供文档、披露、消费者权利流程；当受覆盖的 ADMT 实质影响重大决定时，提供有意义的人工复核/重审。 |
| [NIST AI RMF（GOVERN 1）](https://airc.nist.gov/AI_RMF_Knowledge_Base/Playbook/Govern) | 自愿，被美国监管机构引用 | 任何开发或部署 AI 系统的组织（自愿，但美国联邦机构日益视之为应有标准）。 | 与风险相称的人工监督；监督控制的文档化。 |

共同的主线：如果你的 agent 做出或实质影响对人有重大后果的决定（信贷、就业、医疗、安全），你就需要在"模型的建议"和"动作的执行"之间有一道可审查的闸门。

下面是用 `@openrouter/agent` 满足这些要求的 5 个模式，建立在 [HITL tools cookbook](https://openrouter.ai/docs/cookbook/building-agents/hitl-tools)（讲 SDK 机制）之上——这里讲你额外叠加的合规模式。

> 注：本文提供工程模式，不构成法律建议。哪些法规适用于你的具体用例和辖区，请咨询法律顾问。

## 直接交给你的 agent

想让编码 agent 来实现这套？复制下面这个提示词：

```
I need to add regulatory-compliant human-in-the-loop controls to my AI agent using the OpenRouter Agent SDK.

Inspect my codebase to identify which tools and actions are high-risk (financial, PII, legal, or safety-critical), then infer the appropriate risk tiers and implement a compliance layer using the Agent SDK HITL tools.

The compliance layer should:

1. Mark high-risk tools with requireApproval or onToolCalled gates based on my risk classification.
2. Log every oversight event (tool invocation, human decision, timestamp, reviewer ID) to my audit backend.
3. Add timeout-based escalation: if no human responds within the deadline, escalate to a supervisor or reject the action.
4. Stamp each human decision with reviewer identity and timestamp via onResponseReceived.
5. Persist conversation state with a StateAccessor backed by my chosen storage so audit records survive restarts.

Consult these pages for current SDK shapes and patterns:
- HITL tools reference: https://openrouter.ai/docs/sdks/typescript/call-model/tools#human-in-the-loop-hitl-tools
- Tool Approval & State: https://openrouter.ai/docs/agent-sdk/call-model/tool-approval-state
- callModel API reference: https://openrouter.ai/docs/sdks/typescript/call-model/api-reference

Do not hard-code secrets. Use environment variables for API keys and database credentials.
```

## 1. 按风险层级给工具分类

法规要求对**有重大后果**的动作做人工审查。先把工具切成层级：

| 层级 | 动作示例 | 控制 |
| --- | --- | --- |
| **高风险** | 金融交易、PII 处理、访问决策、医疗建议 | 强制暂停的 HITL 工具（`return null`） |
| **中风险** | 群发邮件、内容审核、数据导出 | 带条件谓词的 `requireApproval` |
| **低风险** | 搜索、只读查询、格式化 | 无需闸门 |

```
import { OpenRouter, tool } from '@openrouter/agent';
import { z } from 'zod';

// High-risk: always pauses for human review
const processCreditDecision = tool({
  name: 'process_credit_decision',
  description: 'Issue or deny a credit application',
  inputSchema: z.object({
    applicationId: z.string(),
    recommendedAction: z.enum(['approve', 'deny', 'refer']),
    riskScore: z.number(),
    applicantName: z.string(),
  }),
  outputSchema: z.object({
    decision: z.enum(['approved', 'denied', 'referred']),
    reviewerId: z.string(),
    reviewedAt: z.number(),
    justification: z.string(),
  }),
  onToolCalled: async () => {
    // Always escalate to human. No auto-resolve path for high-risk.
    return null;
  },
});
```

中风险工具用按上下文触发的条件谓词：

```
const sendBulkEmail = tool({
  name: 'send_bulk_email',
  description: 'Send email to a recipient list',
  inputSchema: z.object({
    recipients: z.array(z.string().email()),
    subject: z.string(),
    body: z.string(),
  }),
  outputSchema: z.object({ sent: z.boolean(), count: z.number() }),
  requireApproval: (params) => {
    // Gate kicks in above 50 recipients
    return params.recipients.length > 50;
  },
  execute: async (params) => {
    await sendEmails(params);
    return { sent: true, count: params.recipients.length };
  },
});
```

## 2. 给每个监督事件加审计日志

法规要求你证明人工监督确实发生了。也就是记录：谁、什么时候、审了什么、做了什么决定。把它接进 `onResponseReceived`：

```
import { tool } from '@openrouter/agent';
import { z } from 'zod';

const auditSchema = z.object({
  decision: z.enum(['approved', 'denied', 'referred']),
  reviewerId: z.string(),
  justification: z.string(),
});

const processCreditDecision = tool({
  name: 'process_credit_decision',
  description: 'Issue or deny a credit application',
  inputSchema: z.object({
    applicationId: z.string(),
    recommendedAction: z.enum(['approve', 'deny', 'refer']),
    riskScore: z.number(),
    applicantName: z.string(),
  }),
  outputSchema: z.object({
    decision: z.enum(['approved', 'denied', 'referred']),
    reviewerId: z.string(),
    reviewedAt: z.number(),
    justification: z.string(),
  }),
  onToolCalled: async (input) => {
    // Log the escalation event itself
    await writeAuditLog({
      event: 'escalated_to_human',
      toolName: 'process_credit_decision',
      input,
      timestamp: Date.now(),
    });
    return null;
  },
  onResponseReceived: async (raw) => {
    const parsed = auditSchema.parse(raw);
    const reviewedAt = Date.now();

    // Write the immutable audit record
    await writeAuditLog({
      event: 'human_decision_recorded',
      toolName: 'process_credit_decision',
      reviewerId: parsed.reviewerId,
      decision: parsed.decision,
      justification: parsed.justification,
      reviewedAt,
    });

    return { ...parsed, reviewedAt };
  },
});
```

`writeAuditLog` 应写入只追加存储。一个最小接口：

```
interface AuditEntry {
  event: string;
  toolName: string;
  timestamp?: number;
  reviewerId?: string;
  decision?: string;
  justification?: string;
  input?: unknown;
  reviewedAt?: number;
  escalatedTo?: string;
}

async function writeAuditLog(entry: AuditEntry): Promise<void> {
  // Write to your audit backend: Postgres, S3, Datadog, Splunk, etc.
  // The record must be append-only and tamper-evident for compliance.
  await db.insertInto('audit_log').values({
    ...entry,
    timestamp: entry.timestamp ?? Date.now(),
    id: crypto.randomUUID(),
  }).execute();
}
```

> 欧盟 AI 法案第 12 条（Record-Keeping，记录保存）要求高风险系统在其运行期内持续留日志。审计日志请存放在持久的、只追加的存储里，保留政策与你的法规要求对齐。

## 3. 实现基于超时的升级

没人响应的审查闸门比没有闸门更糟。法规预期系统能处理"审核人不响应"的情形。实现一个超时：要么升级给主管，要么默认拒绝该动作。

这个模式跑在 `callModel` 循环之外——在某个轮询陈旧待审记录的服务里：

```
interface PendingReview {
  conversationId: string;
  callId: string;
  toolName: string;
  createdAt: number;
  assignedTo: string;
}

const REVIEW_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes

async function escalateStaleReviews(
  pendingReviews: PendingReview[],
): Promise<void> {
  const now = Date.now();

  for (const review of pendingReviews) {
    const elapsed = now - review.createdAt;
    if (elapsed < REVIEW_TIMEOUT_MS) continue;

    await writeAuditLog({
      event: 'review_timeout_escalated',
      toolName: review.toolName,
      reviewerId: review.assignedTo,
      timestamp: now,
    });

    // Option A: Escalate to supervisor
    await assignToSupervisor(review);

    // Option B: Default-deny and resume the agent with a rejection
    // await resumeWithDenial(review);
  }
}
```

选哪个取决于你的风险偏好。对欧盟 AI 法案下的高风险系统，默认拒绝（方案 B）更稳：动作没有明确人工批准就永不执行。延迟有运营成本的较低风险系统，升级到主管（方案 A）既能推进、又保住了监督链条。

## 4. 让 StateAccessor 背后是持久存储

内存态在进程重启时就没了。为了合规，你的 `StateAccessor` 必须用持久存储，让待审记录、对话历史和审计上下文熬过崩溃、部署和水平扩容。

```
import type { ConversationState, StateAccessor, Tool } from '@openrouter/agent';

function createDurableStateAccessor<TTools extends readonly Tool[]>(
  conversationId: string,
): StateAccessor<TTools> {
  return {
    load: async () => {
      const row = await db
        .selectFrom('conversation_state')
        .where('id', '=', conversationId)
        .selectAll()
        .executeTakeFirst();

      if (!row) return null;
      return JSON.parse(row.state) as ConversationState<TTools>;
    },
    save: async (state) => {
      await db
        .insertInto('conversation_state')
        .values({
          id: conversationId,
          state: JSON.stringify(state),
          updated_at: new Date(),
        })
        .onConflict((oc) =>
          oc.column('id').doUpdateSet({
            state: JSON.stringify(state),
            updated_at: new Date(),
          }),
        )
        .execute();
    },
  };
}
```

状态每次迁移到 `'awaiting_hitl'` 或 `'awaiting_approval'`，待审记录就被持久化。你的升级服务（第 3 步）查这张表找陈旧的待审。

## 5. 全部接起来

完整流程：分类、闸门、日志、超时、恢复。以下假设第 1-2 步定义了 `processCreditDecision` 和 `sendBulkEmail`、第 2 步定义了 `writeAuditLog`、第 4 步定义了 `createDurableStateAccessor`。

```
import { OpenRouter } from '@openrouter/agent';

// processCreditDecision, sendBulkEmail defined in steps 1-2
// createDurableStateAccessor defined in step 4

const openrouter = new OpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY,
});

const tools = [processCreditDecision, sendBulkEmail] as const;
const conversationId = `conv-${crypto.randomUUID()}`;
const state = createDurableStateAccessor<typeof tools>(conversationId);

// Initial request
const result = openrouter.callModel({
  model: 'openai/gpt-4o',
  input: 'Review application APP-2024-001 and issue a credit decision',
  tools,
  state,
});

// Wait for the call to complete (or pause for human review)
const snapshot = await result.getState();

if (snapshot?.status === 'awaiting_hitl' || snapshot?.status === 'awaiting_approval') {
  const pending = snapshot.pendingToolCalls ?? [];

  // Surface to your review UI, queue, or notification system.
  // 'awaiting_hitl' fires for onToolCalled tools (processCreditDecision).
  // 'awaiting_approval' fires for requireApproval tools (sendBulkEmail).
  // Both resume via function_call_output here; see approval-and-state docs
  // for the approveToolCalls/rejectToolCalls alternative for requireApproval tools.
  for (const call of pending) {
    await createPendingReview({
      conversationId,
      callId: call.id,
      toolName: call.name,
      createdAt: Date.now(),
      assignedTo: getReviewerForTool(call.name),
      arguments: call.arguments,
    });
  }
}
```

审核人响应时（通过你的管理界面、Slack 动作、队列 consumer 等）：

```
// Retrieve the pending call from your review queue (by conversationId, callId, etc.)
const pendingCall = await getPendingReview(conversationId);

// Human supplies their decision
const humanDecision = {
  decision: 'approved' as const,
  reviewerId: 'reviewer-jane-smith',
  justification: 'Risk score within policy limits, verified income docs',
};

const resumed = openrouter.callModel({
  model: 'openai/gpt-4o',
  input: [
    {
      type: 'function_call_output',
      callId: pendingCall.callId,
      output: JSON.stringify(humanDecision),
    },
  ],
  tools,
  state,
});

const text = await resumed.getText();
```

`onResponseReceived` 钩子触发、给审计记录盖章，模型收到校验过的决定。

## 现在就开建

欧盟 AI 法案的高风险义务 2026 年 8 月落地；科罗拉多 [ADMT 法](https://leg.colorado.gov/bills/sb26-189)2027 年 1 月 1 日生效；NIST AI RMF 是自愿的，但被美国联邦机构日益引用为基线期望。一套实现——风险分类、审计日志、超时升级、持久状态——同时满足这三个框架。

Agent SDK 负责暂停执行、跨重启持久状态、按 schema 校验人工响应、干净恢复。你的活是把它接进你的审查工作流和审计存储。

相关治理控制（预算封顶、数据保留政策、模型限制）见 [Guardrails](https://openrouter.ai/blog/announcements/guardrails/)。

完整 SDK 参考和可运行示例：[HITL tools 文档](https://openrouter.ai/docs/sdks/typescript/call-model/tools#human-in-the-loop-hitl-tools)。

想把审查队列只留给真正需要人的调用，[Gate Agent Tool Calls with Jev](https://openrouter.ai/docs/cookbook/building-agents/gate-tool-calls-with-jev) 演示如何拿每个工具调用对照用户请求和你的政策打分、明确的自动放行或拦截、只有含糊的才升级——每次调用的理由和概率保留给审计日志。

## 常见问题

### 欧盟 AI 法案第 14 条要求什么？

第 14 条要求高风险 AI 系统纳入人工监督措施：人必须能理解系统能力、监控其运行、解读输出，并介入或推翻决定。审计日志的保留要求在第十二条（记录保存）和第九条（风险管理）之下。

### 欧盟 AI 法案什么时候生效？

法案 2024 年 8 月生效，但高风险义务（含第 14 条人工监督）自 2026 年 8 月起适用。被归类为高风险的系统须在该期限前展示合规的监督控制。

### 科罗拉多 ADMT 法什么时候生效？

科罗拉多的自动化决策技术法（[SB26-189](https://leg.colorado.gov/bills/sb26-189)）一般自 2027 年 1 月 1 日生效，适用于该日期当天及之后做出的重大决定。[科罗拉多州总检察长规则制定页面](https://coag.gov/ai/)跟踪实施细节。

### 科罗拉多 ADMT 法适用于科罗拉多之外的公司吗？

适用。该法覆盖任何"在科罗拉多开展业务"的开发者或部署者，不只是总部位于该州的公司。如果你部署的 ADMT 对科罗拉多居民的重大决定（就业、金融、住房、保险、医疗、教育、基本政府服务）有实质影响，你大概率在管辖之内。这与[科罗拉多隐私法](https://coag.gov/resources/colorado-privacy-act/)的管辖模式一致——覆盖在科罗拉多开展业务、或以商业产品/服务面向科罗拉多居民的实体。执法经由科罗拉多消费者保护法（违规按欺骗性贸易行为处理）。

### AI agent 的 human-in-the-loop（HITL）是什么？

指由人审查并批准（或拒绝）AI agent 提议的动作，然后才执行。在 Agent SDK 里，它通过 `onToolCalled`（暂停执行等待人工输入）和 `requireApproval`（按参数有条件地闸门工具执行）实现。
