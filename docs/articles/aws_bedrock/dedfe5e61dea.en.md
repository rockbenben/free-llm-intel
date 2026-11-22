---
vendor: aws_bedrock
title: Reimagine marketing at Volkswagen Group with generative AI
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/reimagine-marketing-at-volkswagen-group-with-generative-ai
date: 2026-03-30
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 1faa0157136b
---

# Reimagine marketing at Volkswagen Group with generative AI

*This post is cowritten by Sebastian Angersbach, Philip Trempler, and Weiran Zhang from Volkswagen Group.*

[Volkswagen Group](https://www.volkswagen-group.com/en) stands as one of the world’s largest automotive manufacturers, delivering 6.6 million vehicles in the first nine months of 2025. The Group comprises ten distinct brands from five European countries: Volkswagen, Volkswagen Commercial Vehicles, ŠKODA, SEAT, CUPRA, Audi, Lamborghini, Bentley, Porsche, and Ducati. In 2025, the AWS Generative AI Innovation Center worked with Volkswagen Group’s marketing and technical teams to build a solution that could harness generative AI’s speed and scale while maintaining the brand precision that defines Volkswagen Group. The result is an end-to-end marketing image generation and evaluation pipeline, with image generation models hosted on Amazon SageMaker AI endpoints and image evaluation powered by Amazon Bedrock. The following diagram shows the end-to-end marketing image generation and evaluation pipeline.

![Architecture diagram showing the end-to-end marketing image generation and evaluation pipeline, from image generation on Amazon SageMaker AI to evaluation on Amazon Bedrock](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/23/ML-18778-vw-1.png)

In this post, we explore the challenges that Volkswagen Group faced in producing brand-compliant marketing assets at scale. We walk through how we built a generative AI solution that generates photorealistic vehicle images, validates technical accuracy at the component level, and helps enforce brand guideline compliance alignment across the ten brands.

## The challenge – global scale meets brand precision

For Volkswagen Group’s marketing teams, this scale creates an extraordinary challenge: producing thousands of marketing assets annually while making sure that every image reflects the exact brand standards that customers have come to expect. A single vehicle launch might require hundreds of variations—different angles, environments, lighting conditions, and regional adaptations—each traditionally requiring months of production work.

On-location photo shoots for a single model could cost upwards of six figures. They require physical prototypes, professional studio setups with precise lighting rigs, and complex logistics to transport vehicles between locations for different environmental shots. Beyond the production costs, the real bottleneck emerged in the validation process: making sure each asset aligned with its brand’s unique voice and visual guidelines before it could reach the market.

What if Volkswagen could generate photorealistic vehicle images in minutes instead of weeks? The potential was clear—faster time-to-market, dramatic cost reductions, and the ability to create personalized content at scale. But for a premium automotive brand, there was a non-negotiable constraint: every generated image had to be indistinguishable from professional photography and perfectly aligned with brand guidelines.

The challenge extended beyond technical accuracy. Each of the Group’s ten brands has its own visual language: the understated elegance of Bentley demands different staging than the performance-focused aesthetic of Porsche or the accessible modernity of ŠKODA. Solutions would need to generate high-quality images and also systematically validate that each asset honored its brand’s unique identity.

## Generating on-brand vehicle images at scale

The first step in Volkswagen’s generative AI journey was deceptively simple: could foundation models (FMs) generate photorealistic images of their vehicles? Initial experiments with base diffusion models revealed two critical gaps. First, while these models could produce impressive automotive imagery, they lacked decades of Volkswagen design language. The tiniest features matter: the exact texture of a grille mesh, the precise geometry of headlight housings, the specific wheel spoke patterns for each model line. The models would generate a Volkswagen, but with generic wheels and grille patterns that didn’t match an actual model year. Second, base models had no knowledge of unreleased vehicles. They couldn’t generate images of next year’s models still under development, severely limiting their utility for forward-looking marketing campaigns.

The solution required fine-tuning foundation models on Volkswagen’s proprietary visual assets. Working with [SolidMeta](https://solidmeta.io/), the team used DreamBooth fine-tuning techniques with training data collected from digital twins in NVIDIA Omniverse. The following diagram illustrates this process for the Volkswagen Tiguan. DreamBooth training works in two parts: first, the model learns from VW Tiguan images paired with a unique identifier token *[VW Tiguan] *that teaches it this specific vehicle. Second, the model trains on generic car images to preserve its general capabilities and help prevent overfitting to the training set.

![Diagram illustrating the DreamBooth fine-tuning process for the Volkswagen Tiguan, showing how the model learns from VW Tiguan images paired with a unique identifier token alongside generic car images](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/23/ML-18778-vw-2.png)

With this approach, we can generate high-quality training data with precise control over vehicle specifications and environmental conditions. The team deployed the Flux.1-Dev diffusion model enhanced with a LoRA (Low-Rank Adaptation) adapter on an Amazon SageMaker AI endpoint. This approach allowed them to specialize the model’s understanding of the VW design language, down to grille textures and specific trim options, while maintaining the base model’s general image generation capabilities.

The architecture used the managed infrastructure of Amazon SageMaker AI for both training and inference. The customized model was deployed to Amazon SageMaker AI endpoints configured for asynchronous inference on ml.g5.2xlarge GPU instances handling the computationally intensive diffusion process. The team configured the pipeline for asynchronous inference with automatic scaling, allowing it to handle variable workloads efficiently.

But generating images required more than a fine-tuned model, it required the right prompts. The team quickly discovered that effective prompts for automotive marketing imagery required specialized vocabulary and style modifiers that most users lacked. A marketing team member might input “silver VW in a forest,” but generating brand compliance-aligned imagery required far more specificity: lighting conditions, camera angles, environmental details, and precise descriptions of vehicle features.

To bridge this gap, Volkswagen implemented an automated prompt optimization system using Amazon Nova Lite. Before each image generation request, Nova Lite helps enhance the user’s input prompt, expanding it with brand-appropriate details, technical specifications, and stylistic elements drawn from VW’s marketing guidelines. A simple prompt becomes a comprehensive description that guides the diffusion model toward brand compliance-aligned outputs.

The fine-tuned model generated images with accurate grille textures, correct wheel designs specific to each trim level, and proper vehicle proportions unique to each VW brand. The prompt optimization facilitated consistency in style and tone across different users and use cases. Marketing teams could now generate high-quality vehicle renderings quicker – including for unreleased models that would have been impossible to visualize with traditional methods.

![Side-by-side comparison of base model output versus fine-tuned model output, showing improved accuracy in vehicle details such as grille textures and wheel designs](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/24/ML-18778-comparison.png)

But a new challenge emerged: at scale, how do you validate that every generated image meets Volkswagen’s exacting standards? Manual inspection of each image wasn’t feasible when generating hundreds or thousands of variations. The team needed an automated quality control system that could evaluate images with the same precision as a human brand expert—and do it at machine speed.

## Automated quality control – component-level evaluation

The team’s first instinct was to leverage established image quality metrics like PSNR (Peak Signal-to-Noise Ratio) and SSIM (Structural Similarity Index). These metrics quickly proved inadequate. They evaluated entire images including backgrounds, making it impossible to isolate the vehicle itself. More critically, they couldn’t identify which specific components were wrong. A generated image might score acceptably while having an incorrect grille pattern or wrong wheel design—precisely the details that matter most. The numerical scores often failed to align with human perception: images that looked obviously wrong to experts might score well on traditional metrics.

The team needed a different approach: evaluate vehicles the way human experts do, by examining individual components with detailed criteria specific to automotive design.

The solution combined computer vision segmentation with vision-language models (VLMs) as automated judges. The process begins by breaking down both reference photographs and generated images into individual components: wheels, grille, headlights, windshield, mirrors, doors, bumpers, and logos. The following real, photographic images of the Volkswagen Tiguan show this segmentation from four standard angles with bounding boxes highlighting each component using a zero-shot image segmentation model.

![Reference photographs of the Volkswagen Tiguan from four standard angles with bounding boxes highlighting individual components such as wheels, grille, headlights, and mirrors](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/23/ML-18778-vw-4.png)

The following figure shows the same process applied to a generated image:
![Generated image of the Volkswagen Tiguan with bounding boxes highlighting segmented components for evaluation against reference images](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/23/ML-18778-vw-5.png)
 This segmentation uses the open source Florence-2 model, hosted on an Amazon SageMaker AI endpoint. With this, the team could specify exactly which components to detect rather than relying on generic object detection. To handle occasional errors, the pipeline includes a large language model (LLM)-aided verification step using Nova Lite to confirm each extracted segment matches its intended label. After the components are segmented and paired, they’re presented side-by-side for evaluation as shown in the following figure.

![Side-by-side comparison of segmented vehicle components from reference and generated images, paired for evaluation](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/23/ML-18778-vw-6.png)

The team developed component-specific criteria: for wheels, this includes spoke design, center cap details, and rim profile; for grilles, it covers shape, texture, and logo positioning; for headlights, it evaluates housing, trim, and internal structure. Claude 4.5 Sonnet on Amazon Bedrock acts as the VLM judge, applying these criteria to each component pair. The model receives a calibration guide defining scores from 1 (obvious flaws visible to casual viewers) to 5 (no differences detectable even by experts). Claude evaluates each criterion individually with detailed reasoning. The following figure demonstrates this for a headlight evaluation.
![Headlight evaluation example showing Claude scoring housing, trim, and internal structure criteria with detailed reasoning](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/23/ML-18778-vw-7.png)
 Housing and trim receive perfect 5/5 scores, but internal structure receives 4/5, with the explanation: “the AI-generated image shows more detail in the internal structure, which might not be accurate according to the provided reference image.” This granular feedback provides exactly what Volkswagen needed—specific, actionable insights about where generated images deviate from reference specifications.

The pipeline is orchestrated through AWS Step Functions, with Amazon S3 providing storage for reference images, generated outputs, and evaluation results. The system can aggregate scores across multiple images to identify systematic issues—for example, discovering that certain angles consistently score lower, indicating a need for additional training data.

This component-based approach solved the technical accuracy challenge. But facilitating product correctness was only half the battle. Volkswagen also needed to validate that generated images honored each brand’s unique identity and marketing guidelines.

## Facilitating brand guideline compliance alignment

Component-level accuracy solved the technical challenge of whether a generated grille or wheel matched specifications. But Volkswagen’s brand standards extend far beyond technical correctness. Each of the Group’s ten brands has carefully crafted guidelines governing everything from color palettes and lighting conditions to environmental contexts and emotional tone. A technically perfect image of a Porsche could still violate brand guidelines if staged incorrectly or lit inappropriately.

Volkswagen’s brand identity emphasizes realistic, attainable settings with softer evening golden hour tones. Images should show vehicles in urban streets, countryside roads, family driveways—not fantastical or overly stylized environments. The staging must feel authentic: vehicles parked legally, positioned naturally, and presented in ways that align with the brand’s values of quality, reliability, and thoughtful engineering.

![Example of Volkswagen brand identity guidelines showing realistic vehicle staging with golden hour lighting in an everyday setting](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/23/ML-18778-vw-8.png)

The complexity multiplies when considering regional variations. What’s compliant in one industry may violate regulations or cultural norms in another. Consider marketing the trunk feature of the Volkswagen Touareg. In Sweden, local law requires a dog to be transported in a safety harness or transport box. If the German marketing team uses an image showing a dog loose in the trunk, that content is legally non-compliant in Sweden. Multiply this by thousands of micro-regulations across dozens of markets, and manual review becomes impossible to scale.

The team developed an LLM-based brand guideline evaluation system to systematically assess these subjective elements. The approach uses Claude 4.5 Sonnet on Amazon Bedrock, providing it with both the generated image and Volkswagen’s comprehensive brand guidelines as context. The model evaluates multiple dimensions: brand identity and design language, color representation, image style and tone, vehicle presentation, staging and environment, perspective and focal length, and compliance with regional regulations. The following figure shows an example of a brand compliance analysis.

![Example of a brand compliance analysis showing evaluation scores across multiple dimensions including brand identity, color representation, and staging](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/23/ML-18778-vw-9.png)

Unlike the component evaluation system that compares against reference images, this evaluation is criteria-based. The model assesses whether the image honors brand-specific elements like Volkswagen’s signature color palette, whether the emotional tone is “disarmingly honest, genuinely human, and surprisingly empathetic” for story-driven images, and whether the staging feels authentic rather than overly produced.

The system proved particularly valuable for catching regional compliance issues that would be nearly impossible to identify manually. In one example, the system evaluated an image intended for UK industry localization. While the image successfully showed a right-hand drive vehicle in a British urban setting, the brand guideline evaluation flagged a critical issue. The following images show an example of regional compliance evaluation.

![Regional compliance evaluation example showing a UK-localized image flagged for using a European continental license plate instead of a UK plate](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/23/ML-18778-vw-10.png)

The model assigned a 2/5 score to “Logos and License Plates,” explaining that the license plate used a European continental style and identified it as a German plate starting with “WOI”. This detail would immediately signal to UK customers that the image wasn’t properly localized. This kind of subtle inconsistency could undermine the authenticity that Volkswagen works so hard to maintain, yet could go unnoticed in a manual review of hundreds of images.

By combining component-level technical evaluation with brand guideline compliance checking, Volkswagen created a comprehensive quality control system. Generated images are automatically filtered for both accuracy and brand alignment before reaching marketing teams. The system provides detailed feedback on both dimensions, allowing teams to quickly identify which images meet the standards and understand exactly why others don’t.

The team recognized an opportunity to go further. Could they fine-tune the evaluation models themselves to better align with Volkswagen’s specific brand expertise? Could they teach the AI judges to think more like Volkswagen’s own marketing experts?

## Continuous improvement – customizing Nova Pro for brand evaluation

The brand guideline evaluation system using Claude 4.5 Sonnet provided strong results, but the team saw an opportunity to go further. Could they customize a foundation model specifically for Volkswagen’s brand standards, teaching it to evaluate images the way the company’s own marketing experts would?

One approach is Supervised Fine-Tuning (SFT), but this typically requires thousands of labeled examples. Getting marketing analysts at Volkswagen Group to manually label thousands of images would be impractical and expensive. The team needed a more efficient solution.

Their insight was to use the brand guidelines themselves to generate synthetic training data. Using an LLM, they generated 1,000 image prompts designed to produce brand compliance-aligned images and 1,000 prompts crafted to violate specific brand guidelines. The following illustration shows a compliance-aligned and non-compliance-aligned prompt example as part of the synthetic training data generation process.

![Illustration showing a compliance-aligned and non-compliance-aligned prompt example as part of the synthetic training data generation process](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/23/ML-18778-vw-11.png)

Because the team knew which prompts were compliance-aligned and which weren’t based on how they were constructed, they could automatically generate the corresponding evaluation text for each image as shown in the following illustration. This created complete SFT training pairs: image input paired with the correct brand evaluation output. ![Illustration showing how compliance-aligned and non-compliance-aligned prompts are paired with corresponding evaluation text to create SFT training data](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/23/ML-18778-vw-12.png)

With this synthetic dataset, the team used the Amazon Nova Model Customization SFT recipe running on Amazon SageMaker Training Jobs to customize Nova Pro. The following figure illustrates this process end to end.

![End-to-end diagram of the Nova Pro customization process using synthetic training data and Amazon SageMaker Training Jobs](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/03/23/ML-18778-vw-13.png)

The fine-tuning process taught the model to recognize and articulate brand compliance issues specific to Volkswagen’s guidelines, from color palette adherence to environmental authenticity to regional regulatory requirements. The customized model’s reasoning became more precise, referencing Volkswagen-specific design language and brand values in its evaluations.

This approach offers a scalable path forward. The same technique can be extended to each of Volkswagen Group’s ten brands, customizing evaluation models for the unique voice and guidelines of Porsche, Audi, ŠKODA, and others. As the company generates more real-world data and gathers feedback from marketing teams, these customized models can be continuously refined, creating an evaluation system that can grow more aligned with brand expertise over time.

> “By combining our domain expertise with AWS, we built a generative AI platform that makes our marketing faster, smarter, and safer.”
>         – Sebastian Angersbach, Head of IT Strategy & Innovation, Volkswagen Group Services

### Acknowledgements

Special thanks to Egor Krasheninnikov, Satyam Saxena, and Huong Vu for their invaluable contributions and guidance.

## About the Authors
