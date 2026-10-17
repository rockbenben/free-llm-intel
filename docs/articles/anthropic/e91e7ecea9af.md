---
vendor: anthropic
title: Anthropic 日本的一位 BDR，如何带着一队 Claude 智能体过一天
original_title: 
url: https://claude.com/resources/articles/how-an-anthropic-japan-business-development-representative-runs-his-day
date: 2026-10-16
lang: zh
captured: 2026-10-17
extractor: readability-v1
translator: agent
status: translated
body_sha: 98098b60598d
---

作为 Anthropic 日本团队的 business development representative，我的工作是向日本公司展示 Claude 能怎样简化和自动化它们的工作流，但直到今年早些时候，我自己的大部分流程还都是手工的。我每天早上要花上两个小时把进来的线索分派出去、判断它们的成色，然后用日语或英语写邮件。在剩下的那点时间里，我在更新我们的 CRM，通常已经落后一天甚至更多。现在，我的智能体在我这一天开始之前就把其中大部分准备好了，我来审阅。

我搭的第一个由 Claude 跑起来的工作流相当简陋，但它确实把活儿干完了。我一次只交给 Claude 一件我的活儿，把它做错的地方纠正过来，再把这些纠正存下来。久而久之，它长成了几个智能体，各自覆盖一件日常事。

消息传得很快，同事们开始找我要 prompt 和 skill，好自己也搭一套。我能发给他们的只有一个 zip 文件，里面是我的 skills 和知识库里几个 Markdown 文件，他们得把这些上传到 Claude，再回答一轮设置问题，之后才有东西能跑起来。我自己那套也越来越难记住：每个智能体是一个 skill、一个定时任务加一个共享文件夹，而我改它们的方式是在手边随便哪个 chat 里跟 Claude 说，所以同一个 skill 会从许多不同的对话里被编辑。

我想把一个智能体只在一个地方定义一次，并且能看到我对它做过的每一次改动。于是我决定试试 [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview)（beta），这是我们在 Claude Platform 上的托管智能体基础设施。

一开始我有点不敢试。文档里讲的是调度、工具和凭证库，而我是个销售，所以我以为 Managed Agents 是给那些能搭建并维护相应基础设施的开发者用的。我还是试了，因为我的智能体已经存在了，我只需要把它们搬过去。

