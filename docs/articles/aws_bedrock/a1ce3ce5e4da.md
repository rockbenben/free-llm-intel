---
vendor: aws_bedrock
title: Fast-track SOP processing using Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/fast-track-sop-processing-using-amazon-bedrock
date: 2025-06-02
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: afefc0532104
---

# 使用 Amazon Bedrock 加速 SOP 处理

在法规与合规语境下，标准操作规程（SOP）是必不可少的文档。SOP 列明各项流程的具体步骤，确保做法一致、高效并符合监管标准。

SOP 文档通常包含标题、范围、目的、职责、流程、文档记录、引用（参考文献）以及详细的审批与修订历史等关键章节。在医疗健康和生命科学等受 FDA 监管的行业中，SOP 在界定生产、临床、实验室、质量控制、质量保证和法规合规做法方面起着关键作用。

当美国食品药品监督管理局（FDA）这样的监管机构对法规作出变更时，组织必须对照其内部 SOP 评估这些变更。必要时，他们必须更新 SOP，使其与法规变更保持一致并维持合规。

本文展示使用 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 识别法规变更与 SOP 之间关系的几种不同方法。

## 挑战

在医疗健康和生命科学行业，FDA 和欧洲药品管理局（EMA）等监管机构会频繁更新临床试验、医疗器械、药物研发与审批、质量风险管理、系统与数据管理、技术采用等各个领域的法规。这些法规更新往往要求组织相应更新内部 SOP 以保持一致。该过程通常是人工的，需要一支领域专家团队审阅法规变更、筛选 SOP 以找出相关性、判定影响并明确需要更新的内容。这种人工方式给企业带来显著开销，评审周期可能长达数天到数月。

为应对这一挑战，我们探索了若干方法，帮助自动识别法规变更与 SOP 之间的关系。这些方法还可扩展用于评估法规变更对组织内部流程和文档的影响。借助自动化，企业可以简化 SOP 更新流程，减少与不断演进的监管要求保持一致所需的时间和资源。

## 示例数据

本文使用了 FDA 生物制品评价与研究中心（CBER）发布的 SOP。这些公开可得的 SOP 被 FDA 工作人员用于指导其职责。

具体而言，我们聚焦于以下与生物制品流程相关的 SOP。这一较窄的范围让我们能够深入探讨医疗健康和生命科学大行业中的某个特定监管领域。

