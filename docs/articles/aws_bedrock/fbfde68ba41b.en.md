---
vendor: aws_bedrock
title: NewDay builds A Generative AI based Customer service Agent Assist with over 90% accuracy
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/newday-builds-a-generative-ai-based-customer-service-agent-assist-with-over-90-accuracy
date: 2025-06-24
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: f7f372686f0b
---

# NewDay builds A Generative AI based Customer service Agent Assist with over 90% accuracy

*This post is co-written with Sergio Zavota and Amy Perring from NewDay.*

[NewDay](https://www.newday.co.uk/) has a clear and defining purpose: to help people move forward with credit. NewDay provides around 4 million customers access to credit responsibly and delivers exceptional customer experiences, powered by their in-house technology system. NewDay’s contact center handles 2.5 million calls annually, so having the right technology to empower their customer service agents to have effective conversations with customers is paramount to deliver great customer experience.

The role of the contact center is complex, and with nearly 200 knowledge articles in Customer Services alone, there are times where an agent needs to search the right answer for a customer question from these articles. This led to a hackathon problem statement in early 2024 for NewDay: how can they harness the power of generative AI to improve the speed to resolution, improving both the customer and agent experience.

The hackathon event led to the creation of NewAssist—a real-time generative AI assistant designed to empower customer service agents with speech-to-text capabilities. Built on [Amazon Bedrock](https://aws.amazon.com/bedrock/?gclid=EAIaIQobChMIptmIuvijjAMVzhWtBh1HJCgLEAAYASAAEgIh6_D_BwE&trk=0eaabb80-ee46-4e73-94ae-368ffb759b62&sc_channel=ps&ef_id=EAIaIQobChMIptmIuvijjAMVzhWtBh1HJCgLEAAYASAAEgIh6_D_BwE:G:s&s_kwcid=AL!4422!3!692006004688!p!!g!!amazon%20bedrock!21048268554!159639952935), NewAssist would deliver rapid, context-aware support during live interactions with customers.

In this post, we share how NewDay turned their hackathon idea into a a successful Generative AI based solution and their learnings during this journey

## Inception and early challenges

NewAssist won the hackathon event by showcasing the potential generative AI could deliver on speed of call resolution. However, despite a positive start, the team faced significant hurdles:

- **Managing costs and competing priorities –** Amid large strategic initiatives and limited resources, the team remained focused and proactive, even as securing executive buy-in proved challenging
- **Lack of infrastructure –** The existing legacy systems were not conducive to rapid experimentation
- **Unproven technology –** The NewAssist team needed to prove the investment would truly add value back to the business

Realizing their ambitions of a fully fledged voice assistant were too ambitious given the challenges, the team made a strategic pivot. They scaled back to a chatbot solution, concentrating on standing up a proof of concept to validate that their existing knowledge management solution would work effectively with generative AI technology. The NewDay contact center team’s goal is to use one source of truth for its future generative AI solutions, so this task was crucial in setting the right foundation for a solid long-term strategy.With an agile, step-by-step approach, a small cross-functional team of three experts set out to build the proof of concept with a target of 80% accuracy. A golden dataset of over 100 questions and correct answers for these questions was created and the generative AI application was tested with this dataset to evaluate its accuracy of responses.

## Solution overview

NewAssist’s technical design and implementation were executed by following these principles:

- **Embrace a culture of experimentation** **–** A small cross-functional team of three people was formed. The team followed the [Improvement Kata](https://public.websites.umich.edu/~jmondisa/TK/Handbook/Full_IK_Handbook_v32.0.pdf) methodology to implement rapid Build-Measure-Learn cycles. In just 10 weeks and over 8 experiment loops, the team honed the solution. Early iterations saw accuracy below 60%, but through rigorous testing and smart data strategies, they boosted performance to over 80%, a 33% improvement in just a few weeks.
- **Adopt a serverless Infrastructure** **–** [Amazon Bedrock](https://aws.amazon.com/bedrock/), [AWS Fargate](https://aws.amazon.com/fargate/), [AWS Lambda](https://aws.amazon.com/pm/lambda/?gclid=Cj0KCQjwhYS_BhD2ARIsAJTMMQbJI73vM8jqZQpj-unBFHpqG1XSWnWcCpeTN6pLuCeotwd8WhVGVxgaAnyXEALw_wcB&trk=27324d1f-ee08-40b9-8e7b-5ac228e2fecc&sc_channel=ps&ef_id=Cj0KCQjwhYS_BhD2ARIsAJTMMQbJI73vM8jqZQpj-unBFHpqG1XSWnWcCpeTN6pLuCeotwd8WhVGVxgaAnyXEALw_wcB:G:s&s_kwcid=AL!4422!3!651612449951!e!!g!!aws%20lambda!19836376234!148728884764), [Amazon API Gateway](https://aws.amazon.com/api-gateway/), and [Amazon OpenSearch Serverless](https://aws.amazon.com/opensearch-service/features/serverless/) formed the backbone of the application. This approach not only reduced costs (with running cost kept under $400 per month), but also made sure the system could scale in response to real-time demand. In addition, this allowed the developer of the team to focus only on activities that would validate the result of the experiments without worrying about managing infrastructure.

NewAssist is implemented as a [Retrieval Augmented Generation](https://aws.amazon.com/what-is/retrieval-augmented-generation/) (RAG) solution. The following diagram shows the high-level solution architecture.

[![NewAssist Architecture with Cognito, Lambda and Amazon Bedrock](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/ML-18185-arch-diag.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/ML-18185-arch-diag.png)

The high-level architecture is made up of five components:

- **User interface – **A simple AI assistant UI is built using the [Streamlit](https://streamlit.io/) framework. Users can log in, ask questions, give feedback to answers in the form of thumbs up and thumbs down, and optionally provide a comment to explain the reason for the bad feedback. The UI is hosted using Fargate and authentication is implemented through [Amazon Cognito](https://aws.amazon.com/cognito/) with [Microsoft Entra ID](https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id) integration to provide single sign-on (SSO) capabilities to customer service agents.
- **Knowledge base processing – **This component mostly drove the 40% increase in accuracy. Here, articles are retrieved by using APIs from the third-party knowledge base and chunked with a defined chunking strategy. The chunks are processed to convert to vector embeddings and finally stored in the vector database implemented using OpenSearch Serverless.
- **Suggestion generation – **Questions on the UI are forwarded to the suggestion generation component, which retrieves the most relevant chunks and passess these chunks to the large language model (LLM) for generating suggestions based on the context. [Anthropic’s Claude 3 Haiku](https://www.anthropic.com/news/claude-3-haiku) was the preferred LLM and was accessed through Amazon Bedrock. Anthropic’s Claude 3 Haiku is still used at the time of writing, even though more performant models have been released. There are two reasons for this: first, it’s the most cost-effective model accessible through Amazon Bedrock that provides satisfying results; second, NewDay has a response time requirement of a maximum of 5 seconds, which Anthropic’s Claude 3 Haiku satisfies. To achieve required accuracy, NewDay experimented with different chunking strategies and retrieval configurations while maintaining cost with Anthropic Claude 3 Haiku.
- **Observability – **Questions and answers with feedback are logged into [Snowflake](https://www.snowflake.com/en/uk/). A dashboard is created on top of it to show different metrics, such as accuracy. Every week, business experts review the answers with bad feedback, and AI engineers translate them into experiments that, if successful, increase the solution’s performance. Additionally, [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) logs the requests that the AWS services described in the architecture process.
- **Offline evaluation **– When a new version of NewAssist is created during the experimentation cycles, it is first evaluated in pre-production against an evaluation dataset. If the version’s accuracy surpasses a specified threshold, then it can be deployed in production.

## Understand your data and invest in a robust data processing solution

The one experiment that had the biggest impact on the accuracy of NewAssist, increasing it by 20%, was replacing the general-purpose data parser for knowledge articles with a custom-built version.This new parser was designed specifically to understand the structure and meaning of NewDay’s data, and by using this data, the LLM could generate more accurate outputs.Initially, the workflow that implements the data processing logic consisted of the following steps:

- Manually extract the articles from the data source and save them in PDF.
- Use [PyPDF](https://pypi.org/project/pypdf/) to parse the articles.

With this approach, the solution was performing at around 60% accuracy. The simple reason was that the logic didn’t take into account the type of data that was being processed, providing below-average results. Things changed when NewDay started studying their data.In NewDay, knowledge articles for agents are created by a team of experts in the contact center area. They create articles using a specific methodology and store them in a third-party content management system. This system in particular allows the creation of articles through widgets. For example, lists, banners, and tables.In addition, the system provides APIs that can be used to retrieve articles. The articles are returned in the form of a JSON object, where each object contains a widget. There is a limited number of widgets available, and each one of them has a specific JSON schema.Given this discovery, the team studied each single widget schema and created a bespoke parsing logic that extracts the relevant content and formats it in a polished way.It took longer than simply parsing with PyPDF, but the results were positive. Just focusing on the data and without touching the AI component, the solution’s accuracy increased from 60% to 73%. This demonstrated that data quality plays a key role in developing an effective generative AI application.

## Understand how your users use the solution

With the 80% accuracy milestone, the team proved that the proof of concept could work, so they obtained approval to expand experimentation to 10 customer service agents after just 3 months. NewDay selected 10 experienced agents because they needed to identify where the solution gave an incorrect response.As soon as NewAssist was handed over to customer service agents, something unexpected happened. Agents used NewAssist differently from what the NewDay technical team expected: they used various acronyms in their questions to NewAssist. As an example, consider the following questions:

- How do I set a direct debit for a customer?
- How do I set a dd for a cst?

Here, direct debit is abbreviated with “dd” and customer with “cst.” Unless this information is provided in the context, the LLM will struggle to provide the right answer. As a result, NewAssist’s accuracy dropped to 70% when agents started using it.The solution NewDay adopted was to statically inject the acronyms and abbreviations in the LLM prompt so it could better understand the question. Slowly, the accuracy recovered to over 80% . This is just a simple example that demonstrates how important it is to put a product in the hands of the final users to validate the assumptions.Another positive finding discovered was that agents would use NewAssist to understand how to explain a process to a customer. As we know, it’s difficult to translate technical content into a format that non-technical people understand. Agents started to ask NewAssist questions like: “How do I explain to a customer how to unlock their account?” with the outcome of producing a great answer they could just read to customers.

## Scaling up for greater impact

By expanding NewDay’s experimentation to 10 agents, NewDay was able to test many different scenarios. Negative responses were reviewed and root cause analysis conducted. The NewAssist team identified several gaps in the knowledge base, which they solved with new and improved content. They made enhancements to the solution by training it on acronyms and internal language. Additionally, they provided training and feedback to the pilot team on how to effectively use the solution.By doing this, the NewAssist Team improved the accuracy to over 90% and gained approval from NewDay’s executive team to productionize the solution. NewDay is currently rolling out the solution to over 150 agents, with plans to expand the scope of the solution to all departments within Customer Operations (such as Fraud and Collections).Early results indicate a substantial reduction in the time it takes to retireve an answer to queries being raised by agents. Previously, it would take them on average 90 seconds to retrieve an answer; the solution now retrieves an answer in 4 seconds.

## Learnings to build a production-ready generative AI application

NewDay acquired the following insights by deploying a production-ready generative AI application:

- **Embrace a culture of experimentation** **– This includes the following strategies:**  Adopt an agile, iterative approach to rapidly test hypotheses and improve the solution Implement methodologies like the Improvement Kata and Build-Measure-Learn cycles to achieve significant gains in short time frames Start small with a focused proof of concept and gradually scale to validate effectiveness before full deployment
- **Focus on data quality** **–** Invest time in understanding and properly processing your data, because this can yield substantial improvements
- **Understand how your users interact with the product** **– This includes the following steps:**  Conduct real-world testing with actual users to uncover unexpected usage patterns and behaviors Be prepared to adapt your solution based on user insights, such as accommodating internal jargon or abbreviations Look for unforeseen use cases that might emerge during user testing, because these can provide valuable directions for feature development Balance AI capabilities with human expertise, recognizing the importance of oversight and training to facilitate optimal use of the technology.

## Looking ahead

NewAssist’s journey is far from over. Due to a robust feedback mechanism and the right level of oversight, the team will continue to deliver optimizations to improve the accuracy of the output further. Future iterations will explore deeper integrations with AWS AI services, further refining the balance between human and machine intelligence in customer interactions.By adopting AWS serverless solutions and adopting an agile, data-driven approach, NewDay turned a hackathon idea into a powerful tool that has optimized customer services. The success of NewAssist is a testament to the innovation possible when creativity meets robust cloud infrastructure, setting the stage for the next wave of advancements in contact center technology.

## Conclusion

NewAssist’s journey demonstrates the power of AWS in enabling rapid experimentation and deployment of RAG solutions. For organizations looking to enhance customer service, streamline operations, or unlock new insights from data, AWS provides the tools and infrastructure to drive innovation, in addition to numerous other opportunities:

- **Accelerate RAG experiments** **–** Services like Amazon Bedrock, Lambda, and Amazon Serverless enable quick building and iteration of ideas
- **Scale with confidence** **–** AWS [serverless](https://aws.amazon.com/serverless/) offerings provide effective cost management while making sure solutions can grow with demand
- **Focus on data quality** **–** If data quality isn’t good enough at the source, you can implement data processing, cleansing, and extraction techniques to improve the accuracy of responses
- **Streamline deployment** **–** Fargate and API Gateway simplify the process of moving from proof of concept to production-ready applications
- **Optimize for performance** **–** [Cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html) and other AWS features help meet strict latency requirements while balancing cost considerations.

To learn more on how AWS can help you in your Generative AI Journey, visit : [Transform your business with generative AI](https://aws.amazon.com/ai/generative-ai/?trk=c30d9c04-dff1-48dd-85e1-551e986fbb60&sc_channel=ps&ef_id=Cj0KCQjw0qTCBhCmARIsAAj8C4bw3YeanT24ZgQMVnhHaz-aEf0ZlaiRhlBt2SAM3-O64F26TOyjIA4aAr9rEALw_wcB:G:s&s_kwcid=AL!4422!3!686122457182!e!!g!!amazon%20generative%20ai!20894978760!155960704734&gad_campaignid=20894978760&gbraid=0AAAAADjHtp_zSYqiHDZM4hgKjksmG3mYT&gclid=Cj0KCQjw0qTCBhCmARIsAAj8C4bw3YeanT24ZgQMVnhHaz-aEf0ZlaiRhlBt2SAM3-O64F26TOyjIA4aAr9rEALw_wcB).

### About the authors

**[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/DSC_3445.jpg)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/DSC_3445.jpg) Kaushal Goyal** is a Solutions Architect at AWS, working with Enterprise Financial Services in the UK and Ireland region. With a strong background in banking technology, Kaushal previously led digital transformation initiatives at major banks. At AWS, Kaushal helps financial institutions modernize legacy systems and implement cloud-native solutions. As a Generative AI enthusiast and Container Specialist, Kaushal focuses on bringing innovative AI solutions to enterprise customers and share the learnings through blogs, public speaking.

**[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/IMG_2370.jpg)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/IMG_2370.jpg)Sergio Zavota** is an AI Architect at NewDay, specializing in MLOps and Generative AI. Sergio designs scalable platforms to productionize machine learning workloads and enable Generative AI at scale in Newday. Sergio shares his expertise at industry conferences and workshops, focusing on how to productionise AI solutions and aligning AI with organisational goals.

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/Picture1-9.jpg)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/Picture1-9.jpg)**Amy Perring** is a Senior Optimisation Manager at NewDay, based in London. She specialises in building a deep understanding of contact drivers through customer and agent feedback. This helps identify optimisation opportunities to improve overall efficiency and experience, through the introduction or improvement of products and processes.

**[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2023/01/03/udemayur.jpg)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2023/01/03/udemayur.jpg)Mayur Udernani** leads AWS Generative AI & ML business with commercial enterprises in UK & Ireland. In his role, Mayur spends majority of his time with customers and partners to help create impactful solutions that solve the most pressing needs of a customer or for a wider industry leveraging AWS Cloud, Generative AI & ML services. Mayur lives in the London area. He has an MBA from Indian Institute of Management and Bachelors in Computer Engineering from Mumbai University.
