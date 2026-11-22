---
vendor: aws_bedrock
title: Fast-track SOP processing using Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/fast-track-sop-processing-using-amazon-bedrock
date: 2025-06-02
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: dbefbb0c4bcc
---

# Fast-track SOP processing using Amazon Bedrock

Standard operating procedures (SOPs) are essential documents in the context of regulations and compliance. SOPs outline specific steps for various processes, making sure practices are consistent, efficient, and compliant with regulatory standards.

SOP documents typically include key sections such as the title, scope, purpose, responsibilities, procedures, documentation, citations (references), and a detailed approval and revision history. In FDA-regulated industries such as healthcare and life sciences, SOPs play a crucial role in defining manufacturing, clinical, laboratory, quality control, quality assurance, and regulatory compliance practices.

When a regulatory body like the US Food and Drug Administration (FDA) introduces changes to regulations, organizations are required to evaluate the changes against their internal SOPs. When necessary, they must update their SOPs to align with the regulation changes and maintain compliance.

In this post, we show different approaches using [Amazon Bedrock](https://aws.amazon.com/bedrock/) to identify relationships between regulation changes and SOPs.

## Challenge

In the healthcare and life sciences industry, regulatory authorities like the FDA and the European Medicines Agency (EMA) frequently update regulations across various areas, such as clinical trials, medical devices, drug development and approvals, quality risk management, systems and data management, and technology adoption. These regulatory updates often require organizations to correspondingly update their internal SOPs to align with the changes. This process is typically manual, requiring a team of subject matter experts to review the regulatory changes, screen the SOPs to identify relevance, determine the impact, and specify what needs to be updated. This manual approach adds significant overhead for companies and can result in review cycles lasting several days to months.

To address this challenge, we explore approaches that can help automate the identification of relationships between regulatory changes and SOPs. These approaches can also be extended to assess the impact of regulatory changes on an organization’s internal processes and documentation. By using automation, companies can streamline the SOP update process, reducing the time and resources required to maintain alignment with evolving regulatory requirements.

## Sample Data

For this post, we used SOPs published by the FDA’s Center for Biologics Evaluation and Research. These publicly available SOPs are used by the FDA staff to guide their duties.

Specifically, we focused on the following SOPs related to biologics procedures. This narrow scope allowed us to dive deeper into a specific regulatory domain within the larger healthcare and life sciences industry.

- [SOPP 8005: Formal Dispute Resolution Process](https://www.fda.gov/media/108908/download?attachment)
- [SOPP 8117: Issuing Tracking Numbers in Advance of Electronic Submissions in eCTD Format](https://www.fda.gov/media/93416/download?attachment)
- [SOPP 8201: Administrative Processing of Clinical Holds for Investigational New Drug Applications](https://fda.report/media/88774/SOPP+8201-IND-Clinical-Holds-Ver_5-Final_March_2020.pdf)
- [SOPP 8301: Receipt and Processing of Master Files](https://www.fda.gov/media/158382/download?attachment)
- [SOPP 8403: Issuance, Reissuance, and Voluntary Revocation of Biological Products Licenses](https://www.fda.gov/media/108918/download?attachment)
- [SOPP 8507: Procedures for Responding to an Illegitimate Product Notification and Request for Termination of Notification](https://www.fda.gov/media/96005/download?attachment)
- [SOPP 8717: Required Biocompatibility Training and Toxicology Profiles for Evaluation of Medical Devices](https://fda.report/media/109201/SOPP-8717--Required-Biocompatibility-Training-and-Toxicology-Profiles-for-Evaluation-of-Medical-Devices.pdf)
- [SOPP 9151: Procedures for Handling Requests for Exemptions and Alternative Procedures for Human Cells, Tissues, and Cellular and Tissue-Based Products (HCT/Ps) Under 21 CFR Section 1271.155](https://www.fda.gov/media/109151/download?attachment)

In addition to the SOPs, we also used three of the FDA’s Biologics Guidance Documents to test the relationship between the regulatory documents and the SOPs.

These guidance documents describe the FDA’s policy interpretations on regulatory issues related to the biologics domain. They cover a wide range of topics, including processing, content, evaluation, approval, inspection, and enforcement of policies. The guidance documents also discuss specific products or issues relating to the design, production, labeling, promotion, manufacturing, and testing of regulated products.

We used the following specific FDA Biologics Guidance Documents for this analysis:

- [Regulation of Human Cells, Tissues, and Cellular and Tissue-Based Products (HCT/Ps) – Small Entity Compliance Guide; Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/regulation-human-cells-tissues-and-cellular-and-tissue-based-products-hctps-small-entity-compliance)
- [Formal Dispute Resolution: Appeals Above the Division Level; Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/formal-dispute-resolution-sponsor-appeals-above-division-level-guidance-industry-and-review-staff)
- [Submitting and Reviewing Complete Responses to Clinical Holds (Revised); Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised)

## Approaches

A key step in assessing the impact of regulatory changes is to identify if a regulatory guidance is related to an organization’s SOPs. We used Amazon Bedrock along with [Amazon Simple Storage Service (Amazon S3)](https://aws.amazon.com/s3/) to store the input dataset.

Amazon Bedrock is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies like AI21 Labs, Anthropic, Cohere, Meta, Mistral, Stability AI, and Amazon through a single API, along with a broad set of capabilities to build generative AI applications with security, privacy, and responsible AI.

Our experiments used Anthropic’s Claude 3 Opus large language model (LLM) on Amazon Bedrock. However, you can use the broad selection of models available on Amazon Bedrock to experiment with alternative models and choose the one that best suits your specific requirements. Amazon Bedrock frequently releases updated versions of existing AI models that can be accessed and used by simply applying a configuration change, making it a highly flexible choice for deploying the latest AI capabilities.

We focused on the following approaches:

- **Full document match **– Comparing the full text of the regulatory guidance and SOP documents
- **Text similarity** – This approach consists of two options:  **Vector embeddings** – Measuring the semantic similarity between the guidance and SOP texts **Keyword Search** – Identifying relevant keywords and their occurrences in the documents
- **Taxonomy topic match** – Mapping the guidance and SOP content to a taxonomic structure to identify topical relationships

This post details the approaches we explored and the learnings from our experiments.

### Full document match

The following diagram illustrates the full document match architecture.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/16/ML-17198-arch-diag-Image-001.png)

In this approach, we compared each regulatory change to every SOP by passing the full contents of the SOP and the regulatory change to the model. The goal was to identify relationship between the regulatory change and the SOP.

The following is a sample prompt to check if an SOP is related to a regulation change:

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

When we ran the full document matching approach using Amazon Bedrock across all the SOPs and the regulatory guidance documents in the dataset, the results showed accurate identification of related SOPs. For example, [SOPP 9151](https://www.fda.gov/media/109151/download?attachment) was correctly identified as the only SOP related to the [Regulation of Human Cells, Tissues, and Cellular and Tissue-Based Products (HCT/Ps) – Small Entity Compliance Guide; Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/regulation-human-cells-tissues-and-cellular-and-tissue-based-products-hctps-small-entity-compliance) regulation change, with others being identified as unrelated:

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

Similarly, [SOPP 8005](https://www.fda.gov/media/108908/download?attachment) was correctly identified as the only SOP related to the [Formal Dispute Resolution: Appeals Above the Division Level; Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/formal-dispute-resolution-sponsor-appeals-above-division-level-guidance-industry-and-review-staff) regulation change, and the other SOPs were identified as unrelated.

Finally, [SOP 8201](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised) was also correctly identified as the only SOP related to the [Submitting and Reviewing Complete Responses to Clinical Holds (Revised); Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised) regulation change.

These results demonstrate the effectiveness of the full document matching approach in accurately linking the relevant SOPs to their corresponding regulatory guidance documents.

### Text similarity

The following diagram illustrates the text similarity match workflow.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/16/ML-17198-arch-diag-Image-002.png)

In our second approach, we indexed the SOPs using either vector embeddings for semantic similarity or a keyword-based similarity approach. This allowed us to submit the contents of a regulatory change as a query and return the most similar SOP documents.

The steps involved in this text similarity approach are:

- Index the SOPs:  For a vector embeddings approach, we generated vector representations of the SOP contents using an LLM to capture semantic similarities. For a keyword-based approach, we identified the most relevant keywords in each SOP and built an index based on their occurrences.
- Query the index:  For a given regulatory change, we submitted the text as a query to the SOP index. The index then returned the most similar SOPs based on the chosen similarity metric (semantic or keyword-based).

#### Vector Search

For the text similarity approach, we used the open source in-memory database ChromaDB to generate the vector embeddings and perform the search.

We created a collection within ChromaDB containing all the SOP documents. We then independently queried each regulation guidance document text against this SOP collection. We used the default L2 distance algorithm, where a lower distance score indicates a closer match between the query and the indexed SOP documents.

Although the vector embedding-based text similarity approach identified the top matching SOP document in some cases, it also produced some inaccurate results.

For example, when querying with the [Regulation of Human Cells, Tissues, and Cellular and Tissue-Based Products (HCT/Ps) – Small Entity Compliance Guide; Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/regulation-human-cells-tissues-and-cellular-and-tissue-based-products-hctps-small-entity-compliance) regulation, [SOPP 9151](https://www.fda.gov/media/109151/download?attachment) was correctly identified as the top match. However, a few other unrelated SOP documents also had low distance scores, which could potentially lead to them being misidentified as relevant:

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

Similarly, when querying with the [Formal Dispute Resolution: Appeals Above the Division Level; Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/formal-dispute-resolution-sponsor-appeals-above-division-level-guidance-industry-and-review-staff) regulation, the vector search incorrectly identified [SOPP 8717](https://www.fda.gov/media/93416/download?attachment) as the best match, whereas [SOPP 8005](https://www.fda.gov/media/108908/download?attachment), which is more directly related to formal dispute resolution, had a higher distance score:

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

Finally, for the regulation [Submitting and Reviewing Complete Responses to Clinical Holds (Revised); Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised), the vector search again identified [SOPP 8717](https://www.fda.gov/media/93416/download?attachment) as the top match, rather than the more relevant [SOP 8201](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised):

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

#### Keyword search

We also explored a keyword-based similarity method using the Whoosh Python search library. We first created an index of all the SOP documents using the Whoosh library. Then, for each regulation guidance document, we separately searched the index using a Whoosh query parser.

The Whoosh library returns a search score for each matched SOP document, where a higher score indicates a better match to the query.

When searching for the [Regulation of Human Cells, Tissues, and Cellular and Tissue-Based Products (HCT/Ps) – Small Entity Compliance Guide; Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/regulation-human-cells-tissues-and-cellular-and-tissue-based-products-hctps-small-entity-compliance) regulation, the top matching document was incorrectly identified as [SOPP 8301](https://www.fda.gov/media/158382/download?attachment) instead of the more relevant [SOPP 9151](https://www.fda.gov/media/109151/download?attachment):

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

Similarly, when searching for the [Formal Dispute Resolution: Appeals Above the Division Level; Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/formal-dispute-resolution-sponsor-appeals-above-division-level-guidance-industry-and-review-staff) regulation using the keyword-based similarity approach, the Whoosh library again incorrectly identified [SOPP 8301](https://www.fda.gov/media/158382/download?attachment) as the top matching document, instead of the more relevant [SOPP 8005](https://www.fda.gov/media/108908/download?attachment):

```
8 results found
<Hit {'fname': 'SOPP-8301-Receipt-and-Processing-of-Master-Files_V4.txt'}> with score of 721.9535225922815
…
…
```

In contrast with the previous examples, when searching for the [Submitting and Reviewing Complete Responses to Clinical Holds (Revised); Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised) regulation, [SOP 8201](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised) was correctly identified as the top matching document:

```
8 results found
<Hit {'fname': 'SOPP-8201-Administrative-Processing-Clinical-Holds-INDs_V9.txt'}> with score of 503.3284407067554
…
…
```

These results indicate that although the keyword-based similarity approach can be effective in some cases, it might also struggle to accurately identify the most relevant SOPs, similar to the challenges faced with the vector embedding-based method.

### Taxonomy-based topic matching

The following diagram illustrates the taxonomy-based topic matching architecture.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/16/ML-17198-arch-diag-Image-003.png)

In our third approach, we focused on building a hierarchical taxonomy of topics associated with the subject of biologics procedures. This taxonomy-based approach aimed to capture the topical relationships between the regulatory guidance documents and the SOPs. This approach has the potential to provide a cost-effective solution, because the entire SOP or input document doesn’t need to be passed with the prompt for every query to the LLM. Performing a full text match between an SOP and a regulatory change might not be a cost-effective approach, especially as the input documents grow in size.

The key steps in this approach were:

**Step 1**: We constructed a multi-level taxonomy that organized the topics related to biologics procedures. The taxonomy included a hierarchy of main topics, each of which could include subtopics.

The following is an example prompt for building the taxonomy:

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

The following is a sample taxonomy hierarchy returned by Amazon Bedrock when using Anthropic’s Claude 3 Opus LLM:

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

This hierarchy covers the key areas involved in CBER’s regulation of biologics, from administrative processes, to investigational products, marketing applications, clinical development, safety monitoring, quality control, labeling, and compliance for the major categories of biological products. The structure aims to capture the breadth of guidances and procedures that CBER staff rely on to ensure the safety, purity, potency and effectiveness of biologics and related products.

**Step 2**: Using the taxonomy we built, we labeled each SOP with the topics that are covered in the SOP. We instructed the model to select the most specific ones from the list of topics and subtopics.

The following is an example prompt to label SOPs with taxonomy topics using Anthropic’s Claude 3 Opus model:

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

The following is the example SOP topic labeling output from Amazon Bedrock:

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

**Step 3:** To find the relationships between the regulatory guidance documents and the SOPs, we followed a similar approach to label the regulatory changes with the most specific topics or subtopics from the built taxonomy.

The following is an example prompt to label regulatory guidance documents with taxonomy topics:

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

**Step 4:** If the topic assigned to a regulatory change document matches one of the topics of an SOP, we can conclude the regulatory change is related to the SOP.

The following are example outputs of regulatory guidance topic alignment using Amazon Bedrock with the Anthropic Claude 3 Opus model.

The first example uses regulatory guidance [Regulation of Human Cells, Tissues, and Cellular and Tissue-Based Products (HCT/Ps) – Small Entity Compliance Guide; Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/regulation-human-cells-tissues-and-cellular-and-tissue-based-products-hctps-small-entity-compliance). The aligned taxonomy topic is Cellular and Gene Therapies. This topic aligns with [SOPP 9151](https://www.fda.gov/media/109151/download?attachment).

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

The [Formal Dispute Resolution: Appeals Above the Division Level; Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/formal-dispute-resolution-sponsor-appeals-above-division-level-guidance-industry-and-review-staff) regulatory guidance was aligned with the Dispute Resolution topic, which was also identified as a key topic covered in [SOPP 8005](https://www.fda.gov/media/108908/download?attachment).

```
For reg change Regs/Formal_Dispute_Resolution.txt:

The regulatory guidance description is about formal dispute resolution procedures for sponsors to appeal scientific and/or medical disputes to management above the division level at CDER and CBER. This falls under the broad topic of "Administrative Guidances", and the specific subtopic of "Dispute Resolution".

Therefore, the most specific and appropriate topic for this guidance is:

<topic>Dispute Resolution</topic>
```

The [Submitting and Reviewing Complete Responses to Clinical Holds (Revised); Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised) regulatory guidance was mapped to the Investigational New Drug Applications topic, which was found to be aligned with the content covered in [SOP 8201](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised), indicating a strong relationship between the guidance and this particular SOP:

For reg change Regs/Submitting_And_Reviewing_Complete_Responses_To_Clinical_Holds.txt:

The regulatory guidance is about the process for submitting and reviewing responses to clinical holds on INDs. The key points are:

- When FDA imposes a clinical hold on an IND, the study cannot proceed until the sponsor submits a complete response addressing all the clinical hold issues, and FDA notifies the sponsor they can proceed.
- The guidance describes what the sponsor should include in the complete response, how to submit it, and how FDA will review and respond to it within 30 days.
- It also covers procedural details like how FDA will track and measure the 30-day response timeline for PDUFA goals.

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

The taxonomic alignment approach was effective in accurately identifying the relationships between the regulatory changes and the SOPs in the test dataset.

## Learnings

The following table summarizes our observations. SOPs formatted as ***red bold italic*** in the table are misidentified.

| **Regulation** | **Full text match** | **Taxonomy topic match** | **Text similarity** |  |
| --- | --- | --- | --- | --- |
| **Vector embeddings** | **Keyword Search** |  |  |  |
| [Regulation of Human Cells, Tissues, and Cellular and Tissue-Based Products (HCT/Ps) – Small Entity Compliance Guide; Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/regulation-human-cells-tissues-and-cellular-and-tissue-based-products-hctps-small-entity-compliance) | [SOPP 9151](https://www.fda.gov/media/109151/download?attachment) | [SOPP 9151](https://www.fda.gov/media/109151/download?attachment) | [SOPP 9151](https://www.fda.gov/media/109151/download?attachment) | [***SOPP 8301***](https://www.fda.gov/media/158382/download?attachment) |
| [Formal Dispute Resolution: Appeals Above the Division Level; Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/formal-dispute-resolution-sponsor-appeals-above-division-level-guidance-industry-and-review-staff) | [SOPP 8005](https://www.fda.gov/media/108908/download?attachment) | [SOPP 8005](https://www.fda.gov/media/108908/download?attachment) | [***SOPP 8717***](https://www.fda.gov/media/93416/download?attachment) | [***SOPP 8201***](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised) |
| [Submitting and Reviewing Complete Responses to Clinical Holds (Revised); Guidance for Industry](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/submitting-and-reviewing-complete-responses-clinical-holds-revised) | [SOP 8201](https://fda.report/media/88774/SOPP+8201-IND-Clinical-Holds-Ver_5-Final_March_2020.pdf) | [SOP 8201](https://fda.report/media/88774/SOPP+8201-IND-Clinical-Holds-Ver_5-Final_March_2020.pdf) | [***SOPP 8717***](https://www.fda.gov/media/93416/download?attachment) | [SOP 8201](https://fda.report/media/88774/SOPP+8201-IND-Clinical-Holds-Ver_5-Final_March_2020.pdf) |

The combination of the full text matching and taxonomy-based topic matching approaches, using Amazon Bedrock and the Anthropic Claude 3 Opus model, enabled accurate identification of the SOPs most closely related to the regulation guidance documents in the dataset. In contrast, the text similarity methods using vector embeddings and keyword search were less successful in correctly matching the SOPs to the relevant regulatory guidance documents.

## Conclusion

In this post, we explored various approaches to quickly identify the relationships between regulatory changes and an organization’s SOPs, using Amazon Bedrock and Anthropic’s Claude 3 Opus model. The methods we evaluated included full text matching, text similarity using vector embeddings and keyword search, and a taxonomy-based topic alignment approach.

Our findings indicate that the full text matching and taxonomy-based topic matching were the most effective in accurately identifying the SOPs most closely related to the regulation guidance documents in the test dataset. In contrast, the text similarity techniques using vector embeddings and keyword search were less reliable in consistently matching the SOPs to the relevant regulatory documents.

Both the full text matching and taxonomy-based approaches can be viable options for organizations to assess the relationships between regulatory changes and their internal SOPs. The full text matching might provide more accurate results but requires providing the complete text of the SOP or input document, which could have cost implications.

The taxonomy-based approach, on the other hand, offers a structured way to map the content of the documents to a customizable topic hierarchy. Although the initial taxonomy might not be complete or fully accurate, it can be further enriched and tailored to an organization’s specific needs. If you choose a taxonomy-based approach, you can use a machine-generated starting point and then refine it to better suit your domain and use case requirements.

By adopting the taxonomy-based approach and adapting it to their specific needs, organizations can not only identify the relationships between regulatory changes and SOPs, they can also assess the potential impact of regulatory changes on their internal procedures. This can help streamline the process of screening SOPs against new regulations and fast-track the impact assessment in regulated industries like life sciences and others.

If you want to implement a similar solution in your AWS environment, reach out to your AWS account team for assistance.

I would like to acknowledge Greg Sommerville, Thomaz Silva and Murtuza Bootwala for their contributions to this blog. It couldn’t have been done without them.

### About the Author

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/16/ML-16693-author-ganeshrd-Image-003-1-100x117.jpeg)**Ganesh Raam Ramadurai** is a Senior Technical Program Manager at Amazon Web Services (AWS), where he leads the PACE (Prototyping and Cloud Engineering) team. He specializes in delivering innovative, AI/ML and Generative AI-driven prototypes that help AWS customers explore emerging technologies and unlock real-world business value. With a strong focus on experimentation, scalability, and impact, Ganesh works at the intersection of strategy and engineering—accelerating customer innovation and enabling transformative outcomes across industries.
