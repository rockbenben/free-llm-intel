---
vendor: aws_bedrock
title: Build a protein research copilot with Amazon Bedrock AgentCore
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-a-protein-research-copilot-with-amazon-bedrock-agentcore
date: 2026-06-23
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: ea8b8eb24aee
---

# 使用 Amazon Bedrock AgentCore 构建蛋白质研究 copilot

蛋白质研究人员面临一项耗时的挑战：在数千条肽序列中手动搜索结构相似的候选对象，不仅缓慢、容易出错，还需要深厚的领域专业知识才能解读结果。构建一个蛋白质研究 copilot 可以改变研究人员在大型数据集中搜索结构相似肽的方式——在单个对话式界面中实现自然语言查询、自动化 embedding 生成，以及由 AI 驱动的结果摘要。

本文展示如何构建一个对话式蛋白质研究助手，它结合三项能力：

- 解析自然语言查询，以抽取结构化搜索参数。
- 使用专门的语言模型，在蛋白质 embedding 上执行向量相似度搜索。
- 对搜索结果生成由 AI 驱动的科学摘要。

该系统使用 [Strands Agents SDK](https://github.com/strands-agents/sdk-python) 在一个 agent 内编排三个专用工具，部署到 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 以提供生产服务，并把肽 embedding 存储在带 pgvector 的 Amazon Aurora PostgreSQL-Compatible Edition 中。

读完全文，你将构建出一个端到端的 agent 应用，演示如何：

- 使用 Strands Agents SDK 的 tool-use 模式，把类似“Find 10 similar peptides to the dengue virus peptide LPAIVREAI”这样的自然语言用户输入解析为结构化的工具参数。
- 把自定义 ML 模型（ESM-C 300M）部署为 Amazon SageMaker AI 无服务器端点，并打包模型权重以实现快速冷启动。
- 在单个查询中把向量相似度搜索（Amazon Aurora PostgreSQL 上的 pgvector）与元数据过滤结合起来。
- 在单个 Bedrock AgentCore runtime 内编排多个专用工具——包括嵌套的 LLM agent——并生成搜索结果的科学摘要。

## 前提条件

要跟随本文操作，你需要：

- 一个可访问 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 基础模型（Anthropic Claude Sonnet 4.6）的 [AWS 账户](https://aws.amazon.com/free/)。
- Python 3.12 或更高版本。
- 已配置适当凭证的 [AWS Command Line Interface (AWS CLI)](https://aws.amazon.com/cli/)。
- Amazon Bedrock、Amazon SageMaker AI、Amazon Aurora、Amazon Elastic Container Service (Amazon ECS) 和 AWS CodeBuild 的 IAM 权限。
- 已安装 `bedrock-agentcore-starter-toolkit`（`pip install bedrock-agentcore-starter-toolkit`）。
- [IEDB](https://www.iedb.org/) 病毒表位数据集。
- 预计部署时间：30–45 分钟；请查看 Bedrock、SageMaker AI、Aurora Serverless v2 和 AWS Fargate 的 AWS 定价页面以估算成本。

## 解决方案概览

该 copilot 采用 tool-use 模式：单个 Strands agent 编排三个专用工具来处理完整的研究工作流。当研究人员提交自然语言查询时，agent 会把它解析为结构化参数，使用蛋白质 embedding 搜索相似肽，并结合科学背景对结果进行摘要。

下图展示了该架构：

![架构图：蛋白质研究 copilot，包括运行在 AWS Fargate 上的 Streamlit 前端、Amazon Bedrock AgentCore 上的 Strands agent、解析与摘要 agent、用于 ESM-C 300M embedding 的 SageMaker AI 端点，以及带 pgvector 的 Aurora PostgreSQL](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/03/ML-19630-1.jpeg)

该架构包含五个组件：

- 运行在 AWS Fargate 上的 Streamlit 前端提供对话式界面。它把查询发送到 AgentCore runtime，并以结构化格式展示结果，附带可下载的表格。
- 运行在单个 Amazon Bedrock AgentCore runtime 内的 Strands agent 负责编排工作流。该 agent 通过 Bedrock Converse API 使用 Anthropic Claude Sonnet 4.6，并可访问三个用 `@tool` 装饰器定义的工具。
- 解析工具使用专门的 Strands agent（LLM-as-parser 模式）从自然语言查询中抽取结构化搜索参数——序列、物种过滤条件、结果数量限制。
- 搜索工具通过运行 ESM-C 300M 的 Amazon SageMaker AI 无服务器端点生成蛋白质 embedding，然后针对带 pgvector 的 Amazon Aurora PostgreSQL 执行余弦相似度搜索。
- 摘要工具使用另一个专门的 Strands agent 分析搜索结果，并生成简洁的科学摘要，附带进一步研究的建议。

这种单 runtime、多工具的设计让部署保持简单，同时保持清晰的关注点分离。每个工具封装一项独特能力，编排 agent 则根据用户的查询决定何时以及如何调用它们。

## 使用 ESM-C 300M 生成蛋白质 embedding

相似度搜索的核心是 ESM-C 300M，这是 EvolutionaryScale（Built with ESM）推出的蛋白质语言模型，可生成 960 维 embedding，捕捉氨基酸序列的结构与功能特性。生物功能相似的两条肽会产生在向量空间中彼此接近的 embedding，从而无需序列比对即可进行相似度搜索。

ESM-C 300M 部署为 Amazon SageMaker AI 无服务器端点，空闲时可缩容到零，调用之间不产生费用。模型权重被打包进部署产物，以避免在推理时从 HuggingFace 下载——这对冷启动延迟至关重要的无服务器端点尤为关键。

推理处理器直接构建模型架构并加载预先打包的权重：

```
from esm.models.esmc import ESMC
from esm.tokenization import get_esmc_model_tokenizers

def model_fn(model_dir):
    weights_path = os.path.join(model_dir, "weights", "esmc_300m.pt")
    model = ESMC(
        d_model=960,
        n_heads=15,
        n_layers=30,
        tokenizer=get_esmc_model_tokenizers(),
        use_flash_attn=False,
    )
    state_dict = torch.load(weights_path, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()
    return model
```

`predict_fn` 处理器接收蛋白质序列，对其进行编码，并返回均值池化后的 embedding：

```
def predict_fn(input_data, model):
    sequence = input_data["sequence"]
    protein = ESMProtein(sequence=sequence)
    protein_tensor = model.encode(protein)
    logits_output = model.logits(
        protein_tensor, LogitsConfig(sequence=True, return_embeddings=True)
    )
    embeddings = logits_output.embeddings
    mean_embeddings = embeddings[:, 1:-1, :].mean(dim=1)
    return mean_embeddings[0].detach().cpu().tolist()
```

该端点以无服务器配置部署，内存 6144 MB，最大并发数为 5，使用 PyTorch 2.6.0 CPU 推理容器。模型打包脚本通过 `from_pretrained` 下载一次权重，保存 state dict，并把它与推理代码一起打包到 `model.tar.gz` 中，同时带有 SageMaker AI 所需的 `code/` 目录结构。

## 使用 Aurora PostgreSQL 与 pgvector 进行向量搜索

肽 embedding 存储在带 pgvector 扩展的 Amazon Aurora PostgreSQL-Compatible Edition Serverless v2 中。数据库 schema 很直接：

```
CREATE TABLE peptides (
    id SERIAL PRIMARY KEY,
    sequence TEXT NOT NULL,
    embedding vector(960),
    properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX peptides_embedding_idx
ON peptides USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

`properties` JSONB 列存储生物学元数据——物种、来源生物体、来源分子、表位位置——从而支持向量与元数据的组合过滤。例如，“Find peptides similar to LPAIVREAI from dengue virus”这样的查询会同时触发对 `embedding` 列的余弦相似度搜索和对 `properties->>'species'` 的过滤。

数据加载 pipeline 从 IEDB 病毒表位数据集读取数据，通过 SageMaker AI 端点为每条肽序列生成 embedding，并使用 Amazon RDS Data API 把它们插入数据库。初始加载会采样 1,000 条线性肽：

```
def import_peptides(df):
    for i, row in tqdm(df.iterrows(), total=len(df)):
        sequence = row["Epitope_Name"]
        embedding = get_embedding(sequence)  # SageMaker AI endpoint call
        properties = {
            "species": row["Epitope_Species"],
            "source_organism": row["Epitope_Source Organism"],
            "source_molecule": row["Epitope_Source Molecule"],
            # ... additional metadata
        }
        run_statement(
            "INSERT INTO peptides (sequence, embedding, properties) "
            "VALUES (:sequence, :embedding::vector, :properties::jsonb)",
            params=[...]
        )
```

数据库访问经由 Amazon Relational Database Service (Amazon RDS) Data API，这意味着 agent runtime 不需要与数据库直连的网络连通性——它通过 HTTPS 通信，从而简化了 AgentCore 部署的网络要求。

## 使用 Strands Agents SDK 构建 agent

[Strands Agents SDK](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-frameworks/strands-agents.html) 为构建使用工具的 agent 提供了清晰的抽象。每个工具都是带有 `@tool` 装饰器的 Python 函数，agent 会根据函数的 docstring 和类型提示，自动为 LLM 生成工具描述。

### 工具定义

解析工具委托给一个专门的 Strands agent，后者充当结构化输出抽取器：

```
from strands import Agent, tool
from strands.models import BedrockModel

parser_agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-4-6",
                       region_name="us-east-1", streaming=False),
    system_prompt="""You are a peptide query parser. Extract structured search
    parameters from natural language queries. Return ONLY a valid JSON object."""
)

@tool
def parse_peptide_query(query: str) -> str:
    """Parse a natural language peptide query into structured search parameters.

    Args:
        query: The user's natural language query about peptides.

    Returns:
        JSON string with extracted parameters like sequence, species, limit.
    """
    result = parser_agent(f"Parse this query: {query}")
    parsed = json.loads(str(result))
    return json.dumps(parsed)
```

搜索工具把 SageMaker AI 的 embedding 生成与 pgvector 相似度搜索结合起来：

```
@tool
def search_similar_peptides(sequence: str, species: str = "", limit: int = 20) -> str:
    """Search for peptides similar to the given sequence using ESM embeddings.

    Args:
        sequence: The peptide amino acid sequence (e.g., "LPAIVREAI").
        species: Optional species filter (e.g., "Dengue virus").
        limit: Maximum number of results to return.

    Returns:
        JSON string with list of similar peptides and their properties.
    """
    # Get embedding from SageMaker AI
    resp = sagemaker_client.invoke_endpoint(
        EndpointName=endpoint, ContentType="application/json",
        Body=json.dumps({"sequence": sequence}))
    embedding = json.loads(resp["Body"].read().decode())["embedding"]

    # Vector similarity search with optional metadata filter
    sql = "SELECT sequence, properties, "
    sql += "(embedding <=> :query_embedding::vector) AS cosine_distance "
    sql += "FROM peptides"
    if species:
        sql += " WHERE properties->>'species' = :species"
    sql += " ORDER BY cosine_distance LIMIT :limit"

    results = run_sql(sql, params)
    return json.dumps({"results": peptides, "count": len(peptides)})
```

摘要工具使用另一个专门的 Strands agent 进行科学分析：

```
summarizer_agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-4-6",
                       region_name="us-east-1", streaming=False),
    system_prompt="""You are a peptide research expert providing concise,
    high-level summaries. Analyze search results and provide a brief,
    insightful summary focusing on key findings and ideas for further
    investigation."""
)

