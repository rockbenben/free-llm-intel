---
vendor: aws_bedrock
title: Build an intelligent financial analysis agent with LangGraph and Strands Agents
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-an-intelligent-financial-analysis-agent-with-langgraph-and-strands-agents
date: 2025-08-13
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 2f66c25e449a
---

# 使用 LangGraph 与 Strands Agents 构建智能财务分析 agent

Agentic AI 正凭借自主决策与实时适应的能力重塑金融服务行业，其范围已远超传统自动化。设想一个能够分析季度财报、将其与行业预期对比，并就未来业绩给出洞见的 AI assistant。这一看似直接的任务其实涉及多个复杂步骤：文档处理、数据抽取、数值分析、上下文整合与洞见生成。

财务分析工作流为[生成式 AI](https://aws.amazon.com/generative-ai/) 带来了独特的技术挑战，会触及传统[大语言模型](https://aws.amazon.com/what-is/large-language-model/)（LLM）实现的现有边界。这一领域需要专为应对财务工作流固有复杂性而设计的架构模式，以辅助分析师开展工作。agentic AI 系统固然在运营效率与客户体验上带来了显著提升，并在各项业务中交付了可衡量的生产力增益，但它们也在治理、数据隐私与监管合规方面带来了独特的实施挑战。金融机构必须谨慎平衡 agentic AI 的变革潜力——从动态财务辅导到实时风险评估——与对稳健监督和控制框架的需求。

本文介绍一种把三项强大技术组合起来的方法，用以说明一套你可以针对自身财务分析需求加以调整和扩展的架构：用于工作流编排的 LangGraph、用于结构化推理的 [Strands Agents](https://strandsagents.com/latest/)，以及用于工具集成的 [Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro)（MCP）。

以下截图展示了该方案在实践中如何运作：

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/ML-18622-1.png)

本文讨论的参考架构源自针对财务领域应用各种模式的实验。我们希望这些洞见能帮助你在自己的项目中应对类似挑战，无论处在金融领域还是其他复杂分析领域。

## 理解财务分析工作流中的挑战

在深入解决方案的实现细节之前，有必要理解那些塑造了我们架构决策的核心挑战。这些挑战并非我们项目独有，它们是财务分析的本质属性，也会出现在许多复杂分析应用中。我们的第一个挑战涉及动态且自适应的分析流程。财务分析工作流本质上是动态的，分析师会不断根据观察到的模式与直觉调整方法。分析师可能把焦点从收入分析转向运营指标，也可能根据新出现的洞见深入特定行业细分。这需要一种编排策略，既能处理灵活、非线性的执行路径，又能在整个过程中保持分析的连贯性和上下文。在第二个挑战中，我们要面对跨多个数据源的复杂集成。财务分析需要与各类内部和外部系统无缝集成，从专有数据库到公开的行业数据 API。每个集成点都会引入潜在的兼容性问题和架构复杂性。挑战在于：在保持系统耦合度可控的同时，实现对多样化数据源的访问，而每个数据源都有自己的接口、认证方法和数据格式。需要一套稳健的集成策略，把系统复杂度维持在可持续的水平，同时保持跨数据源可靠的数据访问。

## 解决方案概览

为应对这些挑战，我们开发了一种组合三项互补技术的架构模式：

- **LangGraph** —— 通过结构化的工作流编排，为处理动态分析流程提供基础，使执行路径保持灵活，同时维持状态与上下文
- **Strands Agents** —— 充当中间层，在[基础模型](https://aws.amazon.com/what-is/foundation-models/)（FM）与专用工具之间进行协调，以执行复杂的分析任务
- **MCP** —— 统一多样化数据源与工具的集成方式，简化连接多个财务系统与服务的复杂性。

该模式如下图所示。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/ML-18662-2-1024x328.png)

这些框架的组合在架构中承担着不同但互补的职责。LangGraph 擅长编排高层工作流和方向性流程，Strands Agents 则在更细的粒度上优化自主 agent 的交互与决策。我们采用这种双框架方案，是为了充分发挥每项技术的优势：用 LangGraph 的结构化工作流能力做宏观层面的编排，用 Strands Agents 对 agent 与工具交互的专门处理。这一架构并不冗余，而是构建出更稳健、更灵活的系统，能够同时有效应对复杂的工作流管理和智能体的操作。这套模块化、可维护的系统可以处理财务分析的复杂性，同时保持灵活性和可扩展性。

### LangGraph：为财务分析工作流建立结构

实现多 agent 系统时一个有效的设计原则，是把复杂问题拆解为更简单的任务。与其要求一个 agent 一次性解决整个财务问题，不如考虑把它分解为一个个离散的分析步骤。看下面这个例子。当用户想分析公司 A 相对公司 B 的业绩表现时，流程如下：

- 用户提交一条自然语言查询：“比较公司 A 和公司 B 过去一年的季度收入增长，并解释是什么造成了这些差异。”
- router 节点分析该查询，判定它需要先做财务数据检索、再做对比分析。它把请求路由给专做财务分析的 agent。
- 专用 agent 处理该请求，并生成一份回应了用户查询的完整答复。（该 agent 生成答复所用的具体工具与推理过程将在下一节介绍。）

该工作流如下图所示。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/ML-18662-3-1024x733.png)

