---
vendor: aws_bedrock
title: Build an intelligent financial analysis agent with LangGraph and Strands Agents
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-an-intelligent-financial-analysis-agent-with-langgraph-and-strands-agents
date: 2025-08-13
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 3393d0219788
---

# Build an intelligent financial analysis agent with LangGraph and Strands Agents

Agentic AI is revolutionizing the financial services industry through its ability to make autonomous decisions and adapt in real time, moving well beyond traditional automation. Imagine an AI assistant that can analyze quarterly earnings reports, compare them against industry expectations, and generate insights about future performance. This seemingly straightforward task involves multiple complex steps: document processing, data extraction, numerical analysis, context integration, and insight generation.

Financial analysis workflows present unique technical challenges for [generative AI](https://aws.amazon.com/generative-ai/) that push the boundaries of traditional [large language model](https://aws.amazon.com/what-is/large-language-model/) (LLM) implementations. This domain requires architectural patterns designed to handle the inherent complexities of financial workflows to assist analysts. Although agentic AI systems drive substantial improvements in operational efficiency and customer experience, delivering measurable productivity gains across operations, they also present unique implementation challenges around governance, data privacy, and regulatory compliance. Financial institutions must carefully balance the transformative potential of agentic AI—from dynamic financial coaching to real-time risk assessment—with the need for robust oversight and control frameworks.

This post describes an approach of combining three powerful technologies to illustrate an architecture that you can adapt and build upon for your specific financial analysis needs: LangGraph for workflow orchestration, [Strands Agents](https://strandsagents.com/latest/) for structured reasoning, and [Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro) (MCP) for tool integration.

The following screenshot figure demonstrates how this solution operates in practice:

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/ML-18622-1.png)

The reference architecture discussed in this post emerged from experimenting with different patterns for financial domain applications. We hope these insights help you navigate similar challenges in your own projects, whether in finance or other complex analytical domains.

## Understanding the challenges in financial analysis workflows

Before diving into the solution implementation details, it’s worth understanding the core challenges that informed our architectural decisions. These challenges aren’t unique to our project, they’re inherent to the nature of financial analysis and appear in many complex analytical applications.Our first challenge involved dynamic and adaptive analysis flows. Financial analysis workflows are inherently dynamic, with analysts constantly adjusting their approach based on observed patterns and intuition. An analyst might shift focus from revenue analysis to operational metrics, or dive deeper into specific industry segments based on emerging insights. This requires an orchestration strategy that can handle flexible, nonlinear execution paths while maintaining analytical coherence and context throughout the process.In our second challenge, we were faced with complex integration across multiple data sources. Financial analysis requires seamless integration with various internal and external systems, from proprietary databases to public industry data APIs. Each integration point introduces potential compatibility issues and architectural complexity. The challenge lies in maintaining manageable system coupling while enabling access to diverse data sources, each with their own interfaces, authentication methods, and data formats. A robust integration strategy is needed to keep system complexity at a sustainable level while maintaining reliable data access across sources.

## Solution overview

To address these challenges, we developed an architectural pattern combining three complementary technologies:

- **LangGraph** – Provides the foundation for handling dynamic analysis flows through structured workflow orchestration, enabling flexible execution paths while maintaining state and context
- **Strands Agents** – Serves as an intermediary layer, coordinating between [foundation models](https://aws.amazon.com/what-is/foundation-models/) (FMs) and specialized tools to execute complex analytical tasks
- **MCP** – Standardizes the integration of diverse data sources and tools, simplifying the complexity of connecting to multiple financial systems and services.

This pattern is illustrated in the following diagram.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/ML-18662-2-1024x328.png)

The combination of these frameworks serves distinct but complementary purposes in the architecture. LangGraph excels at orchestrating high-level workflows and directional processes, and Strands Agents optimizes autonomous agent interactions and decision-making at a more granular level. We used this dual-framework approach to make the most of the strengths of each technology: LangGraph’s structured workflow capabilities for macro-level orchestration, and the specialized handling by Strands Agents of agent-tool interactions. Rather than being redundant, this architecture creates a more robust and flexible system capable of handling both complex workflow management and intelligent agent operations effectively. This modular, maintainable system can handle the complexity of financial analysis while remaining flexible and extensible.

### LangGraph: Structuring financial analysis workflows

One effective design principle when implementing multi-agent systems is breaking down complex problems into simpler tasks. Instead of asking an agent to solve an entire financial problem at one time, consider decomposing it into discrete analytical steps.Consider the following example. When a user wants to analyze the performance of company A compared to company B, the process works as follows:

- The user submits a natural language query: “Compare the quarterly revenue growth of Company A and Company B for the past year and explain what’s driving the differences.”
- The router node analyzes this query and determines that it requires financial data retrieval followed by comparative analysis. It routes the request to the agent specialized for financial analysis.
- The specialized agent processes the request and generates a comprehensive response that addresses the user’s query. (The specific tools and reasoning process that the agent uses to generate its response will be covered in the next section.)

This workflow is illustrated in the following diagram.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/ML-18662-3-1024x733.png)

