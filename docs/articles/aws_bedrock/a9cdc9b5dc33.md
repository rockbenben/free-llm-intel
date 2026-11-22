---
vendor: aws_bedrock
title: Build an enterprise synthetic data strategy using Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-an-enterprise-synthetic-data-strategy-using-amazon-bedrock
date: 2025-04-08
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: dea5f23fbde8
---

# 使用 Amazon Bedrock 构建企业级合成数据策略

AI 格局正在快速演进，越来越多的组织认识到合成数据在推动创新方面的力量。然而，希望使用 AI 的企业面临一大障碍：如何安全地使用敏感数据。严格的隐私法规使得使用此类数据充满风险，即便做了强力的匿名化处理也是如此。高级分析有可能发现隐藏的相关性并反推出真实数据，从而导致合规问题与声誉受损。此外，许多行业还苦于缺少软件测试、产品开发和 AI 模型训练等关键流程所需的高质量、多样化数据集。这种数据短缺会阻碍创新，拖慢各项业务运营的开发周期。

组织需要创新的解决方案，在不牺牲伦理或数据隐私的前提下释放数据驱动流程的潜力。合成数据正是在此登场——它模拟真实数据的统计属性与模式，同时完全是虚构的。借助合成数据，企业可以训练 AI 模型、开展分析、开发应用，而不必冒泄露敏感信息的风险。合成数据有效地弥合了数据可用性与隐私保护之间的鸿沟。不过，创建高质量的合成数据也伴随着重大挑战：

- **数据质量**——要确保合成数据准确反映真实世界的统计属性与细微差别是很困难的。数据可能无法捕获罕见的边界情况或人类互动的完整谱系。
- **偏差管理**——虽然合成数据有助于减少偏差，但若管理不慎，也可能无意间放大既有偏差。合成数据的质量在很大程度上取决于用于生成它的模型与数据。
- **隐私与可用性**——在保护隐私与保持数据可用性之间取得平衡是复杂的。如果实施不当，存在被逆向工程或数据泄露的风险。
- **校验难题**——核实合成数据的质量与代表性往往需要与真实数据比对，而在处理敏感信息时这可能会带来问题。
- **现实差距**——合成数据可能无法完全捕捉真实世界的动态特性，从而可能导致模型在合成数据上的表现与真实应用场景脱节。

本文将探讨如何使用 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 生成合成数据，在权衡这些挑战与潜在收益的基础上，为 AI 与机器学习（ML）等多个行业的各类应用制定有效策略。Amazon Bedrock 提供了一整套丰富的能力来构建生成式 AI 应用，并聚焦于安全、隐私与负责任的 AI。Amazon Bedrock 构建于 AWS 体系之内，旨在帮助维持企业使用所需的安全与合规标准。

## 高质量合成数据的特征

要真正有效，合成数据必须既贴近现实又可靠。这意味着它应准确反映真实世界数据的复杂性与细微差别，同时保持完全的匿名性。高质量的合成数据集具备若干关键特征，这些特征使其能够忠实于原始数据：

- **数据结构**——合成数据应保持与真实数据相同的结构，包括相同的列数、数据类型以及不同数据源之间的关系
- **统计属性**——合成数据应模拟真实数据的统计属性，例如均值、中位数、标准差、变量间的相关性以及分布模式。
- **时间模式**——如果真实数据呈现时间模式（例如昼夜模式或季节模式），合成数据也应反映这些模式。
- **异常与离群值**——真实世界的数据常常包含异常与离群值。合成数据也应包含比例与分布相近的异常与离群值，以准确代表真实世界场景。
- **引用完整性**——如果真实数据在不同数据源之间存在关系与依赖，合成数据应保持这些关系，以维护引用完整性。
- **一致性**——合成数据应在不同数据源之间保持一致，并维护它们之间的关系与依赖，从而形成连贯统一的数据集表示。
- **可扩展性**——合成数据的生成过程应可扩展，以处理海量数据，并支持为不同场景与用例生成合成数据。
- **多样性**——合成数据应捕获真实数据中存在的多样性。

## 解决方案概览

生成既能保护隐私又有用的合成数据需要深思熟虑的方法。下图展示了所提方案的高层架构。该过程包含三个关键步骤：

- 识别出定义真实数据结构与统计属性的校验规则。
- 使用 Amazon Bedrock 依据这些规则生成代码，用于创建合成数据子集。
- 把多个合成子集合并成完整数据集。

