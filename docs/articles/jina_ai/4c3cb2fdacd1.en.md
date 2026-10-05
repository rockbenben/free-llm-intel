---
vendor: jina_ai
title: Jina Code Embeddings: SOTA Code Retrieval at 0.5B and 1.5B
original_title: 
url: https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b
date: 2025-09-04
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 4941c50ad962
---

star

Featured

Press release

September 04, 2025

# Jina Code Embeddings: SOTA Code Retrieval at 0.5B and 1.5B

Code generation LLMs → code embeddings: 0.5B/1.5B models achieve SOTA performance across 25 code retrieval benchmarks.

Jina AI • 6 minutes read

Efficient Code Embeddings from Code Generation Models

jina-code-embeddings is a novel code embedding model suite designed to retrieve code from natural language queries, perform technical question-answering, and identify semantically similar code snippets across programming languages. It makes innovative use of an autoregressive backbone pre-trained on both text and code, generating embeddings via last-token pooling. We outline the training recipe and demonstrate state-of-the-art performance despite the relatively small size of the models, validating this approach to code embedding model construction.

arXiv.org

Daria Kryvosheieva

jina-code-embeddings-1.5b - Search Foundation Models

Efficient code embeddings from code generation models

Search Foundation Models

Jina AI

jinaai/jina-code-embeddings-1.5b · Hugging Face

We’re on a journey to advance and democratize artificial intelligence through open source and open science.

Today we're releasing `jina-code-embeddings`, a new suite of code embedding models in two sizes—0.5B and 1.5B parameters—along with [1-4 bit GGUF quantizations](https://huggingface.co/jinaai/jina-code-embeddings-1.5b-GGUF) for both. Built on the latest code generation LLMs, these models achieve state-of-the-art retrieval performance despite their compact size. They support five retrieval tasks including `nl2code`, `code2code`, `code2nl`, `code2completions`, and `qa` across 15 programming languages including Python, JavaScript, Java, C++, C#, Go, Rust, TypeScript, SQL, MATLAB, R, Swift, Kotlin, HTML/CSS, PHP, Ruby, Scala, Perl, and Shell.

`jina-code-embeddings` achieves 78.41% (0.5B) and 79.04% (1.5B) average performance across 25 code retrieval benchmarks. The 0.5B model outperforms `Qwen3-Embedding-0.6B` by 5 percentage points despite being 20% smaller, while the 1.5B variant matches `voyage-code-3` (79.23%) and exceeds `gemini-embedding-001` (77.38%)—both proprietary models with undisclosed architectures.

