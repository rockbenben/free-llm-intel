---
vendor: aws_bedrock
title: Building intelligent AI voice agents with Pipecat and Amazon Bedrock – Part 1
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/building-intelligent-ai-voice-agents-with-pipecat-and-amazon-bedrock-part-1
date: 2025-06-09
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 1b78c3823ba6
---

# Building intelligent AI voice agents with Pipecat and Amazon Bedrock – Part 1

Voice AI is transforming how we interact with technology, making conversational interactions more natural and intuitive than ever before. At the same time, AI agents are becoming increasingly sophisticated, capable of understanding complex queries and taking autonomous actions on our behalf. As these trends converge, you see the emergence of intelligent AI voice agents that can engage in human-like dialogue while performing a wide range of tasks.

In this series of posts, you will learn how to build intelligent AI voice agents using [Pipecat](https://github.com/pipecat-ai/pipecat), an open-source framework for voice and multimodal conversational AI agents, with foundation models on [Amazon Bedrock](https://aws.amazon.com/bedrock/). It includes high-level reference architectures, best practices and [code samples](https://github.com/aws-samples/building-intelligent-voice-ai-agents-with-pipecat-and-amazon-bedrock) to guide your implementation.

## Approaches for building AI voice agents

There are two common approaches for building conversational AI agents:

- **Using cascaded models:** In this post (Part 1), you will learn about the cascaded models approach, diving into the individual components of a conversational AI agent. With this approach, voice input passes through a series of architecture components before a voice response is sent back to the user. This approach is also sometimes referred to as pipeline or component model voice architecture.
- **Using speech-to-speech foundation models in a single architecture:** In [Part 2](https://aws.amazon.com/blogs/machine-learning/building-intelligent-ai-voice-agents-with-pipecat-and-amazon-bedrock-part-2/), you will learn how [Amazon Nova Sonic](https://aws.amazon.com/blogs/aws/introducing-amazon-nova-sonic-human-like-voice-conversations-for-generative-ai-applications/), a state-of-the-art, unified speech-to-speech foundation model can enable real-time, human-like voice conversations by combining speech understanding and generation in a single architecture.

## Common use cases

AI voice agents can handle multiple use cases, including but not limited to:

- **Customer Support:** AI voice agents can handle customer inquiries 24/7, providing instant responses and routing complex issues to human agents when necessary.
- **Outbound Calling:** AI agents can conduct personalized outreach campaigns, scheduling appointments or following up on leads with natural conversation.
- **Virtual Assistants:** Voice AI can power personal assistants that help users manage tasks, answer questions.

## Architecture: Using cascaded models to build an AI voice agent

To build an agentic voice AI application with the cascaded models approach, you need to orchestrate multiple architecture components involving multiple machine learning and foundation models.

![Reference Architecture - Pipecat](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/09/Reference-Architecture-Pipecat.png)

*Figure 1: Architecture overview of a Voice AI Agent using Pipecat*

These components include:

**WebRTC Transport:** Enables real-time audio streaming between client devices and the application server.

**Voice Activity Detection (VAD):** Detects speech using [Silero VAD](https://github.com/snakers4/silero-vad) with configurable speech start and speech end times, and noise suppression capabilities to remove background noise and enhance audio quality.

**Automatic Speech Recognition (ASR):** Uses [Amazon Transcribe](https://aws.amazon.com/transcribe/) for accurate, real-time speech-to-text conversion.

**Natural Language Understanding (NLU):** Interprets user intent using [latency-optimized inference](https://aws.amazon.com/blogs/machine-learning/optimizing-ai-responsiveness-a-practical-guide-to-amazon-bedrock-latency-optimized-inference/) on Bedrock with models like [Amazon Nova Pro](http://Amazon Nova Pro) optionally enabling [prompt caching](https://aws.amazon.com/bedrock/prompt-caching/) to optimize for speed and cost efficiency in Retrieval Augmented Generation (RAG) use cases.

**Tools Execution and API Integration:** Executes actions or retrieves information for RAG by integrating backend services and data sources via Pipecat Flows and leveraging the [tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html) capabilities of foundation models.

**Natural Language Generation (NLG):** Generates coherent responses using [Amazon Nova Pro](https://aws.amazon.com/ai/generative-ai/nova/) on Bedrock, offering the right balance of quality and latency.

**Text-to-Speech (TTS):** Converts text responses back into lifelike speech using [Amazon Polly](https://aws.amazon.com/polly/) with [generative voices](https://docs.aws.amazon.com/polly/latest/dg/generative-voices.html).

**Orchestration Framework:** Pipecat orchestrates these components, offering a modular Python-based framework for real-time, multimodal AI agent applications.

## Best practices for building effective AI voice agents

Developing responsive AI voice agents requires focus on latency and efficiency. While best practices continue to emerge, consider the following implementation strategies to achieve natural, human-like interactions:

**Minimize conversation latency:** Use [latency-optimized inference](https://docs.aws.amazon.com/bedrock/latest/userguide/latency-optimized-inference.html) for foundation models (FMs) like [Amazon Nova Pro](https://aws.amazon.com/ai/generative-ai/nova/) to maintain natural conversation flow.

**Select efficient foundation models:** Prioritize smaller, faster foundation models (FMs) that can deliver quick responses while maintaining quality.

**Implement prompt caching:** Utilize [prompt caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) to optimize for both speed and cost efficiency, especially in complex scenarios requiring knowledge retrieval.

**Deploy text-to-speech (TTS) fillers:** Use natural filler phrases (such as “Let me look that up for you”) before intensive operations to maintain user engagement while the system makes tool calls or long-running calls to your foundation models.

**Build a robust audio input pipeline:** Integrate components like noise to support clear audio quality for better speech recognition results.

**Start simple and iterate:** Begin with basic conversational flows before progressing to complex agentic systems that can handle multiple use cases.

**Region availability:** Low-latency and prompt caching features may only be available in certain regions. Evaluate the trade-off between these advanced capabilities and selecting a region that is geographically closer to your end-users.

## Example implementation: Build your own AI voice agent in minutes

This post provides a [sample application on Github](https://github.com/aws-samples/building-intelligent-voice-ai-agents-with-pipecat-and-amazon-bedrock) that demonstrates the concepts discussed. It uses [Pipecat](https://github.com/pipecat-ai/pipecat) and and its accompanying state management framework, [Pipecat Flows](https://github.com/pipecat-ai/pipecat-flows) with Amazon Bedrock, along with Web Real-time Communication (WebRTC) capabilities from [Daily](https://daily.co/) to create a working voice agent you can try in minutes.

### Prerequisites

To setup the sample application, you should have the following prerequisites:

- Python 3.10+
- An AWS account with appropriate Identity and Access Management (IAM) permissions for Amazon Bedrock, Amazon Transcribe, and Amazon Polly
- [Access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html#:~:text=To%20request%20access%20to%20a,want%20to%20add%20access%20to.) to foundation models on Amazon Bedrock
- [Access](https://docs.daily.co/reference/rest-api) to an API key for Daily
- Modern web browser (such as Google Chrome or Mozilla Firefox) with WebRTC support

## Implementation Steps

After you complete the prerequisites, you can start setting up your sample voice agent:

- Clone the repository: `git clone https://github.com/aws-samples/build-intelligent-ai-voice-agents-with-pipecat-and-amazon-bedrock cd build-intelligent-ai-voice-agents-with-pipecat-and-amazon-bedrock/part-1 `
- Set up the environment: `cd server python3 -m venv venv source venv/bin/activate # Windows: venv\Scripts\activate pip install -r requirements.txt`
- Configure API key in`.env`: `DAILY_API_KEY=your_daily_api_key AWS_ACCESS_KEY_ID=your_aws_access_key_id AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key AWS_REGION=your_aws_region`
- Start the server: `python server.py`
- Connect via browser at `http://localhost:7860` and grant microphone access
- Start the conversation with your AI voice agent

### Customizing your voice AI agent

To customize, you can start by:

- Modifying `flow.py` to change conversation logic
- Adjusting model selection in` bot.py` for your latency and quality needs

To learn more, see [documentation](https://docs.pipecat.ai/guides/features/pipecat-flows) for Pipecat Flows and review the [README](https://github.com/aws-samples/building-intelligent-voice-ai-agents-with-pipecat-and-amazon-bedrock) of our code sample on Github.

### Cleanup

The instructions above are for setting up the application in your local environment. The local application will leverage AWS services and Daily through AWS IAM and API credentials. For security and to avoid unanticipated costs, when you are finished, delete these credentials to make sure that they can no longer be accessed.

## Accelerating voice AI implementations

To accelerate AI voice agent implementations, [AWS Generative AI Innovation Center (GAIIC)](https://aws.amazon.com/ai/generative-ai/innovation-center/) partners with customers to identify high-value use cases and develop proof-of-concept (PoC) solutions that can quickly move to production.

### Customer Testimonial: InDebted

[InDebted](https://www.indebted.co/), a global fintech transforming the consumer debt industry, collaborates with AWS to develop their voice AI prototype.

> “We believe AI-powered voice agents represent a pivotal opportunity to enhance the human touch in financial services customer engagement. By integrating AI-enabled voice technology into our operations, our goals are to provide customers with faster, more intuitive access to support that adapts to their needs, as well as improving the quality of their experience and the performance of our contact centre operations” 
>         says Mike Zhou, Chief Data Officer at InDebted.

By collaborating with AWS and leveraging Amazon Bedrock, organizations like InDebted can create secure, adaptive voice AI experiences that meet regulatory standards while delivering real, human-centric impact in even the most challenging financial conversations.

## Conclusion

Building intelligent AI voice agents is now more accessible than ever through the combination of open-source frameworks such as [Pipecat](https://github.com/pipecat-ai/pipecat), and powerful foundation models with [latency optimized inference](https://aws.amazon.com/blogs/machine-learning/optimizing-ai-responsiveness-a-practical-guide-to-amazon-bedrock-latency-optimized-inference/) and [prompt caching](https://aws.amazon.com/bedrock/prompt-caching/) on Amazon Bedrock.

In this post, you learned about two common approaches on how to build AI voice agents, delving into the cascaded models approach and its key components. These essential components work together to create an intelligent system that can understand, process, and respond to human speech naturally. By leveraging these rapid advancements in generative AI, you can create sophisticated, responsive voice agents that deliver real value to your users and customers.

To get started with your own voice AI project, try our [code sample on Github](https://github.com/aws-samples/building-intelligent-voice-ai-agents-with-pipecat-and-amazon-bedrock) or contact your AWS account team to explore an engagement with [AWS Generative AI Innovation Center (GAIIC)](https://aws.amazon.com/ai/generative-ai/innovation-center/).

You can also learn about building AI voice agents using a unified speech-to-speech foundation models, [Amazon Nova Sonic](https://aws.amazon.com/blogs/aws/introducing-amazon-nova-sonic-human-like-voice-conversations-for-generative-ai-applications/) in [Part 2](https://aws.amazon.com/blogs/machine-learning/building-intelligent-ai-voice-agents-with-pipecat-and-amazon-bedrock-part-2/).

### About the Authors

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/09/adxthya.jpeg)**[Adithya Suresh](https://www.linkedin.com/in/adithyaxx/)** serves as a Deep Learning Architect at the AWS Generative AI Innovation Center, where he partners with technology and business teams to build innovative generative AI solutions that address real-world challenges.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/02/05/wirjo.jpeg)**[Daniel Wirjo](https://www.linkedin.com/in/wirjo/)** is a Solutions Architect at AWS, focused on FinTech and SaaS startups. As a former startup CTO, he enjoys collaborating with founders and engineering leaders to drive growth and innovation on AWS. Outside of work, Daniel enjoys taking walks with a coffee in hand, appreciating nature, and learning new ideas.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/28/karan.jpg)**[Karan Singh](https://www.linkedin.com/in/karan-singh-a8aa7518/)** is a Generative AI Specialist at AWS, where he works with top-tier third-party foundation model and agentic frameworks providers to develop and execute joint go-to-market strategies, enabling customers to effectively deploy and scale solutions to solve enterprise generative AI challenges.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2023/10/07/liuxuefeng.jpg)**[Xuefeng Liu](https://www.linkedin.com/in/xuefeng-liu-aa915362/)** leads a science team at the AWS Generative AI Innovation Center in the Asia Pacific regions. His team partners with AWS customers on generative AI projects, with the goal of accelerating customers’ adoption of generative AI.
