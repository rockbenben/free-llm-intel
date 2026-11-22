---
vendor: aws_bedrock
title: Scale visual production using Stability AI Image Services in Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/scale-visual-production-using-stability-ai-image-services-in-amazon-bedrock
date: 2025-09-18
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: d1223ee093e6
---

# Scale visual production using Stability AI Image Services in Amazon Bedrock

*This post was written with Alex Gnibus of Stability AI.*

Stability AI Image Services are now available in [Amazon Bedrock](https://aws.amazon.com/bedrock/), offering ready-to-use media editing capabilities delivered through the Amazon Bedrock API. These image editing tools expand on the capabilities of Stability AI’s Stable Diffusion 3.5 models (SD3.5) and Stable Image Core and Ultra models, which are already [available in Amazon Bedrock](https://aws.amazon.com/bedrock/stability-ai/) and have set new standards in image generation.

The professional creative production process consists of multiple editing steps to get the exact output needed. With Stability AI Image Services in Amazon Bedrock, you can modify, enhance, and transform existing images without jumping between multiple systems or sending files to external services. Everything runs through the same Amazon Bedrock experience you’re already using. The business impact can be immediate for teams that produce visual content at scale.

In this post, we explore examples of how these tools enable precise creative control to accelerate professional-grade visual content.

## Editing tools now available in Amazon Bedrock

Stability AI Image Services span 13 tools across three categories: Edit, Upscale, and Control. Each tool handles specific editing tasks that typically require specialized software or manual intervention.

### Edit: Advanced capabilities for granular editing steps

The tools in the Edit category make complex editing tasks more accessible and efficient.

The suite begins with fundamental yet powerful retouching tools. The Erase Object tool, for example, removes unwanted elements from images while intelligently maintaining background consistency. The following animation showcases the Erase Object tool removing a mannequin from a product shot while preserving the background. The tool can transform a source image based on a mask image or derive the mask from the source image’s alpha channel.

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-1.gif)

The Remove Background tool automatically isolates subjects with precision. This enables the creation of clean, professional product listings with consistent backgrounds or a variety of lifestyle settings, which is a game changer for ecommerce.

The following example illustrates the removal of an image background, while preserving details of a furniture product in the foreground.

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-2.gif)

The Search and Recolor and Search and Replace tools target specific elements within images for modification. Search and Recolor changes object colors; for example, showing different colorways of a dress without new photoshoots. In the following illustration, Search and Recolor changes the color swatch on furniture.

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-3.gif)

Search and Replace can swap objects entirely, which is useful for updating seasonal elements in marketing materials or replacing products. The following is an application of Search and Replace for virtual try-on experiences.

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-4.gif)

The Inpaint tool intelligently modifies images by filling in or replacing specified areas with new content based on the content of a mask image. In contrast, the Outpaint tool generates content to fill an image in any direction. Compared to other automated or manual attempts to expand the content in an image, the Outpaint tool minimizes artifacts and signs that the original image has been edited.

### Upscale: Enhance images for professional quality

Three of the new Stability AI Image Services offer different approaches to image upscaling and enhancement, each tailored to specific use cases.

The Creative Upscale tool enhances resolution while adding AI-driven detail enhancement. This tool increases both pixel count and visual appeal, making it suitable for high-impact marketing materials. Standard product shots become billboard-ready images through intelligent detail addition and vibrancy enhancement.

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-5.gif)

For situations where maintaining the integrity of the original image is crucial, the Conservative Upscale tool offers a more nuanced approach. It increases resolution while preserving the original image’s details and character. This service can upscale images by 20 to 40 times, up to a 4-megapixel output image with minimal alteration to the original image.

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-6.gif)

Completing the trio of tools is Fast Upscale. This Upscale tool is faster than the previous two and is ideal for enhancing the quality of compressed images, making it suitable for social media posts and other applications.

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-7.gif)

### Control: Structural and stylistic precision

This category of tools provides precise manipulation of image structure and style through three specialized tools.

The Sketch tool transforms sketch-style renderings into photorealistic concepts. Architecture firms might use this to convert conceptual drawings into realistic visualizations, and apparel brands to turn design sketches into product mockups. The tool helps accelerate the creative production process from initial concepts to final visual execution.