在多 agent 的架构设计中，LangGraph 提供了强大的工作流编排能力，与财务分析的动态特性高度契合。它同时支持方向性与递归式工作流，因此你既可以建模从简单的顺序流程，也可以建模那种会随中间发现而演进的复杂迭代分析。LangGraph 的一个关键优势在于，它把灵活的工作流模式与精确的程序化控制结合起来。你不必把所有流程决策都交给 LLM 推理，而可以实现具体的业务逻辑来引导分析过程。例如，我们架构中的 router 节点可以依据具体判据把请求分派给专用 agent，判断某项请求需要文件处理、数值分析还是行业数据集成。此外，LangGraph 的 GraphState 原语优雅地解决了在分布式 agent 节点之间维持上下文的难题。这种共享状态机制确保工作流中每个 agent 都能访问并基于先前的分析结果继续推进，从而减少重复处理，同时在整个过程中保持分析的连贯性。

### Strands Agents：编排财务推理

LangGraph 负责管理整体工作流，Strands Agent 则处理每个节点内部的专门推理与工具使用。当 agent 收到对比两家公司的请求时，它首先确定所需的具体数据：

- **初始推理** —— agent 判定它需要两家公司的季度收入数字、同比增长百分比，以及用于提供上下文的行业基准
- **数据检索** —— agent 检索提及这两家公司的财务新闻，并拉取季度收入数据和行业均值等基本面指标
- **分析与综合** —— agent 分析增长趋势，识别新闻事件与业绩变化之间的关联，并把发现综合成一份完整分析，不仅解释收入差异，也说明潜在的驱动因素

这个推理与工具执行的循环如下图所示，它让 agent 能够按需动态收集信息并完善分析。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/ML-18662-4-1024x774.png)

再换一个用例，考虑这样一条请求：“创建一份 Word 文档，向投资者总结 Amazon 的财务业绩”：

- 文档 agent 使用文档生成工具创建一份格式规范的 Word 文档
- agent 用恰当的章节组织内容，例如“执行摘要”“收入分析”和“行业地位”
- 借助专门的格式化工具，它创建用于季度对比的数据表格、用于关键洞见的项目符号，以及可视化业绩趋势的嵌入式图表
- 最后，它交付一份格式专业、带有下载链接的文档

Strands agent 被设计为借助提供给它的工具灵活地迭代执行专门任务，为完整答复收集必要信息。关键在于为这些 agent 配备与其任务性质相匹配的合适工具——无论是财务数据分析工具、文档生成能力，还是其他专门功能。agent 能力与工具集之间的这种匹配，有助于它们在履行既定职责时发挥最佳表现。

### MCP：与财务工具交互

MCP 为构建可扩展、标准化的财务工具提供了基础。与其构建单体应用、让 M 个客户端各自连接 N 个服务器（形成 M×N 的集成复杂度），不如让 MCP 统一通信协议，把复杂度降为 M+N 个连接。这样便形成一套模块化系统：财务分析师可以专注于创建专门工具，agent 开发者可以专注于推理与编排，而新增能力无需修改已有组件。