@tool
def summarize_results(original_query: str, search_results_json: str) -> str:
    """Summarize peptide search results with scientific insights.

    Args:
        original_query: The original user query.
        search_results_json: JSON string of search results.

    Returns:
        A concise scientific summary of the search results.
    """
    results = json.loads(search_results_json)
    summary = summarizer_agent(f"Original query: {original_query}"
                               f"Results: {results}")
    return str(summary)
```

### 编排 agent

编排 agent 把一切串联起来。它接收用户的查询，并决定调用哪些工具以及以什么顺序调用：

```
SYSTEM_PROMPT = """You are a peptide research assistant. You have three tools:
1. parse_peptide_query - Parse a natural language query into structured parameters
2. search_similar_peptides - Search for similar peptides using ESM embeddings
3. summarize_results - Summarize search results with scientific insights

For every user query, follow this workflow:
1. First, use parse_peptide_query to extract the sequence and parameters
2. Then, use search_similar_peptides with the extracted sequence
3. Finally, use summarize_results to provide insights

Always complete the three steps."""

strands_agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-4-6",
                       region_name="us-east-1", streaming=False),
    tools=[parse_peptide_query, search_similar_peptides, summarize_results],
    system_prompt=SYSTEM_PROMPT
)
```

这种设计采用“agents-as-tools”模式：解析器和摘要器本身就是 Strands agent，但它们被包裹在 `@tool` 装饰器中，并作为可调用工具暴露给编排器。编排器并不知道也不关心这些工具内部是否使用 LLM——它只把它们当函数调用。这样既保持了编排逻辑的清晰，又让每个工具都能在需要时利用 LLM 能力。

## 部署到 Amazon Bedrock AgentCore

[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 提供用于托管 AI agent 的托管 runtime。agent 代码在由 AWS CodeBuild 构建和部署的容器化环境中运行——无需在本地安装 Docker。

### Agent 入口点

AgentCore runtime 需要一个接收 payload 和 context 的入口函数：

```
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload, context):
    query = payload.get("query") or payload.get("prompt")
    result = strands_agent(query)
    return {
        "status": "success",
        "original_query": query,
        "parsed_query": _tool_outputs.get("parsed_query", {}),
        "search_results": _tool_outputs.get("search_results", []),
        "summary": _tool_outputs.get("summary", str(result)),
        "session_id": context.session_id
    }

