---
vendor: aws_bedrock
title: Build an enterprise synthetic data strategy using Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-an-enterprise-synthetic-data-strategy-using-amazon-bedrock
date: 2025-04-08
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: f08e7a7db88d
---

# Build an enterprise synthetic data strategy using Amazon Bedrock

The AI landscape is rapidly evolving, and more organizations are recognizing the power of synthetic data to drive innovation. However, enterprises looking to use AI face a major roadblock: how to safely use sensitive data. Stringent privacy regulations make it risky to use such data, even with robust anonymization. Advanced analytics can potentially uncover hidden correlations and reveal real data, leading to compliance issues and reputational damage. Additionally, many industries struggle with a scarcity of high-quality, diverse datasets needed for critical processes like software testing, product development, and AI model training. This data shortage can hinder innovation, slowing down development cycles across various business operations.

Organizations need innovative solutions to unlock the potential of data-driven processes without compromising ethics or data privacy. This is where synthetic data comes in—a solution that mimics the statistical properties and patterns of real data while being entirely fictitious. By using synthetic data, enterprises can train AI models, conduct analyses, and develop applications without the risk of exposing sensitive information. Synthetic data effectively bridges the gap between data utility and privacy protection. However, creating high-quality synthetic data comes with significant challenges:

- **Data quality** – Making sure synthetic data accurately reflects real-world statistical properties and nuances is difficult. The data might not capture rare edge cases or the full spectrum of human interactions.
- **Bias management** – Although synthetic data can help reduce bias, it can also inadvertently amplify existing biases if not carefully managed. The quality of synthetic data heavily depends on the model and data used to generate it.
- **Privacy vs. utility** – Balancing privacy preservation with data utility is complex. There’s a risk of reverse engineering or data leakage if not properly implemented.
- **Validation challenges** – Verifying the quality and representation of synthetic data often requires comparison with real data, which can be problematic when working with sensitive information.
- **Reality gap** – Synthetic data might not fully capture the dynamic nature of the real world, potentially leading to a disconnect between model performance on synthetic data and real-world applications.

