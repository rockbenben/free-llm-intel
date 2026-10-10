---
vendor: openai
title: Codex 全面升级
original_title: Introducing upgrades to Codex
url: https://openai.com/index/introducing-upgrades-to-codex
date: 2026-10-02
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 39c898b50c12
---


2025年9月15日



# Codex 全面升级

Codex 现在运行更高效、性能更稳定，实时协作与独立任务处理能力显著提升，无论是在终端、IDE、网页，还是在手机上进行开发，均能随时使用。

$ npm i -g @openai/codex


***Update on September 23, 2025****: ** GPT‑5‑Codex is now available to developers using Codex via API key (in addition to being available to developers using Codex via their ChatGPT subscription). GPT‑5 Codex is available at the same price as GPT‑5, and is available in the Responses API only. The underlying model snapshot will be regularly updated. Check out the Codex *[*developer documentation*](http://platform.openai.com/docs/models/gpt-5-codex)* and *[*changelog*](https://developers.openai.com/codex/changelog)* for more details.*

Today, we’re releasing GPT‑5‑Codex—a version of GPT‑5 further optimized for agentic coding in Codex. GPT‑5‑Codex was trained with a focus on real-world software engineering work; it’s equally proficient at quick, interactive sessions and at independently powering through long, complex tasks. Its code review capability can catch critical bugs before they ship. GPT‑5‑Codex is available everywhere you use Codex—it’s the default for cloud tasks and code review, and developers can choose to use it for local tasks via Codex CLI and the IDE extension.

Since we first launched [Codex CLI](https://github.com/openai/codex) in April and [Codex⁠](https://openai.com/zh-Hans-CN/index/introducing-codex/) web in May, Codex has steadily evolved into a more effective coding collaborator. Two weeks ago, we unified Codex into a single product experience connected by your ChatGPT account, enabling you to move work seamlessly between your local environment and the cloud without losing context. Codex now works where you develop—in your terminal or IDE, on the web, in GitHub, and even in the ChatGPT iOS app. Codex is included with ChatGPT Plus, Pro, Business, Edu, and Enterprise plans.

With these updates, Codex moves closer to what we’ve been building toward all along—a teammate that understands your context, works alongside you, and reliably takes on work for your team.

## GPT‑5‑Codex

GPT‑5‑Codex is a version of GPT‑5 further optimized for agentic software engineering in Codex. It’s trained on complex, real-world engineering tasks such as building full projects from scratch, adding features and tests, debugging, performing large-scale refactors, and conducting code reviews. It’s more steerable, adheres better to [AGENTS.md](http://agents.md) instructions, and produces higher-quality code—just tell it what you need without writing long instructions on style or code cleanliness.

***SWE-Bench 验证：****在 GPT‑5 发布时及历史评估中，我们报告了 477 个 SWE-bench 验证任务的结果，因为有些任务无法在我们的基础设施中运行。我们已修复这个问题，现在可以报告全部 500 项任务的评估结果。*

***代码重构任务：****我们的代码重构评估包含来自大型、成熟代码库的重构式任务，包括 Python、Go 甚至 OCaml 中的任务。一个示例任务是*[*来自 Gitea 的以下拉取请求*](https://github.com/go-gitea/gitea/commit/fd7d83ace60258acf7139c4c787aa8af75b7ba8c)*，它更改了 232 个文件和 3,541 行代码，以将 ctx 变量贯穿应用程序逻辑。*

GPT‑5‑Codex adapts how much time it spends thinking more dynamically based on the complexity of the task. The model combines two essential skills for a coding agent: pairing with developers in interactive sessions, and persistent, independent execution on longer tasks. That means Codex will feel snappier on small, well-defined requests or while you are chatting with it, and will work for longer on complex tasks like big refactors. During testing, we’ve seen GPT‑5‑Codex work independently for more than 7 hours at a time on large, complex tasks, iterating on its implementation, fixing test failures, and ultimately delivering a successful implementation.

On OpenAI employee traffic, we see that for the bottom 10% of user turns sorted by model-generated tokens (including hidden reasoning and final output), GPT‑5‑Codex uses 93.7% fewer tokens than GPT‑5. Conversely, for the top 10%, GPT‑5‑Codex thinks more, spending twice as long reasoning, editing and testing code, and iterating.

GPT‑5‑Codex has been trained specifically for conducting code reviews and finding critical flaws. When reviewing, it navigates your codebase, reasons through dependencies, and runs your code and tests in order to validate correctness. We evaluated code review performance on recent commits from popular open-source repositories. For each commit, experienced software engineers evaluated review comments for correctness and importance. We find that comments by GPT‑5‑Codex are less likely to be incorrect or unimportant, reserving more user attention for critical issues.

GPT‑5‑Codex is a reliable partner on front-end tasks. In addition to creating aesthetic desktop apps, GPT‑5‑Codex also shows significant improvements in human preference evaluations when creating mobile websites. When working in the cloud, it can look at images or screenshots you provide as input, visually inspect its progress, and display screenshots of its work to you.

GPT‑5‑Codex was purpose-built for Codex CLI, the Codex IDE extension, the Codex cloud environment, and working in GitHub, and also supports versatile tool use. Unlike GPT‑5, which is a general-purpose model, we recommend using GPT‑5‑Codex only for agentic coding tasks in Codex or Codex-like environments.

## Updates to Codex

We also recently made some updates to make Codex a better pair programmer, with a revamped Codex CLI and the new Codex IDE extension.

### Codex CLI

Codex CLI is open-source, and community feedback over the last few months has been invaluable in shaping its evolution. With this feedback, we’ve rebuilt Codex CLI around agentic coding workflows to harness our models into more capable and reliable partners. You can now attach and share images—screenshots, wireframes, and diagrams—right in the CLI to build shared context on design decisions and get exactly what you want. When doing more complex work, Codex now tracks progress with a to-do list, and includes tools like web search and MCP for connecting to external systems, with more accurate tool use overall.

The terminal UI has also been upgraded: tool calls and diffs are better formatted and easier to follow. Approval modes are simplified to three levels: read-only with explicit approvals, auto with full workspace access but requiring approvals outside the workspace, and full access with the ability to read files anywhere and run commands with network access. It also supports compacting conversation state to make longer sessions easier to manage.

Check out the [Codex CLI quickstart](https://developers.openai.com/codex/cli) to learn more.

### The Codex IDE extension

Codex meets you where you already work, including in your IDE. The IDE extension brings the Codex agent into VS Code, Cursor, and other VS Code forks, so that you can seamlessly preview local changes and edit code with Codex. When you use Codex in your IDE, you can write shorter prompts and get faster results because Codex can use context like the files you’ve opened or the code you’ve selected.

The Codex IDE extension also lets you move work smoothly between the cloud and your local environment. You can create new cloud tasks, track in‑progress work, and review completed tasks without leaving your editor. To make finishing touches, you can open cloud tasks in your IDE, and Codex maintains context. Learn more on how to get the most out of the IDE extension in the [quickstart](https://developers.openai.com/codex/ide).

### Codex cloud

In addition to Codex CLI, the new IDE extension and GitHub integration bring the Codex cloud agent closer to developer workflows so you can now delegate tasks without switching away from your editor or GitHub.

Behind the scenes, we’ve also been continuously improving cloud infrastructure performance. By caching containers, we’ve slashed the median completion time for new tasks and follow-ups by 90%. Codex also now automatically sets up its own environment by scanning for common setup scripts and executing them, and with configurable internet access can run commands like pip install to fetch dependencies as needed at runtime.

Like in the CLI and IDE extension, you can now use images to share frontend design specs or explain UI bugs. As it builds for you, Codex can spin up its own browser, look at what it built, iterate, and attach a screenshot of the result to the task and GitHub PR. For more details, check out the [docs](https://developers.openai.com/codex/cloud).

### Code review

Codex also now includes code review capabilities trained to catch critical flaws. Unlike static analysis tools, it matches the stated intent of a PR to the actual diff, reasons over the entire codebase and dependencies, and executes code and tests to validate behavior. Only the most thorough human reviewers put this level of effort into every PR they review, so Codex fills the gap—helping teams find problems earlier, reduce reviewer load, and ship with more confidence.

Once turned on for a GitHub repo, Codex automatically reviews PRs as they move from draft to ready, posting its analysis on the PR. If it recommends edits, you can stay in the same thread and ask Codex to implement them. You can also explicitly ask for a review by mentioning “@codex review” in a PR, and give it extra guidance like “@codex review for security vulnerabilities” or “@codex review for outdated dependencies”. Check out [the quickstart](https://developers.openai.com/codex/cloud/code-review) to learn how to set up code review for your repos.

At OpenAI, Codex now reviews the vast majority of our PRs, catching hundreds of issues every day—often before a human review begins. It’s been key to letting the Codex team move fast with greater confidence.

### 开发人员如何使用 Codex

## Building safe and trustworthy AI agents

We’re building Codex with a focus on protecting code and data from exfiltration, and guarding against misuse. By default, Codex runs in a sandboxed environment with [network access](https://platform.openai.com/docs/codex/agent-network) disabled, whether locally or in the cloud. This helps ensure Codex can’t take harmful actions on your computer, and reduces the risk of prompt injections from untrusted sources.

Codex can ask for permission before potentially dangerous actions and is trained to run commands to verify its outputs. Developers can customize security settings to match their risk tolerance. In the cloud, you can limit network access to trusted domains. In the CLI and IDE extension, developers can approve commands to run with full access or allow the agent to use web search and connect to MCP servers. This can expand capabilities of the agent while increasing the risks–learn more about how to securely operate and manage Codex [here](https://developers.openai.com/codex/security).

We always encourage developers to review the agent’s work before making changes or deploying to production. Codex provides citations, terminal logs, and test results with each task to help with this. While Codex code reviews help reduce the risk of dangerous issues being deployed to production, whether created by humans or agents, we always recommend using Codex as an additional reviewer—not a replacement for human reviews.

Consistent with our approach to GPT‑5, we have decided to treat GPT‑5‑Codex as High capability in the Biological and Chemical domains, and have implemented safeguards to minimize the associated risks. Read more about our assessments and robust safety approach in the [system card addendum⁠](https://openai.com/zh-Hans-CN/index/gpt-5-system-card-addendum-gpt-5-codex/).

## Pricing and availability

Codex is included with ChatGPT Plus, Pro, Business, Edu, and Enterprise plans. Usage scales with your plan: Plus, Edu and Business seats can cover a few focused coding sessions each week, while Pro can support a full workweek across multiple projects.

Business plans can purchase credits to enable developers to go beyond their included limits, while Enterprise plans provide a shared credit pool so you only pay for what your developers use. Learn more about usage limits in ChatGPT [here](https://developers.openai.com/codex/pricing).

For developers using Codex CLI via API key, we plan to make GPT‑5‑Codex available in the API soon.

Codex is becoming the coding partner we’ve always envisioned—one that’s faster, more reliable, and deeply integrated into the tools you already use. We’re excited to see what you build with it and will keep improving Codex to make it an even better teammate for your most ambitious projects.


## 作者

OpenAI
