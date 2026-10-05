---
vendor: huggingface
title: 我在 Google Cloud 上部署 serverless transformers pipeline 之旅
original_title: My Journey to a serverless transformers pipeline on Google Cloud
url: https://huggingface.co/blog/how-to-deploy-a-pipeline-to-google-clouds
date: 2021-03-18
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 我在 Google Cloud 上部署 serverless transformers pipeline 之旅

> 社区成员 Maxence Dominici 撰写的客座博客

本文将讲述我把 `transformers` 的 *sentiment-analysis*（情感分析）pipeline 部署到 [Google Cloud](https://cloud.google.com) 的历程。我们先简单介绍 `transformers`，然后进入实现的技术部分，最后总结这次实现并回顾我们的成果。

## 目标

[![img.png](https://huggingface.co/blog/assets/14_how_to_deploy_a_pipeline_to_google_clouds/Customer_review.png)](https://huggingface.co/blog/assets/14_how_to_deploy_a_pipeline_to_google_clouds/Customer_review.png) 我想创建一个微服务，自动判断顾客在 Discord 里留下的评价是正面还是负面。这样我就能相应处理评论、改善客户体验。例如，如果是差评，我可以做一个功能联系顾客、为糟糕的服务质量道歉，并告知我们的支持团队会尽快联系他/她提供帮助、争取解决问题。由于我预计每月不超过 2000 个请求，我没有对处理时间和可扩展性设置性能约束。

## Transformers 库

一开始下载 .h5 文件时我有点困惑。我以为它能用 `tensorflow.keras.models.load_model` 加载，事实并非如此。研究几分钟后我发现该文件是权重 checkpoint 而非 Keras 模型。之后我试了 Hugging Face 提供的 API，又读了他们 pipeline 功能的介绍。既然 API 和 pipeline 的效果都很棒，我决定在自己的服务器上通过 pipeline 服务这个模型。

下面是 Transformers GitHub 页面的[官方示例](https://github.com/huggingface/transformers#quick-tour)。

```
from transformers import pipeline

# Allocate a pipeline for sentiment-analysis
classifier = pipeline('sentiment-analysis')
classifier('We are very happy to include pipeline into the transformers repository.')
[{'label': 'POSITIVE', 'score': 0.9978193640708923}]
```

## 把 transformers 部署到 Google Cloud

> 选 GCP 是因为它是我个人组织在用的云环境。

### 第 1 步 - 调研

我已经知道可以用 `flask` 这类 API 服务来托管 `transformers` 模型。我在 Google Cloud AI 文档里找到了托管 Tensorflow 模型的 [AI-Platform Prediction](https://cloud.google.com/ai-platform/prediction/docs) 服务，也看到了 [App Engine](https://cloud.google.com/appengine) 和 [Cloud Run](https://cloud.google.com/run)，但我担心 App Engine 的内存占用，对 Docker 也不熟悉。

### 第 2 步 - 在 AI-Platform Prediction 上测试

由于该模型不是"纯 TensorFlow"的 saved model 而是 checkpoint，我又无法把它转成"纯 TensorFlow 模型"，我判断[这个页面](https://cloud.google.com/ai-platform/prediction/docs/deploying-models)上的例子行不通。从那里我看到可以写自定义代码，直接加载 `pipeline` 而不必自己处理模型，这看起来更简单。我还了解到可以定义预测前/预测后动作，将来按客户需求对数据做前后处理时可能有用。我照着 Google 的指南做，但因为该服务仍在 beta、很多功能不稳定，遇到了一个问题，详情见[这里](https://github.com/huggingface/transformers/issues/9926)。

### 第 3 步 - 在 App Engine 上测试

我转到 Google 的 [App Engine](https://cloud.google.com/appengine)，因为这是我熟悉的服务，但 TensorFlow 因缺少系统依赖文件安装失败。我随后改试 PyTorch，在 F4_1G 实例上能跑，但同一实例无法处理超过 2 个请求，性能实在不理想。

### 第 4 步 - 在 Cloud Run 上测试

最后，我带着 docker 镜像转到 [Cloud Run](https://cloud.google.com/run)。我按[这个指南](https://cloud.google.com/run/docs/quickstarts/build-and-deploy#python)了解了它的运作方式。在 Cloud Run 上，我可以配置更大的内存和更多 vCPU，用 PyTorch 完成预测。我彻底放弃了 Tensorflow，因为 PyTorch 加载模型看起来更快。

## Serverless pipeline 的实现

最终方案由四个组件组成：

- `main.py`，处理发往 pipeline 的请求
- `Dockerfile`，用于构建要部署到 Cloud Run 的镜像。
- 模型文件夹，包含 `pytorch_model.bin`、`config.json` 和 `vocab.txt`。模型：[DistilBERT base uncased finetuned SST-2](https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english)。下载模型文件夹请按照按钮中的说明操作。[![img.png](https://huggingface.co/blog/assets/14_how_to_deploy_a_pipeline_to_google_clouds/Download_instructions_button.png)](https://huggingface.co/blog/assets/14_how_to_deploy_a_pipeline_to_google_clouds/Download_instructions_button.png) 由于我们用 [PyTorch](https://pytorch.org/)，不需要保留 `rust_model.ot` 或 `tf_model.h5`。
- `requirement.txt`，用于安装依赖

`main.py` 的内容非常简单。思路是接收一个包含两个字段的 `GET` 请求：第一个是需要分析的评价，第二个是用来"保护"服务的 API key。第二个参数是可选的，我用它来避免配置 Cloud Run 的 oAuth2。参数提供后，我们加载基于模型 `distilbert-base-uncased-finetuned-sst-2-english`（上文提供）构建的 pipeline，最后把最佳匹配返回给客户端。

```
import os
from flask import Flask, jsonify, request
from transformers import pipeline

app = Flask(__name__)

model_path = "./model"

@app.route('/')
def classify_review():
    review = request.args.get('review')
    api_key = request.args.get('api_key')
    if review is None or api_key != "MyCustomerApiKey":
        return jsonify(code=403, message="bad request")
    classify = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path)
    return classify("that was great")[0]


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google Cloud
    # Run, a webserver process such as Gunicorn will serve the app.
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
```

然后是 `DockerFile`，用于构建服务的 docker 镜像。我们声明服务以 python:3.7 运行，并且需要安装 requirements；随后用 `gunicorn` 在端口 `5000` 上处理进程。

```
# Use Python37
FROM python:3.7
# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
# Copy requirements.txt to the docker image and install packages
COPY requirements.txt /
RUN pip install -r requirements.txt
# Set the WORKDIR to be the folder
COPY . /app
# Expose port 5000
EXPOSE 5000
ENV PORT 5000
WORKDIR /app
# Use gunicorn as the entrypoint
CMD exec gunicorn --bind :$PORT main:app --workers 1 --threads 1 --timeout 0
```

需要注意 `--workers 1 --threads 1` 参数，意思是我只用一个 worker（= 1 个进程）、单线程运行应用。这是因为我不想同时出现 2 个实例（可能推高账单）。缺点之一是服务同时收到两个请求时处理时间会更长。之后把线程数限制为 1 是因为把模型加载进 pipeline 所需的内存：如果用 4 个线程，可能只剩 4 Gb / 4 = 1 Gb 来完成整个进程，这不够，会导致内存错误。

最后是 `requirement.txt` 文件

```
Flask==1.1.2
torch===1.7.1
transformers~=4.2.0
gunicorn>=20.0.0
```

## 部署说明

首先，你需要满足一些前提：在 Google Cloud 上有项目、启用计费、安装 `gcloud` cli。更多细节见 [Google 指南 - Before you begin](https://cloud.google.com/run/docs/quickstarts/build-and-deploy#before-you-begin)。

其次，我们需要构建 docker 镜像并部署到 cloud run，选择正确的项目（替换 `PROJECT-ID`）并设置实例名，例如 `ai-customer-review`。部署的更多信息见 [Google 指南 - Deploying to](https://cloud.google.com/run/docs/quickstarts/build-and-deploy#deploying_to)。

```
gcloud builds submit --tag gcr.io/PROJECT-ID/ai-customer-review
gcloud run deploy --image gcr.io/PROJECT-ID/ai-customer-review --platform managed
```

几分钟后，你还需要把 Cloud Run 实例的内存从 256 MB 升级到 4 Gb。请在项目的 [Cloud Run Console](https://console.cloud.google.com/run) 操作。

在那里找到你的实例并点击。

[![img.png](https://huggingface.co/blog/assets/14_how_to_deploy_a_pipeline_to_google_clouds/Cloud_run_instance.png)](https://huggingface.co/blog/assets/14_how_to_deploy_a_pipeline_to_google_clouds/Cloud_run_instance.png)

之后屏幕顶部会有一个蓝色按钮 "edit and deploy new revision"，点击后会弹出许多配置项。在底部找到 "Capacity" 部分，即可指定内存。

[![img.png](https://huggingface.co/blog/assets/14_how_to_deploy_a_pipeline_to_google_clouds/Edit_memory.png)](https://huggingface.co/blog/assets/14_how_to_deploy_a_pipeline_to_google_clouds/Edit_memory.png)

## 性能

[![img.png](https://huggingface.co/blog/assets/14_how_to_deploy_a_pipeline_to_google_clouds/Request_Result.png)](https://huggingface.co/blog/assets/14_how_to_deploy_a_pipeline_to_google_clouds/Request_Result.png)

处理一个请求（包括把模型加载进 pipeline 和预测）耗时不到五秒；冷启动可能再多花大约 10 秒。

我们可以通过预热模型来改善请求处理性能——即在启动时而非每个请求时加载模型（例如用全局变量）。这样能节省时间和内存。

## 成本

我用 [Google pricing simulator](https://cloud.google.com/products/calculator#id=cd314cba-1d9a-4bc6-a7c0-740bbf6c8a78) 按 Cloud Run 实例配置模拟了成本 [![Estimate of the monthly cost](https://huggingface.co/blog/assets/14_how_to_deploy_a_pipeline_to_google_clouds/Estimate_of_the_monthly_cost.png)](https://huggingface.co/blog/assets/14_how_to_deploy_a_pipeline_to_google_clouds/Estimate_of_the_monthly_cost.png)

对我的微服务，我乐观估计每月接近 1000 个请求；以我的使用情况更可能是 500 个。所以我把 2000 个请求作为设计微服务时的上限。请求量这么低，我没怎么费心可扩展性，但如果账单上涨也许会回来重新考虑。

不过要强调，你的构建镜像每个 Gigabyte 都要付存储费，大约每 Gb 每月 €0.10。这没问题——前提是你不把所有版本都留在云上，因为我的镜像略超 1 Gb（PyTorch 约 700 Mb，模型 250 Mb）。

## 结论

借助 Transformers 的情感分析 pipeline，我节省了相当可观的时间：与其训练/微调一个模型，我直接找到了一个可用于生产环境的现成模型并开始在我的系统里部署。将来我可能会微调它，但从我的测试看，准确率已经非常出色！我本希望有一个"纯 TensorFlow"模型，或至少有一种不依赖 Transformers 就能在 TensorFlow 里加载它的方式以使用 AI 平台。如果有个精简版本就更棒了。
