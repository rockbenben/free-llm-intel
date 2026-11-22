---
vendor: aws_bedrock
title: Build an agentic solution with Amazon Nova, Snowflake, and LangGraph
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-an-agentic-solution-with-amazon-nova-snowflake-and-langgraph
date: 2025-11-19
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 0a29082664ef
---

# 使用 Amazon Nova、Snowflake 和 LangGraph 构建 agentic 解决方案

*本文与来自 Snowflake 的 Bharath Suresh 和 Mary Law 共同撰写。*

[Agentic AI](https://aws.amazon.com/ai/agentic-ai/) 是一类能够自主运行的 AI，可在极少监督下自动化更广泛的任务。它融合传统 AI 与[生成式 AI](https://aws.amazon.com/generative-ai/) 的能力，在无需持续人工干预的情况下做出决策、执行任务并适应环境。这些自主系统可以规划、推理并采取行动以实现特定目标。下图取自 [A Practical Guide to AI Agents](https://www.snowflake.com/wp-content/uploads/2025/03/A-Practical-Guide-to-AI-Agents-1.pdf)，展示了这些自主行动的流程。

![AI agent 工作流的可视化表示，六个相连的蓝色圆圈展示了从输入感知到持续学习的演进过程](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/17/ml-18769-image-1.png)

本文中，我们介绍如何结合 [Snowflake](https://www.snowflake.com/en/) AI Data Cloud 与 [Amazon Web Services](https://aws.amazon.com/)（AWS）的工具，构建可供组织用来做数据驱动决策、提升运营效率并最终获得竞争优势的生成式 AI 解决方案。

Snowflake 是 [AWS Competency Partner](https://partners.amazonaws.com/partners/001E000000d8qQcIAI/Snowflake)，拥有多项 AWS 能力认证，包括生成式 AI、数据与分析、机器学习以及零售独立软件供应商（ISV）。Snowflake 已在 [AWS Marketplace 上提供](https://partners.amazonaws.com/partners/001E000000d8qQcIAI/Snowflake)。Snowflake 为各类组织打造工具，用于调动数据、统一孤岛数据，并发现数据、安全地共享数据。Snowflake 把 AI 引入受治理的数据，使团队能够对非结构化数据运行分析工作流、开发 agentic 应用，并在结构化与非结构化数据上训练模型，同时把运营开销降到最低并实现端到端治理。Snowflake 是实力雄厚的 AWS 合作伙伴，已在 [20 多个 AWS 区域](https://docs.snowflake.com/en/user-guide/intro-regions)提供，提供广泛的支持并与 AWS 服务集成。这包括 [AWS PrivateLink](https://aws.amazon.com/privatelink/) 提供的安全连接、从 [Amazon Simple Storage Service](https://aws.amazon.com/s3/)（Amazon S3）自动加载数据的 Snowpipe、用于数据编目的 [AWS Glue](https://aws.amazon.com/glue/)，以及用 [Amazon SageMaker](https://aws.amazon.com/sagemaker/) 进行模型开发。Snowflake 已获得 Amazon SageMaker Ready Product 服务验证。

## 业务挑战

传统的车辆保险理赔处理包含多个阶段，从人工校验驾驶证、理赔表单和车辆损伤图片等文档开始。这种人工工作流往往彼此孤立，且容易出错。本文中，我们演示一个把这套端到端流程自动化的 agentic AI 工作流。这个示例展示了技术可行性的边界，同时提升运营效率与可扩展性、减少人为错误，并支撑更有依据的决策。示例方案涉及以下关键服务：

- **[Snowflake](https://partners.amazonaws.com/partners/001E000000d8qQcIAI/Snowflake)** – AI Data Cloud。一个消除数据孤岛的统一平台，让数据与 AI 变得直接、互联且可信。
- **[Snowflake Document AI](https://docs.snowflake.com/en/user-guide/snowflake-cortex/document-ai/overview)** – 一项使用专有[大语言模型](https://aws.amazon.com/what-is/large-language-model/)（LLM）Arctic-TILT 从文档中抽取数据的 AI 功能。Document AI 最适合把文档中的非结构化数据转换为表中的结构化数据。请参阅 [Document AI 可用性](https://docs.snowflake.com/en/user-guide/snowflake-cortex/document-ai/limitations.html#label-document-ai-availability)。
- Snowflake 中的 **[Streamlit](https://streamlit.io/)** 是一个开源 Python 库，让创建和分享用于[机器学习](https://aws.amazon.com/ai/machine-learning/)（ML）与数据科学的自定义 Web 应用变得无缝。借助 Streamlit，你可以快速构建并部署强大的数据应用。有关构建仪表盘、数据工具以及[人工智能与机器学习](https://aws.amazon.com/training/learn-about/machine-learning/)（AI/ML）的更多用例，请参阅 [Streamlit in Snowflake 示例](https://github.com/Snowflake-Labs/snowflake-demo-streamlit)。
- **[Amazon Bedrock](https://aws.amazon.com/bedrock)** – 一项用于构建生成式 AI 应用的全托管服务，提供来自领先 AI 公司的高性能[基础模型](https://aws.amazon.com/what-is/foundation-models/)（FM）选择。[Amazon Nova Lite](https://aws.amazon.com/ai/generative-ai/nova/) 是一款低成本多模态模型，处理图像、视频和文本输入的速度极快。
- **[LangGraph](https://www.langchain.com/langgraph)** – 一个有状态的编排框架，为 agent 工作流带来更强的控制力。

该方案的演示见以下视频。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-18769/ml-18769-image-2.gif)

## 方案概述

![使用包括 S3、Textract 和 Step Functions 在内的 AWS 服务进行文档处理的保险理赔工作流](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/13/ml-18769-image-2.1-1.png)

该方案使用 agentic AI 架构，为车辆保险理赔处理实现了一个完全自主、可解释的工作流。其核心 pipeline 把结构化文档抽取、多模态图像分析、保单校验和自然语言生成结合起来，通过有状态的 LangGraph 工作流串联，并通过交互式 Streamlit UI 呈现。以下是端到端流程的高层说明：

- 用户上传三份必要材料：一份扫描的驾驶证（DL）、一份填写好的理赔表单（PDF 或图片）、一张车辆损伤照片
- 上传的驾驶证与理赔文档使用 Snowflake 的 Cortex Document AI 模型（`LICENSE_DATA` 和 `CLAIMS_DATA`）处理。这些模型抽取姓名、驾驶证号、车辆信息和事故日期等结构化字段，全部采用零样本或微调推理。
- 车辆损伤照片通过 Amazon Bedrock 交由 Amazon Nova Lite 分析。图像与文本 prompt 一并传给模型，模型返回关于可见损伤、车型、品牌和颜色的专业摘要。这为推理过程加入了非结构化的图像洞察。
- 从驾驶证、理赔表单和图像中抽取的值会做一致性交叉校验（例如姓名匹配、驾驶证号、车辆颜色），并与 Snowflake 中的保单记录核对（例如客户档案、VIN、保单到期时间）。由此确认该理赔真实且符合条件。
- 理赔表单中的事故日期会与从 Snowflake 取回的保单结束日期比较。落在保单有效期之外的理赔会被自动标记。
- 系统依据匹配准确率和保单状态做出决定。系统汇总比对摘要，并使用 Amazon Nova Lite 的自然语言生成能力生成面向客户的决策邮件。
- 所有阶段都作为节点连接在 LangGraph 状态机中，每个节点处理共享的工作流状态并将其向前传递。这种结构带来了模块化、可审计性和确定性的控制。
- 最终输出——包括工作流步骤、决策状态、匹配值和邮件——通过 Streamlit UI 实时展示给用户。一个调试用的折叠面板会显示每个抽取阶段的完整原始 JSON 数据。

该方案展示了文档理解、多模态推理以及自定义模型生成等多个 AI 组件如何被紧密集成到同一条 pipeline 中，自主完成感知、推理与行动。方案工作流遵循以下步骤：

- 用户把所有文档提交到 Streamlit 应用。
- 用户把事故照片、驾驶证和保险理赔表单等文档上传到 Snowflake Stage。
- 使用 Snowflake Document AI 从保险理赔表单中抽取数据。
- 使用 Amazon Bedrock 中的 Amazon Nova Lite 比对抽取出的理赔数据以验证真实性。
- Amazon Bedrock 中的 Amazon Nova Lite 分析车辆图片以识别损伤细节。
- 系统综合前面各步骤的结果对理赔做出裁定。
- 起草一封邮件，把决定告知客户。
- 工作流信息与决定通过邮件发送给用户。

这些步骤如下图所示。

![端到端保险理赔架构，展示文档分析、数据处理和自动化决策工作流](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/13/ml-18769-image-2.2-1.png)

## 前提条件

要实施本文给出的方案，你需要以下条件：

- **Snowflake 账户** – 已激活且具备相应权限的账户，熟悉 Snowflake SQL 或 Snowsight，并已启用 Cortex Document AI。
- **AWS 账户** – 已激活且可访问 Amazon Bedrock（包括 Amazon Nova Lite）的账户，并已配置好 AWS 凭证。
- **Python 环境** – 已安装 Python 3.x 及所需依赖包。
- **GitHub 访问** – 克隆提供的 [GitHub 仓库](https://github.com/Snowflake-Labs/sf-samples/tree/main/samples/vehicle-insurance-agentic-ai)。该仓库完整呈现了各组件如何通过由 LangGraph 驱动的状态机，从文档上传、抽取一直到校验，无缝集成并协同工作。
- **文档准备** – 带有相关数据的示例驾驶证图片、理赔表单 PDF 和车辆损伤图片。
- **Snowflake 数据设置** – 一个包含投保人数据（`customer ID`、`VIN` 和 `POLICY_END`）与示例数据的 `customer_policy_view` 表或视图。
- **Snowflake Document AI 模型构建** – 在 Snowsight 中为驾驶证和理赔表单分别构建两个模型，完成训练并发布以供预测。
- **Amazon Bedrock 配置** – 为 Python 配置好 AWS 凭证，以访问 Amazon Bedrock 中的 FM。

## **使用的文档**

为给这一 agentic AI 工作流模拟真实的保险理赔场景，我们准备了三份具有代表性的输入文档，与真实用户提交理赔的方式保持一致。数据集包括：

- 一份驾驶证（DL），显示姓名、驾驶证号、出生日期、地址和证照有效期，如下图所示

![模拟的加利福尼亚州驾驶证，展示版式、熊图案标识以及带占位数据的基本信息字段](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/17/ml-18769-image-3.png)

- 一份填写完成的理赔表单（PDF），记录客户 ID、车辆信息、事故描述和事故日期，如下图所示

![综合机动车辆保险理赔表单模板，展示保单信息、事故记录字段以及第三方事故声明部分](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/17/ml-18769-image-4.png)

- 展示车辆损伤的照片，如下图所示

![汽修场内的绿色轿车，前部可见碰撞损伤，显示引擎盖与保险杠受损范围](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/17/ml-18769-image-6.png)![车辆前端的明显撞击损伤，可见车身皱褶和板件错位](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/17/ml-18769-image-5.png)

本文使用的车辆损伤图片来自[车辆损伤数据集](https://www.kaggle.com/datasets/lplenka/coco-car-damage-detection-dataset)。

## **文档处理**

本示例方案使用由专有 Arctic-TILT LLM 驱动的 Snowflake Document AI，以极强的灵活性从上传文档中抽取信息。关于 Document AI 的入门信息，请访问[设置 Document AI](https://docs.snowflake.com/en/user-guide/snowflake-cortex/document-ai/setting-up)。

我们在 Snowsight 中创建了两个 Document AI 模型构建——一个用于驾驶证，一个用于理赔表单——使用由 Arctic-TILT LLM 驱动的 Snowflake `DOCUMENT_INTELLIGENCE` 类。对每个模型，我们上传示例文档、用自然语言 prompt 定义抽取字段（例如“驾驶证号是多少？”）、审阅带置信度评分的结果，并使用 `MODEL_NAME!PREDICT(GET_PRESIGNED_URL(...))` SQL 语法发布模型以供使用。这使得 pipeline 中可以进行零样本抽取，无需为每个新文件重新训练。下图展示了文档处理的工作流。

![端到端 Document AI 工作流示意图，展示模型创建、训练、文档上传、查询构建和自动化处理 pipeline](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/17/ml-18769-image-7.png)

上传的文档会经过专门的 AI 驱动处理。驾驶证使用 LICENSE_DATA!PREDICT 解析姓名、驾驶证号等字段。理赔表单使用 CLAIMS_DATA!PREDICT 解析车辆与事故细节（包括推断出的车辆颜色）。

车辆图片由 Amazon Bedrock 上的 Amazon Nova Lite 模型分析，以抽取结构化的损伤细节。这一多模态抽取层把原始输入转化为可供下游决策使用的结构化洞察。

### **在 Snowsight 中准备 Document AI 模型**

为从驾驶证和保险理赔表单等非结构化文档中抽取信息，我们使用 Snowflake 的 Document AI。我们创建了两个模型构建——`LICENSE_DATA` 和 `CLAIMS_DATA`——各自用于通过自然语言 prompt 抽取特定字段。以合适的角色登录 Snowsight 后，我们在左侧导航窗格中选择 **AI & ML** 和 **Document AI **。随后创建一个新的构建并上传示例文档。

每个文件都会经过光学字符识别（OCR），之后我们通过把值名称与抽取问题配对来定义字段。随后我们会收到带置信度评分的答案，并进行审阅与确认。当准确率令人满意时，我们发布模型，使其可以通过 `MODEL_NAME!PREDICT(GET_PRESIGNED_URL(...))` 语法从 SQL 中调用。为提升精确度，我们还可以用已审阅的文档微调模型。这一配置让我们能从真实表单中稳健地做零样本字段抽取——无需自定义 ML pipeline。

在 Snowsight 中创建并训练 Document AI 模型（例如 `LICENSE_DATA` 和 `CLAIMS_DATA`），并确保它们已发布、可用 `MODEL_NAME!PREDICT(GET_PRESIGNED_URL(...))` 做预测之后，我们转向用 Python 代码处理工作流的其余部分。Python 代码将负责完成理赔处理 pipeline 所需的编排、数据检索、LLM 交互和决策步骤。

以下视频展示了这一过程。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/17/ml-18769-image-8-1.gif)

### **用 Amazon Nova Lite 做车辆损伤分析**

为从事故图片评估车辆损伤，我们使用 AWS Bedrock 中的 Amazon Nova Lite——一款高性能、低延迟的多模态 FM。Nova Lite 让我们 agentic 工作流仅用一条自然语言 prompt 就能解读车辆照片这类非结构化图像数据，无需专门的计算机视觉模型。

图像通过 Streamlit 界面上传后，会被 base64 编码并封装进多模态 prompt。我们把图像和文本指令一起发给模型，模拟专业的损伤查勘场景。以下是我们后端实际使用的逻辑：

```
with open(path, "rb") as image_file:
    binary_data = image_file.read()
    base64_string = base64.b64encode(binary_data).decode("utf-8")
client = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "us.amazon.nova-lite-v1:0"
system_list = [{
    "text": "You are an expert car inspector. When provided with a car accident photo, return a technical summary describing the vehicle and any visible damage."
}]
message_list = [{
    "role": "user",
    "content": [
        {
            "image": {
                "format": ext,
                "source": {"bytes": base64_string}
            }
        },
        {
            "text": "Please inspect this damaged car image and return a summary of the damage and car type in professional language."
        }
    ],
}]
native_request = {
    "schemaVersion": "messages-v1",
    "messages": message_list,
    "system": system_list,
    "inferenceConfig": {"maxTokens": 500, "topP": 0.1, "topK": 20, "temperature": 0.3}
}
The invoke_model() method then sends this payload to Bedrock:
response = client.invoke_model(
    modelId=model_id,
    body=json.dumps(native_request),
    accept="application/json",
    contentType="application/json"
)
```

模型返回自然语言响应，例如：

```
The vehicle appears to be a hatchback with moderate rear-end collision damage. There are visible dents around the rear bumper. The car is likely a dark purple Ford Focus.
```

我们把这份摘要作为 `car` 对象的一部分存入共享工作流状态：

```
model_response = json.loads(response["body"].read())
content_text = model_response["output"]["message"]["content"][0]["text"]
car_data = {
    "visible_damage": content_text
}
```

借助 Amazon Nova Lite 的多模态能力，我们大幅降低了图像处理的复杂度，也无需训练和维护单独的图像识别模型。这一步为 agentic pipeline 注入了视觉智能——让保险理赔评估更完整、更贴近人类的判断。

## **使用 Amazon Nova 做跨文档比对与保单校验**

从驾驶证、理赔表单和车辆图片抽取数据之后，agentic AI 工作流会校验这些信息的一致性与真实性。这通过跨文档比对以及对照 Snowflake 记录的保单校验来完成。

首先，我们用从理赔表单中抽取的姓名识别客户。我们查询 Snowflake 视图（`customer_policy_view`）以取回关联的客户 ID。然后把这个视图与 `DRIVER_LICENSES` 表连接，取回颜色、品牌与型号、出生日期、驾驶证号和保单结束日期等参考字段。

以下是工作流中实际使用的 SQL 逻辑：

```
df_id = session.sql(f"""
    SELECT CUSTOMER_ID FROM customer_policy_view
    WHERE LOWER(NAME) = '{extracted_name.lower()}'
""").to_pandas()
df = session.sql(f"""
    SELECT
        cpv.NAME,
        cpv.COLOR,
        cpv.MAKE_MODEL,
        cpv.POLICY_END,
        dl.LICENSE_NO,
        dl.DOB
    FROM
        customer_policy_view cpv
    JOIN
        DRIVER_LICENSES dl ON LOWER(cpv.NAME) = LOWER(dl.NAME)
    WHERE
        cpv.CUSTOMER_ID = '{customer_id}'
""").to_pandas()
```

接下来，我们把文档中抽取的每个值与数据库中的对应值进行比较。参与比对的字段包括：

- `full_name`
- `dl_no`
- `dob`
- `vehicle_color`
- `make_model`

每次比较都会返回匹配状态（`true` 或 `false`）以及抽取值和参考值，便于我们清晰追溯不一致之处。比对字典的结构如下：

```
comparison = {
    "full_name": {
        "match": extracted_name.lower() == db_name.lower(),
        "claim_value": extracted_name,
        "db_value": db_name
    },
    ...
}
```

随后我们通过把理赔表单中的事故日期与 Snowflake 中的保单结束日期比较，校验保单是否处于有效状态：

```
incident_date = datetime.strptime(claim.get("date_of_incident", [{}])[0].get("value"), "%Y-%m-%d").date()
valid = incident_date and db_policy_end_date_obj and incident_date <= db_policy_end_date_obj
decision = "✅ Claim Accepted" if valid else "❌ Claim Rejected due to expired policy"
```

这种双层校验让理赔既在事实层面准确，也在法律层面有效。关键性的不一致（例如驾驶证号无效或保单已过期）会导致自动拒赔，而校验通过的匹配且事故发生在保单期内则会被接受。

这一步推理完全用 Python 以结构化的比对逻辑完成，从而保持了完全的透明性、灵活性和可审计性——这对企业级保险系统至关重要。

## **使用 Amazon Nova 自主推理并做出理赔决定**

在抽取并校验了所有相关数据——涵盖驾驶证、理赔表单、车辆照片和保单数据库——之后，工作流的最后一步是对完整上下文进行推理，并生成清晰、专业的理赔决定。这里再次由 Amazon Nova Lite 出手，这次它担任逻辑处理器和自然语言生成器。

我们精心构造一个结构化 prompt，把目前收集到的全部证据提供给 Amazon Nova Lite，包括字段级比对结果、保单结束日期、事故日期以及计算出的决定标志（接受或拒绝）。以下是用 Python 计算决定逻辑的方式：`decision = "✅ Claim Accepted" if valid else "❌ Claim Rejected due to expired policy"`

然后我们准备一段供人阅读的推理 prompt，用来概述当前情况：

```
email_prompt = f"""Write a short professional email to a customer summarizing their insurance claim review.
Comparison:
{json.dumps(comparison, indent=2)}
Incident Date: {incident_date}
Policy End: {db_policy_end_date_obj}
Decision: {decision}
"""
```

这段 prompt 通过 Amazon Bedrock Runtime API 传给 Amazon Nova Lite。Nova Lite 会解读完整上下文，并生成针对该客户的清晰邮件：

```
body = {
    "schemaVersion": "messages-v1",
    "messages": [{"role": "user", "content": [{"text": email_prompt}]}],
    "inferenceConfig": {"maxTokens": 1000}
}
email_response = bedrock.invoke_model(
    body=json.dumps(body),
    modelId="us.amazon.nova-lite-v1:0",
    accept="application/json",
    contentType="application/json"
)
```

响应可能如下所示：

```
Dear Steven, we have completed the review of your insurance claim submitted on February 14, 2025. Based on our evaluation, your documents have been successfully verified and the incident falls within your active policy period. We’re pleased to inform you that your claim has been accepted.
```

这份输出会与结构化决定和比对结果一起存入工作流状态。无论结果如何，在我们 agentic 应用的最后一步，系统都会在无需人工参与的情况下自动生成可直接发给客户的消息。

借助 Amazon Nova Lite 处理多模态输入并自主传达决定，我们闭合了一个智能、可自我推理的工作流闭环——它模拟人类保险理赔员的判断力与同理心，并且能够在规模化场景下做到这一点。

### **最终输出示例**

在处理上传的文档、分析车辆图片、校验抽取字段并确认保单符合条件之后，agentic AI 工作流会产出结构化且可解释的输出，包含跨文档与 Snowflake 记录的比对结果、理赔决定（接受或拒绝），以及由 Amazon Nova Lite 生成的面向客户的邮件。以下是一份成功理赔的完整输出示例：

```
{
  "decision": "✅ Claim Accepted",
  "comparison": {
    "full_name": {
      "match": true,
      "claim_value": "Steven Smith",
      "db_value": "Steven Smith"
    },
    "dl_no": {
      "match": true,
      "claim_value": "DL-2605979475",
      "db_value": "DL-2605979475"
    },
    "dob": {
      "match": true,
      "claim_value": "1991-08-15",
      "db_value": "1991-08-15"
    },
    "vehicle_color": {
      "match": true,
      "claim_value": "Purple",
      "db_value": "Dark Purple"
    },
    "make_model": {
      "match": true,
      "claim_value": "Ford Focus",
      "db_value": "Ford Focus Titanium"
    }
  },
  "email": "Dear Steven, we have completed the review of your insurance claim submitted on February 14, 2025. Based on our evaluation, your documents have been successfully verified and the incident falls within your active policy period. We’re pleased to inform you that your claim has been accepted. You will receive a follow-up with next steps shortly. Thank you for choosing our services."
}
```

这份输出展示了整条 pipeline 的完整能力：来自 Snowflake 的真值、使用 Document AI 的智能抽取、借助 Amazon Nova Lite 的多模态推理，以及用自然语言做出的决定解释。

这种结构化格式让审计、记录日志或与下游系统（如客户关系管理（CRM）系统、邮件工作流或保险管理平台）集成都变得简单直接。更重要的是，它在生产环境中闭合了可信、可解释 AI 的闭环。

## **agentic AI 工作流是如何自动化的**

整条车辆保险理赔处理 pipeline 被实现为一个 agentic AI 工作流：每个阶段观察输入、应用推理、使用 LLM 做出决策，并把上下文传递给下一阶段。这由 LangGraph 编排——一个把每项任务视为模块化节点、并在整个图中传递共享状态的有状态工作流引擎。

这套自动化的核心是一台 LangGraph 状态机，文档抽取、车辆图像分析和最终理赔决定等主要处理阶段都被定义为节点。这些节点通过有向边连接，形成一条顺序化、可解释的 pipeline：

```
builder = StateGraph(WorkflowState)
builder.add_node("upload", upload_all)
builder.add_node("extract_dl", extract_dl)
builder.add_node("extract_claim", extract_claim)
builder.add_node("extract_car", extract_car)
builder.add_node("compare_email", compare_and_email)
```

每个函数接收当前状态，执行其指定任务——例如运行 LLM 推理或查询 Snowflake——并返回更新后的状态信息。各步骤的贡献如下：

- **文档上传与暂存 **– `upload_all` 节点处理来自 Streamlit 前端的文件上传，并把它们暂存到 Snowflake 内部 stage：

`session.file.put(local_path, STAGE_NAME, overwrite=True)`

- **使用 Document AI 抽取文档 **– `extract_dl` 和 `extract_claim` 两个节点使用带预签名 URL 的零样本预测调用 Snowflake Document AI：

`sql = f"SELECT LICENSE_DATA!PREDICT(GET_PRESIGNED_URL(@doc_ai_stage, '{path}'), 2)"`

- **多模态车辆图像分析（Amazon Nova Lite） **– `extract_car` 节点把结构化 prompt 和 Base64 编码的图像发给 Amazon Nova Lite。尽管参考版本会返回品牌与型号等详细 JSON 字段，当前实现使用的是自然语言摘要来做损伤查勘。
- **跨文档推理与比对 **– `compare_and_email` 节点执行推理阶段，比对以下来源中抽取的值：驾驶证与理赔表单（姓名、驾驶证号）车辆图像与理赔表单（车辆颜色、品牌与型号）理赔表单与 Snowflake 保单（保单日期）
- 这些内容被组织成结构化 prompt 并传给 Amazon Nova Lite。输出被解析为 `comparison` 字典，供下游决策使用。
- **保单有效性检查（Snowflake SQL）** – 仍在同一个节点内，一条 SQL 查询会取回保单记录：

`SELECT VEHICLE_NUMBER, POLICY_END FROM customer_policy_view WHERE customer_id = '{customer_id}'`

- 随后检查理赔表单中的事故日期是否落在保单有效期内。
- **理赔决定与邮件生成 **– 依据字段级和日期级校验，理赔会被接受或拒绝：

`decision = "✅ Claim Accepted" if incident_date <= policy_end_date else "❌ Claim Rejected"`

- 该结果会连同比对上下文一起，用于通过 Amazon Nova Lite 构造面向客户的邮件。
- **agentic 状态串联** – 流程通过图中的有向边串联起来：

```
builder.set_entry_point("upload")
builder.add_edge("upload", "extract_dl")
builder.add_edge("extract_dl", "extract_claim")
builder.add_edge("extract_claim", "extract_car")
builder.add_edge("extract_car", "compare_email")
builder.add_edge("compare_email", END)
```

每个节点都用新的观察和决定来增强状态，使 pipeline 能够自主感知、推理和行动——这正是 agentic AI 系统的标志。

## **用 Streamlit 做交互式前端**

为了让工作流易于访问且直观，我们用 Streamlit 构建了一个简洁的面向用户的前端。Streamlit 是一个流行的开源 Python 框架，用于快速制作 UI 原型和数据应用。Streamlit 应用的用户可以上传理赔相关文档，并实时获得包括理赔校验、保单决定和生成的面向客户邮件在内的输出。

Streamlit 界面首先要求提供三份必需文档：扫描的驾驶证、理赔表单（PDF 或图片）以及车辆损伤照片。它们通过带格式限制的 `file_uploader` 组件采集，以确保输入有效：

```
dl_file = st.file_uploader("Driver's License", type=["jpg", "jpeg", "png", "pdf"])
claim_file = st.file_uploader("Claim Document", type=["jpg", "jpeg", "png", "pdf"])
car_file = st.file_uploader("Car Damage Photo", type=["jpg", "jpeg", "png", "pdf"])
```

所有文档上传完成后，用户点击按钮启动后端 pipeline，该 pipeline 会调用由 LangGraph 驱动的 `run_claim_processing_workflow()` 函数：

```
if st.button("Run Claim Workflow"):
    result = run_claim_processing_workflow({
        "dl": dl_file,
        "claim": claim_file,
        "car": car_file
    })
```

工作流执行期间会显示加载指示器，错误会立即显示在 UI 上以便排查。

工作流完成后，UI 会把结果分节结构化展示：已完成的工作流步骤、字段级比对输出、保单有效性结果，以及一封

由 Amazon Nova Lite 生成的面向客户的最终邮件。这些结果使用 `st.markdown()` 和 `st.json()` 渲染，便于解读：

```
st.markdown("### Workflow Steps")
for step in result.get("steps", []):
    st.markdown(f"✅ {step}")
st.markdown("### Document Comparison")
st.json(result.get("comparison", {}))
st.markdown("### Policy Validity")
st.markdown(result.get("decision"))
st.markdown("### Final Email")
st.code(result.get("email"))
```

对开发者或质量保证（QA）团队，一个可折叠区域提供了从驾驶证、理赔表单和车辆图像中抽取的原始 JSON 输出：

```
with st.expander("Raw Data"):
    st.json(result.get("dl", {}))
    st.json(result.get("claim", {}))
    st.json(result.get("car", {}))
```

这为所有 AI 驱动的决策提供了完全透明性，并支持可审计性——这在保险等受监管行业中是一项关键特性。

## **清理**

演示结束后，请执行以下清理步骤：

- Snowflake 清理：（可选）如果 `customer_policy_view` 表或视图仅为演示而创建，请截断或删除它。如果不再需要 Document AI 模型（`LICENSE_DATA` 和 `CLAIMS_DATA`），请考虑将其删除。移除上传到内部 stage 的文件（`doc_ai_stage`）
- AWS 清理：如果创建了临时 AWS 资源，请删除它们。Amazon Bedrock 模型访问通常不需要清理，但如果创建了临时 [AWS Identity and Access Management](https://aws.amazon.com/iam/)（IAM）角色或策略，则应将其删除。

遵循这些设置与清理步骤，可以获得顺畅的演示体验，并在之后保持环境整洁。

## **结论**

本项目以车辆保险理赔校验为案例，展示了 agentic AI 工作流在处理现实世界中以文档为中心的流程方面的潜力。系统跨多个任务和数据流执行复杂工作流，在无需持续人工监督的情况下编排各项操作。通过集成 Snowflake 的 Document AI、Amazon Bedrock 与 Amazon Nova Lite 的多模态与推理模型，以及 LangGraph 的编排，我们打造出一个稳健、可解释、可用于生产的方案，具备自主感知、推理与行动的能力。

从结构化文档抽取到视觉损伤理解、跨文档比对、保单查询和自然语言邮件起草——pipeline 的每一步都像一个专用 agent，为整体目标做出贡献。LangGraph 的有状态工作流设计使其易于进一步扩展更多能力，例如欺诈检测、文档分类或供应商协调。

这不仅仅是一个保险应用，而是一个构建下一代 AI 系统的模板——这类系统能够跨模态推理、与企业数据交互并自主执行。随着 agentic AI 日益普及，这些模块化、可解释的工作流将成为在真实业务流程中落地 AI 的关键。Agentic AI 有潜力提升效率、改进决策、加快上市速度、提高客户满意度，并创造更多创新机会。

## 资源

- 更多信息以及 Amazon Nova 的入门指引，请参阅 [Amazon Nova 基础模型](https://aws.amazon.com/ai/generative-ai/nova/)。
- 在 AWS Marketplace 中免费试用 Snowflake [30 天](https://aws.amazon.com/marketplace/saas/ordering?productId=106ff316-230f-4ad7-9d64-91e400266426&tryForFree=true)。观看这场 [AWS 与 Snowflake Better Together 网络研讨会](https://www.snowflake.com/en/resources/webinar/snowflake-on-snowflake/modern-revenue-automation/thankyou/)。
- 想了解更多并获取上手资源以开始使用 Snowflake 的生成式 AI，请访问 [Snowflake for AI](https://www.snowflake.com/en/product/ai/)，并[下载《A Practical Guide to AI Agents》](https://www.snowflake.com/resource/a-practical-guide-to-ai-agents/)。

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/30/ml-18769-image-8-BharathSuresh-1.jpeg)**Bharath Suresh** 是 Snowflake 的高级解决方案工程师，曾任 Amazon Web Services（AWS）与 IBM 的架构师，在全球企业的云架构、数据平台和 AI 驱动解决方案方面拥有超过 15 年经验。在 Snowflake，他帮助客户实现数据与 AI 工作负载的现代化，专注于 agentic 工作流、治理和多云转型。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/30/Mary-1-1.jpg)**Mary Law** 是 Snowflake（AI Data Cloud）的 APJ 合作伙伴技术负责人。她的经历包括在 AWS 领导 APJ Analytics Acceleration Lab，以及在 Microsoft 担任数据与 AI 专家岗位。这段穿越不同云生态的历程，让 Mary 对解决复杂数据挑战拥有独到见解。她热衷于帮助合作伙伴开发能带来真实业务价值的解决方案。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/30/ml-18769-image-10-aamantle-2.jpeg)**Amelia Mantle** 是 Amazon Web Services（AWS）的助理解决方案架构师。凭借数据科学背景，Amelia 持续帮助客户在云上开发 AI/ML 解决方案。她为正在推进数字化转型的组织担任值得信赖的 AI 顾问，与 AWS 合作伙伴和客户紧密合作，设计和实施创新的 AI 服务。
