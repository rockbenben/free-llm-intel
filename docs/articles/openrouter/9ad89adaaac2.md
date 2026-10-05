---
vendor: openrouter
title: 如何在 CI 中控制 LLM 评估的 Pull 请求
original_title: How to Gate Pull Requests on LLM Evals in CI
url: https://openrouter.ai/blog/tutorials/how-to-gate-pull-requests-on-llm-evals-in-ci
date: 2026-10-01
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: df3dfab1f6bd
translator: agent
---

# 如何在 CI 中控制 LLM 评估的 Pull 请求

OpenRouter ·10/1/2026

改一行客服 agent 的系统提示词，就可能上线一个告诉客户退款期限是 30 天、而你的政策写的是 14 天的 agent。普通 CI 流水线里没有任何环节检查模型说了什么——构建通过，第一个看到错误答案的人是顾客。

用一固定评测集来给 pull request 设闸门，机制和"单元测试失败就拦住"完全一样：测试用例存在仓库里，提示词变更时运行它们，失败太多就阻止合并。

本指南里，你会为一个客服 agent 写一套评测集，用一个调 OpenRouter 的脚本来评分；然后测量什么都不改时结果在运行之间的波动，最后把脚本接进 GitHub Actions 作为一个必需的 status check。

## 太长不看

- 固定的评测集是一份提交进你仓库的测试用例列表，只能通过经过评审的 pull request 改动。
- 过滤放在 job 级别而不是 workflow 级别。被 `if` 条件跳过的 job，GitHub 报为通过的 check；而被路径过滤跳过的 workflow 会让必需 check 一直挂在 Pending、阻止合并。
- 评测脚本在通过率低于你的阈值时以非零码退出，这个退出码就是让 job 失败的东西。
- 阈值要从"对着未改动分支重复运行"里量出来，别拍一个严格数字。
- `temperature` 和 `seed` 只在 `supported_parameters` 里列了它们的模型上有效。多次采样加多数投票对所有模型都有效。

