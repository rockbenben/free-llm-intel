---
vendor: aws_bedrock
title: Exploring accessible audio descriptions with Amazon Nova
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/exploring-accessible-audio-descriptions-with-amazon-nova
date: 2025-06-13
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 057fa28569cf
---

# Exploring accessible audio descriptions with Amazon Nova

According to the World Health Organization, [more than 2.2 billion people globally have vision impairment](https://www.who.int/news-room/fact-sheets/detail/blindness-and-visual-impairment#:~:text=Prevalence-,Globally%2C%20at%20least%202.2%20billion%20people%20have%20a%20near%20or,has%20yet%20to%20be%20addressed.). For compliance with disability legislation, such as the [Americans with Disabilities Act](https://www.ada.gov/) (ADA) in the United States, media in visual formats like television shows or movies are required to provide accessible formats to visually disabled people. This often comes in the form of audio description tracks that narrate key visual elements of the film or show. These tracks are time-consuming and expensive to create. They require a host of specialists, including script writers, engineers, and voice actors, and, according to the [International Documentary Association](https://www.documentary.org/blog/5-things-consider-when-adding-audio-description-and-captioning-your-documentary-film#:~:text=Costs%20usually%20range%20on%20average,and%20everywhere%20by%20end%20users.), can cost upwards of $25 per minute. This leads to the natural question, is it possible to automate this process with the help of [generative AI](https://aws.amazon.com/generative-ai/) offerings in [Amazon Web Services (AWS)](https://aws.amazon.com/)?

While the number of audio-described television shows and movies is increasing, the majority of video content remains inaccessible to visually disabled audiences. The biggest barrier to increasing the amount of audio described content is the cost. Minimizing that barrier with GenAI would spur the creation of more accessible content.

The [Amazon Nova Foundation Models](https://aws.amazon.com/ai/generative-ai/nova/?gclid=CjwKCAiA-ty8BhA_EiwAkyoa33w9TlOtBTRQ8LYw-0V_BrK4khqzEX539Mrj5E9njcPe0-ZvqQGUPBoCr2UQAvD_BwE&trk=36201f68-a9b0-45cc-849b-8ab260660e1c&sc_channel=ps&ef_id=CjwKCAiA-ty8BhA_EiwAkyoa33w9TlOtBTRQ8LYw-0V_BrK4khqzEX539Mrj5E9njcPe0-ZvqQGUPBoCr2UQAvD_BwE:G:s&s_kwcid=AL!4422!3!692006004844!e!!g!!amazon%20nova!21048268689!159639953895) family, available through [Amazon Bedrock](https://aws.amazon.com/bedrock/), includes three multimodal [foundational models](https://aws.amazon.com/what-is/foundation-models/) (FMs) that could be used for this purpose:

- **Amazon Nova Lite (GA)** – A low-cost multimodal model that’s lightning-fast for processing image, video, and text inputs
- **Amazon Nova Pro (GA)** – A highly capable multimodal model with a balanced combination of accuracy, speed, and cost for a wide range of tasks
- **Amazon Nova Premier** **(GA)** – Our most capable model for complex tasks and a teacher for model distillation

In this post, we demonstrate how we combined Amazon Nova, [Amazon Rekognition](https://aws.amazon.com/rekognition/), and [Amazon Polly](https://aws.amazon.com/polly/) to automate the creation of accessible audio descriptions for video content. This approach can significantly reduce the time and cost required to make videos accessible for visually disabled audiences. However, it is important to note that this post is an early experiment in automating the creation of audio descriptions. It doesn’t provide a complete, deployment-ready solution.

To demonstrate the possibilities, we share pseudocode snippets and guidance in sequential order, in addition to detailed explanations and links to resources. The automated workflow described in the post involves analyzing video content, generating text descriptions, and narrating them using AI voice generation. By the end of this post, you’ll understand the use of key tools that you can use as you continue to experiment to create a production-ready solution for your use cases.

## Solution overview

The following architecture diagram demonstrates the end-to-end workflow of the proposed solution. We will describe each component in-depth in the later sections of this post, but note that you can define the logic within a single script. You can then run your script on an [Amazon Elastic Compute Cloude (Amazon EC2)](https://aws.amazon.com/ec2) instance or on your local computer. For this post, we assume that you will run the script on an [Amazon SageMaker notebook](https://docs.aws.amazon.com/sagemaker/latest/dg/nbi.html).

![End-to-end AWS workflow demonstrating video content analysis using AI services to generate text descriptions and audio narration](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/02/image-1.jpeg)

As you experiment with generating audio descriptions, be mindful of the architectural components of the solution. In a production environment, being mindful of any potential scaling, security, and storage elements is important because the architecture might begin to resemble something more complex than the basic solution architecture diagram shown here.

## Services used

The services shown in the architecture diagram include:

- **Amazon S3** – [Amazon Simple Storage Service (Amazon S3)](https://aws.amazon.com/s3) is an object storage service that provides scalable, durable, and highly available storage. In this example, we use Amazon S3 to store the video files (input) and scene description (text files) and audio description (MP3 files) output generated by the solution. The script starts by fetching the source video from an S3 bucket.
- **Amazon Rekognition** – Amazon Rekognition is a computer vision service that can detect and extract video segments or *scenes* by identifying technical cues such as shot boundaries, black frames, and other visual elements. To yield higher accuracy for the generated video descriptions, you use Amazon Rekognition to segment the source video into smaller chunks before passing it to Amazon Nova. These video segments can be stored in a temporary directory on your compute machine.
- **Amazon Bedrock** – Amazon Bedrock is a managed service that provides access to large, pre-trained AI models such as the Amazon Nova Pro model, which is used in this solution to analyze the content of each video segment and generate detailed scene descriptions. You can store these text descriptions in a text file (for example, `video_analysis.txt`).
- **Amazon Polly** – Amazon Polly is a text-to-speech service that is used to convert the text descriptions generated by the Amazon Nova Pro model into high-quality audio, made available using an MP3 file.

## Prerequisites

To follow along with the solution outlined in this post, you should have the following in place:

- A video file. For this post, we use a public domain video, [This is Coffee](https://archive.org/details/ThisisCo1961).
- An AWS account with access to the following services:  Amazon Rekognition Amazon Nova Pro Amazon S3 Amazon Polly Configure your [AWS Command Line Interface (AWS CLI)](https://aws.amazon.com/cli/) or environment with valid credentials (using `aws configure` or environment variables)
- To write the script, you need access to an [AWS Software Development Kit (AWS SDK)](https://aws.amazon.com/developer/tools/) in the language of your choice. In this post, we assume that you will use the [AWS SDK for Python](https://aws.amazon.com/sdk-for-python/) (Boto3). Additional information on AWS SDK for Boto3 is available in the [Quickstart for Boto3](https://d.docs.live.net/ffa2d987aac0fa7b/Documents/Steyer/AWS/AWS%20Data/Code%20style.docx).

You can use AWS SDK to create, configure, and manage AWS services. For Boto3, you can include it at the top of your script using: `import boto3`

Additionally, you need a mechanism to split videos. If you’re using Python, we recommend the `moviepy` library.
`import moviepy # pip install moviepy`

## Solution walkthrough

The solution includes the following basic steps, which you can use as a basic structure and customize or expand to fit your use case.

- Define the requirements for the AWS environment, including defining the use of the Amazon Nova Pro model for its visual support and the [AWS Region](https://docs.aws.amazon.com/glossary/latest/reference/glos-chap.html#region) you’re working in. For optimal throughput, we recommend using [inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html) when configuring Amazon Bedrock to invoke the Amazon Nova Pro model. Initialize a client for Amazon Rekognition, which you use for its support of segmentation.

```
CLASS VideoAnalyzer:
	FUNCTION initialize():
 		Set AWS_REGION to "us-east-1"
 		Set MODEL_ID to "amazon.nova-pro-v1:0"
 		Set chunk_delay to 20 Initialize AWS clients (Bedrock and Rekognition)
```

- Define a function for detecting segments in the video. Amazon Rekognition supports segmentation, which means users have the option to detect and extract different segments or scenes within a video. By using the [Amazon Rekognition Segment API](https://docs.aws.amazon.com/rekognition/latest/dg/segment-api.html), you can perform the following:  Detect *technical cues* such as black frames, color bars, opening and end credits, and studio logos in a video. Detect *shot boundaries* to identify the start, end, and duration of individual shots within the video.

The solution uses Amazon Rekognition to partition the video into multiple segments and perform Amazon Nova Pro-based inference on each segment. Finally, you can piece together each segment’s inference output to return a comprehensive audio description for the entire video.

```
FUNCTION get_segment_results(job_id):
 	TRY:
 	   Initialize empty segments list 
 	   WHILE more results exist:
 	         Get segment detection results 
                Add segments to list 
                IF no more results THEN break
          RETURN segments 
       CATCH any errors and return null 

FUNCTION extract_scene(video_path, start_time, end_time):
       TRY: 
           Load video file 
           Validate time range
           Create temporary directory 
           Extract video segment 
           Save segment to file 
           RETURN path to saved segment 
       CATCH any errors and return null
```

![Three coffee cups on checkered tablecloth and close-up of coffee grounds in cup](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/02/image-2.png)

In the preceding image, there are two scenes: a screenshot of one scene on the left followed by the scene that immediately follows it on the right. With the Amazon Rekognition segmentation API, you can identify that the scene has changed—that the content that is displayed on screen is different—and therefore you need to generate a new scene description.

- Create the segmentation job and:  Upload the video file for which you want to create an audio description to Amazon S3. Start the job using that video.

Setting `SegmentType=[‘SHOT’]` identifies the start, end, and duration of a scene. Additionally, [MinSegmentConfidence](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition/client/start_segment_detection.html) sets the minimum confidence Amazon Rekognition must have to return a detected segment, with 0 being lowest confidence and 100 being highest.

- Use the `analyze_chunk` function. This function defines the main logic of the audio description solution. Some items to note about `analyze_chunk`:  For this example, we sent a video scene to Amazon Nova Pro for an analysis of the contents using the prompt `Describe what is happening in this video in detail`. If you are trying out this process for your own use cases, you’ll want to experiment with customizing the prompt. Based on our prompt, Amazon Nova Pro then returned the text description for our video scene. For longer videos with many scenes, you might encounter throttling. This is resolved by implementing a retry mechanism. For details on throttling and quotas for Amazon Bedrock, see [Quotas for Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas.html).

```
FUNCTION analyze_chunk(chunk_path): 
     TRY: 
        Convert video chunk to base64 
        Create request body for Bedrock 
        Set max_retries and backoff_time 

        WHILE retry_count < max_retries:
          TRY:
             Send InvokeModel request to Bedrock
             RETURN analysis results 
          CATCH throttling: 
              Wait and retry with exponential backoff 
          CATCH other errors: 
              Return null 
     CATCH any errors:
         Return null
```

In effect, the raw scenes are converted into rich, descriptive text. Using this text, you can generate a complete scene-by-scene walkthrough of the video and send it to Amazon Polly for audio.

- Use the following code to orchestrate the process:  Initiate the detection of the various segments by using Amazon Rekognition. Each segment is processed through a flow of:  Extraction. Analysis using Amazon Nova Pro. Compiling the analysis into a `video_analysis.txt` file.
- The `analyze_video` function brings together all the components and produces a text file that contains the complete, scene-by-scene analysis of the video contents, with timestamps

```
FUNCTION analyze_video(video_path, bucket): 
     TRY: 
         Start segment detection 
         Wait for job completion 
         Get segments 
         FOR each segment: 
             Extract scene 
             Analyze chunk 
             Save analysis results 
         Write results to file 
      CATCH any errors
```

If you refer back to the previous screenshot, the output—without any additional refinement—will look similar to the following image.

![Three coffee cups on checkered tablecloth and close-up of coffee grounds in cup](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/02/image-2.png)

```
“Segment 103.136-126.026 seconds:
[{'text': 'The video shows a close-up of a coffee cup with steam rising from it, followed by three cups of coffee on a table with milk and sugar jars. A person then picks up a bunch of coffee beans from a plant.'}]
Segment 126.059-133.566 seconds:
[{'text': "The video starts with a person's hand, covered in dirt and holding a branch with green leaves and berries. The person then picks up some berries. The video then shows a man standing in a field with trees and plants. He is holding a bunch of red fruits in his right hand and looking at them. He is wearing a shirt and has a mustache. He seems to be picking the fruits. The fruits are probably coffee beans. The area is surrounded by green plants and trees."}]” 
```

The following screenshot is an example is a more extensive look at the `video_analysis.txt` for the `coffee.mp4` video:

![Detailed video analysis text file displaying 12 chronological segments with timestamps, describing a day's journey from waking up to coffee cultivation and brewing.](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/02/image-4.png)

- Ensure that the text file is correct and appropriate for the audience and purpose of the video. There are several ways to correct any issues you find. For example, each scene description produced by Amazon Nova may begin with something like “In this video…” You should remove this text, as it degrades the quality of the final audio description. You can do this in one of these ways:  Edit the text file manually. Programatically find and remove that type of text from the output. Prevent the introductory text from being created by using prompt engineering to request that Amazon Bedrock return only the scene descriptions in a structured format or without any additional commentary Define and use a tool when performing inference on Amazon Bedrock. This can be a more comprehensive technique of defining the format of the output that you want Amazon Bedrock to return. Using tools to shape model output, is known as function calling. For more information, see [Use a tool to complete an Amazon Bedrock model response](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html).
- Send the contents of the text file to Amazon Polly. Amazon Polly adds a voice to the text file, completing the workflow of the audio description solution.

```
FUNCTION generate_audio(text_file, output_audio_file):
     TRY:
        Read analysis text
        Set max_retries and backoff_time

        WHILE retry_count < max_retries:
           TRY:
              Initialize Polly client
              Convert text to speech
              Save audio file
              RETURN success
           CATCH throttling:
              Wait with exponential backoff
              retry_count += 1
           CATCH other errors:
              retry_count += 1
              Continue or Break based on error type
     CATCH any errors:
         RETURN error
```

For a list of different voices that you can use in Amazon Polly, see [Available voices](https://docs.aws.amazon.com/polly/latest/dg/available-voices.html) in the Amazon Polly Developer Guide.

Your final output with Polly should sound something like this:

## Clean up

It’s a best practice to delete the resources you provisioned for this solution. If you used an EC2 or SageMaker Notebook Instance, stop or terminate it. Remember to delete unused files from your S3 bucket (eg: video_analysis.txt and video_analysis.mp3).

## Conclusion

Recapping the solution at a high level, in this post, you used:

- Amazon S3 to store the original video, intermediate data, and the final audio description artifacts
- Amazon Rekognition to partition the video file into time-stamped scenes
- Computer vision capabilities from Amazon Nova Pro (available through Amazon Bedrock) to analyze the contents of each scene

We showed you how to use Amazon Polly to create an MP3 audio file from the final scene description text file, which is what will be consumed by the audience members.

The solution outlined in this post demonstrates key steps that will be necessary to create automated audio descriptions for video content. By using Amazon Rekognition for video segmentation, the Amazon Nova Pro model for scene analysis, and Amazon Polly for text-to-speech, you can generate a comprehensive audio description track that narrates the key visual elements of a video. This end-to-end automation has the potential to significantly reduce the time and cost required to make video content accessible for visually disabled audiences, helping businesses and organizations meet their accessibility goals. With the power of AWS AI services, this solution demonstrates the first steps towards a scalable and efficient way to improve accessibility and inclusion for video-based media. While this solution is powerful, we recognize that it’s still Day 1, and we will continue iterating and experimenting until we’ve found a solution that our customers are delighted with.

For more information about the Amazon Nova model family and the things these models can do, see [Introducing Amazon Nova foundation models: Frontier intelligence and industry leading price performance](https://aws.amazon.com/blogs/aws/introducing-amazon-nova-frontier-intelligence-and-industry-leading-price-performance/).

### About the Authors

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/05/dylan-martin.jpeg)**Dylan Martin** is an AWS Solutions Architect, working primarily in the generative AI space helping AWS Technical Field teams build AI/ML workloads on AWS. He brings his experience as both a security solutions architect and software engineer. Outside of work he enjoys motorcycling, the French Riviera and studying languages.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/05/ankit.jpeg)**Ankit Patel** is an AWS Solutions Developer, part of the Prototyping And Customer Engineering (PACE) team. Ankit helps customers bring their innovative ideas to life by rapid prototyping; using the AWS platform to build, orchestrate, and manage custom applications.