结果发现我不必是个开发者。我用平实的语言描述每个智能体干什么活儿，Claude 写了几段简短的设置脚本，我在笔记本电脑的终端里跑它们。（如果你从零开始，Console 里也有一个带现成智能体模板的 [quickstart](https://platform.claude.com/workspaces/default/agent-quickstart)。）从那以后，我再没有什么基础设施要照看了。

在这篇文章里，我会走一遍我如何设计并把这支队伍做出原型、为什么把它搬到 Managed Agents 上、Claude Tag 怎么接住落在常规之外的事、这一切怎样改变了我的一周，以及我会对那些想搭自己的智能体、把手工重复的工作流自动化下去的销售说什么。

## 设计我的智能体队伍

我把我的工作流拆给几个智能体，每个智能体只给一件清楚的活儿。职责单一，每个智能体才好理解、好跟踪——尤其是它出毛病的时候。我还给每个智能体起了日语名字，因为它们大部分工作是用日语做的。它们合在一起叫 *Nakama*，意思是“我们这伙人”，更字面一点，是和你一起共事的那些同伴：

- ***Furiwake***（“分拣”）最先开工：它读取每天进来的队列，把每条线索分给团队里合适的同事，兼顾每人线索数量和各条线索的优先级，还会看谁当天在，于是我们任何人开始一天的工作之前，每条线索都已经有了负责人。每次跑完，它会在一个专门的 Slack 频道发一份报告（每一条进来的线索、每一条派出去的线索），这样我能跟踪交接。
- ***Sabaki* **（“处理”）给分到我名下的线索做分诊：它逐条判断线索成色，按预设标准归类，执行那一类定好的下一步（草拟一封指向自助服务的回复、写一封定制的首封邮件），在 Salesforce 里更新线索记录，并起草首次触达的邮件。草稿的内容来自 *Nakama* 共享的知识库——那是一个 [memory store](https://claude.com/blog/claude-managed-agents-memory)，每个智能体都会读它、也会往里写（下面详细说）。
- ***Henji* **（“回复”）每小时扫一遍我的收件箱，找出需要回复的客户邮件，并按所在线程的语言准备一份日语或英语的回复草稿，用的知识和 *Sabaki* 是同一套。我可以审阅、编辑草稿并发送。
- ***Shoudan***（“商机”）读取最近的客户互动，把更新推进 Salesforce，这样商机记录不用手工录入也能保持最新。
- ***Nokori* **（“还剩下的事”）在一天结束时跑：它扫我的日历，读取附上的会议记录，为每场会议做摘要，并起草后续的跟进事项，同样是从那个知识库里取内容。

每个智能体都按[调度](https://claude.com/blog/whats-new-in-claude-managed-agents) 运行。第六个智能体是 Nakama 的协调者，它是这支队伍的运营经理，负责在各次运行之间更新各智能体的指令和共享知识库。当我想改某个智能体的做法时，我在 Nakama 的 Slack 频道里用平实的语言写下我要什么。只有我能发出修改智能体指令和 system prompt 的请求。协调者每隔 15 分钟左右检查那个频道，接住请求并完成更新。

![展示这些智能体以及各自角色的示意图](https://assets.claude.com/1fabdce2187d0997e43f9b0518820c25606a0f1d.png)

## 在 Claude 里把队伍先做出原型

起步并不需要 Managed Agents。我整支队伍都是先在 Claude 里做出原型的，用的是这些东西：

- 每个智能体一个 skill：一件活儿对应的指令。
- 每个 skill 配一个定时任务，这样我不必手动去跑它。
- 笔记本电脑上一个共享文件夹，当作每个 skill 都往里写经验的知识库：它起草的内容和我实际发出去的内容之间有什么差别，加上它一路上挖到的新东西。

到了 Managed Agents 上，skill 变成了智能体的 system prompt，定时任务变成了 [智能体 deployment 上的调度](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments)，共享文件夹变成了 memory store。我照旧用平实的语言提改动，只是现在全在一个 Slack 频道里做，而且对智能体指令的每一次改动都会另存为一个新版本，于是每个智能体都留着一份带编号的指令历史。我的建议是：先在 Claude 里起步，等你手上的智能体多到自己舒舒服服记不过来的程度，再把它们搬到 Managed Agents 上。

![展示这些智能体如何部署在 Claude Managed Agents 上的示意图](https://assets.claude.com/a04a480dffb7c328be71e45d708df2ccb10c3e30.png)

## 在 Claude Managed Agents 上运行这支队伍

上了 Managed Agents 之后，三件对我的工作流最重要的事：

**智能体能在后台运行**

不管我的笔记本电脑开没开，智能体都按自己的调度运行，哪怕它离线也一样。调度是每个智能体 deployment 的一部分。在 Claude 里我也能给 skill 排期，但那些调度里的每一个都是在我自己的 app 里建起来的一个任务。在 Managed Agents 上，我在 Console 里、就在那个已部署智能体的指令和工具旁边，设定频率和时区，我手边再没有要维护的 cron 任务。某次运行出了问题，我可以在 Console 里打开它，看到智能体走过的每一步。而当我在试用对某个智能体的改动时，定时运行仍在用那个已经部署的版本，所以一个改到一半的编辑不会跑到明天的运行里去。

**Nakama 共享一份记忆，并从我的修改里学习**

每个智能体读和写的都是同一个 [memory store](https://claude.com/blog/claude-managed-agents-memory)，所以任何一个智能体都能用上其他智能体学到的东西。智能体会把自己写的草稿和我发出去的邮件做对比，并把每一处差别存成一条笔记，记下我会怎么表达。它们也会留下自己在研究答案时挖到的新信息，来源包括我们的内部文档和我们的官方网站。我在 Henji 的草稿里把一处措辞改对一次，Sabaki 和 Nokori 就不再犯同一个错。

**凭证放在托管的凭证库里，权限按范围划定**

我的智能体能访问我的邮件和我们的 Salesforce 记录，但这些是客户对话和公司记录，所以我想把这份访问权管起来。凭证放在 [managed vaults](https://platform.claude.com/docs/en/managed-agents/vaults) 里，它保护的是智能体登录外部服务所用的凭证，比如 OAuth access token 和 refresh token、API key、personal access token。每个智能体的 deployment 只用它那件活儿需要的 vault，它自己永远看不到凭证，而我一步就能撤销访问权。

## 把下一步交给 Claude Tag

Nakama 产出的大部分东西，我只需要在收件箱里读一眼草稿再发出去，或者扫一眼更新过的 Salesforce 记录。但有些事项需要一个后续步骤，比如搞清楚一条升级路径或采购途径，或者把一个问题升级给另一个团队。

这些情况下，智能体不会停下来等我，而是把事项交给 [Claude Tag](https://www.anthropic.com/news/introducing-claude-tag)（beta）。Claude Tag 就是把 Claude 设置成我们 Slack workspace 的一名成员：它加入的任何频道里的任何人，一个人或我的某个智能体，都可以 @Claude 提一个请求，它就会接住这个请求并在线程里干活。一旦在你们的 workspace 里配置好，没有新东西要学。你像 @ 一位同事那样 @ Claude 就好。

在我这套设置里它是这样运作的。一个智能体把行动项发到 Nakama 的 Slack 频道，并 @ Claude。Claude 读这个线程，查我们的规则和适用的条款，把选项摆出来，并起草需要的内容。当某一步需要我审阅或拍板时，它会 @ 我。当需要客户或另一个团队先回复时，Claude 会给自己设一个提醒，在定好的那天回来查。在下面这个线程里，它设了一个周二的提醒，去看客户是否回复了、deal desk 是否回答了那张工单。提醒到期时，Claude 把两件事都查一遍，并在同一个线程里发出目前的状态。如果有人需要被催一下，它起草好消息，然后 @ 我让我发出去。

![一个人、Claude 和一个智能体之间对话的截图示意图](https://assets.claude.com/407d1a67eadd3ebd1d4ec34fd1fabebb42b64829.png)

Claude 还会在早上发一份产品和定价更新的简报。Nakama 的协调者接住那份简报，把必要的改动写进共享知识库。

## 我的一周因此变了什么样

现在 Claude 会把进来的回复准备好、让 CRM 记录（大体上）不用我手工输入也保持最新，我的角色就成了审阅那些需要人来判断的东西。一份写下来的规则手册划定了每个智能体的车道，像定价问题、敏感客户或含义模糊的请求这类事项会路由给我。Henji、Sabaki 或 Nokori 的每一封邮件草稿都在最上面带一小段摘要，说清这是怎么一回事，所以我不必把整个线程追一遍才能明白上下文：我读摘要、确认、改一改、发送。

![Claude 起草、供人工审阅的一封邮件的截图](https://assets.claude.com/209fde33711300fd8cfb2f1fc7005f21bca2a20d.png)

看看 Nakama 一周处理掉多少事的日志，并把每项任务按我自己手工做要花的时间来算，这支队伍为我省下大约 60 小时的工作。省出来的时间我花在智能体（暂时）还做不利索的活儿上：和客户的对话、outbound 策略、跨职能项目，还有帮同事们搭他们自己的队伍。

## 把智能体设计得更省

定时运行的智能体每天照跑，不管我在不在看，所以浪费会在成本和可靠性上累积起来。最常见的错误包括：往现有指令上不断追加而不是更新它、给智能体超过任务所需的上下文、每个活儿都用最大的模型和最高的 effort 等级来跑。

让智能体保持高效的，多半是我如何设计这支队伍：每个智能体只有一件活儿，所以它的指令始终聚焦在那件活儿上；每个干活的智能体按调度运行，所以它醒来、做完它那一遍、然后停下；智能体之间共享记忆，所以做过一次的修正到处都能复用。

另一个大因素是每个智能体跑在哪个模型上。一个智能体的活儿定清楚之后，它未必需要我们最强的模型。Furiwake 和 Shoudan 照一份写好的规则手册办事，所以它们跑在 Sonnet 上，我们较小的那个模型。Sabaki、Nokori 和协调者跑在 Opus 上，我们较大的那个模型，因为它们的工作需要更多判断。协调者最需要判断力，因为它改的是其他智能体的指令，一次改坏会波及每一个智能体。Henji 需要的判断力和 Sabaki 一样多，因为每个客户的邮件都不一样，但它也比任何别的智能体跑得都频繁，整个工作时间都在跑。每次都让它跑 Opus 会是最贵的选择，所以我在 Managed Agents 上用 [advisor 策略](https://claude.com/blog/the-advisor-strategy)：Henji 跑在 Sonnet 上，当它碰到一个自己做不了的决定，就向 Opus 要建议。advisor 读 Henji 到目前为止做了什么，回给它一个方案、一处修正或一个停止信号，然后 Henji 把草稿做完交给我审阅。我还把每个智能体的 effort 等级（模型回答前思考多久）和它用的模型分开设定，只在推理确实难的地方调高，比如 Henji 的回复。

![展示各个智能体用哪些模型来完成各自工作的示意图](https://assets.claude.com/f9f71df9bc447aba6114949e002ce0fb8dd34ba2.png)

## 我学到的东西

三件我想交给任何搭自己队伍的人的事。

- **不必每次都写一段详细的 prompt。** 把活儿描述一次，让 Claude 起草，改掉草稿里不对的地方，然后让它把这个修改留住。
- **知识库比 prompt 更重要。** 每一次修正、每一次过往互动都存在所有智能体都能读写的地方，所以 Claude 从那里取上下文，而不是靠一段更长的 prompt。为了让草稿听起来像我写的，我花了大概几百轮成本很低的起草、修改和保存。
- **更早、更多地给 Claude 留出空间。** 一开始我一直在自己做那些我以为非得我来做的活儿：更新知识库，或者手工编辑每个智能体的指令。等我放手，这两件事都照样好用。智能体现在自己把它们学到的写进知识库，而协调者会在我用平实英语提要求时更新其他智能体的指令。我对那些本可以放心交给智能体的活儿过于谨慎了。

[开始使用 Claude Managed Agents](https://platform.claude.com/workspaces/default/agent-quickstart)

文章

2026 年 10 月 16 日

### Claude Code 团队怎么做 code review

智能体产出代码的量到了这个地步，你该怎么审？Claude Code 团队分享了他们的审阅流程，从 Claude 验证自己的工作，到按风险分层的人工审批，外加一份用于采纳这套流程的检查清单。

Claude Code


文章

2026 年 10 月 8 日

### 构建有效的智能体自动化

一份针对定时运行的 Claude Managed Agents 自动化的参考实现走查，附带配置文件，以及六条避开常见失败模式的规则。

Claude Platform


文章

2026 年 10 月 7 日

### 用 Claude 自动化 eval 设计与 hillclimbing

设计 eval 并不被自己骗到、再针对它做 hillclimbing 的原则，以及 claude-api skill 的 build-eval 和 hillclimb 命令如何把它们用起来。

Claude Platform


文章

2026 年 10 月 6 日

### 云上的 Claude Code：cloud session 实战手册

当 Claude Code 跑在自己的一台机器上会有什么变化、哪些工作流能从中得到回报，以及怎么一次就把 GitHub 接上。

Claude Code


## 用 Claude 改变你组织的运作方式

[查看定价](https://claude.com/pricing#api)[联系销售](https://claude.com/contact-sales)

### 订阅 developer 通讯

产品更新、操作指南、社区聚焦等等，每月送达你的收件箱。

如果你想订阅我们每月的 developer 通讯，请提供你的邮箱地址。你可以随时退订。
