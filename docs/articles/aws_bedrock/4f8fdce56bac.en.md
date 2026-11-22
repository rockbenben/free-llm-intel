---
vendor: aws_bedrock
title: Tyson Foods elevates customer search experience with an AI-powered conversational assistant
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/tyson-foods-elevates-customer-search-experience-with-an-ai-powered-conversational-assistant
date: 2025-08-20
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: a7bc084b33c2
---

# Tyson Foods elevates customer search experience with an AI-powered conversational assistant

[Tyson Foodservice](https://www.tysonfoodservice.com/) operates as a critical division within [Tyson Foods Inc.](https://www.tysonfoods.com/), using its extensive protein production capabilities to supply a diverse array of foodservice clients across multiple sectors. As one of the largest protein providers in the US, Tyson Foods produces approximately 20% of the nation’s beef, pork, and chicken, which forms the foundation of its foodservice offerings.

Tyson Foodservice operates through a B2B model, selling products to distributors rather than directly to end consumers, while serving diverse foodservice operators, including restaurants, schools, healthcare facilities, and convenience stores. Until recently, Tyson had limited direct engagement with over 1 million unattended operators who purchased their products through distributors without direct company relationships. To bridge this gap, Tyson has implemented a generative AI assistant on their website, enabling them to scale sales efforts, gather customer insights, and establish direct communication channels. The company’s website now functions as a critical interface where operators can explore products, access menu trends, and discover tailored solutions for their specific foodservice segments, all enhanced by AI-driven personalization that better serves both established customers and previously unattended operators.

In this post, we explore how Tyson Foods collaborated with the [AWS Generative AI Innovation Center](https://aws.amazon.com/ai/generative-ai/innovation-center/) to revolutionize their customer interaction through an intuitive AI assistant [integrated into their website](https://www.tysonfoodservice.com/). The AI assistant was built using [Amazon Bedrock](https://aws.amazon.com/bedrock/), a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies like AI21 Labs, Anthropic, Cohere, Meta, Mistral AI, Stability AI, and Amazon through a single API, along with a broad set of capabilities to build generative AI applications with security, privacy, and responsible AI.

![Tyson FoodService AI chat assistant interface](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/01/tyson-bp-image-1.jpeg)

## Solution overview

In this section, we describe the overall architecture of the solution. The workflow includes the following high-level steps:

- A user uses the search bar in [https://www.tysonfoodservice.com/](https://www.tysonfoodservice.com/). The query string is converted to embeddings using Amazon Bedrock and the [Amazon Titan Text Embeddings model](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html). The search application performs a k-nearest neighbors (k-NN) vector search to find relevant results in [Amazon OpenSearch Serverless](https://aws.amazon.com/opensearch-service/features/serverless/) and return those results to the website. The search application is deployed in [Amazon Elastic Container Service](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html) (Amazon ECS) using [AWS Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html) as the capacity provider and exposed as a REST API using an [Application Load Balancer](https://aws.amazon.com/elasticloadbalancing/application-load-balancer/) protected by [AWS WAF](https://aws.amazon.com/waf/).
- The user uses the AI assistant interface to ask questions in natural language. The query is processed by the agent node using [Anthropic’s Claude 3.5 Sonnet](https://aws.amazon.com/bedrock/claude/) on Amazon Bedrock. Depending on the subject of the query, the agent might orchestrate multiple agents to return relevant information to the user. The application is deployed using a similar architecture to the semantic search component with the addition of an [Amazon Relational Database Service](https://aws.amazon.com/rds/) (Amazon RDS) database cluster to persist the user high-value actions for analytics purposes.
- Products, recipes, ingredients and other relevant data are available from external sources in JSON format. These are processed using Amazon Bedrock and the Amazon Titan Text Embeddings model to create semantic search embeddings. Then these are ingested into OpenSearch Serverless. The ingestion process run in a different ECS cluster using Fargate as the capacity provider.

The following diagram illustrates this architecture.

![Tyson FoodService AI assistant architecture](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/01/tyson-bp-image-2.png)

In the following sections, we discuss the solution’s key components and benefits in more detail.

## Improved semantic search

The earlier iteration of search on the Tyson Foodservice website relied on keyword-based search. Traditional keyword-based search on CPG websites like Tyson Foodservice often falters when customers search for products using industry terminology that varies from official catalog descriptions. Chefs searching for “pulled chicken” might miss relevant products labeled as “shredded chicken,” or those looking for “wings” might not see results for “party wings” or “drummettes.” This disconnect frustrates food service professionals who need specific ingredients under tight deadlines and ultimately drives them to competitors where they can more quickly find what they need, resulting in lost revenue opportunities for Tyson. Semantic search transforms this experience by understanding the conceptual relationships between culinary terms, preparation methods, and product applications. A chef searching for “buffalo-style appetizers” would receive results for wings, boneless bites, and similar products regardless of exact keyword matches. By recognizing menu trends, cooking techniques, and professional kitchen terminology, semantic search helps foodservice operators quickly find the Tyson products that meet their exact operational needs, even when using language that differs from catalog descriptions.

Tyson Foodservice implemented their semantic search capability using OpenSearch Serverless, a fully managed service that minimized the operational complexity of maintaining search infrastructure. This solution automatically scales compute and storage resources to match query volume and product catalog size without requiring dedicated administrative overhead. The serverless architecture helped Tyson rapidly deploy advanced natural language processing capabilities across their entire product database while maintaining cost-efficiency, because they only pay for the resources they actually use. With OpenSearch Serverless, Tyson incorporated vector embeddings and powerful query capabilities that understand foodservice terminology variations, preparation methods, and culinary applications, transforming how operators discover products that meet their specific needs even when their search terms don’t exactly match catalog descriptions.

For indexing Tyson’s diverse content library of products, recipes, and articles, we implemented a preprocessing workflow that transforms raw metadata into optimized semantic search queries. We used large language models (LLMs) to analyze and extract only the most relevant elements from each content piece, creating meaningful search strings specifically designed for semantic indexing. This approach made sure that purely presentational website copy and non-essential informational text were filtered out, and search-critical elements like culinary applications, preparation methods, and ingredient specifications received proper emphasis in the index. By curating what content gets indexed rather than including everything verbatim, we dramatically improved search relevance while reducing index bloat, so OpenSearch Serverless delivered more precise results that truly match the intent behind chef and operator queries. For indexing the text as semantic vectors, we used Amazon Titan Text Embeddings V2 on Amazon Bedrock.

The following example prompt illustrates the transformation using only the title, description, and reasons to buy metadata. This generic strategy can be customized according to the customer’s specific needs.

```
SEARCH_STRING_PROMPT = """ Given a product title, description, and reasons to
buy, create a single, concise search string suitable for indexing in a vector
database. This string should focus on distinguishing features, assuming all
products are for foodservice operators unless explicitly stated otherwise.
Enclose the generated search string within <search_string> XML tags. 

Follow these guidelines:
1. Start with the brand name and product line (if applicable).
2. Include the main product type and specific identifying features.
3. List concrete attributes such as preparation state, packaging, or quantity.
4. Mention specific varieties or assortments included in the product.
5. Incorporate key points from the reasons to buy, focusing on unique and
   specific selling points.
6. Avoid generic terms or those common to all products in the category (e.g.,
   "food service", "restaurant", "operator").
7. Omit cliché marketing terms (e.g., "versatile", "high-quality", "innovative")
   unless they have a specific, demonstrable meaning in the context of the
   product.
8. Use precise descriptors that differentiate the product from others in its
   category.
9. Omit articles (a, an, the) and unnecessary connecting words.
10. Use lowercase for all terms except proper nouns.
11. Separate terms with single spaces.
12. Aim for a length of 15-20 words.
13. Prioritize terms that potential buyers are most likely to use in specific
    search queries.
    
Example input:
<title>Tyson® Heritage Valley™ IF Unbreaded 8 Piece Cut Chicken</title>
<description>Order a variety of crispy, seasoned chicken cuts with 
Heritage Valley™ Uncooked, Ice Glazed 8 Piece Cut Chicken. Featuring an 
assortment of breasts, drumsticks, thighs and wings, our chicken portions 
are completely customizable and perfect for center-of-plate features. 
Separately packaged for quick and easy preparation and portion control, 
our packaging helps your staff reduce waste by allowing them to use what 
they need, when they need. Ready to cook from frozen, simply fry and 
serve as an assortment for a buffet protein choice.
</description>
<reasons_to_buy>
['Bone-in assortment of breasts, drumsticks, thighs and wings.', 
'Individually quick frozen, locking in natural juices and tenderness.', 
'Different cuts separately bagged for quick and easy preparation and cleanup.', 
'Ready to cook from frozen.']
</reasons_to_buy>

Example output: <search_string>tyson heritage valley unbreaded raw 8-piece
chicken bone-in breasts drumsticks thighs wings individually-frozen
separate-bags cook-from-frozen juicy center-of-plate</search_string>

Now, create a similar search string for the following product:
<title>{title}</title>
<description>{description}</description>
<reasons_to_buy>{reasons_to_buy}</reasons_to_buy>
"""
```

## Agentic chat built using Anthropic’s Claude 3.5 Sonnet on Amazon Bedrock and LangGraph

Tyson Foodservice has integrated a powerful generative AI assistant into their website, using Anthropic’s Claude 3.5 Sonnet on Amazon Bedrock and [LangGraph](https://www.langchain.com/langgraph). This AI assistant delivers a seamless conversational search experience that offers comprehensive support across Tyson’s extensive range of products, recipes, and articles, providing contextual guidance through natural conversation. Its capabilities include:

- **Personalized search** – Uses semantic search to find relevant products, recipes, and articles. The AI assistant customizes recommendations by learning about the user’s business and role, creating a tailored experience while gathering valuable customer insights for Tyson.
- **Detailed product information** – Provides comprehensive details about specific Tyson products, including descriptions, ingredients, preparation methods, and suggested applications.
- **Distributor services** – Helps users locate nearby distributors and check product availability in their area.
- **Purchasing assistance** – Offers information on how to buy Tyson products and connects customers with sales representatives when needed.
- **Promotion awareness** – Keeps customers informed about current Tyson Foodservice promotions and special offers.
- **Feedback channel** – Provides a streamlined way for customers to submit product and service feedback directly to Tyson.
- **Natural conversational flow** – Maintains context throughout the interaction, allowing users to reference previous results and ask follow-up questions for a more human-like conversation experience.

The following diagram illustrates the high-level architecture of the AI assistant. The system uses the tool calling capabilities of Anthropic’s Claude to implement the AI assistant’s agentic behavior. We used LangGraph to streamline the implementation process, because it provides several convenient primitives specifically designed for building agentic systems with LLMs.

![Tyson Food Services agentic chat tool calling](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/01/tyson-bp-image-3.jpeg)

The main components of the architecture are:

- **Agent node** – The agent node is implemented using a large prompt that directly receives the user message and responds using the conversational capabilities of the LLM. It also defines the agentic behavior by using the tool calling capability: whenever serving the user’s request requires calling a tool, the agent node issues a tool request.
- **Tool execution node **– This node implements a generic tool executor that connects to various tools. Whenever a tool call is issued by the agent node, this node handles the execution of the tool call. The tool calling node executes the tools, which are defined as Python functions, and returns the results to the agent node to be transformed or summarized and presented to the user. LangGraph provides a generic implementation of the [ToolNode](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/) that can also be extended to implement additional functionality.
- **Tools layer **– Tools are implemented as simple programmatic functions that take inputs and return outputs. These tools augment the capabilities of LLMs by performing functions like retrieving data or submitting feedback. The tools are stateless and agnostic to the current conversation between the user and agent. The LLM agent extracts the input parameters required to execute these tools. These tools in our implementation are a thin wrapper around the services and database layer that implement the actual functionality.

The following system prompt provides a general guidance for implementing the agent node:

```
import date

AGENT_SYSTEM_PROMPT = """
# Tyson Foodservice (TFS) Customer Support Assistant

## Core Role and Purpose
You are a helpful customer support assistant for Tyson Foodservice a.k.a TFS
hosted on their https://www.tysonfoodservice.com/ website.  You will be helpful
and answer the customers questions. The customers are mainly interested in
learning about the products for their specific needs.
Refrain from engaging in any conversation unrelated to tyson food search of
products, recipes or distributors. If the user asks any unrelated questions the
politely decline and mention your purpose. Do not provide and additional
information or advice.
 
Your job is to stay factual and only provide relevant information from the
current context or retrieved using the tools. Do not offer your own suggestions.
Customers are looking for concrete information that is available in the Tyson
Foodservice database.

## About Tyson Foodservice
Tyson Foods is a major American multinational corporation and one of the world's
largest processors and marketers of chicken, beef, and pork.

### Distributors
Tyson foods mainly sells their products through distributors and does not sell
them directly. Each distributor is identified by a unique identifier named
distributor_id which is used as parameters for the tools, do not use the
distributor name as query parameter.

### Foodservice Operators
Foodservice Operators, or simply Operators, are Tyson Foods' primary customers.
These encompass diverse businesses in the foodservice sector, each with unique
needs. Understanding the distinct personas of various Operator types is crucial
for Tyson Foods to:
- Tailor product offerings effectively
- Develop targeted marketing strategies
- Create relevant recipe suggestions
- Address specific operational challenges
By analyzing different Operator segments (e.g., quick-service restaurants, fine
dining, educational institutions, healthcare facilities), Tyson Foods can
customize its products, offer innovative menu solutions, and provide value-added
services. This approach positions Tyson Foods as a strategic partner, driving
growth and maintaining competitiveness in the foodservice industry.

## Using Tools
You will be provide a variety of tools to perform your job, use them wisely and
ask the customer for relevant information that they have not provided. E.g. if
the search tool requires persona and the customer has not provided it then ask
the customer.
- Do not explicitly declare the tools to the users as the users are not aware of
  the internal workings of the tools.
- Do not try to intrepret the results of the search tool and show them as it is
  to the user.
- Operators may have their preferred distributor they buy from so let them
  confirm or select their distributor before checking for availability of
  products.
- Customers might sometimes search for things that are not available in tyson
  food catalog. If the search did not produce any results then just inform the
  user and do not suggest any external sources.
- When trying to determine the parameters for a tool, do not infer them from
  other parameters. E.g. do not infer the User's name from their email.
  Explicitly ask for the name.
- If the users complain or praise the chatbot then you can ask for their
  feedback in the chatbot and use the `submit_feedback` tool to submit the
  feedback. Ask the user to provide the relevant contact information.

## Product, Recipes, and Articles Search
Search functionality is a critical tool on Tyson's website, allowing users to
find products, recipes, and articles. It enables searches across three main
entity types:
- **Products**: The core offerings of Tyson Foods. These are identified by a
  unique GTIN (Global Trade Item Number).
- **Recipes**: Culinary ideas provided by Tyson Foods to encourage product use.
  Each recipe incorporates one or more Tyson products.
- **Articles**: Informative content on various topics, created by Tyson Foods
  for their customers.
- Do not provide any items or suggestions outside of the ones that are found
  through search.
- When the user asks to for details or a product or compare two or more
  products, retrieve the details of the products first using the tools to get
  product details.
- While users of the site are mainly looking for products, they might also be
interested in recipes and articles so it's important to not omit them when
displaying the search results.

### User Profile or Persona
In order to serve the user's better, the search tool can accept the user's
persona as an input. User profile or persona is a concise description of the
type of role that a user performs in the foodservice industry. A few examples
of persona are
- Restaurant owners looking to optimize costs
- Chef looking for unique ingredients
- K12 operators looking for healthy menu items
They can also be simple roles if the user has not provided any additional
information. Examples are
- Restaurant owner
- Chef
- Hotel Manager
The user persona should not include the search query that they are using for
finding products E.g. these are not good personas
- Restaurant owner looking for chicken nuggets
The above is not a good persona because it includes the product

### Search query string
Search queries should be simple and specific to the products or recipes and
should not contain the operator information
Here are some examples: 
- Instead of "healthy chicken wings for K12" use "chicken wings"
- Instead of "mexican beef patties for Deli operation" use "mexican beef
  patties"

### Product Results Display 
When listing the product results, always display them in the following format as
a numbered list. This will be displayed in the UI using markdown. 
1. **Title**
- GTIN
- description - This is a brief description
- [Product Page](Product url link)

### Recipes Results Display
When displaying recipes. Display the following
1. **Title**
- description - This is a brief description
- [Recipe Page](Recipe url link)

## Contact or provide feedback
- If the users want to reach out to Tyson foods team then they can use the form
  using this link [Contact
  Us](https://www.tysonfoodservice.com/connect/contact-us) 
- Users can submit their feedback using the chatbot using tools. When submitting
  feedback to Tyson extract user's message verbatim and do not rephrase it.

## How to buy
If the user wants to buy a product then they have two options. 
1. through distributor (preferred option)
2. reaching out to tysons sales representative by filling a form
If the user has not already indicated their preference then present these two
options. 
When the user asks for ordering information you do not need to retrieve all the
product details again, only specify the title of the product and be concise with
the details.

### Order through distributor
If they user is interested in buying through a distributor then let them
identify their preferred distributor and then for a specific product or products
they have identified provide the ordering link obtained through the user of
appropriate tool. Also help them check if a product is available with their
distributor.

### Find a tyson Sales Rep
If the user is not interested in a purchasing through a distributor then direct
them to submit a form through this link which will submit their information to a
sales team and someone will reach out to them. Here is the link to the form
https://www.tysonfoodservice.com/connect/find-a-sales-rep 

Current date (YYYY-MM-DD): """ + date.today().strftime("%Y-%m-%d") + "\n" 
```

## Capturing high-value actions: Turning conversations into insights

In designing Tyson Foodservice’s AI assistant, we implemented an innovative solution for capturing high-value actions that transforms customer interactions into strategic business intelligence. This capability provides deeper contextual understanding of customer interests and needs than traditional web analytics. Whereas conventional analytics tools track user behavior through page views, clicks, and time-on-site metrics, our solution uses the rich conversational data generated through natural dialogue. This provides Tyson with unprecedented visibility into customer interests, pain points, and purchase intentions.

The system identifies and logs specific high-value interactions whenever users request detailed product information, inquire about specific product categories, ask about preparation methods or recipe ideas, seek distributor information in their region, or express interest in bulk purchasing or promotions. This approach creates a powerful feedback loop for Tyson Foodservice. As customers naturally express their needs and interests through conversation, the system captures these signals in an aggregate, privacy-respecting manner. Tyson can use these insights to identify trending product categories and potential gaps in their portfolio, understand regional variations in customer interests, recognize seasonal patterns in product inquiries, refine marketing strategies based on direct customer language, and improve inventory management through better demand forecasting. The technical implementation uses the tool-calling capabilities of Anthropic’s Claude 3.5 Sonnet in a straightforward but effective way. Rather than analyzing chat logs after the fact, we integrated the capture mechanism directly into the AI assistant’s operational workflow through LangGraph, allowing for real-time insight collection during customer interactions. When the LLM invokes certain tools to retrieve information requested by users, these tool calls simultaneously trigger the capture of high-value action data. We’ve designed a configurable system where specific tools are designated as high-value action triggers that record meaningful interactions while fulfilling the user’s immediate request.This dual-purpose approach makes sure that valuable business intelligence is gathered as a natural byproduct of providing excellent customer service, without requiring additional processing or analysis steps. The system includes configurable parameters that allow Tyson to adjust which user intents and actions qualify as high value based on evolving business priorities. By transforming every customer conversation into structured, actionable data, Tyson Foodservice can now measure customer interest with unprecedented precision while delivering a superior search experience that feels natural to users.

## Conclusion

In this post, we demonstrated a powerful approach to implementing natural conversational AI assistants that seamlessly integrate with existing website functionalities and provide intuitive language interactions for users. By using Amazon Bedrock FMs and OpenSearch Serverless, businesses can quickly expose their website’s capabilities through conversation rather than complex interfaces. The high-value action capture mechanism further enhances this solution by gathering valuable customer insights directly from natural interactions, creating a rich source of business intelligence without additional user friction. This framework provides a flexible blueprint for implementing AI-powered assistants across retail and CPG websites. Organizations can adapt this approach to their specific needs, such as product discovery, customer support, or personalized recommendations. The combination of semantic search with conversational AI creates experiences that understand user intent while maintaining the context necessary for natural dialogue.

If you’re interested in building a similar AI assistant that orchestrates multiple tools, you can get started with [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/), a fully managed AWS solution designed specifically for this purpose. Amazon Bedrock Agents simplifies the process of creating, testing, and deploying conversational experiences that can execute complex tasks across your business systems. With the right architecture and implementation approach demonstrated in this post, you can develop AI-powered interactions that deliver measurable business value while significantly enhancing your customer journey.

For developers exploring AI agent frameworks today, AWS recently introduced [Strands Agents](https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/), an open source SDK that takes a model-driven approach to building agents with just a model, tools, and a prompt. Unlike workflow-based frameworks, Strands adopts a model-first philosophy that uses advanced reasoning capabilities, offering an interesting alternative approach to frameworks like LangGraph.

Try out these solutions for your own use case, and share your feedback in the comments.

### About the authors

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/05/anveshi.jpeg) Anveshi Charuvaka **is a Senior Applied Scientist at AWS’s Generative AI Innovation Center, where he partners with customers to turn Generative AI into solutions for mission-critical business problems. He holds a PhD in Machine Learning and brings over 10 years of experience applying innovative ML and GenAI techniques to complex, real-world challenges.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/05/barret.jpg)**Barret Miller** leads the Digital Enterprise Organization at Tyson Foods, where he spearheads progress in emerging technologies, artificial intelligence, and Smart Office initiatives. With more than 17 years of expertise in software development, data, analytics, and AI, Barret excels at leveraging innovative technology paradigms, including Agentic AI, to tackle and enhance complex business processes.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/05/vincil.png) **Vincil Bishop** is a Senior Deep Learning Architect in the Generative AI Innovation Center. Vincil has 25 years of experience in the IT industry and holds a PhD in Systems Engineering from Colorado State University. Vincil specializes in the design and implementation of AI solutions that help solve customers’ toughest business challenges.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/05/tes.png) **Tesfagabir Meharizghi** is an Applied Scientist at the AWS Generative AI Innovation Center, where he leads projects and collaborates with enterprise customers across various industries to leverage cutting-edge generative AI technologies in solving complex business challenges. He specializes in identifying and prioritizing high-impact use cases, developing scalable AI solutions, and fostering knowledge-sharing partnerships with stakeholders.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/05/tanay.png) **Tanay Chowdhury** is a Data Scientist at Generative AI Innovation Center at Amazon Web Services who helps customers solve their business problems using generative AI and machine learning. He has done MS with Thesis in Machine Learning from University of Illinois and has extensive experience in solving customer problem in the field of data science.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/05/angona.jpg) **Angel Goni** is a Principal Solutions Architect at AWS with 15+ years of IT experience across the Financial Services, Retail, and Consumer Packaged Goods sectors. Angel specializes in utilizing cloud technology to impact business KPIs, with particular expertise in multicloud strategies, SAP migrations, and supply chain improvement.
