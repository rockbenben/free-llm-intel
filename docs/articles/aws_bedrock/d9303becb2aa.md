---
vendor: aws_bedrock
title: 在 Amazon Bedrock 上推出 GLM 5.3
original_title:  Introducing GLM 5.3 on Amazon Bedrock
url:  https://aws.amazon.com/blogs/machine-learning/introducing-glm-5-3-on-amazon-bedrock
date: 2026-10-05
lang: zh
captured: 2026-10-06
extractor: readability-v1
translator: agent
status: translated
---

编码与智能体（agentic）工作负载对 AI 模型的要求前所未有：重构一个横跨数百个文件的代码仓库、在不丢失上下文的情况下维持一个持续数小时的智能体工作流，以及在每一步都借助工具调用来推理复杂的系统问题。而要用开放权重（open-weight）模型满足这些需求，历来意味着自行预置并运维你自己的推理基础设施。

来自 Z.ai（智谱 AI）的 [GLM 5.3](https://z.ai/blog/glm-5.3) 现已登陆 [Amazon Bedrock](https://aws.amazon.com/bedrock/)。按 [Hugging Face Hub](https://huggingface.co/zai-org/GLM-5.3) 上发布的版本，GLM 5.3 是一个 7530 亿（753B）参数的混合专家（mixture-of-experts）模型，专为编码和长时程（long-horizon）智能体任务优化。尤其值得一提的是，Z.ai 报告称该模型展现出值得关注的网络安全能力。在 Amazon Bedrock 上，你现在可以通过全托管 API 使用它，并享有跨区域（cross-Region）推理、prompt 缓存和服务层级（service tiers）。你无需管理任何基础设施。Bedrock 上的 GLM 5.3 面向符合条件的企业客户开放。

在这篇文章中，我们将展示如何使用兼容 OpenAI 的 API 在 Amazon Bedrock 上调用 GLM 5.3，并借助 prompt 缓存降低成本和延迟。随后我们会把这个模型投入一个真实场景的智能体工作流：用 Strix（一个开源 AI 渗透测试智能体）对你自己的应用执行一次获得授权的安全测试。

## 与 GLM 5 相比有哪些新变化

GLM 5 于今年早些时候登陆 Amazon Bedrock。GLM 5.3 延续了同一谱系，并带来了一系列重要的提升：

- **更强的编码能力：** [Z.ai 声称](https://z.ai/blog/glm-5.3)该模型在 DeepSWE、Terminal Bench 3.0 和 FrontierSWE 等一系列编码基准上表现具有竞争力。其内部编码基准相比 GLM 5.2 也有 50% 的提升。之所以没有报告与 GLM 5 的直接对比，是因为自 [GLM 5.1 发布](https://z.ai/blog/glm-5.1)以来，提升幅度之大促使基准测试本身也做了更新。
- **涌现出的网络安全能力：** 其在安全任务基准上的报告性能尤为突出，这使该模型天然适合防御性安全工作流。例如，Z.ai 在发布时于 CyberGym 基准上[测得 84.5 的领先分数](https://z.ai/blog/glm-5.3)。
- **更广泛的 Amazon Bedrock 集成：** 跨区域推理配置（profile）、隐式与显式 prompt 缓存，以及与 Invoke 和 Converse 并行、功能对齐度更高的兼容 OpenAI 的 Responses 与 Chat Completions API。

## 关键能力

- **前沿的编码与智能体性能。** GLM 5.3 专为复杂系统工程和长时程智能体任务而设计，涵盖多步推理、工具增强（tool-augmented）工作流，以及在大型代码库上持续维持上下文。
- **灵活的 API 访问。** 你可以通过兼容 OpenAI 的 Responses 与 Chat Completions API，或 Amazon Bedrock 的 Invoke 与 Converse API 来调用 GLM 5.3。
- **Prompt 缓存。** GLM 5.3 默认支持隐式（自动）prompt 缓存，并在 Responses 和 Chat Completions API 上支持显式缓存控制（推荐）。对于那些每一轮都重发大型 system prompt 或仓库上下文的智能体工作负载，缓存能同时降低延迟和输入成本。
- **跨区域推理。** GLM 5.3 可通过美国跨区域推理（`us.zai.glm-5.3`）和全球跨区域推理（`global.zai.glm-5.3`）配置使用。你把请求发送到你选定的"源"AWS 区域，Amazon Bedrock 会安全地路由每一个请求进行处理。更多细节参见 [Amazon Bedrock 用户指南](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html)。
- **服务层级。** 选择 Flex 以在对时效要求不那么高的工作负载上优化成本；选择 Priority 以更高的价格换取对延迟敏感的请求的优先处理；选择 Standard 以获得价格与速度之间的默认平衡。

## 前置条件

要运行下面的使用示例，你需要：

- 一个可访问 Amazon Bedrock 的 AWS 账户。
- 调用基础模型及目标推理配置所需的 AWS Identity and Access Management (IAM) [权限](https://docs.aws.amazon.com/service-authorization/latest/reference/list_bedrock.html)：`bedrock:InvokeModel`、`bedrock:InvokeModelWithResponseStream` 和 `bedrock:CallWithBearerToken`。
- （对于基于代码的演示）Python 3.10 或更高版本。
- （仅对于可选的安全测试演示）安装 Docker，以及带 bedrock 附加依赖的 [Strix](https://docs.strix.ai/llm-providers/bedrock)。

## 在 Amazon Bedrock 控制台体验 GLM 5.3

你可以在 AWS Management Console 上直接向 GLM 5.3 发送 prompt，无需编写代码或安装开发工具。要开始，请前往 [Amazon Bedrock](https://console.aws.amazon.com/bedrock/)，然后从左侧边栏菜单选择 **Test > Playground**。

在这个 playground 界面中，你可以从模型列表中选择 GLM 5.3，并通过聊天 UI 发送你的第一批 prompt，如下图所示：

图 1：在 Amazon Bedrock 控制台上与 GLM 5.3 对话

## 开始使用 Responses API

在编程调用层面，你可以通过 `bedrock-runtime` endpoint 调用该模型。对于 GLM 5.3，它同时支持兼容 OpenAI 的 [Responses](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-responses-api.html) 和 [Chat Completions](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-chat-completions.html) API，以及 Amazon Bedrock 的 [Invoke](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-api.html) 和 [Converse](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html) API。对于新应用，推荐使用兼容 OpenAI 的 API，因为它们支持更完整的功能集。

Amazon Bedrock 确实支持为需要 API key 的兼容 OpenAI 集成[生成 API key](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys-generate.html)。不过，我们强烈建议：在可能的情况下，优先使用短期凭证而非长期 API key。

在下面的示例中，我们将使用 OpenAI Python SDK 从 Python 调用 Responses API，并用 [aws-bedrock-token-generator](https://pypi.org/project/aws-bedrock-token-generator/) 库从你标准的 [AWS Command Line Interface (AWS CLI) 凭证](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-authentication.html)生成短期 token。

- 安装所需的包。  `pip install -U openai aws-bedrock-token-generator`
- 将以下代码保存为 `bedrock-request.py`。  `from aws_bedrock_token_generator import provide_token from openai import OpenAI region = "us-west-2" # Your source AWS Region client = OpenAI( api_key=provide_token(region=region), base_url=f"https://bedrock-runtime.{region}.amazonaws.com/openai/v1", ) resp = client.responses.create( input="Refactor this Python function to be iterative instead of recursive: ...", model="global.zai.glm-5.3", ) print(resp.output_text)`
- 运行脚本，它会显示模型的输出。  `python bedrock-request.py`

### 通过显式 prompt 缓存优化推理

长时间的编码与知识类工作流常常在多个对话轮次之间重复发送稳定的上下文，例如 system prompt、工具定义或仓库文件。

Amazon Bedrock 上的 GLM 5.3 默认支持隐式 prompt 缓存，这有助于降低那些共享同一初始 prompt 前缀的重复调用的响应延迟和输入 token 成本。

通过[显式 prompt 缓存](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)模式，你可以专门指明可复用的 prompt 前缀，相比隐式缓存能够进一步提升缓存命中率（从而进一步提升延迟和成本的节省）。

要为 GLM 5.3 使用显式 prompt 缓存，如下例所示：

- 通过请求上的 `prompt_cache_options` 选择显式缓存模式。
- 在输入内容块上添加一个或多个 `prompt_cache_breakpoint` 标记，用以标明可复用 prompt 前缀的结束位置（含该位置）。每个断点必须至少包含 1,024 个 token 才符合缓存条件。

```
resp = client.responses.create(
    model="global.zai.glm-5.3",
    # Enable explicit caching mode:
    extra_body={"prompt_cache_options": {"mode": "explicit"}},
    input=[
        {
            "type": "message",
            "role": "system",
            "content": [
                {
                    "type": "input_text",
                    "text": SYSTEM_PROMPT,
                    # A long, static system prompt is a great target for caching:
                    "prompt_cache_breakpoint": {"mode": "explicit"},
                },
            ]
        },
        {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": USER_INPUT,
                    # Multiple breakpoints can also be defined, for layered cache:
                    "prompt_cache_breakpoint": {"mode": "explicit"},
                },
            ],
        },
    ],
)

if resp.usage.input_tokens_details.cached_tokens:
    print("Hit cache!")
```

更多信息参见 Amazon Bedrock 用户指南的 [prompt 缓存章节](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html#prompt-caching-openai)。

## 示例智能体工作负载：用 Strix 执行授权安全测试

能直接从 GLM 5.3 的优势中受益的工作负载之一，就是对你自己应用的自动化安全测试。[Strix](https://github.com/usestrix/strix) 是一个开源 AI 渗透测试智能体，它会动态运行你的代码、找出漏洞，并通过概念验证（proof-of-concept）测试加以验证。截至本文撰写之时，Strix 文档[将 GLM 5.3](https://docs.strix.ai/quickstart#configuration) 作为其默认模型。你可以配置 Strix 使用 Amazon Bedrock 上的 GLM 5.3，而不是第三方推理服务方，从而让模型推理在你 AWS 账户的管控之下运行。

**只测试你拥有或已获得明确书面许可可测试的应用。** 对你不拥有的系统进行未经授权的安全测试，在大多数司法辖区均属违法，并违反 AWS 可接受使用政策（AWS Acceptable Use Policy）。在本演练中，目标是 [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/)——一个在你本机本地运行的、刻意留有漏洞的示例应用。

如果你想在自行运行开源智能体之外，获得全托管的、持续的安全测试，[AWS Continuum](https://aws.amazon.com/security-agent/) 会以托管服务的形式提供按需渗透测试及其他安全分析。这两种方式是互补的：像 Strix 这样的开源智能体为你提供由开发者主导、人在回路（in-the-loop）且深度可定制的、针对本地构建的测试；而 AWS Continuum 则大规模地运行托管评估。

### 执行一次获得授权的安全测试

- 在本地启动示例 Juice Shop 目标应用。  `docker run --rm -p 3000:3000 bkimminich/juice-shop`
- 配置 Strix 以使用 Amazon Bedrock 上的 GLM 5.3。Strix 底层使用 [LiteLLM](https://docs.litellm.ai/docs/providers/bedrock)，因此（如[其 Amazon Bedrock 文档](https://docs.strix.ai/llm-providers/bedrock)所述）你的 AWS CLI 凭证会被自动获取。这意味着无需 API key，但你可能需要设置诸如 `AWS_PROFILE` 和 `AWS_REGION` 的环境变量来配置你的连接。截至撰写之时，LiteLLM 尚不能解析 `bedrock/global.zai.glm-5.3`。在此问题解决之前，你可以显式指定 Converse API 路由和推理配置的 Amazon Resource Name (ARN)，如下面的片段所示：  `# Fill in the REGION and ACCOUNT_ID placeholders below before running! export STRIX_LLM="bedrock/converse/arn:aws:bedrock:{AWS_REGION}:{AWS_ACCOUNT_ID}:inference-profile/global.zai.glm-5.3"`
- 针对本地目标运行 Strix。  `strix --target http://localhost:3000`
- 等待根 Strix 智能体完成，然后审阅所发现的漏洞。

Strix 会启动一组子智能体（sub-agent）来绘制威胁面（threat surface）、探索一系列潜在的漏洞类别，并尝试用一个可运行的概念验证来验证每一项发现。这有助于把甄别误报（false positive）所花的时间降到最低。一次成功的运行会生成一份报告，其中包含每一项发现的严重程度、证据和修复建议。

下面的视频展示了针对示例应用配置并运行 Strix、以及探索结果的端到端过程：

图 2：用 GLM 5.3 和 Strix 运行一次示例安全测试

## 清理

在其运行的终端中用 **Ctrl+C** 停止 Juice Shop 容器，或运行 `docker ps` 找到容器 ID，然后用 `docker stop <container-id>` 停止它。Amazon Bedrock 推理按 token 付费、不占用持久资源，因此请求完成后不会再有额外费用。如果你为本次演练生成了 Amazon Bedrock API key 且已不再需要，请在 Amazon Bedrock 控制台上将其删除。

## 可用性

到 [Amazon Bedrock 控制台](https://console.aws.amazon.com/bedrock) 上试试 GLM 5.3，按照我们[最近一篇介绍 Kimi K3 的文章](https://aws.amazon.com/blogs/machine-learning/use-open-weight-models-as-your-ai-coding-agent-with-amazon-bedrock/)所示通过 OpenCode 之类的编码助手使用它，或通过受支持的 API 连接你自己的应用。

*想了解 Amazon Bedrock 如何支持你的团队？* [*联系我们*](https://pages.awscloud.com/Amazon-Bedrock-Contact-Us.html)*，开启这段对话。*
