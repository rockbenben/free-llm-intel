---
vendor: openrouter
title: EU AI Act & Colorado ADMT Compliance: Human Oversight for AI Agents
original_title: EU AI Act & Colorado ADMT Compliance: Human Oversight for AI Agents
url: https://openrouter.ai/blog/tutorials/human-oversight-eu-ai-act-compliance-agent-sdk
date: 2026-06-08
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 1ae2691d3ccb
---

# EU AI Act & Colorado ADMT Compliance: Human Oversight for AI Agents

Kenny Rogers ·6/8/2026 · Updated 9/24/2026

AI agents aren’t just answering questions anymore. They’re approving loan applications, triaging patient intake forms, running payroll calculations, deciding who gets flagged for fraud review. When one of those calls goes wrong, the liability sits with the deployer.

Regulators caught up. The first hard deadline lands in August 2026, and if you’re building agents that touch financial services, healthcare, hiring, or any domain where a wrong output has real consequences for a real person, the compliance clock is already running.

Three regulations converge on the same obligation: a human must be able to oversee, intervene in, and override AI-driven decisions that affect people. The [Agent SDK](https://openrouter.ai/docs/sdks/typescript/call-model/overview) has the primitives to wire these controls into your agent today.

| Regulation | Effective | Who it applies to | Core requirement |
| --- | --- | --- | --- |
| [EU AI Act, Article 14](https://artificialintelligenceact.eu/article/14/) | Aug 2026 (high-risk obligations) | Any provider or deployer of high-risk AI systems serving EU residents, regardless of where the company is based. | Human oversight with ability to intervene and override. Audit trail of oversight actions. |
| [Colorado ADMT Law (SB26-189)](https://leg.colorado.gov/bills/sb26-189) | Jan 2027 | Any developer or deployer doing business in Colorado, including companies outside Colorado that make consequential decisions about Colorado residents. | Covered developers/deployers must provide documentation, disclosures, consumer rights processes, and meaningful human review/reconsideration where covered ADMT materially influences consequential decisions. |
| [NIST AI RMF (GOVERN 1)](https://airc.nist.gov/AI_RMF_Knowledge_Base/Playbook/Govern) | Voluntary, referenced by US regulators | Any organization developing or deploying AI systems (voluntary, but increasingly expected by US federal agencies). | Human oversight proportional to risk. Documentation of oversight controls. |

The common thread: if your agent makes or influences decisions that materially affect people (credit, employment, healthcare, safety), you need a reviewable gate between the model’s recommendation and the action’s execution.

Below are 5 patterns that satisfy those requirements using `@openrouter/agent`, building on the [HITL tools cookbook](https://openrouter.ai/docs/cookbook/building-agents/hitl-tools) (which covers the SDK mechanics). Here we cover the compliance patterns you bolt on top.

> Note: This post provides engineering patterns, not legal advice. Consult legal counsel to determine which regulations apply to your specific use case and jurisdiction.

## Give this to your agent

Want your coding agent to implement this? Copy the prompt below:

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

## 1. Classify your tools by risk tier

Regulations require human review on actions that are **consequential**. Start by splitting your tools into tiers:

| Tier | Example actions | Control |
| --- | --- | --- |
| **High-risk** | Financial transactions, PII processing, access decisions, medical recommendations | HITL tool with mandatory pause (`return null`) |
| **Medium-risk** | Bulk emails, content moderation, data exports | `requireApproval` with conditional predicate |
| **Low-risk** | Search, read-only queries, formatting | No gate needed |

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

For medium-risk tools, use a conditional predicate that gates on context:

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

## 2. Add audit logging to every oversight event

Regulations require you to prove that human oversight happened. That means logging who reviewed what, when, and what they decided. Wire this into `onResponseReceived`:

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

The `writeAuditLog` function should write to append-only storage. A minimal interface:

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

> EU AI Act Article 12 (Record-Keeping) requires that high-risk systems maintain logs for their operational lifetime. Store audit logs in durable, append-only storage with retention policies that match your regulatory requirements.

## 3. Implement timeout-based escalation

A human review gate that nobody responds to is worse than no gate at all. Regulations expect the system to handle unresponsive reviewers. Implement a timeout that either escalates to a supervisor or rejects the action by default.

This pattern runs outside the `callModel` loop, in whatever service polls for stale pending reviews:

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

Which option to pick depends on your risk appetite. For EU AI Act compliance with high-risk systems, default-deny (Option B) is safer: the action never executes without explicit human approval. For lower-risk systems where delays have operational cost, escalation to a supervisor (Option A) keeps things moving while preserving the oversight chain.

## 4. Back your StateAccessor with durable storage

In-memory state disappears on process restart. For compliance, your `StateAccessor` must use durable storage so that pending reviews, conversation history, and audit context survive crashes, deploys, and horizontal scaling.

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

Every time state transitions to `'awaiting_hitl'` or `'awaiting_approval'`, the pending review is persisted. Your escalation service (step 3) queries this table to find stale reviews.

## 5. Wire it all together

Here’s the complete flow: classify, gate, log, timeout, resume. This assumes `processCreditDecision` and `sendBulkEmail` from steps 1-2, `writeAuditLog` from step 2, and `createDurableStateAccessor` from step 4.

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

When the reviewer responds (through your admin UI, Slack action, queue consumer, etc.):

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

The `onResponseReceived` hook fires, stamps the audit record, and the model receives the validated decision.

## Start building today

EU AI Act high-risk obligations land August 2026. Colorado’s [ADMT law](https://leg.colorado.gov/bills/sb26-189) takes effect January 1, 2027. NIST AI RMF is voluntary but increasingly referenced by US federal agencies as the baseline expectation. One implementation (risk classification, audit logging, timeout escalation, durable state) satisfies all three frameworks.

The Agent SDK handles pausing execution, persisting state across restarts, validating human responses against schemas, and resuming cleanly. Your job is to wire it into your review workflows and audit storage.

For related governance controls (budget caps, data retention policies, model restrictions), see [Guardrails](https://openrouter.ai/blog/announcements/guardrails/).

Full SDK reference and working examples: [HITL tools documentation](https://openrouter.ai/docs/sdks/typescript/call-model/tools#human-in-the-loop-hitl-tools).

To keep the review queue to the calls that need a person, [Gate Agent Tool Calls with Jev](https://openrouter.ai/docs/cookbook/building-agents/gate-tool-calls-with-jev) shows how to score each tool call against the user’s request and your policy, approve or block the clear cases automatically, and escalate only the ambiguous ones, with the per-call reason and probabilities kept for the audit log.

## FAQ

### What does EU AI Act Article 14 require?

Article 14 mandates that high-risk AI systems include human oversight measures. Humans must be able to understand the system’s capabilities, monitor its operation, interpret outputs, and intervene or override decisions. Audit log retention requirements fall under Article 12 (Record-Keeping) and Article 9 (Risk Management).

### When does the EU AI Act take effect?

The AI Act entered into force August 2024, but the high-risk obligations (including Article 14 human oversight) apply starting August 2026. That’s the deadline for systems classified as high-risk to demonstrate compliant oversight controls.

### When does Colorado’s ADMT law take effect?

Colorado’s Automated Decision-Making Technology law ([SB26-189](https://leg.colorado.gov/bills/sb26-189)) generally takes effect January 1, 2027 and applies to consequential decisions made on or after that date. The [Colorado AG’s rulemaking page](https://coag.gov/ai/) tracks implementation details.

### Does Colorado’s ADMT law apply to companies outside Colorado?

Yes. The law applies to any developer or deployer “doing business in” Colorado, not just companies headquartered there. If you deploy ADMT that materially influences consequential decisions (employment, finance, housing, insurance, healthcare, education, essential government services) about Colorado residents, you’re likely subject to the law. This follows the same jurisdictional pattern as the [Colorado Privacy Act](https://coag.gov/resources/colorado-privacy-act/), which covers entities that conduct business in Colorado or target Colorado residents with commercial products or services. Enforcement runs through the Colorado Consumer Protection Act (violations are treated as deceptive trade practices).

### What is human-in-the-loop (HITL) for AI agents?

HITL means a human reviews and approves (or rejects) an AI agent’s proposed action before it executes. In the Agent SDK, this is implemented through `onToolCalled` (which pauses execution and waits for human input) and `requireApproval` (which conditionally gates tool execution based on parameters).
