---
vendor: aws_bedrock
title: Build financial document processing with Pulse AI and Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-financial-document-processing-with-pulse-ai-and-amazon-bedrock
date: 2026-05-13
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: bb3796a886f4
---

# 使用 Pulse AI 与 Amazon Bedrock 构建财务文档处理流程

金融机构每天要处理成千上万份复杂文档。财务数据中的光学字符识别（OCR）错误会沿着彼此关联的计算传播，影响分析准确性。在普通法律文档中，单个 OCR 错误也许只需快速人工修正；但同样的错误出现在财务数据里，就会在相互关联的计算之间级联放大，导致分析出现系统性错误，并可能给组织带来高昂代价。

在处理机构日常面对的复杂财务文档——资产负债表、利润表、SEC 申报文件、研究报告和审计材料——时，传统 OCR 工具明显力不从心。这些文档具有带合并单元格与层级数据的复杂表格结构、含相互引用关系的多栏布局，以及需要语义理解才能把握的依赖上下文的信息。传统 OCR 把这类文档当作图像处理，因而漏掉了让财务文档具有意义的结构关系与上下文细节。结果就是一串串人工修正、数据录入延迟和系统性分析错误。

本文演示如何构建一条文档抽取与模型微调的 pipeline 来应对这些关键挑战。通过把 Pulse AI 先进的文档理解能力与 Amazon Bedrock 强大的 AI 服务相结合，组织可以实现企业级准确度，并大规模提取与上下文相关的财务洞察。Amazon Bedrock 提供完全托管的模型定制，无需任何机器学习（ML）运维开销，按需部署、无需容量规划；Nova 模型系列具备出色的性价比，因此团队可以专注于创新而不是基础设施。