In this example, the Sketch tool transforms a building architecture drawing to help real estate developers visualize the concept against a cityscape.

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-8.gif)

In another example, the Sketch tool transforms a mannequin drawing into a photorealistic model shot.

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-9.gif)

The Structure tool maintains the structural elements of input images while allowing content modification. This tool helps preserve layouts, compositions, and spatial relationships while changing subjects or styles. Creative teams can use the Structure tool to recreate scenes with different subjects or render new characters while maintaining consistent framing.

The following example demonstrates the Structure tool transforming a workshop scene into a new scene while preserving the composition and spatial relationships.

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-10.gif)

The Style Guide and Style Transfer tools help marketing teams produce new images that align with brand style and guidelines. The Style Guide tool takes artistic styles and colors from a reference style image and generates new images based on text prompts.

In the following example, the Style Guide tool takes clues from a brand’s color palette and textures and generates new images matching brand identity.

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-11.gif)

The Style Transfer tool uses visual characteristics from reference images to transform existing images, while preserving the original composition. For example, a home decor retailer can transform product imagery from modern minimalist to traditional styles without new photography. Marketing teams could create seasonal variations by applying different visual styles to existing product catalogs.

## Solution overview

To demonstrate Stability AI Image Services in Amazon Bedrock, let’s walk through an example using a Jupyter notebook found in the [GitHub repo](https://github.com/aws-samples/stabilityai-sample-notebooks/tree/main/stability-ai-image-services).

## Prerequisites

To follow along, you must have the following prerequisites:

- An AWS account.
- AWS credentials configured for creating and accessing Amazon Bedrock and [Amazon SageMaker AI](https://aws.amazon.com/sagemaker/ai/) resources.
- An [AWS Identity and Access Management](https://aws.amazon.com/iam/) (IAM) execution role for SageMaker AI, which has the `AmazonSageMakerFullAccess` and `AmazonBedrockLimitedAccess` AWS managed policies attached. For more details, see [How to use SageMaker AI execution roles](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html).
- A [SageMaker notebook instance](https://docs.aws.amazon.com/sagemaker/latest/dg/nbi.html).
- Stability AI Image Services model access, which you can request through the Amazon Bedrock console. Refer to [Access Amazon Bedrock foundation models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) for more details.

## Create a SageMaker AI notebook instance

Complete the following steps to create a [SageMaker AI notebook](https://aws.amazon.com/sagemaker/ai/notebooks/) instance, which can be used to run the sample notebook:

- On the SageMaker AI console, in the navigation pane, under **Applications and IDEs**, choose **Notebooks**.
- Choose **Create notebook instance**.
- For **Notebook instance name**, enter a name for your notebook instance (for example, `ai-images-notebook-instance`).
- For **Notebook Instance type**, choose **ml.t2.medium**.
- For **Platform identifier**, choose **Amazon Linux 2**.
- For **IAM role**, choose either an existing IAM role, which has the `AmazonSageMakerFullAccess` and `AmazonBedrockLimitedAccess` policies attached, or choose **Create a new role**.
- Note the name of the IAM role that you chose.
- Leave other settings as default and choose **Create notebook instance**.

After a few minutes, SageMaker AI creates a notebook instance, and its status changes from **Pending** to **InService**.

## Confirm the IAM role for the notebook instance has the necessary permissions

Complete the following steps to verify that the SageMaker AI execution role that you assigned to the notebook instance has the correct permissions:

- On the IAM console, in the navigation pane, under **Access management**, choose **Roles**.
- In the **Roles** search bar, enter the name of the SageMaker AI execution role that you used when creating the notebook instance.
- Choose the IAM role.
- Under **Permissions policies**, verify that the AWS managed policies `AmazonSageMakerFullAccess` and `AmazonBedrockLimitedAccess` are present.
- (Optional) If either policy is missing, choose **Add permissions**, then choose **Attach policies** to attach the missing policy.  In the **Other permissions policies** search bar, enter the policy name. Select the policy, then chose **Add permissions**.

## Run the notebook

Complete the following steps to run the notebook:

- On the SageMaker AI console, in the navigation pane, under **Applications and IDEs**, choose **Notebooks**.
- Choose the newly created `ai-images-notebook-instance` notebook instance.
- Wait for the notebook to be in **InService** status.
- Choose the **Open JupyterLab** link to launch JupyterLab in a new browser tab.
- On the **Git** menu, choose **Clone a Repository**.
- Enter the URI `https://github.com/aws-samples/stabilityai-sample-notebooks.git` and select **Include submodules** and **Download the repository**.
- Choose **Clone**.
- On the **File** menu, choose **Open from path**.
- Enter the following:
`stabilityai-sample-notebooks/stability-ai-image-services/stability-ai-image-services-sample-notebook.ipynb`
- Choose **Open**.
- When prompted, choose the kernel `conda_python3`, then choose **Select**.
- Run through each notebook cell to experience Stability AI Image Services in Amazon Bedrock.

## Clean up

To avoid ongoing charges, stop the `ai-images-notebook-instance` SageMaker AI notebook instance that you created in this walkthrough:

- On the SageMaker AI console, in the navigation pane, under **Applications and IDEs**, choose **Notebooks**.
- Choose the `ai-images-notebook-instance` SageMaker AI notebook instance that you created.
- Choose **Actions**, then choose **Stop**.

After a few minutes, the notebook instance transitions from **Stopping** to **Stopped** status.

- Choose **Actions**, then **Delete**.

After a few seconds, SageMaker AI deletes the notebook instance.

For more details, refer to [Clean up Amazon SageMaker notebook instance resources](https://docs.aws.amazon.com/sagemaker/latest/dg/ex1-cleanup.html).

## Conclusion

The availability of [Stability AI Image Services in Amazon Bedrock](https://aws.amazon.com/bedrock/stability-ai/) is an exciting step forward for visual content creation and manipulation, with particularly time-saving implications for professional creative teams at enterprises.

For example, in media and entertainment, creators can rapidly enhance scenes and create special effects, and marketing teams can generate multiple campaign variations effortlessly. Retail and ecommerce businesses can streamline product photography and digital catalog creation, and gaming developers can prototype environments more efficiently. Architecture firms can visualize design concepts instantly, and educational institutions can create more engaging visual content.

With these tools, businesses of different sizes can produce professional-grade, highly engaging visual content with efficiency and creativity. These tools can streamline operations, reduce costs, and open new creative possibilities, helping brands tell their stories more effectively and engage customers in more compelling ways.

To get started, check out [Stability AI models in Amazon Bedrock](https://aws.amazon.com/bedrock/stability-ai/) and the AWS Samples [GitHub repo](https://github.com/aws-samples/stabilityai-sample-notebooks/tree/main/stability-ai-image-services).

### About the authors

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/09/ml-19647-12.jpeg)Alex Gnibus** is a Product Marketing Manager at Stability AI, connecting the dots between cutting-edge research breakthroughs and practical use cases. With experience spanning from creative agencies to deep enterprise tech, Alex brings both technical expertise and an understanding of the challenges that professional creative teams can solve with generative AI.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/09/ml-19647-13.png)Isha Dua** is a Senior Solutions Architect based in the San Francisco Bay Area. She helps AWS Enterprise customers grow by understanding their goals and challenges and guiding them on how they can architect their applications in a cloud-based manner while making sure they are resilient and scalable. She’s passionate about machine learning technologies and environmental sustainability.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/09/ml-19647-14.png)Fabio Branco** is a Senior Customer Solutions Manager at Amazon Web Services (AWS) and strategic advisor helping customers achieve business transformation, drive innovation through generative AI and data solutions, and successfully navigate their cloud journeys. Prior to AWS, he held Product Management, Engineering, Consulting, and Technology Delivery roles across multiple Fortune 500 companies in industries, including retail and consumer goods, oil and gas, financial services, insurance, and aerospace and defense.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/15/solpatel-headshot-2-100x100-1.jpg)Suleman Patel** is a Senior Solutions Architect at Amazon Web Services (AWS), with a special focus on machine learning and modernization. With expertise in both business and technology, Suleman helps customers design and build solutions that tackle real-world business problems. When he’s not immersed in his work, Suleman loves exploring the outdoors, taking road trips, and cooking up delicious dishes in the kitchen.
