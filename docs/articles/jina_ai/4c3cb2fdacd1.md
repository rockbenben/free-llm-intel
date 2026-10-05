---
vendor: jina_ai
title: 6 minutes readJina Code Embeddings: SOTA Code Retrieval at 0.5B and 1.5BCode generation LLMs → code embeddings: 0.5B/1.5B models achieve SOTA performance across 25 code retrieval benchmarks.
original_title: 
url: https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b
date: 2025-09-04
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
body_sha: 749bc81374c1
---

# Jina Code Embeddings：0.5B 与 1.5B 规模下的 SOTA 代码检索

从代码生成 LLM 到代码 embedding：0.5B / 1.5B 模型在 25 个代码检索基准上取得 SOTA 表现。

*jina-code-embeddings* 是一套新颖的代码 embedding 模型，用于从自然语言查询检索代码、做技术问答，并在多种编程语言间识别语义相似的代码片段。它创新地采用了在文本与代码上同时预训练的自回归骨干，通过 last-token pooling 生成向量。我们给出训练配方，并证明尽管模型相对很小，仍达到业内领先表现，验证了这条构建代码 embedding 模型的路子。

今天我们发布 `jina-code-embeddings`，一套两种尺寸（0.5B 与 1.5B 参数）的代码 embedding 模型，并同时提供两者的 [1–4 bit GGUF 量化版本](https://huggingface.co/jinaai/jina-code-embeddings-1.5b-GGUF)。它们构建在最新的代码生成 LLM 之上，体积紧凑却达到业内领先的检索性能。支持五类检索任务：`nl2code`、`code2code`、`code2nl`、`code2completions` 与 `qa`，覆盖 15+ 种编程语言，包括 Python、JavaScript、Java、C++、C#、Go、Rust、TypeScript、SQL、MATLAB、R、Swift、Kotlin、HTML/CSS、PHP、Ruby、Scala、Perl 与 Shell。

`jina-code-embeddings` 在 25 个代码检索基准上平均达到 78.41%（0.5B）与 79.04%（1.5B）。0.5B 模型虽比 `Qwen3-Embedding-0.6B` 小 20%，却高出其 5 个百分点；1.5B 变体则追平 `voyage-code-3`（79.23%）并超过 `gemini-embedding-001`（77.38%）——后两者都是架构不公开的专有模型。

| 模型 | 参数量 | Overall AVG | MTEB Code AVG |
| --- | --- | --- | --- |
| [jina-code-embeddings-1.5b](https://jina.ai/?sui&model=jina-code-embeddings-1.5b) | **1.54B** | **79.04%** | **78.94%** |
| [jina-code-embeddings-0.5b](https://jina.ai/?sui&model=jina-code-embeddings-0.5b) | **494M** | **78.41%** | **78.72%** |
| voyage-code-3 | 未知* | 79.23% | 79.84% |
| gemini-embedding-001 | 未知* | 77.38% | 76.48% |
| [jina-embeddings-v4](https://jina.ai/?sui&model=jina-embeddings-v4) | 3.8B | 74.11% | 74.87% |
| Qwen3-Embedding-0.6B | 600M | 73.49% | 74.69% |

> *架构不公开的闭源模型

这些模型支持跨 29 种自然语言与 15+ 种编程语言的跨语言检索。自然语言包括英语、中文、法语、西班牙语、葡萄牙语、德语、意大利语、俄语、日语、韩语、越南语、泰语与阿拉伯语；编程语言则涵盖 Python、JavaScript、Java、C++、C#、Go、Rust、TypeScript、SQL、MATLAB、R、Swift、Kotlin、HTML/CSS、PHP、Ruby、Scala、Perl 与 Shell。jina-code-embeddings 让你能从任意自然语言出发检索任意编程语言的代码，也能在编程语言之间做跨语言代码检索。作为专门的代码检索模型，它并未针对自然语言到自然语言的检索做优化。

两个模型都用了[五种针对不同检索场景的任务指令前缀](https://huggingface.co/jinaai/jina-code-embeddings-1.5b/blob/main/config_sentence_transformers.json)，每种都同时支持 query 与 document 角色以实现非对称检索。例如，你可以用 `nl2code_query` 对查询编码、用 `nl2code_document` 对文档编码。

| 任务 | 用例 | 指令前缀 |
| --- | --- | --- |
| `nl2code` | “如何读取 CSV” → `pandas.read_csv()` | "Find the most relevant code snippet given the following query:\n" |
| `qa` | 技术问答检索 | "Find the most relevant answer given the following question:\n" |
| `code2code` | 查找相似实现 | "Find an equivalent code snippet given the following code snippet:\n" |
| `code2nl` | 代码到文档 | "Find the most relevant comment given the following code snippet:\n" |
| `code2completion` | 自动补全场景 | "Find the most relevant completion given the following start of code snippet:\n" |

## [训练配方](https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/#training-recipe)

我们使用预训练的代码生成模型作为 embedding 骨干。基于 `Qwen2.5-Coder-0.5B` 与 `1.5B`，我们的模型特性如下：

| 特性 | [jina-code-embeddings-0.5b](https://jina.ai/?sui&model=jina-code-embeddings-0.5b) | [jina-code-embeddings-1.5b](https://jina.ai/?sui&model=jina-code-embeddings-1.5b) |
| --- | --- | --- |
| **基础模型** | Qwen2.5-Coder-0.5B | Qwen2.5-Coder-1.5B |
| **Embedding 维度** | 896 | 1536 |
| **Matryoshka 维度** | 64, 128, 256, 512, 896 | 128, 256, 512, 1024, 1536 |
| **最大序列长度** | 32,768 tokens | 32,768 tokens |
| **池化策略** | Last-token pooling | Last-token pooling |
| **注意力** | FlashAttention2 | FlashAttention2 |
| **数据类型** | BFloat16 | BFloat16 |

传统代码 embedding 模型面临一个根本瓶颈：高质量的“注释-代码”对根本不够多，无法支撑监督训练。通过以在 5.5 万亿 token、92+ 编程语言上预训练的 `Qwen2.5-Coder` 起步，我们继承了其对编程构造的深度语义理解、跨语言模式识别，以及内建的语法与惯用法知识。随后的对比微调只需极少量对齐数据就能把这份知识适配到检索任务——绕开了制约 encoder-only 模型的数据稀缺问题。

对于跨框架代码翻译这类样本不足的任务，我们用 LLM 合成了数据，且每一个合成样例都经过人工校验以保证质量。训练数据把现有的 MTEB 代码任务训练划分与改编后的公开数据集结合起来，包括 CommitPackFT、SWE-Bench、Spider、MBPP 与 CodeSearchNet。

与 [jina-embeddings-v3](https://jina.ai/?sui&model=jina-embeddings-v3) 和 `v4` 不同，我们没有用 LoRA，而是直接做完整后训练。对于我们这样的小模型（494M 与 1.54B 参数），LoRA 的参数效率吸引力下降——当容量有限时，适配器的开销反而会伤害性能。我们需要每个参数都真正用在 embedding 任务上。即便在多任务场景下，任务特定的指令前缀也比多个 LoRA 适配器更干净：与其切换权重配置，我们只是前置不同的指令——更轻量，也更契合 LLM 天然处理条件信息的方式。

训练极其高效：两个模型都用 InfoNCE 损失的对比学习训练，在 4×A100 80GB 上，0.5B 仅 8.3 小时完成，1.5B 约 12 小时。

最后，我们基准测试了不同的池化策略。Last-token pooling 达到 78.41% 的总体均值，在所有基准类别上都稳定优于 mean pooling（77.20%）与 latent attention pooling（78.27%）。这 1.2 个百分点的优势让我们打破了自己在 `jina-embeddings-v2`、`v3`、`v4` 中确立的 mean pooling 传统。随着更多检索模型构建在 decoder-only LLM 之上，last-token pooling 成为自然选择——mean pooling 与单向注意力机制本就不契合。虽然 mean pooling 也能工作、且早期训练往往更容易（可能源于其凸优化曲面），但我们的实验始终显示它会停滞在 last-token pooling 所能达到天花板的下方。

## [快速上手](https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/#getting-started)

两个模型都能无缝通过我们的 Search Foundation API 使用，也支持 `sentence-transformers`、`transformers`、`llama.cpp` 等流行框架。

### [通过 API](https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/#via-api)

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

### [通过 `sentence-transformers`](https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/#via-sentence-transformers)

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

### [通过 `transformers`](https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/#via-transformers)

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

### [Matryoshka Embedding 截断](https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/#matryoshka-embeddings-cut-off)

两个模型都用 Matryoshka 表示学习在维度 `[64, 128, 256, 512, 896]` 上训练，允许你无需重算即可截断 embedding：

```
# Full embeddings: 896d (0.5B) or 1536d (1.5B)
full_embedding = model.encode(text)

# Truncate to smaller dimensions for efficiency
small_embedding = full_embedding[:256]  # Works for both models
tiny_embedding = full_embedding[:128]   # 0.5B supports down to 64d
```

这份灵活性让你能根据自身需求在性能与效率之间权衡。

## [结论](https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/#conclusion)

`jina-code-embeddings` 表明，有效的代码 embedding *并不*需要巨大规模。通过构建在代码生成模型之上并施加针对性微调，我们用不到 1.5B 参数的模型达到了业内领先性能。

如此紧凑的模型（0.5B/1.5B）取得强劲结果，印证了我们的论点：**选对基础比参数量更重要。** 生成式模型理解代码语义——这份理解能直接迁移到表示任务上。

这也契合我们在 Jina AI 的更大愿景：统一架构，让 embedding 与 generation 从同一基础中涌现，推动 search foundation models 的边界。
