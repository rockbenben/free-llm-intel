---
vendor: aws_bedrock
title: How BQA streamlines education quality reporting using Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-bqa-streamlines-education-quality-reporting-using-amazon-bedrock
date: 2025-01-13
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: f2081406b7a3
---

# How BQA streamlines education quality reporting using Amazon Bedrock

Given the value of data today, organizations across various industries are working with vast amounts of data across multiple formats. Manually reviewing and processing this information can be a challenging and time-consuming task, with a margin for potential errors. This is where intelligent document processing (IDP), coupled with the power of [generative AI](https://aws.amazon.com/generative-ai/), emerges as a game-changing solution.

Enhancing the capabilities of IDP is the integration of generative AI, which harnesses large language models (LLMs) and generative techniques to understand and generate human-like text. This integration allows organizations to not only extract data from documents, but to also interpret, summarize, and generate insights from the extracted information, enabling more intelligent and automated document processing workflows.

The [Education and Training Quality Authority (BQA)](https://www.bqa.gov.bh/en/pages/home.aspx) plays a critical role in improving the quality of education and training services in the Kingdom Bahrain. BQA reviews the performance of all education and training institutions, including schools, universities, and vocational institutes, thereby promoting the professional advancement of the nation’s human capital.

BQA oversees a comprehensive quality assurance process, which includes setting performance standards and conducting objective reviews of education and training institutions. The process involves the collection and analysis of extensive documentation, including self-evaluation reports (SERs), supporting evidence, and various media formats from the institutions being reviewed.

The collaboration between BQA and AWS was facilitated through the [Cloud Innovation Center](https://aws.amazon.com/government-education/cloud-innovation-centers/) (CIC) program, a joint initiative by AWS, [Tamkeen](https://www.tamkeen.bh/en/), and leading universities in Bahrain, including [Bahrain Polytechnic](https://cic.polytechnic.bh/) and [University of Bahrain](https://cic.uob.edu.bh/). The CIC program aims to foster innovation within the public sector by providing a collaborative environment where government entities can work closely with AWS consultants and university students to develop cutting-edge solutions using the latest cloud technologies.

As part of the CIC program, BQA has built a proof of concept solution, harnessing the power of AWS services and generative AI capabilities. The primary purpose of this proof of concept was to test and validate the proposed technologies, demonstrating their viability and potential for streamlining BQA’s reporting and data management processes.

In this post, we explore how BQA used the power of [Amazon Bedrock](https://aws.amazon.com/bedrock/?gclid=Cj0KCQjwwuG1BhCnARIsAFWBUC03_InmY_quI5NznbN0QZdSz2CSo13J-rH0N48_ALkNHbrvfRG25m4aArV6EALw_wcB&trk=a9c05117-53bb-40a3-89b2-a3ee2d23e7d2&sc_channel=ps&ef_id=Cj0KCQjwwuG1BhCnARIsAFWBUC03_InmY_quI5NznbN0QZdSz2CSo13J-rH0N48_ALkNHbrvfRG25m4aArV6EALw_wcB:G:s&s_kwcid=AL!4422!3!691967569326!e!!g!!amazon%20bedrock!21054971690!157173594137), [Amazon SageMaker JumpStart](https://aws.amazon.com/sagemaker/jumpstart/), and other AWS services to streamline the overall reporting workflow.

## The challenge: Streamlining self-assessment reporting

BQA has traditionally provided education and training institutions with a template for the SER as part of the review process. Institutions are required to submit a review portfolio containing the completed SER and supporting material as evidence, which sometimes did not adhere fully to the established reporting standards.

The existing process had some challenges:

- **Inaccurate or incomplete submissions** – Institutions might provide incomplete or inaccurate information in the submitted reports and supporting evidence, leading to gaps in the data required for a comprehensive review.
- **Missing or insufficient supporting evidence **– The supporting material provided as evidence by institutions frequently did not substantiate the claims made in their reports, which challenged the evaluation process.
- **Time-consuming and resource-intensive **– The process required dedicating significant time and resources to review the submissions manually and follow up with institutions to request additional information if needed to rectify the submissions, resulting in slowing down the overall review process.

These challenges highlighted the need for a more streamlined and efficient approach to the submission and review process.

## Solution overview

The proposed solution uses Amazon Bedrock and the Amazon Titan Express model to enable IDP functionalities. The architecture seamlessly integrates multiple AWS services with Amazon Bedrock, allowing for efficient data extraction and comparison.

Amazon Bedrock is a fully managed service that provides access to high-performing [foundation models](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) (FMs) from leading AI startups and Amazon through a unified API. It offers a wide range of FMs, allowing you to choose the model that best suits your specific use case.

The following diagram illustrates the solution architecture.

![solution architecture diagram](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/10/ml-17266-arch-diag-2.jpg)

The solution consists of the following steps:

- Relevant documents are uploaded and stored in an [Amazon Simple Storage Service](https://aws.amazon.com/pm/serv-s3/?gclid=Cj0KCQjwwuG1BhCnARIsAFWBUC3J-Yduiyiq9oLppu44jUYJ1XG0W8lLG6z69mWHML3hlur_Zdo9LO0aAgyuEALw_wcB&trk=518a7bef-5b4f-4462-ad55-80e5c177f12b&sc_channel=ps&ef_id=Cj0KCQjwwuG1BhCnARIsAFWBUC3J-Yduiyiq9oLppu44jUYJ1XG0W8lLG6z69mWHML3hlur_Zdo9LO0aAgyuEALw_wcB:G:s&s_kwcid=AL!4422!3!645186213484!e!!g!!amazon%20s3!19579892800!143689755565) (Amazon S3) bucket.
- An event notification is sent to an [Amazon Simple Queue Service](https://aws.amazon.com/sqs/) (Amazon SQS) queue to align each file for further processing. Amazon SQS serves as a buffer, enabling the different components to send and receive messages in a reliable manner without being directly coupled, enhancing scalability and fault tolerance of the system.
- The text extraction [AWS Lambda](https://aws.amazon.com/lambda/) function is invoked by the SQS queue, processing each queued file and using [Amazon Textract](https://aws.amazon.com/textract/) to extract text from the documents.
- The extracted text data is placed into another SQS queue for the next processing step.
- The text summarization Lambda function is invoked by this new queue containing the extracted text. This function sends a request to SageMaker JumpStart, where a Meta Llama text generation model is deployed to summarize the content based on the provided prompt.
- In parallel, the InvokeSageMaker Lambda function is invoked to perform comparisons and assessments. It compares the extracted text against the BQA standards that the model was trained on, evaluating the text for compliance, quality, and other relevant metrics.
- The summarized data and assessment results are stored in an [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) table
- Upon request, the InvokeBedrock Lambda function invokes Amazon Bedrock to generate generative AI summaries and comments. The function constructs a detailed prompt designed to guide the [Amazon Titan Express model](https://aws.amazon.com/bedrock/amazon-models/titan/) in evaluating the university’s submission.

## Prompt engineering using Amazon Bedrock

To take advantage of the power of Amazon Bedrock and make sure the generated output adhered to the desired structure and formatting requirements, a carefully crafted prompt was developed according to the following guidelines:

- **Evidence submission** – Present the evidence submitted by the institution under the relevant indicator, providing the model with the necessary context for evaluation
- **Evaluation criteria **– Outline the specific criteria the evidence should be assessed against
- **Evaluation instructions** – Instruct the model as follows:  Indicate N/A if the evidence is irrelevant to the indicator Evaluate the university’s self-assessment based on the criteria Assign a score from 1–5 for each comment, citing evidence directly from the content
- **Response format **– Specify the response as bullet points, focusing on relevant analysis and evidence, with a word limit of 100 words

To use this prompt template, you can create a custom Lambda function with your project. The function should handle the retrieval of the required data, such as the indicator name, the university’s submitted evidence, and the rubric criteria. Within the function, include the prompt template and dynamically populate the placeholders `(${indicatorName}, ${JSON.stringify(allContent)}`, and `${JSON.stringify(c.comment)})` with the retrieved data.

The Amazon Titan Text Express model will then generate the evaluation response based on the provided prompt instructions, adhering to the specified format and guidelines. You can process and analyze the model’s response within your function, extracting the compliance score, relevant analysis, and evidence.

The following is an example prompt template:

```
for (const c of comments) {
        const prompt = `
        Below is the evidence submitted by the university under the indicator "${indicatorName}":
        ${JSON.stringify(allContent)}
    
         Analyze and Evaluate the university's eviedence based on the provided rubric criteria:
        ${JSON.stringify(c.comment)}

        - If the evidence does not relate to the indicator, indicate that it is not applicable (N/A) without any additional commentary.
        
       Choose one from the below compliance score based on evidence submitted:
       1. Non-compliant: The comment does not meet the criteria or standards.
        2.Compliant with recommendation: The comment meets the criteria but includes a suggestion or recommendation for improvement.
        3. Compliant: The comment meets the criteria or standards.

        THE END OF THE RESPONSE THERE SHOULD BE EITHER SCORE: [SCORE: COMPLIANT OR NON-COMPLIANT OR COMPLIANT WITH RECOMMENDATION]
        Write your response in concise bullet points, focusing strictly on relevant analysis and evidence.
        **LIMIT YOUR RESPONSE TO 100 WORDS ONLY.**

        `;

        logger.info(`Prompt for comment ${c.commentId}: ${prompt}`);

        const body = JSON.stringify({
          inputText: prompt,
          textGenerationConfig: {
            maxTokenCount: 4096,
            stopSequences: [],
            temperature: 0,
            topP: 0.1,
          },
        });
```

The following screenshot shows an example of the Amazon Bedrock generated response.

![Amazon Bedrock generated response](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/10/ml-17266-bedrock-response.png)

## Results

The implementation of Amazon Bedrock enabled institutions with transformative benefits. By automating and streamlining the collection and analysis of extensive documentation, including SERs, supporting evidence, and various media formats, institutions can achieve greater accuracy and consistency in their reporting processes and readiness for the review process. This not only reduces the time and cost associated with manual data processing, but also improves compliance with the quality expectations, thereby enhancing the credibility and quality of their institutions.

For BQA the implementation helped in achieving one of its strategic objectives focused on streamlining their reporting processes and achieve significant improvements across a range of critical metrics, substantially enhancing the overall efficiency and effectiveness of their operations.

Key success metrics anticipated include:

- Faster turnaround times for generating 70% accurate and standards-compliant self-evaluation reports, leading to improved overall efficiency.
- Reduced risk of errors or non-compliance in the reporting process, enforcing adherence to established guidelines.
- Ability to summarize lengthy submissions into concise bullet points, allowing BQA reviewers to quickly analyze and comprehend the most pertinent information, reducing evidence analysis time by 30%.
- More accurate compliance feedback functionality, empowering reviewers to effectively evaluate submissions against established standards and guidelines, while achieving 30% reduced operational costs through process optimizations.
- Enhanced transparency and communication through seamless interactions, enabling users to request additional documents or clarifications with ease.
- Real-time feedback, allowing institutions to make necessary adjustments promptly. This is particularly useful to maintain submission accuracy and completeness.
- Enhanced decision-making by providing insights on the data. This helps universities identify areas for improvement and make data-driven decisions to enhance their processes and operations.

The following screenshot shows an example generating new evaluations using Amazon Bedrock

![generating new evaluations using Amazon Bedrock](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/10/ml-17266-generate-comments.png)

## Conclusion

This post outlined the implementation of Amazon Bedrock at the Education and Training Quality Authority (BQA), demonstrating the transformative potential of generative AI in revolutionizing the quality assurance processes in the education and training sectors. For those interested in exploring the technical details further, the full code for this implementation is available in the following [GitHub repo](https://github.com/bahrain-bp/bqa-genai-challenge/tree/main). If you are interested in conducting a similar proof of concept with us, submit your challenge idea to the [Bahrain Polytechnic](https://cic.polytechnic.bh/) or [University of Bahrain](https://cic.uob.edu.bh/uob-cic-challenge-submission-form/) CIC website.

### About the Author

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/11/ml-17266-headshot-1.jpg)Maram AlSaegh** is a Cloud Infrastructure Architect at Amazon Web Services (AWS), where she supports AWS customers in accelerating their journey to cloud. Currently, she is focused on developing innovative solutions that leverage generative AI and machine learning (ML) for public sector entities.
