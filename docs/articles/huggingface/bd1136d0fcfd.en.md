---
vendor: huggingface
title: The Agent Said It Was Done. The Database Disagreed.
original_title: The Agent Said It Was Done. The Database Disagreed.
url: https://huggingface.co/blog/microsoft/thinkingbox
date: 2026-08-27
lang: en
captured: 2026-10-10
extractor: readability-v1
status: ok
body_sha: 40538b2a7fbf
---


# The Agent Said It Was Done. The Database Disagreed.

Enterprise

Article

					October 3, 2026


64

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64b8491203124195cd795cad/KWtqxooyzbqzLqdJorOPi.png)](https://huggingface.co/tuhink)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6a27ffbf0ea26227e43a0d29/Hk8XoWHT5braavBTjifaw.jpeg)](https://huggingface.co/Hectozar)
- [![](https://huggingface.co/avatars/821997acf79b7113de576661b1111109.svg)](https://huggingface.co/youngko)
- [![](https://huggingface.co/avatars/1462091a632d06d8b3bdf28a8007f621.svg)](https://huggingface.co/IronTech-Studios)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/YtxawKNmLmMd5dkoGXX6j.png)](https://huggingface.co/bedesign62)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/0K6rX9DTE_L7C_ktLloT7.jpeg)](https://huggingface.co/geminiomnidev)

Tuhin Kundu

tuhink

microsoft

*Microsoft ThinkingBox grades AI agents on the records they leave behind, not the sentences they generate, and then asks whether they can do it twenty times in a row. It is now available through Hugging Face.*

[![Figure-1](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/Dzuml_9K2lfRq4hZi17EY.png)](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/Dzuml_9K2lfRq4hZi17EY.png)

*Figure 1: ThinkingBox runs an agent against isolated MCP tool sessions, then grades the terminal backend state and side effects it leaves behind. From our [ThinkingBox paper](https://arxiv.org/abs/2608.19741).*

#### This is a joint blog by Microsoft and Hugging Face, special thanks to Tommy Guy (founder at Enderis AI, previously Microsoft), Sergio Paniego from Hugging Face and our former interns Zhuochun Li (University of Pittsburgh), Ali Keramati (UC Irvine), Youngmin Ko (Northwestern) for co-authoring/reviewing efforts.

A customer writes in. Her $745 kitchen appliance has been stuck in a courier "exception" at a Nashville distribution center, fifteen days past its estimated delivery date.

The AI agent does careful work. Nine tool calls: it pulls the order, checks tracking, looks up her customer profile, searches the refund policy twice, confirms no ticket exists, opens one, documents the timeline, and reads the policy correctly; her account segment genuinely does not qualify for late-delivery compensation.

Then it closes the ticket as **resolved** and replies “ *Since your query is resolved, is there anything I may assist you with?* ”

Two things are wrong. The carrier exception is still open, so the required end state was **on hold**, pending resolution. And the customer never got a real answer to what she actually asked.

An AI grader checking tool calls would see nine well-formed ones. The grader checking whether the agent wrote to the database would see that too. The database is what **disagrees**.

That gap is what ThinkingBox measures. Across 507 stateful business workflows, each run 20 times against various LLM models, it grades agents on terminal backend state and side effects. This post covers what we found, what consistency costs, and how to run the benchmark yourself through [OpenEnv](https://github.com/huggingface/OpenEnv/tree/main/envs/thinkingbox_env).

**You can run this one yourself:** the example above is adapted from a benchmark task [sandbox_external_retail_group1.py:test_case_ST003_006](https://github.com/microsoft/thinkingbox-data/blob/thinkingbox-bench-v1.0/dataset/test_case/sandbox_external_retail/sandbox_external_retail_group1.py#L984-L1223), and the executable check that fails is a single field: the ticket's status is solved where the required end state is hold. The full trace is in [ Appendix D.4, Case 3 of our paper](https://arxiv.org/pdf/2608.19741).

**Contents**

- [A tool call is not an outcome](https://huggingface.co/blog/microsoft/thinkingbox#a-tool-call-is-not-an-outcome)
- [One success is not reliability](https://huggingface.co/blog/microsoft/thinkingbox#one-success-is-not-reliability)
- [Can you depend on the model behind your agent?](https://huggingface.co/blog/microsoft/thinkingbox#can-you-depend-on-the-model-behind-your-agent)
- [What consistency costs](https://huggingface.co/blog/microsoft/thinkingbox#what-consistency-costs)
- [Failure signatures](https://huggingface.co/blog/microsoft/thinkingbox#failure-signatures)
- [How it works](https://huggingface.co/blog/microsoft/thinkingbox#how-it-works)
- [Run it yourself](https://huggingface.co/blog/microsoft/thinkingbox#run-it-yourself)
- [Where this goes next](https://huggingface.co/blog/microsoft/thinkingbox#where-this-goes-next)

> Want to try it before reading the results? Skip to section Run it yourself.

## A tool call is not an outcome

Final responses and valid tool calls are only proxies. An agent can sound correct while leaving the wrong value, changing the wrong record, or creating an extra side effect. Only the records it leaves behind settle the question.

The gap is substantial. In a common-set ablation covering 121,680 valid trials across 12 LLM models, 79,853 attempts failed the executable checks. Of those failures, 67.24% still terminated cleanly, invoked a state-changing tool, and reported no final tool error. Executable checks nevertheless found wrong field values in 77.61% of them, unintended extra effects in 43.30%, and missing required effects in 25.36%. Those state-check findings overlap.

> A trajectory is a claim. Database state is the evidence. Repetition is the trust test.

## One success is not reliability

An agent that processes a refund correctly once and mishandles it the next four times is not a working refund agent. So every task runs **20 independent times**, each from an identical clean backend, and we report three different things:

*Table 1: The three numbers we report, and the question each one answers.*

| Metric | What it measures | What it answers |
| --- | --- | --- |
| pass@1 | Share of all attempts that succeeded | How does it usually do? |
| pass@20 | Share of tasks solved **at least once** in 20 tries | Can it *ever* do this? Breadth. |
| Observed 20/20 | Tasks that actually passed **all** 20 recorded attempts | Can it *always* be correct? |

We use **observed 20/20** in this blog post as the literal count of how many of the 507 tasks passed 20 out of 20. No estimator, no smoothing.

Starting with the familiar view. The table below reports pass@1, the single-attempt score estimate, broken out by domain. This is the number most leaderboards publish, and on its own it reads like an ordinary capability ranking.

*Table 2: ThinkingBox-Bench pass@1 (%) by domain. Each model is evaluated on every task for 20 repeated trials. Bold marks the group leader; underline marks the runner-up. The standard errors for the single attempt score estimates are provided in [Table 4 in our ThinkingBox paper](https://arxiv.org/abs/2608.19741).*

| Model | Retail (98) | Auto insurance (100) | Travel (104) | Neobank (104) | Consulting (101) | Overall, task-weighted (507) |
| --- | --- | --- | --- | --- | --- | --- |
| *Proprietary models* |  |  |  |  |  |  |
| Claude Opus 5.5 | **80.97** | **68.40** | 54.28 | **71.25** | 61.58 | **67.16** |
| Claude Opus 5 | 80.71 | 65.80 | 49.95 | 70.62 | **66.19** | 66.50 |
| GPT-5.4 | 76.33 | 62.65 | **68.12** | 65.34 | 54.60 | 65.36 |
| GPT-5.6 Sol | 67.65 | 65.30 | 60.34 | 59.09 | 57.52 | 61.91 |
| Claude Sonnet 4.6 | 72.35 | 54.40 | 58.94 | 56.39 | 54.31 | 59.19 |
| GPT-6 Astra | 71.73 | 46.55 | 55.87 | 60.87 | 56.83 | 58.31 |
| GPT-5.2 | 70.20 | 22.40 | 53.70 | 51.15 | 34.06 | 46.28 |
| Claude Opus 4.6 | 68.62 | 8.30 | 21.11 | 35.67 | 27.82 | 32.09 |
| o3-pro | 37.70 | 2.95 | 17.31 | 24.28 | 14.60 | 19.31 |
| Grok-4.3 | 43.93 | 2.60 | 15.14 | 1.78 | 9.55 | 14.38 |
| *Open-weight models* |  |  |  |  |  |  |
| Kimi-K3 | **82.24** | **50.80** | **61.83** | 41.35 | **51.63** | **57.37** |
| Qwen3.8-27B | 64.03 | 47.85 | 53.41 | **47.88** | 45.69 | 51.70 |
| DeepSeek-V4-Pro | 68.21 | 29.65 | 43.13 | 44.86 | 31.04 | 43.26 |
| Kimi-K2.6 | 53.72 | 24.50 | 39.52 | 33.65 | 37.33 | 37.66 |
| GLM-5.1 | 58.67 | 25.70 | 35.43 | 13.27 | 34.06 | 33.19 |
| Qwen3.6-27B | 43.11 | 29.00 | 46.39 | 27.84 | 18.37 | 32.94 |
| Qwen3.5-9B | 19.90 | 0.70 | 4.71 | 1.15 | 2.33 | 5.65 |
| Mistral-Large-3 | 11.28 | 1.30 | 8.99 | 1.15 | 0.74 | 4.66 |

Claude Opus 5.5 **leads** overall at 67.16%, two-thirds of a point above Claude Opus 5. Kimi-K3 is the strongest **open-weights model**, within a point of GPT-6-Astra. **Domain matters just as much**: Claude Opus 4.6 scores 68.62% on retail but 8.30% on auto insurance.

> One good run tells you a model can do the work. It does not tell you whether it will do it again. So run every task 20 times and ask how much of that score survives.

[![Figure-2](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/DjaLNZKNeU--Xy2WFCvVX.png)](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/DjaLNZKNeU--Xy2WFCvVX.png)

*Figure 2: How much of each model's single-attempt score survives 20 repeats.*

**Only three** hold on to most of their pass@1 scores: GPT-6 Astra retains 78% of its single-attempt rate, and Claude Opus 5.5 and Claude Opus 5 each retain 71%. At the other end, GLM-5.1, Kimi-K2.6 and DeepSeek-V4-Pro each keep about 8%.

The gap between what a model **can do once** and what it does **every time** is the whole story.

## Can you depend on the model behind your agent?

[![Figure-3](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/NONd2WGm4vtGpsVgs-CIq.png)](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/NONd2WGm4vtGpsVgs-CIq.png)

*Figure 3: Breadth and consistency pull apart. Twelve of the eighteen models are shown; six below 33% pass@1 are omitted for legibility.*

**Kimi-K3 has the broadest coverage of any model we tested.** It solves **93.89%** of the benchmark at least once: 476 of 507 tasks. Only 31 tasks defeat it entirely, the lowest count in the field. On retail workflows it leads outright at 82.24% pass@1, ahead of every proprietary model.

**Kimi-K3 is also among the least consistent.** Just 68 of 507 tasks, 13.41%, succeed in all 20 attempts.

Claude Opus 5 inverts this. It solves fewer tasks at least once (79.09%; 106 defeat it entirely) but completes **47.53%** of the benchmark on every single attempt.

**A newer model does not fix this.** Claude Opus 5.5 scores higher than Claude Opus 5 on every-attempt average, 67.16% against 66.50%, and solves more tasks at least once. It passes exactly the same number of tasks on all 20 attempts: 241. Half a point of headline accuracy bought no additional dependability at all.

- Kimi-K3 solves **75 more tasks at least once** than Opus 5.
- Opus 5 solves **173 more tasks consistently** than Kimi-K3.

If you are choosing a model for work that touches real records, pass@20 is the wrong column to look at.

## What consistency costs

Capability comparisons usually stop at the score. For anyone deploying, the relevant question is what a successful unit of work costs. We measure that as cost per successful task attempt. We say task attempt because every benchmark task is run repeatedly and cost is incurred per attempt, so pass@1 is the matching quality denominator.

We took each model's recorded token usage from its full 507 × 20 campaign and priced it at undiscounted list rates available on [OpenRouter](https://openrouter.ai/)+, reversing promotional discounts and excluding endpoints that declare quantization. Input, output and cache rates all come from one provider endpoint per model.

Then we divided one run's cost by the number of attempts that **succeeded**:

> Cost per successful task attempt = estimated cost for 507 attempts, one per task ÷ (507 × pass@1)

This is a comparative efficiency index, not an invoice, and not the price of serving one production request. It also prices single successes, not consistency. We price consistency next.

**Example:** GPT-5.4 costs $43.49 for 507 attempts (one attempt per task) and has 65.36% pass@1, so $43.49 ÷ (507 × 0.6536) = $0.131 per successful task attempt.

### Pareto cost frontier

A model is on the frontier if no other model is both *no more expensive* **and** *at least as accurate*. Three models qualify; every other model is dominated on at least one axis.

[![Figure-4](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/oGmXYrxoNPJfsQndxlcMD.png)](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/oGmXYrxoNPJfsQndxlcMD.png)

*Figure 4: Cost per successful task attempt against pass@1. Ringed dots are pareto cost frontier models.*

**The frontier has three steps.** GPT-5.6 Sol has the **lowest cost per success** at $0.127; GPT-5.4 raises pass@1 by 3.45 percentage points for $0.004 more per success; Claude Opus 5.5 adds another 1.80 points at $0.276 per success. Each of the three remains on the cost frontier line because no cheaper model matches its pass@1.

Claude Opus 5 is the clearest case: at $0.475 per successful attempt and 66.50% pass@1, it is both more expensive and less accurate than Claude Opus 5.5 at $0.276 and 67.16%.

### Now price consistency

Cost per success rewards a model that is cheap and often right. It does not reward a model that is right every time. So we also compute cost per dependable task: the cost of the full 20-run campaign divided by the number of tasks the model passed on all 20 attempts.

> Cost per dependable task = estimated cost of 20 runs of 507 attempts ÷ tasks passing 20/20

**Example:** GPT-6-Astra costs 20 × $86.03 = $1,720.60 for the campaign and passes 231 tasks on every attempt, so $1,720.60 ÷ 231 = $7.45 per dependable task.

*Table 3: The nine lowest costs per dependable task among models with at least one observed 20/20 task, sorted low to high. Estimated $, not actual cloud bills.*

| Model | Tasks passing 20/20 | Est. cost, 20 runs | Cost per dependable task |
| --- | --- | --- | --- |
| GPT-5.4 | 128 (25.25%) | $869.80 | **$6.80** |
| GPT-6 Astra | 231 (45.56%) | $1,720.60 | $7.45 |
| Claude Opus 5.5 | 241 (47.53%) | $1,880.77 | $7.80 |
| GPT-5.6 Sol | 82 (16.17%) | $800.00 | $9.76 |
| Claude Opus 5 | 241 (47.53%) | $3,206.00 | $13.30 |
| Claude Sonnet 4.6 | 102 (20.12%) | $1,587.60 | $15.56 |
| GPT-5.2 | 44 (8.68%) | $878.00 | $19.95 |
| Kimi-K3 | 68 (13.41%) | $1,406.40 | $20.68 |
| Qwen3.8-27B | 38 (7.50%) | $925.80 | $24.36 |

**Now rank by consistency.** GPT-5.4 is the **cheapest** at $6.80, though only 128 tasks meet the bar. GPT-6 Astra reaches 231 at $7.45, and Claude Opus 5.5 the joint-highest 241 at $7.80.

None of the three dominates the others: each additional dependable task costs more. Claude Opus 5 also passes 241, but at $13.30, so Opus 5.5 dominates it outright. GPT-5.6 Sol, the cheapest per single success at $0.127, costs $9.76 per dependable task. The cheapest way to get a right answer is not the cheapest way to get a dependable one.

## Failure signatures

We assign each failed trace one deterministic diagnostic signature, and the headline is actionable: roughly four in five failures are tool handling, not reasoning. Across an ablation study in [Table 5 of our paper](https://arxiv.org/pdf/2608.19741):

| Failure signature | Share of failures |
| --- | --- |
| Tool usage | 79.9% |
| Wrong state updates | 10.3% |
| Incomplete user resolutions | 7.0% |
| No state-changing action | 2.9% |

These are unweighted averages of per-model shares and observable labels, not unique causal explanations.

The practical pattern is simple: agents usually get far enough to attempt the workflow, then fail to recover from tool errors, failed preconditions, or empty lookups. That is a retry and error-recovery problem before it is a model problem.

Difficulty also changes by domain: across the models listed in Table 2 above, retail averages 59.52% pass@1 while auto insurance averages 33.83%.

**What to do about it.** Treat the 20/20 rate as a design input, not a verdict. The same signal the benchmark grades on is available in production: check the terminal state before you commit, not the model's summary of it.

Classify tool and system errors so retries target the recoverable ones. Cut the tool surface to what the workflow needs. And require human approval on the changes you cannot cheaply reverse. We have not measured the lift from any of these on this benchmark, which is exactly the kind of thing the environment now makes testable.

## How it works

ThinkingBox is the agent sandbox, while ThinkingBox-Bench is a dataset benchmark to evaluate agents. The diagram at the top of this post shows the loop; here is what each part does.

[![Figure-1a](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/elbRGqTXW6PIqci7xcEJN.png)](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/elbRGqTXW6PIqci7xcEJN.png)

*Figure 5: The sandbox loop from panel A in Figure 1 above: isolated tool session, terminal database state, side effects, executable judges.*

Each task defines a starting backend state, a user goal, the available MCP tools, the domain policy, and executable checks over the terminal state. A simulated user holds private context (a booking reference, a preference, or a date of birth) and releases it only when asked.

Every attempt gets an isolated MCP session with freshly initialized state. Two attempts of the same task never share a database row or cached tool state, which is what makes 20-trial comparison meaningful.

At the end, a side-effect extractor derives what actually changed, and deterministic judges compare it against the required end state, accepting *any* trajectory that produces the right outcome while rejecting wrong, missing or extra effects. For requirements with no clean database value ("did the agent disclose this is not guaranteed?"), a narrow binary rubric question handles the semantics. 477 of the 507 tasks are graded on state alone; 30 add response rubrics.

The trust boundary: the model sees tasks, dialogue and tool schemas. Golden state, assertions, grading internals and credentials stay on the evaluator side.

## Run it yourself

ThinkingBox is now on Hugging Face, both [the harness](https://huggingface.co/docs/openenv/environments/thinkingbox) and [the dataset](https://huggingface.co/datasets/microsoft/ThinkingBox-Bench). ThinkingBox-Bench now sits behind the OpenEnv interface, and each finished episode returns a binary pass/fail reward. The released adapter is designed for evaluation; separate, non-benchmark scenarios can use the same interface in training workflows.

### Before you start

Tested on Linux and WSL, with Python 3.11+, [uv](https://docs.astral.sh/uv/) and Docker. You also need a [thinkingbox-data](https://github.com/microsoft/thinkingbox-data) checkout at the pinned release and model endpoints for the agent, simulated user and judge. One endpoint can serve all three roles, which is the simplest way to start. The OpenEnv image starts *only the OpenEnv API*; everything else you run yourself.

### Install

```
# 1. OpenEnv + the ThinkingBox environment
git clone https://github.com/huggingface/OpenEnv
cd OpenEnv
uv sync --project envs/thinkingbox_env --frozen
# 2. The executable benchmark, at the pinned release
git clone https://github.com/microsoft/thinkingbox-data
git -C thinkingbox-data checkout thinkingbox-bench-v1.0
# 3. The ThinkingBox CLI, which provides `tb`
uv tool install "thinkingbox @ git+https://github.com/microsoft/thinkingbox"
```

### Start Typesense

In a **second terminal**, start Typesense 30.1 and wait for its health check:

```
mkdir -p .typesense-data
docker run --rm -d --name thinkingbox-typesense \
  -p 8108:8108 \
  -v "$PWD/.typesense-data:/data" \
  typesense/typesense:30.1 \
  --data-dir /data --api-key=Fake --enable-cors
until curl -fsS http://127.0.0.1:8108/health; do sleep 1; done
```

### Start the MCP servers

In a **third terminal**, start the Session Proxy and MCP servers.

```
cd OpenEnv
tb mcp-start --host 127.0.0.1 --port 7111 \
  --servers "$PWD/thinkingbox-data/servers/servers.yaml"
curl -fsS http://127.0.0.1:7111/health
```

### Start the OpenEnv server

Back in the first terminal, start the OpenEnv server against a ThinkingBox YAML config naming your three models ([config guide](https://github.com/microsoft/thinkingbox/blob/main/docs/llm_endpoint_config.md)):

```
OPENENV_TB_CONFIG="$PWD/thinkingbox.yaml" \
uv run --project envs/thinkingbox_env --frozen server
```

### Check readiness

Gate on readiness before running anything. It returns 503 until its observable data, configuration and Session Proxy checks pass. It cannot observe Typesense or live-probe every model endpoint, so confirm those separately:

```
curl -sS http://127.0.0.1:8000/ready
```

### Score an episode

Now score a real episode. [example_usage.py](https://github.com/huggingface/OpenEnv/blob/main/examples/thinkingbox/example_usage.py) only resets and lists tools; for agent actions, effects and assertions use the packaged evaluator:

```
echo "- sandbox_external_retail_group1.py:test_case_ST002_001" > one_task.yaml
uv run --project envs/thinkingbox_env thinkingbox-eval \
  one_task.yaml \
  --config "$PWD/thinkingbox.yaml" \
  --output results.jsonl \
  --errors-output errors.jsonl \
  --repeat 1 --message-timeout 1800
```

The OpenEnv adapter writes operational failures to an errors sidecar so they can be rerun rather than silently mixed with model outcomes. A canonical result must resolve or explicitly account for those attempts; we counted system errors as unsuccessful trials.

Runs are gated on a pinned framework commit, a pinned data release and a bundle hash, so a canonical result is verifiable rather than asserted.

## Where this goes next

The useful part of this work is not our pass@1 leaderboard. It is the environment.

If you are evaluating an agent that touches real records:

- **Inspect a failure.** Find a run that terminated cleanly and still failed, and look at what actually changed in the database. It reframes what your own evals measure.
- **Reproduce one task** through OpenEnv with your own model.
- **Report a repeat metric, and define it.** Whatever k your use case justifies; say whether you are reporting best-of-k or every-of-k, and how you computed it.

Further details can be found in the following links:

- **Environment:** [envs/thinkingbox_env](https://github.com/huggingface/OpenEnv/tree/main/envs/thinkingbox_env)
- **OpenEnv:** [https://huggingface.co/docs/openenv/environments/thinkingbox](https://huggingface.co/docs/openenv/environments/thinkingbox)
- **Framework:** [microsoft/thinkingbox](https://github.com/microsoft/thinkingbox) · [tutorial](https://github.com/microsoft/thinkingbox/blob/main/docs/tutorial.md)
- **Benchmark:** [microsoft/thinkingbox-data](https://github.com/microsoft/thinkingbox-data) · [v1.0 release](https://github.com/microsoft/thinkingbox-data/releases/tag/thinkingbox-bench-v1.0)
- **Dataset viewer:** [microsoft/ThinkingBox-Bench](https://huggingface.co/datasets/microsoft/ThinkingBox-Bench)
- **Paper:** [arXiv:2608.19741](https://arxiv.org/abs/2608.19741) or [HF](https://huggingface.co/papers/2608.19741)
- **RL training (coming soon):** [microsoft/thinkingbox-training](https://github.com/microsoft/thinkingbox-training)

ThinkingBox code is MIT-licensed; the benchmark data is [CDLA-Permissive-2.0](https://cdla.dev/permissive-2-0/); the OpenEnv environment ships under OpenEnv's BSD-3-Clause.

Disclaimer: every task in the public benchmark is a synthetic reconstruction. The workflows and policies are modeled on real AI agentic enterprise patterns; the customers are not real.

*ThinkingBox and ThinkingBox-Bench is built by the Microsoft Copilot Studio team in partnership with Toloka with collaborators from the University of Pittsburgh, Northwestern University, Columbia University and UC Irvine who interned at Microsoft. Questions are welcome in the comments section below or on [github](https://github.com/microsoft/thinkingbox/discussions)*

+ OpenRouter cost snapshot taken on Sept 20th 2026; Opus 5.5 pricing as per the Anthropic site.

## Datasets mentioned in this article 1

## Papers mentioned in this article 1

More from this author

## Hugging Face Models on Foundry Managed Compute

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1583646260758-5e64858c87403103f9f1055d.png)

21

July 7, 2026

## Differential Transformer V2

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1583646260758-5e64858c87403103f9f1055d.png)

53

January 20, 2026

### Community

CyberNativeAI

5 days ago

`ST003_006` delegates its pass check to [`validate_database`](https://github.com/microsoft/thinkingbox-data/blob/fcaba4c1a9debec42fda7f15bf29fe6d6b46c431/dataset/test_case/sandbox_external_retail/sandbox_external_retail_group1.py#L13). Unequal result and golden database hashes fail even when `diff` is empty. The diff explains a failure; it does not decide the pass.

This [small replay](https://github.com/CyberNative-AI/.github/tree/main/notes/thinkingbox-state-check) exercises the released function with four authored effect inputs. Run `python3 reproduce.py`. It verifies the source pin and tests supplied hashes; it does not calculate a database hash, run an agent, or reproduce the full environment.

AI-assisted source reading and example by CyberNative AI LLC.

Nomad-link-id

4 days ago

The useful cut is agent-reported "done" versus backend terminal state.

A green success from the same process that acted is a claim, not a grade. I'd want the eval to score durable side effects (ticket status, refund state, policy-cited fields) against a frozen oracle — and fail when the narrative is green while the database disagrees.

Practical check: can a run be marked done when the terminal-state fixture is red?

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fmicrosoft%2Fthinkingbox) or [log in](https://huggingface.co/login?next=%2Fblog%2Fmicrosoft%2Fthinkingbox) to comment


64

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64b8491203124195cd795cad/KWtqxooyzbqzLqdJorOPi.png)](https://huggingface.co/tuhink)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6a27ffbf0ea26227e43a0d29/Hk8XoWHT5braavBTjifaw.jpeg)](https://huggingface.co/Hectozar)
- [![](https://huggingface.co/avatars/821997acf79b7113de576661b1111109.svg)](https://huggingface.co/youngko)
- [![](https://huggingface.co/avatars/1462091a632d06d8b3bdf28a8007f621.svg)](https://huggingface.co/IronTech-Studios)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/YtxawKNmLmMd5dkoGXX6j.png)](https://huggingface.co/bedesign62)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/0K6rX9DTE_L7C_ktLloT7.jpeg)](https://huggingface.co/geminiomnidev)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/647cfece36e109abce3f0090/jTLaPk6En8p608on8sfZ3.png)](https://huggingface.co/jmarceno)
- [![](https://huggingface.co/avatars/2b4cb7be234f99a0df5cea995cf46837.svg)](https://huggingface.co/garyamorris)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/vIHJ-RvmYKUbiydPc5GFl.png)](https://huggingface.co/whitesal)
- [![](https://huggingface.co/avatars/39abcb2f6dba6ec01822dce0b5a7c2ab.svg)](https://huggingface.co/sisoma2)
- [![](https://huggingface.co/avatars/7a38edf6010c8b01c2c2e1e5c21e4b67.svg)](https://huggingface.co/Hivartei)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/reKDqB0OArc5x-li5obfp.png)](https://huggingface.co/Wizzas)

## Datasets mentioned in this article 1

## Papers mentioned in this article 1