if __name__ == '__main__':
    app.run()
```

该入口点把工具输出捕获到一个共享字典中，因此响应会包含结构化数据（解析后的查询、搜索结果表、摘要文本），而不只是 agent 最终的文本输出。Streamlit 前端正是使用这种结构化响应来渲染表格和可展开的区块。

### 基础设施即代码

部署使用 AWS CloudFormation 管理所有基础设施。VPC 堆栈创建带 NAT 网关的私有子网，以及用于 Amazon Bedrock、Amazon RDS Data API 和 AWS Secrets Manager 的 VPC 端点——帮助确保 agent runtime 无需经过公共互联网即可访问所有必需的服务。

需要 Amazon Aurora PostgreSQL-Compatible Edition Serverless v2 数据库，支持从 0.5 到 4 ACU（1–8 GB RAM）的自动扩缩容。一个由 AWS Lambda 支持的自定义资源会在堆栈创建期间初始化 pgvector 扩展并创建 peptides 表：

```
DBCluster:
  Type: AWS::RDS::DBCluster
  Properties:
    Engine: aurora-postgresql
    EnableHttpEndpoint: true  # Amazon RDS Data API
    ServerlessV2ScalingConfiguration:
      MinCapacity: 0.5
      MaxCapacity: 4
```

### 部署解决方案

该解决方案需要以下组件，并按顺序部署：

> 警告：请按顺序完成部署步骤。跳过步骤可能导致部署失败。

- **VPC 与网络**——带 NAT 网关的私有子网，以及用于 Amazon Bedrock、Amazon RDS Data API 和 AWS Secrets Manager 的 VPC 端点，使 agent runtime 无需经过公共互联网即可访问所有必需的服务。
- **Aurora PostgreSQL 数据库**——一个启用了 pgvector 扩展的 Amazon Aurora PostgreSQL-Compatible Edition Serverless v2 集群，peptides 表通过由 Lambda 支持的 AWS CloudFormation 自定义资源初始化。
- **SageMaker AI 端点**——运行 ESM-C 300M 的无服务器端点，内存 6144 MB，最大并发数为 5，使用 PyTorch 2.6.0 CPU 推理容器。
- **肽数据**——通过 SageMaker AI 端点为每条序列生成 embedding，并使用 Amazon RDS Data API 插入，从而把 IEDB 病毒表位数据集加载到数据库中。
- **AgentCore runtime 与 Streamlit UI**——Strands agent 通过 AWS CodeBuild 部署到 Amazon Bedrock AgentCore runtime（无需本地 Docker），Streamlit 前端则部署到 AWS Fargate。

## Streamlit 前端

前端是一个轻量级 Streamlit 应用，通过 `bedrock-agentcore` boto3 客户端与 AgentCore runtime 通信。它运行在 AWS Fargate 上，使用仅包含 `streamlit`、`pandas` 和 `boto3` 的最小容器镜像——不包含任何 ML 库。

```
client = boto3.client('bedrock-agentcore', region_name='us-east-1')

