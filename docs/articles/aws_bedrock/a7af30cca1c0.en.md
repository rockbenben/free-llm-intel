---
vendor: aws_bedrock
title: Sentiment Analysis with Text and Audio Using AWS Generative AI Services: Approaches, Challenges, and Solutions
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/sentiment-analysis-with-text-and-audio-using-aws-generative-ai-services-approaches-challenges-and-solutions
date: 2026-01-09
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 89392e8d0e08
---

# Sentiment Analysis with Text and Audio Using AWS Generative AI Services: Approaches, Challenges, and Solutions

*This post is co-written by Instituto de Ciência e Tecnologia Itaú (ICTi) and AWS.*

Sentiment analysis has grown increasingly important in modern enterprises, providing insights into customer opinions, satisfaction levels, and potential frustrations. As interactions occur largely through text (such as social media, chat applications, and ecommerce reviews) or voice (such as call centers and telephony), organizations need robust methods to interpret these signals at scale. By accurately identifying and classifying a customer’s emotional state, companies can deliver more proactive, customized experiences, positively impacting customer satisfaction and loyalty.

Despite its strategic value, implementing comprehensive sentiment analysis solutions presents several challenges. Language ambiguity, cultural nuances, regional dialects, sarcastic expressions, and high volumes of real-time data all demand scalable and flexible architectures. Additionally, in voice-based sentiment analysis, critical features such as intonation and prosody can be lost if the audio is transcribed and treated purely as text. Amazon Web Services (AWS) offers a suite of tools to address these challenges. AWS provides services ranging from audio capture and transcription ([Amazon Transcribe](https://aws.amazon.com/transcribe/)) to text sentiment classification ([Amazon Comprehend](https://aws.amazon.com/blogs/machine-learning/sentiment-analysis-with-text-and-audio-using-aws-generative-ai-services-approaches-challenges-and-solutions/Comprehend)), as well as intelligent contact center solutions ([Amazon Connect](https://aws.amazon.com/connect/)) and real-time data streaming ([Amazon Kinesis](https://aws.amazon.com/kinesis/)).

This post, developed through a strategic scientific partnership between AWS and the Instituto de Ciência e Tecnologia Itaú (ICTi), P&D hub maintained by Itaú Unibanco, the largest private bank in Latin America, explores the technical aspects of sentiment analysis for both text and audio. We present experiments comparing multiple machine learning (ML) models and services, discuss the trade-offs and pitfalls of each approach, and highlight how AWS services can be orchestrated to build robust, end-to-end solutions. We also offer insights into potential future directions, including more advanced prompt engineering for large language models (LLMs) and expanding the scope of audio-based analysis to capture emotional cues that text data alone might miss. We explore audio-based sentiment analysis in two stages:

- **Stage 1** – Transcribe audio into text and perform sentiment analysis using LLMs
- **Stage 2 **– Analyze sentiment directly from the audio signal using audio models

## Sentiment analysis in text

In this section, we discuss the method of transcribing audio into text and performing sentiment analysis using LLMS.

### Challenges and characteristics

This method presents the following challenges:

- **Variety of data sources** – Textual interactions emerge from numerous channels—social networks, ecommerce platforms, chatbots, and helpdesk tickets—each with unique formats and constraints. For instance, social media text might contain hashtags, emojis, or character limits, whereas chat messages might include acronyms and domain-specific jargon. A robust text-processing pipeline must therefore include appropriate data cleaning and preprocessing steps to normalize these variations.
- **Ambiguity of natural language **– Human language is often ambiguous and context-dependent. Sarcasm, irony, and figurative expressions complicate classification by superficial natural language processing (NLP) techniques. Although deep neural networks—such as BERT, RoBERTa, and Transformers-based architectures—have proven more adept at capturing nuanced semantics, it remains an ongoing challenge to fully account for creative or context-dependent language usage.
- **Multilingual and dialect considerations **– Global enterprises like Itaú Unibanco encounter multiple languages and regional dialects, each requiring specialized models or additional training data. A sentiment model trained primarily on one language or dialect might fail when confronted with slang, colloquialisms, or distinctive grammatical structures from another.

### Tested models and rationale

In our experiments, we evaluated several LLMs with a focus on sentiment classification. Among them were popular foundation models (FMs) available through [Amazon Bedrock](https://aws.amazon.com/bedrock/) and [Amazon SageMaker JumpStart](https://aws.amazon.com/sagemaker-ai/jumpstart/), such as Meta’s Llama 3 70B, Anthropic’s Claude 3.5 Sonnet, Mistral AI’s Mixtral 8x7B, and [Amazon Nova Pro](https://aws.amazon.com/nova/). Each service offers unique advantages based on specific needs. For example, Amazon Bedrock simplifies large-scale experimentation by providing a unified, serverless interface to multiple LLM providers through API-based access. SageMaker AI provides a serverful managed experience for accessing popular FMs with a user-friendly UI or API-based deployment and management. Both Amazon Bedrock and SageMaker AI streamline operational concerns like model hosting, scalability, security, and cost optimization—key benefits for enterprise adoption of generative AI.

We tested each model in two configurations:

- **Zero-shot or few-shot prompting** – Using generic prompts to classify sentiment in text
- **Fine-tuning** – Adapting the model on domain-specific sentiment data to assess whether this specialized training improved performance or risked overfitting

### AWS services for text analysis

Amazon offers a suite of services to help streamline the process of text analysis. For this post, we used the following services to build a text analysis service:

- [Amazon Bedrock](https://aws.amazon.com/bedrock/) – Facilitates serverless access to pre-trained FMs from different providers within a single, secure interface—particularly access to closed weights models like Anthropic’s Claude. This allows rapid testing of multiple models without managing underlying infrastructure.
- [Amazon SageMaker AI](https://aws.amazon.com/sagemaker-ai/) – Provides access to the latest open-source FMs like Llama, Mistral, DeepSeek, and more. With SageMaker AI, you have the option to simplify deployment of FMs using [Amazon SageMaker JumpStart](https://aws.amazon.com/sagemaker-ai/jumpstart/)—an ML and generative AI managed hub that provides simple UI or API based deployment of hundreds of FMs or alternatively helping you deploy your preferred FM and architecture on managed NVIDIA GPU infrastructure with ease.
- [Amazon Comprehend](https://aws.amazon.com/comprehend/) – An AI service with text analytics capabilities including sentiment analysis, entity recognition, and topic modeling. It can serve as a baseline or be integrated with advanced LLM workflows for a more comprehensive pipeline.
- [Amazon Kinesis](https://aws.amazon.com/kinesis/) – Handles real-time ingestion and streaming of text data from diverse sources (such as social media feeds, log streams, or real-time customer chat sessions).

A simplified architecture might consist of the following components:

- Data ingestion using Kinesis to capture text from various sources
- Data preprocessing using [AWS Lambda](https://aws.amazon.com/lambda) or [Amazon EMR](https://aws.amazon.com/emr/) for normalization, tokenization, and filtering.
- Model inference using either an LLM accessed through Amazon Bedrock or SageMaker AI
- Storage and analytics in [Amazon Simple Storage Service](https://aws.amazon.com/s3) (Amazon S3) or [Amazon Redshift](https://aws.amazon.com/redshift) for long-term analysis, reporting, and visualization

### Experimental results for text

The following table summarizes performance metrics (accuracy, precision, recall) across different models tested. Each was evaluated on the same text dataset with the goal of classifying sentences as positive, negative, or neutral.

| **Model** | **Accuracy** | **Precision** | **Recall** |
| --- | --- | --- | --- |
| Amazon SageMaker JumpStart Llama 3 70B Instruct v1 | **0.189** | 0.527 | **0.189** |
| Amazon Bedrock Anthropic Claude 3.5 Sonnet 2024-06-20-v1 | 0.187 | 0.44 | 0.187 |
| Amazon SageMaker Mixtral 8x7B Instruct v0 | 0.164 | **0.545** | 0.164 |
| Amazon Bedrock Amazon Nova Pro v1 | 0.159 | 0.239 | 0.16 |
| Closed Source state-of-the-art LLM 1 (>50B) | 0.159 | 0.025 | 0.159 |
| Closed Source state-of-the-art LLM 2 (>50B) | 0.159 | 0.025 | 0.159 |

### Analysis of findings

We observed the following from our results:

- **Overall low performance** – All models show relatively low accuracy in detecting sentiment polarity. This suggests purely text-based inputs might not provide enough contextual or emotional cues, especially for more subtle expressions like sarcasm or irony.
- **Impact of fine-tuning** – The two fine-tuned OpenAI models achieved higher metrics than most other configurations, though the jump in performance might indicate overfitting. They consistently labeled sentences as non-neutral only when a strong emotional indicator was present.
- **Model variation** – Meta’s Llama 3 70B and Anthropic’s Claude 3.5 Sonnet performed better than some other base models but still below the fine-tuned OpenAI solutions. This might reflect their pre-training objectives and the domain differences between their original training data and our sentiment classification task.

### Future directions for text-based analysis

You might consider expanding your text-based analysis in the following ways:

- **Advanced prompt engineering** – Current experiments employed straightforward chain-of-thought prompts. Future work could explore more refined few-shot or zero-shot prompt designs, including advanced reasoning strategies like “buffer of thoughts,” or carefully targeted domain-specific prompting.
- **Multimodal inputs** – Incorporating paralinguistic information (such as intonation or speaker emphasis) might boost text-based classification. Such data could be encoded as metadata or extracted by auxiliary models to enrich the textual context.
- **Language coverage** – Extending to non-English corpora and training domain-specific or multilingual models would likely improve generalization in real-world deployments.

## Sentiment analysis in audio

In this section, we discuss the method of analyzing sentiment directly from the audio signal using audio models.

### Challenges and characteristics

This method presents the following challenges:

- **Intonation and prosody** – Spoken language carries acoustic cues (tone, pitch, volume, tempo, and rhythm) that greatly influence perceived sentiment. A simple greeting such as “Hi, how are you?” can be genuinely enthusiastic or passively sarcastic, depending on the intonation. Traditional speech-to-text pipelines discard these non-verbal cues, potentially weakening the sentiment signal.
- **Speech-to-text conversion** – Many audio sentiment analysis systems rely on [ASR (Automatic Speech Recognition)](https://huggingface.co/tasks/automatic-speech-recognition) to generate transcripts, which are then fed into text-based sentiment models. Though beneficial for content understanding, purely textual analysis ignores prosodic features—one reason direct audio-based sentiment classification has garnered research interest.
- **Noise and recording quality** – Real-world audio often contains background noise, overlapping dialogue, or low-fidelity recordings. Models must be robust to such conditions to be viable in environments like call centers or customer support lines.

### Experimental datasets

We used two distinct types of datasets, each focusing on different aspects of emotion in speech:

- **Type 1** – A curated collection of short utterances recorded with different emotional intonations. Initially labeled by arousal (such as, happy, angry, disgusted), the data was then re-labeled by valence (positive, negative, neutral). Recordings labeled as “surprise” were removed because it can manifest as either positive or negative.  Sources include [CREMA-D](https://www.kaggle.com/datasets/ejlok1/cremad), [RAVDESS](https://www.kaggle.com/datasets/uwrfkaggler/ravdess-emotional-speech-audio), and [TESS](https://tspace.library.utoronto.ca/handle/1807/24487).
- **Type 2** – Contains more varied sentences, each labeled as positive, negative, or neutral. The diversity and complexity of utterances make this dataset significantly more challenging.  Sources include the [Audio Speech Sentiment dataset](https://www.kaggle.com/datasets/imsparsh/audio-speech-sentiment) and [MELD](https://www.kaggle.com/datasets/zaber666/meld-dataset).

### Tested models and rationale

We evaluated three prominent speech-based models:

- **HuBERT (Hidden Unit BERT)** – Employs a self-supervised Transformer that learns hidden cluster assignments in the audio signal. HuBERT excels at capturing prosodic and acoustic patterns crucial for emotion detection.
- **Wav2Vec** – Similar in philosophy to HuBERT, Wav2Vec learns powerful representations directly from raw audio using a Transformer-encoder backbone. Its self-supervised training scheme is highly effective with limited labeled data.
- **Whisper** – A Transformer-based encoder-decoder originally designed for robust speech recognition. Although its emphasis is on transcription and translation, we tested its ability to extract embeddings for downstream sentiment classification tasks.

### AWS services for audio analysis

To streamline the training and inference pipeline, we used the following AWS services:

- [Amazon SageMaker Studio](https://aws.amazon.com/sagemaker/ai/studio/) – Allows quick setup of training jobs on purpose-built instances (for example, GPU-enabled) without significant infrastructure overhead. Each model (HuBERT, Wav2Vec, Whisper) was trained and validated in separate SageMaker sessions.
- [Amazon Transcribe](https://aws.amazon.com/transcribe/) – For those workflows requiring speech-to-text conversion, Amazon Transcribe provides scalable and accurate ASR. Though not the focus of direct audio-based sentiment methods, it’s commonly integrated into contact center architectures, where text transcripts are also used for analytics or compliance checks.

A representative architecture could involve Kinesis for audio ingestion, Lambda for orchestrating pre-processing or route selection (such as direct audio-based sentiment vs. text-based after transcription), and Amazon S3 for storing final results. The following diagram illustrates this example architecture.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/03/ml-19126-image-1.jpg)

### Experimental results for audio

Our evaluation considered classification accuracy on separate test splits for Type 1 and Type 2 datasets. In general, all three models achieved higher performance on Type 1 than on Type 2. The following table summarizes these results.

| **Dataset Type** | **Sentiment** | **Wav2Vec ** | **Hubert** | **Whisper ** |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  | **Precision** | **Recall** | **F1** | **Accuracy** | **Precision** | **Recall** | **F1** | **Accuracy** | **Precision** | **Recall** | **F1** | **Accuracy** |
| Type 1: Fixed Phrases | Negative | 0.85 | 0.82 | 0.83 | 0.78 | 0.94 | 0.83 | 0.88 | 0.84 | 0.98 | 0.89 | 0.93 | 0.91 |
| Type 1: Fixed Phrases | Neutral | 0.57 | 0.95 | 0.72 | 0.61 | 0.98 | 0.75 | 0.8 | 0.96 | 0.87 |  |  |  |
| Type 1: Fixed Phrases | Positive | 0.86 | 0.49 | 0.63 | 0.84 | 0.74 | 0.79 | 0.82 | 0.92 | 0.86 |  |  |  |
| Type 2: Variable Phrases | Negative | 0.55 | 0.39 | 0.46 | 0.54 | 0.56 | 0.37 | 0.42 | 0.55 | 0.6 | 0.46 | 0.52 | 0.58 |
| Type 2: Variable Phrases | Neutral | 0.59 | 0.73 | 0.65 | 0.6 | 0.74 | 0.66 | 0.63 | 0.71 | 0.67 |  |  |  |
| Type 2: Variable Phrases | Positive | 0.35 | 0.31 | 0.33 | 0.38 | 0.35 | 0.36 | 0.44 | 0.47 | 0.46 |  |  |  |

### Analysis of findings

We observed the following from our results:

- **Type 1** – Because the same phrases were repeated with different emotional intonations, models focused more on acoustic cues rather than content. This led to higher accuracy—especially in distinguishing high-arousal (anger, excitement) from low-arousal (sadness, calm) states.
- **Type 2** – Performance dropped significantly when faced with more varied sentences. Here, the differences in lexical content and context overshadowed purely prosodic features. The models struggled to generalize across diverse sentence structures, speaker styles, and emotional expressions.

### Future directions for audio-based analysis

You might consider expanding your text-based analysis in the following ways:

- **Data diversity** – Expanding the datasets to include more languages, regional accents, and environmental conditions might improve the generalizability of these models.
- **Multimodal fusion** – Combining direct audio embeddings (prosody, intonation) with textual analysis (lexical content) might yield richer sentiment representations. This is especially pertinent in customer service scenarios where semantic content and emotional tone both matters.
- **Real-time inference** – For applications like live contact center support using Amazon Connect, real-time inference pipelines are crucial. Researchers can investigate methods such as streaming-based model inference (for example, chunk-by-chunk or frame-level processing) to get immediate feedback on customer sentiment and adapt responses accordingly.

## Conclusion

Sentiment analysis—whether performed on text or audio—offers powerful insights into customer perceptions, enabling more proactive and empathetic engagement strategies. However, the technical hurdles are non-trivial:

- **Text** – Ambiguity, irony, and limited context can hinder purely text-based classification. LLMs, even those fine-tuned, might underperform without careful data curation, advanced prompt engineering, or additional metadata.
- **Audio** – Directly analyzing audio captures prosodic and acoustic cues often lost in transcription. However, environmental noise, overlapping speech, and speaker diversity complicate training robust models.

AWS provides an extensive suite of services that cover the end-to-end sentiment analysis pipeline:

- **Data ingestion** – Kinesis for real-time text and audio streaming
- **Preprocessing** – Lambda and Amazon EMR for data cleansing, feature extraction, and transformations
- **Transcription (Optional)** – Amazon Transcribe to convert audio to text if a combined text and audio approach is needed
- **Sentiment classification** – AWS offers the following:  **Text** – Amazon Comprehend or FMs accessed through Amazon Bedrock and SageMaker AI **Audio** – Custom models (such as HuBERT, Wav2Vec, Whisper) trained in SageMaker AI
- **Customer Engagement** – Amazon Connect for intelligent contact centers with potential for real-time sentiment feedback loops

Ultimately, the choice between audio-based, text-based, or hybrid approaches depends on the use case and available data. Direct audio-based methods might capture emotional subtleties crucial in call center interactions—particularly during greetings or highly charged conversations—whereas text-based methods are often more straightforward to deploy at scale for chats, social media, and review-based analysis. By using AWS Cloud-based capabilities alongside rigorous ML methodologies, enterprises can tailor sentiment analysis solutions that balance accuracy, scalability, and cost-effectiveness. Future explorations might further integrate multimodal streams, advanced prompt engineering, and domain-specific fine-tuning, continuously refining our ability to interpret and act on the “voice of the customer.”

### About the authors

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/06/caique-1.png)Caique de Almeida** is a Staff Data Scientist at Itaú’s Institute of Science and Technology (ICTI). He focuses on Natural Language Processing, Deep Learning, and Cloud Architecture, bridging applied research with production-grade AI systems. He holds 11 AWS certifications and applies that cloud expertise to building scalable, reliable AI solutions. His current work centers on building customer-facing agents for financial services, applying AI in finance, and investigating factuality and reasoning in generative AI. Outside of work, he enjoys cycling.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/06/guilherme-1.jpg)Guilherme Rinaldo** is a Staff AI Engineer and Researcher at Instituto de Ciência e Tecnologia Itaú (ICTI), where he builds and evaluates Generative AI systems for text and voice, including LLM based agents and deep learning models. With 8 years of experience, he has led work from research prototypes to production pipelines, with an emphasis on reliability, security, and rigorous evaluation. His interests include continual learning, self evolving agents, and model monitoring at scale. Outside of work, Guilherme enjoys writing, travelling, and playing strategy games. You can find Guilherme on [LinkedIn](https://www.linkedin.com/in/guilhermerinaldo/).

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/06/paulo-1.jpg)Paulo Finardi** is a Principal Data Scientist at Itaú’s Institute of Science and Technology (ICTI). He has over 10 years of experience in Deep Learning and Natural Language Processing, with a focus on AI applied to finance, simulations, and digital twins. His work spans large-scale applied research, as well as AI strategy and innovation. Outside of work, he enjoys cycling. You can find Finardi on [LinkedIn](https://www.linkedin.com/in/paulo-finardi-964a1425b/).

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/06/victor-1.jpg)Victor Costa Beraldo** is a Lead Data Scientist at Itaú’s Institute of Science and Technology (ICTi), working at the intersection of voice and AI. With a strong background in signal processing and deep learning, he focuses on speech-based solutions, including ASR, ASV, emotion recognition, and real-time audio processing, bridging applied research and production systems in financial services. Outside of work, he enjoys watching soccer matches. You can find Victor on [LinkedIn](https://www.linkedin.com/in/victor-costa-beraldo-99746b144/).

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/06/vini-1.png)Vinicius Caridá** is a Distinguished Data Scientist at Itaú Unibanco and a member of the scientific and technical committee at Itaú’s Institute of Science and Technology (ICTI). He works across generative AI, natural language processing, virtual assistants, recommendation systems, control systems, and the end-to-end MLOps lifecycle. Vinicius is honored to be recognized as an AWS AI Hero, proudly representing Latin America in the program. His current work focuses on building customer-facing AI agents for financial services and advancing factuality and reasoning in generative models. Outside of work, he loves teaching and learning with the tech community and spending time with his wife Jerusa and their daughter Olivia. You can find Vinicius on [LinkedIn](https://www.linkedin.com/in/viniciuscarida/).

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/10/PranavMurthy-ProfilePhoto.jpg)Pranav Murthy** is a Senior Generative AI Data Scientist at AWS, specializing in helping organizations innovate with Generative AI, Deep Learning, and Machine Learning on Amazon SageMaker AI. Over the past 10+ years, he has developed and scaled advanced computer vision (CV) and natural language processing (NLP) models to tackle high-impact problems—from optimizing global supply chains to enabling real-time video analytics and multilingual search. You can find Pranav on [LinkedIn](https://www.linkedin.com/in/pranavvm26/).