In a multi-agent architecture design, LangGraph provides powerful workflow orchestration capabilities that align well with the dynamic nature of financial analysis. It supports both directional and recursive workflows, so you can model everything from straightforward sequential processes to complex iterative analyses that evolve based on intermediate findings.A key strength of LangGraph is how it combines flexible workflow patterns with precise programmatic control. Rather than leaving all flow decisions to LLM reasoning, you can implement specific business logic to guide the analysis process. For instance, our architecture’s router node can direct requests to specialized agents based on concrete criteria, determining whether a request requires file processing, numerical analysis, or industry data integration.Additionally, LangGraph’s GraphState primitive elegantly solves the challenge of maintaining context across distributed agent nodes. This shared state mechanism makes sure that each agent in the workflow can access and build upon previous analysis results, minimizing redundant processing while maintaining analytical coherence throughout the entire process.

### Strands Agents: Orchestrating financial reasoning

While LangGraph manages the overall workflow, Strands Agent handles the specialized reasoning and tool usage within each node. When the agent receives the request to compare companies, it first identifies the specific data needed:

- **Initial reasoning** – The agent determines that it needs quarterly revenue figures for both companies, year-over-year growth percentages, and industry benchmarks for context
- **Data retrieval** – The agent retrieves financial news mentioning both companies and pulls fundamental metrics such as quarterly revenue data and industry averages
- **Analysis and synthesis** – The agent analyzes growth trends, identifies correlations between news events and performance changes, and synthesizes findings into a comprehensive analysis explaining not only the revenue differences but also potential driving factors

This reasoning-tool execution cycle, shown in the following diagram, allows the agent to dynamically gather information and refine its analysis as needed.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/ML-18662-4-1024x774.png)

For a different use case, consider a request to “Create a Word document summarizing the financial performance of Amazon for investors”:

- The documentation agent uses a document generation tool to create a Word document with proper formatting
- The agent structures the content with appropriate sections, such as “Executive Summary,” “Revenue Analysis,” and “Industry Position”
- Using specialized formatting tools, it creates data tables for quarterly comparisons, bullet points for key insights, and embedded charts visualizing performance trends
- Finally, it delivers a professionally formatted document ready with download links

Strands agents are designed to flexibly iterate through their specialized tasks using the tools provided to them, gathering necessary information for comprehensive responses. It’s crucial to connect these agents with appropriate tools that match the nature of their assigned tasks—whether it’s financial data analysis tools, document generation capabilities, or other specialized functionalities. This alignment between agent capabilities and their toolsets facilitates optimal performance in executing their designated responsibilities.

### MCP: Interaction with financial tools

The MCP provides a foundation for creating extensible, standardized financial tools. Rather than building monolithic applications where M clients need to connect to N servers (creating M×N integration complexity), MCP standardizes the communication protocol, reducing this to M+N connections. This creates a modular system where financial analysts can focus on creating specialized tools, agent developers can concentrate on reasoning and orchestration, and new capabilities can be added without modifying existing components.

### Modular server architecture

Our architecture uses specialized MCP servers that provide focused financial capabilities. Each server exposes self-documenting tools through the standardized MCP protocol:

- **Stock analysis** – Real-time quotes and historical market data from Yahoo Finance
- **Financial analysis** – Combines fundamental metrics, such as price-to-earnings (P/E) ratios and revenue growth, with technical indicators, such as relative strength index (RSI) and moving average convergence/divergence (MACD) for investment recommendations
- **Web and news search** – Aggregates sentiment from news sources and social media with theme extraction

These capabilities are shown in the following diagram.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/ML-18662-5-1024x284.png)

Here’s how a typical MCP tool is structured:

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

### Client-side integration

The Strands Agents MCP client connects to available servers and provides unified tool access. However, because individual MCP servers can expose multiple tools, having too many tools in context can make the agent’s reasoning process inefficient. To address this, our implementation provides flexible server selection, so users can connect only to relevant MCP servers based on their analysis needs:

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

