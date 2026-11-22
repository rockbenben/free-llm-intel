---
vendor: aws_bedrock
title: Choosing the right approach for generative AI-powered structured data retrieval
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/choosing-the-right-approach-for-generative-ai-powered-structured-data-retrieval
date: 2025-07-01
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: da45e2907c00
---

# Choosing the right approach for generative AI-powered structured data retrieval

Organizations want direct answers to their business questions without the complexity of writing SQL queries or navigating through business intelligence (BI) dashboards to extract data from structured data stores. Examples of structured data include tables, databases, and data warehouses that conform to a predefined schema. Large language model (LLM)-powered natural language query systems transform how we interact with data, so you can ask questions like “Which region has the highest revenue?” and receive immediate, insightful responses. Implementing these capabilities requires careful consideration of your specific needs—whether you need to integrate knowledge from other systems (for example, unstructured sources like documents), serve internal or external users, handle the analytical complexity of questions, or customize responses for business appropriateness, among other factors.

In this post, we discuss LLM-powered structured data query patterns in AWS. We provide a decision framework to help you select the best pattern for your specific use case.

## Business challenge: Making structured data accessible

Organizations have vast amounts of structured data but struggle to make it effectively accessible to non-technical users for several reasons:

- Business users lack the technical knowledge (like SQL) needed to query data
- Employees rely on BI teams or data scientists for analysis, limiting self-service capabilities
- Gaining insights often involves time delays that impact decision-making
- Predefined dashboards constrain spontaneous exploration of data
- Users might not know what questions are possible or where relevant data resides

## Solution overview

An effective solution should provide the following:

- A conversational interface that allows employees to query structured data sources without technical expertise
- The ability to ask questions in everyday language and receive accurate, trustworthy answers
- Automatic generation of visualizations and explanations to clearly communicate insights.
- Integration of information from different data sources (both structured and unstructured) presented in a unified manner
- Ease of integration with existing investments and rapid deployment capabilities
- Access restriction based on identities, roles, and permissions

In the following sections, we explore five patterns that can address these needs, highlighting the architecture, ideal use cases, benefits, considerations, and implementation resources for each approach.

## Pattern 1: Direct conversational interface using an enterprise assistant

