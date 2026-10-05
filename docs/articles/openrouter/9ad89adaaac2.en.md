---
vendor: openrouter
title: How to Gate Pull Requests on LLM Evals in CI
original_title: How to Gate Pull Requests on LLM Evals in CI
url: https://openrouter.ai/blog/tutorials/how-to-gate-pull-requests-on-llm-evals-in-ci
date: 2026-10-01
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: df3dfab1f6bd
---

# How to Gate Pull Requests on LLM Evals in CI

OpenRouter ·10/1/2026

Changing one line in a support agent’s system prompt can ship an agent that tells customers the refund window is 30 days when your policy says 14. Nothing in a normal CI pipeline checks what the model says, so the build passes and the first person to see the wrong answer is a customer.

Gating a pull request on a fixed eval set works the same way as gating on a failing unit test. You keep test cases in the repository, run them when a prompt changes, and block the merge when too many fail.

In this guide, you write an eval set for a support agent and score it with a script that calls OpenRouter. You measure how much the results move between runs with nothing changed, then wire the script into GitHub Actions as a required status check.

## Tl;dr

- A fixed eval set is a list of test cases committed to your repository. It changes only through a reviewed pull request.
- Filter at the job level rather than the workflow level. GitHub reports a job skipped by an `if` condition as a passing check, while a workflow skipped by a path filter leaves a required check pending and blocks the merge.
- The eval script exits non-zero when the pass rate falls below your threshold, and that exit code is what fails the job.
- Measure the threshold from repeated runs against an unchanged branch rather than picking a strict number.
- `temperature` and `seed` only help on models that list them in `supported_parameters`. Repeated sampling with a majority vote works on every model.

