---
vendor: aws_bedrock
title: How 123RF saved over 90% of their translation costs by switching to Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-123rf-saved-over-90-of-their-translation-costs-by-switching-to-amazon-bedrock
date: 2024-11-25
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 81cf3dfcd848
---

# How 123RF saved over 90% of their translation costs by switching to Amazon Bedrock

In the rapidly evolving digital content industry, multilingual accessibility is crucial for global reach and user engagement. [123RF](https://www.123rf.com/), a leading provider of royalty-free digital content, is an online resource for creative assets, including AI-generated images from text. [In 2023, they used Amazon OpenSearch Service to improve discovery of images by using vector-based semantic search](https://aws.amazon.com/solutions/case-studies/123rf-gen-ai/). Building on this success, they have now implemented [Amazon Bedrock](https://aws.amazon.com/bedrock/) and Anthropic’s Claude 3 Haiku to improve their [content moderation a hundredfold and more sped up content translation](https://aws.amazon.com/solutions/case-studies/123rf-2024/) to further enhance their global reach and efficiency.

Although the company achieved significant success among English-speaking users with its generative AI-based semantic search tool, it faced content discovery challenges in 15 other languages because of English-only titles and keywords. The cost of using Google Translate for continuous translations was prohibitive, and other models such as Anthropic’s Claude Sonnet and OpenAI GPT-4o weren’t cost-effective. Although OpenAI GPT-3.5 met cost criteria, it struggled with consistent output quality. This prompted 123RF to search for a more reliable and affordable solution to enhance multilingual content discovery.

This post explores how 123RF used Amazon Bedrock, Anthropic’s Claude 3 Haiku, and a vector store to efficiently translate content metadata, significantly reduce costs, and improve their global content discovery capabilities.

## The challenge: Balancing quality and cost in mass translation

After implementing generative AI-based semantic search and text-to-image generation, they saw significant traction among English-speaking users. This success, however, cast a harsh light on a critical gap in their global strategy: their vast library of digital assets—comprising millions of images, audio files, and motion graphics—needed a similar overhaul for non-English speaking users.

The crux of the problem lay in the nature of their content. User-generated titles, keywords, and descriptions—the lifeblood of searchability in the digital asset world—were predominantly in English. To truly serve a global audience and unlock the full potential of their library, 123RF needed to translate this metadata into 15 different languages. But as they quickly discovered, the path to multilingual content was filled with financial and technical challenges.

### The translation conundrum: Beyond word-for-word

Idioms don’t always translate well

As 123RF dove deeper into the challenge, they uncovered layers of complexity that went beyond simple word-for-word translation. The preceding figure shows one particularly difficult example: idioms. Phrases like “The early bird gets the worm” being literally translated would not convey the meaning of the word as well as another similar idiom in Spanish, “A quien madruga, Dios le ayuda”. Another significant hurdle was named entity resolution (NER)—a critical aspect for a service dealing with diverse visual and audio content.

NER involves correctly identifying and handling proper nouns, brand names, specific terminology, and culturally significant references across languages. For instance, a stock photo of the Eiffel Tower should retain its name in all languages, rather than being literally translated. Similarly, brand names like Coca-Cola or Nike should remain unchanged, regardless of the target language.

This challenge is particularly acute in the realm of creative content. Consider a hypothetical stock image titled Young woman using MacBook in a Starbucks. An ideal translation system would need to do the following:

- Recognize *MacBook* and *Starbucks* as brand names that should not be translated
- Correctly translate *Young woman* while preserving the original meaning and connotations
- Handle the preposition *in* appropriately, which might change based on the grammatical rules of the target language
- Moreover, the system needed to handle industry-specific jargon, artistic terms, and culturally specific concepts that might not have direct equivalents in other languages. For instance, how would one translate *bokeh effect* into languages where this photographic term isn’t commonly used?

These nuances highlighted the inadequacy of simple machine translation tools and underscored the need for a more sophisticated, context-aware solution.

### Turning to language models: Large models compared to small models

In their quest for a solution, 123RF explored a spectrum of options, each with its own set of trade-offs:

- **Google Translate** – The incumbent solution offered reliability and ease of use. However, it came with a staggering price tag. The company had to clear their backlog of 45 million translations. Adding to this, there was an ongoing monthly financial burden for new content that their customers generated. Though effective, this option threatened to cut into 123RF’s profitability, making it unsustainable in the long run.
- **Large language models** – Next, 123RF turned to cutting-edge large language models (LLMs) such as OpenAI GPT-4 and Anthropic’s Claude Sonnet. These models showcased impressive capabilities in understanding context and producing high-quality translations. However, the cost of running these sophisticated models at 123RF’s scale proved prohibitive. Although they excelled in quality, they fell short in cost-effectiveness for a business dealing with millions of short text snippets.
- **Smaller models** – In an attempt to find a middle ground, 123RF experimented with less capable models such as OpenAI GPT-3.5. These offered a more palatable price point, aligning better with 123RF’s budget constraints. However, this cost savings came at a price: inconsistency in output quality. The translations, although sometimes acceptable, lacked the reliability and nuance required for professional-grade content description.
- **Fine-tuning** – 123RF briefly considered fine-tuning a smaller language model to further reduce cost. However, they understood there would be a number of hurdles: they would have to regularly fine-tune models as new model updates occur, hire subject matter experts to train the models and manage their upkeep and deployment, and potentially manage a model for each of the output languages.

This exploration laid bare a fundamental challenge in the AI translation space: the seemingly unavoidable trade-off between cost and quality. High-quality translations from top-tier models were financially unfeasible, whereas more affordable options couldn’t meet the standard of accuracy and consistency that 123RF’s business demanded.

## Solution: Amazon Bedrock, Anthropic’s Claude 3 Haiku, prompt engineering, and a vector store

[Amazon Bedrock](https://aws.amazon.com/bedrock/) is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies such as AI21 Labs, Anthropic, Cohere, Meta, Mistral AI, Stability AI, and Amazon through a single API, along with a broad set of capabilities you need to build generative AI applications with security, privacy, and responsible AI.

Throughout this transformative journey, Amazon Bedrock proved to be the cornerstone of 123RF’s success. Several factors contributed to making it the provider of choice:

- **Model variety** – Amazon Bedrock offers access to a range of state-of-the-art language models, allowing 123RF to choose the one best suited for their specific needs, like Anthropic’s Claude 3 Haiku.
- **Scalability** – The ability of Amazon Bedrock to handle massive workloads efficiently was crucial for processing millions of translations.
- **Cost-effectiveness** – The pricing model of Amazon Bedrock, combined with its efficient resource utilization, played a key role in achieving the dramatic cost reduction.
- **Integration capabilities** – The ease of integrating Amazon Bedrock with other AWS services facilitated the implementation of advanced features such as a vector database for dynamic prompting.
- **Security and compliance** – 123RF works with user-generated content, and the robust security features of Amazon Bedrock provided peace of mind in handling potentially sensitive information.
- **Flexibility for custom solutions** – The openness of Amazon Bedrock to custom implementations, such as the dynamic prompting technique, allowed 123RF to tailor the solution precisely to their needs

## Cracking the code: Prompt engineering techniques

The first breakthrough in 123RF’s translation journey came through a collaborative effort with the AWS team, using the power of Amazon Bedrock and Anthropic’s Claude 3 Haiku. The key to their success lay in the innovative application of prompt engineering techniques—a set of strategies designed to coax the best performance out of LLMs, especially important for cost effective models.

Prompt engineering is crucial when working with LLMs because these models, while powerful, can produce non-deterministic outputs—meaning their responses can vary even for the same input. By carefully crafting prompts, we can provide context and structure that helps mitigate this variability. Moreover, well-designed prompts serve to steer the model towards the specific task at hand, ensuring that the LLM focuses on the most relevant information and produces outputs aligned with the desired outcome. In 123RF’s case, this meant guiding the model to produce accurate, context-aware translations that preserved the nuances of the original content.

Let’s dive into the specific techniques employed.

### Assigning a role to the model

The team began by assigning the AI model a specific role—that of an AI language translation assistant. This seemingly simple step was crucial in setting the context for the model’s task. By defining its role, the model was primed to approach the task with the mindset of a professional translator, considering nuances and complexities that a generic language model might overlook.

For example:

```
You are an AI language translation assistant. 
Your task is to accurately translate a passage of text from English into another specified language.
```

### Separation of data and prompt templates

A clear delineation between the text to be translated and the instructions for translation was implemented. This separation served two purposes:

- Provided clarity in the model’s input, reducing the chance of confusion or misinterpretation
- Allowed for simpler automation and scaling of the translation process, because the same prompt template could be used with different input texts

For example:

```
Here is the text to translate:
<text> {{TEXT}} </text>
Please translate the above text into this language: {{TARGET_LANGUAGE}}
```

### Chain of thought

One of the most innovative aspects of the solution was the implementation of a scratchpad section. This allowed the model to externalize its thinking process, mimicking the way a human translator might work through a challenging passage.

The scratchpad prompted the model to consider the following:

- The overall meaning and intent of the passage
- Idioms and expressions that might not translate literally
- Tone, formality, and style of the writing
- Proper nouns such as names and places that should not be translated
- Grammatical differences between English and the target language
- This step-by-step thought process significantly improved the quality and accuracy of translations, especially for complex or nuanced content.

### K-shot examples

The team incorporated multiple examples of high-quality translations directly into the prompt. This technique, known as K-shot learning, provided the model with a number (K) of concrete examples in the desired output quality and style.

By carefully selecting diverse examples that showcased different translation challenges (such as idiomatic expressions, technical terms, and cultural references), the team effectively trained the model to handle a wide range of content types.

For example:

```
Examples:
<text>The early bird catches the worm.</text>
<translated_text>El que madruga, Dios le ayuda.</translated_text>
```

### The magic formula: Putting it all together

The culmination of these techniques resulted in a prompt template that encapsulated the elements needed for high-quality, context-aware translation. The following is an example prompt with the preceding steps. The actual prompt used is not shown here.

```
You are an AI language translation assistant. Your task is to accurately translate a passage of text from English into another specified language. Here is the text to translate:
<text> {{TEXT}} </text>
Please translate the above text into this language: {{TARGET_LANGUAGE}}
Think carefully, in the <scratchpad> section below, think through how you will translate the text while preserving its full meaning and nuance. Consider:
- The overall meaning and intent of the passage
- Idioms and expressions that may not translate literally
- Tone, formality, and style of the writing
- Proper nouns like names and places that should not be translated
- Grammatical differences between English and {{TARGET_LANGUAGE}}
Examples:
<text>The software update is scheduled for next Tuesday.</text>
<translated_text>La actualización del software está programada para el próximo martes.</translated_text>
<text>Breaking news: Elon Musk acquires Twitter for $44 billion.</text>
<translated_text>Última hora: Elon Musk adquiere Twitter por 44 mil millones de dólares.</translated_text>
... [8 more diverse examples] ...
Now provide your final translated version of the text inside <translated_text> tags. Ensure the translation is as accurate and natural-sounding as possible in {{TARGET_LANGUAGE}}. Do not translate any names, places or other proper nouns.
<translated_text>
```

This template provided a framework for consistent, high-quality translations across a wide range of content types and target languages.

## Further refinement: Dynamic prompting for grounding models

Although the initial implementation yielded impressive results, the AWS team suggested further enhancements through dynamic prompting techniques. This advanced approach aimed to make the model even more adaptive and context aware. They adopted the Retrieval Augmented Generation (RAG) technique for creating a dynamic prompt template with K-shot examples relevant to each phrase rather than generic examples for each language. This also allowed 123RF to take advantage of their current catalog of high quality translations to further align the model.

### Vector database of high-quality translations

The team proposed creating a vector database for each target language, populated with previous high-quality translations. This database would serve as a rich repository of translation examples, capturing nuances and domain-specific terminologies.

The implementation included the following components:

- **Embedding generation:**  Use embedding models such as Amazon Titan or Cohere’s offerings on Amazon Bedrock to convert both source texts and their translations into high-dimensional vectors.
- **Chunking strategy:**  To maintain context and ensure meaningful translations, the team implemented a careful chunking strategy:  Each source text (in English) was paired with its corresponding translation in the target language. These pairs were stored as complete sentences or logical phrases, rather than individual words or arbitrary character lengths. For longer content, such as paragraphs or descriptions, the text was split into semantically meaningful chunks, ensuring that each chunk contained a complete thought or idea. Each chunk pair (source and translation) was assigned a unique identifier to maintain the association.
- **Vector storage:**  The vector representations of both the source text and its translation were stored together in the database. The storage structure included:  The original source text chunk. The corresponding translation chunk. The vector embedding of the source text. The vector embedding of the translation. Metadata such as the content type, domain, and any relevant tags.
- **Database organization:**  The database was organized by target language, with separate indices or collections for each language pair (for example, English-Spanish and English-French). Within each language pair, the vector pairs were indexed to allow for efficient similarity searches.
- **Similarity search:**  For each new translation task, the system would perform a hybrid search to find the most semantically similar sentences from the vector database:  The new text to be translated was converted into a vector using the same embedding model. A similarity search was performed in the vector space to find the closest matches in the source language. The corresponding translations of these matches were retrieved, providing relevant examples for the translation task.

This structured approach to storing and retrieving text-translation pairs allowed for efficient, context-aware lookups that significantly improved the quality and relevance of the translations produced by the LLM.

### Putting it all together

The top matching examples from the vector database would be dynamically inserted into the prompt, providing the model with highly relevant context for the specific translation task at hand.

This offered the following benefits:

- Improved handling of domain-specific terminology and phraseology
- Better preservation of style and tone appropriate to the content type
- Enhanced ability to resolve named entities and technical terms correctly

The following is an example of a dynamically generated prompt:

```
[Standard prompt preamble]
...
Examples:
<text>{{Dynamically inserted similar source text 1}}</text>
<translated_text>{{Corresponding high-quality translation 1}}</translated_text>
<text>{{Dynamically inserted similar source text 2}}</text>
<translated_text>{{Corresponding high-quality translation 2}}</translated_text>
...
[Rest of the standard prompt]
```

This dynamic approach allowed the model to continuously improve and adapt, using the growing database of high-quality translations to inform future tasks.
 The following diagram illustrates the process workflow.

How to ground translations with a vector store

The process includes the following steps:

- Convert the new text to be translated into a vector using the same embeddings model.
- Compare text and embeddings against a database of high-quality existing translations.
- Combine similar translations with an existing prompt template of generic translation examples for target language.
- Send the new augmented prompt with initial text to be translated to Amazon Bedrock.
- Store the output of the translation in an existing database or to be saved for human-in-the-loop evaluation.

## The results: A 95% cost reduction and beyond

The impact of implementing these advanced techniques on Amazon Bedrock with Anthropic’s Claude 3 Haiku and the engineering effort with AWS account teams was nothing short of innovative for 123RF. By working with AWS, 123RF was able to achieve a staggering 95% reduction in translation costs. But the benefits extended far beyond cost savings:

- **Scalability** – The new solution with Anthropic’s Claude 3 Haiku allowed 123RF to rapidly expand their multilingual offerings. They quickly rolled out translations for 9 languages, with plans to cover all 15 target languages in the near future.
- **Quality improvement** – Despite the massive cost reduction, the quality of translations saw a marked improvement. The context-aware nature of the LLM, combined with careful prompt engineering, resulted in more natural and accurate translations.
- **Handling of edge cases** – The system showed remarkable prowess in handling complex cases such as idiomatic expressions and technical jargon, which had been pain points with previous solutions.
- **Faster time-to-market** – The efficiency of the new system significantly reduced the time required to make new content available in multiple languages, giving 123RF a competitive edge in rapidly updating their global offerings.
- **Resource reallocation** – The cost savings allowed 123RF to reallocate resources to other critical areas of their business, fostering innovation and growth.

## Looking ahead: Continuous improvement and expansion

The success of this project has opened new horizons for 123RF and set the stage for further advancements:

- **Expanding language coverage** – With the cost barrier significantly lowered, 123RF is now planning to expand their language offerings beyond the initial 15 target languages, potentially tapping into new markets and user bases.
- **Anthropic’s Claude 3.5 Haiku** – The [recent release of Anthropic’s Claude 3.5 Haiku](https://www.aboutamazon.com/news/aws/amazon-bedrock-anthropic-ai-claude-3-5-sonnet) has sparked excitement at 123RF. This upcoming model promises even greater intelligence and efficiency, potentially allowing for further refinements in translation quality and cost-effectiveness.
- **Broader AI integration** – Encouraged by the success in translation, 123RF is exploring additional use cases for generative AI within their operations. Potential areas include the following:  Enhanced image tagging and categorization. Content moderation of user-generated images. Personalized content recommendations for users.
- **Continuous learning loop** – The team is working on implementing a feedback mechanism where successful translations are automatically added to the vector database, creating a virtuous cycle of continuous improvement.
- **Cross-lingual search enhancement** – Using the improved translations, 123RF is developing more sophisticated cross-lingual search capabilities, allowing users to find relevant content regardless of the language they search in.
- **Prompt catalog** – They can explore the newly launched [Amazon Bedrock Prompt Management](https://aws.amazon.com/bedrock/prompt-management/) as a way to manage prompt templates and iterate on them effectively.

## Conclusion

123RF’s success story with Amazon Bedrock and Anthropic’s Claude is more than just a tale of cost reduction—it’s a blueprint for how businesses can use cutting-edge AI to break down language barriers and truly globalize their digital content. This case study demonstrates the transformative power of innovative thinking, advanced prompt engineering, and the right technological partnership.

123RF’s journey offers the following key takeaways:

- The power of prompt engineering in extracting optimal performance from LLMs
- The importance of context and domain-specific knowledge in AI translations
- The potential of dynamic, adaptive AI solutions in solving complex business challenges
- The critical role of choosing the right technology partner and platform

As we look to the future, it’s clear that the combination of cloud computing, generative AI, and innovative prompt engineering will continue to reshape the landscape of multilingual content management. The barriers of language are crumbling, opening up new possibilities for global communication and content discovery.

For businesses facing similar challenges in global content discovery, 123RF’s journey offers valuable insights and a roadmap to success. It demonstrates that with the right technology partner and a willingness to innovate, even the most daunting language challenges can be transformed into opportunities for growth and global expansion. If you have a similar use case and want help implementing this technique, reach out to your AWS account teams, or sharpen your prompt engineering skills through our prompt engineering workshop available on [GitHub](https://github.com/aws-samples/prompt-engineering-with-anthropic-claude-v-3).

### About the Author

![Fahim Surani picture](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/20/fahimsur-1.jpg)**Fahim Surani **is a Solutions Architect at Amazon Web Services who helps customers innovate in the cloud. With a focus in Machine Learning and Generative AI, he works with global digital native companies and financial services to architect scalable, secure, and cost-effective products and services on AWS. Prior to joining AWS, he was an architect, an AI engineer, a mobile games developer, and a software engineer. In his free time he likes to run and read science fiction.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/20/ML-15758-mark-roy.png)**Mark Roy **is a Principal Machine Learning Architect for AWS, helping customers design and build generative AI solutions. His focus since early 2023 has been leading solution architecture efforts for the launch of Amazon Bedrock, AWS’ flagship generative AI offering for builders. Mark’s work covers a wide range of use cases, with a primary interest in generative AI, agents, and scaling ML across the enterprise. He has helped companies in insurance, financial services, media and entertainment, healthcare, utilities, and manufacturing. Prior to joining AWS, Mark was an architect, developer, and technology leader for over 25 years, including 19 years in financial services. Mark holds six AWS certifications, including the ML Specialty Certification.
