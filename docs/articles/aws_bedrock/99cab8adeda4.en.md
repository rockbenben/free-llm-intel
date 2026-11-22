---
vendor: aws_bedrock
title: Going beyond AI assistants: Examples from Amazon.com reinventing industries with generative AI
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/going-beyond-ai-assistants-examples-from-amazon-com-reinventing-industries-with-generative-ai
date: 2025-05-30
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: d7aa4838a2b3
---

# Going beyond AI assistants: Examples from Amazon.com reinventing industries with generative AI

[Generative AI](https://aws.amazon.com/generative-ai/) revolutionizes business operations through various applications, including conversational assistants such as Amazon’s [Rufus](https://www.aboutamazon.com/news/retail/amazon-rufus) and [Amazon Seller Assistant](https://www.aboutamazon.com/news/innovation-at-amazon/amazon-project-amelia). Additionally, some of the most impactful generative AI applications operate autonomously behind the scenes, an essential capability that empowers enterprises to transform their operations, data processing, and content creation at scale. These non-conversational implementations, often in the form of agentic workflows powered by [large language models (LLMs)](https://aws.amazon.com/what-is/large-language-model/), execute specific business objectives across industries without direct user interaction.

Non-conversational applications offer unique advantages such as higher latency tolerance, batch processing, and caching, but their autonomous nature requires stronger guardrails and exhaustive quality assurance compared to conversational applications, which benefit from real-time user feedback and supervision.

This post examines four diverse Amazon.com examples of such generative AI applications:

- [Amazon.com listing creation and catalog data quality improvements](https://www.aboutamazon.com/news/innovation-at-amazon/amazon-generative-ai-powered-product-listings) – Demonstrating how LLMs are helping selling partners and Amazon.com create higher-quality listings at scale
- [Prescription processing in Amazon Pharmacy](https://www.aboutamazon.com/news/retail/how-amazon-pharmacy-uses-generative-ai) – Showcasing implementation in a highly regulated environment and task decomposition for agentic workflows
- [Review highlights](https://www.aboutamazon.com/news/amazon-ai/amazon-improves-customer-reviews-with-generative-ai) – Illustrating massive scale batch processing, traditional [machine learning](https://aws.amazon.com/ai/machine-learning/) (ML) integration, use of smaller LLMs, and cost-effective solution at scale
- [Amazon Ads creative image and video generation](https://advertising.amazon.com/library/guides/how-to-use-ai-image-generators) – Highlighting multimodal generative AI and responsible AI practices in creative endeavors

Each case study reveals different aspects of implementing non-conversational generative AI applications, from technical architecture to operational considerations. Throughout these examples, you will learn how the comprehensive suite of AWS services, including [Amazon Bedrock](https://aws.amazon.com/bedrock/) and [Amazon SageMaker](https://aws.amazon.com/sagemaker/), are the key to success. Finally, we list key learnings commonly shared across these use cases.

## Creating high-quality product listings on Amazon.com

Creating high-quality product listings with comprehensive details helps customers make informed purchase decisions. Traditionally, selling partners manually entered dozens of attributes per product. The new generative AI solution, launched in 2024, transforms this process by proactively acquiring product information from brand websites and other sources to improve the customer experience across numerous product categories.

Generative AI simplifies the selling partner experience by enabling information input in various formats such as URLs, product images, or spreadsheets and automatically translating this into the required structure and format. Over 900,000 selling partners have used it, with nearly 80% of generated listing drafts accepted with minimal edits. AI-generated content provides comprehensive product details that help with clarity and accuracy, which can contribute to product discoverability in customer searches.

For new listings, the workflow begins with selling partners providing initial information. The system then generates comprehensive listings using multiple information sources, including titles, descriptions, and detailed attributes. Generated listings are shared with selling partners for approval or editing.

For existing listings, the system identifies products that can be enriched with additional data.

### Data integration and processing for a large variety of outputs

The Amazon team built robust connectors for internal and external sources with LLM-friendly APIs using Amazon Bedrock and other AWS services to seamlessly integrate into Amazon.com backend systems.

A key challenge is synthesizing diverse data into cohesive listings across more than 50 attributes, both textual and numerical. LLMs require specific control mechanisms and instructions to accurately interpret ecommerce concepts because they might not perform optimally with such complex, varied data. For example, LLMs might misinterpret “capacity” in a knife block as dimensions rather than number of slots, or mistake “Fit Wear” as a style description instead of a brand name. Prompt engineering and fine-tuning were extensively used to address these cases.

### Generation and validation with LLMs

The generated product listings should be complete and correct. To help this, the solution implements a multistep workflow using LLMs for both generation and validation of attributes. This dual-LLM approach helps prevent hallucinations, which is critical when dealing with safety hazards or technical specifications. The team developed advanced self-reflection techniques to make sure the generation and validation processes complement each other effectively.

The following figure illustrates the generation process with validation both performed by LLMs.

Figure 1. Product Listing creation workflow

### Multi-layer quality assurance with human feedback

Human feedback is central to the solution’s quality assurance. The process includes Amazon.com experts for initial evaluation and selling partner input for acceptance or edits. This provides high-quality output and enables ongoing enhancement of AI models.

The quality assurance process includes automated testing methods combining ML-, algorithm-, or LLM-based evaluations. Failed listings undergo regeneration, and successful listings proceed to further testing. Using [causal inference models](https://en.wikipedia.org/wiki/Causal_inference), we identify underlying features affecting listing performance and opportunities for enrichment. Ultimately, listings that pass quality checks and receive selling partner acceptance are published, making sure customers receive accurate and comprehensive product information.

The following figure illustrates the workflow of going to production with testing, evaluation, and monitoring of product listing generation.

Figure 2. Product Listing testing and human in the loop workflow

### Application-level system optimization for accuracy and cost

Given the high standards for accuracy and completeness, the team adopted a comprehensive experimentation approach with an automated optimization system. This system explores various combinations of LLMs, prompts, playbooks, workflows, and AI tools to iterate for higher business metrics, including cost. Through continuous evaluation and automated testing, the product listing generator effectively balances performance, cost, and efficiency while staying adaptable to new AI developments. This approach means customers benefit from high-quality product information, and selling partners have access to cutting-edge tools for creating listings efficiently.

## Generative AI-powered prescription processing in Amazon Pharmacy

Building upon the human-AI hybrid workflows previously discussed in the seller listing example, Amazon Pharmacy demonstrates how these principles can be applied in a [Health Insurance Portability and Accountability Act](https://aws.amazon.com/compliance/hipaa-compliance/) (HIPAA)-regulated industry. Having shared a conversational assistant for patient care specialists in the post [Learn how Amazon Pharmacy created their LLM-based chat-bot using Amazon SageMaker](https://aws.amazon.com/blogs/machine-learning/learn-how-amazon-pharmacy-created-their-llm-based-chat-bot-using-amazon-sagemaker/), we now focus on automated prescription processing, which you can read about in [The life of a prescription at Amazon Pharmacy](https://www.amazon.science/blog/the-life-of-a-prescription-at-amazon-pharmacy) and the following [research paper in Nature Magazine](https://www.nature.com/articles/s41591-024-02933-8).

At Amazon Pharmacy, we developed an AI system built on Amazon Bedrock and SageMaker to help pharmacy technicians process medication directions more accurately and efficiently. This solution integrates human experts with LLMs in creation and validation roles to enhance precision in medication instructions for our patients.

### Agentic workflow design for healthcare accuracy

The prescription processing system combines human expertise (data entry technicians and pharmacists) with AI support for direction suggestions and feedback. The workflow, shown in the following diagram, begins with a pharmacy knowledge-based preprocessor standardizing raw prescription text in [Amazon DynamoDB](https://aws.amazon.com/dynamodb/), followed by fine-tuned small language models (SLMs) on SageMaker identifying critical components (dosage, frequency).

| ![Data entry technician and pharmacist workflow with two GenAI modules](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/16/Picture3-blog17678-1.jpg)  (a) |  |
| --- | --- |
| ![Data entry technician and pharmacist workflow with two GenAI modules](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/16/Picture4-blog17678-1-645x1024.png)  (b) | ![Flagging module workflow](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/16/Picture5-blog17678-1-548x1024.png)  (c) |
| *Figure 3. (a) Data entry technician and pharmacist workflow with two GenAI modules, (b) Suggestion module workflow and (c) Flagging module workflow* |  |

The system seamlessly integrates experts such as data entry technicians and pharmacists, where generative AI complements the overall workflow towards agility and accuracy to better serve our patients. A direction assembly system with safety guardrails then generates instructions for data entry technicians to create their typed directions through the suggestion module. The flagging module flags or corrects errors and enforces further safety measures as feedback provided to the data entry technician. The technician finalizes highly accurate, safe-typed directions for pharmacists who can either provide feedback or execute the directions to the downstream service.

One highlight from the solution is the use of task decomposition, which empowers engineers and scientists to break the overall process into a multitude of steps with individual modules made of substeps. The team extensively used fine-tuned SLMs. In addition, the process employs traditional ML procedures such as [named entity recognition (NER)](https://docs.aws.amazon.com/sagemaker/latest/dg/sms-named-entity-recg.html) or estimation of final confidence with [regression models](https://en.wikipedia.org/wiki/Regression_analysis). Using SLMs and traditional ML in such contained, well-defined procedures significantly improved processing speed while maintaining rigorous safety standards due to incorporation of appropriate guardrails on specific steps.

The system comprises multiple well-defined substeps, with each subprocess operating as a specialized component working semi-autonomously yet collaboratively within the workflow toward the overall objective. This decomposed approach, with specific validations at each stage, proved more effective than end-to-end solutions while enabling the use of fine-tuned SLMs. The team used [AWS Fargate](https://aws.amazon.com/fargate/) to orchestrate the workflow given its current integration into existing backend systems.

In their product development journey, the team turned to Amazon Bedrock, which provided high-performing LLMs with ease-of-use features tailored to generative AI applications. SageMaker enabled further LLM selections, deeper customizability, and traditional ML methods. To learn more about this technique, see [How task decomposition and smaller LLMs can make AI more affordable](https://www.amazon.science/blog/how-task-decomposition-and-smaller-llms-can-make-ai-more-affordable) and read about the [Amazon Pharmacy business case study](https://aws.amazon.com/solutions/case-studies/amazon-pharmacy-improves-customer-care-case-study/).

### Building a reliable application with guardrails and HITL

To comply with HIPAA standards and provide patient privacy, we implemented strict data governance practices alongside a hybrid approach that combines fine-tuned LLMs using Amazon Bedrock APIs with [Retrieval Augmented Generation](https://aws.amazon.com/what-is/retrieval-augmented-generation/) (RAG) using [Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/). This combination enables efficient knowledge retrieval while maintaining high accuracy for specific subtasks.

Managing LLM hallucinations—which is critical in healthcare—required more than just fine-tuning on large datasets. Our solution implements domain-specific guardrails built on [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/), complemented by human-in-the-loop (HITL) oversight to promote system reliability.

The Amazon Pharmacy team continues to enhance this system through real-time pharmacist feedback and expanded prescription format capabilities. This balanced approach of innovation, domain expertise, advanced AI services, and human oversight not only improves operational efficiency, but means that the AI system properly augments healthcare professionals in delivering optimal patient care.

## Generative AI-powered customer review highlights

Whereas our previous example showcased how Amazon Pharmacy integrates LLMs into real-time workflows for prescription processing, this next use case demonstrates how similar techniques—SLMs, traditional ML, and thoughtful workflow design—can be applied to [offline batch inferencing](https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model.html) at massive scale.

Amazon has introduced [AI-generated customer review highlights](https://www.aboutamazon.com/news/retail/amazon-ai-generated-review-highlights) to process over 200 million annual product reviews and ratings. This feature distills shared customer opinions into concise paragraphs highlighting positive, neutral, and negative feedback about products and their features. Shoppers can quickly grasp consensus while maintaining transparency by providing access to related customer reviews and keeping original reviews available.

The system enhances shopping decisions through an interface where customers can explore review highlights by selecting specific features (such as picture quality, remote functionality, or ease of installation for a Fire TV). Features are visually coded with green check marks for positive sentiment, orange minus signs for negative, and gray for neutral—which means shoppers can quickly identify product strengths and weaknesses based on verified purchase reviews. The following screenshot shows review highlights regarding noise level for a product.

Figure 4. An example product review highlights for a product.

### A recipe for cost-effective use of LLMs for offline use cases

The team developed a cost-effective hybrid architecture combining traditional ML methods with specialized SLMs. This approach assigns sentiment analysis and keyword extraction to traditional ML while using optimized SLMs for complex text generation tasks, improving both accuracy and processing efficiency. The following diagram shows ttraditional ML and LLMs working to provide the overall workflow.

Figure 5. Use of traditional ML and LLMs in a workflow.

The feature employs [SageMaker batch transform](https://docs.aws.amazon.com/sagemaker/latest/dg/batch-transform.html) for asynchronous processing, significantly reducing costs compared to real-time endpoints. To deliver a near zero-latency experience, the solution [caches](https://aws.amazon.com/caching/aws-caching/) extracted insights alongside existing reviews, reducing wait times and enabling simultaneous access by multiple customers without additional computation. The system processes new reviews incrementally, updating insights without reprocessing the complete dataset. For optimal performance and cost-effectiveness, the feature uses [Amazon Elastic Compute Cloud](https://aws.amazon.com/ec2) (Amazon EC2) [Inf2 instances](https://aws.amazon.com/ec2/instance-types/inf2/) for batch transform jobs, [providing up to 40% better price-performance to alternatives](https://aws.amazon.com/ec2/instance-types/inf2/).

By following this comprehensive approach, the team effectively managed costs while handling the massive scale of reviews and products so that the solution remained both efficient and scalable.

## Amazon Ads AI-powered creative image and video generation

Having explored mostly text-centric generative AI applications in previous examples, we now turn to multimodal generative AI with [Amazon Ads creative content generation for sponsored ads](https://advertising.amazon.com/lp/grow-your-business-with-sponsored-ads). The solution has capabilities for [image](https://advertising.amazon.com/blog/ai-image-generation) and [video](https://www.aboutamazon.com/news/innovation-at-amazon/amazon-ads-generative-ai-video-generator-advertisers) generation, the details of which we share in this section. In common, this solution uses [Amazon Nova](https://aws.amazon.com/ai/generative-ai/nova/creative/) creative content generation models at its core.

Working backward from customer need, a March 2023 Amazon survey revealed that nearly 75% of advertisers struggling with campaign success cited creative content generation as their primary challenge. Many advertisers—particularly those without in-house capabilities or agency support—face significant barriers due to the expertise and costs of producing quality visuals. The Amazon Ads solution democratizes visual content creation, making it accessible and efficient for advertisers of different sizes. The impact has been substantial: advertisers using AI-generated images in [Sponsored Brands](https://advertising.amazon.com/solutions/products/sponsored-brands) campaigns saw nearly 8% [click-through rates (CTR)](https://en.wikipedia.org/wiki/Click-through_rate) and submitted 88% more campaigns than non-users.

Last year, the AWS Machine Learning Blog published a post [detailing the image generation solution](https://aws.amazon.com/blogs/machine-learning/learn-how-amazon-ads-created-a-generative-ai-powered-image-generation-capability-using-amazon-sagemaker/). Since then, Amazon has adopted [Amazon Nova Canvas](https://aws.amazon.com/ai/generative-ai/nova/creative/) as its foundation for creative image generation, creating professional-grade images from text or image prompts with features for text-based editing and controls for color scheme and layout adjustments.

In September 2024, the Amazon Ads team included the creation of [short-form video ads](https://www.aboutamazon.com/news/innovation-at-amazon/amazon-ads-generative-ai-video-generator-advertisers) from product images. This feature uses [foundation models available on Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) to give customers control over visual style, pacing, camera motion, rotation, and zooming through natural language, using an agentic workflow to first describe video storyboards and then generate the content for the story. The following screenshot shows an example of creative image generation for product backgrounds on Amazon Ads.

Figure 6. Ads image generation example for a product.

As discussed in the original post, [responsible AI](https://aws.amazon.com/ai/responsible-ai/) is at the center of the solution, and Amazon Nova creative models come with built-in controls to support safety and responsible AI use, including watermarking and content moderation.

The solution uses [AWS Step Functions](https://aws.amazon.com/step-functions/) with [AWS Lambda](https://aws.amazon.com/lambda/) functions to orchestrate serverless orchestration of both image and video generation processes. Generated content is stored in [Amazon Simple Storage Service](https://aws.amazon.com/s3/) (Amazon S3) with metadata in DynamoDB, and [Amazon API Gateway](https://aws.amazon.com/api-gateway) provides customer access to the generation capabilities. The solution now employs Amazon Bedrock Guardrails in addition to maintaining [Amazon Rekognition](https://aws.amazon.com/rekognition/) and [Amazon Comprehend](https://aws.amazon.com/comprehend/) integration at various steps for additional safety checks. The following screenshot shows creative AI-generated videos on Amazon Ads campaign builder.

Figure 7. Ads video generation for a product

Creating high-quality ad creatives at scale presented complex challenges. The generative AI model needed to produce appealing, brand-appropriate images across diverse product categories and advertising contexts while remaining accessible to advertisers regardless of technical expertise. Quality assurance and improvement are fundamental to both image and video generation capabilities. The system undergoes continual enhancement through extensive HITL processes enabled by [Amazon SageMaker Ground Truth](https://aws.amazon.com/sagemaker-ai/groundtruth/). This implementation delivers a powerful tool that transforms advertisers’ creative process, making high-quality visual content creation more accessible across diverse product categories and contexts.

This is just the beginning of Amazon Ads using generative AI to empower advertising customers to create the content they need to drive their advertising objectives. The solution demonstrates how reducing creative barriers directly increases advertising activity while maintaining high standards for responsible AI use.

## Key technical learnings and discussions

Non-conversational applications benefit from higher latency tolerance, enabling batch processing and caching, but require robust validation mechanisms and stronger guardrails due to their autonomous nature. These insights apply to both non-conversational and conversational AI implementations:

- **Task decomposition and agentic workflows –** Breaking complex problems into smaller components has proven valuable across implementations. This deliberate decomposition by domain experts enables specialized models for specific subtasks, as demonstrated in Amazon Pharmacy prescription processing, where fine-tuned SLMs handle discrete tasks such as dosage identification. This strategy allows for specialized agents with clear validation steps, improving reliability and simplifying maintenance. The Amazon seller listing use case exemplifies this through its multistep workflow with separate generation and validation processes. Additionally, the review highlights use case showcased cost-effective and controlled use of LLMs by using traditional ML for preprocessing and performing parts that could be associated with an LLM task.
- **Hybrid architectures and model selection –** Combining traditional ML with LLMs provides better control and cost-effectiveness than pure LLM approaches. Traditional ML excels at well-defined tasks, as shown in the review highlights system for sentiment analysis and information extraction. Amazon teams have strategically deployed both large and small language models based on requirements, integrating RAG with fine-tuning for effective domain-specific applications like the Amazon Pharmacy implementation.
- **Cost optimization strategies –** Amazon teams achieved efficiency through batch processing, caching mechanisms for high-volume operations, specialized instance types such as [AWS Inferentia](https://aws.amazon.com/machine-learning/inferentia/) and [AWS Trainium](https://aws.amazon.com/ai/machine-learning/trainium/), and optimized model selection. Review highlights demonstrates how incremental processing reduces computational needs, and Amazon Ads used Amazon Nova [foundation models](https://aws.amazon.com/what-is/foundation-models/) (FMs) to cost-effectively create creative content.
- **Quality assurance and control mechanisms –** Quality control relies on domain-specific guardrails through Amazon Bedrock Guardrails and multilayered validation combining automated testing with human evaluation. Dual-LLM approaches for generation and validation help prevent hallucinations in Amazon seller listings, and self-reflection techniques improve accuracy. Amazon Nova creative FMs provide inherent responsible AI controls, complemented by continual A/B testing and performance measurement.
- **HITL implementation –** The HITL approach spans multiple layers, from expert evaluation by pharmacists to end-user feedback from selling partners. Amazon teams established structured improvement workflows, balancing automation and human oversight based on specific domain requirements and risk profiles.
- **Responsible AI and compliance –** Responsible AI practices include content ingestion guardrails for regulated environments and adherence to regulations such as HIPAA. Amazon teams integrated content moderation for user-facing applications, maintained transparency in review highlights by providing access to source information, and implemented data governance with monitoring to promote quality and compliance.

These patterns enable scalable, reliable, and cost-effective generative AI solutions while maintaining quality and responsibility standards. The implementations demonstrate that effective solutions require not just sophisticated models, but careful attention to architecture, operations, and governance, supported by AWS services and established practices.

## Next steps

The examples from Amazon.com shared in this post illustrate how generative AI can create value beyond traditional conversational assistants. We invite you to follow these examples or create your own solution to discover how generative AI can reinvent your business or even your industry. You can visit the [AWS generative AI use cases](https://aws.amazon.com/ai/generative-ai/use-cases/) page to start the ideation process.

These examples showed that effective generative AI implementations often benefit from combining different types of models and workflows. To learn what FMs are supported by AWS services, refer to [Supported foundation models in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) and [Amazon SageMaker JumpStart Foundation Models](https://docs.aws.amazon.com/sagemaker/latest/dg/jumpstart-foundation-models.html). We also suggest you explore [Amazon Bedrock Flows](https://aws.amazon.com/bedrock/flows/), which can ease the path towards building workflows. Additionally, we remind you that Trainium and Inferentia accelerators provide important cost savings in these applications.

Agentic workflows, as illustrated in our examples, have proven particularly valuable. We recommend exploring [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) for quickly building agentic workflows.

Successful generative AI implementation extends beyond model selection—it represents a comprehensive software development process from experimentation to application monitoring. To begin building your foundation across these essential services, we invite you to explore [Amazon QuickStart](https://aws.amazon.com/events/quickstart/).

## Conclusion

These examples demonstrate how generative AI extends beyond conversational assistants to drive innovation and efficiency across industries. Success comes from combining AWS services with strong engineering practices and business understanding. Ultimately, effective generative AI solutions focus on solving real business problems while maintaining high standards of quality and responsibility.

To learn more about how Amazon uses AI, refer to [Artificial Intelligence](https://www.aboutamazon.com/news/tag/artificial-intelligence) in Amazon News.

### About the Authors

![Burak](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2023/09/12/Burak.jpeg)**Burak Gozluklu** is a Principal AI/ML Specialist Solutions Architect and lead GenAI Scientist Architect for Amazon.com on AWS, based in Boston, MA. He helps strategic customers adopt AWS technologies and specifically Generative AI solutions to achieve their business objectives. Burak has a PhD in Aerospace Engineering from METU, an MS in Systems Engineering, and a post-doc in system dynamics from MIT in Cambridge, MA. He maintains his connection to academia as a research affiliate at MIT. Outside of work, Burak is an enthusiast of yoga.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/21/emilio-1.jpg) **Emilio Maldonado** is a Senior leader at Amazon responsible for Product Knowledge, oriented at building systems to scale the e-commerce Catalog metadata, organize all product attributes, and leverage GenAI to infer precise information that guides Sellers and Shoppers to interact with products. He’s passionate about developing dynamic teams and forming partnerships. He holds a Bachelor of Science in C.S. from Tecnologico de Monterrey (ITESM) and an MBA from Wharton, University of Pennsylvania.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/21/wenchao.jpg)**Wenchao Tong** is a Sr. Principal Technologist at Amazon Ads in Palo Alto, CA, where he spearheads the development of GenAI applications for creative building and performance optimization. His work empowers customers to enhance product and brand awareness and drive sales by leveraging innovative AI technologies to improve creative performance and quality. Wenchao holds a Master’s degree in Computer Science from Tongji University. Outside of work, he enjoys hiking, board games, and spending time with his family.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/21/Alexander.png)**Alexandre Alves** is a Sr. Principal Engineer at Amazon Health Services, specializing in ML, optimization, and distributed systems. He helps deliver wellness-forward health experiences.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/21/Puneet-1.jpg) **Puneet Sahni** is Sr. Principal Engineer in Amazon. He works on improving the data quality of all products available in Amazon catalog. He is passionate about leveraging product data to improve our customer experiences. He has a Master’s degree in Electrical engineering from Indian Institute of Technology (IIT) Bombay. Outside of work he enjoying spending time with his young kids and travelling.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/21/Vaughn-1.jpg) **Vaughn Schermerhorn** is a Director at Amazon, where he leads Shopping Discovery and Evaluation—spanning Customer Reviews, content moderation, and site navigation across Amazon’s global marketplaces. He manages a multidisciplinary organization of applied scientists, engineers, and product leaders focused on surfacing trustworthy customer insights through scalable ML models, multimodal information retrieval, and real-time system architecture. His team develops and operates large-scale distributed systems that power billions of shopping decisions daily. Vaughn holds degrees from Georgetown University and San Diego State University and has lived and worked in the U.S., Germany, and Argentina. Outside of work, he enjoys reading, travel, and time with his family.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/21/Tarik-1.png) **Tarik Arici** is a Principal Applied Scientist at Amazon Selection and Catalog Systems (ASCS), working on Catalog Quality Enhancement using GenAI workflows. He has a PhD in Electrical and Computer Engineering from Georgia Tech. Outside of work, Tarik enjoys swimming and biking.
