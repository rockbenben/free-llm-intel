---
vendor: aws_bedrock
title: Build a conversational data assistant, Part 2 – Embedding generative business intelligence with AWS Quick Sight
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-a-conversational-data-assistant-part-2-embedding-generative-business-intelligence-with-amazon-q-in-quicksight
date: 2025-07-11
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 1294e464fce5
---

# Build a conversational data assistant, Part 2 – Embedding generative business intelligence with AWS Quick Sight

In [Part 1](https://aws.amazon.com/blogs/machine-learning/build-a-conversational-data-assistant-part-1-text-to-sql-with-amazon-bedrock-agents/) of this series, we explored how Amazon’s Worldwide Returns & ReCommerce (WWRR) organization built the Returns & ReCommerce Data Assist (RRDA)—a generative AI solution that transforms natural language questions into validated SQL queries using [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/). Although this capability improves data access for technical users, the WWRR organization’s journey toward truly democratized data doesn’t end there.

For many stakeholders across WWRR, visualizing trends and patterns is far more valuable than working with raw data. These users need quick insights to drive decisions without having to interpret SQL results. Although we maintain pre-built [AWS Quick Sight](https://aws.amazon.com/quicksight/) dashboards for commonly tracked metrics, business users frequently require support for long-tail analytics—the ability to conduct deep dives into specific problems, anomalies, or regional variations not covered by standard reports.

To bridge this gap, we extended our RRDA solution beyond SQL generation to include visualization capabilities. In this post, we dive into how we integrated [AWS Quick Sight](https://aws.amazon.com/quicksight/q/) to transform natural language requests like “Show me how many items were returned in the US over the past 6 months” into meaningful data visualizations. We demonstrate how combining Amazon Bedrock Agents with AWS Quick Sight creates a comprehensive data assistant that delivers both SQL code and visual insights through a single, intuitive conversational interface—democratizing data access across the enterprise.

## Intent and domain classification for visual analytics

The overall architecture diagram of the RRDA system has two parts. In [Part 1](https://aws.amazon.com/blogs/machine-learning/build-a-conversational-data-assistant-part-1-text-to-sql-with-amazon-bedrock-agents/), we focused on the upper pathway that generates SQL; for Part 2, we explore the lower pathway (highlighted in red in the following diagram) that connects users directly to visual insights through AWS Quick Sight.

RRDA Architecture Overview highlighting the visualization pathway (shown in red) that processes SHOW_METRIC intents through Q topic retrieval and selection to deliver embedded AWS Quick Sight visualizations.

As mentioned in [Part 1](https://aws.amazon.com/blogs/machine-learning/build-a-conversational-data-assistant-part-1-text-to-sql-with-amazon-bedrock-agents/), RRDA routes user queries through intent and domain classification systems that determine how each request should be processed. When a query is classified as `SHOW_METRIC` (triggered by phrases like “show me” or “display,” or questions about visualizing trends), the system routes to our AWS Quick Sight integration pathway instead of generating SQL. Simultaneously, our domain classifier identifies business contexts like Returns Processing or Promotions to focus the search scope. This dual classification makes it possible to seamlessly switch the user experience between receiving code and receiving visual insights while maintaining business context.

For example, when a user asks “Show me the trend for how many items were returned for the past quarter,” our system identifies both the visualization intent and the Returns Processing business domain, allowing subsequent LLMs to search within domain-specific [AWS Quick Sight Q topics](https://docs.aws.amazon.com/quicksight/latest/user/quicksight-q-topics.html) rather than across the entire catalog. After the user intent is classified, RRDA notifies the user that it’s searching for relevant metrics in AWS Quick Sight and initiates the domain-filtered Q topic selection process described in the next section.

## Q topic retrieval and selection

After the user intent is classified as `SHOW_METRIC` and the relevant business domain is identified, RRDA must now determine which specific Q topic can best visualize the requested information. Q topics are specialized configurations that enable business users to ask natural language questions about specific datasets. Each Q topic contains metadata about available metrics, dimensions, time periods, and synonyms—making topic selection a critical step in delivering accurate visual insights. The challenge lies in intelligently mapping user requests to the most appropriate Q topics from our catalog of over 50 specialized configurations. To solve this problem, RRDA employs a two-step approach: first retrieving semantically relevant Q topics using vector search with [metadata filtering](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-knowledge-bases-now-supports-metadata-filtering-to-improve-retrieval-accuracy/) to narrow down candidates efficiently, then selecting the best matches using an [Amazon Bedrock](https://aws.amazon.com/bedrock/) [foundation model](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) (FM) to evaluate each candidate’s ability to address the specific metrics and dimensions in the user’s query.

We implemented this retrieval-then-selection approach by building a dedicated Q topic knowledge base using [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/), a fully managed service that you can use to store, search, and retrieve organization-specific information for use with large language models (LLMs). The metadata for each Q topic—including name, description, available metrics, dimensions, and sample questions—is converted into a searchable document and embedded using the [Amazon Titan Text Embeddings V2](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html) model. When a user asks a question, RRDA extracts the core query intent and specified domain, then performs a vector similarity search against our Q topic knowledge base. The system applies domain filters to the [vector search configuration](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_KnowledgeBaseVectorSearchConfiguration.html) when a specific business domain is identified, making sure that only relevant Q topics are considered. From this retrieved list, a lightweight Amazon Bedrock FM analyzes the candidates and identifies the most relevant Q topic that can address the user’s specific question, considering factors like metric availability, dimension support, and query compatibility.

The following diagram illustrates the Q topic retrieval and selection workflow.

Q topic retrieval and selection workflow illustrating how RRDA identifies relevant visualization sources through vector search, then optimizes user questions for AWS Quick Sight using Amazon Bedrock.

Continuing our previous example, when a user asks “Show me the trend for how many items were returned for the past quarter,” our system first detects the intent as `SHOW_METRIC`, then determines whether a domain like Returns Processing or Promotions is specified. The query is then passed to our Q topic retrieval function, which uses the [Retrieve API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Retrieve.html) to search for Q topics with relevant metadata. The search returns a ranked list of 10 candidate Q topics, each containing information about its capabilities, supported metrics, and visualization options.

This retrieval mechanism solves a critical problem in enterprise business intelligence (BI) environments—discovering which report or dataset has information to answer the user’s question. Rather than requiring users to know which of our more than 50 Q topics to query, our system automatically identifies the relevant Q topics based on semantic understanding of the request. This intelligent Q topic selection creates a frictionless experience where business users can focus on asking questions in natural language while RRDA handles the complexity of finding the right data sources behind the scenes.

## Question rephrasing for optimal Q topic results

After RRDA identifies relevant Q topics, we face another critical challenge: bridging the gap between how users naturally ask questions and the optimal format that AWS Quick Sight expects. Without this crucial step, even with the right Q topic selected, users might receive suboptimal visualizations.

### The question rephrasing challenge

Business users express their data needs in countless ways:

- Imprecise time frames: “How many items were returned lately?”
- Complex multi-part questions: “Compare how many items were returned between NA & EU for Q1”
- Follow-up questions: “Write a SQL query for how many returned items are currently being processed in the returns center” and after RRDA responds with the SQL query, then “Great! Now show me this metric for this year”

Although AWS Quick Sight is designed to handle natural language, it is a generative Q&A system rather than a conversational interface, and it performs best with clear, well-structured questions. The right phrasing significantly improves response quality by making sure AWS Quick Sight precisely understands what to visualize.

### Structured question generation with the Amazon Bedrock Converse API

To solve this challenge, we implemented a question rephrasing system using the Amazon Bedrock [Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) with [structured outputs](https://docs.aws.amazon.com/nova/latest/userguide/prompting-structured-output.html). This approach makes sure user queries are transformed into optimal formats for AWS Quick Sight while preserving critical filters and parameters.

First, we define [Pydantic](https://docs.pydantic.dev/latest/concepts/models/) data models to structure the FM output:

```
class QTopicQuestionPair(BaseModel):
    """A question related to a Q topic."""
    topic_id: str = Field(..., description="The ID of the chosen Q topic")
    question: str = Field(..., description="The relevant question to ask this Q topic")

class ListOfQTopicQuestionPairs(BaseModel):
    """Response containing a list of questions corresponding to Q topics."""
    pairs: List[QTopicQuestionPair] = Field(
        default_factory=list, description="List of {Q topic Id, Question} pair objects."
    )
```

The Converse API [tool use capability](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-inference-call.html) makes it possible to structure responses using these defined data models so our code can parse them reliably. Our system passes the user query, conversation history, and retrieved Q topic metadata to the Amazon Bedrock FM, which formulates questions following validated patterns:

- “Show me the [specific metric(s)] for/over [user filters]”
- “How has [specific metric] changed from [start time frame] to [end time frame]?”
- “Compare [metric A] to [metric B] for [time frame]”
- “What is [specific metric] for [user filters]?”

These formats consistently produce optimal results in AWS Quick Sight across our business domains while preserving critical business context—including domain-specific terminology, time filters, dimensional constraints, and comparative elements. For example, after reviewing SQL results for a resolution index metric, a user might ask the follow-up question “Now show me how this metric trended over the last 6 months,” which our system rephrases to “Show me how the resolution index trended over the last 6 months” while selecting only Amazon Q topics related to the Returns Processing business domain.

## Embedding AWS Quick Sight visualizations within the chat interface

When users ask to visualize data in the RRDA chat interface, the system seamlessly embeds AWS Quick Sight directly within the conversation. Using the Quick Sight embedding functionality, RRDA generates a secure embedding URL that renders interactive visualizations directly in the chat window. Users can view data visualizations without leaving the conversation flow. The system automatically selects the appropriate Q topic and rephrases the user’s question for optimal results, then passes this information to the embedded Quick Sight component, which generates and displays the visualization. The following screenshot shows a view (with sample data) of what this embedded experience looks like. For detailed information about the embedding capabilities used, see [Embedding the AWS Quick Sight Generative Q&A experience](https://docs.aws.amazon.com/quicksight/latest/user/embedding-gen-bi.html).

Sample Q Topic showing embedded visualization capabilities within RRDA’s chat interface, demonstrating how users can seamlessly transition from natural language questions to interactive data visualizations.

### Direct Q topic suggestions for visualization requests

When users ask visualization-oriented questions with the `SHOW_METRIC` intent (for example, “Show me how many items were returned over the past 3 months”), RRDA presents relevant Q topics as interactive suggestion cards within the conversation flow. Each suggestion includes the topic name (like “Returns Processing – Sample Topic”), along with an optimized question format that the user can choose to immediately generate the visualization.

![Screenshot of RRDA interface showing a user query "Show me how many items were returned over the past 3 months?" with the system's response recommending relevant AWS Quick Sight topics. The response suggests "Returns Processing - Sample Topic" with a specific question link "What is the return quantity for the past 3 months?" Thumbs up and thumbs down feedback buttons appear at the bottom of the response.](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/24/ML-18493-rp-chat.png)

These suggestions appear with a clear heading: “Here are the most relevant questions and AWS Quick Sight Q topics:” so it’s straightforward for users to identify which data source will best answer their question. The system formats these suggestions as clickable prompts that, when selected, automatically trigger the embedded AWS Quick Sight generative Q&A modal illustrated in the previous section.

### Contextual follow-up visualizations in conversations

RRDA proactively suggests relevant visualizations even when users are engaged in regular text conversations with the Amazon Bedrock agent described in [Part 1](https://aws.amazon.com/blogs/machine-learning/build-a-conversational-data-assistant-part-1-text-to-sql-with-amazon-bedrock-agents/). For example, when a user asks for information about a specific metric (“What is the resolution index metric? Explain it to me in 1-2 sentences”), the system provides a text explanation (which is blurred out in the following screenshot) but also automatically identifies opportunities for visual analysis. These suggestions appear as “Get related insights from AWS Quick Sight:” followed by relevant questions like “What is resolution index for the last 3 months?” This creates a seamless bridge between learning about metrics and visualizing them—users can start with simple queries about metric definitions and quickly transition to data exploration without reformulating their requests. This contextual awareness makes sure users discover valuable visualizations they might not have otherwise known to request, enhancing the overall analytics experience.

![Screenshot of a RRDA interface showing a query "Define the RP resolution index metric in 1-2 sentences" with the system's response providing the definition as "The Returns Processing Resolution Index is the percentage of returned items that are successfully processed within 7 business days, tracking how efficiently the returns fulfillment centers handle incoming returns." The interface also displays the calculation formula and suggests related insights from Amazon Q in QuickSight, with feedback buttons at the bottom.](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/24/ML-18493-rp-chat-2.png)

## Automating Q topic metadata management

Behind RRDA’s ability to suggest relevant visualizations is a knowledge base of over 50 Q topics and their metadata. To keep this knowledge base up-to-date as our analytics landscape grows, we’ve implemented an automated metadata management workflow using [AWS Step Functions](https://aws.amazon.com/step-functions/) that refreshes daily, pictured in the following diagram.

Automated Q topic metadata management workflow using AWS Step Functions that refreshes daily to keep the knowledge base current with the latest Quick Sight Q topic configurations and validated questions.

The workflow begins with our `FetchQTopicMetadata` [AWS Lambda](https://aws.amazon.com/lambda/) function, which connects to Quick Sight and gathers essential information about each Q topic—what metrics it tracks, what filters users can apply, and importantly, what questions it has successfully answered in the past. We specifically use the [DescribeTopic](https://docs.aws.amazon.com/quicksight/latest/APIReference/API_DescribeTopic.html) and [ListTopicReviewedAnswers](https://docs.aws.amazon.com/quicksight/latest/APIReference/API_ListTopicReviewedAnswers.html) APIs, and store the resulting metadata in [Amazon DynamoDB](https://aws.amazon.com/dynamodb/), a NoSQL key-value database. This creates a powerful feedback loop—when Q topic authors review and validate questions from users, these validated questions are automatically incorporated into our knowledge base, making sure the system continuously learns from user interactions and expert curation.

For the next step in the workflow, the `BatchSummarizeQTopics` function generates a concise summary of this collected metadata using Amazon Bedrock FMs. This step is necessary because raw Q topic configurations often [exceed token limits for context windows in FMs](https://aws.amazon.com/blogs/security/context-window-overflow-breaking-the-barrier/). The function extracts essential information—metrics, measures, dimensions, and example questions—into compact summaries that can be effectively processed during vector retrieval and question formulation.

The final step in our workflow is the `SyncQTopicsKnowledgeBase` function, which transforms this enriched metadata into vector-searchable documents, one for each Q topic with explicit business domain tags that enable domain-filtered retrieval. The function triggers Amazon Bedrock [knowledge base ingestion](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_StartIngestionJob.html) to rebuild vector embeddings (numerical representations that capture semantic meaning), completing the cycle from Q topic configuration to searchable knowledge assets. This pipeline makes sure RRDA consistently has access to current, comprehensive Q topic metadata without requiring manual updates, significantly reducing operational overhead while improving the quality of Q topic recommendations.

## Best practices

Based on our experience extending RRDA with visualization capabilities through AWS Quick Sight, the following are some best practices for implementing generative BI solutions in the enterprise:

- **Anticipate analytical needs with intelligent suggestions** – Use AI to predict what visualizations users potentially expect, automatically surfacing relevant charts during conversations about metrics or SQL. This alleviates discovery barriers and empowers users with insights they might not have thought initially, seamlessly bridging the gap between understanding data and visualizing trends.
- **Build an automatic translation layer when connecting disparate AI systems **– Use AI to automatically reformat natural language queries into the structured patterns that systems expect, rather than requiring users to learn precise system-specific phrasing. Preserve the user’s original intent and context while making sure each system receives input in its preferred format.
- **Design feedback loops **– Create automated systems that collect validated content from user interactions and feed it back into your knowledge bases. By harvesting human-reviewed questions from tools like AWS Quick Sight, your system continuously improves through better retrieval data without requiring model retraining.
- **Implement retrieval before generation **– Use vector search with domain filtering to narrow down relevant visualization sources before employing generative AI to select and formulate the optimal question, dramatically improving response quality and reducing latency.
- **Maintain domain context across modalities **– Make sure that business domain context carries through the entire user journey, whether users are receiving SQL code or visualizations, to maintain consistency in metric definitions and data interpretation.

For comprehensive guidance on building production-ready generative AI solutions, refer to the [AWS Well-Architected Framework Generative AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html) for best practices across security, reliability, performance efficiency, cost optimization, operational excellence, and sustainability.

## Conclusion

In this [two-part series](https://aws.amazon.com/blogs/machine-learning/build-a-conversational-data-assistant-part-1-text-to-sql-with-amazon-bedrock-agents/), we explored how Amazon’s Worldwide Returns & ReCommerce organization built RRDA, a conversational data assistant that transforms natural language into both SQL queries and data visualizations. By combining Amazon Bedrock Agents for orchestration and SQL generation with AWS Quick Sight for visual analytics, our solution democratizes data access across the organization. The domain-aware architecture, intelligent question rephrasing, and automated metadata management alleviate barriers between business questions and data insights, significantly reducing the time required to make data-driven decisions. As we continue enhancing RRDA with additional capabilities based on user feedback and advancements in FMs, we remain focused on our mission of creating a seamless bridge between natural language questions and actionable business insights.

### About the authors

**![Photo of author: Dheer Toprani](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/ML-18493-dtoprani-100x150.jpeg)Dheer Toprani** is a System Development Engineer within the Amazon Worldwide Returns and ReCommerce Data Services team. He specializes in large language models, cloud infrastructure, and scalable data systems, focusing on building intelligent solutions that enhance automation and data accessibility across Amazon’s operations. Previously, he was a Data & Machine Learning Engineer at AWS, where he worked closely with customers to develop enterprise-scale data infrastructure, including data lakes, analytics dashboards, and ETL pipelines.

**![Photo of author: Nicolas Alvarez](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/24/ML-18493-nickkalv-100x150.jpeg)Nicolas Alvarez** is a Data Engineer within the Amazon Worldwide Returns and ReCommerce Data Services team, focusing on building and optimizing recommerce data systems. He plays a key role in developing advanced technical solutions, including Apache Airflow implementations and front-end architecture for the team’s web presence. His work is crucial in enabling data-driven decision making for Amazon’s reverse logistics operations and improving the efficiency of end-of-lifecycle product management.

**![Photo of author: Lakshdeep Vatsa](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/24/ML-18493-lvatsa-100x150.jpeg)Lakshdeep Vatsa** is a Senior Data Engineer within the Amazon Worldwide Returns and ReCommerce Data Services team. He specializes in designing, building, and optimizing large-scale data and reporting solutions. At Amazon, he plays a key role in developing scalable data pipelines, improving data quality, and enabling actionable insights for Reverse Logistics and ReCommerce operations. He is deeply passionate about enhancing self-service experiences for users and consistently seeks opportunities to utilize generative BI capabilities to solve complex customer challenges.

**![Photo of author: Karam Muppidi](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/24/ML-18493-karamup-100x138.jpeg)Karam Muppidi** is a Senior Engineering Manager at Amazon Retail, leading data engineering, infrastructure, and analytics teams within the Worldwide Returns and ReCommerce organization. He specializes in using LLMs and multi-agent architectures to transform data analytics and drive organizational adoption of AI tools. He has extensive experience developing enterprise-scale data architectures, analytics services, and governance strategies using AWS and third-party tools. Prior to his current role, Karam developed petabyte-scale data and compliance solutions for Amazon’s Fintech and Merchant Technologies divisions.

**![Photo of author: Sreeja Das](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/24/ML-18493-sreejdas-100x150.jpeg)Sreeja Das** is a Principal Engineer in the Returns and ReCommerce organization at Amazon. In her 10+ years at the company, she has worked at the intersection of high-scale distributed systems in eCommerce and Payments, Enterprise services, and Generative AI innovations. In her current role, Sreeja is focusing on system and data architecture transformation to enable better traceability and self-service in Returns and ReCommerce processes. Previously, she led architecture and tech strategy of some of Amazon’s core systems including order and refund processing systems and billing systems that serve tens of trillions of customer requests everyday.