This selective approach significantly improves analysis quality by reducing tool context noise and helping the agent focus on relevant capabilities. The implementation also supports connecting to individual servers when specific functionality is needed:

```
# Connect to a single server for specialized tasks
financial_client = get_mcp_client("financial")
available_tools = get_all_available_tools()  # Discover all tools across servers
```

Although our examples use localhost endpoints for development, MCP’s streamable HTTP protocol enables seamless connection to remote servers by simply updating the URL mappings:

```
# Production setup with remote MCP servers
PRODUCTION_SERVER_URLS = {
    "stock": "https://stock-analysis-api.company.com/mcp",
    "financial": "https://financial-analysis-engine.company.com/mcp",
    "news": "https://news-sentiment-service.company.com/mcp"
}
```

The following is an example request that asks, “Analyze Amazon financial performance and market position for Q3 2025.”

The workflow is as follows:

- LangGraph receives the request and routes to the financial_analysis node
- MCP servers provide the necessary tools:  **Stock server** – `yahoo_stock_quote()` for current prices **Financial server** – `comprehensive_analysis()` for detailed metrics **News server** – `get_market_sentiment()` for recent sentiment data
- Strands Agents orchestrates the analysis and returns the final answer about the financial performance and market position of Amazon in Q3 2025:  **Stock server** – Current price: $220, P/E: 47.8, market cap: $1.6T **Financial server** – Revenue growth: +11.2% YoY, AWS: +19% YoY, operating margin: 7.8% **News server** – Sentiment: Positive (0.74), key themes: AI investments, logistics efficiency, holiday retail prep

The agent returns the following output:

> Amazon demonstrates strong performance across key segments in Q3 2025.
>           AWS continues robust growth at +19% YoY, driving improved operating margins to 7.8%.
>           The company’s AI investments are positioning it well for future growth, while logistics improvements support retail competitiveness heading into holiday season.
>           Overall sentiment remains positive despite some margin pressure from continued infrastructure investments.

## Deploy the financial analysis agent

The deployment of our financial analysis agent follows two main paths: local development for testing and iteration, followed by production deployment options for real-world use. This section focuses on getting the application running in your development environment, with production deployment covered separately.

Local deployment enables rapid iteration and testing of your financial analysis workflows before moving to production. Our application uses [Amazon Bedrock](https://aws.amazon.com/bedrock/) for its foundational AI capabilities, powering the Strands Agents components. Make sure your AWS account has Amazon Bedrock access enabled with appropriate model permissions for the models specified in your configuration. The solution can be found on GitHub in the [sample-agentic-frameworks-on-aws](https://github.com/aws-samples/sample-agentic-frameworks-on-aws/tree/main/langgraph/financial-agent) repository. Follow these steps:

### Development environment deployment

- To set up your development environment, clone the repository and install dependencies for both frontend and backend components:

```
# Clone the repository
git clone https://github.com/your-organization/financial-agent.git
cd financial-agent

# Install frontend dependencies
npm install
```

- To set up the Python backend, install the Python dependencies required for the backend services:

```
# Navigate to the backend directory
cd py-backend

# Install dependencies
pip install -r requirements.txt

# Return to the main project directory
cd ..
```

- To launch the application, use the convenient script configured in the project, which launches both the frontend and backend services simultaneously:

```
# Launch both frontend and backend
npm run dev
```

This command Starts the Next.js frontend on port 3000 and launches the FastAPI backend on port 8000.

You can now access the financial analysis agent in your browser at [http://localhost:3000](http://localhost:3000).

- To make sure your local deployment is functioning correctly,

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/ML-18622-6-1024x584.png)

- To configure the MCP tool integration, on the MCP console under **Configuration**, choose **Tool**. You can connect or disconnect necessary tools when you want to change MCP settings. This flexibility means you can:  Tailor the agent’s capabilities to specific financial analysis tasks Add specialized data sources for industry segments Control which external APIs the agent can access Create custom tool combinations for different analytical scenarios

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/ML-18662-7.png)

This configuration-driven approach embodies the flexible architecture we’ve discussed throughout this article, allowing the financial analysis agent to be adapted to various use cases without code changes. Whether you need stock market analysis, portfolio evaluation, industry news integration, or financial documentation generation, the appropriate combination of MCP tools can be selected through this interface.

### Production deployment

Local development is sufficient for testing and iteration, but deploying the financial analysis agent to production requires a more robust architecture. This section outlines our production deployment approach, which uses AWS services to create a scalable, resilient, and secure solution.

