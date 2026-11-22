---
vendor: aws_bedrock
title: Exploring accessible audio descriptions with Amazon Nova
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/exploring-accessible-audio-descriptions-with-amazon-nova
date: 2025-06-13
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 06919b768833
---

# 探索使用 Amazon Nova 生成可访问的音频描述

据世界卫生组织统计，[全球有超过 22 亿人存在视力障碍](https://www.who.int/news-room/fact-sheets/detail/blindness-and-visual-impairment#:~:text=Prevalence-,Globally%2C%20at%20least%202.2%20billion%20people%20have%20a%20near%20or,has%20yet%20to%20be%20addressed.)。为遵守残疾人相关法规，例如美国的 [Americans with Disabilities Act](https://www.ada.gov/)（ADA），电视节目或电影这类视觉形式的媒体必须为视障人士提供可访问的格式。这通常以音频描述音轨的形式呈现，为影片或节目的关键视觉元素配上旁白。这类音轨的制作既耗时又昂贵。它们需要一大批专业人员参与，包括脚本撰稿人、工程师与配音演员，而且根据 [International Documentary Association](https://www.documentary.org/blog/5-things-consider-when-adding-audio-description-and-captioning-your-documentary-film#:~:text=Costs%20usually%20range%20on%20average,and%20everywhere%20by%20end%20users.) 的说法，其成本可能高达每分钟 25 美元。这就引出了一个自然的问题：能否借助 [Amazon Web Services（AWS）](https://aws.amazon.com/) 中的[生成式 AI](https://aws.amazon.com/generative-ai/) 产品来自动化这一过程？

尽管配有音频描述的电视节目与电影数量在增加，但绝大多数视频内容对视障观众而言仍然无法访问。增加音频描述内容数量的最大障碍是成本。用 GenAI 尽量降低这一障碍，将推动更多可访问内容的产生。

通过 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 可用的 [Amazon Nova Foundation Models](https://aws.amazon.com/ai/generative-ai/nova/?gclid=CjwKCAiA-ty8BhA_EiwAkyoa33w9TlOtBTRQ8LYw-0V_BrK4khqzEX539Mrj5E9njcPe0-ZvqQGUPBoCr2UQAvD_BwE&trk=36201f68-a9b0-45cc-849b-8ab260660e1c&sc_channel=ps&ef_id=CjwKCAiA-ty8BhA_EiwAkyoa33w9TlOtBTRQ8LYw-0V_BrK4khqzEX539Mrj5E9njcPe0-ZvqQGUPBoCr2UQAvD_BwE:G:s&s_kwcid=AL!4422!3!692006004844!e!!g!!amazon%20nova!21048268689!159639953895) 系列，包含三个可用于此目的的多模态[基础模型](https://aws.amazon.com/what-is/foundation-models/)（FM）：

- **Amazon Nova Lite（GA）** – 一款低成本多模态模型，处理图像、视频与文本输入时速度极快
- **Amazon Nova Pro（GA）** – 一款能力很强的多模态模型，在准确度、速度与成本之间取得平衡，适用于广泛的任务
- **Amazon Nova Premier** **（GA）** – 我们面向复杂任务能力最强的模型，也是模型蒸馏的教师模型

本文中，我们演示如何将 Amazon Nova、[Amazon Rekognition](https://aws.amazon.com/rekognition/) 与 [Amazon Polly](https://aws.amazon.com/polly/) 组合起来，自动化地为视频内容生成可访问的音频描述。这一做法能够显著减少让视频对视障观众可访问所需的时间与成本。不过需要说明，本文只是自动化生成音频描述的一次早期实验，并未提供完整、可直接部署的方案。

为展示其中的可能性，我们按顺序分享伪代码片段与指引，并配上详细说明与相关资源链接。本文描述的自动化工作流包括分析视频内容、生成文本描述，以及使用 AI 语音生成来朗读这些描述。读完全文，你将理解一些关键工具的用法，从而在持续实验中为自身用例构建出可上生产的方案。

## 解决方案概览

下面的架构图展示了所提方案的端到端工作流。我们将在本文后面的章节中深入描述每个组件，但请注意你可以把相关逻辑定义在单个脚本里。随后你可以在 [Amazon Elastic Compute Cloud（Amazon EC2）](https://aws.amazon.com/ec2) 实例上或本地计算机上运行该脚本。本文中，我们假设你在 [Amazon SageMaker notebook](https://docs.aws.amazon.com/sagemaker/latest/dg/nbi.html) 上运行脚本。

![使用 AI 服务分析视频内容以生成文本描述与音频旁白的端到端 AWS 工作流](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/02/image-1.jpeg)

在实验生成音频描述时，请留意该方案的架构组件。在生产环境中，关注潜在的扩展性、安全性与存储要素很重要，因为架构可能会逐渐演变得比此处展示的基础方案架构图更为复杂。

## 使用的服务

架构图中展示的服务包括：

- **Amazon S3** – [Amazon Simple Storage Service（Amazon S3）](https://aws.amazon.com/s3) 是一项对象存储服务，提供可扩展、持久且高可用的存储。在本例中，我们用 Amazon S3 存放视频文件（输入），以及方案生成的场景描述（文本文件）与音频描述（MP3 文件）输出。脚本首先从 S3 存储桶获取源视频。
- **Amazon Rekognition** – Amazon Rekognition 是一项计算机视觉服务，可通过识别镜头边界、黑帧等技术与视觉要素来检测并提取视频片段，即*场景*。为让生成的视频描述更准确，你使用 Amazon Rekognition 先把源视频切分为更小的块，再传给 Amazon Nova。这些视频片段可存放在计算主机的临时目录中。
- **Amazon Bedrock** – Amazon Bedrock 是一项托管服务，提供对大型预训练 AI 模型的访问，例如本方案中用于分析每个视频片段内容并生成详细场景描述的 Amazon Nova Pro 模型。你可以把这些文本描述存入一个文本文件（例如 `video_analysis.txt`）。
- **Amazon Polly** – Amazon Polly 是一项文本转语音服务，用于把 Amazon Nova Pro 模型生成的文本描述转换为高质量音频，并以 MP3 文件的形式提供。

## 前置条件

要跟着本文所述的方案动手实践，你需要准备好以下内容：

- 一个视频文件。本文中我们使用一段公有领域视频 [This is Coffee](https://archive.org/details/ThisisCo1961)。
- 一个可访问以下服务的 AWS 账户：  Amazon Rekognition Amazon Nova Pro Amazon S3 Amazon Polly 使用有效的凭证配置你的 [AWS Command Line Interface（AWS CLI）](https://aws.amazon.com/cli/) 或环境（可通过 `aws configure` 或环境变量）
- 编写脚本时，你需要使用所选语言的 [AWS Software Development Kit（AWS SDK）](https://aws.amazon.com/developer/tools/)。本文中我们假设你使用 [AWS SDK for Python](https://aws.amazon.com/sdk-for-python/)（Boto3）。关于 AWS SDK for Boto3 的更多信息，请参见 [Boto3 快速入门](https://d.docs.live.net/ffa2d987aac0fa7b/Documents/Steyer/AWS/AWS%20Data/Code%20style.docx)。

你可以使用 AWS SDK 创建、配置与管理 AWS 服务。对于 Boto3，可在脚本顶部这样引入：`import boto3`

此外，你还需要一种切分视频的机制。如果使用 Python，我们推荐 `moviepy` 库。
`import moviepy # pip install moviepy`

## 方案走查

该方案包含以下基本步骤，你可以把它当作基础结构，再根据自身用例定制或扩展。

- 定义 AWS 环境的需求，包括确定使用 Amazon Nova Pro 模型来获得其视觉能力，以及确定你工作所在的 [AWS Region](https://docs.aws.amazon.com/glossary/latest/reference/glos-chap.html#region)。为获得最佳吞吐量，我们建议在配置 Amazon Bedrock 调用 Amazon Nova Pro 模型时使用[推理配置文件（inference profiles）](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html)。初始化一个 Amazon Rekognition 客户端，用于其分段能力。

```
CLASS VideoAnalyzer:
	FUNCTION initialize():
 		Set AWS_REGION to "us-east-1"
 		Set MODEL_ID to "amazon.nova-pro-v1:0"
 		Set chunk_delay to 20 Initialize AWS clients (Bedrock and Rekognition)
```

- 定义一个用于检测视频中分段的函数。Amazon Rekognition 支持分段，这意味着用户可以选择检测并提取视频中的不同片段或场景。通过使用 [Amazon Rekognition Segment API](https://docs.aws.amazon.com/rekognition/latest/dg/segment-api.html)，你可以完成以下操作：  检测视频中的*技术信号*，例如黑帧、彩条、片头与片尾字幕以及制片厂标识。检测*镜头边界*，以确定视频中各个镜头的起点、终点与时长。

该方案使用 Amazon Rekognition 把视频划分为多个片段，并对每个片段执行基于 Amazon Nova Pro 的推理。最后，你可以把各个片段的推理输出拼接起来，得到整段视频的完整音频描述。

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

![格子桌布上的三个咖啡杯，以及杯中咖啡渣的特写](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/02/image-2.png)

在上图中可以看到两个场景：左侧是某个场景的截图，右侧紧随其后的就是下一个场景。借助 Amazon Rekognition 的分段 API，你可以识别出场景已经变化——屏幕上显示的内容不同了——因此需要生成新的场景描述。

- 创建分段任务，并：  把你要为其生成音频描述的视频文件上传到 Amazon S3。用该视频启动任务。

设置 `SegmentType=[‘SHOT’]` 可识别场景的起点、终点与时长。此外，[MinSegmentConfidence](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition/client/start_segment_detection.html) 设定 Amazon Rekognition 返回检测到的片段所需的最低置信度，0 为最低置信度，100 为最高。

- 使用 `analyze_chunk` 函数。该函数定义了音频描述方案的主体逻辑。关于 `analyze_chunk`，有几点需要注意：  在本例中，我们把一个视频场景发给 Amazon Nova Pro，使用 prompt `Describe what is happening in this video in detail` 分析其内容。如果你要在自己的用例中尝试这一流程，可以试着定制这个 prompt。根据我们的 prompt，Amazon Nova Pro 随后返回了该视频场景的文本描述。对于场景众多的更长视频，你可能会遇到限流。这可以通过实现重试机制来解决。关于 Amazon Bedrock 的限流与配额细节，请参阅 [Amazon Bedrock 的配额](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas.html)。

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

实际上，原始场景就这样被转换为内容丰富的描述性文本。借助这些文本，你可以生成整段视频逐场景的完整走查，并发送给 Amazon Polly 转为音频。

- 使用下面的代码来编排整个流程：  借助 Amazon Rekognition 启动各片段检测。每个片段都经过这样的流程处理：  提取。使用 Amazon Nova Pro 分析。把分析结果汇总到 `video_analysis.txt` 文件。
- `analyze_video` 函数把各个组件整合起来，产出一个文本文件，其中包含带时间戳的、逐场景的视频内容完整分析。

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

如果回看前面的截图，输出——在没有任何额外润色的情况下——看起来会与下图类似。

![格子桌布上的三个咖啡杯，以及杯中咖啡渣的特写](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/02/image-2.png)

```
“Segment 103.136-126.026 seconds:
[{'text': 'The video shows a close-up of a coffee cup with steam rising from it, followed by three cups of coffee on a table with milk and sugar jars. A person then picks up a bunch of coffee beans from a plant.'}]
Segment 126.059-133.566 seconds:
[{'text': "The video starts with a person's hand, covered in dirt and holding a branch with green leaves and berries. The person then picks up some berries. The video then shows a man standing in a field with trees and plants. He is holding a bunch of red fruits in his right hand and looking at them. He is wearing a shirt and has a mustache. He seems to be picking the fruits. The fruits are probably coffee beans. The area is surrounded by green plants and trees."}]” 
```

下面的截图是一个示例，更完整地展示了 `coffee.mp4` 视频对应的 `video_analysis.txt`：

![详细的视频分析文本文件，按时间顺序展示 12 个带时间戳的片段，描述从起床、种植咖啡到冲泡咖啡的一日历程。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/02/image-4.png)

- 确认该文本文件对视频的受众与用途而言准确且合适。修正所发现的问题有几种做法。例如，Amazon Nova 生成的每段场景描述可能以“In this video…”这类说法开头。你应当删除这段文字，因为它会降低最终音频描述的质量。可以用以下方式之一完成：  手动编辑文本文件。以编程方式在输出中查找并删除这类文字。通过 prompt engineering 在请求中要求 Amazon Bedrock 以结构化格式仅返回场景描述、不附加任何评论，从而避免生成开场白文字。在对 Amazon Bedrock 执行推理时定义并使用工具。这可以是一种更全面的技术，用来定义你希望 Amazon Bedrock 返回的输出格式。用工具塑造模型输出，称为 function calling。更多信息，请参阅 [使用工具完成 Amazon Bedrock 模型响应](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html)。
- 把文本文件的内容发送给 Amazon Polly。Amazon Polly 为文本文件配上语音，从而完成音频描述方案的工作流。

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

关于 Amazon Polly 中可使用的各种语音列表，请参阅 Amazon Polly 开发者指南中的[可用语音](https://docs.aws.amazon.com/polly/latest/dg/available-voices.html)。

经 Polly 处理后的最终输出听上去大致如下：

## 清理

最佳实践是删除你为本方案预置的资源。如果你使用了 EC2 或 SageMaker Notebook 实例，请停止或终止它。记得删除 S3 存储桶中不再使用的文件（例如：video_analysis.txt 与 video_analysis.mp3）。

## 结论

概括回顾该方案，本文中你使用了：

- Amazon S3 存放原始视频、中间数据以及最终的音频描述产物
- Amazon Rekognition 把视频文件切分为带时间戳的场景
- Amazon Nova Pro（通过 Amazon Bedrock 提供）的计算机视觉能力，用于分析每个场景的内容

我们还演示了如何使用 Amazon Polly，从最终的场景描述文本文件生成 MP3 音频文件——也就是听众最终会听到的内容。

本文所述方案展示了为视频内容自动生成音频描述所必需的关键步骤。通过用 Amazon Rekognition 做视频分段、用 Amazon Nova Pro 模型做场景分析、用 Amazon Polly 做文本转语音，你可以生成一条完整的音频描述音轨，为视频的关键视觉元素配上旁白。这种端到端的自动化有望显著减少让视频内容对视障观众可访问所需的时间与成本，帮助企业与组织达成其无障碍目标。借助 AWS AI 服务的能力，该方案展示了迈向可扩展且高效的视频类媒体无障碍与包容性改进的第一步。尽管这一方案很强大，但我们清楚它仍处在 Day 1，我们会继续迭代与实验，直到找到让客户满意的方案。

如需了解 Amazon Nova 模型系列及其能力的更多信息，请参阅 [Introducing Amazon Nova foundation models: Frontier intelligence and industry leading price performance](https://aws.amazon.com/blogs/aws/introducing-amazon-nova-frontier-intelligence-and-industry-leading-price-performance/)。

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/05/dylan-martin.jpeg)**Dylan Martin** 是 AWS 解决方案架构师，主要从事生成式 AI 领域的工作，帮助 AWS 技术现场团队在 AWS 上构建 AI/ML 工作负载。他兼具安全解决方案架构师与软件工程师的经验。工作之外，他喜欢骑摩托车、法国里维埃拉以及学习语言。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/05/ankit.jpeg)**Ankit Patel** 是 AWS 解决方案开发人员，隶属 Prototyping And Customer Engineering（PACE）团队。Ankit 通过快速原型帮助客户把创新想法落地；他使用 AWS 平台构建、编排与管理定制应用。
