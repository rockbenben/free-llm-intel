---
vendor: aws_bedrock
title: Tyson Foods elevates customer search experience with an AI-powered conversational assistant
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/tyson-foods-elevates-customer-search-experience-with-an-ai-powered-conversational-assistant
date: 2025-08-20
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 7816de43d471
---

# Tyson Foods 借助 AI 驱动的对话式助手提升客户搜索体验

[Tyson Foodservice](https://www.tysonfoodservice.com/) 是 [Tyson Foods Inc.](https://www.tysonfoods.com/) 旗下关键的食品服务部门，凭借其强大的蛋白质生产能力，为多个行业领域的各类食品服务客户供货。作为美国最大的蛋白质供应商之一，Tyson Foods 生产了全美约 20% 的牛肉、猪肉和鸡肉，这构成了其食品服务业务的基础。

Tyson Foodservice 采用 B2B 模式运营，把产品卖给分销商而非直接面向最终消费者，同时服务餐厅、学校、医疗机构和便利店等各类食品服务运营商。直到最近，Tyson 与超过 100 万家无人跟进的运营商（他们通过分销商购买产品，与公司没有直接关系）的直接互动仍然有限。为弥合这一差距，Tyson 在其网站上上线了一个生成式 AI 助手，从而能够扩大销售力度、收集客户洞察并建立直接沟通渠道。公司的网站如今成为一个关键界面：运营商可以在这里浏览产品、了解菜单趋势，并发现针对其特定食品服务细分领域的定制方案——这些体验都由 AI 驱动的个性化能力增强，既能更好地服务现有客户，也能服务此前无人跟进的运营商。

本文介绍 Tyson Foods 如何与 [AWS Generative AI Innovation Center](https://aws.amazon.com/ai/generative-ai/innovation-center/) 合作，通过一个[集成到其网站](https://www.tysonfoodservice.com/)中的直观 AI 助手彻底改变客户互动方式。该 AI 助手基于 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 构建，这是一项完全托管的服务，通过单一 API 提供来自 AI21 Labs、Anthropic、Cohere、Meta、Mistral AI、Stability AI 和 Amazon 等领先 AI 公司的高性能基础模型（FM）选择，并提供一整套用于构建生成式 AI 应用的能力，兼顾安全、隐私和负责任 AI。

![Tyson FoodService AI 聊天助手界面](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/01/tyson-bp-image-1.jpeg)

## 解决方案概览

本节介绍该解决方案的整体架构。工作流包含以下高层步骤：

- 用户在 [https://www.tysonfoodservice.com/](https://www.tysonfoodservice.com/) 的搜索栏中进行搜索。查询字符串使用 Amazon Bedrock 和 [Amazon Titan Text Embeddings 模型](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html) 转换为 embedding。搜索应用在 [Amazon OpenSearch Serverless](https://aws.amazon.com/opensearch-service/features/serverless/) 中执行 k 近邻（k-NN）向量搜索以找到相关结果，并将这些结果返回给网站。搜索应用部署在 [Amazon Elastic Container Service](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html)（Amazon ECS）中，以 [AWS Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html) 作为容量提供程序，并通过受 [AWS WAF](https://aws.amazon.com/waf/) 保护的 [Application Load Balancer](https://aws.amazon.com/elasticloadbalancing/application-load-balancer/) 以 REST API 形式对外暴露。
- 用户通过 AI 助手界面用自然语言提问。查询由 agent 节点使用 Amazon Bedrock 上的 [Anthropic 的 Claude 3.5 Sonnet](https://aws.amazon.com/bedrock/claude/) 处理。根据查询主题的不同，agent 可能会编排多个 agent 来向用户返回相关信息。该应用的部署架构与语义搜索组件类似，只是额外增加了 [Amazon Relational Database Service](https://aws.amazon.com/rds/)（Amazon RDS）数据库集群，用于持久化用户的高价值操作以便分析。
- 产品、食谱、食材及其他相关数据以 JSON 格式从外部来源获取。这些数据使用 Amazon Bedrock 和 Amazon Titan Text Embeddings 模型处理，生成语义搜索 embedding，然后被摄取到 OpenSearch Serverless 中。摄取流程运行在另一个 ECS 集群中，同样以 Fargate 作为容量提供程序。

下图展示了这一架构。

![Tyson FoodService AI 助手架构](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/01/tyson-bp-image-2.png)

接下来的章节将更详细地讨论该解决方案的关键组件和收益。

## 改进的语义搜索

Tyson Foodservice 网站早期版本的搜索依赖基于关键词的检索。在 Tyson Foodservice 这样的 CPG 网站上，当客户使用与官方目录描述不同的行业术语搜索产品时，传统的基于关键词的搜索往往会失灵。厨师搜索“pulled chicken”时可能会漏掉标注为“shredded chicken”的相关产品，或者想找“wings”的人可能看不到“party wings”或“drummettes”的结果。这种落差让需要在紧迫期限内拿到特定食材的食品服务专业人士感到挫败，最终把他们推向能更快找到所需产品的竞争对手，使 Tyson 错失收入机会。语义搜索通过理解烹饪术语、备制方式和产品应用之间的概念关联，改变了这种体验。搜索“buffalo-style appetizers”的厨师会得到鸡翅、无骨鸡块及类似产品，而不必依赖精确的关键词匹配。通过识别菜单趋势、烹饪技法和专业厨房术语，语义搜索帮助食品服务运营商快速找到满足其确切运营需求的 Tyson 产品，即便他们使用的语言与目录描述不同。

Tyson Foodservice 使用 OpenSearch Serverless 实现了语义搜索能力，这项完全托管的服务把维护搜索基础设施的运维复杂度降到最低。该解决方案会自动伸缩计算和存储资源，以匹配查询量和产品目录规模，无需专门的管理开销。Serverless 架构帮助 Tyson 在整个产品数据库上快速部署先进的自然语言处理能力，同时保持成本效益，因为他们只需为实际使用的资源付费。借助 OpenSearch Serverless，Tyson 引入了向量 embedding 和强大的查询能力，能够理解食品服务术语的各种变体、备制方式和烹饪应用，改变了运营商发现符合其特定需求的产品的方式——即使他们的搜索词与目录描述并不完全匹配。

为索引 Tyson 由产品、食谱和文章组成的多样化内容库，我们实现了一套预处理工作流，把原始元数据转化为优化后的语义搜索查询。我们使用大语言模型（LLM）分析并只抽取每篇内容中最相关的要素，生成专为语义索引设计的、有意义的搜索字符串。这一做法确保纯展示性的网站文案和非必要的信息性文本被过滤掉，而烹饪应用、备制方式、配料规格等对搜索至关重要的要素在索引中得到恰当强调。通过筛选哪些内容被索引，而不是把所有内容原样纳入，我们大幅提升了搜索相关性并减少了索引膨胀，使 OpenSearch Serverless 返回更精确、真正契合厨师和运营商查询意图的结果。为了把文本索引为语义向量，我们使用了 Amazon Bedrock 上的 Amazon Titan Text Embeddings V2。

下面的示例 prompt 展示了仅使用标题、描述和购买理由（reasons to buy）元数据时的转换过程。这套通用策略可以根据客户的具体需求进行定制。

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

## 使用 Amazon Bedrock 上的 Anthropic Claude 3.5 Sonnet 与 LangGraph 构建的 agentic 聊天

Tyson Foodservice 把强大的生成式 AI 助手集成到了其网站中，使用 Amazon Bedrock 上的 Anthropic Claude 3.5 Sonnet 和 [LangGraph](https://www.langchain.com/langgraph)。这个 AI 助手带来无缝的对话式搜索体验，在 Tyson 广泛的产品、食谱和文章范围内提供全面支持，并通过自然对话提供上下文相关的引导。其能力包括：

- **个性化搜索** – 使用语义搜索查找相关产品、食谱和文章。AI 助手通过学习用户的业务和角色来定制推荐，打造贴合个人需求的体验，同时为 Tyson 收集有价值的客户洞察。
- **详细的产品信息** – 提供 Tyson 特定产品的完整细节，包括描述、配料、备制方法和建议的用法。
- **分销商服务** – 帮助用户查找附近的分销商，并查看其所在地区的产品供应情况。
- **采购协助** – 提供如何购买 Tyson 产品的信息，并在需要时把客户与销售代表对接。
- **促销信息** – 让客户及时了解 Tyson Foodservice 当前的促销和特别优惠。
- **反馈渠道** – 为客户提供简洁的方式，直接向 Tyson 提交产品和服务反馈。
- **自然的对话流程** – 在整个交互过程中保持上下文，让用户可以引用之前的结果并提出后续问题，获得更像真人的对话体验。

下图展示了 AI 助手的高层架构。系统使用 Anthropic Claude 的工具调用能力来实现 AI 助手的 agentic 行为。我们使用 LangGraph 简化实现过程，因为它提供了一些专为使用 LLM 构建 agentic 系统而设计的便捷原语。

![Tyson Food Services agentic 聊天的工具调用](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/01/tyson-bp-image-3.jpeg)

该架构的主要组件包括：

- **Agent 节点** – agent 节点通过一个大型 prompt 实现，它直接接收用户消息，并利用 LLM 的对话能力进行响应。它还通过工具调用能力来定义 agentic 行为：只要响应用户请求需要调用工具，agent 节点就会发出工具请求。
- **工具执行节点** – 该节点实现了一个通用的工具执行器，用于连接各种工具。每当 agent 节点发出工具调用，该节点就负责执行这次工具调用。工具调用节点执行这些以 Python 函数形式定义的工具，并把结果返回给 agent 节点，由其转换或总结后呈现给用户。LangGraph 提供了 [ToolNode](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/) 的通用实现，也可以扩展它来实现额外功能。
- **工具层** – 工具以简单的程序化函数实现，接收输入并返回输出。这些工具通过检索数据或提交反馈等功能来增强 LLM 的能力。工具是无状态的，与用户和 agent 之间的当前对话无关。LLM agent 会抽取执行这些工具所需的输入参数。在我们的实现中，这些工具是对实现实际功能的服务和数据库层的轻量封装。

下面的 system prompt 为实现 agent 节点提供了总体指导：

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

## 捕获高价值操作：把对话转化为洞察

在设计 Tyson Foodservice 的 AI 助手时，我们实现了一套用于捕获高价值操作的创新方案，把客户互动转化为具有战略价值的商业智能。这一能力比传统网站分析能更深入地理解客户的兴趣和需求所处的语境。传统分析工具通过页面浏览量、点击和页面停留时间等指标跟踪用户行为，而我们的方案利用自然对话产生的丰富会话数据，为 Tyson 提供了前所未有的可见性，洞悉客户的兴趣、痛点和购买意向。

当用户请求详细的产品信息、询问特定产品品类、咨询备制方法或食谱创意、寻找所在地区的分销商信息，或表达对批量采购或促销的兴趣时，系统会识别并记录这些具体的高价值交互。这种做法为 Tyson Foodservice 打造了一个强大的反馈闭环。客户在对话中自然地表达需求与兴趣，系统则以聚合的、尊重隐私的方式捕获这些信号。Tyson 可以利用这些洞察来识别热门产品品类和产品组合中的潜在缺口、理解客户兴趣的区域差异、识别产品咨询的季节性规律、根据客户的直接表述优化营销策略，并通过更好的需求预测改善库存管理。技术实现以直接而有效的方式使用了 Anthropic Claude 3.5 Sonnet 的工具调用能力。我们不是事后分析聊天日志，而是通过 LangGraph 把捕获机制直接集成到 AI 助手的运行工作流中，从而在客户交互过程中实时收集洞察。当 LLM 调用某些工具来检索用户请求的信息时，这些工具调用会同时触发高价值操作数据的捕获。我们设计了一套可配置的系统，把特定工具指定为高价值操作触发器，在满足用户即时请求的同时记录有意义的交互。这种双重用途的做法确保有价值的商业智能成为提供优质客户服务的自然副产品，而不需要额外的处理或分析步骤。系统包含可配置的参数，让 Tyson 可以依据不断变化的业务优先级调整哪些用户意图和操作算作高价值。通过把每一次客户对话转化为结构化、可操作的数据，Tyson Foodservice 如今能够以前所未有的精确度衡量客户兴趣，同时提供对用户而言自然流畅的优质搜索体验。

## 结论

本文展示了一种强有力的方法，用于实现能自然对话的 AI 助手，使其与现有网站功能无缝集成，并为用户提供直观的语言交互。通过使用 Amazon Bedrock 的 FM 和 OpenSearch Serverless，企业可以借助对话而非复杂界面快速开放网站能力。高价值操作捕获机制直接从自然交互中收集宝贵的客户洞察，无需额外的用户摩擦便能形成丰富的商业智能来源，进一步增强了这一方案。该框架为在零售和 CPG 网站实现 AI 驱动的助手提供了灵活的蓝图。组织可以根据自身需求（例如产品发现、客户支持或个性化推荐）调整这一做法。语义搜索与对话式 AI 的结合，创造出既能理解用户意图、又能保持自然对话所需上下文的体验。

如果你有兴趣构建类似的、能编排多个工具的 AI 助手，可以从 [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) 开始，这是 AWS 专为此目的设计的完全托管解决方案。Amazon Bedrock Agents 简化了创建、测试和部署对话式体验的过程，这些体验可以跨业务系统执行复杂任务。借助本文展示的合理架构和实现方法，你可以开发出带来可衡量业务价值、同时显著改善客户旅程的 AI 驱动交互。

对于如今正在探索 AI agent 框架的开发者，AWS 最近推出了 [Strands Agents](https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/)，这是一个开源 SDK，采用模型驱动的方式，只需一个模型、一些工具和一段 prompt 就能构建 agent。与基于工作流的框架不同，Strands 秉持模型优先的理念，利用先进的推理能力，为 LangGraph 这类框架提供了一种有趣的替代方案。

不妨针对你自己的用例试用这些方案，并在评论区分享你的反馈。

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/05/anveshi.jpeg) Anveshi Charuvaka** 是 AWS Generative AI Innovation Center 的资深应用科学家，他与客户合作，把生成式 AI 转化为解决关键业务问题的方案。他拥有机器学习博士学位，在把创新的 ML 和生成式 AI 技术应用于复杂的现实挑战方面拥有 10 多年的经验。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/05/barret.jpg)**Barret Miller** 领导 Tyson Foods 的数字企业组织，推动新兴技术、人工智能和 Smart Office 举措的进展。他在软件开发、数据、分析和 AI 方面拥有 17 年以上的专业经验，擅长运用包括 Agentic AI 在内的创新技术范式来应对和改进复杂的业务流程。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/05/vincil.png) **Vincil Bishop** 是 Generative AI Innovation Center 的资深深度学习架构师。Vincil 在 IT 行业拥有 25 年经验，并拥有科罗拉多州立大学的系统工程博士学位。他专长于设计和实施 AI 解决方案，帮助客户解决最棘手的业务挑战。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/05/tes.png) **Tesfagabir Meharizghi** 是 AWS Generative AI Innovation Center 的应用科学家，在那里他领导项目，并与各行业的企业客户协作，利用前沿生成式 AI 技术解决复杂的业务挑战。他擅长识别并优先处理高影响力用例、开发可扩展的 AI 解决方案，并与利益相关方建立知识共享伙伴关系。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/05/tanay.png) **Tanay Chowdhury** 是 Amazon Web Services Generative AI Innovation Center 的数据科学家，帮助客户利用生成式 AI 和机器学习解决业务问题。他拥有伊利诺伊大学机器学习方向的硕士学位（含论文），在数据科学领域解决客户问题方面经验丰富。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/05/angona.jpg) **Angel Goni** 是 AWS 的首席解决方案架构师，在金融服务、零售和消费品行业拥有 15 年以上的 IT 经验。Angel 擅长利用云技术影响业务 KPI，尤其精通多云策略、SAP 迁移和供应链改进。