The production deployment follows a distributed architecture pattern that separates concerns while maintaining efficient communication paths. As shown in the following diagram, the production architecture consists of:

- **Web frontend** – A Next.js application deployed on [AWS Amplify](https://aws.amazon.com/amplify/) that provides the user interface for interacting with the financial agent
- **Backend application** – A containerized FastAPI service running on [Amazon Elastic Container Service](https://aws.amazon.com/ecs/) (Amazon ECS) that orchestrates the LangGraph workflow and Strands Agents for financial analysis and documentation
- **MCP server farm** – A collection of specialized microservices that provide financial tools and data connectors
- **Amazon Bedrock** – The FM service that powers the agents’ reasoning capabilities
- **[Amazon DynamoDB](https://aws.amazon.com/dynamodb/)** – A persistent storage layer for conversation history and state management

This distributed approach enables scalable performance while preserving the fundamental architectural patterns we’ve discussed throughout this post. The deployment strategy can be adapted to your specific organizational requirements and infrastructure preferences.

## Conclusion: Beyond implementation to architectural thinking

In this post, we’ve demonstrated how combining LangGraph, Strands Agents, and MCP creates a powerful architectural pattern for financial analysis applications. This approach directly addresses the key challenges in financial workflows:

- **Decomposition of complex problems** – Breaking financial analysis into manageable components with LangGraph allows for focused, accurate reasoning while maintaining overall context
- **Reasoning-tool execution cycles** – The separation between reasoning (using Strands Agents) and execution (using MCP) creates a more modular system that mirrors how financial analysts actually work
- **Flexible tool integration** – The Strands Agents built-in MCP support enables seamless connection to financial tools and document generation capabilities, allowing continuous expansion of functionality without disrupting the core architecture

This architecture serves as a foundation that you can extend and adapt to your specific financial analysis needs. Whether you’re building portfolio analysis tools, equity research assistants, investment advisory solutions, or financial documentation generators, these patterns provide a robust starting point.This post offers building blocks that you can adapt to your specific financial analysis needs. We hope these architectural insights help you navigate similar challenges in your own projects, whether in finance or other complex analytical domains.

## Next steps

We invite you to build upon our LangGraph, Strands, and MCP architecture to transform your financial workflows. Whether you’re building for a portfolio manager, equity analyst, risk professional, or financial advisor, you can create specialized tools that connect to your unique data sources. Start with a single MCP server addressing a specific pain point, then gradually expand as you experience the benefits.

Join our community. We’re building a community of generative AI practitioners who are pushing the boundaries of what’s possible with these technologies. Share your tools by contributing to our [Agentic Frameworks](https://github.com/aws-samples/sample-agentic-frameworks-on-aws/tree/main) open source GitHub repository.

## About the Authors

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/06/headshot-100x100.jpeg)**Evan Grenda** Sr. GenAI Specialist at AWS, where he works with top-tier third-party foundation model and agentic frameworks providers to develop and execute joint go-to-market strategies, enabling customers to effectively deploy and scale solutions to solve enterprise agentic AI challenges. Evan holds a BA in Business Administration from the University of South Carolina, a MBA from Auburn University, and an MS in Data Science from St. Joseph’s University.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/karanaws-100x100.jpeg)**Karan Singh** is a Agentic AI leader at AWS, where he works with top-tier third-party foundation model and agentic frameworks providers to develop and execute joint go-to-market strategies, enabling customers to effectively deploy and scale solutions to solve enterprise agentic AI challenges. Karan holds a BS in Electrical Engineering from Manipal University, a MS in Electrical Engineering from Northwestern University, and an MBA from the Haas School of Business at University of California, Berkeley.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/07/Sayan-100x100.jpeg)**Sayan Chakraborty** is a Sr. Solutions Architect at AWS. He helps large enterprises build secure, scalable, and performant solutions in the AWS Cloud. With a background of Enterprise and Technology Architecture, he has experience delivering large scale digital transformation programs across a wide range of industry verticals. He holds a B. Tech. degree in Computer Engineering from Manipal University, Sikkim, India.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/09/kevmyung-100x133.jpg)Kihyeon Myung** is a Sr. Applied AI Architect at AWS, where he helps enterprise customers build and deploy agent applications and RAG pipelines. With over 3 years of experience in AI and GenAI, Kihyeon specializes in designing and implementing agentic AI systems, combining his development background with expertise in Machine Learning and Generative AI.