![Diagram of the eval gate in GitHub Actions: a pull request triggers a changes job that runs a path filter, an eval-gate job that either runs the fixed eval set or is skipped, and a merge that is allowed when the pass rate meets the threshold or the job was skipped and blocked when the pass rate is below the threshold](https://openrouter.ai/blog/images/eval-gate-job-level-path-filter.png)

## What LLM evals in CI means

An eval is a test case for an agent. It has an input and a rule for deciding whether the model’s answer was acceptable. A fixed eval set is a list of those cases committed to your repository, and it changes only through a reviewed pull request. The pipeline part is your CI setup. It decides when the cases run and what happens to the pull request when too many of them fail.

Deciding whether a model’s answer was good is a separate problem, and one option is to hand it to another model acting as a grader. That technique is called LLM-as-a-judge, and we cover it in [our LLM-as-a-judge guide](https://openrouter.ai/blog/tutorials/llm-as-a-judge-evaluate-ai-agents/). [Our tool-calling loop guide](https://openrouter.ai/blog/tutorials/build-tool-calling-agent-loop/) covers building the agent itself. This guide is about the pipeline between them.

## What you need before you can gate anything

Three things need to be in place before the gate can tell you anything useful.

- **A fixed, versioned eval set.** Anthropic’s guide to agent evals recommends [20 to 50 simple tasks drawn from real failures](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) as a starting set. We use three here so the example stays short.
- **A scoring method and a threshold.** The scoring method turns one answer into a pass or a fail you can count. The threshold applies to the run as a whole. This guide uses string assertions. A rubric or a judge model also works.
- **Runs repeatable enough to trust.** The gate should block on regressions, not on noise. Repeated sampling with a majority vote works on every model. `temperature` and `seed` help only on models that list them, so check [the model’s `supported_parameters`](https://openrouter.ai/docs/guides/overview/models) before relying on them.

You also need an [OpenRouter API key](https://openrouter.ai/keys) exported as `OPENROUTER_API_KEY`, Node 20 or newer, and [jq](https://jqlang.org/).

## Build the gate in four steps

By the end of these four steps, a pull request that touches your prompts runs your eval set automatically and cannot merge if the score drops.

- Trigger the eval only on the changes that can break your agent.
- Put the eval set in the repository, beside the prompts it tests.
- Write the script the CI job runs.
- Measure the threshold that decides whether the merge is blocked.

### Step 1: Trigger only on relevant changes

Run the eval when prompts, agent logic, tool schemas, the eval set, the eval script, or the workflow itself change. The last two are easy to leave out. If they are missing from the filter, a pull request that breaks the scoring logic or edits the gate skips the eval and merges untested.

You do that with two jobs. The first one always runs. It checks the files the pull request changed against a list of paths and outputs `true` or `false` depending on whether any match. The second job runs the eval, and it starts only when the first job returns `true`.

Start `.github/workflows/eval-gate.yml` with the workflow header and the first job. The paths listed under `agent:` are the ones you change for your own repository.

```
name: eval-gate
on: pull_request
concurrency:
  group: eval-gate-${{ github.ref }}
  cancel-in-progress: true
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      agent: ${{ steps.filter.outputs.agent }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: dorny/paths-filter@ceb8a2b8f2d89434be7ff52d3de7ec3738c5cc9d # v4.0.3
        id: filter
        with:
          filters: |
            agent:
              - '.github/workflows/eval-gate.yml'
              - 'prompts/**'
              - 'agents/**'
              - 'tools/**/schema.json'
              - 'eval-sets/**'
              - 'scripts/run-evals.mjs'
```

`concurrency` with `cancel-in-progress` cancels the previous run when someone pushes again to the same branch, so a pull request with several pushes in a row doesn’t pay for an eval run on each one.

Two things can go wrong here.

The first is a green check with no eval behind it. When the first job returns `false`, GitHub skips the eval job, and a [skipped job satisfies a required status check](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging). That is what lets unrelated pull requests merge. It also means a mistyped glob passes the check without running a single case, and a `changes` job that fails outright has the same effect, because GitHub skips a job whose `needs` dependency failed. Step 3 closes the second gap by making `changes` a required check as well. For the first, open the run log the first time a prompt change goes through and confirm the eval ran.

The second is where you put the filter. Do not move it up to the workflow level as `on.pull_request.paths`. GitHub’s documentation on [skipping workflow runs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs) says that when a workflow is skipped by path filtering, “checks associated with that workflow will remain in a ‘Pending’ state,” and a pull request that requires those checks is blocked from merging.

### Step 2: Put the eval set in the repository

Keep the eval set in the same repository as the prompts it tests. When someone edits a prompt, the test for it changes in the same pull request, and one reviewer sees both.

Four files sit alongside each other.

```
your-repo/
  .github/workflows/eval-gate.yml  -> the workflow from Step 1
  prompts/support-agent.md         -> the system prompt
  eval-sets/support-agent.json     -> the cases that test it
  scripts/run-evals.mjs            -> the script from Step 3
```

Save the eval set as `eval-sets/support-agent.json`. Each case has an input, the strings the answer must contain, and the strings it must not. An entry in `mustMention` can also be a list, as in the third case, and then the answer only has to contain one of the strings in it. A single literal string fails whenever the model writes “a person” or “our team” where you expected “human”, so use a list wherever more than one wording is acceptable.

```
[
  {
    "id": "refund-window",
    "input": "How long do I have to request a refund on a digital download?",
    "mustMention": ["14 days"],
    "mustNotMention": ["30 days"]
  },
  {
    "id": "refund-exception",
    "input": "I bought a download 60 days ago. Can I still get a refund?",
    "mustMention": ["14 days"],
    "mustNotMention": ["yes, you can"]
  },
  {
    "id": "escalation",
    "input": "Your product deleted my files and I want a lawyer.",
    "mustMention": [["human", "person", "our team", "specialist"]],
    "mustNotMention": ["14 days"]
  }
]
```

The prompt those cases test lives beside it, in `prompts/support-agent.md`.

```
You are a support agent for a digital downloads store.
The refund window is 14 days from purchase. There are no exceptions to it.
If a customer threatens legal action or reports data loss, hand off to a human
and do not quote the refund policy.
Answer in at most three sentences.
```

Start with three cases. Add one every time the agent does something wrong in production.

Put both `prompts/` and `eval-sets/` behind a [CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) rule, and turn on “Require review from Code Owners” in your branch protection rules. Otherwise the quickest way past a failing gate is to loosen the test that caught the regression. A `CODEOWNERS` file on its own only requests a review and does not block the merge.

### Step 3: Write the script the CI job runs

The job runs one script and exits non-zero when the pass rate falls below the threshold. That exit code is all CI needs to block a merge.

The script loads the eval set, sends each case to the model, checks the answer, and exits with a code that tells CI what happened. It uses only Node builtins, so there is nothing to install. Save it as `scripts/run-evals.mjs`.

```
import { readFileSync } from "node:fs";
import { parseArgs } from "node:util";

const { values } = parseArgs({
  options: {
    set: { type: "string", default: "eval-sets/support-agent.json" },
    prompt: { type: "string", default: "prompts/support-agent.md" },
    model: { type: "string", default: "anthropic/claude-sonnet-5" },
    threshold: { type: "string", default: "0.9" },
    samples: { type: "string", default: "3" },
    concurrency: { type: "string", default: "8" },
  },
});

const systemPrompt = readFileSync(values.prompt, "utf8");
const cases = JSON.parse(readFileSync(values.set, "utf8"));
const threshold = Number(values.threshold);
const samples = Number(values.samples);
const concurrency = Number(values.concurrency);

// Exit 2 for anything that stops the eval from running, so the job can tell
// "the agent got worse" apart from "the eval could not run".
function abort(message) {
  console.error(`::error::eval could not run: ${message}`);
  process.exit(2);
}

if (!Array.isArray(cases) || cases.length === 0) abort(`${values.set} has no cases`);
if (!(threshold > 0 && threshold <= 1)) abort(`--threshold must be greater than 0 and at most 1, got "${values.threshold}"`);
if (!Number.isInteger(samples) || samples < 1 || samples % 2 === 0) abort(`--samples must be a positive odd integer, got ${values.samples}`);
if (!Number.isInteger(concurrency) || concurrency < 1) abort(`--concurrency must be a positive integer, got ${values.concurrency}`);

class EvalDidNotRun extends Error {}

async function callModel(input) {
  const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    signal: AbortSignal.timeout(60_000),
    headers: {
      Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: values.model,
      // Route to one provider only. A different provider serving the same slug
      // between runs would look like a prompt regression.
      provider: { order: ["anthropic"], allow_fallbacks: false },
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: input },
      ],
    }),
  });
  if (!res.ok) throw new EvalDidNotRun(`${res.status} ${await res.text()}`);
  const body = await res.json();
  return { text: body.choices?.[0]?.message?.content ?? "", cost: body.usage?.cost ?? 0 };
}

async function run(input) {
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      return await callModel(input);
    } catch (err) {
      if (attempt === 3) throw new EvalDidNotRun(err.message);
      await new Promise((resolve) => setTimeout(resolve, attempt * 2000));
    }
  }
}

// A requirement is either a string, or an array meaning "any one of these".
function matches(answer, requirement) {
  const options = Array.isArray(requirement) ? requirement : [requirement];
  return options.some((option) => answer.includes(option.toLowerCase()));
}

function score(text, testCase) {
  const answer = text.toLowerCase();
  const must = testCase.mustMention ?? [];
  const mustNot = testCase.mustNotMention ?? [];
  return (
    must.every((r) => matches(answer, r)) &&
    !mustNot.some((r) => matches(answer, r))
  );
}

// One unit of work per sample, so the whole matrix runs with a fixed
// concurrency instead of one request at a time.
const jobs = cases.flatMap((testCase) =>
  Array.from({ length: samples }, () => testCase),
);
const results = new Map(cases.map((c) => [c.id, []]));
let spend = 0;
let cursor = 0;

async function worker() {
  while (cursor < jobs.length) {
    const testCase = jobs[cursor++];
    const { text, cost } = await run(testCase.input);
    spend += cost;
    results.get(testCase.id).push(score(text, testCase));
  }
}

const started = Date.now();
try {
  await Promise.all(Array.from({ length: Math.min(concurrency, jobs.length) }, worker));
} catch (err) {
  // A provider timeout is not a quality regression.
  abort(err.message);
}

let passed = 0;
for (const testCase of cases) {
  const verdicts = results.get(testCase.id);
  const majority = verdicts.filter(Boolean).length > samples / 2;
  if (majority) passed++;
  const trace = verdicts.map((v) => (v ? "." : "x")).join("");
  console.log(`${majority ? "PASS" : "FAIL"}  ${testCase.id}  ${trace}`);
}

const rate = passed / cases.length;
const seconds = ((Date.now() - started) / 1000).toFixed(1);
console.log(`\npass rate ${rate.toFixed(2)} against threshold ${threshold}`);
console.log(`${jobs.length} calls in ${seconds}s, cost $${spend.toFixed(4)} on ${values.model}`);

if (rate < threshold) {
  console.error(`::error::eval gate failed: ${passed}/${cases.length} cases passed`);
  process.exit(1);
}
```

The script does three things beyond calling the model.

It refuses to run when the eval set is empty or an option is malformed, and exits 2 before sending a request. Without those checks, an eval set that was accidentally replaced with `[]` would produce a pass rate of `NaN`, and `NaN < threshold` is false, so zero evaluations would pass the gate. A `--threshold` of `90%` or a negative `--samples` would pass it the same way, and a blank `--threshold` becomes `0`, which no pass rate can fall below, so the check also rejects `0`.

It runs each case several times, and each of those runs is a sample. It takes the majority verdict across the samples, because the same prompt does not always produce the same answer.

It also routes every request to one provider. A model slug such as `anthropic/claude-sonnet-5` is served by more than one provider through OpenRouter. At the time of writing, its endpoints include Anthropic, Amazon Bedrock, Azure, and Google. Without a routing preference, two runs of the same eval can reach two different providers, and a difference between their answers looks like a prompt regression. `provider.order` is a priority list of provider slugs, and `allow_fallbacks: false` tells us not to try any provider outside that list. If the listed provider fails, the request fails instead of moving to a backup, and the script exits 2. The [provider selection docs](https://openrouter.ai/docs/guides/routing/provider-selection) cover both fields. The pin is tied to the model you name. If you change `--model` to a model from another vendor, change the `order` value too, or no provider will match and every request will fail.

The cost printed on the last line comes from the `usage` object we include in every non-streaming response. The [usage accounting docs](https://openrouter.ai/docs/cookbook/administration/usage-accounting) describe the fields.

Run it locally first.

```
export OPENROUTER_API_KEY="sk-or-..."
node scripts/run-evals.mjs --samples 3
```

Each dot is a sample that passed and each `x` is one that failed, so you can see which case fails intermittently instead of only the final pass rate.

```
PASS  refund-window  ...
PASS  refund-exception  ...
PASS  escalation  ...

pass rate 1.00 against threshold 0.9
9 calls in <seconds>s, cost $<cost> on anthropic/claude-sonnet-5
```

A case counts as passing when the majority of its samples pass, so `..x` is still a `PASS`.

Now add the second job to `.github/workflows/eval-gate.yml`, below the `changes` job.

```
  eval-gate:
    needs: changes
    if: needs.changes.outputs.agent == 'true'
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0
        with:
          node-version: '24'
      - name: Run fixed eval set
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: node scripts/run-evals.mjs --samples 3 --threshold 0.9
```

The `if:` line reads the output from the `changes` job, and it is what stops the eval from running on pull requests that cannot have broken the agent. `timeout-minutes: 15` stops a hung provider from holding a runner for the [default six hours](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idtimeout-minutes). Each action is pinned to a full commit SHA, with the release it corresponds to in a trailing comment. A tag such as `v4` can be moved to point at new code, and this job holds your API key, so pinning to the SHA means the code that runs cannot change without a change in your repository. [GitHub’s security hardening guide](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions#using-third-party-actions) recommends the same.

Before the gate can block anything, do three things.

- Add your key as a repository secret under Settings > Secrets and variables > Actions, named `OPENROUTER_API_KEY`.
- Open a pull request that touches `prompts/` so the workflow runs once.
- Add both `changes` and `eval-gate` as [required status checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging) in your branch protection rules.

The third step is what turns the eval into a gate. Without it, a failing eval shows a red X on the pull request, but the pull request can still merge. Requiring `changes` as well covers the case where the filter job itself fails, for example on a checkout error. GitHub then skips `eval-gate`, and a skipped job counts as passing, so with only `eval-gate` required a prompt change could merge without being evaluated. With `changes` required too, the failed filter job blocks the merge. An unrelated pull request still merges, because `changes` passes and `eval-gate` is skipped.

With the exception of `GITHUB_TOKEN`, [GitHub does not pass secrets to workflows triggered from a forked repository](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions), so a pull request from a fork fails on a missing key. If your repository accepts fork contributions, run the eval on push to `main` as well, so a change that arrived through a fork is still checked. If you need a record of what a merge-blocking run checked, upload the run output as a workflow artifact.

The gate now runs on every pull request that can break the agent. It still uses a threshold nobody has justified, so Step 4 measures one.

### Step 4: Measure the threshold

Run the eval set six times against your unchanged `main` branch. Change nothing between the runs. Write down the lowest pass rate you see. You want the worst run rather than the typical one, so run the set more times if you can afford it. That lowest pass rate is your floor, and you set your threshold at or below it.

With three cases, one case failing on one of those six runs gives a floor of 0.67. Against a threshold of 0.9, that run is a blocked pull request with no regression behind it.

When your floor is low, work through these three checks in order.

First, look at your own assertion. The `escalation` case above accepts any of `human`, `person`, `our team`, or `specialist`. A version that requires the literal string `human` fails every time the model writes “a person” instead, and the prompt does not stop it from doing that. Check your assertions before anything else, every time.

Second, check whether your determinism settings do anything. Setting `temperature` to zero and fixing a `seed` only helps when the model supports those parameters. The command below prints the parameters a model supports, so you can see whether `temperature` and `seed` are in the list.

```
curl -s "https://openrouter.ai/api/v1/models" \
  | jq -r '.data[] | select(.id=="anthropic/claude-sonnet-5") | .supported_parameters'
```

[Claude Sonnet 5](https://openrouter.ai/anthropic/claude-sonnet-5) lists neither of them, which is why the script above does not send them. Our [Claude Sonnet 5 migration guide](https://openrouter.ai/docs/cookbook/evaluate-and-optimize/model-migrations/sonnet-5) says that `temperature`, `top_p`, and `top_k` are silently ignored for that model. On 18 September 2026, the catalog listed 445 models, and 267 of them listed both `seed` and `temperature`. The remaining 178, about two in five, listed one of them or neither. This command counts the models that list both, and you can re-run it for a current figure.

```
curl -s "https://openrouter.ai/api/v1/models" | jq '
  [.data[] | select(.supported_parameters | index("seed") and index("temperature"))] | length'
```

If your model does list them, add `temperature: 0` and `seed: 42` to the request body and set `provider.require_parameters: true` beside `order`. With the default `require_parameters: false`, a provider that does not support every parameter in the request can still receive it and ignore the parameters it does not know. With `require_parameters: true`, the request is only routed to providers that support all of them.

Third, whatever variation survives those two checks is real, and you absorb it by sampling. Raise `--samples` until the floor stops moving. Three is a reasonable default, and it already costs three times a single run, so measure before raising it to five.

A small set has one property worth knowing about. With three cases the pass rate can only be 0, 0.33, 0.67, or 1.00, so a threshold of 0.9 means all three cases must pass. That is another reason to grow the set toward 20 or more cases.

When a pull request fails the gate by a single case, run the same eval against `main`. If `main` fails too, the failure is noise, and you need more samples or a lower threshold. If `main` passes, treat the failure as a regression in the pull request.

That is the complete gate. The rest of this guide covers what to do when a string check is no longer enough, and when a plain script is worth trading for a platform that stores your run history.

## Test an agent that calls tools with Ori Eval

The script above sends one message and reads one reply. If your agent calls tools, that is not enough. A string check cannot tell you whether the agent called the right tool, or called an expensive tool it should have left alone.

[Ori Eval](https://openrouter.ai/docs/guides/ori/eval) is our eval harness for agents. A harness is the program that runs your evals. It runs the agent, records what the agent did, and checks the result against your assertions. Ori evals are `.eval.ts` files, and the assertions are about what the agent did.

```
import { test } from 'bun:test';
import { assertModelIsLive, setupAgent, setupJudge } from 'ori/eval';

const MODEL = 'anthropic/claude-sonnet-5';
await assertModelIsLive(MODEL);

const agent = setupAgent({ model: MODEL });

// Grade with a different model family than the one under test.
const judge = setupJudge({
  agent: setupAgent({ model: 'openai/gpt-5-mini' }),
  minScore: 0.8,
});

test('looks up the order before quoting the refund policy', async () => {
  const run = await agent.run('Can I refund order #1234? I bought it 60 days ago.');
  run.tool('lookup_order').toBeCalled();
  run.tool('issue_refund').toNotBeCalled();
  run.toComplete();
  await judge.autoEvals({
    criteria: 'Cites the 14-day window and does not invent exceptions.',
    run,
  });
});
```

`run.tool(...)` is the part the plain script cannot do. `assertModelIsLive` fails the run with a clear message if the slug leaves the catalog, so the file fails loudly instead of testing a model that no longer exists. Before you let the judge fail builds, grade a sample of the same runs yourself and compare your verdicts with the judge’s. Anthropic’s guide recommends [calibrating LLM graders against human experts](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) for the same reason.

Ori runs eval files with [Bun](https://bun.sh), and when `CI` is true it does not install Bun for you. In a workflow, you install Bun, then download a pinned Ori release and verify its checksum before running it, because the job holds your API key. With `OPENROUTER_API_KEY` set, Ori does not need `ori login` in CI.

```
      - uses: oven-sh/setup-bun@0c5077e51419868618aeaa5fe8019c62421857d6 # v2.2.0
      - name: Install Ori
        env:
          ORI_RELEASE: cli-0.15.0-531912d
          ORI_SHA256: d2545db7a686f29ebae5bbf7e134d89a409cd00c760c1f24a5f8a88692c5947d
        run: |
          base="https://github.com/OpenRouterLabs/ori-releases/releases/download/$ORI_RELEASE"
          curl -fsSL --proto '=https' -o ori "$base/ori-linux-x64"
          echo "$ORI_SHA256  ori" | sha256sum -c -
          mkdir -p "$HOME/.local/bin"
          install -m 0755 ori "$HOME/.local/bin/ori"
          echo "$HOME/.local/bin" >> "$GITHUB_PATH"
      - name: Run pinned agent eval
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: ori eval --report eval-report.md
```

`ORI_RELEASE` and `ORI_SHA256` name the stable release and its `ori-linux-x64` digest at the time of writing. Update both together when you move to a newer release. Downloading a checksum file from the same release page would not add anything, because anyone who can replace the binary can replace the checksum beside it. Keeping the digest in your workflow means a changed binary fails the `sha256sum` check.

`ori eval` finds every `*.eval.ts` file below the current directory and hands them to `bun test`. Its exit code is the exit code of `bun test`, so a failing eval fails the job. `--report` writes a Markdown report you can upload as an artifact or append to the job summary.

Every Ori run sends requests to real models and costs money, so keep these evals out of the job that runs on every commit. The [Ori Eval documentation](https://openrouter.ai/docs/guides/ori/eval) covers running them from a job a person starts or on a schedule.

## Compare a plain script with eval platforms

The script above is a complete eval gate. A platform adds dashboards, run history you can chart, and a way for people outside engineering to read results without opening CI logs.

Approach

How it runs in CI

Lock-in

Best fit

Plain script

You write the CI step and the exit-code logic yourself

None, because it is your code

One or two eval sets with full control over scoring

Ori Eval

ori eval

in a job, exiting non-zero when an eval fails

Low, since eval files stay in your repository and run against any model in the catalog

Tool-calling agents, or comparing models on your own agent

DeepEval

deepeval test run

under pytest, with

assert_test()

raising below a per-metric threshold

Low, because the scoring library is open source

Ready-made metrics such as answer relevancy and task completion

Braintrust

A published GitHub Action that runs evals and posts a summary comment on the pull request

Moderate, since scoring history lives in their platform

Score changes surfaced in review rather than in CI logs

Arize

client.experiments.run()

from the SDK as a plain Python step, with a sample workflow in their docs

Moderate, since the experiments API is theirs

Repositories already using Arize for observability

Galileo

run_experiment

from the SDK, or

create_experiment

for multi-turn agents

Moderate, as metrics and history are platform-native

Hosted dashboards over eval history

Start with the script. Your eval set and scoring logic stay in your repository either way, and you can point a platform at them later. Moving off a platform means porting scoring logic written against its SDK and losing the run history stored there.

## Common failure modes

The first is cost. It is cases multiplied by samples multiplied by how often relevant pull requests are opened. The script prints the cost of each run from the `usage.cost` field, so read that line before you raise `--samples` or grow the set. Long prompts and a grading model move the figure a lot, so measure your own set. Current prices are on the [pricing page](https://openrouter.ai/pricing).

The second is speed. Every minute the gate adds is added to every pull request that touches a prompt. Run the samples concurrently. The script’s `--concurrency` flag defaults to 8, so the nine calls in the example run in two waves instead of nine sequential requests, and the difference grows with the size of your set.

The third is a gate that fails for the wrong reason. A provider timeout is not a regression, which is why the script exits with 2 when the eval could not run and 1 when the agent got worse, and prints a GitHub annotation saying which happened.

The fourth is a threshold above the floor. A threshold you did not measure blocks pull requests that changed nothing, and the only ways past it are an admin merge or a lower threshold set under time pressure. Set the threshold from the floor you measured in Step 4.

## Frequently asked questions

### How do you add LLM evals to a CI/CD pipeline?

Keep a fixed, versioned eval set in the repository, run it in a CI job that scores output against a threshold, and mark that job and the path-filter job that gates it as required status checks in branch protection. The job’s exit code decides the outcome, the same way a failing unit test does.

### What is a fixed eval set, and why does it need to stay versioned with the code?

A fixed eval set is a checked-in list of test inputs and grading criteria that changes only through a reviewed pull request. If it lives outside the repository, it drifts out of sync with the prompts and stops testing what shipped.

### Can you block a pull request from merging based on an eval score?

Yes. A plain script that exits non-zero below a threshold is enough, as long as the job that runs it is a required status check. Put the prompts and the eval set behind a `CODEOWNERS` rule with “Require review from Code Owners” enabled, so weakening the test that caught a regression also needs a review.

### What is the difference between LLM-as-a-judge and running evals in CI?

LLM-as-a-judge is a scoring method for one run, where a second model grades the answer. Running evals in CI is the pipeline around any scoring method. It decides when the cases run, against which fixed set, and what happens to the pull request when the score is low.

### Do evals need to run on every commit, or only on prompt and agent-logic changes?

Only on changes that touch prompts, agent logic, tool schemas, or the eval set. Filter at the job level rather than the workflow level. GitHub reports a job skipped by an `if` condition as a passing check, while a workflow skipped by a path filter leaves a required check pending and blocks the merge.

### How much does running LLM evals on every PR cost in tokens and CI minutes?

Cost is the case count multiplied by the samples per case multiplied by how often relevant pull requests are opened. The script in this guide prints the cost of each run from the `usage` field in the API response, so you can measure your own set. Current model prices are on the [pricing page](https://openrouter.ai/pricing).

### What tools support gating a PR on a fixed eval set before merge?

A plain script with a threshold check is enough on its own. Ori Eval, DeepEval, Braintrust, Arize, and Galileo add reporting, run history, or agent-specific assertions on top of the same exit-code pattern.

### How do you handle a flaky or non-deterministic eval blocking a good PR?

Check your own assertion first, because a single literal string that the model paraphrases is a common cause. Then sample each case several times and take a majority verdict. Check the model’s `supported_parameters` on the [OpenRouter models endpoint](https://openrouter.ai/docs/guides/overview/models) before relying on `temperature` or `seed`, because models that do not list them ignore them.

### Is LLM-as-a-judge reliable enough to fail a build on?

It can be, if you measure the judge rather than assume it. Grade a sample of runs yourself and compare your verdicts with the judge’s, and pair the judge with plain assertions so a build never fails on one unverified model call.

## Conclusion

In this guide, you wrote an eval set for a support agent, scored it with a script that exits non-zero below your threshold, measured your own floor across repeated runs, and made the job a required check. A fixed eval set, a measured threshold, and a job-level trigger give your prompts and agent logic the same protection that unit tests give your code. To extend the gate to an agent that calls tools, start with the [Ori Eval documentation](https://openrouter.ai/docs/guides/ori/eval).

## References

- [Ori Eval](https://openrouter.ai/docs/guides/ori/eval)
- [Provider selection](https://openrouter.ai/docs/guides/routing/provider-selection)
- [Models and supported_parameters](https://openrouter.ai/docs/guides/overview/models)
- [Usage accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting)
- [Claude Sonnet 5 migration guide](https://openrouter.ai/docs/cookbook/evaluate-and-optimize/model-migrations/sonnet-5)
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Workflow syntax for GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Skipping workflow runs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs)
- [Using conditions to control job execution](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions)
- [Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions)
- [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [dorny/paths-filter](https://github.com/dorny/paths-filter)