### 模块化服务器架构

我们的架构采用专门的 MCP 服务器来提供聚焦的财务能力。每个服务器都通过标准化的 MCP 协议暴露自描述的工具：

- **股票分析** —— 来自 Yahoo Finance 的实时报价与历史市场数据
- **财务分析** —— 结合市盈率（P/E）和收入增长等基本面指标，与相对强弱指数（RSI）和指数平滑异同移动平均线（MACD）等技术指标，给出投资建议
- **Web 与新闻搜索** —— 聚合来自新闻来源与社交媒体的情绪，并进行主题抽取

这些能力如下图所示。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/ML-18662-5-1024x284.png)

下面是一个典型 MCP 工具的结构：

```
@mcp.tool()
async def comprehensive_analysis(equity: str) -> str:
    """
    Get complete investment analysis combining both fundamental and technical factors.
    Provides a holistic view of a stock with interpreted signals, valuation assessment,
    growth metrics, financial health indicators, and momentum analysis with clear buy/sell signals.
    
    Args:
        equity: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
    """
    try:
        data = await fetch_comprehensive_analysis(equity)
        return format_analysis_results(data)
    except Exception as e:
        return f"Error retrieving comprehensive analysis: {str(e)}"
```

### 客户端集成

Strands Agents 的 MCP 客户端连接到可用的服务器，并提供统一的工具访问。不过，由于单个 MCP 服务器可能暴露多个工具，上下文中的工具过多会使 agent 的推理过程效率低下。为此，我们的实现提供了灵活的服务器选择机制，用户可以按分析需求只连接相关的 MCP 服务器：

```
# Server name mapping for easy selection
SERVER_NAME_TO_URL = {
    "word": "http://localhost:8089/mcp",
    "stock": "http://localhost:8083/mcp", 
    "financial": "http://localhost:8084/mcp",
    "news": "http://localhost:8085/mcp"
}

async def execute_financial_analysis(state: GraphState) -> GraphState:
    # Select relevant servers based on analysis type
    selected_servers = [
        SERVER_NAME_TO_URL["stock"],
        SERVER_NAME_TO_URL["financial"],
        SERVER_NAME_TO_URL["news"]  # Skip document generation for basic analysis
    ]
    
    mcp_clients, all_tools = await create_mcp_clients(selected_servers)
    
    # Create agent with focused tool access
    agent = Agent(
        model=model,
        tools=all_tools,  # Only tools from selected servers
        system_prompt=FINANCIAL_SYSTEM_PROMPT
    )
```

这种选择性接入通过减少工具上下文的噪声、帮助 agent 聚焦于相关能力，显著提升了分析质量。该实现同样支持在需要特定功能时连接单个服务器：

```
# Connect to a single server for specialized tasks
financial_client = get_mcp_client("financial")
available_tools = get_all_available_tools()  # Discover all tools across servers
```

虽然我们的示例为便于开发使用了 localhost 端点，但 MCP 的可流式 HTTP 协议只要求更新 URL 映射，就能无缝连接远程服务器：

```
# Production setup with remote MCP servers
PRODUCTION_SERVER_URLS = {
    "stock": "https://stock-analysis-api.company.com/mcp",
    "financial": "https://financial-analysis-engine.company.com/mcp",
    "news": "https://news-sentiment-service.company.com/mcp"
}
```

下面是一条示例请求，内容为“分析 Amazon 在 2025 年第三季度的财务业绩与市场地位”。

工作流如下：

- LangGraph 接收请求并路由到 financial_analysis 节点
- MCP 服务器提供必要的工具：**股票服务器** —— `yahoo_stock_quote()` 提供当前价格 **财务服务器** —— `comprehensive_analysis()` 提供详细指标 **新闻服务器** —— `get_market_sentiment()` 提供近期情绪数据
- Strands Agents 编排分析并返回关于 Amazon 2025 年第三季度财务业绩与市场地位的最终答复：**股票服务器** —— 当前价格：$220，P/E：47.8，市值：$1.6T **财务服务器** —— 收入增长：同比 +11.2%，AWS：同比 +19%，营业利润率：7.8% **新闻服务器** —— 情绪：正面（0.74），关键主题：AI 投入、物流效率、假日零售备货

