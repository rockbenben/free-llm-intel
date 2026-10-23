---
vendor: cohere
title: AI 能理解文化吗？一位退休教师和一名高中生来试试
original_title: 
url: https://cohere.com/blog/can-ai-understand-culture
date: 2026-10-22
lang: zh
captured: 2026-10-23
extractor: readability-v1
translator: agent
status: translated
body_sha: 596b20920851
---

# AI 能理解文化吗？一位退休教师和一名高中生来试试

一位退休教师和一名高中生对 AI 做了一场测试

![](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/24b8abec4b5cf28df9a82d105fb39fc45881c2cf-3840x2160.png?auto=format&fit=max&q=80&w=1130)

想想这个古老的谜语：「你闭着眼睛走进去、睁着眼睛走出来的，是哪种房子？」说英语的人会一下子认出答案是 "a school"（学校），可如果用另一种语言问同一道谜语，AI 模型可能就被难住了。Cohere Labs 的一个[开放科学项目](https://cohere.com/research/papers/culturalriddles-2026-10-22)揭开了「解读」这件事的复杂本性，结果出人意料。

「riddle」这个词源自古英语的 "rædan"，意思是「解读」或者「劝告」，这暗示谜语要的是解读和洞察，而不光是瞎猜。谜语靠含糊活着，却各有各的确解。人靠练习和反馈把谜语越猜越准，AI 也一样，它靠机器学习把自己的本事磨上去。

> 「我们简直不敢相信自己的眼睛……这不再是『只是』研究，它是一场运动。」- Boczka Károly

匈牙利外交官 Boczka Károly 一直在主动找 AI 研究的机会。当他决定编一批刁钻的、匈牙利冷知识风格的谜语，来测一测 AI 模型能否认得出文化线索时，他拿到了令人震惊的结果。模型的回答*听起来*是对的，但并不是对的。模型缺的是文化里特有的那些事实，有些情况下还产生了幻觉。在一场由 Cohere Labs 主持、围绕 AI 里的文化展开的开放科学社区讨论中，Boczka 把自己的发现讲给了 Julia Kreutzer。Kreutzer 是 Cohere Labs 的 Staff Research Scientist，她立刻看出这里有一个可以上手检验的落差：AI 的流利，和文化知识之间的距离。两人一起把一个项目铺到了全球规模，去测那些主要用英文数据训练出来的模型里的流利度、逻辑和推理，以及每个答案背后的盲区。

参与这个项目不需要什么专业资历，只要你认同某一种文化、肯花时间写谜语和做评估就够了——这就给任何年龄、任何背景的研究参与者打开了门。一次发在社交媒体上、也发在 [Cohere Labs 已有的研究社区](https://cohere.com/research/open-science)里的公开召集，邀请人们加入项目，不设任何准入条件，刻意拆掉了平时会把人挡在门外的那些门槛。社区聚在 Discord 上，在体育、历史、政治这些文化板块上搭起了自己的 benchmark，每一道题都按谜语来设计。

![](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/6649183f3a280f2ee323dde028a0a60da216a63c-932x1146.png?auto=format&fit=max&q=80&w=468)

Boczka 先生的这个点子很快就长成了一个国际性的行动。「我们简直不敢相信自己的眼睛，」他说。「我们有 100 多位贡献者，来自 50 多个国家。这不再是『只是』研究，它是一场运动。」他接着说，「我们这个集体专注、独立又彼此协作，整个项目就像一株栽种得当的植物那样生长起来。」在这个根扎得很深的社区里，有两位参与的成员：15 岁的美国少年 Henry Gagnier，和加拿大的退休教师 Jane Smith。

大多数青少年面对这种规模的全球研究团队可能会发怵，但 Henry Gagnier 那股有感染力的热情，压过了「典型的研究团队成员该是什么样」的任何先入之见。「我会说，AI 研究是属于每一个人的。AI 研究有太多个各不相同的面向。我们需要来自许多不同文化的人，而对这个 benchmark 的搭建真正管用的不是『AI 技能』，是实实在在的文化知识。」当被问到在这个群体里有没有发怵或者吃惊，他说：「最让我惊讶的是他们的包容和开放，因为作为一个高中生，我其实一直有点发怵——加入这个项目，然后说我想要给这个团队当 lead。但每个人都特别好。那是一段特别棒的经历。」

这个项目虽然扎在文化和语义的细微之处，却让他对研究、以及研究可能给他的那条路，看得清楚了不少。「它让我提前偷看了一眼真正的研究者手头在做什么，」Gagnier 说。「我想在这个领域继续做研究。我现在也在做几个项目，推进自己在这个领域的知识，所以我觉得这个项目是一次很好的教育经历，它确实改变了我对自己将来要往哪儿走的看法。」

作为一名退休教师，Jane Smith 把她所谓的「教师路子」用在了研究上。「我以前评估孩子们，要是他们答错了什么，我总会试着往回推，就是想，好，『它是从哪一步开始走错的？』『是什么把它引到了一个完全错误的答案上？』一定有什么东西把他们带到了那里，所以我发现自己在做评估的时候常常就这么干。」她还试着给自己的流程加上拟人的色彩，在谜语里放进老虎、螃蟹之类的东西，把逻辑做成游戏，当作一件有力的教学工具。

每解开一道谜语、每生成一道谜题，都成为一个数据点，让这个项目对语言和逻辑的理解更准一点。让这个谜语项目格外有意义的地方是，它不只是为了好玩——它展示的是解读能力，而正是这种能力定义着谜语，也定义着 AI。

![](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/27bc21d714e6bd39c667a3ffdd00fc3b240d6b73-3840x2160.png?auto=format&fit=max&q=80&w=800)

AI 在不同语言、不同语境下应付文化谜语时的吃力，可能是开发模型过程中最要紧的挑战之一。「我有点惊讶，因为那不只是文化理解的欠缺，」Gagnier 说。「这些模型压根就不懂这门语言，而我觉得 Buginese 是一门说的人相当多的语言。让我惊讶的是，这些模型对这门语言的了解几乎是零，而在我们这套评估方式下，这也等于对那门文化的了解是零。」

这个项目点明了一件事：智能不只关乎[解谜](https://culturalriddles.ai/)，还关乎理解人类经验，以及经验背后的那些语言。当我们想到解读必须扎在文化里才谈得上有意义，"rædan"（解读）的词源就有了新的分量。

Smith 太太说出了一种社会上广泛共有的担忧：AI 文化模型的准确度。「让我惊讶的是，模型回答『我不知道』的次数那么少。它给出的反而是那些听起来相当权威的 [答案]，会让人以为：『哦，这东西知道自己在说什么。』」

让团队感到不安的，是模型那种有限的结论——答错了，听上去却毫不摇摆地自信。看清了这个盲区，Smith 太太说：「让我害怕的地方在于，它听起来是那么权威，而人们正是在找权威的答案。」她补充说：「我不觉得要我们命的是 AI。要我们命的是我们缺乏批判性思考。」

在一个有人担心日常生活里属于人的那些成分正在飞快消失的时代，这项谜语研究逼着人们重新去想任何缺少人的温度的解决方案。Smith 太太以她的智慧抛出一句话，看着像个逗趣的双关，却可能恰恰是对待 AI 文化难题的*那个*决定性态度：「犯错的是 AI。会批判性思考的才是人。」

在人类认知与 AI 的思考之间，有一个有意思的中间地带。Cohere Labs 正通过深入钻研[今天模型里的信心](https://cohere.com/blog/rethinking-confidence-in-reasoning-models)来做更好的上下文理解。这些谜语证明：随着 AI 越来越确信自己的回答，我们必须记得，是批判性思考让我们保持为人。

## 接下来阅读此内容

- [![Rerank 5 标识](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/001e212cb8f99611514f36805a3c3ef32a51f7d9-3840x2160.png?auto=format&fit=max&q=80&w=440)](https://cohere.com/blog/rerank-5)[产品发布](https://cohere.com/blog/tag/product-launch)[公司新闻](https://cohere.com/blog/tag/company-news)[企业人工智能](https://cohere.com/blog/tag/enterprise-ai)[介绍 Rerank 5：精准、高效的企业文档检索2026 年 10 月 21 日8 分钟阅读](https://cohere.com/blog/rerank-5)
- [![抽象图片](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/29364be119de6f05876cf2f747d763c297eafa69-3840x2160.png?auto=format&fit=max&q=80&w=440)](https://cohere.com/blog/rethinking-confidence-in-reasoning-models)[研究](https://cohere.com/blog/tag/research)[重新思考推理模型的信心2026 年 10 月 20 日6 分钟阅读](https://cohere.com/blog/rethinking-confidence-in-reasoning-models)
- [![公用事业的 AI 需要能力，也需要控制](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/b36c731c34b23aeeb737f166444aeaa87d9e9c68-1920x1080.png?auto=format&fit=max&q=80&w=440)](https://cohere.com/blog/ai-for-utilities-requires-capability-and-control)[企业人工智能](https://cohere.com/blog/tag/enterprise-ai)[能源与公用事业](https://cohere.com/blog/tag/energy-utilities)[公用事业的 AI 需要能力，也需要控制2026 年 10 月 15 日6 分钟阅读](https://cohere.com/blog/ai-for-utilities-requires-capability-and-control)
