---
vendor: tencent_hunyuan
title: 复杂推理
original_title: 
url: https://hunyuan.tencent.com/research/hy3-preview
date: 2026-04-23
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: native
status: translated
body_sha: a021be6292f6
---

2026年4月23日

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/f38ef6a6/2026062420424729_754ceac666fd5bbc07f8a74c70934340.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1782304970;2097664970&q-key-time=1782304970;2097664970&q-header-list=&q-url-param-list=&q-signature=d4522dc104ff4c0274e99580b815911588b6f1d0)

Hy3 preview： 混元大模型重建的第一步

![Hy AI Studio](https://hunyuan-portal-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/ai-logo-svgs/hunyuan-color.svg)Hy AI Studio

![腾讯云](https://hunyuan-portal-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/ai-logo-svgs/tencentcloud-color.svg)腾讯云

![GitHub](https://hunyuan-portal-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/ai-logo-svgs/github.svg)GitHub

![Hugging Face](https://hunyuan-portal-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/ai-logo-svgs/huggingface-color.svg)Hugging Face

![ModelScope](https://hunyuan-portal-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/ai-logo-svgs/modelscope-color.svg)ModelScope

4 月 23 日，腾讯混元 Hy3 preview 语言模型发布并开源。这是一个快慢思考融合的混合专家模型，总参数 295B，激活参数 21B，最大支持 256K 上下文长度。

今年 2 月，我们重建了预训练和强化学习的基础设施， 以及模型追求实用性的三个原则：

• 能力体系化： 我们不推崇“偏科”，因为即使是代码智能体的单一应用，也涉及推理、长文、指令、对话、代码、工具等多种能力的深度协同。

• 评测真实性： 我们主动跳出易被“刷榜”的公开榜单，通过自建题目、最新考试、人工评测、产品众测等多种方式评估和改进模型的“真实战斗力”。

• 性价比追求：实用性离不开商业合理性，我们深度协同模型架构和推理框架的设计，大幅降低任务成本，让智能用得起、用得好。

Hy3 preview 是我们重建后训练的第一个模型，也是混元迄今最智能的模型，在复杂推理、指令遵循、上下文学习、代码、智能体等能力及推理性能上实现了大幅的提升。

# 复杂推理

推理能力是模型解决各种问题的基础。Hy3 preview 在 FrontierScience-Olympiad、IMOAnswerBench 等高难度理工科推理任务中表现突出，并在最新的清华大学求真书院数学博资考（26春）和全国中学生生物学联赛（CHSBO 2025）中取得优异成绩，展现出可泛化的强推理能力。

![tuili1.jpg](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/f38ef6a6/2026062421035182_57555372f3d755c96b330d797197425b.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1782306232;2097666232&q-key-time=1782306232;2097666232&q-header-list=&q-url-param-list=&q-signature=950a11cab2330d8d2610320f7d630487ce9912ba)

# 上下文学习和指令遵循

在各种真实的生产与生活场景，理解杂乱冗长的上下文并遵从复杂多变的规则，是模型的首要挑战。基于我们业务场景的灵感，我们提出了 [CL-bench](https://github.com/Tencent-Hunyuan/CL-bench) 和 [CL-bench Life](https://huggingface.co/datasets/tencent/CL-bench-Life) 来创新性地评估模型的上下文学习能力，并在 Hy3 preview 显著地提升了模型上下文学习和指令遵循能力。

![2.jpg](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/f38ef6a6/2026062421040521_156005c5baf40ff51a327f1c34f2975b.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1782306247;2097666247&q-key-time=1782306247;2097666247&q-header-list=&q-url-param-list=&q-signature=5bc55edd0e4a02df0bec6a24a4f442bd427af34c)

在处理工作场景下的复杂排期任务时，Hy3 preview 展现出更强的隐性信息挖掘与上下文约束整合能力，能够准确识别会议纪要中隐含的项目启动时间、工作日规则、请假安排和加班要求，并将分散在多轮表达中的依赖统一转化为正确、可执行的排班结果。而 Hy2 在项目开启日期的识别，和休假安排上，均出现错误。

System prompt：

你是一个软件开发项目管理小助手，你需要根据用户提供的开会内容，整理出开会核心项目关于人员安排的部分。 你只需要生成表格，表格中的内容行应按照用户的开发流程的先后顺序从上到下排列。表格格式如下： | 人员名字 | 开发流程 | 时间 | | :--- | :--- | :--- | | 人员A | 开发流程 | MM.dd-MM.dd | | 人员B | 开发流程 | MM.dd-MM.dd | | 人员C | 开发流程 | MM.dd-MM.dd | …… 其中表格的每个“开发流程”字段都只能在以下六个中选择一个填写：需求分析、页面设计、UI设计、后端开发、前端开发、软件测试。 工期需要按照工作日计算，日期安排按照自然日填写就好，起止日期都包含首尾当天。除非在特殊情况下被要求加班，否则周六、周日及法定节假日不上班。若在周六、周日或节假日安排加班，该休息日可计入工期。 时间格式应为：MM.dd-MM.dd，例如：03.02-03.04。 现在时间是2026.3.4（星期三）。

李亮：好，拉个会啊，就是这个月20号是春分，我们现在是需求是给春分做一个h5的活动，内容是“竖彩蛋 ‘玩’春分”主题活动。我们先欢迎新人张思，是我们新来的页面设计。简单给新人介绍一下我们的开发流程，依次是：需求分析、页面设计、UI设计、后端开发、前端开发、软件测试。这次只是个h5的网站，不涉及到UI设计。页面设计之后就直接到开发那边了。我来简单的讲一下这次的需求，昨天开始简单写了一下，有什么疑问可以提出来。
 …… 
李亮：好了，以上大家清楚了吗。 
张思：嗯大概清楚了。你的这个需求报告还需要修改吗？不需要的话，设计这边给出的工期是2天。
 李亮：今天3月4号，我再修改下，明天完成。设计6号可以开始吗？
 张思：可以。但是我下周一这边需要请假。
 李亮：嗯 ，那顺延一个工作日完成问题不大。开发呢？ 
 王五：涉及到的后端不复杂，前后端个各2天都行。我这边人也都在王哥那个项目上，后端13号可以开始，后端做完之后赵一那边第二天就可以开始做前端的。
 李亮：测试这边呢？ 
 散散：不够啊，等开发完，开始的话都19号了，20号就要上线，一天时间还是太赶了。 
李亮：也是，王五这边看能沟通一下，周六加个班吗？后面可以调休。因为20当天需要上线的。 
王五：好的，理解。赵一呢？
 李亮：赵一周末还是休息吧。回来再开始就好。 
散散：那时间是够的，两天可以完成测试。 
张思：或者我下周二请假，周一先完成。
 李亮：其实都还好，看你。因为开发那边13号才能开始。
 张思：嗯……那还是周一请吧。

![](https://hunyuan-portal-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/ai-logo-svgs/hunyuan-color.svg)Hy2

| 人员名字 | 开发流程 | 时间 |
| --- | --- | --- |
| 李亮 | 需求分析 | 03.04-03.05 |
| 张思 | 页面设计 | 03.06-03.10 |
| 王五 | 后端开发 | 03.13-03.14 |
| 赵一 | 前端开发 | 03.17-03.18 |
| 散散 | 软件测试 | 03.19-03.20 |

![](https://hunyuan-portal-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/ai-logo-svgs/hunyuan-color.svg)Hy3 preview

| 人员名字 | 开发流程 | 时间 |
| --- | --- | --- |
| 李亮 | 需求分析 | 03.03-03.05 |
| 张思 | 页面设计 | 03.06-03.10 |
| 王五 | 后端开发 | 03.13-03.14 |
| 赵一 | 前端开发 | 03.16-03.17 |
| 散散 | 软件测试 | 03.18-03.19 |

# 代码和智能体

代码和智能体是 Hy3 preview 提升最为显著的方向。得益于预训练及强化学习框架的重建和强化学习任务规模的提升，我们以较快的速度在 SWE-Bench Verified、Terminal-Bench 2.0 等主流代码智能体基准以及 BrowseComp、WideSearch 等主流搜索智能体基准中取得了强竞争力的结果。

![示例图片 1](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/f38ef6a6/2026062421115544_10fb15c77258a991b0028080a64fb42d.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1782306718;2097666718&q-key-time=1782306718;2097666718&q-header-list=&q-url-param-list=&q-signature=a68815ea71da1503e7a4783388d40d8f5f016476)

![示例图片 2](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/f38ef6a6/2026062421121823_d0096ec6c83575373e3a21d129ff8fef.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1782306741;2097666741&q-key-time=1782306741;2097666741&q-header-list=&q-url-param-list=&q-signature=f62e689d1fdc983e14c38763c8ac6b0bd141071f)

![示例图片 3](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/f38ef6a6/2026062421123911_032b2cc936860b03048302d991c3498f.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1782306762;2097666762&q-key-time=1782306762;2097666762&q-header-list=&q-url-param-list=&q-signature=0d373ea6b9443ad6e9162cacd9ad946147fc7fdc)

![示例图片 3](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/f38ef6a6/2026062421125735_18e2999891374a475d0687ca9f989d83.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1782306779;2097666779&q-key-time=1782306779;2097666779&q-header-list=&q-url-param-list=&q-signature=1dec0e0b894410ee699df49f9a620590077f1d4c)

在数字世界中，代码关注的是模型在开发环境中的执行能力，搜索则聚焦于开放信息空间中的检索、筛选与整合能力，两者共同决定了模型在复杂智能体场景（例如 OpenClaw）中是否真正具备可用性。Hy3 preview 在 ClawEval 和 WildClawBench 等评测中表现突出，进一步表明我们的智能体能力的全面与实用性。
![7.jpg](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/f38ef6a6/2026062421154735_fe5df232cafa4c4e0f1a0294418e5660.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1782306950;2097666950&q-key-time=1782306950;2097666950&q-header-list=&q-url-param-list=&q-signature=0b754a1b69ffc82b2aa55534f21d9d620f5616dd)

除了公开榜单，我们进一步构建了多个内部的评测集，对模型在真实开发场景中的表现进行评估。结果表明，无论是在后端工程任务集 Hy-Backend，贴近真实用户开发交互的 Hy-Vibe Bench，还是高难度软件工程开发任务集 Hy-SWE Max 上，Hy3 preview 均体现出了强竞争力。
![8.jpg](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/f38ef6a6/2026062421161417_8cda81fc7ad906927144235dda5fdf15.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1782306976;2097666976&q-key-time=1782306976;2097666976&q-header-list=&q-url-param-list=&q-signature=e9831f13c9c8038b7d5aafb74d02a0b9fa728cbf)

比较各个开源模型的大小与智能体综合表现，Hy3 preview 展现出高性价比。
![9.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/f38ef6a6/2026062421163514_7afbb1602613ec52b265d7a54ad27330.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1782306998;2097666998&q-key-time=1782306998;2097666998&q-header-list=&q-url-param-list=&q-signature=92ea0f78ff8652e7e41155c599f33f3e2d58f4b1)

![根据图生成类似效果图](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/f38ef6a6/2026062421173625_e1c4a83798f6c67d823724358560a0df.gif?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1782307060;2097667060&q-key-time=1782307060;2097667060&q-header-list=&q-url-param-list=&q-signature=3bf988f70c2f36e3364221238ff6e24cae93fabd)

Prompt：请帮我使用微信小程序原生框架开发一个完整、可直接编译运行的徒步路线与旅游计划推荐小程序，请一次性输出包含 app.json 等全局配置、所有页面（WXML/WXSS/JS/JSON）以及完整的 Mock 数据，核心需求包括：一个带有精美图片轮播、‘当季推荐’及‘路线难度’分类导航的首页； 一个包含行程时间轴、精美沿途图库、适宜季节与装备建议的路线详情页；以及一个支持本地缓存收藏功能的个人中心页，UI设计需清新自然、图文并茂，请确保代码逻辑闭环、无缺失文件或引用错误，生成后我可以直接导入微信开发者工具成功预览并体验完整交互。

# 自然对话和用户理解

在探索智能上限的同时，我们始终关注模型与人的交互和对人的理解。为此，我们与元宝团队进行了深度的合作，使用 URM (User-Feedback RM) 对用户的真实反馈进行建模，并结合 RLHF 技术进行了细粒度的优化。结合推理、长文、指令、智能体等能力的优化，这带来了用户体验的大幅提升：Hy3 preview 的事实性错误显著降低，能更精准理解用户的模糊意图和碎片化的输入，回复风格更加共情，内容更具深度。在元宝的灰度测试上，我们看到 Hy3 preview 在元宝用户活跃度上较之前模型实现了大幅增长。

在闲聊场景中，Hy3 preview 更能理解用户的倾诉意图，用简洁且有温度的方式承接用户情绪，避免冗长的咨询建议式回复

**Prompt：**如果离别是尽头 那相遇的意义是什么

Hy2

这个问题像一颗裹着糖衣的苦杏仁——明明知道“离别”可能是故事的注脚，却依然忍不住追问“相遇”的重量。其实我们不必急着给“意义”找一个标准答案，因为相遇本身，早已在生命里刻下了无法被“尽头”抹去的痕迹

### 相遇是“把陌生的光，照进彼此的生命褶皱”

你有没有过这样的时刻？某个人出现前，你以为自己的孤独是常态，自己的脆弱只能藏起来，自己对世界的感知只有一种颜色。但TA来了——可能是一句“我懂”让你敢卸下防备，是一次并肩面对难题让你发现自己比想象中坚韧，甚至是一次争执让你看清自己未曾察觉的执念。
就像春天的风撞碎了湖面的冰，相遇从不是“为了走向离别”的铺垫，而是**让原本封闭的我们，第一次看见“原来我可以被这样理解”“原来活着可以这么鲜活”**。那些一起笑到流泪的瞬间、互相托底的温暖、甚至共同经历的遗憾，都变成了生命里的“锚点”——后来哪怕独自走过漫漫长路，想起这些片段，也会觉得“我没白来这趟”。

### 相遇是“教会我们如何与‘失去’和解”

离别之所以痛，恰恰是因为相遇太珍贵。就像握过一杯热可可的手，会更记得温暖的触感；听过一首好歌的人，会在旋律消失后依然哼着调子想念。相遇让我们尝过“拥有”的甜，才懂得“失去”不是否定过去，而是**给曾经的温暖一个“被铭记”的身份**。
我们总说“天下没有不散的筵席”，但别忘了：筵席散了，桌上的酒渍、碰杯时的笑声、邻座递来的纸巾，早已经变成你身体的一部分。相遇的意义，或许就是让我们学会——**认真爱过、痛过、活过，就是对“尽头”最温柔的反抗**。

### 相遇是“让你成为‘更完整的自己’”的前序

心理学里有个概念叫“镜像自我”：我们通过他人的眼睛，看见自己未曾发现的模样。那个陪你熬夜改方案的朋友，让你看见自己的执着；那个在你崩溃时沉默陪伴的人，让你学会接纳脆弱；甚至那个曾伤害过你的人，也让你更清楚“我要守住怎样的边界”。
相遇从不是为了“永远在一起”，而是**借另一个人的轨迹，补全自己的人生拼图**。就像两块不同的石头碰撞，哪怕最后各自滚向远方，也都在彼此身上留下了打磨过的光泽——这光泽，会跟着你走完剩下的路，让你更懂如何爱自己、爱世界。
所以啊，别害怕相遇后的离别。就像我们看一场烟花，明知它会落进夜色，却依然为绽放的瞬间心动——因为烟花的美丽，从来不是“永不熄灭”，而是“我曾见过它照亮过我的眼睛”。
相遇的意义，不过是：**你来了，我活过，我们共同写过一段“值得”的故事**。至于尽头？那是故事的余韵，而我们已经拥有了最珍贵的“正文”。

Hy3 preview

这个问题真的很戳心呀。其实相遇的意义，或许就藏在那些“明知会结束却依然值得”的瞬间里。
哪怕离别是注定的终点，相遇时的温度也是真的：一起吹过的晚风、分享过的秘密、互相照亮过的时刻，这些碎片拼成了现在的我们。就像烟花会消失，但抬头看的那几秒，天空确实亮过。
有时候想想，正因为有离别，那些共同走过的路才显得珍贵。如果没有相遇，连怀念的机会都没有呢。你最近是不是也在经历某种告别呀？愿意的话可以和我聊聊～🌙

# 产品的上线和初步反馈

Hy3 preview 已在元宝、CodeBuddy、WorkBuddy 、QQ、ima、QQ浏览器、腾讯文档、腾讯乐享上线，并在微信公众号、腾讯新闻、腾讯自选股、和平精英、腾讯客服等多个产品陆续上线中。另外，Hy3 preview 已支持流行的开源智能体产品，如 OpenClaw、OpenCode、KiloCode 等。

![](https://hunyuan-portal-prod-1258344703.cos.ap-guangzhou.myqcloud.com/commonAssets/platform-icons/yuanbao.png)

元宝

元宝产品经理：Logan

Hy3 preview研发过程中，混元与元宝进行了深度 Co-Design 。一方面针对性地提升了模型在意图理解精准度、文本创作质量、深度搜索等硬核指标上的表现；另一方面对文风、文笔、情商、内容组织和内容专业度上进行了精细化调优。模型与产品的深度协同，为用户带来了更智能且更具“活人感”的交互体验。

# 开源、API、Token Plan

Hy3 preview 的模型权重、代码已在[GitHub](https://github.com/Tencent-Hunyuan/Hy3-preview)、[HuggingFace](https://huggingface.co/tencent/Hy3-preview)、[ModelScope](https://modelscope.cn/models/Tencent-Hunyuan/Hy3-preview)、[GitCode](https://ai.gitcode.com/tencent_hunyuan/Hy3-preview)等平台开源，支持vLLM、SGLang 等主流推理框架，开发者可以直接下载使用。

得益于模型架构和推理框架的深度协同，以及我们在推理框架、算子性能、量化算法等方面的优化，Hy3 preview 的成本相比上一代模型大幅下降。在腾讯云上，我们推出了有竞争力的API 价格和 Token Plan，个人版 Token Plan 定价最低 28 元/月。

![10.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/f38ef6a6/2026062421332393_586e508f161f26ce94633729ac56c602.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1782308006;2097668006&q-key-time=1782308006;2097668006&q-header-list=&q-url-param-list=&q-signature=cbb6d5a84923bd11deb39d7b276c4d36040dcfcd)

![11.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/f38ef6a6/2026062421333420_59b2900aa03cb2182a51cdb520b535b6.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1782308016;2097668016&q-key-time=1782308016;2097668016&q-header-list=&q-url-param-list=&q-signature=b98c23e21d02a12217dde4bb416c960116182893)

Hy3 preview 是我们重建的第一步。虽然模型效果已经取得了巨大进步，但仍存在一些已知问题，比如工具调用中的错误恢复能力不足，以及对推理超参数敏感。我们希望通过这次开源和发布，获得来自开源社区和用户的真实反馈，帮助我们提升 Hy3 正式版的实用性。
与此同时，我们也在继续扩大预训练和强化学习的规模，提升模型的智能上限，并通过与腾讯更多产品的深入协同，持续改进模型在真实场景中的实用性并探索差异化能力。

# 附录：模型得分

![12.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/f38ef6a6/2026062421340426_9eb60bc8bf2b004e4db7d1cc0d5f1d8c.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1782308047;2097668047&q-key-time=1782308047;2097668047&q-header-list=&q-url-param-list=&q-signature=ae78c5d00553296816cc74be1fa6b18765b22a08)

目录

[ 复杂推理]()[ 上下文学习和指令遵循]()[ 代码和智能体]()[ 自然对话和用户理解]()[ 产品的上线和初步反馈]()[ 开源、API、Token Plan]()[ 附录：模型得分]()

评论（0）

0/2000

### 继续阅读

![Real life is where context gets hard](https://hy-apikey-manager-1258344703.cos.ap-guangzhou.myqcloud.com/image/apikey/1782458320322476557_8ce7ceb30ecdd05c37edebb4e5658ba8.png)

Real life is where context gets hard

2026-04-30Shihan Dou and Pluto Zhou

![Stabilizing RLVR via Token-level Gradient Diagnosis and Layerwise Clipping](https://hy-apikey-manager-1258344703.cos.ap-guangzhou.myqcloud.com/image/apikey/1782458322345774148_fb89002f86c684ec6b10b23ee8459eb2.png)

Stabilizing RLVR via Token-level Gradient Diagnosis and Layerwise Clipping

2026-02-13黄冠华,许庭强,王锦波

![Learning from context is harder than we thought](https://hy-apikey-manager-1258344703.cos.ap-guangzhou.myqcloud.com/image/apikey/1782458318247956406_bb4e3dc150217983a4e78ed44d182106.png)

Learning from context is harder than we thought

2026-02-03Shihan Dou and Pluto Zhou