agent 返回如下输出：

> Amazon 在 2025 年第三季度于各关键业务板块均展现出强劲表现。
>           AWS 继续以同比 +19% 保持稳健增长，推动营业利润率提升至 7.8%。
>           公司对 AI 的投入为其未来增长奠定了良好基础，同时物流改善也支撑着零售业务在进入假日季时的竞争力。
>           尽管持续的基础设施投入带来一定利润压力，整体情绪仍保持正面。

## 部署财务分析 agent

财务分析 agent 的部署遵循两条主要路径：先在本地开发环境中测试与迭代，再进入面向真实使用的生产部署方案。本节着重介绍如何在开发环境中把应用跑起来，生产部署另行说明。

本地部署让你在进入生产之前就能快速迭代和测试财务分析工作流。我们的应用使用 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 提供基础 AI 能力，为 Strands Agents 组件提供支撑。请确保你的 AWS 账户已开通 Amazon Bedrock 访问权限，并对配置中指定的模型具有相应的模型权限。该方案已发布在 GitHub 的 [sample-agentic-frameworks-on-aws](https://github.com/aws-samples/sample-agentic-frameworks-on-aws/tree/main/langgraph/financial-agent) 仓库中。按以下步骤操作：

### 开发环境部署

- 要搭建开发环境，请克隆仓库，并为前端和后端组件安装依赖：

```
# Clone the repository
git clone https://github.com/your-organization/financial-agent.git
cd financial-agent

# Install frontend dependencies
npm install
```

- 要搭建 Python 后端，请安装后端服务所需的 Python 依赖：

```
# Navigate to the backend directory
cd py-backend

# Install dependencies
pip install -r requirements.txt

# Return to the main project directory
cd ..
```

- 要启动应用，请使用项目中配置好的便捷脚本，它会同时启动前端和后端服务：

```
# Launch both frontend and backend
npm run dev
```

该命令会在 3000 端口启动 Next.js 前端，并在 8000 端口启动 FastAPI 后端。

现在你可以在浏览器中通过 [http://localhost:3000](http://localhost:3000) 访问财务分析 agent。

- 要确认本地部署运行正常，

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/ML-18622-6-1024x584.png)

- 要配置 MCP 工具集成，请在 MCP 控制台的 **Configuration** 下选择 **Tool**。当你想要修改 MCP 设置时，可以连接或断开必要的工具。这种灵活性意味着你可以：  针对具体财务分析任务定制 agent 的能力  为行业细分添加专门的数据源  控制 agent 可以访问哪些外部 API  为不同分析场景创建自定义的工具组合

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/ML-18662-7.png)

这种配置驱动的做法体现了我们在本文中反复讨论的灵活架构：无需改动代码，就能让财务分析 agent 适配多种用例。无论你需要股市分析、投资组合评估、行业新闻集成还是财务文档生成，都可以通过这个界面选择合适的 MCP 工具组合。

### 生产部署

本地开发足以支撑测试与迭代，但要把财务分析 agent 部署到生产，需要更稳健的架构。本节概述我们的生产部署方案，它使用 AWS 各项服务构建可扩展、有韧性且安全的解决方案。

生产部署采用分布式架构模式，在分离关注点的同时保持高效的通信路径。如下图所示，生产架构包括：