This pattern uses [Amazon Q Business](https://aws.amazon.com/q/business/), a generative AI-powered assistant, to provide a chat interface on data sources with native connectors. When users ask questions in natural language, Amazon Q Business connects to the data source, interprets the question, and retrieves relevant information without requiring intermediate services. The following diagram illustrates this workflow.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/01/ML_18613_pattern-1.png)

This approach is ideal for internal enterprise assistants that need to answer business user-facing questions from both structured and unstructured data sources in a unified experience. For example, HR personnel can ask “What’s our parental leave policy and how many employees used it last quarter?” and receive answers drawn from both leave policy documentation and employee databases together in one interaction. With this pattern, you can benefit from the following:

- Simplified connectivity through the extensive Amazon Q Business library of built-in connectors
- Streamlined implementation with a single service to configure and manage
- Unified search experience for accessing both structured and unstructured information
- Built-in understanding and respect existing identities, roles, and permissions

You can define the scope of data to be pulled in the form of a SQL query. Amazon Q Business pre-indexes database content based on defined SQL queries and uses this index when responding to user questions. Similarly, you can define the sync mode and schedule to determine how often you want to update your index. Amazon Q Business does the heavy lifting of indexing the data using a Retrieval Augmented Generation (RAG) approach and using an LLM to generate well-written answers. For more details on how to set up Amazon Q Business with an [Amazon Aurora PostgreSQL-Compatible Edition](https://aws.amazon.com/rds/aurora/postgresql-features/) connector, see [Discover insights from your Amazon Aurora PostgreSQL database using the Amazon Q Business connector](https://aws.amazon.com/blogs/machine-learning/discover-insights-from-your-amazon-aurora-postgresql-database-using-the-amazon-q-business-connector/). You can also refer to the complete list of [supported data source connectors](https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/connectors-list.html).

## Pattern 2: Enhancing BI tool with natural language querying capabilities

This pattern uses [AWS Quick Sight](https://aws.amazon.com/quicksight/q/) to process natural language queries against datasets that have been previously configured in [AWS Quick Sight](https://aws.amazon.com/quicksight). Users can ask questions in everyday language within the Quick Sight interface and get visualized answers without writing SQL. This approach works with Quick Sight (Enterprise or Q edition) and supports various data sources, including [Amazon Relational Database Service](https://aws.amazon.com/rds/) (Amazon RDS), [Amazon Redshift](https://aws.amazon.com/redshift), [Amazon Athena](https://aws.amazon.com/athena), and others. The architecture is depicted in the following diagram.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/01/ML_18613_pattern-2.png)

This pattern is well-suited for internal BI and analytics use cases. Business analysts, executives, and other employees can ask ad-hoc questions to get immediate visualized insights in the form of dashboards. For example, executives can ask questions like “What were our top 5 regions by revenue last quarter?” and immediately see responsive charts, reducing dependency on analytics teams. The benefits of this pattern are as follows:

- It enables natural language queries that produce rich visualizations and charts
- No coding or machine learning (ML) experience is needed—the heavy lifting like natural language interpretation and SQL generation is managed by AWS Quick Sight
- It integrates seamlessly within the familiar Quick Sight dashboard environment

Existing Quick Sight users might find this the most straightforward way to take advantage of generative AI benefits. You can optimize this pattern for higher-quality results by configuring topics like curated fields, synonyms, and expected question phrasing. This pattern will pull data only from a specific configured data source in Quick Sight to produce a dashboard as an output. For more details, check out [Quick Sight DemoCentral](https://democentral.learnquicksight.online/) to view a demo in Quick Sight, see the generative BI learning dashboard, and view guided instructions to create dashboards with Amazon Q. Also refer to the list of [supported data sources](https://docs.aws.amazon.com/quicksight/latest/user/supported-data-sources.html).

## Pattern 3: Combining BI visualization with conversational AI for a seamless experience

This pattern merges BI visualization capabilities with conversational AI to create a seamless knowledge experience. By [integrating AWS Quick Sight](https://docs.aws.amazon.com/quicksight/latest/user/generative-bi-q-business.html) with [Amazon Q Business](https://aws.amazon.com/q/business/) (with the Quick Sight plugin enabled), organizations can provide users with a unified conversational interface that draws on both unstructured and structured data. The following diagram illustrates the architecture.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/01/ML_18613_pattern-3a.png)

This is ideal for enterprises that want an internal AI assistant to answer a variety of questions—whether it’s a metric from a database or knowledge from a document. For example, executives can ask “What was our Q4 revenue growth?” and see visualized results from data warehouses through Amazon Redshift through Quick Sight, then immediately follow up with “What is our company vacation policy?” to access HR documentation—all within the same conversation flow. This pattern offers the following benefits:

- It unifies answers from structured data (databases and warehouses) and unstructured data (documents, wikis, emails) in a single application
- It delivers rich visualizations alongside conversational responses in a seamless experience with real-time analysis in chat
- There is no duplication of work—if your BI team has already built datasets and topics in Quick Sight for analytics, you use that in Amazon Q Business
- It maintains conversational context when switching between data and document-based inquiries

For more details, see [Query structured data from Amazon Q Business using AWS Quick Sight integration](https://aws.amazon.com/blogs/machine-learning/query-structured-data-from-amazon-q-business-using-amazon-quicksight-integration/) and [Amazon Q Business now provides insights from your databases and data warehouses (preview)](https://aws.amazon.com/about-aws/whats-new/2024/12/amazon-q-business-insights-databases-data-warehouses-preview/).

Another variation of this pattern is recommended for BI users who want to expose unified data through rich visuals in Quick Sight, as illustrated in the following diagram.

![Structured data retrieval using hybrid approach option 2](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/01/ML_18613_pattern3b-1.png)

For more details, see [Integrate unstructured data into AWS Quick Sight using Amazon Q Business](https://aws.amazon.com/blogs/business-intelligence/integrate-unstructured-data-into-amazon-quicksight-using-amazon-q-business/).

## Pattern 4: Building knowledge bases from structured data using managed text-to-SQL

This pattern uses [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/) to enable [structured data retrieval](https://aws.amazon.com/about-aws/whats-new/2024/12/amazon-bedrock-knowledge-bases-structured-data-retrieval/). The service provides a fully managed text-to-SQL module that alleviates common challenges in developing natural language query applications for structured data. This implementation uses [Amazon Bedrock](https://aws.amazon.com/bedrock/) ([Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) and Amazon Bedrock Knowledge Bases) along with your choice of data warehouse such as Amazon Redshift or [Amazon SageMaker Lakehouse](https://aws.amazon.com/sagemaker/lakehouse/). The following diagram illustrates the workflow.

![Structured data retrieval using Amazon Bedrock Knowledge Bases](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/01/ML_18613_pattern4.png)

For example, a seller can use this capability embedded into an ecommerce application to ask a complex query like “Give me top 5 products whose sales increased by 50% last year as compared to previous year? Also group the results by product category.” The system automatically generates the appropriate SQL, executes it against the data sources, and delivers results or a summarized narrative. This pattern features the following benefits:

- It provides fully managed text-to-SQL capabilities without requiring model training
- It enables direct querying of data from the source without data movement
- It supports complex analytical queries on warehouse data
- It offers flexibility in foundation model (FM) selection through Amazon Bedrock
- API connectivity, personalization options, and context-aware chat features make it better suited for customer facing applications

Choose this pattern when you need a flexible, developer-oriented solution. This approach works well for applications (internal or external) where you control the UI design. Default outputs are primarily text or structured data. However, executing arbitrary SQL queries can be a security risk for text-to-SQL applications. It is recommended that you take precautions as needed, such as using restricted roles, read-only databases, and sandboxing. For more information on how to build this pattern, see [Empower financial analytics by creating structured knowledge bases using Amazon Bedrock and Amazon Redshift](https://aws.amazon.com/blogs/big-data/empower-financial-analytics-by-creating-structured-knowledge-bases-using-amazon-bedrock-and-amazon-redshift/). For a list of supported structured data stores, refer to [Create a knowledge base by connecting to a structured data store](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-structured-create.html).

## Pattern 5: Custom text-to-SQL implementation with flexible model selection

This pattern represents a build-your-own solution using FMs to convert natural language to SQL, execute queries on data warehouses, and return results. Choose Amazon Bedrock when you want to quickly integrate this capability without deep ML expertise—it offers a fully managed service with ready-to-use FMs through a unified API, handling infrastructure needs with pay-as-you-go pricing. Alternatively, select [Amazon SageMaker AI](https://aws.amazon.com/sagemaker-ai/) when you require extensive model customization to build specialized needs—it provides complete ML lifecycle tools for data scientists and ML engineers to build, train, and deploy custom models with greater control. For more information, refer to our [Amazon Bedrock or Amazon SageMaker AI decision guide](https://docs.aws.amazon.com/decision-guides/latest/bedrock-or-sagemaker/bedrock-or-sagemaker.html). The following diagram illustrates the architecture.

![Structured data retrieval using Amazon Bedrock or Amazon SageMaker AI](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/01/ML_18613_pattern-5.png)

Use this pattern if your use case requires specific open-weight models, or you want to fine-tune models on your domain-specific data. For example, if you need highly accurate results for your query, then you can use this pattern to fine-tune models on specific schema structures, while maintaining the flexibility to integrate with existing workflows and multi-cloud environments. This pattern offers the following benefits:

- It provides maximum customization in model selection, fine-tuning, and system design
- It supports complex logic across multiple data sources
- It offers complete control over security and deployment in your virtual private cloud (VPC)
- It enables flexible interface implementation (Slack bots, custom web UIs, notebook plugins)
- You can implement it for external user-facing solutions

For more information on steps to build this pattern, see [Build a robust text-to-SQL solution generating complex queries, self-correcting, and querying diverse data sources](https://aws.amazon.com/blogs/machine-learning/build-a-robust-text-to-sql-solution-generating-complex-queries-self-correcting-and-querying-diverse-data-sources/).

## Pattern comparison: Making the right choice

To make effective decisions, let’s compare these patterns across key criteria.

### Data workload suitability

Different out-of-the-box patterns handle transactional (operational) and analytical (historical or aggregated) data with varying degrees of effectiveness. Patterns 1 and 3, which use Amazon Q Business, work with indexed data and are optimized for lookup-style queries against previously indexed content rather than real-time transactional database queries. Pattern 2, which uses AWS Quick Sight, gets visual output for transactional information for ad-hoc analysis. Pattern 4, which uses Amazon Bedrock structured data retrieval, is specifically designed for analytical systems and data warehouses, excelling at complex queries on large datasets. Pattern 5 is a self-managed text-to-SQL option that can be built to support both transactional or analytical needs of users.

### Target audience

Architectures highlighted in Patterns 1, 2, and 3 (using Amazon Q Business, AWS Quick Sight, or a combination) are best suited for internal enterprise use. However, you can use [AWS Quick Sight Embedded](https://aws.amazon.com/quicksight/embedded-analytics/) to embed data visuals, dashboards, and natural language queries into both internal or customer-facing applications. Amazon Q Business serves as an enterprise AI assistant for organizational knowledge that uses subscription-based pricing tiers that is designed for internal employees. Pattern 4 (using Amazon Bedrock) can be used to build both internal as well as customer-facing applications. This is because, unlike the subscription-based model of Amazon Q Business, Amazon Bedrock provides API-driven services that alleviate per-user costs and identity management overhead for external customer scenarios. This makes it well-suited for customer-facing experiences where you need to serve potentially thousands of external users. The custom LLM solutions in Pattern 5 can similarly be tailored to external application requirements.

### Interface and output format

Different patterns deliver answers through different interaction models:

- **Conversational experiences** – Patterns 1 and 3 (using Amazon Q Business) provide chat-based interfaces. Pattern 4 (using Amazon Bedrock Knowledge Bases for structured data retrieval) naturally supports AI assistant integration, and Pattern 5 (a custom text-to-SQL solution) can be designed for a variety of interaction models.
- **Visualization-focused output** – Pattern 2 (using AWS Quick Sight) specializes in generating on-the-fly visualizations such as charts and tables in response to user questions.
- **API integration** – For embedding capabilities into existing applications, Patterns 4 and 5 offer the most flexible API-based integration options.

The following figure is a comparison matrix of AWS structured data query patterns.

![Diagram Table](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/03/Diagram-Table-modified-title-2.png)

## Conclusion

Between these patterns, your optimal choice depends on the following key factors:

- **Data location and characteristics** – Is your data in operational databases, already in a data warehouse, or distributed across various sources?
- **User profile and interaction model** – Are you supporting internal or external users? Do they prefer conversational or visualization-focused interfaces?
- **Available resources and expertise** – Do you have ML specialists available, or do you need a fully managed solution?
- **Accuracy and governance requirements** – Do you need strictly controlled semantics and curation, or is broader query flexibility acceptable with monitoring?

By understanding these patterns and their trade-offs, you can architect solutions that align with your business objectives.

### About the authors

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/20/akshara2.png)**Akshara Shah** is a Senior Solutions Architect at Amazon Web Services. She helps commercial customers build cloud-based generative AI services to meet their business needs. She has been designing, developing, and implementing solutions that leverage AI and ML technologies for more than 10 years. Outside of work, she loves painting, exercising and spending time with family.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/20/Sanghwa-Profilenew.png)Sanghwa Na** is a Generative AI Specialist Solutions Architect at Amazon Web Services. Based in San Francisco, he works with customers to design and build generative AI solutions using large language models and foundation models on AWS. He focuses on helping organizations adopt AI technologies that drive real business value