不同于传统的单体 OCR pipeline，[Pulse](https://www.runpulse.com/) 把视觉语言模型（vision language model）与专为文档理解而设计的经典 ML 组件结合起来，形成一套智能方案：以具备语义感知的方式抽取结构化数据、为财务领域模型生成更优质的监督式微调数据集，并支持部署在你特定财务数据上训练的自定义大语言模型（LLM）。[Pulse](https://www.runpulse.com/) 已部署在多家全球企业，包括 Samsung、Cloudera、Howard Hughes，以及处理大量财务与运营文档的《财富》500 强金融机构和领先的私募股权公司。

在一次部署中，一批约 1,000 份此前需要数天周转时间的复杂财务文档在三小时内处理完毕，产出了结构化、可审计的输出，可直接用于下游分析与 AI 应用。

图 1：文档处理工作流：传统方式 vs. Pulse

总而言之，Pulse AI 与 Amazon Bedrock 结合可以提供：

- Pulse AI 从复杂财务文档中抽取结构化、具备语义感知的数据，处理错综复杂的表格、多栏布局与层级数据。
- Amazon Bedrock 在这些高质量数据上微调 Amazon Nova 模型，为你的组织的财务惯例打造领域专属智能。
- 随后，自定义模型以贴合组织特点的理解方式处理新文档，把人工复核从数天缩短到数小时。

下面的工作流演示了构建智能化财务应用的一种思路。从原始财务文档出发，这条 pipeline 编排了一系列精细的步骤——文档处理、微调到部署——最终形成针对财务数据分析与洞察量身定制的 AI 方案。

图 2：文档处理参考架构工作流，展示 Pulse AI 与 AWS 服务集成后如何为智能文档处理（IDP）创建领域专属模型

系统首先（步骤 1）把文档摄入到你的 VPC 内的 Pulse 容器，或 Pulse 的软件即服务（SaaS）产品中。Pulse 模型处理这些财务文档（步骤 2）。抽取数据的输出会被转换为 Amazon Bedrock Nova Micro 监督式微调格式，然后存入 [Amazon Simple Storage Service（Amazon S3）](https://aws.amazon.com/s3/)（步骤 3）。

随后，工作流使用 Amazon Bedrock 的其他扩展功能：

使用 [Amazon Nova Micro](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-micro.html)（amazon.nova-micro-v1:0）运行一个监督式微调作业，这是一款为基于文本的抽取任务设计、具备 128K 上下文窗口的高性价比模型（步骤 5 和 6）。Nova Micro 的性价比很有竞争力。作业完成后，部署生成的模型用于按需推理。对于需要稳定性能的关键业务负载，你也可以使用 Provisioned Throughput。使用 *Test in Playground* 评估并比较响应。生成的定制模型被导入 Amazon Bedrock（步骤 8），并以 provisioned throughput 部署（步骤 9），为可扩展的终端用户应用提供支撑（步骤 10）。该架构把领域专属财务数据集与定制监督式微调模型结合起来，使组织能够构建理解财务语境、同时保持性能与成本效率的生产级 AI 应用。

## 先决条件

跟随本文操作，你需要满足以下先决条件。

- [AWS 账户](https://aws.amazon.com/) – 用于访问 AWS 服务，包括 Amazon Bedrock 以及存放数据集的 S3 存储。
- [允许 Amazon Bedrock 访问 S3 数据集的 AWS Identity and Access Management（IAM）策略](https://docs.aws.amazon.com/bedrock/latest/userguide/s3-bucket-access.html) – 授予 Amazon Bedrock 安全读取并处理你存储在 S3 桶中数据所需的权限。
- [Pulse Standard 账户（在 runpulse.com 注册）](https://www.runpulse.com/pricing-studio-pulse) – 用于接入 Pulse 系统并使用本工作流所需的功能。
- AWS 区域要求：`us-east-1`。
- Python 3.12 或更高版本。
- 实例类型：t3.medium。
- Amazon Elastic Compute Cloud（Amazon EC2）实例按小时计费。完成本教程后请记得终止实例，以免产生持续费用。
- Amazon Linux 2023（最新版）。
- 公开财务报表：[https://www.impact-bank.com/user/file/dummy_statement.pdf](https://www.impact-bank.com/user/file/dummy_statement.pdf)。
- S3 训练数据桶：`s3://<your s3 bucket>/training-data/`。

注意：本教程会创建产生费用的 AWS 资源，包括：EC2 实例（按小时）、S3 存储（按 GB-月）、Amazon Bedrock 微调（按训练小时）、provisioned throughput 部署（按小时）以及 AWS Secrets Manager（按密钥按月）。

## **分步实施**

按照以下步骤，使用 Pulse AI 与 Amazon Bedrock 搭建并配置你的财务文档处理 pipeline。

- 前往 [Pulse 控制台](https://console.runpulse.com/) 并创建账户。
- 使用 AWS 控制台启动 EC2 实例。前往 EC2 控制台。选择 **Launch Instance**。在 AMI 选择界面搜索 Amazon Linux 2023 AMI。选择 **Amazon Linux 2023 AMI**。在实例类型界面选择 **t3.medium**。创建新的密钥对，用于通过 SSH 访问该 Linux 实例。在安全组配置中，添加一条允许你的 IP 地址通过 SSH（端口 22）访问的规则。选择 **Launch**。保存成功消息中出现的实例 ID。
- 从 [RunPulse](https://console.runpulse.com/dashboard/api-keys) 创建你的 API key。
- 要找到实例的公有 DNS，请前往 EC2 控制台。选择你的实例。从 Details 选项卡复制 Public IPv4 DNS 值。
- 要连接 EC2 实例，请运行以下 SSH 命令。把 `YOUR_KEY_FILE.pem` 替换为你实际的密钥对文件名，把 `YOUR_INSTANCE_DNS` 替换为第 4a 步中的 Public IPv4 DNS 值：`ssh -i YOUR_KEY_FILE.pem ec2-user@YOUR_INSTANCE_DNS Example: ssh -i my-keypair.pem ec2-user@ec2-54-123-45-67.compute-1.amazonaws.com`
- 在 EC2 实例上运行 aws configure 配置 AWS 凭据。按提示输入 Access Key ID、secret access key、区域（`us-east-1`）和输出格式（json）。
- 使用给定命令把 Pulse API key 存入 AWS Secrets Manager：`aws secretsmanager create-secret --name pulse-api-key --secret-string "your-api-key"`
- 记下 ARN，权限策略会用到它

注意：Amazon Linux 2023 AMI 默认预装了 AWS Command Line Interface（AWS CLI）version 2。

- 在你的 EC2 实例上安装 runpulse SDK。安装 pip：`sudo yum install pip` 安装 Pulse Python SDK：`pip install pulse-python-sdk`
- 在你的 EC2 实例上，于当前工作目录创建名为 **bedrock-trust-policy.json** 的文件，内容如下一节所示。你可以使用 nano 或 vi 这类文本编辑器：nano `bedrock-trust-policy.json`。创建 `bedrock-trust-policy.json` `{ "Version": "2012-10-17", "Statement": [ { "Effect": "Allow", "Principal": { "Service": "bedrock.amazonaws.com" }, "Action": "sts:AssumeRole", "Condition": { "StringEquals": { "aws:SourceAccount": "your-aws-account-ID" }, "ArnLike": { "aws:SourceArn": "arn:aws:bedrock:us-east-1:your-aws-account-ID:model-customization-job/*" } } } ] }` 创建 `bedrock-permissions.json` `{ "Version": "2012-10-17", "Statement": [ { "Sid": "S3AccessForFineTuning", "Effect": "Allow", "Action": [ "s3:GetObject", "s3:PutObject", "s3:ListBucket" ], "Resource": [ "arn:aws:s3:::your-bucket-name", "arn:aws:s3:::your-bucket-name/*" ] }, { "Sid": "SecretsManagerAccess", "Effect": "Allow", "Action": [ "secretsmanager:GetSecretValue", "secretsmanager:PutSecretValue", "secretsmanager:CreateSecret", "secretsmanager:UpdateSecret", "secretsmanager:DescribeSecret" ], "Resource": [ "arn:aws:secretsmanager:us-east-1:your-aws-account-ID:secret:your-secret-name-*" ] } ] }` 然后创建角色：`aws iam create-role --role-name AmazonBedrock-FineTuning-S3-Role --assume-role-policy-document file://bedrock-trust-policy.json --description "Role for Bedrock fine-tuning with S3 and Secrets Manager access"` 预期输出：包含角色 ARN、ID 和创建时间戳的 JSON。接下来，

- 创建权限策略：

```
aws iam put-role-policy --role-name AmazonBedrock-FineTuning-S3-Role --policy-name Bedrock-S3-Access-Policy --policy-document file://bedrock-permissions.json
```

- 查看角色与信任策略：

```
aws iam get-role --role-name AmazonBedrock-FineTuning-S3-Role
```

- 要从[参考财务文档](https://www.impact-bank.com/user/file/dummy_statement.pdf)中抽取数据集，请在 EC2 实例上运行以下命令

# 从 Secrets Manager 取出 API key。安全最佳实践：不要把凭据硬编码在代码里，而应从 AWS Secrets Manager 取出。

```
curl -X POST https://api.runpulse.com/extract -H "x-api-key: $(aws secretsmanager get-secret-value --secret-id pulse-api-key --query SecretString --output text)" -H "Content-Type: application/json" -d '{ "file_url": "https://www.impact-bank.com/user/file/dummy_statement.pdf", "figureProcessing": {"description": true}, "extensions": {"altOutputs": {"returnHtml": true}} }'&gt; pulse_output.json
```

### Pulse AI 抽取的 json 片段示例：

```
{"bounding_boxes":{"Header":[{"average_word_confidence":0.9940000000000001,"bounding_box":[0.7418,0.04248181818181818,0.8901529411764706,0.042281818181818184,0.8901764705882352,0.05528181818181818,0.741835294117647,0.05548181818181818],"content":"0a-Account # 12345678","id":"txt-8","original_content":"Account # 12345678","page_number":2}],"Page Number":[{"average_word_confidence":0.99425,"bounding_box":[0.8071411764705881,0.24754545454545454,0.889635294117647,0.2474909090909091,0.8896588235294117,0.2616454545454545,0.8071529411764706,0.2617],"content":"0a-Page 1 of 2","id":"txt-3","original_content":"Page 1 of 2","page_number":1},{"average_word_confidence":0.9925,"bounding_box":[0.8076235294117646,0.057600000000000005,0.8898117647058823,0.05738181818181818,0.8898705882352942,0.0704,0.8076823529411765,0.07061818181818182],"content":"0a-Page 2 of 2","id":"txt-9","original_content":"Page 2 of 2","page_number":2}],"Tables":[{"cell_data":[{"confidence":0.9772562500000003,"location":{"coordinates":[0.0906,0.44435454545454545,0.8865647058823529,0.44499090909090905,0.8865647058823529,0.4685,0.0906,0.4678636363636363],"page":1},"position":{"column":0,"row":0},"properties":{"spans_columns":4,"type":"header"},"text":"0t-"},
```

- 检查文件是否存在且包含有效 JSON，以确认抽取成功

```
jq empty pulse_output.json &amp;amp;&amp;amp; echo "Valid JSON" || echo " Invalid JSON"
```

- 接下来，把抽取到的数据转换为 Nova 训练数据集。
- 创建名为 **convert_to_nova.py** 的新文件，并粘贴以下代码。

```
import jsonINPUT_FILE = "pulse_output.json" OUTPUT_FILE = "nova_dataset.jsonl"MAX_TOKENS = 30000 # Buffer below 32,768 limitdef estimate_tokens(text): """Rough token estimation: ~4 characters per token""" return len(text) // 4def create_truncated_samples(data): """Creates smaller training samples within token limits""" samples = [] # Sample 1: Header and Page Number only if "bounding_boxes" in data: if "Header" in data["bounding_boxes"] and "Page Number" in data["bounding_boxes"]: header_sample = { "Header": data["bounding_boxes"]["Header"], "Page Number": data["bounding_boxes"]["Page Number"] } samples.append({ "document": header_sample, "extracted_data": header_sample }) # Samples 2-4: Individual tables (truncated to 20 cells) if "Tables" in data["bounding_boxes"]: for i, table in enumerate(data["bounding_boxes"]["Tables"][:3]): truncated_table = { "table_info": table.get("table_info", {}), "cell_data": table.get("cell_data", [])[:20] } samples.append({ "document": {"Tables": [truncated_table]}, "extracted_data": {"Tables": [truncated_table]} }) # Samples 5-7: Text chunks (3 items each) if "Text" in data["bounding_boxes"]: text_items = data["bounding_boxes"]["Text"] chunk_size = 3 for i in range(0, min(9, len(text_items)), chunk_size): text_chunk = {"Text": text_items[i:i+chunk_size]} samples.append({ "document": text_chunk, "extracted_data": text_chunk }) # Sample 8: Title only if "Title" in data["bounding_boxes"]: title_sample = {"Title": data["bounding_boxes"]["Title"]} samples.append({ "document": title_sample, "extracted_data": title_sample }) return samplesdef convert_to_nova_format(sample): """ Converts to Nova format with instructional prompts for domain-specific learning This function creates training samples that teach the model: 1. Financial document structure recognition (headers, tables, transactions) 2. Data type standardization (dates to ISO 8601, amounts to numbers) 3. Hierarchical relationship preservation (accounts → transactions → details) 4. Out-of-sequence detection (items marked with *) 5. Financial domain conventions (check numbers, terminal IDs, merchant data)""" doc_str = json.dumps(sample["document"]) extract_str = json.dumps(sample["extracted_data"]) total_tokens = estimate_tokens(doc_str) + estimate_tokens(extract_str) if total_tokens &gt; MAX_TOKENS: print(f"Warning: Sample too large ({total_tokens} tokens), skipping...") return None return { "schemaVersion": "bedrock-conversation-2024", "messages": [ { "role": "user", "content": [{"text": doc_str}] }, { "role": "assistant", "content": [{"text": extract_str}] } ] }# Read inputwith open(INPUT_FILE, "r") as f: pulse_data = json.load(f)if isinstance(pulse_data, dict): pulse_data = [pulse_data]# Generate truncated samplesall_samples = []skipped = 0for record in pulse_data: truncated_samples = create_truncated_samples(record) for sample in truncated_samples: nova_record = convert_to_nova_format(sample) if nova_record: all_samples.append(nova_record) else: skipped += 1# Write to JSONLwith open(OUTPUT_FILE, "w") as f: for nova_record in all_samples: f.write(json.dumps(nova_record) + "\n")print(f"✓ Created {len(all_samples)} training samples")print(f"✓ Skipped {skipped} samples that were too large")print(f"✓ Output saved to: {OUTPUT_FILE}")print(f"All samples are under {MAX_TOKENS} tokens (limit: 32,768)")print(f"Next steps:")print(f"1. Verify: wc -l {OUTPUT_FILE}")print(f"2. Upload: aws s3 cp {OUTPUT_FILE} s3://anypulse/training-data/nova_dataset.jsonl")print(f"3. Create new fine-tuning job")"""TRAINING FORMAT EXPLANATION:What this fine-tuning teaches Nova Micro:This conversion script creates training samples in a format that teaches Nova Micro domain-specific financial document understanding through pattern learning. While the training samples use a direct JSON-to-JSON mapping (user message contains Pulse extracted JSON, assistant message contains the same structured JSON), the model learns several key capabilities:1. DOCUMENT STRUCTURE RECOGNITION - Hierarchical relationships: Headers → Tables → Text → Page Numbers - Bounding box spatial understanding: Coordinate systems and element positioning - Multi-page document handling: Page number tracking and cross-page references 2. FINANCIAL DATA PATTERNS - Table structure preservation: Row/column semantics, cell-level extraction - Confidence score interpretation: High-confidence fields (0.99+) vs. lower confidence - Data type consistency: Account numbers, dates, monetary amounts, check numbers 3. STRUCTURAL CONSISTENCY - Field naming conventions: "content", "confidence", "page_number", "bounding_box" - Nested object relationships: Tables contain cell_data arrays with position metadata - Metadata preservation: Original_content alongside normalized values for audit trails4. DOMAIN-SPECIFIC CONVENTIONS - Financial document sections: Headers, footers, transaction tables, summary sections - Out-of-sequence detection: Items marked with asterisk (*) in check numbers - Merchant data extraction: Terminal IDs, location information, transaction referencesLEARNING MECHANISM:The model learns through exposure to Pulse AI's high-quality structured extraction patterns. By seeing hundreds of examples of how Pulse structures financial document data (with confidence scores, bounding boxes, hierarchical relationships), Nova Micro internalizes these patterns and can apply them to new financial documents.This approach is effective because:- Pulse AI provides consistently structured, high-quality training data- The JSON schema is self-documenting (field names indicate purpose)- Repetition across samples reinforces structural patterns- Confidence scores teach the model which extractions are reliableALTERNATIVE APPROACHES:For production deployments requiring more explicit task framing, consider adding instructional prompts to the training samples: instructional_prompt = f'''You are a financial document extraction specialist. Extract structured information from the following financial document and return it as valid JSON. Requirements: - Extract all key financial data (accounts, balances, transactions, dates) - Use consistent field naming (snake_case format) - Convert dates to ISO 8601 format (YYYY-MM-DD) - Represent monetary amounts as numbers with currency metadata - Preserve hierarchical relationships - Detect out-of-sequence items (marked with *) Financial Document: {doc_str} Return only the extracted JSON without explanations.'''This instructional approach provides explicit requirements and task context, which can improve generalization to document types not seen during training. However, for workflows where Pulse AI handles extraction and the model primarily learns to replicate Pulse's output structure, the current direct mapping approach is sufficient and avoids token overhead from lengthy instructions.PRODUCTION CONSIDERATIONS:- Training dataset size: 100–500 samples for pilot, 5,000–10,000 for production- Evaluation metrics: Compare fine-tuned model output against Pulse baseline- Iterative improvement: Retrain quarterly with new document types and edge cases- Quality monitoring: Track confidence scores and manual review rates post-deployment"""
```

### ** 运行转换脚本：python3 convert_to_nova.py**

这会生成一个 jsonl 文件：`nova_dataset.jsonl`

微调之后，Nova Micro 应当在以下方面有所改进：完整的文档结构识别、全面的表格抽取、跨文档数据整合以及财务文档惯例。

- 创建用于训练数据的 S3 桶（如果尚未创建）：

```
aws s3 mb s3://your-unique-bucket-name --region us-east-1
```

### ** 启用版本控制以保护数据： **

```
aws s3api put-bucket-versioning --bucket your-unique-bucket-name --versioning-configuration Status=Enabled
```

- 把 Nova 训练数据集写入你的 S3 训练桶，供 Amazon Bedrock Nova 微调使用

```
aws s3 cp nova_dataset.jsonl s3://<your s3 bucket>/training-data/
```

注意：Amazon Bedrock 微调作业和自定义模型部署都会产生费用。继续之前，请先查看 Amazon Bedrock 定价 `https://aws.amazon.com/bedrock/pricing/`。

- 接下来运行 Amazon Bedrock 训练作业

```
aws bedrock create-model-customization-job  --job-name my-fine-tuning-job-nova-micro   --custom-model-name my-custom-pulse-model-nova-micro  --role-arn arn:aws:iam::<Your-AWS-Account>:role/AmazonBedrockNovaFineTuningRole   --base-model-identifier amazon.nova-micro-v1:0:128k  --training-data-config s3Uri=s3://<your-s3-bucket>/training-data/nova_dataset.jsonl --output-data-config s3Uri=s3://<your-s3-bucket>/output/  --hyper-parameters '{"epochCount":"2","learningRate":"0.00001","learningRateWarmupSteps":"10"}'
```

- 你可以在控制台中监控训练进度

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/05/02/ML-19858-image-3.png)

或者运行以下命令

```
export CUSTOM_MODEL_ARN=$(aws bedrock get-model-customization-job  --job-identifier "<JobArn>"  --region us-east-1  --query 'outputModelArn'  --output text)
```

```
echo "Your custom model ARN: $CUSTOM_MODEL_ARN"
```

jobArn 可以从控制台获取，也可以从刚运行的作业输出中获取。

完成后，控制台会反映相应状态

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/05/02/ML-19858-image-4.png)

- 要部署新的自定义模型，请运行：

```
aws bedrock create-custom-model-deployment  --model-deployment-name "my-custom-pulse-model-deployment"  --model-arn "$CUSTOM_MODEL_ARN"  --region us-east-1
```

- 检查自定义模型部署状态

```
aws bedrock get-custom-model-deployment --custom-model-deployment-identifier "your-deployment-name-or-arn" --region us-east-1
```

状态为“Active”即表示部署完成

确认模型已就绪：

```
aws bedrock get-provisioned-model-throughput --provisioned-model-id <model-id> --region us-east-1
```

在进入测试之前，确认状态显示为“**InService**”。使用 Amazon Bedrock playground 进行测试。

### **测试用的 prompt： **

```
Extract detailed transaction information from this bank statement:
SAMPLE Statement of Account 12345678

Transaction Details:
10/02 - POS PURCHASE TERMINAL 24349201 WAL-MART #3492 WICHITA KS 00-00-00 00:00 PM 0000000000000000 - $4.23
10/04 - POS PURCHASE TERMINAL 443565 PLAYERS SPORTS BAR AND GRILL WICHITA KS 00-00-00 00:00 PM 0000000000000000 - $11.68
10/05 - CHECK 1234 - $9.98
10/05 - POS PURCHASE TERMINAL 422443 KWAN COURT WICHITA KS 00-00-00 00:00 PM 0000000000000000 - $25.50
10/12 - CHECK 1236* - $69.00
10/14 - CHECK 1237 - $180.63

Checks Paid Table:
Check # | Date | Amount | Check # | Date | Amount
1234 | 10/05 | $9.98 | 1238 | 10/28 | $91.06
1236* | 10/12 | $69.00 | 1239 | 10/30 | $451.20
1237 | 10/14 | $180.63 | 1246* | 10/30 | $37.07

For each POS purchase, extract:
1. Terminal ID
2. Merchant name
3. Location (city, state)
4. Transaction reference number
5. Amount

For each check, extract:
1. Check number
2. Date cleared
3. Amount
4. Sequence status (normal or out-of-sequence marked with *)

Provide output as structured JSON with nested objects for transaction details.
```

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/05/02/ML-19858-image-5.png)

**结果**：

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/05/02/ML-19858-image-6.png)

## **性能对比**

模型对比：领域知识评估

| **指标** | **Nova Micro（基座）** | **my-custom-pulse-model-nova-micro-v5** |
| --- | --- | --- |
| **延迟** | 540,508 ms（约 9 分钟） | 543,600 ms（约 9 分钟 3.6 秒） |
| **抽取到的支票** | 6 张中 3 张 | 6 张中 6 张 |
| **抽取到的 POS 消费** | 3 笔中 3 笔 | 3 笔中 3 笔 |
| **交易组织方式** | 按类型分开 | 按时间顺序 |
| **完整性** | 支票数据的 50% | 支票数据的 100% |
| **顺序状态准确性** | 部分（3 张支票） | 完整（全部 6 张支票） |
| **JSON 结构** | 分段格式 | 统一的交易列表 |
| **领域知识** | 基础抽取 | 全面的文档理解 |

*免责声明：这些指标仅针对该示例文档数据集，你的结果会有所不同*

## 清理

完成以下清理任务，以免产生费用。

- 删除实例配置文件：`aws iam delete-instance-profile --instance-profile-name BedrockTutorialProfile`
- 终止 EC2 实例：`aws ec2 terminate-instances --instance-ids <instance-id>`
- 删除安全组：`aws ec2 delete-security-group --group-id <security-group-id> --region us-east-1`
- 删除密钥对：`aws ec2 delete-key-pair --key-name <key-pair-name> --region us-east-1`
- 删除自定义模型部署：`aws bedrock delete-custom-model-deployment --custom-model-deployment-identifier <deployment-name> --region us-east-1`
- 删除自定义模型：`aws bedrock delete-custom-model --model-identifier $CUSTOM_MODEL_ARN --region us-east-1`

**警告：** 数据丢失风险 – 以下命令将永久删除所有训练数据和输出。

继续之前：1）确认 S3 桶中只有教程数据，2）备份你需要保留的文件，3）确认你已正确记下桶名。

- 从 S3 删除微调训练数据：`aws s3 rm s3://<your-bucket>/training-data/ --recursive`
- 从 S3 删除微调作业输出：`aws s3 rm s3://<your-bucket>/output/ --recursive`
- 如果不再需要，删除 S3 桶：`aws s3 rb s3://<your-bucket>`
- 移除 IAM 策略：

```
aws iam delete-role-policy --role-name AmazonBedrock-FineTuning-S3-Role --policy-name Bedrock-S3-Access-Policy
```

- 删除 Secrets Manager 密钥：`aws secretsmanager delete-secret --secret-id pulse-api-key --force-delete-without-recovery --region us-east-1`
- 删除微调作业：`aws bedrock stop-model-customization-job --job-identifier <job-arn> --region us-east-1`

这篇 AWS 博客给出了迭代微调的详细说明，因此你可以基于此前定制的模型持续改进，而不必从头开始。Pulse 把非结构化文档转换为结构化、与 schema 对齐的输出。这些输出可以通过程序导出为 JSONL 数据集，兼容 Amazon Bedrock 对文本模型和视觉模型的微调要求。这实质上让 Pulse 承担抽取与数据质量的繁重工作，同时让生成 Amazon Bedrock 模型定制所需的训练数据集变得简单直接。

## 结论

通过把 Pulse AI 先进的文档理解与 AWS 的 ML 能力结合，你可以构建比传统方法更快、更准确、更具扩展性的财务数据处理系统。该架构展示了使用 Amazon Bedrock 与 Pulse AI 进行财务文档处理的生产级方案。上手 Pulse AI 非常简单。

注册一个 [Pulse AI Standard 账户](https://www.runpulse.com/)，开始在你的财务工作流中使用微调模型。如果你是初次使用该系统，[Pulse AI 快速上手指南](https://docs.runpulse.com/quickstart)提供了分步指引，帮助你配置第一个微调作业，并部署贴合组织需求的自定义模型。如需个性化协助，或对大规模实施微调有疑问，请联系 [hello@runpulse.com](mailto:hello@runpulse.com) 的团队——他们随时准备帮助你释放领域专属 AI 的全部潜力。

微调真正的威力，在于用组织独有的财务数据集补充基座模型（FM）。用你的专有文档、术语和业务流程训练模型，可以打造出通用模型通常无法企及的专业能力。这种做法把 AI 从通用工具转变为理解你特定财务领域细微差别的战略资产。

**更多资源**

要深入理解监督式微调并探索进阶实施策略，请参阅 [AWS Nova 微调指南](https://docs.aws.amazon.com/nova/latest/userguide/nova-fine-tune.html)以及[自定义 Amazon Nova 模型](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-models.html)的文档。这些资源提供了关于超参数改进、数据准备最佳实践和部署模式的技术细节。[Pulse API 文档](https://docs.runpulse.com/introduction)提供了将生产级文档抽取能力集成到你现有工作流的全面指引。

## 关于作者