- [SOPP 8005：正式争议解决流程](https://www.fda.gov/media/108908/download?attachment)
- [SOPP 8117：以 eCTD 格式电子提交之前签发跟踪编号](https://www.fda.gov/media/93416/download?attachment)
- [SOPP 8201：研究性新药申请临床试验暂停的行政处理](https://fda.report/media/88774/SOPP+8201-IND-Clinical-Holds-Ver_5-Final_March_2020.pdf)
- [SOPP 8301：主文件的接收与处理](https://www.fda.gov/media/158382/download?attachment)
- [SOPP 8403：生物制品许可的签发、重新签发与自愿撤销](https://www.fda.gov/media/108918/download?attachment)
- [SOPP 8507：应对不合规产品通知及终止通知请求的流程](https://www.fda.gov/media/96005/download?attachment)
- [SOPP 8717：医疗器械评价所需的生物相容性培训与毒理学档案](https://fda.report/media/109201/SOPP-8717--Required-Biocompatibility-Training-and-Toxicology-Profiles-for-Evaluation-of-Medical-Devices.pdf)
- [SOPP 9151：处理 21 CFR 第 1271.155 条下针对人类细胞、组织以及基于细胞和组织的产品（HCT/P）的豁免与替代流程请求的流程](https://www.fda.gov/media/109151/download?attachment)

除 SOP 之外，我们还使用了三份 FDA 生物制品指南文件，用以检验监管文档与 SOP 之间的关系。

这些指南文件阐述了 FDA 对生物制品领域相关监管问题的政策解读。它们涵盖广泛主题，包括处理、内容、评估、批准、检查和政策执行。指南文件还讨论了与受监管产品的设计、生产、标签、推广、制造和检测有关的特定产品或问题。

本次分析我们使用了以下具体的 FDA 生物制品指南文件：

- [人类细胞、组织以及基于细胞和组织的产品（HCT/P）的监管——小型实体合规指南；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/regulation-human-cells-tissues-and-cellular-and-tissue-based-products-hctps-small-entity-compliance)
- [正式争议解决：部门层级以上的申诉；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/formal-dispute-resolution-sponsor-appeals-above-division-level-guidance-industry-and-review-staff)
- [提交与审评针对临床试验暂停的完整答复（修订版）；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised)

## 方法

评估法规变更影响的关键一步，是判断某项监管指南是否与组织的 SOP 相关。我们使用 Amazon Bedrock，并用 [Amazon Simple Storage Service（Amazon S3）](https://aws.amazon.com/s3/)存储输入数据集。

Amazon Bedrock 是一项完全托管的服务，可通过单一 API 提供来自 AI21 Labs、Anthropic、Cohere、Meta、Mistral、Stability AI 和 Amazon 等领先 AI 公司的高性能基础模型（FM）供你选择，同时还提供一整套能力，帮助你以安全、隐私和负责任 AI 的方式构建生成式 AI 应用。

我们的实验在 Amazon Bedrock 上使用 Anthropic 的 Claude 3 Opus 大型语言模型（LLM）。不过，你可以利用 Amazon Bedrock 上丰富的模型选择来试验其他模型，挑选最契合你具体需求的那一个。Amazon Bedrock 会频繁发布现有 AI 模型的更新版本，只需修改配置即可访问和使用，这使其成为部署最新 AI 能力的极具灵活性的选择。

我们聚焦于以下方法：

- **全文匹配 ** – 比较监管指南与 SOP 文档的全文
- **文本相似度** – 该方法包含两个选项： **向量嵌入** – 度量指南文本与 SOP 文本之间的语义相似度 **关键词搜索** – 识别相关关键词及其在文档中的出现情况
- **分类法主题匹配** – 将指南和 SOP 内容映射到分类结构，以识别主题层面的关系

本文详细介绍了我们探索的方法以及实验中的经验。

### 全文匹配

下图展示了全文匹配架构。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/16/ML-17198-arch-diag-Image-001.png)

在该方法中，我们把 SOP 和法规变更的完整内容一起传给模型，从而将每一项法规变更与每一个 SOP 进行比较。目标是识别法规变更与 SOP 之间的关系。

以下是用于判断某个 SOP 是否与某项法规变更相关的示例 prompt：

```
Human:

Act as an expert who understands the Food and Drug Administration's Center for Biologics Evaluation and Research (CBER) internal Biologics procedures, which help their staff in performing their duties in assuring the safety, purity, potency, and effectiveness of biologics and related products (such as vaccines, live biotherapeutics (probiotics), blood products, and cell, tissue, and gene therapies).

Given a regulatory guidance change, and a document describing a CBER Biologics procedure of evaluation, research or review, tell me if the regulatory change is related the procedure.
```

```
<regulatory_change>
{regchange}
</regulatory_change>

<biologics_procedure>
{procedure}
</biologics_procedure>
```

```
To answer this question, first, determine what the subject of the regulatory change is. For example, the subject might be something like "regulatory considerations for human cells and tissues" or "processing of clinical holds for new drug applications".

In order for the regulatory change to be related to the biologics procedure, the procedure description must include information about the topic. In other words, you should have a specific section from the procedure that is clearly related to the regulatory change in order to say that it is related.

For example, if a procedure description mentions cells or tissues, it could be related to how they need to be handled or manipulated. Similarly if a procedure mentions dispute resolution, it could be related to how a biologics procedure handles dispute resolution. Tell me whether the regulatory change is related to that the biologics procedure. Don't guess, and explain your thinking. If you can't find specific elements in the procedure that are clearly related to the regulations, then the answer is that the procedure is not related by the regulatory change.

Your answer should end with the word "RELATED" or "UNRELATED", reflecting your overall evaluation of whether the procedure description is related to the regulation change or not.
```

当我们使用 Amazon Bedrock 对数据集中的所有 SOP 和监管指南文档运行全文匹配方法时，结果显示相关 SOP 被准确识别。例如，[SOPP 9151](https://www.fda.gov/media/109151/download?attachment) 被正确识别为唯一与[人类细胞、组织以及基于细胞和组织的产品（HCT/P）的监管——小型实体合规指南；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/regulation-human-cells-tissues-and-cellular-and-tissue-based-products-hctps-small-entity-compliance)法规变更相关的 SOP，其余则被判定为无关：

```
Assistant:

SOPP9151-061306.txt:

The regulatory change is about the regulation of human cells, tissues, and cellular and tissue-based products (HCT/Ps). It provides guidance on the criteria for determining how HCT/Ps will be regulated, registration and listing requirements, donor eligibility requirements, current good tissue practice requirements, and FDA inspection and enforcement of HCT/P establishments.

The biologics procedure is specifically about handling requests for exemptions and alternative procedures for HCT/Ps under 21 CFR 1271.155. The procedure outlines the responsibilities and steps for CBER staff to process and respond to these exemption requests.

There is a clear relationship between the regulatory change and the biologics procedure. The regulatory change provides the overall framework and requirements for regulating HCT/Ps, while the biologics procedure focuses on one specific aspect within that framework - handling exemption requests from certain HCT/P requirements.

The procedure directly references and provides instructions for implementing 21 CFR 1271.155, which is part of the HCT/P regulations covered in the regulatory change document. So the biologics procedure is a detailed process that enables the agency to grant exemptions and alternatives to the HCT/P requirements established in the regulations.

In summary, the regulatory change establishes the rules for HCT/Ps, and the biologics procedure describes how the agency will process requests for exceptions to those rules. Therefore, the two documents are closely related.

RELATED
```

同样，[SOPP 8005](https://www.fda.gov/media/108908/download?attachment) 被正确识别为唯一与[正式争议解决：部门层级以上的申诉；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/formal-dispute-resolution-sponsor-appeals-above-division-level-guidance-industry-and-review-staff)法规变更相关的 SOP，其他 SOP 均被判定为无关。

最后，[SOP 8201](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised) 也被正确识别为唯一与[提交与审评针对临床试验暂停的完整答复（修订版）；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised)法规变更相关的 SOP。

这些结果表明，全文匹配方法在将相关 SOP 准确关联到对应监管指南文档方面是有效的。

### 文本相似度

下图展示了文本相似度匹配工作流。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/16/ML-17198-arch-diag-Image-002.png)

在第二种方法中，我们使用向量嵌入（用于语义相似度）或基于关键词的相似度方法来为 SOP 建立索引。这样我们就可以把法规变更的内容作为查询提交，并返回最相似的 SOP 文档。

该文本相似度方法包含以下步骤：

- 为 SOP 建立索引：对于向量嵌入方法，我们使用 LLM 生成 SOP 内容的向量表示，以捕捉语义相似性。对于基于关键词的方法，我们找出每个 SOP 中最相关的关键词，并基于其出现情况建立索引。
- 查询索引：对于给定的法规变更，我们将其文本作为查询提交给 SOP 索引。索引随后根据所选的相似度度量（语义或基于关键词）返回最相似的 SOP。

#### 向量搜索

在文本相似度方法中，我们使用开源内存数据库 ChromaDB 生成向量嵌入并执行搜索。

我们在 ChromaDB 中创建了一个包含所有 SOP 文档的 collection。随后，我们将每份监管指南文档的文本独立地对该 SOP collection 进行查询。我们使用默认的 L2 距离算法，其中距离分数越低表示查询与索引中的 SOP 文档越接近。

尽管基于向量嵌入的文本相似度方法在某些情况下能识别出最匹配的 SOP 文档，但也产生了一些不准确的结果。

例如，用[人类细胞、组织以及基于细胞和组织的产品（HCT/P）的监管——小型实体合规指南；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/regulation-human-cells-tissues-and-cellular-and-tissue-based-products-hctps-small-entity-compliance)这项法规查询时，[SOPP 9151](https://www.fda.gov/media/109151/download?attachment) 被正确识别为最佳匹配。然而，另外几份无关的 SOP 文档距离分数也很低，这可能导致它们被误判为相关：

```
[
    [
        "SOPP9151-061306.txt",
        0.640560507774353
    ],
    [
        "SOPP-8717--Required-Biocompatibility-Training-and-Toxicology-Profiles-for-Evaluation-of-Medical-Devices.txt",
        0.8971723914146423
    ],
    [
        "SOPP-8403-Issuance-Reissuance-and-Voluntary-Revocation-of-Biological-Product-Licenses-V6.txt",
        0.9069873690605164
    ],
    [
        "SOPP-8117-Issuing-Tracking-Numbers-eCTD-Format-V9.txt",
        1.069345235824585
    ],
    [
        "SOPP-8507V4-IllegitimateProds-Final.txt",
        1.1143898963928223
    ],
    [
        "SOPP-8201-Administrative-Processing-Clinical-Holds-INDs_V9.txt",
        1.157564640045166
    ],
    [
        "SOPP-8005-Formal-Dispute-Resolution-Process-V6.txt",
        1.2106068134307861
    ],
    [
        "SOPP-8301-Receipt-and-Processing-of-Master-Files_V4.txt",
        1.3174282312393188
    ]
]
```

同样，用[正式争议解决：部门层级以上的申诉；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/formal-dispute-resolution-sponsor-appeals-above-division-level-guidance-industry-and-review-staff)这项法规查询时，向量搜索错误地把 [SOPP 8717](https://www.fda.gov/media/93416/download?attachment) 识别为最佳匹配，而与正式争议解决更直接相关的 [SOPP 8005](https://www.fda.gov/media/108908/download?attachment) 反而距离分数更高：

```
[
    [
        "SOPP-8717--Required-Biocompatibility-Training-and-Toxicology-Profiles-for-Evaluation-of-Medical-Devices.txt",
        0.848071277141571
    ],
       …
       …
]
```

最后，对于[提交与审评针对临床试验暂停的完整答复（修订版）；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised)这项法规，向量搜索再次将 [SOPP 8717](https://www.fda.gov/media/93416/download?attachment) 识别为最佳匹配，而不是更相关的 [SOP 8201](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised)：

```
[
    [
        "SOPP-8717--Required-Biocompatibility-Training-and-Toxicology-Profiles-for-Evaluation-of-Medical-Devices.txt",
        0.8028254508972168
    ],
    …
    …
]
```

#### 关键词搜索

我们还探索了使用 Whoosh Python 搜索库的基于关键词的相似度方法。我们先用 Whoosh 库为所有 SOP 文档创建索引。然后，对每份监管指南文档，我们使用 Whoosh 查询解析器分别搜索该索引。

Whoosh 库会为每个匹配的 SOP 文档返回搜索分数，分数越高表示与查询的匹配越好。

搜索[人类细胞、组织以及基于细胞和组织的产品（HCT/P）的监管——小型实体合规指南；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/regulation-human-cells-tissues-and-cellular-and-tissue-based-products-hctps-small-entity-compliance)这项法规时，最匹配的文档被错误识别为 [SOPP 8301](https://www.fda.gov/media/158382/download?attachment)，而不是更相关的 [SOPP 9151](https://www.fda.gov/media/109151/download?attachment)：

```
8 results found
<Hit {'fname': 'SOPP-8301-Receipt-and-Processing-of-Master-Files_V4.txt'}> with score of 744.420492560645
<Hit {'fname': 'SOPP-8507V4-IllegitimateProds-Final.txt'}> with score of 609.3431135327576
<Hit {'fname': 'SOPP-8201-Administrative-Processing-Clinical-Holds-INDs_V9.txt'}> with score of 588.5899332740212
<Hit {'fname': 'SOPP-8403-Issuance-Reissuance-and-Voluntary-Revocation-of-Biological-Product-Licenses-V6.txt'}> with score of 582.278310231856
<Hit {'fname': 'SOPP-8005-Formal-Dispute-Resolution-Process-V6.txt'}> with score of 449.11608593886564
<Hit {'fname': 'SOPP-8117-Issuing-Tracking-Numbers-eCTD-Format-V9.txt'}> with score of 377.9723456561558
<Hit {'fname': 'SOPP9151-061306.txt'}> with score of 328.67972016789844
<Hit {'fname': 'SOPP-8717--Required-Biocompatibility-Training-and-Toxicology-Profiles-for-Evaluation-of-Medical-Devices.txt'}> with score of 160.6985781375766
```

同样，使用基于关键词的相似度方法搜索[正式争议解决：部门层级以上的申诉；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/formal-dispute-resolution-sponsor-appeals-above-division-level-guidance-industry-and-review-staff)这项法规时，Whoosh 库再次错误地把 [SOPP 8301](https://www.fda.gov/media/158382/download?attachment) 识别为最匹配的文档，而不是更相关的 [SOPP 8005](https://www.fda.gov/media/108908/download?attachment)：

```
8 results found
<Hit {'fname': 'SOPP-8301-Receipt-and-Processing-of-Master-Files_V4.txt'}> with score of 721.9535225922815
…
…
```

与前两个例子不同，搜索[提交与审评针对临床试验暂停的完整答复（修订版）；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised)这项法规时，[SOP 8201](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised) 被正确识别为最匹配的文档：

```
8 results found
<Hit {'fname': 'SOPP-8201-Administrative-Processing-Clinical-Holds-INDs_V9.txt'}> with score of 503.3284407067554
…
…
```

这些结果表明，尽管基于关键词的相似度方法在某些情况下有效，但它也可能难以准确识别最相关的 SOP，与基于向量嵌入的方法所面临的挑战类似。

### 基于分类法的主题匹配

下图展示了基于分类法的主题匹配架构。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/16/ML-17198-arch-diag-Image-003.png)

在第三种方法中，我们聚焦于构建一个与生物制品流程主题相关的层级分类法。这一基于分类法的方法旨在捕捉监管指南文档与 SOP 之间的主题关系。该方法有可能提供高性价比的方案，因为不必在每次向 LLM 查询时都把整个 SOP 或输入文档随 prompt 一起传入。在 SOP 与法规变更之间执行全文匹配可能并不划算，尤其是当输入文档规模不断增大时。

该方法的关键步骤是：

**Step 1**：我们构建了一个多层分类法，组织与生物制品流程相关的主题。该分类法包含主主题的层级结构，每个主主题都可以包含子主题。

以下是用于构建该分类法的示例 prompt：

```
Human:

Act as an expert in Biologics procedures for the Food & Drug Administration's Center for Biologics Evaluation and Research (CBER), which help their staff in performing their duties in assuring the safety, purity, potency, and effectiveness of biologics and related products (such as vaccines, live biotherapeutics (probiotics), blood products, and cell, tissue, and gene therapies). Biologics procedures help CBER staff in regulating administration and management of biologics evaluations and reviews including but not limited to clinical studies, electronic submissions, dispute resolutions and management of biologics and related products

I want you to create a hierarchy or taxonomy of topics relating to the biologics procedures. For example, some of the topics may be related to

    - Administrative Guidances

    - Adverse Events and Product Deviation Guidances

    - Application Submission Guidances

    - Biosimilars Guidances

    - Clinical Guidances

    - CMC & GMP Guidances

    - Devices Guidances

    - Generics Guidances

    - Labeling and Promotion Guidances

    - Allergenics Guidances

    - Blood Guidances

    - Cellular and Gene Therapy Guidances

    - Tissue Guidances

    - Vaccine and Related Biological Product Guidances

    - Xenotransplantation Guidances

    - Communication

    - Marketing Applications

    - Compliance

    - Medical Devices

    - Master Files

    - Investigational New Drugs

    - Communication

    - General Information

    - Therapeutic Products

Here's an example of how a topic might be organized:
```

```
<topic>
  <name>Master Files</name>
  <subtopic>
      <name>Drug Substance</name>
  </subtopic>

  <subtopic>
      <name>Packaging Material</name>
  </subtopic>

  <subtopic>
      <name>Preparation Information</name>
  </subtopic>

  <subtopic>
      <name>Clinical Study Data</name>
  </subtopic>

  <subtopic>
      <name>Non-Clinical Study Data</name>
  </subtopic>
</topic>
```

```
Your hierarchy should include all the topics covering the CBER's biologics procedures, and should be sufficiently exhaustive that it covers many different types of activities and duties in different areas of biologics administration, evaluation and review.

Think step by step, using these steps:

Think about all of the important topics that enable CBER's staff to perform their duties in administering, evaluating, reviewing and managing of biologics and related products.
Organize those topics into a hierarchy or taxonomy. There should be a single top-level item called <biologics_topics>.
Output that hierarchy in an XML format. Make sure that each item in the XML is in plain English and doesn't use special characters like the underscore.
```

以下是使用 Anthropic 的 Claude 3 Opus LLM 时 Amazon Bedrock 返回的示例分类层级：

```
Assistant:

<biologics_topics>

  <topic>
    <name>Administrative Guidances</name>
    <subtopic>
      <name>Forms</name>
    </subtopic>
    <subtopic> 
      <name>Meetings</name>
    </subtopic>
    <subtopic>
      <name>Dispute Resolution</name> 
    </subtopic>
  </topic>

  <topic>
    <name>Submission Guidances</name>
    <subtopic>
      <name>Investigational New Drug Applications</name>
    </subtopic>
    <subtopic>
      <name>Biologics License Applications</name>
    </subtopic>
    <subtopic> 
      <name>Supplements and Other Changes to an Approved Application</name>
    </subtopic>
    <subtopic>
      <name>Biosimilars</name>
    </subtopic>
  </topic>

  <topic> 
    <name>Clinical Guidances</name>
    <subtopic>
      <name>Clinical Trial Design</name>
    </subtopic>
    <subtopic>
      <name>Human Subject Protection</name> 
    </subtopic>
    <subtopic>
      <name>Pediatric Studies</name>
    </subtopic>
  </topic>

  <topic>
    <name>Safety Guidances</name> 
    <subtopic>
      <name>Adverse Event Reporting</name>
    </subtopic>
    <subtopic>
      <name>Safety Assessments</name>
    </subtopic>
    <subtopic>
      <name>Pharmacovigilance</name>
    </subtopic>
  </topic>

  <topic>
    <name>Product Quality Guidances</name>
    <subtopic> 
      <name>Chemistry Manufacturing and Controls</name>
    </subtopic>
    <subtopic>
      <name>Good Manufacturing Practices</name>
    </subtopic>
    <subtopic>
      <name>Analytical Methods</name>
    </subtopic>
  </topic>

  <topic>
    <name>Labeling Guidances</name>
    <subtopic>
      <name>Prescribing Information</name> 
    </subtopic>
    <subtopic>
      <name>Medication Guides</name>
    </subtopic>
    <subtopic>
      <name>Promotional Labeling and Advertising</name>
    </subtopic>
  </topic>

  <topic>
    <name>Product Specific Guidances</name>
    <subtopic>
      <name>Vaccines</name>
    </subtopic> 
    <subtopic>
      <name>Blood and Blood Components</name>
    </subtopic>
    <subtopic>
      <name>Cellular and Gene Therapies</name> 
    </subtopic>
    <subtopic>
      <name>Allergenics</name>
    </subtopic>
    <subtopic> 
      <name>Tissues</name>
    </subtopic>
    <subtopic>
      <name>Xenotransplantation Products</name>
    </subtopic>
  </topic>

  <topic>
    <name>Compliance and Enforcement</name>
    <subtopic>
      <name>Inspections</name>
    </subtopic>
    <subtopic>
      <name>Recalls</name> 
    </subtopic>
    <subtopic>
      <name>Warning Letters</name>
    </subtopic>
  </topic>

</biologics_topics>
```

该层级覆盖了 CBER 生物制品监管涉及的关键领域，从行政流程到研究性产品、上市申请、临床开发、安全监测、质量控制、标签，以及主要生物制品类别的合规。该结构旨在涵盖 CBER 工作人员为确保生物制品及相关产品的安全性、纯度、效力和有效性所依赖的指南与流程的广度。

**Step 2**：使用我们构建的分类法，为每个 SOP 标注其涵盖的主题。我们指示模型从主题与子主题列表中选取最具体的那几个。

以下是使用 Anthropic 的 Claude 3 Opus 模型为 SOP 标注分类法主题的示例 prompt：

```
Human:

Act as an expert who understands Biologics procedures.

The following information describes the details of a Biologics procedure. Choose the topics covered in the description only from the following list of possible topics:

{possible_topics}

<procedure_description>

{procedure}

</procedure_description>

Explain your thinking, and end the explanation by generating a JSON string array containing all of the matching topic names.

All topic names must come from the list of possible topics. Do not return a topic unless it is found within the list of valid topics, subtopics, and sub-subtopics. 

If you generate a topic name that is not found in the list of possible topics, it is an error.

Make sure to select the most specific leaf level sub-subtopic or subtopic available from the list of possible topics, subtopics, and sub-subtopics. Be sure your list covers all of the main points of the Biologics procedure description.
```

以下是 Amazon Bedrock 输出的 SOP 主题标注示例：

Assistant:

```
SOPP-8005-Formal-Dispute-Resolution-Process-V6.txt: ['Administrative Guidances', 'Dispute Resolution']

SOPP-8117-Issuing-Tracking-Numbers-eCTD-Format-V9.txt: ['Administrative Guidances', 'Submission Guidances', 'Investigational New Drug Applications', 'Biologics License Applications']

SOPP-8201-Administrative-Processing-Clinical-Holds-INDs_V9.txt: ['Investigational New Drug Applications', 'Meetings', 'Clinical Trial Design', 'Adverse Event Reporting']

SOPP-8301-Receipt-and-Processing-of-Master-Files_V4.txt: ['Administrative Guidances', 'Submission Guidances', 'Compliance and Enforcement']

SOPP-8403-Issuance-Reissuance-and-Voluntary-Revocation-of-Biological-Product-Licenses-V6.txt: ['Submission Guidances', 'Compliance and Enforcement', 'Labeling Guidances']

SOPP-8507V4-IllegitimateProds-Final.txt: ['Compliance and Enforcement', 'Inspections', 'Recalls']

SOPP-8717--Required-Biocompatibility-Training-and-Toxicology-Profiles-for-Evaluation-of-Medical-Devices.txt: ['Product Quality Guidances', 'Submission Guidances', 'Administrative Guidances']

SOPP9151-061306.txt: ['Cellular and Gene Therapies', 'Inspections', 'Tissues']
```

**Step 3：** 为找出监管指南文档与 SOP 之间的关系，我们采用类似的方法，用已构建分类法中最具体的主题或子主题为法规变更打标签。

以下是使用分类法主题为监管指南文档打标签的示例 prompt：

```
Human: 
Act as an expert who understands Biologics procedures. The following information describes a regulatory guidance or change that affects how certain Biologics procedures. Please choose the main topic covered in the change description from the following list of possible topics:
{topics_list} 
<regulatory_guidance_description> 
{regulatory_guidance} </regulatory_guidance_description> 
Explain your thinking, and end the explanation by generating an XML item called <topic> with the relevant topic string in it. Make sure the topic is the most specific one available from the list of possible topics, subtopics, and descendants of those. 
You must choose a single leaf-level XML node from the list of possible topics. The correct answer may be in a <topic> node, or <subtopic> or <subsubtopic>. Choose only one, and return the <name> of the selected node inside of a XML item called <topic>. 
Assistant:
```

**Step 4：** 如果分配给某项法规变更文档的主题与某个 SOP 的某个主题匹配，我们就可以断定该法规变更与该 SOP 相关。

以下是使用 Amazon Bedrock 配合 Anthropic Claude 3 Opus 模型进行监管指南主题对齐的示例输出。

第一个示例使用监管指南[人类细胞、组织以及基于细胞和组织的产品（HCT/P）的监管——小型实体合规指南；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/regulation-human-cells-tissues-and-cellular-and-tissue-based-products-hctps-small-entity-compliance)。对齐得到的分类法主题是 Cellular and Gene Therapies（细胞与基因疗法）。该主题与 [SOPP 9151](https://www.fda.gov/media/109151/download?attachment) 对齐。

```
For reg change Regs/Regulation_Of_HCT_Ps_Small_Entity_Compliance_Guide.txt:

The regulatory guidance is focused on human cells, tissues, and cellular and tissue-based products (HCT/Ps). It provides an overview of the regulations in 21 CFR Part 1271 that apply to HCT/Ps.

The key topics covered include:

Criteria for regulation solely under section 361 of the PHS Act vs as drugs, devices and/or biological products
Registration and listing requirements for HCT/P establishments
Donor eligibility requirements
Current Good Tissue Practice (CGTP) requirements
FDA inspection and enforcement related to HCT/P establishments

Looking at the list of possible topics, the most relevant high-level topic is:

<topic>

  <name>Product Specific Guidances</name>

Within that, the most applicable subtopic is:

<subtopic>

  <name>Cellular and Gene Therapies</name>

Therefore, the most specific and relevant topic for this regulatory guidance is:

<topic>Cellular and Gene Therapies</topic>
```

[正式争议解决：部门层级以上的申诉；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/formal-dispute-resolution-sponsor-appeals-above-division-level-guidance-industry-and-review-staff)这份监管指南被对齐到 Dispute Resolution（争议解决）主题，该主题也被识别为 [SOPP 8005](https://www.fda.gov/media/108908/download?attachment) 涵盖的关键主题。

```
For reg change Regs/Formal_Dispute_Resolution.txt:

The regulatory guidance description is about formal dispute resolution procedures for sponsors to appeal scientific and/or medical disputes to management above the division level at CDER and CBER. This falls under the broad topic of "Administrative Guidances", and the specific subtopic of "Dispute Resolution".

Therefore, the most specific and appropriate topic for this guidance is:

<topic>Dispute Resolution</topic>
```

[提交与审评针对临床试验暂停的完整答复（修订版）；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised)这份监管指南被映射到 Investigational New Drug Applications（研究性新药申请）主题，该主题与 [SOP 8201](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised) 涵盖的内容相符，说明该指南与这份特定 SOP 之间存在强关联：

针对法规变更 Regs/Submitting_And_Reviewing_Complete_Responses_To_Clinical_Holds.txt：

该监管指南讲的是针对 IND 临床试验暂停提交和审阅答复的流程。要点如下：

- 当 FDA 对某项 IND 施加临床试验暂停（clinical hold）时，申办方提交覆盖全部临床暂停问题的完整答复、且 FDA 通知申办方可以继续之前，研究不得推进。
- 该指南说明了申办方应在完整答复中包含哪些内容、如何提交，以及 FDA 将如何在 30 天内审阅并作出回应。
- 它还涵盖程序细节，例如 FDA 将如何跟踪和衡量 PDUFA 目标中的 30 天答复时限。

```
Looking at the list of possible topics, this guidance falls under:

<topic>

  <name>Submission Guidances</name>

  <subtopic>

    <name>Investigational New Drug Applications</name>

  </subtopic>

</topic>

Since it is specifically about the process for responding to clinical holds on INDs, the most relevant leaf-level topic is:

<topic>Investigational New Drug Applications</topic>
```

在测试数据集中，分类法对齐方法在准确识别法规变更与 SOP 之间的关系方面是有效的。

## 经验总结

下表总结了我们的观察结果。表中以***红色粗斜体***标记的 SOP 为误识别。

| **法规** | **全文匹配** | **分类法主题匹配** | **文本相似度** |  |
| --- | --- | --- | --- | --- |
| **向量嵌入** | **关键词搜索** |  |  |  |
| [人类细胞、组织以及基于细胞和组织的产品（HCT/P）的监管——小型实体合规指南；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/regulation-human-cells-tissues-and-cellular-and-tissue-based-products-hctps-small-entity-compliance) | [SOPP 9151](https://www.fda.gov/media/109151/download?attachment) | [SOPP 9151](https://www.fda.gov/media/109151/download?attachment) | [SOPP 9151](https://www.fda.gov/media/109151/download?attachment) | [***SOPP 8301***](https://www.fda.gov/media/158382/download?attachment) |
| [正式争议解决：部门层级以上的申诉；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/formal-dispute-resolution-sponsor-appeals-above-division-level-guidance-industry-and-review-staff) | [SOPP 8005](https://www.fda.gov/media/108908/download?attachment) | [SOPP 8005](https://www.fda.gov/media/108908/download?attachment) | [***SOPP 8717***](https://www.fda.gov/media/93416/download?attachment) | [***SOPP 8201***](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised) |
| [提交与审评针对临床试验暂停的完整答复（修订版）；行业指南](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised) | [SOP 8201](https://fda.report/media/88774/SOPP+8201-IND-Clinical-Holds-Ver_5-Final_March_2020.pdf) | [SOP 8201](https://fda.report/media/88774/SOPP+8201-IND-Clinical-Holds-Ver_5-Final_March_2020.pdf) | [***SOPP 8717***](https://www.fda.gov/media/93416/download?attachment) | [SOP 8201](https://fda.report/media/88774/SOPP+8201-IND-Clinical-Holds-Ver_5-Final_March_2020.pdf) |

结合全文匹配与基于分类法的主题匹配方法，并配合 Amazon Bedrock 和 Anthropic Claude 3 Opus 模型，能够准确识别出数据集中与监管指南文档最密切相关的 SOP。相比之下，使用向量嵌入和关键词搜索的文本相似度方法在将 SOP 正确匹配到相关监管指南文档方面表现较差。

## 结语

本文中，我们使用 Amazon Bedrock 和 Anthropic 的 Claude 3 Opus 模型，探索了多种快速识别法规变更与组织 SOP 之间关系的方法。我们评估的方法包括全文匹配、使用向量嵌入和关键词搜索的文本相似度，以及基于分类法的主题对齐方法。

我们的发现表明，在测试数据集中准确识别与监管指南文档最密切相关的 SOP 方面，全文匹配和基于分类法的主题匹配最为有效。相比之下，使用向量嵌入和关键词搜索的文本相似度技术在稳定地将 SOP 匹配到相关监管文档方面可靠性较低。

全文匹配和基于分类法的方法都可以成为组织评估法规变更与内部 SOP 关系的可行选项。全文匹配可能给出更准确的结果，但需要提供 SOP 或输入文档的完整文本，这会带来成本影响。

另一方面，基于分类法的方法提供了一种结构化方式，将文档内容映射到可定制的主题层级。尽管初始分类法可能并不完整或不够准确，但可以进一步丰富并按组织的具体需求剪裁。如果你选择基于分类法的方法，可以先用机器生成的起点，然后加以细化，使其更好地适配你的领域和用例需求。

通过采用基于分类法的方法并按自身需求调整，组织不仅能识别法规变更与 SOP 之间的关系，还能评估法规变更对其内部流程的潜在影响。这有助于简化依据新法规筛查 SOP 的流程，并在生命科学等受监管行业加速影响评估。

如果你想在自己的 AWS 环境中实现类似方案，请联系你的 AWS 客户团队寻求帮助。

我要感谢 Greg Sommerville、Thomaz Silva 和 Murtuza Bootwala 对本博客的贡献。没有他们，这篇文章无法完成。

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/16/ML-16693-author-ganeshrd-Image-003-1-100x117.jpeg)**Ganesh Raam Ramadurai** 是 Amazon Web Services（AWS）的高级技术项目经理，领导 PACE（Prototyping and Cloud Engineering）团队。他专注于交付创新的、以 AI/ML 和生成式 AI 驱动的原型，帮助 AWS 客户探索新兴技术并释放现实商业价值。Ganesh 高度关注实验、可扩展性和影响力，工作处于战略与工程的交叉点——加速客户创新，并在各行业促成变革性成果。