- **Web 前端** —— 部署在 [AWS Amplify](https://aws.amazon.com/amplify/) 上的 Next.js 应用，提供与财务 agent 交互的用户界面
- **后端应用** —— 运行在 [Amazon Elastic Container Service](https://aws.amazon.com/ecs/)（Amazon ECS）上的容器化 FastAPI 服务，负责编排 LangGraph 工作流与 Strands Agents，用于财务分析和文档生成
- **MCP 服务器集群** —— 一组提供财务工具与数据连接器的专门微服务
- **Amazon Bedrock** —— 为 agent 推理能力提供支持的 FM 服务
- **[Amazon DynamoDB](https://aws.amazon.com/dynamodb/)** —— 用于会话历史与状态管理的持久化存储层

这种分布式做法在保持本文反复讨论的基础架构模式的同时，实现了可扩展的性能。你可以根据自己的组织需求和基础设施偏好调整该部署策略。

## 结论：从实现走向架构思维

在本文中，我们展示了如何把 LangGraph、Strands Agents 和 MCP 结合起来，为财务分析应用构建一种强大的架构模式。这种做法直接回应了财务工作流中的关键挑战：

- **复杂问题的分解** —— 借助 LangGraph 把财务分析拆分为可管理的组件，既能做出聚焦而准确的推理，又能保持整体上下文
- **推理与工具执行的循环** —— 推理（使用 Strands Agents）与执行（使用 MCP）相分离，形成更模块化的系统，这与财务分析师的实际工作方式相呼应
- **灵活的工具集成** —— Strands Agents 内置的 MCP 支持可以无缝连接财务工具与文档生成能力，在不扰动核心架构的前提下持续扩展功能

该架构可作为基础，供你针对自己的财务分析需求进行扩展和调整。无论你是在构建投资组合分析工具、股票研究助手、投资顾问方案还是财务文档生成器，这些模式都提供了稳健的起点。本文提供了可自行调整以适配具体财务分析需求的构件。我们希望这些架构洞见能帮助你在自己的项目中应对类似挑战，无论是在金融领域还是其他复杂分析领域。

## 后续步骤

我们诚邀你在我们的 LangGraph、Strands 和 MCP 架构之上继续构建，改造你的财务工作流。无论你服务的对象是投资组合经理、股票分析师、风险专业人士还是财务顾问，都可以创建连接到独有数据源的专门工具。先从解决某一个具体痛点的单个 MCP 服务器做起，然后随着你体会到收益而逐步扩展。

加入我们的社区。我们正在建设一个生成式 AI 实践者社区，共同推动这些技术的能力边界。欢迎通过向我们的 [Agentic Frameworks](https://github.com/aws-samples/sample-agentic-frameworks-on-aws/tree/main) 开源 GitHub 仓库贡献代码，分享你的工具。

## 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/06/headshot-100x100.jpeg)**Evan Grenda** 是 AWS 的高级 GenAI 专家（Sr. GenAI Specialist），与顶尖的第三方基础模型及 agentic 框架提供商合作，制定并执行联合市场策略，帮助客户有效部署和扩展解决方案，以应对企业级 agentic AI 挑战。Evan 拥有南卡罗来纳大学工商管理学士学位、奥本大学 MBA 学位，以及圣约瑟夫大学数据科学硕士学位。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/karanaws-100x100.jpeg)**Karan Singh** 是 AWS 的 agentic AI 负责人，与顶尖的第三方基础模型及 agentic 框架提供商合作，制定并执行联合市场策略，帮助客户有效部署和扩展解决方案，以应对企业级 agentic AI 挑战。Karan 拥有曼尼帕尔大学电气工程学士学位、西北大学电气工程硕士学位，以及加州大学伯克利分校哈斯商学院的 MBA 学位。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/Sayan-100x100.jpeg)**Sayan Chakraborty** 是 AWS 的高级解决方案架构师（Sr. Solutions Architect）。他帮助大型企业在 AWS 云上构建安全、可扩展且高性能的解决方案。凭借企业与技术架构方面的背景，他在众多行业垂直领域交付过大规模数字化转型项目。他拥有印度锡金曼尼帕尔大学计算机工程学士（B. Tech.）学位。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/09/kevmyung-100x133.jpg)Kihyeon Myung** 是 AWS 的高级应用 AI 架构师（Sr. Applied AI Architect），帮助企业在 AWS 上构建和部署 agent 应用与 RAG pipeline。Kihyeon 拥有 3 年以上 AI 与 GenAI 经验，专长于设计和实现 agentic AI 系统，把开发背景与机器学习、生成式 AI 方面的专业知识相结合。
