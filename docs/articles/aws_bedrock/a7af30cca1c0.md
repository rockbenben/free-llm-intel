---
vendor: aws_bedrock
title: Sentiment Analysis with Text and Audio Using AWS Generative AI Services: Approaches, Challenges, and Solutions
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/sentiment-analysis-with-text-and-audio-using-aws-generative-ai-services-approaches-challenges-and-solutions
date: 2026-01-09
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 801ab4c1685e
---

# 使用 AWS 生成式 AI 服务进行文本与音频情感分析：方法、挑战与解决方案

*本文由 Instituto de Ciência e Tecnologia Itaú（ICTi）与 AWS 合作撰写。*

情感分析在现代企业中变得越来越重要，它能揭示客户的意见、满意度水平与潜在的不满。由于交互主要通过文本（例如社交媒体、聊天应用与电商评论）或语音（例如呼叫中心与电话）进行，组织需要稳健的方法来规模化解读这些信号。通过准确识别并分类客户的情绪状态，企业可以提供更主动、更贴合的服务体验，从而正面影响客户满意度与忠诚度。

尽管具有战略价值，落地完整的情感分析方案仍面临若干挑战。语言歧义、文化差异、地区方言、讽刺表达以及海量实时数据，都要求架构具备可扩展性与灵活性。此外，在基于语音的情感分析中，如果把音频转写后仅当作文本来处理，语调与韵律这类关键特征就会丢失。Amazon Web Services（AWS）提供了一整套工具来应对这些挑战。AWS 提供的服务涵盖从音频采集与转写（[Amazon Transcribe](https://aws.amazon.com/transcribe/)）到文本情感分类（[Amazon Comprehend](https://aws.amazon.com/blogs/machine-learning/sentiment-analysis-with-text-and-audio-using-aws-generative-ai-services-approaches-challenges-and-solutions/Comprehend)），还包括智能联络中心方案（[Amazon Connect](https://aws.amazon.com/connect/)）与实时数据流（[Amazon Kinesis](https://aws.amazon.com/kinesis/)）。

本文源自 AWS 与 Instituto de Ciência e Tecnologia Itaú（ICTi）之间的战略性科研合作——ICTi 是拉丁美洲最大的私营银行 Itaú Unibanco 维护的研发中心——探讨文本与音频两类情感分析的技术细节。我们呈现了对比多个机器学习（ML）模型与服务的实验，讨论各种方法的取舍与陷阱，并说明如何编排 AWS 服务来构建稳健的端到端方案。我们还给出对未来方向的洞察，包括面向大语言模型（LLM）的更高级 prompt engineering，以及扩展基于音频的分析范围以捕捉纯文本数据可能遗漏的情绪线索。我们分两个阶段探讨基于音频的情感分析：

- **Stage 1** – 把音频转写为文本，并使用 LLM 进行情感分析
- **Stage 2** – 直接使用音频模型从音频信号中分析情感

## 文本情感分析

本节讨论把音频转写为文本并使用 LLM 进行情感分析的方法。

### 挑战与特征

该方法面临以下挑战：

- **数据来源多样** – 文本交互来自众多渠道——社交网络、电商平台、聊天机器人与服务台工单——各有独特的格式与限制。例如，社交媒体文本可能包含话题标签、emoji 或字符数限制，而聊天消息可能包含缩写与领域特定行话。因此，稳健的文本处理 pipeline 必须包含适当的数据清洗与预处理步骤，以把这些差异规范化。
- **自然语言歧义** – 人类语言往往含糊且依赖上下文。讽刺、反语与比喻性表达会让表层自然语言处理（NLP）技术的分类变得复杂。尽管深度神经网络——例如 BERT、RoBERTa 与基于 Transformer 的架构——已被证明更擅长捕捉细微语义，但要完整涵盖富有创造性或依赖上下文的语言用法仍是一项持续的挑战。
- **多语言与方言的考量** – 像 Itaú Unibanco 这样的全球性企业会遇到多种语言与地区方言，每一种都可能需要专门的模型或额外的训练数据。主要以某一种语言或方言训练的情感模型，在面对另一种语言的俚语、口语表达或独特语法结构时可能失效。

### 测试的模型与理由

在实验中，我们评估了多个 LLM，重点关注情感分类。其中包括可通过 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 与 [Amazon SageMaker JumpStart](https://aws.amazon.com/sagemaker-ai/jumpstart/) 获取的流行基础模型（FM），例如 Meta 的 Llama 3 70B、Anthropic 的 Claude 3.5 Sonnet、Mistral AI 的 Mixtral 8x7B 以及 [Amazon Nova Pro](https://aws.amazon.com/nova/)。每项服务都依据具体需求提供独特优势。例如，Amazon Bedrock 通过基于 API 的统一无服务器接口对接多个 LLM 提供方，简化了大规模实验。SageMaker AI 则提供有服务器的托管体验，可通过易用的 UI 或基于 API 的部署与管理来使用流行 FM。Amazon Bedrock 与 SageMaker AI 都简化了模型托管、可扩展性、安全与成本优化等运营事项——这些正是企业采用生成式 AI 的关键收益。

我们对每个模型测试了两种配置：

- **Zero-shot 或 few-shot prompting** – 使用通用 prompt 对文本进行情感分类
- **微调** – 在领域特定的情感数据上适配模型，以评估这种专门训练是否提升性能，或是有过拟合风险

### 用于文本分析的 AWS 服务

Amazon 提供一整套服务来帮助简化文本分析流程。在本文中，我们使用以下服务构建了一个文本分析服务：

- [Amazon Bedrock](https://aws.amazon.com/bedrock/) – 在单一、安全的界面中提供对不同提供方预训练 FM 的无服务器访问——尤其是对 Anthropic Claude 这类闭源权重模型的访问。这样无需管理底层基础设施即可快速测试多个模型。
- [Amazon SageMaker AI](https://aws.amazon.com/sagemaker-ai/) – 提供对 Llama、Mistral、DeepSeek 等最新开源 FM 的访问。使用 SageMaker AI，你可以选择通过 [Amazon SageMaker JumpStart](https://aws.amazon.com/sagemaker-ai/jumpstart/) 简化 FM 部署——这是一个 ML 与生成式 AI 托管中枢，既提供以简单 UI 或 API 部署数百个 FM 的方式，也能帮你轻松地把偏好的 FM 与架构部署到托管的 NVIDIA GPU 基础设施上。
- [Amazon Comprehend](https://aws.amazon.com/comprehend/) – 一款具备文本分析能力的 AI 服务，包括情感分析、实体识别与主题建模。它可作为基线，也可集成到更高级的 LLM 工作流中，形成更完整的 pipeline。
- [Amazon Kinesis](https://aws.amazon.com/kinesis/) – 负责从多种来源（例如社交媒体信息流、日志流或实时客户聊天会话）实时摄取与流式传输文本数据。

一个简化架构可能包含以下组件：

- 使用 Kinesis 摄取数据，从多种来源捕获文本
- 使用 [AWS Lambda](https://aws.amazon.com/lambda) 或 [Amazon EMR](https://aws.amazon.com/emr/) 进行数据预处理，用于规范化、分词与过滤。
- 使用通过 Amazon Bedrock 或 SageMaker AI 访问的 LLM 进行模型推理
- 在 [Amazon Simple Storage Service](https://aws.amazon.com/s3)（Amazon S3）或 [Amazon Redshift](https://aws.amazon.com/redshift) 中存储与分析，用于长期分析、报表与可视化

### 文本实验结果

下表汇总了所测各模型的性能指标（accuracy、precision、recall）。每个模型都在同一份文本数据集上评估，目标是把句子分类为正面、负面或中性。

| **模型** | **Accuracy** | **Precision** | **Recall** |
| --- | --- | --- | --- |
| Amazon SageMaker JumpStart Llama 3 70B Instruct v1 | **0.189** | 0.527 | **0.189** |
| Amazon Bedrock Anthropic Claude 3.5 Sonnet 2024-06-20-v1 | 0.187 | 0.44 | 0.187 |
| Amazon SageMaker Mixtral 8x7B Instruct v0 | 0.164 | **0.545** | 0.164 |
| Amazon Bedrock Amazon Nova Pro v1 | 0.159 | 0.239 | 0.16 |
| 闭源最先进 LLM 1（>50B） | 0.159 | 0.025 | 0.159 |
| 闭源最先进 LLM 2（>50B） | 0.159 | 0.025 | 0.159 |

### 结果分析

我们从结果中观察到以下几点：

- **整体表现偏低** – 所有模型在识别情感极性上的准确率都相对较低。这说明纯文本输入可能无法提供足够的上下文或情绪线索，尤其是对讽刺、反语这类更微妙的表达。
- **微调的影响** – 两个微调后的 OpenAI 模型取得了高于多数其他配置的指标，不过性能的跃升也可能意味着过拟合。只有当存在强烈情绪指示时，它们才会一致地把句子标记为非中性。
- **模型差异** – Meta 的 Llama 3 70B 与 Anthropic 的 Claude 3.5 Sonnet 表现优于部分其他基础模型，但仍低于微调后的 OpenAI 方案。这可能反映了它们的预训练目标，以及其原始训练数据与我们这项情感分类任务之间的领域差异。

### 文本分析的未来方向

你可以从以下方面考虑扩展基于文本的分析：

- **更高级的 prompt engineering** – 当前实验使用了直白的 chain-of-thought prompt。未来工作可以探索更精细的 few-shot 或 zero-shot prompt 设计，包括 “buffer of thoughts” 这类高级推理策略，或精心针对领域定制的 prompting。
- **多模态输入** – 引入副语言信息（例如语调或说话人重音）可能会提升基于文本的分类效果。这类数据可以编码为元数据，或由辅助模型提取，以丰富文本上下文。
- **语言覆盖** – 扩展到非英语语料并训练领域特定或多语言模型，很可能提升真实部署中的泛化能力。

## 音频情感分析

本节讨论直接使用音频模型从音频信号中分析情感的方法。

### 挑战与特征

该方法面临以下挑战：

- **语调与韵律** – 口语携带声学线索（音色、音高、音量、语速与节奏），它们极大地影响被感知到的情感。“Hi, how are you?” 这样一句简单问候，可以是真心热情，也可以是消极的讽刺，取决于语调。传统的语音转文本 pipeline 会丢弃这些非语言线索，可能削弱情感信号。
- **语音转文本转换** – 许多音频情感分析系统依赖 [ASR (Automatic Speech Recognition)](https://huggingface.co/tasks/automatic-speech-recognition) 生成转写文本，再喂给基于文本的情感模型。虽然这有利于内容理解，但纯文本分析忽略了韵律特征——这也是直接基于音频的情感分类引起研究兴趣的原因之一。
- **噪声与录音质量** – 真实世界的音频常常包含背景噪声、重叠对话或低保真录音。模型必须对这类条件保持稳健，才能在呼叫中心或客户支持热线等环境中可用。

### 实验数据集

我们使用了两种不同类型的数据集，各自聚焦语音情绪的不同侧面：

- **Type 1** – 一个经过整理的短句集合，以不同情绪语调录制。数据最初按唤醒度（arousal，例如快乐、愤怒、厌恶）标注，随后按效价（valence，正面、负面、中性）重新标注。被标为“surprise”的录音被移除，因为它既可表现为正面也可表现为负面。来源包括 [CREMA-D](https://www.kaggle.com/datasets/ejlok1/cremad)、[RAVDESS](https://www.kaggle.com/datasets/uwrfkaggler/ravdess-emotional-speech-audio) 与 [TESS](https://tspace.library.utoronto.ca/handle/1807/24487)。
- **Type 2** – 包含更多样的句子，每句标注为正面、负面或中性。语句的多样性与复杂性使该数据集难度显著更高。来源包括 [Audio Speech Sentiment dataset](https://www.kaggle.com/datasets/imsparsh/audio-speech-sentiment) 与 [MELD](https://www.kaggle.com/datasets/zaber666/meld-dataset)。

### 测试的模型与理由

我们评估了三个主流的语音模型：

- **HuBERT (Hidden Unit BERT)** – 采用自监督 Transformer，学习音频信号中的隐藏聚类分配。HuBERT 擅长捕捉对情绪检测至关重要的韵律与声学模式。
- **Wav2Vec** – 理念与 HuBERT 相似，Wav2Vec 使用 Transformer 编码器主干，直接从原始音频学习强大的表示。其自监督训练方案在标注数据有限时非常有效。
- **Whisper** – 一个基于 Transformer 的编码器-解码器，最初为稳健的语音识别而设计。虽然它的重点在转写与翻译，我们仍测试了它为下游情感分类任务提取 embedding 的能力。

### 用于音频分析的 AWS 服务

为了简化训练与推理 pipeline，我们使用了以下 AWS 服务：

- [Amazon SageMaker Studio](https://aws.amazon.com/sagemaker/ai/studio/) – 可在专用实例（例如启用 GPU 的实例）上快速建立训练任务，而无需承担显著的基础设施开销。每个模型（HuBERT、Wav2Vec、Whisper）都在独立的 SageMaker 会话中训练与验证。
- [Amazon Transcribe](https://aws.amazon.com/transcribe/) – 对于需要语音转文本的工作流，Amazon Transcribe 提供可扩展且准确的 ASR。虽然它不是直接基于音频的情感分析方法的重点，但它通常被集成到联络中心架构中，那里的文本转写稿也用于分析或合规检查。

一个代表性架构可以包括：Kinesis 负责音频摄取，Lambda 负责编排预处理或路由选择（例如走直接基于音频的情感分析，还是转写后走基于文本的分析），Amazon S3 负责存储最终结果。下图展示了这个示例架构。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/03/ml-19126-image-1.jpg)

### 音频实验结果

我们的评估考察了在 Type 1 与 Type 2 数据集各自独立测试划分上的分类准确率。总体而言，三个模型在 Type 1 上的表现都高于 Type 2。下表汇总了这些结果。

| **数据集类型** | **情感** | **Wav2Vec ** | **Hubert** | **Whisper ** |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  | **Precision** | **Recall** | **F1** | **Accuracy** | **Precision** | **Recall** | **F1** | **Accuracy** | **Precision** | **Recall** | **F1** | **Accuracy** |
| Type 1：固定短语 | 负面 | 0.85 | 0.82 | 0.83 | 0.78 | 0.94 | 0.83 | 0.88 | 0.84 | 0.98 | 0.89 | 0.93 | 0.91 |
| Type 1：固定短语 | 中性 | 0.57 | 0.95 | 0.72 | 0.61 | 0.98 | 0.75 | 0.8 | 0.96 | 0.87 |  |  |  |
| Type 1：固定短语 | 正面 | 0.86 | 0.49 | 0.63 | 0.84 | 0.74 | 0.79 | 0.82 | 0.92 | 0.86 |  |  |  |
| Type 2：变化短语 | 负面 | 0.55 | 0.39 | 0.46 | 0.54 | 0.56 | 0.37 | 0.42 | 0.55 | 0.6 | 0.46 | 0.52 | 0.58 |
| Type 2：变化短语 | 中性 | 0.59 | 0.73 | 0.65 | 0.6 | 0.74 | 0.66 | 0.63 | 0.71 | 0.67 |  |  |  |
| Type 2：变化短语 | 正面 | 0.35 | 0.31 | 0.33 | 0.38 | 0.35 | 0.36 | 0.44 | 0.47 | 0.46 |  |  |  |

### 结果分析

我们从结果中观察到以下内容：

- **Type 1** – 由于同样的句子以不同情绪语调重复出现，模型更多关注声学线索而非内容。这带来了更高的准确率——尤其是在区分高唤醒（愤怒、兴奋）与低唤醒（悲伤、平静）状态方面。
- **Type 2** – 面对更多样的句子时性能显著下降。此时，词汇内容与语境的差异盖过了纯韵律特征。模型难以在多样的句子结构、说话人风格与情绪表达之间泛化。

### 音频分析的未来方向

你可以从以下方面考虑扩展基于文本的分析：

- **数据多样性** – 把数据集扩展到包含更多语言、地区口音与环境条件，可能提升这些模型的泛化能力。
- **多模态融合** – 把直接的音频 embedding（韵律、语调）与文本分析（词汇内容）结合起来，可能得到更丰富的情感表示。这在客服场景中尤其相关，因为语义内容与情绪语气都很重要。
- **实时推理** – 对于使用 Amazon Connect 的实时联络中心支持等应用，实时推理 pipeline 至关重要。研究人员可以研究基于流的模型推理方法（例如逐块或帧级处理），以便即时获得客户情感的反馈并据此调整应答。

## 结语

情感分析——无论作用于文本还是音频——都能提供关于客户感知的有力洞察，使企业能够采取更主动、更有同理心的互动策略。然而，技术门槛并不低：

- **文本** – 歧义、反语与有限的上下文会妨碍纯文本分类。即便是经过微调的 LLM，如果缺少细致的数据整理、高级 prompt engineering 或额外的元数据，也可能表现不佳。
- **音频** – 直接分析音频能捕捉转写中常被丢失的韵律与声学线索。然而，环境噪声、重叠语音与说话人多样性会让训练稳健模型变得复杂。

AWS 提供了一整套服务，覆盖端到端的情感分析 pipeline：

- **数据摄取** – Kinesis 用于实时文本与音频流
- **预处理** – Lambda 与 Amazon EMR 用于数据清洗、特征提取与变换
- **转写（可选）** – 如果需要文本与音频结合的方法，可用 Amazon Transcribe 把音频转为文本
- **情感分类** – AWS 提供以下选择：**文本** – Amazon Comprehend，或通过 Amazon Bedrock 与 SageMaker AI 访问的 FM **音频** – 在 SageMaker AI 中训练的自定义模型（例如 HuBERT、Wav2Vec、Whisper）
- **客户互动** – Amazon Connect 用于智能联络中心，可实现实时情感反馈闭环

归根结底，在基于音频、基于文本或混合方法之间的选择取决于用例与可用数据。直接基于音频的方法可以捕捉在呼叫中心交互中至关重要的情绪细微差别——尤其是在问候或情绪激烈的对话中——而基于文本的方法在聊天、社交媒体与评论分析等场景中往往更容易规模化部署。通过把 AWS 云端能力与严谨的 ML 方法论结合，企业可以定制出在准确率、可扩展性与成本效益之间取得平衡的情感分析方案。未来的探索可能进一步整合多模态数据流、高级 prompt engineering 与领域特定微调，持续提升我们解读并回应“客户之声”的能力。

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/06/caique-1.png)Caique de Almeida** 是 Itaú 科学技术研究院（ICTI）的 Staff Data Scientist。他专注于自然语言处理、深度学习与云架构，把应用研究与生产级 AI 系统衔接起来。他持有 11 项 AWS 认证，并把这份云上专长用于构建可扩展、可靠的 AI 方案。他当前的工作集中在为金融服务构建面向客户的 agent、在金融领域应用 AI，以及研究生成式 AI 中的事实性与推理。工作之外，他喜欢骑行。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/06/guilherme-1.jpg)Guilherme Rinaldo** 是 Instituto de Ciência e Tecnologia Itaú（ICTI）的 Staff AI Engineer 兼研究者，在那里构建并评估面向文本与语音的生成式 AI 系统，包括基于 LLM 的 agent 与深度学习模型。凭借 8 年经验，他把工作从研究原型推进到生产 pipeline，重点在可靠性、安全性与严谨评估。他的兴趣包括持续学习、自演进 agent 与大规模模型监控。工作之外，Guilherme 喜欢写作、旅行与玩策略游戏。你可以在 [LinkedIn](https://www.linkedin.com/in/guilhermerinaldo/) 上找到 Guilherme。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/06/paulo-1.jpg)Paulo Finardi** 是 Itaú 科学技术研究院（ICTI）的首席数据科学家。他在深度学习与自然语言处理领域有 10 年以上经验，专注于 AI 在金融、仿真与数字孪生中的应用。他的工作横跨大规模应用研究以及 AI 战略与创新。工作之外，他喜欢骑行。你可以在 [LinkedIn](https://www.linkedin.com/in/paulo-finardi-964a1425b/) 上找到 Finardi。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/06/victor-1.jpg)Victor Costa Beraldo** 是 Itaú 科学技术研究院（ICTi）的首席数据科学家，工作在语音与 AI 的交汇处。凭借信号处理与深度学习的扎实背景，他专注于基于语音的方案，包括 ASR、ASV、情绪识别与实时音频处理，在金融服务中把应用研究与生产系统衔接起来。工作之外，他喜欢看足球比赛。你可以在 [LinkedIn](https://www.linkedin.com/in/victor-costa-beraldo-99746b144/) 上找到 Victor。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/06/vini-1.png)Vinicius Caridá** 是 Itaú Unibanco 的 Distinguished Data Scientist，也是 Itaú 科学技术研究院（ICTI）科学技术委员会的成员。他的工作横跨生成式 AI、自然语言处理、虚拟助手、推荐系统、控制系统以及端到端 MLOps 生命周期。Vinicius 很荣幸被评为 AWS AI Hero，在该计划中自豪地代表拉丁美洲。他当前的工作聚焦于为金融服务构建面向客户的 AI agent，并推进生成式模型中的事实性与推理。工作之外，他热爱与技术社区相互教学相长，并陪伴妻子 Jerusa 与女儿 Olivia。你可以在 [LinkedIn](https://www.linkedin.com/in/viniciuscarida/) 上找到 Vinicius。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/10/PranavMurthy-ProfilePhoto.jpg)Pranav Murthy** 是 AWS 的资深生成式 AI 数据科学家，专长于帮助组织在 Amazon SageMaker AI 上用生成式 AI、深度学习与机器学习创新。在过去 10 多年里，他开发并扩展了先进的计算机视觉（CV）与自然语言处理（NLP）模型来解决高影响力问题——从优化全球供应链到实现实时视频分析与多语言搜索。你可以在 [LinkedIn](https://www.linkedin.com/in/pranavvm26/) 上找到 Pranav。
