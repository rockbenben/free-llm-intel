---
vendor: aws_bedrock
title: How the Amazon.com Catalog Team built self-learning generative AI at scale with Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-the-amazon-com-catalog-team-built-self-learning-generative-ai-at-scale-with-amazon-bedrock
date: 2026-01-23
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: b6828bfedfdc
---

# Amazon.com Catalog 团队如何借助 Amazon Bedrock 大规模构建自学习生成式 AI

[Amazon.com](http://amazon.com/) 的商品目录是每位客户购物体验的基础——它是产品信息的权威来源，其中的属性支撑着搜索、推荐与商品发现。当卖家上架新产品时，目录系统必须提取结构化属性——尺寸、材质、兼容性和技术规格——同时生成标题等内容，使其与客户的搜索方式相匹配。标题不是像颜色或尺码那样简单的枚举值；它必须平衡卖家意图、客户搜索行为与可发现性。这种复杂性再乘以每天数百万次的上架提交，使目录丰富化成为自学习 AI 的理想试验场。

本文将展示 Amazon Catalog 团队如何借助 [Amazon Bedrock](https://aws.amazon.com/bedrock/)构建自学习系统，在规模化运行中持续提升准确性并降低成本。

## 挑战

在生成式 AI 的部署环境中，提升模型表现需要持续投入精力。由于模型要处理数百万个商品，它们必然会遇到边缘情况、不断演变的术语，以及准确性可能下降的特定领域模式。传统做法——由应用科学家分析失败案例、更新 prompt、测试改动并重新部署——确实有效，但资源消耗大，难以跟上真实世界的体量与多样性。挑战不在于我们能否改进这些系统，而在于如何让改进可扩展、自动化，而不是依赖人工介入。在 Amazon Catalog，我们正面应对了这一挑战。各种取舍看起来无法两全：大模型能带来准确性，但无法以高效的方式扩展到我们的体量；小模型则难以处理卖家最需要帮助的那些复杂、模糊的案例。

## **方案概览**

我们的突破来自一次非常规的尝试。我们没有选择单一模型，而是部署多个更小的模型去处理同一批商品。当这些模型对某个属性提取结果一致时，我们可以信任该结果。但当它们不一致时——无论是出于真实的模糊性、上下文缺失，还是某个模型出了错——我们发现了很深刻的东西。这些分歧并不总是错误，但它们几乎总是复杂性的指示器。这促使我们设计了一套自学习系统，重新构想生成式 AI 如何扩展。多个较小的模型通过共识处理例行案例，只在出现分歧时才调用更大的模型。更大的模型被实现为一个 supervisor agent，它可以访问专门的工具做更深入的调查与分析。但 supervisor 不只是裁决争议；它还会生成可复用的学习成果，存入动态知识库，帮助预防未来整类分歧。我们只在推理时系统检测到高学习价值的情况下调用更强的模型，同时修正输出。结果是一套自学习系统：成本下降、质量上升——因为系统学会了处理那些过去会触发 supervisor 调用的边缘情况。错误率持续下降，不是靠重新训练，而是靠已解决分歧中积累的学习成果被注入到小模型的 prompt 里。下图展示了这套自学习系统的架构。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/14/Screenshot-2026-01-14-at-1.13.05 PM.png)

在这套自学习架构中，商品数据流经 generator-evaluator worker，出现分歧时被路由给 supervisor 进行调查。推理结束后，系统还会采集来自卖家（如上架更新和申诉）与客户（如退货和差评）的反馈信号。来自这些来源的学习成果会存入分层知识库，并被注入回 worker 的 prompt，形成持续改进的闭环。

下面介绍一个简化的参考架构，演示如何用 AWS 服务实现这种自学习模式。我们的生产系统还有额外的复杂性，但这个示例说明了核心组件与数据流。

这套系统可以基于 Amazon Bedrock 构建，它为多模型架构提供了必要的基础设施。Amazon Bedrock 能访问多种基础模型，这让团队可以部署像 Amazon Nova Lite 这样更小、更高效的模型作为 worker，以及像 Anthropic Claude Sonnet 这样能力更强的模型作为 supervisor——同时优化成本与性能。为了在规模化时进一步降低成本，团队还可以在 [Amazon Elastic Compute Cloud（Amazon EC2）](https://aws.amazon.com/ec2) GPU 实例上部署开源小模型，从而完全掌控 worker 模型的选择与批量吞吐优化。要把带有专门工具和动态知识库的 supervisor agent 投入生产，Bedrock AgentCore 提供了可靠地大规模部署自学习系统所需的运行时弹性、内存管理与可观测性。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/15/Supervisor_main_diag-4.png)

我们的 supervisor agent 与 Amazon 庞大的 Selection and Catalog Systems 集成。上图是简化视图，展示了该 agent 的关键特性以及支撑它的部分 AWS 服务。商品数据流经 generator-evaluator worker（Amazon EC2 与 [Amazon Bedrock Runtime](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_Operations_Amazon_Bedrock_Runtime.html)），其中一致的结果直接存储，分歧则路由给 supervisor agent（Bedrock AgentCore）。学习聚合器与 memory manager 使用 [Amazon DynamoDB](https://docs.aws.amazon.com/dynamodb/)承载知识库，学习成果被注入回 worker 的 prompt。人工审核（[Amazon Simple Queue Service（Amazon SQS）](https://aws.amazon.com/sqs)）与可观测性（[Amazon CloudWatch](https://aws.amazon.com/cloudwatch)）补全了整个架构。生产环境的实现很可能还需要额外的组件来实现扩展性、可靠性以及与现有系统的集成。

那么，我们是如何走到这个架构的？关键洞察来自一个意想不到的地方。

## **关键洞察：把分歧变成机会**

我们的视角在一次调试会话中发生了转变。当多个较小的模型（例如 Nova Lite）对商品属性产生分歧时——它们基于各自对技术术语的理解，对同一份规格做出不同解读——我们起初把这看作失败。但数据讲了另一个故事：小模型出现分歧的商品，与需要更多人审和澄清的案例相关。当模型出现分歧时，这些恰恰就是需要额外调查的商品。分歧正在暴露学习机会，但我们不可能让工程师和科学家对每个案例都深挖。supervisor agent 能以规模化方式自动完成这件事。而且关键在于，目标不只是判定哪个模型正确——而是提取学习成果，帮助预防未来出现类似分歧。这才是高效扩展的关键。分歧并不只来自推理时的 AI worker。推理之后，卖家会通过上架更新和申诉表达异议——这些信号说明我们最初的提取可能漏掉了重要上下文。客户则通过退货和差评表达异议，这往往说明商品信息与预期不符。这些推理之后的人工信号会进入同一条学习 pipeline，由 supervisor 调查其中的模式并生成学习成果，帮助预防未来商品上的类似问题。我们发现了一个甜区：AI worker 分歧率中等的属性，产出的学习成果最丰富——高到足以暴露有意义的模式，又低到说明这种模糊性是可以解决的。当分歧率过低时，通常反映的是噪声或模型的根本性局限，而不是可学习的模式——对这类情况，我们考虑改用能力更强的 worker。当分歧率过高时，说明 worker 模型或 prompt 还不够成熟，会触发过多 supervisor 调用，从而削弱这个架构带来的效率收益。这些阈值会因任务和领域而异；关键是找到属于你自己的甜区，在那里分歧代表的是值得调查的真实复杂性，而不是 worker 能力的根本缺口或随机噪声。

## 深入剖析：它是如何工作的

我们系统的核心是多个并行运行的轻量 worker 模型——一些作为 generator 提取属性，另一些作为 evaluator 评估这些提取结果。这些 worker 可以用非 agentic 的方式、以固定输入实现，因此对批处理友好且易于扩展。generator-evaluator 模式制造出有产出的张力，概念上类似[生成对抗网络](https://aws.amazon.com/what-is/gan/)（GAN）中的那种张力，只不过我们的方法是在推理时通过 prompt 实现，而不是在训练时。我们会明确要求 evaluator 保持挑剔，让它们审视提取结果中的模糊之处、缺失的上下文或可能的误解。这种对抗式动态会暴露代表真实复杂性的分歧，而不是让模糊案例悄悄通过。当 generator 与 evaluator 意见一致时，我们对结果有较高信心，并以最小的算力成本处理它。这条共识路径覆盖了大多数商品属性。当它们不一致时，我们就识别出一个值得调查的案例——触发 supervisor 去解决争议并提取可复用的学习成果。

我们的架构把分歧视为通用的学习信号。推理时，worker 之间的分歧能捕捉模糊性。推理之后，卖家反馈能捕捉与意图的偏差，客户反馈能捕捉与预期的偏差。这三条通道都汇入 supervisor，由它提取学习成果，从而全面提升准确性。当 worker 出现分歧时，我们调用 supervisor agent——一个能力更强的模型，由它裁决争议并调查分歧的成因。supervisor 会判断 worker 缺少哪些上下文或推理，这些洞察就成为面向未来案例的可复用学习成果。例如，当 worker 基于某些技术术语对某个商品的使用场景分类产生分歧时，supervisor 进行了调查并澄清：只看这些术语是不够的——还需要结合视觉上下文和其他指标。supervisor 因此生成了一条关于如何为该商品类目正确加权不同信号的学习成果。这条学习成果立即更新了知识库，在被注入到类似商品的 worker prompt 后，帮助在数千个条目上预防了未来的分歧。虽然理论上 worker 可以就是 supervisor 所用的同一个模型，但使用更小的模型对规模化效率至关重要。架构上的优势正来自这种不对称：轻量 worker 通过共识处理例行案例，而能力更强的 supervisor 只在分歧暴露出高价值学习机会时才被调用。随着系统积累学习成果、分歧率下降，supervisor 调用会自然减少——效率收益直接内建于架构之中。这种 worker 与 supervisor 的异构性也带来了更丰富的调查。由于 supervisor 是被选择性调用的，它可以负担得起拉取额外信号——客户评论、退货原因、卖家历史——这些信号为每个商品都检索并不现实，但在解决复杂分歧时能提供关键上下文。当这些信号产出关于客户希望商品信息如何呈现的可泛化洞察时——哪些属性该突出、什么术语更受欢迎、如何组织规格——由此得到的学习成果就能让类似商品上的未来推理受益，而无需再次检索这些高成本信号。随着时间推移，这会形成反馈闭环：更好的商品信息带来更少的退货和差评，而这又反映出客户满意度的提升。

### 知识库：让学习成果可扩展

supervisor 在单个商品层面调查分歧。我们要处理数百万个条目，因此需要一种可扩展的方式，把这些针对单个商品的洞察转化为可复用的学习成果。我们的聚合策略会随上下文调整：高频模式被综合为更宽泛的学习成果，而独特或关键的案例则单独保留。我们采用分层结构，由基于大语言模型（LLM）的 memory manager 在知识树中导航，为每条学习成果安排位置。它从根节点开始，逐层遍历类目与子类目，在每个层级决定是沿已有路径继续、创建新分支、与已有知识合并，还是替换过时信息。这种动态组织方式让知识库能够随着新模式的出现在演进中保持逻辑结构。推理时，worker 会根据商品类目在 prompt 中收到相关的学习成果，自动纳入过往分歧积累的领域知识。知识库还带来了可追溯性——当某个提取结果看起来不对时，我们可以精确定位究竟是哪条学习成果影响了它。这使审计从一项无法扩展的任务变成切实可行的任务：团队不必再抽样审查数百万条输出——那种做法的人力投入会随规模线性增长——而是可以直接审计知识库本身，无论推理量多大，它的规模基本固定。领域专家可以直接新增或完善条目来参与，无需重新训练。一条精心编写的学习成果就能立即提升数千个商品的准确性。知识库连接了人类专业知识与 AI 能力，让自动化学习成果与人的洞察协同工作。

## 经验与最佳实践

**这套自学习架构最适合的场景：**

- **高频次推理**：输入的多样性会带来可累积的学习效果
- **质量至关重要的应用**：共识本身提供了天然的质量保障
- **不断演进的领域**：新模式和术语持续涌现

它不太适合低频场景（分歧不足，难以学习），也不适合规则固定不变的用例。

**关键成功要素：**

- **定义分歧：**在 generator-evaluator 成对的设置下，当 evaluator 判定提取结果需要改进时就构成分歧。若使用多个 worker，阈值要相应调整。关键在于维持 worker 之间那种有产出的张力。如果分歧率落在有效区间之外（过低或过高），就应考虑换用能力更强的 worker 或改进 prompt。
- **跟踪学习效果：**分歧率必须随时间下降——这是你的首要健康度指标。如果分歧率保持不变，请检查知识检索、prompt 注入或 evaluator 的挑剔程度。
- **知识组织：**以分层结构组织学习成果，并保持其可执行性。抽象的原则没有帮助；具体、明确的学习成果才能直接改善未来的推理。

**常见陷阱**

- **只看成本不看智能：**成本下降是副产品，不是目标
- **橡皮图章式 evaluator：**只会给 generator 输出盖章通过的 evaluator 不会暴露有意义的分歧——要 prompt 它们主动质疑和批评提取结果
- **学习成果提取不力：**supervisor 必须识别可泛化的模式，而不只是修正个别案例
- **知识腐化：**缺乏组织，学习成果会变得难以检索、无法使用

关键洞察：把分歧率的下降作为你的北极星指标——它说明系统在真正学习。

**部署策略：两种做法**

- **先学后部署：**从基础 prompt 起步，让系统在预生产环境中激进地学习。之后由领域专家审计知识库——而不是逐条审计输出——以确保学到的模式符合预期结果。审核通过后，带着经过验证的学习成果上线部署。这非常适合你还不清楚 *好* 是什么样子的新用例——分歧能帮助发现正确的模式，知识库审计让你在上线前就能塑造它们。
- **边部署边学：**从精细的 prompt 和良好的初始质量起步，然后在生产环境中通过持续学习不断改进。这最适合已经理解透彻的用例——你可以预先定义质量标准，但仍希望随时间捕捉领域特有的细微差别。

两种做法使用同一套架构——区别在于你是在探索新领域，还是在优化熟悉的领域。

## 结论

一项始于目录丰富化的实验揭示了一个根本事实：AI 系统不必被冻结在某个时间点。通过把分歧当作学习信号而非失败，我们构建出一套架构，能在实际使用中积累领域知识。我们看着系统从通用理解演进为领域专长。它学会了行业特有的术语。它发现了因类目而异的上下文规则。它适应了任何预训练模型都不会遇到的要求——而这一切都无需重新训练，靠的是存入知识库、再注入 worker prompt 的学习成果。对于要把类似架构投入运营的团队，Amazon Bedrock AgentCore 提供了专门为此打造的能力：

- [AgentCore Runtime ](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html) 为例行案例快速做出共识决策，同时在 supervisor 调查复杂分歧时支持扩展推理
- [AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) 让你看清哪些学习成果真正产生影响，帮助团队优化知识传播并在规模化时保持可靠性

这些意义超出了目录管理的范畴。高流量的 AI 应用都能从这一过程中受益——而 Amazon Bedrock 访问多种模型的能力让这套架构易于实现。关键洞察是：我们已经从问“该用哪个模型？”转向问“如何构建能学习我们特定模式的系统？”。无论你是为新用例先学后部署，还是为成熟用例边部署边学，实现起来都很直接：先选适合任务的 worker，再选一个 supervisor，然后让分歧驱动学习。有了正确的架构，每一次推理都能成为积累领域知识的机会。这不仅是扩展——这是把组织知识嵌入到你的 AI 系统之中。

**致谢**
 本工作离不开 **Ankur Datta**（Senior Principal Applied Scientist —— Everyday Essentials Stores 的科学负责人）、**Zhu Cheng**（Applied Scientist）、**Xuan Tang**（Software Engineer）、**Mohammad Ghasemi**（Applied Scientist）的贡献与支持。我们诚挚感谢他们在设计、实现、多次富有成效的头脑风暴以及所有富有洞见的想法与建议中的贡献。

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/tarik.jpeg)**Tarik Arici** 是 Amazon Selection and Catalog Systems（ASCS）的 Principal Scientist，在那里开创面向大规模目录质量提升的自学习生成式 AI 系统设计。他的工作聚焦于构建能在生产使用中自动积累领域知识的 AI 系统——从客户评论与退货、卖家反馈以及模型分歧中学习，在提升质量的同时降低成本。Tarik 拥有佐治亚理工学院电气与计算机工程博士学位。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/sameer.jpeg)**Sameer Thombare** 是 Amazon 的 Senior Product Manager，在产品管理、类目与损益管理方面拥有十余年经验，涉及重型工程、电信、金融和电子商务等多个行业。Sameer 热衷于打造持续改进的闭环系统，并在 Amazon Selection and Catalog Systems（ASCS）领导战略举措，构建精密的自我学习闭环系统，综合来自客户、卖家和供应链运营的信号以优化结果。Sameer 拥有印度管理学院班加罗尔分校的 MBA 学位和孟买大学的工程学位。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/1194689-Amin-2025.jpg)**Amin Banitalebi** 于 2014 年在加拿大不列颠哥伦比亚大学（UBC）获得数字媒体博士学位。此后他承担过多种应用科学岗位，覆盖计算机视觉、自然语言处理、推荐系统、经典机器学习和生成式 AI 等领域。Amin 参与撰写了 90 余篇论文与专利。他目前是 Amazon Everyday Essentials 的应用科学经理。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/puneet.jpeg)**Puneet Sahni** 是 Amazon Selection and Catalog Systems（ASCS）的 Senior Principal Engineer，在那里已投入 8 年以上改进目录数据的完整性、一致性与正确性。他专精于目录数据建模及其在提升 Selling Partner 与客户体验方面的应用，同时利用 ML/DL 与基于 LLM 的丰富化来推动目录数据质量的改进。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/erdinc.jpeg)**Erdinc Basci** 于 2015 年加入 Amazon，拥有超过 23 年的技术行业经验。在 Amazon，他主导了目录系统架构的演进——包括数据摄取 pipeline、优先级处理和流量整形——以及目录数据架构方面的改进，例如分段报价、按需制造商品的产品规格和目录数据实验。Erdinc 在 Amazon 各项服务中倡导动手实践的绩效工程文化，释放了超过 10 亿美元的年化成本节约，并在核心 Stores 服务上取得 20% 以上的延迟改善。他目前专注于提升 Amazon 范围内生成式 AI 应用的性能和 GPU 效率。Erdinc 拥有土耳其比尔肯特大学计算机科学学士学位和美国西雅图大学的 MBA 学位。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/mey.jpeg)**Mey Meenakshisundaram** 是 Amazon Selection and Catalog Systems 的 Director，领导创新的 GenAI 方案，把 Amazon 全球商品目录打造成一流的商品信息来源。他的团队开创先进的机器学习技术，包括 multi-agent 系统和大语言模型，用来自动丰富商品属性并大规模提升目录质量。目录中高质量的商品信息对于让客户愉快地找到合适商品、帮助销售伙伴高效上架商品，以及让 Amazon 运营减少人工投入都至关重要。
