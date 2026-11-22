---
vendor: aws_bedrock
title: Exploring the zero operator access design of Mantle
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/exploring-the-zero-operator-access-design-of-mantle
date: 2025-12-23
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: e7d7b8e59c7a
---

# Exploring the zero operator access design of Mantle

At Amazon, our culture, built on honest and transparent discussion of our growth opportunities, enables us to focus on investing and innovating to continually raise the standard on our ability to deliver value for our customers. Earlier this month, we had the opportunity to share an example of this process at work in Mantle, our next-generation inference engine for [Amazon Bedrock](https://aws.amazon.com/bedrock). As generative AI inferencing and fine-tuning workloads continue to evolve, we need to evolve how we serve inferencing to our customers in an optimized way, which leads to the development of Mantle.

As we set out to reimagine the architecture of our next generation inferencing engine, we made raising the bar on security our top priority. AWS shares our customers’ unwavering focus on security and data privacy. This has been central to our business from the start, and it was particularly in focus from the earliest days of Amazon Bedrock. We’ve understood from the start that generative AI inference workloads present an unprecedented opportunity for customers to harness the latent value of their data, but with that opportunity comes the need to ensure the highest standards in security, privacy, and compliance as our customers build generative AI systems that process their most sensitive data and interact with their most critical systems.

As a baseline, Amazon Bedrock is designed with the same operational security standards that you see across AWS. AWS has always used a least privilege model for operations, where each AWS operator has access to only the minimum set of systems required to do their assigned task, limited to the time when that privilege is needed. Any access to systems that store or process customer data or metadata is logged, monitored for anomalies, and audited. AWS guards against any actions that would disable or bypass these controls. Additionally, on Amazon Bedrock your data is never used to train any models. Model providers have no mechanism to access customer data, because inferencing is done only within the Amazon Bedrock-owned account that model providers don’t have access to. This strong security posture has been a key enabler for our customers to unlock the potential of generative AI applications for their sensitive data.

With Mantle, we raised the bar even further. Following the approach of the [AWS Nitro System](https://docs.aws.amazon.com/whitepapers/latest/security-design-of-aws-nitro-system/no-aws-operator-access.html), we have designed Mantle from the ground up to be zero operator access (ZOA), where we have intentionally excluded any technical means for AWS operators to access customer data. Instead, systems and services are administered using automation and secure APIs that protect customer data. With Mantle, there is no mechanism for any AWS operator to sign in to underlying compute systems or access any customer data, such as inference prompts or completions. Interactive communication tools like Secure Shell (SSH), [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html), and serial consoles aren’t installed anywhere in Mantle. Additionally, all inference software updates need to be signed and verified before they can be deployed into the service, ensuring that only approved code runs on Mantle.

Mantle uses the recently released [EC2 instance attestation capability](https://aws.amazon.com/about-aws/whats-new/2025/09/aws-announces-ec2-instance-attestation/) to configure a hardened, constrained, and immutable compute environment for customer data processing. The services in Mantle that are responsible for handling model weights and conducting inference operations on customer prompts are further backed by the high assurance of cryptographically signed attestation measurements from the [Nitro Trusted Platform Module (NitroTPM)](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/nitrotpm.html).

When a customer calls a Mantle endpoint (for example, `bedrock-mantle.[regions].api.aws`) such as those that serve the [Responses API](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-mantle.html) on Amazon Bedrock, customer data (prompts) leaves the customer’s environment through TLS, and is encrypted all the way to the Mantle service, which operates with ZOA. Throughout the entire flow and in Mantle, no operator, whether from AWS, the customer, or a model provider can access the customer data.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/23/ML-20238-image-1.jpeg)

## Looking forward

Mantle’s ZOA design exemplifies the long-term commitment of AWS to the security and privacy of our customers’ data. It’s this focus that has enabled teams across AWS to invest in further raising the bar for security. At the same time, we’ve made the foundational confidential computing capabilities that we internally use at Amazon, such as NitroTPM Attestation, available to all customers to use on [Amazon Elastic Compute Cloud (Amazon EC2)](https://aws.amazon.com/ec2).

We’re not stopping here; we’re committed to continuing to invest in enhancing the security of your data and to providing you with more transparency and assurance on how we achieve this.

### About the authors

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/04/08/aliguori.jpeg)**Anthony Liguori** is an AWS VP and Distinguished Engineer for Amazon Bedrock, and the lead engineer for Mantle.
