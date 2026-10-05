---
vendor: ai21_labs
title: Reaching SOTA RTL Parsing By Leveraging LTR Capabilities
original_title: Closing the parsing gap: reaching SOTA RTL parsing by leveraging LTR capabilities
url: https://www.ai21.com/blog/rtl-pdf-parsing
date: 2026-01-22
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: ad0559825c4d
---

## A novel method for parsing PDF documents written in right-to-left (RTL) and underrepresented languages

Current parsing strategies break down when used on languages written from right-to-left (RTL), such as Hebrew and Arabic. We introduce a novel encoding technique to translate PDF documents from RTL formats into an easy-to-parse LTR format, significantly improving the overall parsing quality of RTL documents beyond the current SOTA.

## The challenge: the parsing gap for underrepresented languages

In [RAG](https://www.ai21.com/blog/structured-rag-enterprise-accuracy/) architecture, document parsing serves as a foundational ingestion layer. If the parsing process fails to accurately capture the structural and semantic nuances of a document, it can introduce significant noise into the pipeline. This often creates a “garbage in, garbage out” challenge that is difficult to fully resolve through downstream optimization or sophisticated prompting.

As part of a systematic parser evaluation, we tested the effect of language on parsing quality using a synthetic dataset of documents containing text and tables. The results were stark: documents written in right-to-left (RTL) languages suffered a significant drop in parsing quality compared to LTR documents, and were plagued by formatting errors and flagrant hallucinations.

This wasn’t just an academic finding. We were building RAG systems that needed to support Hebrew and other RTL languages, and this parsing gap was seriously compromising our clients’ ability to work with their own data. Realizing that current parsers were inadequate for both our benchmarks and our customers’ needs, we set out to address this gap.

Parsing with GPT-4.1 resulted in numerous hallucinations in the text. For example, replacing “upper urinary tract (דרכי השתן העליונות)” with “lower urinary tract (דרכי שתן תחתונות)”.

### Diving deeper into the problem

To solve this challenge, we developed a novel technique to convert these languages into a format that English-centric parsers can understand. By bridging this gap, we unlocked the full performance of existing tools for RTL languages.

Our first step was to create a robust Hebrew dataset modeled after [OmniDocBench](https://github.com/opendatalab/OmniDocBench), a suite of metrics that is the academic and industry standard for parser evaluations. This ensured coverage of common enterprise formats such as complex tables, presentation slides, technical papers, and business reports.

We then ran this dataset through a process of automated parsing and human verification.

- **Pre-processing:** A modified [MonkeyOCR](https://github.com/Yuliang-Liu/MonkeyOCR) (a pipeline parser which uses VLM for both layout detection and OCR of the various sections) generated initial metadata for page elements, including type, reading order, and placement.
- **Annotation:** Using a custom interface in our data annotation system, we utilized the pre-parsed data to rapidly tag content, type, and reading order.

### Exploring solutions

Known strategies for parsing each have flaws. Training a new model from scratch is too data and compute-intensive; rule-based fixes can’t address erratic hallucinations and formatting bugs.

With the usual tools off the table, we had to get creative. We knew from the start that parsers excel with English and numerical data, so our strategy was to move the problem into a format the system already understood. We first tested this by representing words as numbers, but the parser either ignored the content or lost the document structure. This led us to the core of our experiment: Could we “trick” the parser into treating an RTL document as if it were written in English?

We tried several approaches to determine the optimal way to encode this “English” representation:

- **Direct translation:** We first translated the RTL text directly into English. While this provided the parser with recognizable language, the differing word lengths and directionality caused severe formatting errors. Text frequently crossed table separators and broke the document’s original layout.
- **Length-based mapping:** We then attempted to map each RTL word to an English word of an identical character count. However, because of variable character widths (e.g., “i” vs. “w”), the text still failed to align with the original document structure, leading to overlaps and layout instability.
- **Shape-based mapping (the solution):** Finally, we refined the approach by selecting English words based on their visual geometry rather than just character length. By matching the physical “shape” and bounding box of the RTL text, we successfully preserved the document’s integrity.

This shape-based encoding proved highly effective. Our experiments reveal a key insight: graphical structure—both of the text and the document—matters more for parsing quality than semantic content**.** By prioritizing the layout, we successfully leveraged high-performance English parsing for RTL languages.

## Cracking the code: using Word Shape Encoding to improve RTL parsing:

Having identified shape-based mapping as our most promising path, we implemented a solution using the following process:

- **Build a reference index:** We took a large collection of English words, rendered each word and measured it in a standard font (“Arial”) and size (“10”). This allowed us to measure the precise width and height of each word and map those dimensions into a persistent index. This indexing phase is performed offline, creating a fixed “shape-to-word” index that serves as the foundation for the encoding process.

- **Encode the RTL document: **We extract each word in the document (with the exception of English words and numbers), with its corresponding bounding box. Given the dimensions of the bounding box, we used a KNN algorithm to map each RTL word to an English word with a similar-sized rectangle, using the cosine similarity function to normalize different font sizes. The result was a one-to-one (reversible) mapping between each RTL word and an English word from the shape-to-word index.

- **Document rendering: **Once the encoding is complete, we use the results to render an English-equivalent version of the original PDF. This involves two primary actions: **text substitution** and **layout mirroring** to convert the document from RTL to LTR.

- **Text substitution:** We replace each RTL word with its English-mapped equivalent. While the typeface is standardized to Arial, we preserve the original styles, including font size, bolding, and italics.
- **Spatial mirroring:** To align with LTR reading patterns, we reverse the horizontal coordinates of all page elements.  **Images & text:** These are moved to their exact mirror positions on the page. **Vector Graphics:** These are fully mirrored to ensure visual and structural consistency.

Finally, we render the substituted and mirrored elements into a new PDF. This “English-looking” file maintains the precise graphical structure of the original while becoming fully compatible with standard English parsers.

- **Document parsing**: The processed PDF now looks like standard English, and can be handled by any LTR model without modification. To test this versatility, we ran our experiments across several different model architectures using a PDF-to-Markdown (MD) conversion as our benchmark (detailed below).
- **Decoding: **Given the markdown output and original mapping, we are then able to take each rectangle block and translate it back to the originally encoded word to reintroduce the original semantic meaning back into the text. We use Levenshtein distance to find the best matching original word, rather than exact matching. As some parsers are statistical in nature, we found they may produce slight deviations even from our encoded English word. For example, as seen in the case below:

- **Target:** The English word in our encoded document was **“paypal”**.
- **Parser error:** The model hallucinated the word as **“payplus”**.
- **Resolution:** By using a similarity search, our system identifies **“paypal”** as the intended match, which then successfully points back to the original Hebrew word: **“הבהרה”**.

## Evaluation and results

To validate the effectiveness of our approach, we benchmarked it across a diverse range of parsing solutions. It was important to ensure that our method remained robust across different architectural “types,” from multimodal models to closed-source enterprise tools.

We categorized the parsers into three distinct groups:

- **Vision-Language Models (VLMs):** These are unified models capable of processing images directly, such as **GPT-4o**, **Gemini 3.0**, and **Qwen2.5-VL**. These models represent the current state-of-the-art for visual document understanding.
- **Modular pipelines:** These parsers approach the document in discrete phases, first identifying the page structure (layout analysis) and then processing individual elements like tables or paragraphs separately. Examples include [MinerU](https://mineru.net) and [Marker](https://github.com/datalab-to/marker).
- **Black-box / SaaS commercial solutions:** These are proprietary parsers from third-party vendors where the underlying implementation is not exposed. Examples include [LLaMaParse](https://www.llamaindex.ai/llamaparse) and [Apryse](https://apryse.com).

### Evaluation framework

We measured success by comparing the performance of these models with and without our Word Shape Encoding method. Using the ground-truth dataset of manually tagged Hebrew documents, we evaluated two primary metrics:

- **Text parsing accuracy:** The ability to extract paragraph text accurately and in the correct order, measured with edit distance between the original and the parsed documents.
- **Table extraction quality:** We used Table-TEDS, which is a method that compares both the structure and the content of a table.

#### Results

The results showed a significant improvement over current SOTA across different models, especially on tables. The major exception was Gemini, which showed poor results in Hebrew parsing in general, and what can only be described as an allergic reaction to our method.

## Using Word Shape Encoding on other RTL languages

While our method consistently improved results for Hebrew, the outcomes for Arabic were more nuanced. Using [**Kitab-Bench**](https://github.com/mbzuai-oryx/KITAB-Bench) as our evaluation framework, we observed a performance split: our encoding method improved parsing quality for **GPT-4o-mini**, yet led to a decrease in quality for **GPT-4.1**.

We theorized that handling of RTL formatting is not the sole determinant of parsing quality, and that a model’s exposure to a specific language matters significantly. For a widely spoken language like Arabic, parsing quality remains high despite the complexities of the script, likely due to the vast amount of training data available.

To test this theory, we needed a quantitative metric to assess how well a model understands Arabic OCR, as expressed in lack of ״confusion״. We hypothesized that if a model is “confused,” it will return significantly different answers when presented with the same prompt multiple times. We define this as **self-consistency**: the degree of agreement between independent outputs for the same input.

To calculate this, we parsed our test sets $n$ times and calculated the average pairwise similarity between all resulting outputs. Mathematically, this is expressed as:

Self-Consistency

=

1

n

(

n

−

1

)

/

2

∑

i

=

1

n

−

1

∑

j

=

i

+

1

n

S

(

G

i

,

G

j

)

\text{Self-Consistency} = \frac{1}{n(n-1)/2} \sum_{i=1}^{n-1} \sum_{j=i+1}^n S(G_i, G_j)

Where:

- nn is the number of independent parses.

- GiG_i and GiG_i are individual generated parses.

- SS is the similarity function defined by the **OmniDocBench** metric.

Our self-consistency analysis revealed a clear pattern:

- **GPT-4.1 + Arabic:** High baseline consistency, explaining why our encoding method offered little improvement, as the model already handles Arabic OCR well.
- **GPT-4.1 + Hebrew:** Lower baseline consistency, and our method measurably reduced this confusion.
- **GPT-4o-mini + Arabic:** Behaves similarly to GPT-4.1 with Hebrew – elevated confusion that our method successfully mitigated.

In short, our approach delivers the greatest gains where the model is least confident, likely due to limited exposure to that language in training data.

### Arabic self-confidence:

### Hebrew self-confidence:

## Training our own model

Despite initial reluctance to train our own parsing model, we ended up doing exactly that. Our encoding method delivered strong RTL performance, but it came with a key limitation: dependence on PDF metadata. This meant it couldn’t handle other file formats (e.g., PowerPoint) or scanned/image-based PDFs. Visual language models (VLMs) solve this: they take images as input and don’t rely on metadata.

Beyond the technical limitations, there was also a practical reality: models are first-class citizens in most ML infrastructure. A standalone model is easier to deploy than a service wrapping our method.

Given these constraints, we trained a new model on data generated by our original approach. The result: a model that inherited the same high-quality RTL parsing, now generalized beyond PDFs.

### Building the training data

**Sampling:** We began by curating PDFs from the web, prioritizing slide decks and documents containing tables to align with our partners primary use cases. From each document, we randomly sampled a single page.

**Generating the target**: We converted each sampled page into a 120 DPI image. We then processed the original PDF page using our method to generate the corresponding Markdown output, which served as the “ground truth” target.

**Filtering**: To ensure data quality, we applied two filtering criteria:

- **Content relevance:** We filtered out pages that did not contain a significant amount of Hebrew text. Since our method relies on PDF metadata (the text layer), the presence of detectable text served as a necessary proxy for usable files.
- **Confidence check:** Using the [self confidence](https://docs.google.com/document/d/10JwLpORxwVD4RqPx9LaaOdrij1tEbk0gIQhoPsF7DhI/edit?tab=t.d4tryxbxx32p#heading=h.433d1zil1ady) metric described above, we removed any samples where the method returned a low confidence score, ensuring the model was trained only on high-certainty examples.

**Training**: We started with [DeepSeekOCR](https://github.com/deepseek-ai/DeepSeek-OCR) because it offers a great balance of size (3B parameters) and existing Hebrew capability. We then fine-tuned the model on the data generated in the previous section, using our manually curated Hebrew dataset as a test set.

**Results:** Although training is ongoing, early results are promising – we have surpassed SOTA, with our current parsing model beating GPT-5.2. As mentioned previously, using Word Shape Encoding on GPT models further improves RTL parsing.

That said, we did see a dip in quality regarding tables. After analyzing the errors, we found certain table types that the model struggles to reconstruct accurately. We believe this is due to either:

- **Insufficient data:** Our training set might not be large enough to represent these edge cases.
- **Fine-tuning depth:** The model might be particularly resistant to learning these patterns, requiring more targeted data and a deeper fine-tuning process.

## Conclusion

In this post, we introduced Word Shape Encoding, a novel approach to closing the parsing gap for underrepresented languages by leveraging the strengths of LTR parsers. We demonstrated that this method was the top performer on our Hebrew dataset and subsequently showed how it can be used to synthesize training data. This allowed us to train a standalone model that overcomes the metadata dependencies of the original method.

Our trained model shows promise, but technical challenges remain. We expect further gains from expanding the training dataset and refining our approach.

Looking forward, we see Word Shape Encoding extending to other complex parsing challenges, such as chart and graph parsing. But there’s a bigger concept here, applicable beyond parsing: identify a model’s weaknesses, then create a “reduction function” that maps those problems into its areas of strength. In our case, we transformed a Hebrew perception problem into an English reasoning problem. But we believe this strategy applies far beyond parsing, or RTL languages.