![GitHub Actions 评测闸门示意图：pull request 触发一个跑路径过滤的 changes job、一个要么运行固定评测集要么被跳过的 eval-gate job；达到阈值或被跳过则允许合并，低于阈值则阻止合并](https://openrouter.ai/blog/images/eval-gate-job-level-path-filter.png)

## CI 里的 LLM 评测是什么意思

一个 eval 就是给 agent 的一条测试用例：有输入，有一条判断模型回答是否可接受的规则。固定评测集就是这些用例的列表，提交在你的仓库里，只能通过经过评审的 pull request 改动。"流水线"部分是你的 CI 配置：它决定用例什么时候运行、失败太多时对 pull request 做什么。

"判断模型回答好不好"本身是另一个问题，一个选项是把它交给另一个模型当评分者——这项技术叫 LLM-as-a-judge，我们在[LLM 裁判指南](https://openrouter.ai/blog/tutorials/llm-as-a-judge-evaluate-ai-agents/)里讲。[工具调用循环指南](https://openrouter.ai/blog/tutorials/build-tool-calling-agent-loop/)讲 agent 本体怎么建。本指南讲的是这两者中间的那条流水线。

## 设闸门之前需要什么

三样东西就位，闸门才能给你有用的信号。

- **一份固定、有版本的评测集。**Anthropic 的 agent 评测指南建议以[从真实失败中抽取的 20 到 50 个简单任务](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)作为起始集。这里我们只用三条，让示例保持短小。
- **一个评分方法和一个阈值。**评分方法把一条回答变成可计数的通过/失败；阈值作用于整次运行。本指南用字符串断言，rubric 或裁判模型同样可行。
- **足够可重复、值得信任的运行。**闸门应当拦回归，不拦噪声。多次采样加多数投票对所有模型都有效。`temperature` 和 `seed` 只在列出它们的模型上有帮助，依赖之前先查[模型的 `supported_parameters`](https://openrouter.ai/docs/guides/overview/models)。

你还需要一个导出为 `OPENROUTER_API_KEY` 的 [OpenRouter API key](https://openrouter.ai/keys)、Node 20 或更新版本，以及 [jq](https://jqlang.org/)。

## 四步搭起闸门

这四步走完，一个动了你提示词的 pull request 会自动跑你的评测集，分数掉了就合不进去。

- 只在可能弄坏 agent 的变更上触发评测。
- 评测集放进仓库，与它所测的提示词放在一起。
- 写好 CI job 要跑的那个脚本。
- 量出决定拦不拦合并的那个阈值。

### 第 1 步：只在相关变更上触发

提示词、agent 逻辑、工具 schema、评测集、评测脚本或 workflow 本身变化时跑评测。后两个最容易被漏掉。过滤里少了它们的话，一个改坏评分逻辑或动了闸门的 pull request 会跳过评测、未经测试就合并。

做法是两个 job。第一个永远运行：把 pull request 改动的文件与一份路径清单比对，有匹配就输出 `true`，否则 `false`。第二个 job 跑评测，只在第一个返回 `true` 时启动。

`.github/workflows/eval-gate.yml` 从 workflow 头部和第一个 job 开始。`agent:` 下列的路径请按你自己的仓库改。

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

`concurrency` 配 `cancel-in-progress`：同一分支再次 push 时取消上一次运行，连着推好几次 pull request 的开发者不用为每次 push 付一遍评测钱。

这里可能出两个问题。

第一个是"绿勾但后面根本没跑评测"。第一个 job 返回 `false` 时，GitHub 会跳过评测 job，而[被跳过的 job 满足必需的 status check](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging)。这正是让无关 pull request 能通过的原因。但它也意味着写错一个 glob、check 就在一个用例都没跑的情况下通过；`changes` job 直接失败也是同样效果——GitHub 会跳过 `needs` 依赖失败的 job。第 3 步会把 `changes` 也设为必需 check，从而堵上第二个洞。第一个问题：让一次提示词变更走一遍流程，打开运行日志确认评测真的跑了。

第二个问题是过滤放的位置。别把它上移到 workflow 级的 `on.pull_request.paths`。GitHub 关于[跳过 workflow 运行](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs)的文档写明：workflow 被路径过滤跳过时，"与该 workflow 关联的 checks 将保持在 'Pending' 状态"，要求这些 checks 的 pull request 就合不进去。

### 第 2 步：把评测集放进仓库

评测集与它所测的提示词同仓库。有人改提示词时，对它的测试在同一个 pull request 里一起改，一个评审人同时看到两边。

四个文件并排放着：

```
your-repo/
  .github/workflows/eval-gate.yml  -> the workflow from Step 1
  prompts/support-agent.md         -> the system prompt
  eval-sets/support-agent.json     -> the cases that test it
  scripts/run-evals.mjs            -> the script from Step 3
```

评测集存成 `eval-sets/support-agent.json`。每个用例有输入、回答必须包含的字符串、和必须不包含的字符串。`mustMention` 的条目也可以是列表（如第三个用例），此时回答只需包含其中任意一个。单个字面字符串，会在模型写"a person"或"our team"而不是你期望的"human"时失败——凡是能接受多种措辞的地方，用列表。

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

这些用例所测的提示词就在旁边：`prompts/support-agent.md`。

```
You are a support agent for a digital downloads store.
The refund window is 14 days from purchase. There are no exceptions to it.
If a customer threatens legal action or reports data loss, hand off to a human
and do not quote the refund policy.
Answer in at most three sentences.
```

从三个用例开始。agent 在生产里每做错一件事，就加一条。

把 `prompts/` 和 `eval-sets/` 都放到 [CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) 规则后面，并在分支保护里打开 "Require review from Code Owners"。否则绕过失败闸门最快的办法，就是放宽抓住回归的那个测试。光有 `CODEOWNERS` 文件只会请求评审，不会阻止合并。

### 第 3 步：写 CI job 要跑的脚本

job 只跑一个脚本，通过率低于阈值时以非零码退出。这个退出码就是 CI 拦合并所需的全部。

脚本加载评测集，把每个用例发给模型，检查回答，并以告诉 CI 发生了什么的状态码退出。它只用 Node 内建模块，什么都不用装。存成 `scripts/run-evals.mjs`。

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

脚本在调模型之外做了三件事。

评测集为空或选项不合法时它拒绝运行，在发出任何请求之前以 2 退出。没有这些检查：被误替换成 `[]` 的评测集会算出 `NaN` 通过率，而 `NaN < threshold` 是 false，零次评估反而通过了闸门。`--threshold` 写 `90%` 或负数 `--samples` 也是同样的漏洞；空的 `--threshold` 会变成 0——没有通过率能低于它——所以检查也拒绝 0。

每个用例跑若干次，每次运行是一个样本，样本之间取多数裁决——同一提示词并不总产生同一个回答。

它还将每个请求路由到单一提供商。像 `anthropic/claude-sonnet-5` 这样的模型 slug 在 OpenRouter 上由多家提供商服务，写作时其端点包括 Anthropic、Amazon Bedrock、Azure 和 Google。不设路由偏好的话，同一评测的两次运行可能落到两家提供商，它们答案之间的差异看起来就像提示词回归。`provider.order` 是提供商 slug 的优先级列表，`allow_fallbacks: false` 告诉我们列表之外一家都不试。列出的提供商失败时请求直接失败、不转备份，脚本以 2 退出。两个字段见[提供商选择文档](https://openrouter.ai/docs/guides/routing/provider-selection)。钉定绑定于你指定的模型：把 `--model` 换成另一家的模型时，`order` 也要一起改，否则没有提供商匹配、每个请求都会失败。

最后一行打印的成本来自每个非流式响应里的 `usage` 对象，字段说明见[用量核算文档](https://openrouter.ai/docs/cookbook/administration/usage-accounting)。

先本地跑一遍。

```
export OPENROUTER_API_KEY="sk-or-..."
node scripts/run-evals.mjs --samples 3
```

每个点是一个通过的样本、每个 `x` 是一个失败的样本——这样你能看到哪个用例间歇性失败，而不只是最终通过率。

```
PASS  refund-window  ...
PASS  refund-exception  ...
PASS  escalation  ...

pass rate 1.00 against threshold 0.9
9 calls in <seconds>s, cost $<cost> on anthropic/claude-sonnet-5
```

一个用例在其多数样本通过时算通过，所以 `..x` 仍是 `PASS`。

现在把第二个 job 加进 `.github/workflows/eval-gate.yml`，在 `changes` job 之下。

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

`if:` 这一行读取 `changes` job 的输出，正是它让评测不在"不可能弄坏 agent"的 pull request 上运行。`timeout-minutes: 15` 防止一个卡住的提供商占住 runner 达[默认的六小时](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idtimeout-minutes)。每个 action 都钉到完整 commit SHA，尾注释里写着对应的 release。像 `v4` 这样的 tag 可以被移动到指向新代码，而这个 job 持有你的 API key——钉 SHA 意味着运行的代码不经你仓库的变更就无法改变。[GitHub 的安全加固指南](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions#using-third-party-actions)也是同样的建议。

闸门能拦东西之前，先做三件事。

- 把你的 key 以 repository secret 加进 Settings > Secrets and variables > Actions，名字 `OPENROUTER_API_KEY`。
- 开一个触碰 `prompts/` 的 pull request，让 workflow 先跑一次。
- 在分支保护里把 `changes` 和 `eval-gate` 都加为[必需 status checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging)。

第三步把评测变成了闸门。没有它，失败的评测只在 pull request 上挂个红叉，照样能合并。`changes` 同样设为必需，覆盖的是过滤 job 自身失败的情形（比如 checkout 报错）：GitHub 于是跳过 `eval-gate`，被跳过的 job 算通过——只把 `eval-gate` 设为必需时，一次提示词变更可以未经评估就合并。`changes` 也是必需的之后，过滤 job 失败就会阻止合并。无关的 pull request 照样能合，因为 `changes` 通过、`eval-gate` 被跳过。

除 `GITHUB_TOKEN` 外，[GitHub 不会把 secrets 传给由 fork 仓库触发的 workflow](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions)，fork 来的 pull request 会因缺 key 失败。如果你的仓库接受 fork 贡献，请在 push 到 `main` 时也跑一遍评测，让经由 fork 进来的变更最终仍被检查。需要留存拦发布的运行检查了什么时，把运行输出上传为 workflow artifact。

闸门现在会在每个可能弄坏 agent 的 pull request 上运行。但它用的还是一个没人论证过的阈值，第 4 步就是去量一个。

### 第 4 步：测量阈值

对着未改动的 `main` 分支把评测集跑六次，中间什么都不改。记下你看到的最低通过率。你要的是最差那次而不是典型值，预算允许就多跑几轮。那个最低通过率就是你的地板，阈值设在此处或以下。

只有三个用例时，六次运行里一次挂一个用例，地板就是 0.67。对着 0.9 的阈值，那一次运行就是一个没有任何回归支撑、却被拦下的 pull request。

地板很低时，按顺序过这三关。

第一，检查你自己的断言。上面 `escalation` 用例接受 `human`、`person`、`our team`、`specialist` 任意一个。要求字面 `human` 的版本，会在模型每次写"a person"时失败，而提示词并没有阻止它这么写。任何时候，先检查断言。

第二，检查你的确定性设置到底有没有用。`temperature` 归零、固定 `seed`，只在模型支持这些参数时才有意义。下面的命令打印模型支持的参数，看看 `temperature` 和 `seed` 在不在里面。

```
curl -s "https://openrouter.ai/api/v1/models" \
  | jq -r '.data[] | select(.id=="anthropic/claude-sonnet-5") | .supported_parameters'
```

[Claude Sonnet 5](https://openrouter.ai/anthropic/claude-sonnet-5) 两个都没列——这就是上面的脚本不发它们的原因。我们的 [Claude Sonnet 5 迁移指南](https://openrouter.ai/docs/cookbook/evaluate-and-optimize/model-migrations/sonnet-5)写明该模型会静默忽略 `temperature`、`top_p` 和 `top_k`。2026 年 9 月 18 日，目录列有 445 个模型，其中 267 个同时列了 `seed` 和 `temperature`，其余 178 个（约五分之二）只列其一或都不列。下面这条命令统计同时列出两者的模型数，可以重跑取当前值。

```
curl -s "https://openrouter.ai/api/v1/models" | jq '
  [.data[] | select(.supported_parameters | index("seed") and index("temperature"))] | length'
```

你的模型如果确实列了它们，就在请求体里加 `temperature: 0` 和 `seed: 42`，并在 `order` 旁边设 `provider.require_parameters: true`。默认的 `require_parameters: false` 下，不支持请求中全部参数的提供商仍可能收到请求并忽略它不认识的参数；设为 `true` 后，请求只路由到支持全部参数的提供商。

第三，过了这两关仍然存在的波动就是真实的，靠采样吸收它：提高 `--samples` 直到地板不再移动。3 是合理的默认值，它已经是一次运行三倍的钱——提到 5 之前先测。

小集合有一个值得知道的性质。三个用例时通过率只能是 0、0.33、0.67 或 1.00，阈值 0.9 等于要求三个全过。这也是把集合养到 20 条以上的另一个理由。

某个 pull request 因一个用例的差异被闸门拦下时，拿同一评测对 `main` 跑一遍。`main` 也挂，失败就是噪声——加样本或降阈值。`main` 通过，就把它当作该 pull request 里的回归处理。

闸门到这里就完整了。指南剩下的部分讲：字符串检查不再够用时的出路，以及什么时候值得把普通脚本换成存运行历史的平台。

## 用 Ori Eval 测试会调工具的 agent

上面的脚本发一条消息、读一条回复。如果你的 agent 会调工具，这不够：字符串检查告诉不了你 agent 是否调对了工具，或是否动了那个本不该碰的昂贵工具。

[Ori Eval](https://openrouter.ai/docs/guides/ori/eval) 是我们面向 agent 的评测 harness。harness 就是运行你评测的那个程序：跑 agent、记录 agent 做了什么、再对照你的断言检查结果。Ori 的 eval 是 `.eval.ts` 文件，断言关于 agent 做了什么。

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

`run.tool(...)` 是普通脚本做不到的那部分。`assertModelIsLive` 在 slug 下架时以清晰的消息让运行失败，文件大声报错，而不是去测一个已不存在的模型。在让裁判有权弄挂构建之前，先自己评一批同样的运行、把你的裁决和裁判的对比——Anthropic 的指南出于同样的原因建议[用人类专家校准 LLM 评分器](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)。

Ori 用 [Bun](https://bun.sh) 跑 eval 文件，`CI` 为 true 时它不会替你装 Bun。在 workflow 里，你先装 Bun，再下载钉住版本的 Ori 发布并校验 checksum 后才运行——因为 job 持有你的 API key。设了 `OPENROUTER_API_KEY`，Ori 在 CI 里不需要 `ori login`。

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

`ORI_RELEASE` 和 `ORI_SHA256` 是写作时的稳定版本名和它 `ori-linux-x64` 产物的摘要，升级到新版本时两个一起改。从同一发布页下载 checksum 文件并不能增加什么——能替换二进制的人也能替换旁边的 checksum。摘要写在你的 workflow 里，被替换的二进制就过不了 `sha256sum` 检查。

`ori eval` 会找到当前目录下所有 `*.eval.ts` 文件交给 `bun test`。它的退出码就是 `bun test` 的退出码，一个 eval 失败就让 job 失败。`--report` 写一份 Markdown 报告，可以上传为 artifact 或追加到 job summary。

每次 Ori 运行都会给真实模型发请求、花真钱，所以把这些 eval 放在"每个 commit 都跑"的 job 之外。[Ori Eval 文档](https://openrouter.ai/docs/guides/ori/eval)讲了由人启动或按计划跑的方式。

## 普通脚本与评测平台对比

上面的脚本就是一个完整的评测闸门。平台加的是面板、可以画成图的历史运行，以及让工程之外的人不开 CI 日志就能读结果的途径。

方案

在 CI 里怎么跑

锁定程度

最适合

普通脚本

你自己写 CI step 和退出码逻辑

无，因为都是你的代码

一两个评测集、对评分要完全掌控

Ori Eval

job 里跑 `ori eval`，eval 失败时非零退出

低：eval 文件留在你仓库、可对着目录里任何模型运行

工具调用 agent，或在你自己的 agent 上比较模型

DeepEval

pytest 下 `deepeval test run`，`assert_test()` 在单指标阈值下抛错

低：评分库开源

拿来即用的指标（答案相关性、任务完成度等）

Braintrust

一个发布的 GitHub Action 跑 eval 并在 pull request 上发 summary 评论

中：评分历史存在其平台里

在评审中呈现分数变化、而不是埋在 CI 日志里

Arize

SDK 的 `client.experiments.run()` 作为普通 Python step，文档里有示例 workflow

中：experiments API 是人家的

已经在用 Arize 做可观测性的仓库

Galileo

SDK 的 `run_experiment`，多轮 agent 用 `create_experiment`

中：指标与历史平台原生

评测历史要带托管面板

从脚本开始。评测集和评分逻辑无论如何都留在你的仓库里，之后随时可以把平台对准它们。迁离一个平台，意味着要移植按其 SDK 写的评分逻辑，并丢掉存在那里的运行历史。

## 常见故障模式

第一个是成本。它等于用例数乘样本数乘"相关 pull request 的开单频率"。脚本会从 `usage.cost` 字段打印每次运行的成本，抬 `--samples` 或扩集合之前先读那一行。长提示词和一个评分模型会让数字动很多，请按你自己的集合测量。当前价格在[定价页](https://openrouter.ai/pricing)。

第二个是速度。闸门加的每一分钟，都加在每个触碰提示词的 pull request 上。样本要并发跑：脚本的 `--concurrency` 默认 8，示例里那九个调用分两波跑完而不是九个串行请求，并且集合越大差距越大。

第三个是因错误原因失败的闸门。提供商超时不是回归——这就是脚本在评测跑不起来时以 2 退出、agent 变差时以 1 退出，并打印一条 GitHub annotation 说明发生了哪种。

第四个是阈值定在地板之上。没测出来的阈值会拦下什么都没改的 pull request，唯一的出路是管理员强合，或在时间压力下把阈值调低。请按第 4 步量出的地板设阈值。

## 常见问题

### 怎么把 LLM 评测加进 CI/CD 流水线？

固定、有版本的评测集留在仓库里；CI job 运行它、对着阈值给输出打分；把该 job 和为它过滤路径的 job 都标为分支保护里的必需 status check。job 的退出码决定结果，和失败的单元测试一样。

### 什么是固定评测集，为什么它必须和代码一起管版本？

固定评测集是一份签入的测试输入与评分标准清单，只能通过经过评审的 pull request 改动。住在仓库之外的评测集，会和提示词脱节，停止测试真正上线的东西。

### 能基于评测分数阻止一个 pull request 合并吗？

能。一个低于阈值就以非零码退出的普通脚本就够了——前提是跑它的 job 是必需 status check。把提示词和评测集放到 `CODEOWNERS` 规则后并启用 "Require review from Code Owners"，放宽那个抓住回归的测试也就多需要一次评审。

### LLM-as-a-judge 和在 CI 跑评测有什么区别？

LLM-as-a-judge 是单次运行的评分方法——用第二个模型给答案打分。在 CI 跑评测是包在任何评分方法外面的流水线：它决定用例什么时候跑、对着哪个固定集跑、分数低了时对 pull request 做什么。

### 评测是每个 commit 都要跑，还是只在提示词和 agent 逻辑变更时跑？

只在触碰提示词、agent 逻辑、工具 schema 或评测集的变更上跑。过滤放在 job 级而不是 workflow 级：被 `if` 条件跳过的 job 被 GitHub 报为通过的 check，而被路径过滤跳过的 workflow 会让必需 check 挂着 Pending、阻止合并。

### 每个 PR 都跑 LLM 评测要花多少 token 和 CI 分钟？

成本 = 用例数 x 每用例样本数 x 相关 pull request 的开单频率。本指南的脚本会从 API 响应的 `usage` 字段打印每次运行的成本，量你自己的集合即可。当前模型价格在[定价页](https://openrouter.ai/pricing)。

### 有哪些工具支持"合并前用固定评测集拦 PR"？

一个带阈值检查的普通脚本本身就够。Ori Eval、DeepEval、Braintrust、Arize 和 Galileo 在同一退出码模式之上加报告、运行历史或 agent 专属断言。

### 评测不稳定或非确定性时，怎么避免它误伤好的 PR？

先检查你自己的断言——模型会改写的单个字面字符串是最常见的原因。然后每个用例多次采样取多数裁决。依赖 `temperature` 或 `seed` 之前，先到 [OpenRouter models 端点](https://openrouter.ai/docs/guides/overview/models)查模型的 `supported_parameters`，不列出它们的模型会直接忽略。

### LLM-as-a-judge 可靠到可以让它弄挂构建吗？

测量过裁判、而不是假设它，就可以。自己评一批运行、把你的裁决和裁判对比；再给裁判配上普通断言，让构建永远不会只栽在一次未经验证的模型调用上。

## 结论

本指南里，你为客服 agent 写了一套评测集，用低于阈值即非零退出的脚本评分，在重复运行中量出了自己的地板，并把这个 job 变成了必需 check。固定评测集、测出来的阈值、job 级触发——给你的提示词和 agent 逻辑上了单元测试给代码的同级保护。要把闸门扩展到会调工具的 agent，从 [Ori Eval 文档](https://openrouter.ai/docs/guides/ori/eval)开始。

## 参考资料

- [Ori Eval](https://openrouter.ai/docs/guides/ori/eval)
- [提供商选择](https://openrouter.ai/docs/guides/routing/provider-selection)
- [模型与 supported_parameters](https://openrouter.ai/docs/guides/overview/models)
- [用量核算](https://openrouter.ai/docs/cookbook/administration/usage-accounting)
- [Claude Sonnet 5 迁移指南](https://openrouter.ai/docs/cookbook/evaluate-and-optimize/model-migrations/sonnet-5)
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Workflow syntax for GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [跳过 workflow 运行](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs)
- [用条件控制 job 执行](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions)
- [在 GitHub Actions 中使用 secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions)
- [关于受保护分支](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [关于 code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [dorny/paths-filter](https://github.com/dorny/paths-filter)