response = client.invoke_agent_runtime(
    agentRuntimeArn=HOST_RUNTIME_ARN,
    runtimeSessionId=session_id,
    payload=json.dumps({"prompt": query}).encode()
)
```

该 UI 分三个区块展示结果：解析后的查询参数（可展开）、带余弦距离和元数据的可排序相似肽表格，以及由 AI 生成的科学摘要。用户可以把结果下载为 CSV 以便进一步分析。

以下截图展示了搜索查询及其结果。

![Streamlit 前端展示肽相似度搜索查询，以及带余弦距离和元数据的结果表格](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/03/ML-19630-2.jpeg)

## 注意事项

在将此解决方案部署到生产环境之前，请留意以下设计与运维上的权衡：

**冷启动延迟。** 在空闲期之后，SageMaker AI 无服务器端点的首次调用需要 2–3 分钟，因为容器要初始化并加载模型权重。在保活窗口内的后续调用会在几秒内完成。对于延迟敏感的工作负载，可考虑使用预置端点，或在无服务器配置上设置更高的预置并发。

**Embedding 模型选择。** 我们选择 ESM-C 300M，是看重它在 embedding 质量与 CPU 推理速度之间的平衡。若要在结构相似性任务上获得更高准确率，ESM-C 600M 或 ESM2 模型可提供更大的 embedding 维度，但代价是更高的内存占用和延迟。在测试中，ESM-C 300M 生成的 960 维 embedding 在肽相似度搜索上表现出色。

**扩展数据集。** 初始加载使用从 IEDB 数据集中采样的 1,000 条肽。若要在生产环境使用更大的数据集，可考虑批量加载 embedding、按比例增大 IVFFlat 索引的 lists 参数，并相应扩展 Aurora 的 ACU。Amazon RDS Data API 有 1 MB 的响应大小限制，因此返回大结果集的查询可能需要分页。

**成本。** 无服务器组件（SageMaker AI 无服务器端点、Aurora Serverless v2、AgentCore runtime）在空闲时会缩容到接近零，因此该架构对于使用模式间歇的研究型工作负载颇具成本效益。活跃使用期间的主要持续成本是 Bedrock LLM 推理（每次查询三次调用：解析器、编排器、摘要器）和 SageMaker AI 端点调用。

## 清理资源

为避免持续产生费用，请按以下顺序删除资源：

> 警告：请按相反顺序删除资源，以避免依赖错误。

- **Streamlit UI**——通过 AWS CloudFormation 控制台或 AWS CLI 删除 AWS Fargate 堆栈。
- **SageMaker AI 端点**——通过 Amazon SageMaker AI 控制台或 AWS CLI 删除端点、端点配置和模型。
- **数据库**——先删除 IEDB 数据集，再通过 AWS CloudFormation 控制台删除 Aurora PostgreSQL 数据库堆栈。
- **VPC**——通过 AWS CloudFormation 控制台删除 VPC 堆栈。
- **AgentCore runtime**——通过 Amazon Bedrock AgentCore 控制台删除 runtime。

## 结论

本文展示了如何构建一个蛋白质研究 copilot，在单个对话式界面中把蛋白质语言模型 embedding 与由 LLM 驱动的分析结合起来。

传统上，研究人员需要手动查询序列数据库、运行比对工具，并在多个应用之间解读结果——每次搜索可能耗时数小时——而现在，这一过程被简化为一条自然语言查询，不到一分钟（冷启动时为 2–3 分钟）即可返回排序并汇总过的结果。把解析、基于 embedding 的搜索和科学摘要整合到一个对话式工作流中，可以显著加速肽研究和候选筛选的早期阶段。

Strands Agents SDK 的 tool-use 模式提供了一种清晰的方式，把解析、搜索、摘要等专用能力组合成连贯的工作流，而 Amazon Bedrock AgentCore 则负责托管和扩展 agent 的运维复杂性。

同一架构可以推广到肽研究之外的领域。研究人员需要搜索专用 embedding、按结构化元数据过滤并综合结果的领域——基因组学、药物设计、材料科学——都能受益于这种把领域特定 embedding 模型与 LLM 编排相结合的模式。让它切实可行的关键设计决策包括：打包模型权重以避免冷启动下载、使用 Amazon RDS Data API 简化网络配置，以及用基础设施即代码实现部署自动化。

下一步，可考虑探索更大的 ESM 模型以获得更高的 embedding 准确率、增加批量查询支持，或扩展元数据 schema 以纳入 IEDB 数据集中更多的生物学注释。

### 参考文献

Vita R、Blazeska N、Marrama D 等作者。该文题为“免疫表位数据库（IEDB）：2024 年更新”，发表于《核酸研究》（Nucleic Acids Res.）2025 年 1 月 6 日，第 53 卷第 D1 期，D436–D443 页。doi: 10.1093/nar/gkae1092。PMID：[39558162](https://www.ncbi.nlm.nih.gov/pubmed/39558162)，PMCID：[PMC11701597](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11701597/)。

ESM Team。“ESM Cambrian：用无监督学习揭示蛋白质的奥秘。”EvolutionaryScale，2024。[https://evolutionaryscale.ai/blog/esm-cambrian](https://evolutionaryscale.ai/blog/esm-cambrian)

## 关于作者