![生成合成数据的工作流](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-architecture.png)

下面我们详细探讨创建有用合成数据的这三个关键步骤。

### 第 1 步：定义数据规则与特征

- 要创建合成数据集，首先建立清晰的规则，捕获目标数据的本质：
- 运用领域知识识别关键属性与关系。
- 研究现有的公开数据集、学术资源与行业文档。
- 使用 [AWS Glue DataBrew](https://aws.amazon.com/glue/features/databrew/)、Amazon Bedrock 或开源替代方案（例如 [Great Expectations](https://github.com/great-expectations/great_expectations)）等工具来分析数据结构与模式。
- 制定一套全面的规则集，涵盖：数据类型与取值范围、字段间关系、质量标准、领域特有的模式与异常

这一基础步骤确保你的合成数据能准确反映所在行业的真实世界场景。

### 第 2 步：使用 Amazon Bedrock 生成代码

使用 Amazon Bedrock 的语言模型把你的数据规则转化为可运行的代码：

- 根据代码生成能力与领域相关性选择合适的 Amazon Bedrock 模型。
- 编写详细的 [prompt](https://docs.aws.amazon.com/bedrock/latest/userguide/design-a-prompt.html)，描述期望的代码输出，包括数据结构与生成规则。
- 使用 Amazon Bedrock API 依据你的 prompt 生成 Python 代码。
- 以迭代方式打磨代码：审查其准确性与效率、按需调整 prompt、在复杂场景中纳入开发者的输入

最终得到一个量身定制的脚本，它能生成符合你具体要求的合成数据条目，并高度贴近你所在领域的真实数据。

### 第 3 步：组装并扩展合成数据集

把你生成的数据转化为全面、能代表真实世界的数据集：

- 使用第 2 步的代码为各种场景创建多个合成子集。
- 基于领域知识合并子集，保持贴近现实的占比与关系。
- 对齐时间或序列成分，并引入受控的随机性以形成自然变化。
- 把数据集扩展到所需规模，体现不同的时间段或人群。
- 以适当的频率纳入罕见事件与边界情况。
- 生成配套的元数据，描述数据集特征与生成过程。

最终得到的是一个多样、贴近现实的合成数据集，可用于系统测试、ML 模型训练或数据分析等用途。元数据则让生成过程与数据特征变得透明。这些措施共同构成一个稳健的合成数据集，既高度接近真实世界数据，又避免直接暴露敏感信息。这套通用方法可适配各类数据集，从金融交易到医疗记录，借助 Amazon Bedrock 的代码生成能力，以及领域知识在数据校验与结构化方面的专业性。

## 差分隐私在合成数据生成中的重要性

尽管合成数据为分析与机器学习带来诸多好处，但必须认识到：即便是人工生成的数据集，隐私担忧依然存在。在努力创建高保真合成数据的同时，我们也必须对原始数据保持强健的隐私保护。合成数据虽模拟真实数据中的模式，但若创建不当，就有可能泄露源数据集中敏感信息的细节。差分隐私正是在此发挥作用。差分隐私是一个数学框架，提供了量化并控制数据分析相关隐私风险的方法。它的做法是向数据生成过程注入经过校准的噪声，使得几乎不可能推断出源数据集中任何单个数据点或机密信息。

差分隐私可以防范对手试图提取数据细节的重识别攻击。添加到合成数据中的经过仔细校准的噪声确保：即便对手尝试，把输出关联回原始数据中的具体记录在计算上也不可行，同时仍保持数据集的整体统计属性。这使合成数据能够贴近真实世界特征，在保护隐私的同时仍可用于分析与建模。通过在合成数据生成过程中引入差分隐私技术，你可以创建既保持原始数据统计属性、又提供强隐私保证的数据集。它让组织能够更自由地共享数据、在敏感项目上协作，并以更低的隐私泄露风险开发 AI 模型。例如在医疗健康领域，具备差分隐私的合成患者数据可以加速研究，而不损害单个患者的机密性。

随着合成数据生成领域的不断进步，引入差分隐私已不仅是一项最佳实践，更是负责任的数据科学的必要组成部分。这种做法为数据可用性与隐私保护和谐共存的未来铺平了道路，在促进创新的同时保障个人权利。不过，尽管差分隐私提供了强有力的理论保证，其实际落地仍可能颇具挑战。组织必须谨慎权衡隐私与可用性之间的取舍，因为提升隐私保护往往要以降低数据可用性为代价。

## 使用 Amazon Bedrock 为 Trusted Advisor 核查项构建合成数据集

本文将带你了解如何使用 Amazon Bedrock 为 [AWS Trusted Advisor](https://aws.amazon.com/premiumsupport/technology/trusted-advisor/) 核查项创建合成数据集。Trusted Advisor 提供实时指引来优化你的 AWS 环境，通过 500 多项对照 AWS 最佳实践的检查来改善性能、安全与成本效益。我们以“Underutilized Amazon EBS Volumes”（EBS 卷利用率不足）检查（[checkid: DAvU99Dc4C](https://docs.aws.amazon.com/managedservices/latest/accelerate-guide/tr-supported-checks.html)）为例，演示合成数据的生成方法。

通过阅读本文，你将获得以下方面的实用知识：

- 为 Trusted Advisor 核查项定义数据规则
- 使用 Amazon Bedrock 生成数据创建代码
- 组装并扩展合成数据集

这套方法可应用于 500 多项 Trusted Advisor 检查，使你能够构建全面、兼顾隐私的数据集，用于测试、训练与分析。无论你是想加深对 Trusted Advisor 建议的理解，还是想制定新的优化策略，合成数据都提供了强大的可能性。

### 前提条件

要实施这套方法，你必须拥有一个具备相应权限的 AWS 账户。

- AWS 账户设置：需要以下服务的 IAM 权限：Amazon Bedrock、AWS Trusted Advisor、Amazon EBS
- AWS 服务访问：在你的区域中已启用 Amazon Bedrock 访问权限、可访问 Amazon Bedrock 中的 Anthropic Claude 模型、具备 Enterprise 或 Business 支持计划以获得完整的 Trusted Advisor 访问权限
- 开发环境：已安装 Python 3.8 或更高版本、所需的 Python 包：pandas、numpy、random、boto3
- 知识要求：基本了解以下内容：Python 编程、AWS 服务（尤其是 EBS 与 Trusted Advisor）、数据分析概念、JSON/YAML 文件格式

### 定义 Trusted Advisor 核查项规则

首先查看“Underutilized Amazon EBS Volumes”检查的真实 Trusted Advisor 核查结果。分析这些结果的结构与内容，识别关键数据元素及其关系。请特别关注以下方面：

- **标准字段**——检查 ID、卷 ID、卷类型、快照 ID 与快照时长
- **卷属性**——大小、类型、时长与成本
- **使用指标**——读/写操作数、吞吐量与 IOPS
- **时间模式**——卷类型与大小的变化
- **元数据**——标签、创建日期与最近挂载日期

在研究这些元素时，记录每个属性的典型取值范围、模式与分布。例如，观察卷大小如何与卷类型相关，或使用模式在开发环境与生产环境之间有何差异。这一分析将帮助你制定一套准确反映真实 Trusted Advisor 核查结果的规则。

在分析“Underutilized Amazon EBS Volumes”检查的真实 Trusted Advisor 输出之后，我们识别出以下关键模式与规则：

- **卷类型**——考虑 gp2、gp3、io1、io2 与 st1 卷类型。核实卷大小对相应卷类型是有效的。
- **准则**——覆盖多个 AWS 区域，并使用适当的卷类型。把快照时长与卷时长相关联。
- **数据结构**——每条核查结果都应包含相同的列。

以下是一个示例规则集：

```
Analysis of the AWS Trusted Advisor finding for "Underutilized Amazon EBS Volumes":
1. Columns in the Trusted Advisor Finding:
- Region
- Volume ID
- Volume Name
- Volume Type
- Volume Size
- Monthly Storage Cost
- Snapshot ID
- Snapshot Name
- Snapshot Age
2. Key Columns and Their Significance:
- Region: AWS region where the EBS volume is located
- Volume ID: Unique identifier for the EBS volume
- Volume Type: Type of EBS volume (e.g., gp2, io1, st1)
- Volume Size: Size of the volume in GB
- Monthly Storage Cost: Estimated cost for storing the volume
- Snapshot ID: Identifier of the most recent snapshot (if any)
- Snapshot Age: Age of the most recent snapshot
3. Relationships and Patterns:
- Volume ID and Snapshot ID relationship: Each volume may have zero or more snapshots
- Region and cost correlation: Storage costs may vary by region
- Volume Type and Size correlation: Certain volume types have size limitations
- Volume Size and Cost correlation: Larger volumes generally cost more
- Snapshot Age and utilization: Older snapshots might indicate less active volumes
4. Data Types and Formats:
- Region: String (e.g., "us-east-1")
- Volume ID: String starting with "vol-"
- Volume Name: String (can be null)
- Volume Type: String (gp2, gp3, io1, io2, st1, sc1, standard)
- Volume Size: Integer (in GB)
- Monthly Storage Cost: Decimal number
- Snapshot ID: String starting with "snap-" (can be null)
- Snapshot Name: String (can be null)
```

### 使用 Amazon Bedrock 生成代码

规则定义好之后，你就可以使用 Amazon Bedrock 生成 Python 代码，来创建合成的 Trusted Advisor 核查结果。

以下是给 Amazon Bedrock 的示例 prompt：

```
Give me python code to create a 100 row pandas df with the following data:
<<Copy paste the ruleset from the above step>>
```

你可以通过 Amazon Bedrock 上的 [Anthropic’s Claude 3.5 Sonnet](https://aws.amazon.com/bedrock/claude/) 把这段 prompt 提交到 [Amazon Bedrock 聊天测试场](https://docs.aws.amazon.com/bedrock/latest/userguide/playgrounds.html)，并收到生成的 Python 代码。请仔细审阅这段代码，核实它满足所有规格并能生成贴近现实的数据。如有必要，迭代你的 prompt，或对代码做手动调整，以补齐缺失的逻辑或处理边界情况。

生成的代码将作为基础，用于创建多样、贴近现实且符合既定参数的合成 Trusted Advisor 核查结果。以这种方式使用 Amazon Bedrock，你可以快速开发出复杂的数据生成代码；若没有它，这需要大量人工投入与领域专业知识才能完成。

### 创建数据子集

借助由 Amazon Bedrock 生成、并用你的自定义函数打磨过的代码，你现在可以为“Underutilized Amazon EBS Volumes”检查创建多样的合成 Trusted Advisor 核查结果子集。这一方法让你能够模拟广泛的真实世界场景。在下面的示例代码中，我们把 volume_id 与 snapshot_id 的格式分别定制为以 vol-9999 和 snap-9999 开头：

```
import pandas as pd
import numpy as np
import random

def generate_volume_id():
return f"vol-9999{''.join(random.choices('0123456789abcdef', k=17))}"

def generate_snapshot_id():
return f"snap-9999{''.join(random.choices('0123456789abcdef', k=17))}"

def generate_volume_name():
prefixes = ['app', 'db', 'web', 'cache', 'log']
suffixes = ['prod', 'dev', 'test', 'staging']
return f"{random.choice(prefixes)}-{random.choice(suffixes)}-{random.randint(1, 100)}"

def step3_generate_base_data():

# Generate synthetic data
num_records = 1000
regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
volume_types = ['gp2', 'gp3', 'io1', 'io2', 'st1', 'sc1', 'standard']

data = {
'Region': np.random.choice(regions, num_records),
'Volume ID': [generate_volume_id() for _ in range(num_records)],
'Volume Name': [generate_volume_name() if random.random() > 0.3 else None for _ in range(num_records)],
'Volume Type': np.random.choice(volume_types, num_records, p=[0.4, 0.2, 0.1, 0.1, 0.1, 0.05, 0.05]),
'Volume Size': np.random.choice(range(1, 1001), num_records),
'Monthly Storage Cost': np.random.uniform(0.1, 100, num_records).round(2),
'Snapshot ID': [generate_snapshot_id() if random.random() > 0.4 else None for _ in range(num_records)],
'Snapshot Name': [f"snapshot-{i}" if random.random() > 0.6 else None for i in range(num_records)],
'Snapshot Age': [random.randint(1, 365) if random.random() > 0.4 else None for _ in range(num_records)]
}

df = pd.DataFrame(data)

# Apply some logic and constraints
df.loc[df['Volume Type'] == 'gp2', 'Volume Size'] = df.loc[df['Volume Type'] == 'gp2', 'Volume Size'].clip(1, 16384)
df.loc[df['Volume Type'] == 'io1', 'Volume Size'] = df.loc[df['Volume Type'] == 'io1', 'Volume Size'].clip(4, 16384)
df.loc[df['Volume Type'] == 'st1', 'Volume Size'] = df.loc[df['Volume Type'] == 'st1', 'Volume Size'].clip(500, 16384)
df.loc[df['Volume Type'] == 'sc1', 'Volume Size'] = df.loc[df['Volume Type'] == 'sc1', 'Volume Size'].clip(500, 16384)

# Adjust Monthly Storage Cost based on Volume Size and Type
df['Monthly Storage Cost'] = df.apply(lambda row: row['Volume Size'] * random.uniform(0.05, 0.15) * (1.5 if row['Volume Type'] in ['io1', 'io2'] else 1), axis=1).round(2)

# Ensure Snapshot ID, Name, and Age are consistent
df.loc[df['Snapshot ID'].isnull(), 'Snapshot Name'] = None
df.loc[df['Snapshot ID'].isnull(), 'Snapshot Age'] = None

# Add some underutilized volumes
df['Underutilized'] = np.random.choice([True, False], num_records, p=[0.7, 0.3])
df.loc[df['Underutilized'], 'Monthly Storage Cost'] *= random.uniform(1.2, 2.0)

return df
```

这段代码创建的子集包含：

- 多种卷类型与实例类型
- 不同的利用率水平
- 偶尔出现的配置错误（例如利用率不足的卷）
- 多样的区域分布

### 合并并扩展数据集

合并与扩展合成数据的过程，涉及把多个已生成的数据集合并起来，同时引入贴近现实的异常，以创建全面且有代表性的数据集。这一步对于确保合成数据反映真实世界场景中的复杂性与多变性至关重要。组织通常会以特定比例（一般是数据集的 5–10%）引入受控异常，用以模拟生产环境中可能出现的各种边界情况与不寻常模式。这些异常有助于测试系统响应、开发监控方案，以及训练 ML 模型去识别潜在问题。

在为利用率不足的 EBS 卷生成合成数据时，你可以引入诸如超大卷（比所需大 5–10 倍）、带有旧快照的卷（超过 365 天）或利用率很低但成本高昂的卷等异常。例如，合成数据集可能包含一个 1 TB 的 gp2 卷却只使用了 100 GB 空间，用以模拟资源过度配置的真实场景。参见以下代码：

```
import pandas as pd
import numpy as np
import random
def introduce_anomalies(df, anomaly_rate=0.1):
"""
Introduce various volume-related anomalies into the dataset.

:param df: The input DataFrame
:param anomaly_rate: The rate at which to introduce anomalies (default 10%)
:return: DataFrame with anomalies introduced
"""
num_anomalies = int(len(df) * anomaly_rate)
anomaly_indices = np.random.choice(df.index, num_anomalies, replace=False)

df['Anomaly'] = pd.NA  # Initialize Anomaly column with pandas NA

for idx in anomaly_indices:
anomaly_type = random.choice([
'oversized_volume',
'old_snapshot',
'high_cost_low_size',
'mismatched_type',
'very_old_volume'
])

if anomaly_type == 'oversized_volume':
df.at[idx, 'Volume Size'] = int(df.at[idx, 'Volume Size'] * random.uniform(5, 10))
df.at[idx, 'Monthly Storage Cost'] *= random.uniform(5, 10)

elif anomaly_type == 'old_snapshot':
df.at[idx, 'Snapshot Age'] = random.randint(365, 1000)

elif anomaly_type == 'high_cost_low_size':
df.at[idx, 'Volume Size'] = random.randint(1, 10)
df.at[idx, 'Monthly Storage Cost'] *= random.uniform(10, 20)

elif anomaly_type == 'mismatched_type':
if df.at[idx, 'Volume Type'] in ['gp2', 'gp3']:
df.at[idx, 'Volume Type'] = random.choice(['io1', 'io2'])
else:
df.at[idx, 'Volume Type'] = random.choice(['gp2', 'gp3'])

elif anomaly_type == 'very_old_volume':
df.at[idx, 'Volume Name'] = f"old-volume-{random.randint(1, 100)}"
if pd.notna(df.at[idx, 'Snapshot Age']):
df.at[idx, 'Snapshot Age'] = random.randint(1000, 2000)

df.at[idx, 'Anomaly'] = anomaly_type

return df
```

下面的截图展示了生成的部分示例行。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-sample_rows.png)

### 校验合成的 Trusted Advisor 核查结果

数据校验是一个关键步骤，用于核实合成数据的质量、可靠性与代表性。这一过程包括执行严谨的统计分析，以验证生成的数据保持了合理的分布、关系与模式，并与真实世界场景相符。校验应同时包含量化指标（统计测度）与定性评估（模式分析）。组织应实施全面的校验框架，纳入分布分析、相关性检查、模式验证与异常检测。定期对数据做可视化有助于发现不一致或意料之外的模式。

对于 EBS 卷数据，校验可能包括分析不同卷类型（gp2、gp3、io1）之间的卷大小分布、核实成本相关性符合预期模式，以及确保引入的异常（如利用率不足的卷）保持贴近现实的占比。例如，验证利用率不足的卷所占百分比与典型企业环境相符（或许是总量的 15–20%），并验证成本与大小的关系在各卷类型之间仍然贴近现实。

下面的图展示了我们的校验检查示例。

- 下面的截图展示了所生成合成数据集的统计信息。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-statistics.png)
- 下图展示了所生成合成数据集中利用率不足卷的占比。
![利用率不足卷的占比](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-underutilized_proportion.png)
- 下图展示了所生成合成数据集中卷大小的分布。
![卷大小分布](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-volume_size_distribution.png)
- 下图展示了所生成合成数据集中卷类型的分布。
![卷类型分布](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-volume_type_distribution.png)
- 下图展示了所生成合成数据集中快照时长的分布。
![快照时长](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-snapshot_age.png)

## 用差分隐私增强合成数据

在探讨了为 Trusted Advisor“Underutilized Amazon EBS Volumes”检查创建合成数据集的各个步骤之后，值得再回看差分隐私如何强化这套方法。当一家云咨询公司分析跨多个客户汇总的 Trusted Advisor 数据时，通过 [OpenDP](https://opendp.org/) 实现的差分隐私提供了所需的隐私与可用性之间的关键平衡。通过对利用率不足卷统计量的计算施加经过仔细校准的噪声，咨询顾问可以生成既保留跨区域、跨卷类型的关键模式、又在数学上保证单个客户机密性的合成数据集。这一方法确认合成数据保持足够的准确性以支撑有意义的趋势分析与建议，同时消除泄露客户特定基础设施细节或使用模式的风险——这使其成为我们合成数据生成流水线的理想补充。

## 结论

本文展示了如何使用 Amazon Bedrock 为企业需求创建合成数据。把 Amazon Bedrock 中可用的语言模型与行业知识结合起来，你就能构建一种灵活且安全的测试数据生成方式。这种方法有助于在不使用敏感信息的前提下创建贴近现实的数据集，节省时间与成本。它还便于在各项目之间做一致的测试，并避免使用真实用户数据带来的伦理问题。总体而言，这一策略为数据难题提供了扎实的解决方案，支撑更好的测试与开发实践。

在本系列的第 2 部分，我们将演示如何对不同数据集运用模式识别，以自动化生成规则集——这是 Amazon Bedrock 的 prompt 生成相应合成数据所需要的。

### 关于作者

** [![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-devi-100x125.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-devi-100x125.png)Devi Nair** 是 Amazon Web Services 的技术客户经理，为企业客户在 AWS 上构建、运营与优化工作负载提供战略指引。她专注于把云解决方案与业务目标对齐，以推动长期成功与创新。

** ![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-vishal-100x134.jpeg)Vishal Karlupia** 是 Amazon Web Services（多伦多）的资深技术客户经理/团队负责人。他专精于生成式 AI 应用，帮助客户在 AWS 上构建并扩展其 AI/ML 工作负载。工作之外，他喜欢户外活动，也喜欢让篝火一直烧着。

** ![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-srini.jpg)Srinivas Ganapathi** 是 Amazon Web Services 的首席技术客户经理。他常驻加拿大多伦多，与游戏行业客户合作，在 AWS 上运行高效的工作负载。

** ![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-nic-100x133.jpg)Nicolas Simard** 是常驻蒙特利尔的技术客户经理。他通过技术专长与架构最佳实践帮助组织加速 AI 采用之旅，并让他们从 AWS 的生成式 AI 能力中获得最大的业务价值。
