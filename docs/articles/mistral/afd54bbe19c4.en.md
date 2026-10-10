---
vendor: mistral
title: Agentic Search. More accurate and efficient results from your AI systems.
original_title: Introducing Agentic Search
url: https://mistral.ai/news/agentic-search
date: 2026-08-20
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: aa7203292bce
---

Product

# Agentic Search. More accurate and efficient results from your AI systems.

August 20, 2026

By Mistral


9 min read




Thinking

Summary

Mistral Agentic Search delivers more accurate search results while reducing turns, token use, and latency against FinanceBench and OfficeQA Pro benchmarks. Agentic Search is the retrieval layer that enables AI systems to navigate, read, and verify information inside even the most complex documents. Available through Mistral Search Toolkit and Libraries.

Mistral Agentic Search helps enterprises get better results from their AI systems by letting models search and navigate their organization’s most complex data and documents. Agentic Search introduces a multi-step retrieval loop for finding, inspecting, and verifying information across data sources, wherever it is stored. Agentic Search is available through [Mistral Search Toolkit](https://docs.mistral.ai/studio/search-toolkit), built into [Libraries](https://docs.mistral.ai/studio/libraries) in both [Studio](https://mistral.ai/products/studio/) and [Vibe](https://mistral.ai/products/vibe/), and gives you:

- **Support for sensitive domain-specific data**. Mistral’s portable and open tooling helps you unlock value from your data without crossing your isolation boundaries in the cloud or on-premises.
- **Improved search results. **Your models can search and navigate your data beyond retrieved chunks–inside long, dense documents or across multiple sources.
- **Access to existing indexes.** Agentic Search builds on your existing search index using five tools: `search`, `open`, `navigate`, `read`, and `grep`.
- **Higher accuracy.** Agentic Search delivers to **3x** **correctness** on financial filings, from 26.7% to 86%, based on FinanceBench. On table-heavy, multi-doc questions of the OfficeQA Pro benchmark, we measure a **+45.6 point** gain (6.3% to 51.9%).
- **Lower latency and token use.** Targeted navigation enables Agentic Search to reduce p90** latency up to 39.6%**. Fewer repeated searches reduce token consumption by up to one-third.

## **Data creates competitive advantage**

Competitive edge is built upon years of real-world operations–your data, your processes, and your domain expertise. Proprietary knowledge is both critical to your success and highly confidential, meaning it lives behind isolation boundaries, segmented deployments, and self-hosted platforms. It accumulates in financial filings, legal contracts, internal resources, and government records–long, dense documents that traditional search methods can’t navigate effectively.

Agents that learn and improve continuously can help you compound your competitive advantage, but these agents are often separated from confidential data and proprietary knowledge for security reasons. Getting real impact from AI means pairing frontier reasoning with retrieval tools that can safely reach your most sensitive material.

## **Traditional RAG falls short**

Traditional, one-shot RAG retrieves a fixed set of text chunks and asks a model to answer in a single pass. This works when the answer appears in one of the top results, but falters when the model must navigate a long report, follow references, compare multiple documents, or verify the underlying evidence.

The limitation is more pronounced on dense, complex data and documents. The information needed to answer a question may be spread across documents or buried in a particular table, footnote, or clause. One-shot RAG-based search fails to use the full power of frontier AI and to provide reliable answers for three reasons:

- **Retrieval without reasoning: **The model must answer from the chunks selected during the initial retrieval, even when they are incomplete or not relevant. It cannot decide that it needs a different document, another section, or more context before responding, which limits the impact of the model’s reasoning.
- **Chunk-level limit: **Critical data is often held in complex multi-modal documents. When asked, “*What was the company’s effective tax rate in Q3?”* an index may find the correct document but cannot open it, navigate to the table, read the surrounding context, or verify the answer.
- **No iteration: **Many questions need more than one retrieval pass to get the correct answer. The model may need to refine its search, inspect a promising document, follow a reference, compare multiple sources, keep track of what it has seen, and try a new route when the first results are insufficient. One-shot RAG provides no way to take these next steps.

Without Agentic Search (one-shot retrieval)

Using specifically only the reported values for all individual calendar months in 1953, what is the total sum of these values of expenditures for U.S. national defense and associated activities (in millions of nominal dollars)?

Trajectory 1 tool_call (search only)

`search("national defense expenditures monthly 1953")` → 10 hits: a scatter of monthly bulletins (Table 3), each framed fiscal-year, covering only part of 1953.

I found January–June 1953 data. But I need July–December 1953 monthly values to compute an answer.

With Agentic Search

Using specifically only the reported values for all individual calendar months in 1953, what is the total sum of these values of expenditures for U.S. national defense and associated activities (in millions of nominal dollars)?

Trajectory 3 tool_calls (2× search → read)

`search("national defense expenditures monthly 1953")` → per-month bulletins (partial year)

`search("…1953 November December 1954 to date")` → surfaces `treasury_bulletin_1954_02.pdf`p.15 (Table 3, all 12 months of 1953)

`read(treasury_bulletin_1954_02.pdf, p.15)` → pulls the complete Table 3

Monthly Values for 1953

Table 3, in $millions

| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3,632 | 3,501 | 3,789 | 3,891 | 3,746 | 4,056 | 3,890 | 3,519 | 3,787 | 3,647 | 3,540 | 3,465 |

Sum = 44,463.

## **How Agentic Search works**

[Mistral Search Toolkit](https://docs.mistral.ai/en/studio/search-toolkit) provides open modules for ingesting, embedding, and indexing critical and complex data in the cloud or on-premises. Agentic Search builds on this index by giving the model five tools that resemble familiar file-system operations:

- `search` finds relevant documents across the corpus using the existing index.
- `open` opens a specific document.
- `navigate` moves to a page, section, or region within it.
- `read` retrieves the content at that location.
- `grep` finds a pattern within an open document.

Rather than answering only from the initial top-*k* results, the model can inspect what it finds, refine its search, open relevant documents, navigate to specific sections, and read the source material before answering. The index identifies likely sources; Agentic Search determines what to inspect within and across them.

### **One-shot RAG**

![None](https://mistral.ai/_astro/pasted-image-4_INqkQ.webp?dpl=6abbd11780b53c00082eea6f)

### **Agentic Search**

![None](https://mistral.ai/_astro/pasted-image-5_Z1Id2ck.webp?dpl=6abbd11780b53c00082eea6f)

These tools do not require fine-tuning or model-specific training. As models get better at reasoning and tool use, retrievals get better without infrastructure changes. This is a key property: retrieval quality scales with model capability instead of being capped by your chunking strategy.

## **Use Agentic Search for**

- **Long documents.** Filings, contracts, manuals, technical specifications, and reports where the answer may appear on a particular page or in a specific table, clause, figure, or footnote.
- **Questions across multiple sources.** Research that requires the model to find, compare, or reconcile evidence from several documents before reaching an answer.
- **Answers that must be verified.** Financial figures, legal clauses, regulatory references, and operational data, where the response can be referenced in a stable and specific document location.
- **Tables and structured documents.** Financial statements, government records, and scanned PDFs where meaning depends on rows, columns, page position, or surrounding context–not narrative text alone.

## **Indexed retrieval is the right starting point for**

- **Direct lookups.** Short, clean documents where the answer is likely to appear in one of the first retrieved chunks.
- **High-volume search.** Keyword or semantic lookups that need to return relevant passages without reasoning over or navigating through them.
- **Simple, predictable questions.** Use cases where the likely source and location of the answer are known in advance and additional retrieval steps are unlikely to improve the result.

One-shot RAG is often sufficient for these searches. Add Agentic Search when questions require the model to move beyond the initial results and investigate the source material. A well-configured index remains the right foundation in both cases.

## **More relevant results, faster**

We benchmarked Agentic Search on two industry-standard evaluations, using the out-of-the-box Mistral Search Toolkit stack: default chunking, default ranking, no tuning. These results are floors, not ceilings, meaning you can further improve result quality with use-case-specific tuning.

With these benchmarks, we tested two models using the Mistral Search Toolkit: **Mistral Medium 3.5** (MM 3.5) and **Z.ai GLM-5.2** (GLM-5.2), showcasing performance of a smaller model (MM 3.5) and a larger model (GLM-5.2).

Benchmark results are consistent: the agentic loop delivers substantive quality improvements and navigation tools increase accuracy while reducing wasted tokens, turns, and latency. We observe the same performance patterns across first- and third-party models, which indicates that Agentic Search is model-agnostic, and that search quality should improve with new models.

### **FinanceBench: 368 SEC filings, 150 questions**

FinanceBench (Islam et al., 2023) tests financial question-answering over 368 SEC filings (10-K / 10-Q / 8-K), averaging ~147 pages each, ~53,900 pages total: long, table-heavy financial documents. Answers scored by an LLM judge calibrated against human labels.

We found:

- **The search-only Agentic loop is the biggest quality lever.** Moving from one-shot RAG to a search-only loop lifts accuracy by **+47.3pp** for MM 3.5 and **+52.6pp** for GLM-5.2–a ~3x improvement for both models. Because models can search iteratively, they can recover from weak first results, refine queries, and use the index as an active tool.
- **Navigation adds accuracy. **Adding open, navigate, read, and grep lifts accuracy again (**+8.7pp** for MM 3.5, **+6.7pp** for GLM-5.2). This means a targeted drill-in search beats repeated broad search in complex documents.
- **Token and performance efficiency improve with better retrieval tools.** The full loop with Navigation answers more questions correctly while using fewer tokens than the search-only loop (MM 3.5: **-23.9% token usage**, GLM-5.2: **-33.7%**). The retrieval tools are not additional overhead–they replace wasted search retries with precise navigation.
- **Latency goes down where it matters.** Across FinanceBench, adding navigation retrieval tools improves latency: p90 drops **255s → 154s** and mean latency drops **108s → 71s**. In general, we see the search-only loops conduct repeated broad searches, while navigation helps the model identify evidence more quickly.

### **OfficeQA Pro: 696 Treasury Bulletins, 133 questions**

OfficeQA Pro is a verifiable numeric benchmark over historical U.S. Treasury Bulletins: scanned, table-heavy government-finance PDFs across a 696-document, ~89,000-page corpus. We report the first pass for the 133-question "pro" subset.

We found:

- **Agentic Search and the Agentic loop + Navigation are successful against a harder, verifiable benchmark.** OfficeQA Pro has numeric answers, scanned PDFs, and deep table lookups. Even here, the full agentic loop lifts accuracy materially from one-shot RAG, reaching **51.9%** for GLM-5.2 (**+45.6pp**) and increasing **+27.1pp** for MM 3.5.
- **Navigation improves quality while cutting waste.** Using the full loop (Agentic loop + Navigation) improves accuracy by** up to 35.6% **(**+7.5pp, **MM 3.5; **+8.3pp, 19.0%** GLM-5.2), while reducing token consumption. Turns declined by **up to 7.0%** (MM 3.5, **2.3%** GLM-5.2).
- **The harder the benchmark, the more important the retrieval loop becomes.** OfficeQA Pro is built around numeric answers in scanned, table-heavy documents. One-shot RAG barely gets started, while the agentic loop allows the model to search iteratively, inspect evidence, and deliver substantial accuracy improvements.
- **The tooling stack drives substantial impact on document intelligence and search performance. **Per [Kimi research](https://www.kimi.ai/blog/kimi-k3), GLM-5.2 scores 41.4% on OfficeQA Pro with the Claude Code harness, compared with 51.9% on the Mistral harness–+10.5pp on the same underlying model.

## **Getting started**

Learn more about Agentic Search in the [documentation](https://docs.mistral.ai/studio/search/agentic-search). You can get started across cloud and on-premises deployments using either:

- [Mistral Search Toolkit](https://docs.mistral.ai/studio/search/search-toolkit). Integrate Agentic Search into your own agents, workflows, and customer deployments.
- [Libraries](https://docs.mistral.ai/studio/libraries). Use Agentic Search out-of-the-box in Studio and Vibe, without building the retrieval system yourself.

The fastest way to test Search Toolkit is with the [Search Starter App](https://github.com/mistralai/search-starter-app/tree/main). It creates a local index for your own corpus using a default configuration, so you can try Agentic Search without needing to be a search expert. When you’re ready to configure your use case, you can:

- [Set up ingestion](https://docs.mistral.ai/studio/search/search-toolkit/ingestion). Select parsers, chunking strategies, embedding models, and extractors for your data and file types.
- [Tune indexing and ranking](https://docs.mistral.ai/studio/search/search-toolkit/search-index). Manage Vespa schemas, indexing behavior, and relevance profiles.
- [Extend retrieval](https://docs.mistral.ai/studio/search/search-toolkit/retrieval). Add query rewriting, reranking, or hybrid retrieval to the search pipeline.

0%