| Model | Parameters | Overall AVG | MTEB Code AVG |
| --- | --- | --- | --- |
| [jina-code-embeddings-1.5b](https://jina.ai/?sui&model=jina-code-embeddings-1.5b) | **1.54B** | **79.04%** | **78.94%** |
| [jina-code-embeddings-0.5b](https://jina.ai/?sui&model=jina-code-embeddings-0.5b) | **494M** | **78.41%** | **78.72%** |
| voyage-code-3 | Unknown* | 79.23% | 79.84% |
| gemini-embedding-001 | Unknown* | 77.38% | 76.48% |
| [jina-embeddings-v4](https://jina.ai/?sui&model=jina-embeddings-v4) | 3.8B | 74.11% | 74.87% |
| Qwen3-Embedding-0.6B | 600M | 73.49% | 74.69% |

> *Closed-source models with undisclosed architecture

The models support cross-lingual retrieval across 29 natural languages and over 15 programming languages. Natural languages include English, Chinese, French, Spanish, Portuguese, German, Italian, Russian, Japanese, Korean, Vietnamese, Thai, and Arabic, while programming languages span Python, JavaScript, Java, C++, C#, Go, Rust, TypeScript, SQL, MATLAB, R, Swift, Kotlin, HTML/CSS, PHP, Ruby, Scala, Perl, and Shell. jina-code-embeddings enables searching from any natural language to find code in any programming language, as well as cross-language code search between programming languages. As a specialized code retrieval model, it's not optimized for natural language to natural language search.

Both models were trained with [five task-specific instruction prefixes for different retrieval scenarios](https://huggingface.co/jinaai/jina-code-embeddings-1.5b/blob/main/config_sentence_transformers.json), each supporting both query and document roles for asymmetric retrieval. For example, you can use `nl2code_query` to embed queries and `nl2code_document` to embed documents.

| Task | Use Case | Instruction Prefix |
| --- | --- | --- |
| `nl2code` | "How to read CSV" → `pandas.read_csv()` | "Find the most relevant code snippet given the following query:\n" |
| `qa` | Technical Q&A retrieval | "Find the most relevant answer given the following question:\n" |
| `code2code` | Finding similar implementations | "Find an equivalent code snippet given the following code snippet:\n" |
| `code2nl` | Code to documentation | "Find the most relevant comment given the following code snippet:\n" |
| `code2completion` | Autocomplete scenarios | "Find the most relevant completion given the following start of code snippet:\n" |

## [*tag*](https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/#training-recipe)Training Recipe

We use pre-trained code generation models as embedding backbones. Built on `Qwen2.5-Coder-0.5B` and `1.5B`, our models feature:

| Feature | [jina-code-embeddings-0.5b](https://jina.ai/?sui&model=jina-code-embeddings-0.5b) | [jina-code-embeddings-1.5b](https://jina.ai/?sui&model=jina-code-embeddings-1.5b) |
| --- | --- | --- |
| **Base Model** | Qwen2.5-Coder-0.5B | Qwen2.5-Coder-1.5B |
| **Embedding Dimensions** | 896 | 1536 |
| **Matryoshka Dimensions** | 64, 128, 256, 512, 896 | 128, 256, 512, 1024, 1536 |
| **Max Sequence Length** | 32,768 tokens | 32,768 tokens |
| **Pooling Strategy** | Last-token pooling | Last-token pooling |
| **Attention** | FlashAttention2 | FlashAttention2 |
| **Data Type** | BFloat16 | BFloat16 |

Traditional code embedding models face a fundamental bottleneck: there simply aren't enough high-quality comment-code pairs for supervised training. By starting with `Qwen2.5-Coder` pre-trained on 5.5 trillion tokens spanning 92+ programming languages, we inherit deep semantic understanding of programming constructs, cross-language pattern recognition, and built-in knowledge of syntax and idioms. The contrastive fine-tuning then adapts this knowledge for retrieval tasks with minimal aligned data—sidestepping the data scarcity that constrains encoder-only models.

For underrepresented tasks like cross-framework code translations, we generated synthetic data using LLMs, with every synthetic example manually validated for quality. Our training data combined existing MTEB code task training splits with adapted public datasets including CommitPackFT, SWE-Bench, Spider, MBPP, and CodeSearchNet.

Unlike [jina-embeddings-v3](https://jina.ai/?sui&model=jina-embeddings-v3) and `v4`, we didn't use LoRA and went straight to full post-training. For small models like ours (494M and 1.54B parameters), LoRA's parameter efficiency becomes less compelling—the adapter overhead can actually hurt performance when you have limited capacity. We needed every parameter working on the embedding task. Even for multi-task scenarios, task-specific instruction prefixes proved cleaner than multiple LoRA adapters. Instead of switching weight configurations, we simply prepend different instructions—much leaner and more aligned with how LLMs naturally process conditional information.

Training was remarkably efficient: both models were trained using contrastive learning with InfoNCE loss on 4x A100 80GB GPUs, completing in just 8.3 hours for the 0.5B model and 12 hours for the 1.5B variant.

Finally, we benchmarked different pooling strategies. Last-token pooling achieved 78.41% overall average, consistently outperforming mean pooling (77.20%) and latent attention pooling (78.27%) across all benchmark categories. This 1.2 percentage point advantage led us to break from the mean pooling tradition we established in `jina-embeddings-v2`, `v3`, and `v4`. As more retrieval models build on decoder-only LLMs, last-token pooling becomes the natural choice—mean pooling simply doesn't align well with unidirectional attention mechanisms. While mean pooling can work and often trains more easily in early steps (likely due to its convex optimization landscape), our experiments consistently show it plateaus below the performance ceiling that last-token pooling achieves.

## [*tag*](https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/#getting-started)Getting Started

Both models work seamlessly via our Search Foundation API and with popular frameworks including `sentence-transformers`, `transformers` and `llama.cpp`

### [*tag*](https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/#via-api)Via API

```
curl http://api.jina.ai/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JINA_API_KEY" \
  -d @- <<EOFEOF
  {
    "model": "jina-code-embeddings-1.5b",
    "input": ["print hello world in python"],
    "task": "nl2code.passage"
  }
EOFEOF
```

### [*tag*](https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/#via-sentence-transformers)Via `sentence-transformers`

```
from sentence_transformers import SentenceTransformer

# Load the model (choose 0.5b or 1.5b)
model = SentenceTransformer(
    "jinaai/jina-code-embeddings-1.5b",
    model_kwargs={"torch_dtype": "bfloat16"},
    tokenizer_kwargs={"padding_side": "left"}
)

# Natural language to code
queries = ["print hello world in python", "initialize array of 5 zeros in c++"]
documents = ["print('Hello World!')", "int arr[5] = {0, 0, 0, 0, 0};"]

# Generate embeddings with task-specific prefixes
query_embeddings = model.encode(queries, prompt_name="nl2code_query")
document_embeddings = model.encode(documents, prompt_name="nl2code_document")

# Compute similarity
similarity = model.similarity(query_embeddings, document_embeddings)
```

### [*tag*](https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/#via-transformers)Via `transformers`

```
from transformers import AutoModel, AutoTokenizer
import torch.nn.functional as F

def last_token_pool(last_hidden_states, attention_mask):
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[torch.arange(batch_size), sequence_lengths]

tokenizer = AutoTokenizer.from_pretrained('jinaai/jina-code-embeddings-1.5b')
model = AutoModel.from_pretrained('jinaai/jina-code-embeddings-1.5b')

# Apply task-specific prefix
query = "Find the most relevant code snippet given the following query:\nprint hello world"
code = "Candidate code snippet:\nprint('Hello World!')"

# Tokenize and embed
batch_dict = tokenizer([query, code], padding=True, truncation=True, return_tensors="pt")
outputs = model(**batch_dict)
embeddings = last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
```

### [*tag*](https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/#matryoshka-embeddings-cut-off)Matryoshka Embeddings Cut-Off

Both models was trained with Matryoshka representation learning for dimensions `[64, 128, 256, 512, 896]`, allowing you to truncate embeddings without recomputing:

```
# Full embeddings: 896d (0.5B) or 1536d (1.5B)
full_embedding = model.encode(text)

# Truncate to smaller dimensions for efficiency
small_embedding = full_embedding[:256]  # Works for both models
tiny_embedding = full_embedding[:128]   # 0.5B supports down to 64d
```

This flexibility enables trading off between performance and efficiency based on your requirements.

## [*tag*](https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/#conclusion)Conclusion

`jina-code-embeddings` demonstrates that effective code embeddings *don't* require massive scale. By building on code generation models and applying targeted fine-tuning, we achieve state-of-the-art performance with models under 1.5B parameters.

The strong results from such compact models (0.5B/1.5B) validate our thesis: **the right foundation matters more than parameter count.** Generation models understand code semantics—that understanding transfers directly to representation tasks.

This aligns with our broader vision at Jina AI: unified architectures where embedding and generation emerge from the same foundation, pushing the boundaries of what's possible with search foundation models.

Categories:

star

Featured

Press release

rss_feed

Read more

September 14, 2026 • 9 minutes read

jina-ocr-v1: Faster Document Parsing on Low-Budget GPUs

August 03, 2026 • 11 minutes read

jina-reranker-v3.5: Faster Listwise Reranking with Hybrid Attention and Self-Distillation

May 12, 2026 • 7 minutes read

jina-embeddings-v5-omni: Embeddings for Text, Image, Audio and Video
