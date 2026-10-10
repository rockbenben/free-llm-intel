---
vendor: anyscale
title: How Spotify Built a Robust Ray Platform with a Frictionless Developer Experience
original_title: How Spotify Built a Robust Ray Platform with a Frictionless Developer Experience
url: https://anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer
date: 2023-11-09
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 5a0dc7b68a3b
---



Blog Detail

# How Spotify Built a Robust Ray Platform with a Frictionless Developer Experience

By

Anyscale Ray Team

|

November 9, 2023

Update June 2024: Anyscale Endpoints (Anyscale's LLM API Offering) and Private Endpoints (self-hosted LLMs) are now available as part of the Anyscale Platform. Click [here](https://console.anyscale.com/?utm_source=anyscale&utm_medium=blog&utm_campaign=blog_callout&utm_content=june2024_product_update_subheading) to get started on the Anyscale platform.

*This blog post is part of the Ray Summit 2023 highlights series where we provide a summary of the most exciting talk from our recent LLM developer conference.*

*Disclaimer: Summary was AI generated with human edits from video transcript.*

## LinkKey Takeaway

Spotify's journey to building a robust Ray platform with a frictionless developer experience is an inspiring story of innovation and streamlining the machine learning development process. This blog post delves into the details of their approach, covering the challenges they faced, the solutions they implemented, and the key takeaways from their experience. Learn how Spotify leveraged Kubernetes, Ray, and custom SDKs to create a user-friendly Cloud Development Environment (CDE) that simplified the development workflow for ML engineers, researchers, and data scientists.

- Spotify uses Ray to power machine learning applications like recommending personalized content, search ranking, content discovery, etc.
- Spotify built an internal ML platform called Hendrix on top of Ray, deployed on Google Kubernetes Engine. It provides tools and environments for engineers to quickly productionize ML apps.
- Spotify’s new platform, Hendrix, has an SDK with Ray and PyTorch libraries to standardize common ML tasks. It also leverages open source libraries like Hydra, DeepSpeed, etc.
- Spotify created a cloud development environment (CDE) solution to standardize dev environments and avoid issues with local setups. It provides remote cloud environments with GPUs, auto-configured with tools.
- The CDE improved productivity by eliminating environment issues, provided more compute power, and enabled frictionless onboarding for users of diverse backgrounds.
- Key lessons learned: Ensure availability, performance, and security. Allow for customization and extensibility. Use Kubernetes and leverage its features.
- Spotify integrated PyTorch support with Ray for scalable training, hyperparameter tuning, etc. The Ray ecosystem at Spotify continues to drive more ML innovations.

## LinkHow Spotify Built a Robust Ray Platform with a Frictionless Developer Experience

Spotify, a global leader in the audio streaming industry, has long been associated with cutting-edge technology. With over 515 million users and 210 million subscribers across 184 markets, the company relies on advanced machine learning (ML) applications to enhance user experiences and drive innovation. To achieve this, they embarked on a journey to build a robust Ray platform, seamlessly integrated with a frictionless developer experience.

In this blog post, we will dive deep into how Spotify accomplished this feat, breaking down the key elements of their strategy and the insights gained along the way. By the end, you'll have a comprehensive understanding of how Spotify transformed their ML development process, inspiring you to implement similar solutions in your projects.

## LinkBackground

Spotify's machine learning platform plays a pivotal role in the company's operations. It powers various applications, including personalized content recommendations, search result optimizations, and content discovery. To support these ML initiatives, Spotify's ML platform team developed a centralized machine learning platform named Hendrix.

One of the critical components of Hendrix is Ray, a powerful distributed computing framework. To leverage Ray effectively, Spotify needed to create a user-friendly Cloud Development Environment (CDE). The challenge was to provide a unified and straightforward interface that accommodated users with varying backgrounds, from ML engineers to data scientists.

## LinkThe Vision

Spotify's aim was clear: they wanted to simplify the machine learning development process. To achieve this, they envisioned a CDE that would streamline the workflow for different users. The CDE would offer a flexible and efficient way to access managed Ray infrastructure, no matter the user's role or background.

In essence, the vision was to create a frictionless developer experience that enabled users to focus on their ML tasks without being bogged down by setup and configuration complexities.

## LinkThe Technical Solution

Spotify's technical solution for building this frictionless developer experience was a well-thought-out combination of technologies and custom developments. Here are the key components of their approach:

### LinkRay Clusters on Kubernetes

Spotify's machine learning platform is based on Kubernetes, with GPU nodes attached to it through Google Kubernetes Engine (GKE). They used the open-source Kubernetes operator called Kubeflow for orchestration. By deploying Ray clusters on Kubernetes, they provided a scalable and maintainable infrastructure.

### LinkPython SDK with Ray and PyTorch

To provide a seamless experience for their users, Spotify built a custom Python SDK that included Ray and PyTorch libraries. This SDK simplifies the process of accessing Ray infrastructure and accelerates ML application development. It caters to users with various backgrounds and requirements.

### LinkCloud Development Environments

Spotify created Cloud Development Environments (CDEs) to enable users to work in the cloud seamlessly. These CDEs are based on Kubernetes, offering a quick startup, low latency, and the ability to work from any device. Users can instantly set up fully configured development environments, eliminating the need to troubleshoot broken configurations on their local machines.

### LinkCustom vs. Code Extensions

Spotify recognized that users had diverse preferences when it came to their development environment. To cater to this, they developed custom vs. Code extensions. These extensions integrate with other parts of Spotify's ecosystem, allowing users to query internal data endpoints, run custom SQL engines, and more.

### LinkEcosystem Support

Spotify also leveraged Ray's broader ecosystem, integrating popular ML libraries like Hugging Face, DeepSpeed, PyG, and others. This approach ensured that users could access a wide range of tools and solutions to tackle various ML problems.

## LinkLessons Learned

Spotify's journey to building a frictionless developer experience highlighted several key lessons and insights:

### LinkAvailability and Performance

Ensuring high availability and fast startup times is crucial for any developer environment. Spotify emphasized the need for a fast, highly available reverse proxy to optimize the user experience.

### LinkCustomization and Extensibility

Offering a high level of customization for both personal and repository-level configuration is essential. Users should be able to personalize their environment according to their preferences.

### LinkSecurity and Telemetry

Designing with security in mind is vital. Implement features like access control, authorization, and telemetry to provide a secure and observable platform.

### LinkEfficiency and Cost Savings

Streamline the platform to maximize efficiency and reduce costs. Implement features like idle shutdown to save resources and minimize expenses.

### LinkIntegration with Existing Tools

Consider how the new platform will integrate with existing tools and workflows within your organization. A seamless integration can significantly improve the user experience.

## LinkThe Future

Spotify's journey to building a frictionless developer experience doesn't end here. They have ambitious plans for the future, including completing PyTorch development on Ray, optimizing ML compute accelerator allocation, and further platformizing their development environment to offer better accessibility, reliability, and observability.

## LinkConclusion

Spotify's successful transformation of its ML development process is a testament to the power of innovation and thoughtful planning. By combining technologies like Ray, Kubernetes, and custom SDKs, they have created a user-friendly Cloud Development Environment that caters to the needs of ML engineers, researchers, and data scientists.

The key takeaways from their journey are applicable to anyone looking to streamline their development workflow:

**Simplify the Development Process**: Strive to eliminate complexities in the development process and empower users to focus on their tasks.

**Leverage the Right Technologies**: Choose the right technologies and tools that align with your vision and needs.

**Customization and Extensibility**: Provide options for users to customize their environment to suit their preferences.

**Security and Telemetry**: Prioritize security and monitoring for a secure and observable environment.

**Integration and Scalability**: Ensure that the platform integrates seamlessly with existing tools and can scale as your organization grows.

Spotify's journey showcases the potential for organizations to streamline their machine learning development, and the insights gained along the way are valuable for anyone embarking on a similar transformation.

By taking inspiration from Spotify's story, you can make your own developer experience more frictionless, efficient, and user-friendly, ultimately driving innovation in your projects and products.

Sign up now for[ Anyscale endpoints](https://www.anyscale.com/endpoints?utm_source=anyscale&utm_campaign=ray-highlights-2023-blog) and get started fast or[ contact sales](https://www.anyscale.com/signup?utm_source=anyscale&utm_campaign=ray-highlights-2023-blog) if you are looking for a comprehensive overview of the Anyscale platform.

#### Table of contents

- [Key Takeaway](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#key-takeaway)
- [How Spotify Built a Robust Ray Platform with a Frictionless Developer Experience](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer-experience)
- [Background](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#background)
- [The Vision](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#the-vision)
- [The Technical Solution](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#the-technical-solution)
- [Ray Clusters on Kubernetes](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#ray-clusters-on-kubernetes)
- [Python SDK with Ray and PyTorch](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#python-sdk-with-ray-and-pytorch)
- [Cloud Development Environments](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#cloud-development-environments)
- [Custom vs. Code Extensions](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#custom-vs.-code-extensions)
- [Ecosystem Support](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#ecosystem-support)
- [Lessons Learned](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#lessons-learned)
- [Availability and Performance](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#availability-and-performance)
- [Customization and Extensibility](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#customization-and-extensibility)
- [Security and Telemetry](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#security-and-telemetry)
- [Efficiency and Cost Savings](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#efficiency-and-cost-savings)
- [Integration with Existing Tools](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#integration-with-existing-tools)
- [The Future](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#the-future)
- [Conclusion](https://www.anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer#conclusion)

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
