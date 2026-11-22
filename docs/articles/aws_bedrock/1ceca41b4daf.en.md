---
vendor: aws_bedrock
title: Effective cross-lingual LLM evaluation with Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/effective-cross-lingual-llm-evaluation-with-amazon-bedrock
date: 2025-07-08
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: efb75eaa83cc
---

# Effective cross-lingual LLM evaluation with Amazon Bedrock

Evaluating the quality of AI responses across multiple languages presents significant challenges for organizations deploying generative AI solutions globally. How can you maintain consistent performance when human evaluations require substantial resources, especially across diverse languages? Many companies find themselves struggling to scale their evaluation processes without compromising quality or breaking their budgets.

[Amazon Bedrock Evaluations](https://aws.amazon.com/bedrock/evaluations/) offers an efficient solution through its LLM-as-a-judge capability, so you can assess AI outputs consistently across linguistic barriers. This approach reduces the time and resources typically required for multilingual evaluations while maintaining high-quality standards.

In this post, we demonstrate how to use the evaluation features of [Amazon Bedrock](https://aws.amazon.com/bedrock/) to deliver reliable results across language barriers without the need for localized prompts or custom infrastructure. Through comprehensive testing and analysis, we share practical strategies to help reduce the cost and complexity of multilingual evaluation while maintaining high standards across global large language model (LLM) deployments.

## Solution overview

To scale and streamline the evaluation process, we used Amazon Bedrock Evaluations, which offers both automatic and human-based methods for assessing model and RAG system quality. To learn more, see [Evaluate the performance of Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html).

### Automatic evaluations

Amazon Bedrock supports two modes of automatic evaluation:

- [LLM-as-a-judge evaluations](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-judge.html) – An evaluator model scores the outputs of another model or system
- [Programmatic metric-based evaluations](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-automatic.html) – This approach assesses metrics like accuracy, robustness, and toxicity for different task types by other means than LLMs

For LLM-as-a-judge evaluations, you can choose from a set of [built-in metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-type-judge-prompt.html) or define your own [custom metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-custom-metrics-prompt-formats.html) tailored to your specific use case. You can run these evaluations on models hosted in Amazon Bedrock or on external models by uploading your own prompt-response pairs.

### Human evaluations

For use cases that require subject-matter expert judgment, Amazon Bedrock also supports [human evaluation jobs](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-human.html). You can assign evaluations to human experts, and Amazon Bedrock manages task distribution, scoring, and result aggregation.

Human evaluations are especially valuable for establishing a baseline against which automated scores, like those from judge model evaluations, can be compared.

## Evaluation dataset preparation

We used the Indonesian splits from the [SEA-MTBench dataset](https://huggingface.co/datasets/aisingapore/MultiTurn-Chat-MT-Bench). It is based on [MT-Bench](https://arxiv.org/abs/2306.05685), a widely used benchmark for conversational AI assessment. The Indonesian version was manually translated by native speakers and consisted of 58 records covering a diverse range of categories such as math, reasoning, and writing.

We converted multi-turn conversations into single-turn interactions while preserving context. This allows each turn to be evaluated independently with consistent context. This conversion process resulted in 116 records for evaluation. Here’s how we approached this conversion:

```
Original row: {"prompts: [{ "text": "prompt 1"}, {"text": "prompt 2"}]}
Converted into 2 rows in the evaluation dataset:
Human: {prompt 1}\n\nAssistant: {response 1}
Human: {prompt 1}\n\nAssistant: {response 1}\n\nHuman: {prompt 2}\n\nAssistant: {response 2}
```

For each record, we generated responses using a stronger LLM (Model Strong-A) and a relatively weaker LLM (Model Weak-A). These outputs were later evaluated by both human annotators and LLM judges.

## Establishing a human evaluation baseline

To assess evaluation quality, we first established a set of human evaluations as the baseline for comparing LLM-as-a-judge scores. A native-speaking evaluator rated each response from Model Strong-A and Model Weak-A on a 1–5 Likert helpfulness scale, using the same rubric applied in our LLM evaluator prompts.

We conducted manual evaluations on the full evaluation dataset using the human evaluation feature in Amazon Bedrock. Setting up human evaluations in Amazon Bedrock is straightforward: you upload a dataset and define the worker group, and Amazon Bedrock automatically generates the annotation UI and manages the scoring workflow and result aggregation.

The following screenshot shows a sample result from an Amazon Bedrock human evaluation job.

![Custom evaluation dashboard showing distribution of 116 ratings across 5-point scale with prompt category filter options](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/25/ml-18669-human-eval-1.png)

## LLM-as-a-judge evaluation setup

We evaluated responses from Model Strong-A and Model Weak-A using four judge models: Model Strong-A, Model Strong-B, Model Weak-A, and Model Weak-B. These evaluations were run using custom metrics in an LLM-as-a-judge evaluation in Amazon Bedrock, which allows flexible prompt definition and scoring without the need to manage your own infrastructure.

Each judge model was given a custom evaluation prompt aligned with the same helpfulness rubric used in the human evaluation. The prompt asked the evaluator to rate each response on a 1–5 Likert scale based on clarity, task completion, instruction adherence, and factual accuracy. We prepared both English and Indonesian versions to support multilingual testing. The following table compares the English and Indonesian prompts.

| **English prompt** | **Indonesian prompt** |
| --- | --- |
| `">You are given a user task and a candidate completion from an AI assistant. Your job is to evaluate how helpful the completion is — with special attention to whether it follows the user’s instructions and produces the correct or appropriate output. A helpful response should: - Accurately solve the task (math, formatting, generation, extraction, etc.) - Follow all explicit and implicit instructions - Use appropriate tone, clarity, and structure - Avoid hallucination, false claims, or harmful implications Even if the response is well-written or polite, it should be rated low if it: - Produces incorrect results or misleading explanations - Fails to follow core instructions - Makes basic reasoning mistakes Scoring Guide (1–5 scale): 5 – Very Helpful The response is correct, complete, follows instructions fully, and could be used directly by the end user with confidence. 4 – Somewhat Helpful Minor errors, omissions, or ambiguities, but still mostly correct and usable with small modifications or human verification. 3 – Neutral / Mixed Either (a) the response is generally correct but doesn’t really follow the user’s instruction, or (b) it follows instructions but contains significant flaws that reduce trust. 2 – Somewhat Unhelpful The response is incorrect or irrelevant in key areas, or fails to follow instructions, but shows some effort or structure. 1 – Very Unhelpful The response is factually wrong, ignores the task, or shows fundamental misunderstanding or no effort. Instructions: You will be shown: - The user’s task - The AI assistant’s completion Evaluate the completion on the scale above, considering both accuracy and instruction-following as primary criteria. Task: {{prompt}} Candidate Completion: {{prediction}}` | `Anda diberikan instruksi dari pengguna beserta jawaban/penyelesaian instruksi tersebut oleh asisten AI. Tugas Anda adalah mengevaluasi seberapa membantu jawaban tersebut — dengan fokus utama pada apakah jawaban tersebut mengikuti instruksi pengguna dengan benar dan menghasilkan output yang akurat serta sesuai. Sebuah jawaban dianggap membantu jika: - Menyelesaikan instruksi dengan akurat (perhitungan matematika, pemformatan, pembuatan konten, ekstraksi data, dll.) - Mengikuti semua instruksi eksplisit maupun implisit dari pengguna - Menggunakan nada, kejelasan, dan struktur yang sesuai - Menghindari halusinasi, klaim yang salah, atau implikasi yang berbahaya Meskipun jawaban terdengar baik atau sopan, tetap harus diberi nilai rendah jika: - Memberikan hasil yang salah atau penjelasan yang menyesatkan - Gagal mengikuti inti dari instruksi pengguna - Membuat kesalahan penalaran yang mendasar Panduan Penilaian (Skala 1–5): 5 – Sangat Membantu Jawaban benar, lengkap, mengikuti instruksi pengguna sepenuhnya, dan dapat langsung digunakan oleh pengguna dengan percaya diri. 4 – Cukup Membantu Ada sedikit kesalahan, kekurangan, atau ambiguitas, tetapi jawaban secara umum benar dan masih dapat digunakan dengan sedikit perbaikan atau verifikasi manual. 3 – Netral Baik (a) jawabannya secara umum benar tetapi tidak sepenuhnya mengikuti instruksi pengguna, atau (b) jawabannya mengikuti instruksi tetapi mengandung kesalahan besar yang mengurangi tingkat kepercayaan. 2 – Kurang Membantu Jawaban salah atau tidak relevan pada bagian-bagian penting, atau tidak mengikuti instruksi pengguna, tetapi masih menunjukkan upaya atau struktur penyelesaian. 1 – Sangat Tidak Membantu Jawaban salah secara fakta, mengabaikan instruksi pengguna, menunjukkan kesalahpahaman mendasar, atau tidak menunjukkan adanya upaya untuk menyelesaikan instruksi. Petunjuk penilaian: Anda akan diberikan: - Instruksi dari pengguna - Jawaban dari asisten AI Evaluasilah jawaban tersebut menggunakan skala di atas, dengan mempertimbangkan akurasi dan kepatuhan terhadap instruksi pengguna sebagai kriteria utama. Instruksi pengguna: {{prompt}} Jawaban asisten AI: {{prediction}}` |

To measure alignment, we used two standard metrics:

- **Pearson correlation** – Measures the linear relationship between score values. Useful for detecting overall similarity in score trends.
- **Cohen’s kappa (linear weighted)** – Captures agreement between evaluators, adjusted for chance. Especially useful for discrete scales like Likert scores.

## Alignment between LLM judges and human evaluations

We began by comparing the average helpfulness scores given by each evaluator using the English judge prompt. The following chart shows the evaluation results.

![Comparative analysis of helpfulness scores between Human evaluator and Models (Strong-A/B, Weak-A/B), showing ratings between 4.11-4.93](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/25/ml-18669-helpfulness-1.png)

When evaluating responses from the stronger model, LLM judges tended to agree with human ratings. But on responses from the weaker model, most LLMs gave noticeably higher scores than humans. This suggests that LLM judges tend to be more generous when response quality is lower.

We designed the evaluation prompt to guide models toward scoring behavior similar to human annotators, but score patterns still showed signs of potential bias. Model Strong-A rated its own outputs highly (4.93), whereas Model Weak-A gave its own responses a higher score than humans did. In contrast, Model Strong-B, which didn’t evaluate its own outputs, gave scores that were closer to human ratings.

To better understand alignment between LLM judges and human preferences, we analyzed Pearson and Cohen’s kappa correlations between them. On responses from Model Weak-A, alignment was strong. Model Strong-A and Model Strong-B achieved Pearson correlations of 0.45 and 0.61, with kappa scores of 0.33 and 0.4.

LLM judges and human alignment on responses from Model Strong-A was more moderate. All evaluators had Pearson correlations between 0.26–0.33 and weighted Kappa scores between 0.2–0.22. This might be due to limited variation in either human or model scores, which reduces the ability to detect strong correlation patterns.

To complete our analysis, we also conducted a qualitative deep dive. Amazon Bedrock makes this straightforward by providing JSONL outputs from each LLM-as-a-judge run that include both the evaluation score and the model’s reasoning. This helped us review evaluator justifications and identify cases where scores were incorrectly extracted or parsed.

From this review, we identified several factors behind the misalignment between LLM and human judgments:

- **Evaluator capability ceiling** – In some cases, especially in reasoning tasks, the LLM evaluator couldn’t solve the original task itself. This made its evaluations flawed and unreliable at identifying whether a response was correct.
- **Evaluation hallucination** – In other cases, the LLM evaluator assigned low scores to correct answers not because of reasoning failure, but because it imagined errors or flawed logic in responses that were actually valid.
- **Overriding instructions **– Certain models occasionally overrode explicit instructions based on ethical judgment. For example, two evaluator models rated a response that created misleading political campaign content as very unhelpful (even though the response included its own warnings), whereas human evaluators rated it very helpful for following the task.

These problems highlight the importance of using human evaluations as a baseline and performing qualitative deep dives to fully understand LLM-as-a-judge results.

## Cross-lingual evaluation capabilities

After analyzing evaluation results from the English judge prompt, we moved to the final step of our analysis: comparing evaluation results between English and Indonesian judge prompts.

We began by comparing overall helpfulness scores and alignment with human ratings. Helpfulness scores remained nearly identical for all models, with most shifts within ±0.05. Alignment with human ratings was also similar: Pearson correlations between human scores and LLM-as-a-judge using Indonesian judge prompts closely matched those using English judge prompts. In statistically meaningful cases, correlation score differences were typically within ±0.1.

To further assess cross-language consistency, we computed Pearson correlation and Cohen’s kappa directly between LLM-as-a-judge evaluation scores generated using English and Indonesian judge prompts on the same response set. The following tables show correlation between scores from Indonesian and English judge prompts for each evaluator LLM, on responses generated by Model Weak-A and Model Strong-A.

The first table summarizes the evaluation of Model Weak-A responses.

| **Metric** | **Model Strong-A** | **Model Strong-B** | **Model Weak-A** | **Model Weak-B** |
| --- | --- | --- | --- | --- |
| Pearson correlation | 0.73 | 0.79 | 0.64 | 0.64 |
| Cohen’s Kappa | 0.59 | 0.69 | 0.42 | 0.49 |

The next table summarizes the evaluation of Model Strong-A responses.

| **Metric** | **Model Strong-A** | **Model Strong-B** | **Model Weak-A** | **Model Weak-B** |
| --- | --- | --- | --- | --- |
| Pearson correlation | 0.41 | 0.8 | 0.51 | 0.7 |
| Cohen’s Kappa | 0.36 | 0.65 | 0.43 | 0.61 |

Correlation between evaluation results from both judge prompt languages was strong across all evaluator models. On average, Pearson correlation was 0.65 and Cohen’s kappa was 0.53 across all models.

We also conducted a qualitative review comparing evaluations from both evaluation prompt languages for Model Strong-A and Model Strong-B. Overall, both models showed consistent reasoning across languages in most cases. However, occasional hallucinated errors or flawed logic occurred at similar rates across both languages (we should note that humans make occasional mistakes as well).

One interesting pattern we observed with one of the stronger evaluator models was that it tended to follow the evaluation prompt more strictly in the Indonesian version. For example, it rated a response as unhelpful when it refused to generate misleading political content, even though the task explicitly asked for it. This behavior differed from the English prompt evaluation. In a few cases, it also assigned a noticeably stricter score compared to the English evaluator prompt even though the reasoning across both languages was similar, better matching how humans typically evaluate.

These results confirm that although prompt translation remains a useful option, it is not required to achieve consistent evaluation. You can rely on English evaluator prompts even for non-English outputs, for example by using Amazon Bedrock LLM-as-a-judge predefined and custom metrics to make multilingual evaluation simpler and more scalable.

## Takeaways

The following are key takeaways for building a robust LLM evaluation framework:

- **LLM-as-a-judge is a practical evaluation method** – It offers faster, cheaper, and scalable assessments while maintaining reasonable judgment quality across languages. This makes it suitable for large-scale deployments.
- **Choose a judge model based on practical evaluation needs** – Across our experiments, stronger models aligned better with human ratings, especially on weaker outputs. However, even top models can misjudge harder tasks or show self-bias. Use capable, neutral evaluators to facilitate fair comparisons.
- **Manual human evaluations remain essential** – Human evaluations provide the reference baseline for benchmarking automated scoring and understanding model judgment behavior.
- **Prompt design meaningfully shapes evaluator behavior** – Aligning your evaluation prompt with how humans actually score improves quality and trust in LLM-based evaluations.
- **Translated evaluation prompts are helpful but not required** – English evaluator prompts reliably judge non-English responses, especially for evaluator models that support multilingual input.
- **Always be ready to deep dive with qualitative analysis** – Reviewing evaluation disagreements by hand helps uncover hidden model behaviors and makes sure that statistical metrics tell the full story.
- **Simplify your evaluation workflow using Amazon Bedrock evaluation features** – Amazon Bedrock built-in human evaluation and LLM-as-a-judge evaluation capabilities simplify iteration and streamline your evaluation workflow.

## Conclusion

Through our experiments, we demonstrated that LLM-as-a-judge evaluations can deliver consistent and reliable results across languages, even without prompt translation. With properly designed evaluation prompts, LLMs can maintain high alignment with human ratings regardless of evaluator prompt language. Though we focused on Indonesian, the results indicate similar techniques are likely effective for other non-English languages, but you are encouraged to assess for yourself on any language you choose. This reduces the need to create localized evaluation prompts for every target audience.

To level up your evaluation practices, consider the following ways to extend your approach beyond foundation model scoring:

- Evaluate your Retrieval Augmented Generation (RAG) pipeline, assessing not just LLM responses but also retrieval quality using [Amazon Bedrock RAG evaluation capabilities](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-kb.html)
- Evaluate and monitor continuously, and run evaluations before production launch, during live operation, and ahead of any major system upgrades

Begin your cross-lingual evaluation journey today with Amazon Bedrock Evaluations and scale your AI solutions confidently across global landscapes.

### About the authors

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/25/riza-pic45.jpeg)**Riza Saputra** is a Senior Solutions Architect at AWS, working with startups of all stages to help them grow securely, scale efficiently, and innovate faster. His current focus is on generative AI, guiding organizations in building and scaling AI solutions securely and efficiently. With experience across roles, industries, and company sizes, he brings a versatile perspective to solving technical and business challenges. Riza also shares his knowledge through public speaking and content to support the broader tech community.