In this post, we explore how to use [Amazon Bedrock](https://aws.amazon.com/bedrock/) for synthetic data generation, considering these challenges alongside the potential benefits to develop effective strategies for various applications across multiple industries, including AI and machine learning (ML). Amazon Bedrock offers a broad set of capabilities to build generative AI applications with a focus on security, privacy, and responsible AI. Built within the AWS landscape, Amazon Bedrock is designed to help maintain the security and compliance standards required for enterprise use.

## Attributes of high-quality synthetic data

To be truly effective, synthetic data must be both realistic and reliable. This means it should accurately reflect the complexities and nuances of real-world data while maintaining complete anonymity. A high-quality synthetic dataset exhibits several key characteristics that facilitate its fidelity to the original data:

- **Data structure** – The synthetic data should maintain the same structure as the real data, including the same number of columns, data types, and relationships between different data sources
- **Statistical properties** – The synthetic data should mimic the statistical properties of the real data, such as mean, median, standard deviation, correlation between variables, and distribution patterns.
- **Temporal patterns** – If the real data exhibits temporal patterns (for example, diurnal or seasonal patterns), the synthetic data should also reflect these patterns.
- **Anomalies and outliers** – Real-world data often contains anomalies and outliers. The synthetic data should also include a similar proportion and distribution of anomalies and outliers to accurately represent the real-world scenario.
- **Referential integrity** – If the real data has relationships and dependencies between different data sources, the synthetic data should maintain these relationships to facilitate referential integrity.
- **Consistency** – The synthetic data should be consistent across different data sources and maintain the relationships and dependencies between them, facilitating a coherent and unified representation of the dataset.
- **Scalability** – The synthetic data generation process should be scalable to handle large volumes of data and support the generation of synthetic data for different scenarios and use cases.
- **Diversity** – The synthetic data should capture the diversity present in the real data.

## Solution overview

Generating useful synthetic data that protects privacy requires a thoughtful approach. The following figure represents the high-level architecture of the proposed solution. The process involves three key steps:

- Identify validation rules that define the structure and statistical properties of the real data.
- Use those rules to generate code using Amazon Bedrock that creates synthetic data subsets.
- Combine multiple synthetic subsets into full datasets.

![workflow to generate synthetic data](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-architecture.png)

Let’s explore these three key steps for creating useful synthetic data in more detail.

### Step 1: Define data rules and characteristics

- To create synthetic datasets, start by establishing clear rules that capture the essence of your target data:
- Use domain-specific knowledge to identify key attributes and relationships.
- Study existing public datasets, academic resources, and industry documentation.
- Use tools like [AWS Glue DataBrew](https://aws.amazon.com/glue/features/databrew/), Amazon Bedrock, or open source alternatives (such as [Great Expectations](https://github.com/great-expectations/great_expectations)) to analyze data structures and patterns.
- Develop a comprehensive rule-set covering:  Data types and value ranges Inter-field relationships Quality standards Domain-specific patterns and anomalies

This foundational step makes sure your synthetic data accurately reflects real-world scenarios in your industry.

### Step 2: Generate code with Amazon Bedrock

Transform your data rules into functional code using Amazon Bedrock language models:

- Choose an appropriate Amazon Bedrock model based on code generation capabilities and domain relevance.
- Craft a detailed [prompt](https://docs.aws.amazon.com/bedrock/latest/userguide/design-a-prompt.html) describing the desired code output, including data structures and generation rules.
- Use the Amazon Bedrock API to generate Python code based on your prompts.
- Iteratively refine the code by:  Reviewing for accuracy and efficiency Adjusting prompts as needed Incorporating developer input for complex scenarios

The result is a tailored script that generates synthetic data entries matching your specific requirements and closely mimicking real-world data in your domain.

### Step 3: Assemble and scale the synthetic dataset

Transform your generated data into a comprehensive, real-world representative dataset:

- Use the code from Step 2 to create multiple synthetic subsets for various scenarios.
- Merge subsets based on domain knowledge, maintaining realistic proportions and relationships.
- Align temporal or sequential components and introduce controlled randomness for natural variation.
- Scale the dataset to required sizes, reflecting different time periods or populations.
- Incorporate rare events and edge cases at appropriate frequencies.
- Generate accompanying metadata describing dataset characteristics and the generation process.

The end result is a diverse, realistic synthetic dataset for uses like system testing, ML model training, or data analysis. The metadata provides transparency into the generation process and data characteristics. Together, these measures result in a robust synthetic dataset that closely parallels real-world data while avoiding exposure of direct sensitive information. This generalized approach can be adapted to various types of datasets, from financial transactions to medical records, using the power of Amazon Bedrock for code generation and the expertise of domain knowledge for data validation and structuring.

## Importance of differential privacy in synthetic data generation

Although synthetic data offers numerous benefits for analytics and machine learning, it’s essential to recognize that privacy concerns persist even with artificially generated datasets. As we strive to create high-fidelity synthetic data, we must also maintain robust privacy protections for the original data. Although synthetic data mimics patterns in actual data, if created improperly, it risks revealing details about sensitive information in the source dataset. This is where differential privacy enters the picture. Differential privacy is a mathematical framework that provides a way to quantify and control the privacy risks associated with data analysis. It works by injecting calibrated noise into the data generation process, making it virtually impossible to infer anything about a single data point or confidential information in the source dataset.

Differential privacy protects against re-identification exploits by adversaries attempting to extract details about data. The carefully calibrated noise added to synthetic data makes sure that even if an adversary tries, it is computationally infeasible to tie an output back to specific records in the original data, while still maintaining the overall statistical properties of the dataset. This allows the synthetic data to closely reflect real-world characteristics and remain useful for analytics and modeling while protecting privacy. By incorporating differential privacy techniques into the synthetic data generation process, you can create datasets that not only maintain statistical properties of the original data but also offer strong privacy guarantees. It enables organizations to share data more freely, collaborate on sensitive projects, and develop AI models with reduced risk of privacy breaches. For instance, in healthcare, differentially private synthetic patient data can accelerate research without compromising individual patient confidentiality.

As we continue to advance in the field of synthetic data generation, the incorporation of differential privacy is becoming not just a best practice, but a necessary component for responsible data science. This approach paves the way for a future where data utility and privacy protection coexist harmoniously, fostering innovation while safeguarding individual rights. However, although differential privacy offers strong theoretical guarantees, its practical implementation can be challenging. Organizations must carefully balance the trade-off between privacy and utility, because increasing privacy protection often comes at the cost of reduced data utility.

## Build synthetic datasets for Trusted Advisor findings with Amazon Bedrock

In this post, we guide you through the process of creating synthetic datasets for [AWS Trusted Advisor](https://aws.amazon.com/premiumsupport/technology/trusted-advisor/) findings using Amazon Bedrock. Trusted Advisor provides real-time guidance to optimize your AWS environment, improving performance, security, and cost-efficiency through over 500 checks against AWS best practices. We demonstrate the synthetic data generation approach using the “Underutilized Amazon EBS Volumes” check ([checkid: DAvU99Dc4C](https://docs.aws.amazon.com/managedservices/latest/accelerate-guide/tr-supported-checks.html)) as an example.

By following this post, you will gain practical knowledge on:

- Defining data rules for Trusted Advisor findings
- Using Amazon Bedrock to generate data creation code
- Assembling and scaling synthetic datasets

This approach can be applied across over 500 Trusted Advisor checks, enabling you to build comprehensive, privacy-aware datasets for testing, training, and analysis. Whether you’re looking to enhance your understanding of Trusted Advisor recommendations or develop new optimization strategies, synthetic data offers powerful possibilities.

### Prerequisites

To implement this approach, you must have an AWS account with the appropriate permissions.

- AWS Account Setup:  IAM permissions for:  Amazon Bedrock AWS Trusted Advisor Amazon EBS
- AWS Service Access:  Access enabled for Amazon Bedrock in your Region Access to Anthropic Claude model in Amazon Bedrock Enterprise or Business support plan for full Trusted Advisor access
- Development Environment:  Python 3.8 or later installed Required Python packages:  pandas numpy random boto3
- Knowledge Requirements:  Basic understanding of:   Python programming  AWS services (especially EBS and Trusted Advisor)  Data analysis concepts  JSON/YAML file format

### Define Trusted Advisor findings rules

Begin by examining real Trusted Advisor findings for the “Underutilized Amazon EBS Volumes” check. Analyze the structure and content of these findings to identify key data elements and their relationships. Pay attention to the following:

- **Standard fields** – Check ID, volume ID, volume type, snapshot ID, and snapshot age
- **Volume attributes** – Size, type, age, and cost
- **Usage metrics** – Read and write operations, throughput, and IOPS
- **Temporal patterns** – Volume type and size variations
- **Metadata** – Tags, creation date, and last attached date

As you study these elements, note the typical ranges, patterns, and distributions for each attribute. For example, observe how volume sizes correlate with volume types, or how usage patterns differ between development and production environments. This analysis will help you create a set of rules that accurately reflect real-world Trusted Advisor findings.

After analyzing real Trusted Advisor outputs for the “Underutilized Amazon EBS Volumes” check, we identified the following crucial patterns and rules:

- **Volume type** – Consider gp2, gp3, io1, io2, and st1 volume types. Verify the volume sizes are valid for volume types.
- **Criteria** – Represent multiple AWS Regions, with appropriate volume types. Correlate snapshot ages with volume ages.
- **Data structure** – Each finding should include the same columns.

The following is an example ruleset:

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

### Generate code with Amazon Bedrock

With your rules defined, you can now use Amazon Bedrock to generate Python code for creating synthetic Trusted Advisor findings.

The following is an example prompt for Amazon Bedrock:

```
Give me python code to create a 100 row pandas df with the following data:
<<Copy paste the ruleset from the above step>>
```

You can submit this prompt to the [Amazon Bedrock chat playground](https://docs.aws.amazon.com/bedrock/latest/userguide/playgrounds.html) using [Anthropic’s Claude 3.5 Sonnet](https://aws.amazon.com/bedrock/claude/) on Amazon Bedrock, and receive generated Python code. Review this code carefully, verifying it meets all specifications and generates realistic data. If necessary, iterate on your prompt or make manual adjustments to the code to address any missing logic or edge cases.

The resulting code will serve as the foundation for creating varied and realistic synthetic Trusted Advisor findings that adhere to the defined parameters. By using Amazon Bedrock in this way, you can quickly develop sophisticated data generation code that would otherwise require significant manual effort and domain expertise to create.

### Create data subsets

With the code generated by Amazon Bedrock and refined with your custom functions, you can now create diverse subsets of synthetic Trusted Advisor findings for the “Underutilized Amazon EBS Volumes” check. This approach allows you to simulate a wide range of real-world scenarios. In the following sample code, we have customized the volume_id and snapshot_id format to begin with vol-9999 and snap-9999, respectively:

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

This code creates subsets that include:

- Various volume types and instance types
- Different levels of utilization
- Occasional misconfigurations (for example, underutilized volumes)
- Diverse regional distribution

### Combine and scale the dataset

The process of combining and scaling synthetic data involves merging multiple generated datasets while introducing realistic anomalies to create a comprehensive and representative dataset. This step is crucial for making sure that your synthetic data reflects the complexity and variability found in real-world scenarios. Organizations typically introduce controlled anomalies at a specific rate (usually 5–10% of the dataset) to simulate various edge cases and unusual patterns that might occur in production environments. These anomalies help in testing system responses, developing monitoring solutions, and training ML models to identify potential issues.

When generating synthetic data for underutilized EBS volumes, you might introduce anomalies such as oversized volumes (5–10 times larger than needed), volumes with old snapshots (older than 365 days), or high-cost volumes with low utilization. For instance, a synthetic dataset might include a 1 TB gp2 volume that’s only using 100 GB of space, simulating a real-world scenario of overprovisioned resources. See the following code:

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

The following screenshot shows an example of sample rows generated.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-sample_rows.png)

### Validate the synthetic Trusted Advisor findings

Data validation is a critical step that verifies the quality, reliability, and representativeness of your synthetic data. This process involves performing rigorous statistical analysis to verify that the generated data maintains proper distributions, relationships, and patterns that align with real-world scenarios. Validation should include both quantitative metrics (statistical measures) and qualitative assessments (pattern analysis). Organizations should implement comprehensive validation frameworks that include distribution analysis, correlation checks, pattern verification, and anomaly detection. Regular visualization of the data helps in identifying inconsistencies or unexpected patterns.

For EBS volume data, validation might include analyzing the distribution of volume sizes across different types (gp2, gp3, io1), verifying that cost correlations match expected patterns, and making sure that introduced anomalies (like underutilized volumes) maintain realistic proportions. For instance, validating that the percentage of underutilized volumes aligns with typical enterprise environments (perhaps 15–20% of total volumes) and that the cost-to-size relationships remain realistic across volume types.

The following figures show examples of our validation checks.

- The following screenshot shows statistics of the generated synthetic datasets.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-statistics.png)
- The following figure shows the proportion of underutilized volumes in the generated synthetic datasets.
![underutilized volume proportion](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-underutilized_proportion.png)
- The following figure shows the distribution of volume sizes in the generated synthetic datasets.
![volume_size_distribution](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-volume_size_distribution.png)
- The following figure shows the distribution of volume types in the generated synthetic datasets.
![volume_type_distribution](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-volume_type_distribution.png)
- The following figure shows the distribution of snapshot ages in the generated synthetic datasets.
![snapshot_age](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-snapshot_age.png)

## Enhancing synthetic data with differential privacy

After exploring the steps to create synthetic datasets for the Trusted Advisor “Underutilized Amazon EBS Volumes” check, it’s worth revisiting how differential privacy strengthens this approach. When a cloud consulting firm analyzes aggregated Trusted Advisor data across multiple clients, differential privacy through [OpenDP](https://opendp.org/) provides the critical privacy-utility balance needed. By applying carefully calibrated noise to computations of underutilized volume statistics, consultants can generate synthetic datasets that preserve essential patterns across Regions and volume types while mathematically guaranteeing individual client confidentiality. This approach verifies that the synthetic data maintains sufficient accuracy for meaningful trend analysis and recommendations, while eliminating the risk of revealing sensitive client-specific infrastructure details or usage patterns—making it an ideal complement to our synthetic data generation pipeline.

## Conclusion

In this post, we showed how to use Amazon Bedrock to create synthetic data for enterprise needs. By combining language models available in Amazon Bedrock with industry knowledge, you can build a flexible and secure way to generate test data. This approach helps create realistic datasets without using sensitive information, saving time and money. It also facilitates consistent testing across projects and avoids ethical issues of using real user data. Overall, this strategy offers a solid solution for data challenges, supporting better testing and development practices.

In part 2 of this series, we will demonstrate how to use pattern recognition for different datasets to automate rule-set generation needed for the Amazon Bedrock prompts to generate corresponding synthetic data.

### About the authors

** [![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-devi-100x125.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-devi-100x125.png)Devi Nair** is a Technical Account Manager at Amazon Web Services, providing strategic guidance to enterprise customers as they build, operate, and optimize their workloads on AWS. She focuses on aligning cloud solutions with business objectives to drive long-term success and innovation.

** ![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-vishal-100x134.jpeg)Vishal Karlupia** is a Senior Technical Account Manager/Lead at Amazon Web Services, Toronto. He specializes in generative AI applications and helps customers build and scale their AI/ML workloads on AWS. Outside of work, he enjoys being outdoors and keeping bonfires alive.

** ![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-srini.jpg)Srinivas Ganapathi** is a Principal Technical Account Manager at Amazon Web Services. He is based in Toronto, Canada, and works with games customers to run efficient workloads on AWS.

** ![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-17470-nic-100x133.jpg)Nicolas Simard** is a Technical Account Manager based in Montreal. He helps organizations accelerate their AI adoption journey through technical expertise, architectural best practices, and enables them to maximize business value from AWS’s Generative AI capabilities.
