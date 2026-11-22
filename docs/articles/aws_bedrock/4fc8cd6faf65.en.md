---
vendor: aws_bedrock
title: Build AI-powered malware analysis using Amazon Bedrock with Deep Instinct
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-ai-powered-malware-analysis-using-amazon-bedrock-with-deep-instinct
date: 2025-01-09
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 71b4cc1d0e6b
---

# Build AI-powered malware analysis using Amazon Bedrock with Deep Instinct

*This post is co-written with Yaniv Avolov, Tal Furman and Maor Ashkenazi from Deep Instinct.*

[Deep Instinct](https://www.deepinstinct.com/) is a cybersecurity company that offers a state-of-the-art, comprehensive zero-day data security solution—Data Security X (DSX), for safeguarding your data repositories across the cloud, applications, network attached storage (NAS), and endpoints. DSX provides unmatched prevention and explainability by using a powerful combination of deep learning-based DSX Brain and generative AI DSX Companion to protect systems from known and unknown malware and ransomware in real-time.

Using deep neural networks (DNNs), Deep Instinct analyzes threats with unmatched accuracy, adapting to identify new and unknown risks that traditional methods might miss. This approach significantly reduces false positives and enables unparalleled threat detection rates, making it popular among large enterprises and critical infrastructure sectors such as finance, healthcare, and government.

In this post, we explore how Deep Instinct’s generative AI-powered malware analysis tool, DIANNA, uses [Amazon Bedrock](https://aws.amazon.com/bedrock/) to revolutionize cybersecurity by providing rapid, in-depth analysis of known and unknown threats, enhancing the capabilities of AWS System and Organization Controls (SOC) teams and addressing key challenges in the evolving threat landscape.

## Main challenges for SecOps

There are two main challenges for SecOps:

- **The growing threat landscape** – With a rapidly evolving threat landscape, SOC teams are becoming overwhelmed with a continuous increase of security alerts that require investigation. This situation hampers proactive threat hunting and exacerbates team burnout. Most importantly, the surge in *alert storms* increases the risk of missing critical alerts. A solution is needed that provides the explainability necessary to allow SOC teams to perform quick risk assessments regarding the nature of incidents and make informed decisions.
- **The challenges of malware analysis** – Malware analysis has become an increasingly critical and complex field. The challenge of zero-day attacks lies in the limited information about why a file was blocked and classified as malicious. Threat analysts often spend considerable time assessing whether it was a genuine exploit or a false positive.

Let’s explore some of the key challenges that make malware analysis demanding:

- **Identifying malware **– Modern malware has become incredibly sophisticated in its ability to disguise itself. It often mimics legitimate software, making it challenging for analysts to distinguish between benign and malicious code. Some malware can even disable security tools or evade scanners, further obfuscating detection.
- **Preventing zero-day threats –** The rise of zero-day threats, which have no known signatures, adds another layer of difficulty. Identifying unknown malware is crucial, because failure can lead to severe security breaches and potentially incapacitate organizations.
- **Information overload**** –** The powerful malware analysis tools currently available can be both beneficial and detrimental. Although they offer high explainability, they can also produce an overwhelming amount of data, forcing analysts to sift through a digital haystack to find indicators of malicious activity, increasing the possibility of analysts overlooking critical compromises.
- **Connecting the dots** – Malware often consists of multiple components interacting in complex ways. Not only do analysts need to identify the individual components, but they also need to understand how they interact. This process is like assembling a jigsaw puzzle to form a complete picture of the malware’s capabilities and intentions, with pieces constantly changing shape.
- **Keeping up with cybercriminals** – The world of cybercrime is fluid, with bad actors relentlessly developing new techniques and exploiting newly emerging vulnerabilities, leaving organizations struggling to keep up. The time window between the discovery of a vulnerability and its exploitation in the wild is narrowing, putting pressure on analysts to work faster and more efficiently. This rapid evolution means that malware analysts must constantly update their skill set and tools to stay one step ahead of the cybercriminals.
- **Racing against the clock** – In malware analysis, time is of the essence. Malicious software can spread rapidly across networks, causing significant damage in a matter of minutes, often before the organization realizes an exploit has occurred. Analysts face the pressure of conducting thorough examinations while also providing timely insights to prevent or mitigate exploits.

## DIANNA, the DSX Companion

There is a critical need for malware analysis tools that can provide precise, real-time, in-depth malware analysis for both known and unknown threats, supporting SecOps efforts. Deep Instinct, recognizing this need, has developed DIANNA (Deep Instinct’s Artificial Neural Network Assistant), the DSX Companion. DIANNA is a groundbreaking malware analysis tool powered by [generative AI](https://aws.amazon.com/generative-ai/) to tackle real-world issues, using Amazon Bedrock as its large language model (LLM) infrastructure. It offers on-demand features that provide flexible and scalable AI capabilities tailored to the unique needs of each client. Amazon Bedrock is a fully managed service that grants access to high-performance foundation models (FMs) from top AI companies through a unified API. By concentrating our generative AI models on specific artifacts, we can deliver comprehensive yet focused responses to address this gap effectively.

DIANNA is a sophisticated malware analysis tool that acts as a virtual team of malware analysts and incident response experts. It enables organizations to shift strategically toward zero-day data security by integrating with Deep Instinct’s deep learning capabilities for a more intuitive and effective defense against threats.

## DIANNA’s unique approach

Current cybersecurity solutions use generative AI to summarize data from existing sources, but this approach is limited to retrospective analysis with limited context. DIANNA enhances this by integrating the collective expertise of numerous cybersecurity professionals within the LLM, enabling in-depth malware analysis of unknown files and accurate identification of malicious intent.

DIANNA’s unique approach to malware analysis sets it apart from other cybersecurity solutions. Unlike traditional methods that rely solely on retrospective analysis of existing data, DIANNA harnesses generative AI to empower itself with the collective knowledge of countless cybersecurity experts, sources, blog posts, papers, threat intelligence reputation engines, and chats. This extensive knowledge base is effectively embedded within the LLM, allowing DIANNA to delve deep into unknown files and uncover intricate connections that would otherwise go undetected.

At the heart of this process are DIANNA’s advanced translation engines, which transform complex binary code into natural language that LLMs can understand and analyze. This unique approach bridges the gap between raw code and human-readable insights, enabling DIANNA to provide clear, contextual explanations of a file’s intent, malicious aspects, and potential system impact. By translating the intricacies of code into accessible language, DIANNA addresses the challenge of information overload, distilling vast amounts of data into concise, actionable intelligence.

This translation capability is key for linking between different components of complex malware. It allows DIANNA to identify relationships and interactions between various parts of the code, offering a holistic view of the threat landscape. By piecing together these components, DIANNA can construct a comprehensive picture of the malware’s capabilities and intentions, even when faced with sophisticated threats. DIANNA doesn’t stop at simple code analysis—it goes deeper. It provides insights into why unknown events are malicious, streamlining what is often a lengthy process. This level of understanding allows SOC teams to focus on the threats that matter most.

## Solution overview

DIANNA’s integration with Amazon Bedrock allows us to harness the power of state-of-the-art language models while maintaining agility to adapt to evolving client requirements and security considerations. DIANNA benefits from the robust features of Amazon Bedrock, including seamless scaling, enterprise-grade security, and the ability to fine-tune models for specific use cases.

The integration offers the following benefits:

- **Accelerated development with Amazon Bedrock **– The fast-paced evolution of the threat landscape necessitates equally responsive cybersecurity solutions. DIANNA’s collaboration with Amazon Bedrock has played a crucial role in optimizing our development process and speeding up the delivery of innovative capabilities. The service’s versatility has enabled us to experiment with different FMs, exploring their strengths and weaknesses in various tasks. This experimentation has led to significant advancements in DIANNA’s ability to understand and explain complex malware behaviors. We have also benefited from the following features:  **Fine-tuning **– Alongside its core functionalities, Amazon Bedrock provides a range of ready-to-use features for customizing the solution. One such feature is model fine-tuning, which allows you to train FMs on proprietary data to enhance your performance in specific domains. For example, organizations can fine-tune an LLM-based malware analysis tool to recognize industry-specific jargon or detect threats associated with particular vulnerabilities. **Retrieval Augmented Generation **– Another valuable feature is the use of Retrieval Augmented Generation (RAG), enabling access to and the incorporation of relevant information from external sources, such as knowledge bases or threat intelligence feeds. This enhances the model’s ability to provide contextually accurate and informative responses, improving the overall effectiveness of malware analysis.
- **A landscape for innovation and comparison **– Amazon Bedrock has also served as a valuable landscape for conducting LLM-related research and comparisons.
- **Seamless integration, scalability, and customization **– Integrating Amazon Bedrock into DIANNA’s architecture was a straightforward process. The user-friendly Amazon Bedrock API and well-documented facilitated seamless integration with our existing infrastructure. Furthermore, the service’s on-demand nature allows us to scale our AI capabilities up or down based on customer demand. This flexibility makes sure that DIANNA can handle fluctuating workloads without compromising performance.
- **Prioritizing data security and compliance **– Data security and compliance are paramount in the cybersecurity domain. Amazon Bedrock offers enterprise-grade security features that provide us with the confidence to handle sensitive customer data. The service’s adherence to industry-leading security standards, coupled with the extensive experience of AWS in data protection, makes sure DIANNA meets the highest regulatory requirements such as GDPR. By using Amazon Bedrock, we can offer our customers a solution that not only protects their assets, but also demonstrates our commitment to data privacy and security.

By combining Deep Instinct’s proprietary prevention algorithms with the advanced language processing capabilities of Amazon Bedrock, DIANNA offers a unique solution that not only identifies and analyzes threats with high accuracy, but also communicates its findings in clear, actionable language. This synergy between Deep Instinct’s expertise in cybersecurity and the leading AI infrastructure of Amazon positions DIANNA at the forefront of AI-driven malware analysis and threat prevention.

The following diagram illustrates DIANNA’s architecture.

![DIANNA’s architecture](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/24/image001.png)

## Evaluating DIANNA’s malware analysis

In our task, the input is a malware sample, and the output is a comprehensive, in-depth report on the behaviors and intents of the file. However, generating ground truth data is particularly challenging. The behaviors and intents of malicious files aren’t readily available in standard datasets and require expert malware analysts for accurate reporting. Therefore, we needed a custom evaluation approach.

We focused our evaluation on two core dimensions:

- **Technical features **– This dimension focuses on objective, measurable capabilities. We used programmable metrics to assess how well DIANNA handled key technical aspects, such as extracting indicators of compromise (IOCs), detecting critical keywords, and processing the length and structure of threat reports. These metrics allowed us to quantitatively assess the model’s basic analysis capabilities.
- **In-depth semantics **– Because DIANNA is expected to generate complex, human-readable reports on malware behavior, we relied on domain experts (malware analysts) to assess the quality of the analysis. The reports were evaluated based on the following:  **Depth of information** – Whether DIANNA provided a detailed understanding of the malware’s behavior and techniques. **Accuracy** – How well the analysis aligned with the true behaviors of the malware. **Clarity and structure** – Evaluating the organization of the report, making sure the output was clear and comprehensible for security teams.

Because human evaluation is labor-intensive, fine-tuning the key components (the model itself, the prompts, and the translation engines) involved iterative feedback loops. Small adjustments in a component led to significant variations in the output, requiring repeated validations by human experts. The meticulous nature of this process, combined with the continuous need for scaling, has subsequently led to the development of the auto-evaluation capability.

### Fine-tuning process and human validation

The fine-tuning and validation process consisted of the following steps:

- **Gathering a malware dataset**** –** To cover the breadth of malware techniques, families, and threat types, we collected a large dataset of malware samples, each with technical metadata.
- **Splitting the dataset – **The data was split into subsets for training, validation, and evaluation. Validation data was continually used to test how well DIANNA adapted after each key component update.
- **Human expert evaluation – **Each time we fine-tuned DIANNA’s model, prompts, and translation mechanisms, human malware analysts reviewed a portion of the validation data. This made sure improvements or degradations in the quality of the reports were identified early. Because DIANNA’s outputs are highly sensitive to even minor changes, each update required a full reevaluation by human experts to verify whether the response quality was improved or degraded.
- **Final evaluation on a broader dataset – **After sufficient tuning based on the validation data, we applied DIANNA to a large evaluation set. Here, we gathered comprehensive statistics on its performance to confirm improvements in report quality, correctness, and overall technical coverage.

### Automation of evaluation

To make this process more scalable and efficient, we introduced an automatic evaluation phase. We trained a language model specifically designed to critique DIANNA’s outputs, providing a level of automation in assessing how well DIANNA was generating reports. This critique model acted as an internal judge, allowing for continuous, rapid feedback on incremental changes during fine-tuning. This enabled us to make small adjustments across DIANNA’s three core components (model, prompts, and translation engines) while receiving real-time evaluations of the impact of those changes.

This automated critique model enhanced our ability to test and refine DIANNA without having to rely solely on the time-consuming manual feedback loop from human experts. It provided a consistent, reliable measure of performance and allowed us to quickly identify which model adjustments led to meaningful improvements in DIANNA’s analysis.

## Advanced integration and proactive analysis

DIANNA is integrated with Deep Instinct’s proprietary deep learning algorithms, enabling it to detect zero-day threats with high accuracy and a low false positive rate. This proactive approach helps security teams quickly identify unknown threats, reduce false positives, and allocate resources more effectively. Additionally, it streamlines investigations, minimizes cross-tool efforts, and automates repetitive tasks, making the decision-making process clearer and faster. This ultimately helps organizations strengthen their security posture and significantly reduce the mean time to triage.

This analysis offers the following key features and benefits:

- Performs on-the-fly file scans, allowing for immediate assessment without prior setup or delays
- Generates comprehensive malware analysis reports for a variety of file types in seconds, making sure users receive timely information about potential threats
- Streamlines the entire file analysis process, making it more efficient and user-friendly, thereby reducing the time and effort required for thorough evaluations
- Supports a wide range of common file formats, including Office documents, Windows executable files, script files, and Windows shortcut files (.lnk), providing compatibility with various types of data
- Offers in-depth contextual analysis, malicious file triage, and actionable insights, greatly enhancing the efficiency of investigations into potentially harmful files
- Empowers SOC teams to make well-informed decisions without relying on manual malware analysis by providing clear and concise insights into the behavior of malicious files
- Alleviates the need to upload files to external sandboxes or VirusTotal, thereby enhancing security and privacy while facilitating quicker analysis

## Explainability and insights into better decision-making for SOC teams

DIANNA stands out by offering clear insights into why unknown events are flagged as malicious. Traditional AI tools often rely on lengthy, retrospective analyses that can take hours or even days to generate, and often lead to vague conclusions. DIANNA dives deeper, understanding the intent behind the code and providing detailed explanations of its potential impact. This clarity allows SOC teams to prioritize the threats that matter most.

## Example scenario of DIANNA in action

In this section, we explore some DIANNA use cases.

For example, DIANNA can perform investigations on malicious files.

The following screenshot is an example of a Windows executable file analysis.![Windows executable file analysis](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/24/Screenshot-2024-12-24-at-18.58.16.png)

The following screenshot is an example of an Office file analysis.

![Office file analysis](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/24/Screenshot-2024-12-24-at-18.56.13.png)

You can also quickly triage incidents with enriched data on file analysis provided by DIANNA. The following screenshot is an example using Windows shortcut files (LNK) analysis.![Windows shortcut files (LNK) analysis](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/24/Screenshot-2024-12-24-at-18.51.15.png)

The following screenshot is an example with a script file (JavaScript) analysis.![script file (JavaScript) analysis](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/24/Screenshot-2024-12-24-at-18.51.32.png)

The following figure presents a before and after comparison of the analysis process.![comparison of the analysis process](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/24/Screenshot-2024-12-24-at-18.54.44.png)

Additionally, a key advantage of DIANNA is its ability to provide explainability by correlating and summarizing the intentions of malicious files in a detailed narrative. This is especially valuable for zero-day and unknown threats that aren’t yet recognized, making investigations challenging when starting from scratch without any clues.

## Potential advancements in AI-driven cybersecurity

AI capabilities are enhancing daily operations, but adversaries are also using AI to create sophisticated malicious events and advanced persistent threats. This leaves organizations, particularly SOC and cybersecurity teams, dealing with more complex incidents.

Although detection controls are useful, they often require significant resources and can be ineffective on their own. In contrast, using AI engines for prevention controls—such as a high-efficacy deep learning engine—can lower the total cost of ownership and help SOC analysts streamline their tasks.

## Conclusion

The Deep Instinct solution can predict and prevent known, unknown, and zero-day threats in under 20 milliseconds—750 times faster than the fastest ransomware encryption. This makes it essential for security stacks, offering comprehensive protection in hybrid environments.

DIANNA provides expert malware analysis and explainability for zero-day attacks and can enhance the incident response process for the SOC team, allowing them to efficiently tackle and investigate unknown threats with minimal time investment. This, in turn, reduces the resources and expenses that Chief Information Security Officers (CISOs) need to allocate, enabling them to invest in more valuable initiatives.

DIANNA’s collaboration with Amazon Bedrock accelerated development, enabled innovation through experimentation with various FMs, and facilitated seamless integration, scalability, and data security. The rise of AI-based threats is becoming more pronounced. As a result, defenders must outpace increasingly sophisticated bad actors by moving beyond traditional AI tools and embracing advanced AI, especially deep learning. Companies, vendors, and cybersecurity professionals must consider this shift to effectively combat the growing prevalence of AI-driven exploits.

### About the Authors

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/24/Tzachi-100.jpg)**Tzahi Mizrahi** is a Solutions Architect at Amazon Web Services with experience in cloud architecture and software development. His expertise includes designing scalable systems, implementing DevOps best practices, and optimizing cloud infrastructure for enterprise applications. He has a proven track record of helping organizations modernize their technology stack and improve operational efficiency. In his free time, he enjoys music and plays the guitar.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/25/tal-panchek-100.png)**Tal Panchek** is a Senior Business Development Manager for Artificial Intelligence and Machine Learning with Amazon Web Services. As a BD Specialist, he is responsible for growing adoption, utilization, and revenue for AWS services. He gathers customer and industry needs and partner with AWS product teams to innovate, develop, and deliver AWS solutions.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/27/yaniv2.jpg)**Yaniv Avolov** is a Principal Product Manager at Deep Instinct, bringing a wealth of experience in the cybersecurity field. He focuses on defining and designing cybersecurity solutions that leverage AI\ML, including deep learning and large language models, to address customer needs. In addition, he leads the endpoint security solution, ensuring it is robust and effective against emerging threats. In his free time, he enjoys cooking, reading, playing basketball, and traveling.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/26/tal-1.jpeg)**Tal Furman** is a Data Science and Deep Learning Director at Deep Instinct. His focused on applying Machine Learning and Deep Learning algorithms to tackle real world challenges, and takes pride in leading people and technology to shape the future of cyber security. In his free time, Tal enjoys running, swimming, reading and playfully trolling his kids and dogs.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/26/maor.jpg)**Maor Ashkenazi** is a deep learning research team lead at Deep Instinct, and a PhD candidate at Ben-Gurion University of the Negev. He has extensive experience in deep learning, neural network optimization, computer vision, and cyber security. In his spare time, he enjoys traveling, cooking, practicing mixology and learning new things.
