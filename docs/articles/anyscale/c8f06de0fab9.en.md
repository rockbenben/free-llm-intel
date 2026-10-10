---
vendor: anyscale
title: Building Production AI Applications with Ray Serve
original_title: Building Production AI Applications with Ray Serve
url: https://anyscale.com/blog/building-production-ai-applications-with-ray-serve
date: 2023-10-24
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 95daf710e84c
---



Blog Detail

# Building Production AI Applications with Ray Serve

By

Anyscale Ray Team

|

October 24, 2023

Update June 2024: Anyscale Endpoints (Anyscale's LLM API Offering) and Private Endpoints (self-hosted LLMs) are now available as part of the Anyscale Platform. Click [here](https://console.anyscale.com/?utm_source=anyscale&utm_medium=blog&utm_campaign=blog_callout&utm_content=june2024_product_update_subheading) to get started on the Anyscale platform.

*This blog post is part of the Ray Summit 2023 highlights series where we provide a summary of the most exciting talk from our recent LLM developer conference.*

*Disclaimer: Summary was AI generated with human edits from video transcript.*

## LinkKey Takeaways

Ray Serve, a flexible and efficient compute system for online inference, is revolutionizing the way AI applications are built and deployed. In this blog post, we explore how Ray Serve addresses common challenges in AI application deployment, such as model microservices, the rise of large language models, and the increasing cost of hardware. We also discuss Ray Serve's observability, spot instance support, and auto-scaling features, which make it a powerful tool for building production AI applications.

- Ray Serve helps address common problems in serving online AI applications by providing a python native framework that allows complex applications with multiple models to be expressed in a single Python program. This makes it easy to iterate and deploy quickly.
- Some 2023 trends Ray Serve is addressing:

- Rise of large language models (LLMs) - Ray Serve added optimizations like the [RayLLM](https://github.com/ray-project/ray-llm) subproject to serve LLMs efficiently.
- Increasing cost of hardware - Ray Serve added optimizations like model multiplexing to maximize hardware usage.

- Going to production: Ray Serve focused on production readiness with stability, chaos testing, observability features like the Ray dashboard, and managed offerings like Anyscale.
- Demo highlights:

- Anyscale service UI for visualizing Ray Serve deployments
- CloudWatch integration for request tracing
- Grafana dashboards for metrics and analytics
- Support for spot instances to reduce costs
- Auto-scaling to dynamically scale resources based on load

- Ray Serve is now generally available in Ray 2.7 after increased adoption and hardening in production environments in 2023.

## LinkBuilding Production AI Applications with Ray Serve

Artificial Intelligence (AI) and Machine Learning (ML) have become integral to various industries, driving innovation and efficiency. However, building and deploying AI applications for production can be a complex and resource-intensive task. This is where Ray Serve, a powerful AI serving system, comes into play. In this blog post, we will delve into the world of Ray Serve and how it is transforming the landscape of building production AI applications.

## LinkChallenges in Building Production AI Applications

To understand the significance of Ray Serve, we must first recognize the challenges that AI developers and organizations face when building production AI applications:

- **Model Microservices**: Traditional AI applications often follow a model microservices architecture, where each model runs as a separate service with its own Docker configuration and Kubernetes deployment. This approach is complex and resource-intensive, making it challenging to efficiently innovate and share resources among multiple models.
- **Rise of Large Language Models (LLMs)**: The emergence of Large Language Models like GPT-3 and its variants has marked a significant trend in AI. To harness the potential of LLMs, AI developers need a flexible and scalable infrastructure.
- **Increasing Hardware Costs**: As AI models grow in complexity, the cost of hardware, especially Graphics Processing Units (GPUs), has risen substantially. Efficiently utilizing and managing these resources is paramount for cost-effectiveness.

## LinkIntroducing Ray Serve

Ray Serve is a game-changer in the realm of AI application deployment. It offers a flexible, scalable, and efficient approach to building production AI applications. Let's explore how Ray Serve addresses the challenges mentioned above:

- **Model Microservices Simplified: **Ray Serve allows developers to express complex applications as a single Python program. This means that you can mix business logic with multiple models and iterate quickly, from local testing to production deployment. The Python-native nature of Ray Serve simplifies application architecture, reducing the complexity associated with maintaining separate microservices for each model.
- **Embracing Large Language Models: **In response to the rise of Large Language Models (LLMs), Ray Serve has introduced specialized infrastructure for serving LLMs. This optimized infrastructure integrates with state-of-the-art solutions like VLLM and NVIDIA's TensorRT, ensuring that AI applications can leverage LLMs efficiently.
- **Addressing Hardware Costs: **Ray Serve provides advanced features to optimize resource allocation and scaling. It supports model multiplexing, enabling the concurrent operation of numerous models on the same hardware. This capability is vital in a landscape where GPU availability is dwindling and hardware costs are escalating. Moreover, Ray Serve offers support for spot instances, allowing you to take advantage of cost-effective cloud resources without compromising service availability.

## LinkSavings and Success Stories

Real-world examples highlight the effectiveness of Ray Serve in addressing these challenges. Samsara, a user of Ray Serve, migrated its AI platform to Ray Serve, resulting in a 50% reduction in annual inference costs. Financial institutions like any scale are running significant GPU clusters on Ray Serve, offering state-of-the-art models at a fraction of the cost of competing solutions.

## LinkKeeping Up with Trends

The AI landscape is dynamic, with new models and techniques emerging regularly. To stay competitive, organizations need to adapt quickly. Ray Serve's flexibility and developer productivity have allowed it to keep pace with these trends. It has introduced features such as streaming responses, continuous batching, and tensor parallelism, aligning with the latest advancements in the field. This ensures that businesses can quickly integrate and drive value from emerging developments in AI.

## LinkProduction Readiness

2023 has been a transformative year for AI, with many companies transitioning from ideation to production use of ML. For this transition, having a robust deployment and observability system is vital. Ray Serve has focused on enhancing production readiness, introducing observability features such as the Serv tab on the Ray dashboard, improved metrics, and logging. Continuous chaos and scale testing ensure stability and catch issues before they affect users.

## LinkRay Serve in Action - A Photographic Calculator App

Ray Serve is demonstrated through a Photographic Calculator app. This app showcases Ray Serve's capabilities, including its ability to independently scale deployments, adapt to traffic bursts, and optimize resource usage based on varying hardware requirements.

## LinkObservability for In-Depth Insights

Ray Serve's observability features provide insights into how requests flow through the application, the latency at each deployment, and the health of critical components. This level of visibility empowers administrators to make informed decisions and troubleshoot effectively.

## LinkSpot Instances for Cost Efficiency

Ray Serve introduces support for spot instances, allowing users to leverage cost-effective cloud resources. When spot instances are preempted, Ray Serve gracefully shifts traffic to on-demand nodes and automatically reverts to spot instances when they become available. This cost-saving strategy ensures that AI applications remain cost-efficient.

## LinkAuto-Scaling for Handling Traffic Bursts

Traffic patterns can fluctuate, and applications need to adapt to these changes. Ray Serve's auto-scaling capabilities allow it to dynamically adjust the number of replicas and nodes in response to user demand. As seen in the demo, this results in an increase in throughput and a reduction in latency during traffic bursts.

## LinkConclusion

Building production AI applications can be a challenging endeavor, but Ray Serve simplifies the process by providing a flexible and efficient infrastructure. It addresses the challenges posed by model microservices, the rise of Large Language Models, and the increasing cost of hardware. With observability, spot instance support, and auto-scaling, Ray Serve empowers organizations to deliver AI solutions that are not only cost-effective but also capable of adapting to changing AI trends. As the AI landscape continues to evolve, Ray Serve remains a powerful tool for organizations seeking to harness the potential of AI in a production environment.

Check out [Ray Serve](https://ray.io/serve), sign up now for[ Anyscale endpoints](https://www.anyscale.com/endpoints?utm_source=anyscale&utm_campaign=ray-highlights-2023-blog) and get started fast or[ contact sales](https://www.anyscale.com/signup?utm_source=anyscale&utm_campaign=ray-highlights-2023-blog) if you are looking for a comprehensive overview of the Anyscale platform.

#### Table of contents

- [Key Takeaways](https://www.anyscale.com/blog/building-production-ai-applications-with-ray-serve#key-takeaways)
- [Building Production AI Applications with Ray Serve](https://www.anyscale.com/blog/building-production-ai-applications-with-ray-serve#building-production-ai-applications-with-ray-serve)
- [Challenges in Building Production AI Applications](https://www.anyscale.com/blog/building-production-ai-applications-with-ray-serve#challenges-in-building-production-ai-applications)
- [Introducing Ray Serve](https://www.anyscale.com/blog/building-production-ai-applications-with-ray-serve#introducing-ray-serve)
- [Savings and Success Stories](https://www.anyscale.com/blog/building-production-ai-applications-with-ray-serve#savings-and-success-stories)
- [Keeping Up with Trends](https://www.anyscale.com/blog/building-production-ai-applications-with-ray-serve#keeping-up-with-trends)
- [Production Readiness](https://www.anyscale.com/blog/building-production-ai-applications-with-ray-serve#production-readiness)
- [Ray Serve in Action - A Photographic Calculator App](https://www.anyscale.com/blog/building-production-ai-applications-with-ray-serve#ray-serve-in-action---a-photographic-calculator-app)
- [Observability for In-Depth Insights](https://www.anyscale.com/blog/building-production-ai-applications-with-ray-serve#observability-for-in-depth-insights)
- [Spot Instances for Cost Efficiency](https://www.anyscale.com/blog/building-production-ai-applications-with-ray-serve#spot-instances-for-cost-efficiency)
- [Auto-Scaling for Handling Traffic Bursts](https://www.anyscale.com/blog/building-production-ai-applications-with-ray-serve#auto-scaling-for-handling-traffic-bursts)
- [Conclusion](https://www.anyscale.com/blog/building-production-ai-applications-with-ray-serve#conclusion)

#### Sharing

#### Tags

#### Sign up for product updates

#### Recommended content

#### Ray Summit 2026: Physical AI, RL, and the infrastructure that runs them all


#### Scaling Ray for AI workloads to 10k node clusters


#### Optimizing LLM Serving Efficiency: Moving Beyond KV Cache Reuse to Token-Load Awareness with Ray Serve LLM


## Explore Anyscale today

Build, run, and scale any AI workload on Ray with a multi-cloud platform built for production AI.

Start for Free

Talk to an expert
