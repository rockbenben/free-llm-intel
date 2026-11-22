---
vendor: aws_bedrock
title: AI meets HR: Transforming talent acquisition with Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/ai-meets-hr-transforming-talent-acquisition-with-amazon-bedrock
date: 2026-02-12
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 84d9dd5e8012
---

# AI meets HR: Transforming talent acquisition with Amazon Bedrock

Organizations face significant challenges in making their recruitment processes more efficient while maintaining fair hiring practices. By using AI to transform their recruitment and talent acquisition processes, organizations can overcome these challenges. AWS offers a suite of[ AI services](https://aws.amazon.com/ai/?ams%23interactive-card-vertical%23pattern-data--1593418038.filter=%257B%2522filters%2522%253A%255B%255D%257D) that can be used to significantly enhance the efficiency, effectiveness, and fairness of hiring practices. With AWS AI services, specifically [Amazon Bedrock](https://aws.amazon.com/bedrock/), you can build an efficient and scalable recruitment system that streamlines hiring processes, helping human reviewers focus on the interview and assessment of candidates.

In this post, we show how to create an AI-powered recruitment system using Amazon Bedrock, [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/), [AWS Lambda](https://aws.amazon.com/lambda), and other AWS services to enhance job description creation, candidate communication, and interview preparation while maintaining human oversight.

## The AI-powered recruitment lifecycle

The recruitment process presents numerous opportunities for AI enhancement through specialized [agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html), each powered by Amazon Bedrock and connected to dedicated Amazon Bedrock knowledge bases. Let’s explore how these agents work together across key stages of the recruitment lifecycle.

### Job description creation and optimization

Creating inclusive and attractive job descriptions is crucial for attracting diverse talent pools. The Job Description Creation and Optimization Agent uses advanced language models available in Amazon Bedrock and connects to an Amazon Bedrock knowledge base containing your organization’s historical job descriptions and inclusion guidelines.

Deploy the Job Description Agent with a secure [Amazon Virtual Private Cloud](https://aws.amazon.com/vpc) (Amazon VPC) configuration and [AWS Identity and Access Management](https://aws.amazon.com/iam/) (IAM) [roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html). The agent references your knowledge base to optimize job postings while maintaining compliance with organizational standards and inclusive language requirements.

### Candidate communication management

The Candidate Communication Agent manages candidate interactions through the following components:

- Lambda functions that trigger communications based on workflow stages
- [Amazon Simple Notification Service](https://aws.amazon.com/sns) (Amazon SNS) for secure email and text delivery
- Integration with approval workflows for regulated communications
- Automated status updates based on candidate progression

Configure the Communication Agent with proper VPC endpoints and encryption for all data in transit and at rest. Use [Amazon CloudWatch](https://aws.amazon.com/cloudwatch) monitoring to track communication effectiveness and response rates.

### Interview preparation and feedback

The Interview Prep Agent supports the interview process by:

- Accessing a knowledge base containing interview questions, SOPs, and best practices
- Generating contextual interview materials based on role requirements
- Analyzing interviewer feedback and notes using Amazon Bedrock to identify key sentiments and consistent themes across evaluations
- Maintaining compliance with interview standards stored in the knowledge base

Although the agent provides interview structure and guidance, interviewers maintain full control over the conversation and evaluation process.

## Solution overview

The architecture brings together the recruitment agents and AWS services into a comprehensive recruitment system that enhances and streamlines the hiring process.The following diagram shows how three specialized AI agents work together to manage different aspects of the recruitment process, from job posting creation through summarizing interview feedback. Each agent uses Amazon Bedrock and connects to dedicated Amazon Bedrock knowledge bases while maintaining security and compliance requirements.

## ![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/26/image-1-2.jpg)

The solution consists of three main components working together to improve the recruitment process:

- **Job Description Creation and Optimization Agent** – The Job Description Creation and Optimization Agent uses the AI capabilities of Amazon Bedrock to create and refine job postings, connecting directly to an Amazon Bedrock knowledge base that contains example descriptions and best practices for inclusive language.
- **Candidate Communication Agent **– For candidate communications, the dedicated agent streamlines interactions through an automated system. It uses Lambda functions to manage communication workflows and Amazon SNS for reliable message delivery. The agent maintains direct connections with candidates while making sure communications follow approved templates and procedures.
- **Interview Prep Agent **– The Interview Prep Agent serves as a comprehensive resource for interviewers, providing guidance on interview formats and questions while helping structure, summarize, and analyze feedback. It maintains access to a detailed knowledge base of interview standards and uses the natural language processing capabilities of Amazon Bedrock to analyze interview feedback patterns and themes, helping maintain consistent evaluation practices across hiring teams.

## Prerequisites

Before implementing this AI-powered recruitment system, make sure you have the following:

- AWS account and access:  An AWS account with administrator access Access to Amazon Bedrock [foundation models](https://docs.aws.amazon.com/bedrock/latest/userguide/foundation-models-reference.html) (FMs) Permissions to create and manage IAM roles and policies
- AWS services required:  [Amazon API Gateway](https://aws.amazon.com/api-gateway) Amazon Bedrock with access to FMs Amazon Bedrock Knowledge Bases Amazon CloudWatch [AWS Key Management Service](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html) (AWS KMS) AWS Lambda Amazon SNS [Amazon Simple Storage Service](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html) (Amazon S3) for knowledge base storage Amazon VPC
- Technical requirements:  Basic knowledge of Python 3.9 or later (for Lambda functions) Network access to configure VPC endpoints
- Security and compliance:  Understanding of AWS security best practices SSL/TLS certificates for secure communications Compliance approval from your organization’s security team

In the following sections, we examine the key components that make up our AI-powered recruitment system. Each piece plays a crucial role in creating a secure, scalable, and effective solution. We start with the infrastructure definition and work our way through the deployment, knowledge base integration, core AI agents, and testing tools.

## Infrastructure as code

The following [AWS CloudFormation](https://aws.amazon.com/cloudformation) template defines the complete AWS infrastructure, including VPC configuration, security groups, Lambda functions, API Gateway, and knowledge bases. It facilities secure, scalable deployment with proper IAM roles and encryption.

```
AWSTemplateFormatVersion: '2010-09-09'
Description: 'AI-Powered Recruitment System with Security and Knowledge Bases'

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, prod]

Resources:
  # KMS Key for encryption
  RecruitmentKMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: "Encryption key for recruitment system"
      KeyPolicy:
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'

  RecruitmentKMSAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: !Sub 'alias/recruitment-${Environment}'
      TargetKeyId: !Ref RecruitmentKMSKey

  # VPC Configuration
  RecruitmentVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub 'recruitment-vpc-${Environment}'

  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref RecruitmentVPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
 
 PrivateSubnetRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref RecruitmentVPC
      Tags:
        - Key: Name
          Value: !Sub 'recruitment-private-rt-\${Environment}'
 
 PrivateSubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet
      RouteTableId: !Ref PrivateSubnetRouteTable
 
# Example Interface Endpoints
VPCEBedrockRuntime:
  Type: AWS::EC2::VPCEndpoint
  Properties:
    VpcId: !Ref RecruitmentVPC
    ServiceName: !Sub 'com.amazonaws.${AWS::Region}.bedrock-runtime'
    VpcEndpointType: Interface
    SubnetIds: [ !Ref PrivateSubnet ]
    SecurityGroupIds: [ !Ref LambdaSecurityGroup ]

VPCEBedrockAgent:
  Type: AWS::EC2::VPCEndpoint
  Properties:
    VpcId: !Ref RecruitmentVPC
    ServiceName: !Sub 'com.amazonaws.${AWS::Region}.bedrock-agent'
    VpcEndpointType: Interface
    SubnetIds: [ !Ref PrivateSubnet ]
    SecurityGroupIds: [ !Ref LambdaSecurityGroup ]

VPCESNS:
  Type: AWS::EC2::VPCEndpoint
  Properties:
    VpcId: !Ref RecruitmentVPC
    ServiceName: !Sub 'com.amazonaws.${AWS::Region}.sns'
    VpcEndpointType: Interface
    SubnetIds: [ !Ref PrivateSubnet ]
    SecurityGroupIds: [ !Ref LambdaSecurityGroup ]

# Gateway endpoints for S3 (and DynamoDB if you add it later)
VPCES3:
  Type: AWS::EC2::VPCEndpoint
  Properties:
    VpcId: !Ref RecruitmentVPC
    ServiceName: !Sub 'com.amazonaws.${AWS::Region}.s3'
    VpcEndpointType: Gateway
    RouteTableIds:
      - !Ref PrivateSubnetRouteTable   # create if not present
  # Security Group
  LambdaSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for recruitment AWS Lambda functions
      VpcId: !Ref RecruitmentVPC
      SecurityGroupEgress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0

  # KnowledgeBase IAM role
  KnowledgeBaseRole:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal: { Service: bedrock.amazonaws.com }
          Action: sts:AssumeRole
    Policies:
      - PolicyName: BedrockKBAccess
        PolicyDocument:
          Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - bedrock:Retrieve
                - bedrock:RetrieveAndGenerate
              Resource: "*"
            - Effect: Allow
              Action:
                - s3:GetObject
                - s3:ListBucket
              Resource: "*"   # scope to your KB bucket(s) in real deployments

    JobDescriptionKnowledgeBase:
        Type: AWS::Bedrock::KnowledgeBase
        Properties:
            Name: !Sub 'job-descriptions-${Environment}'
            RoleArn: !GetAtt KnowledgeBaseRole.Arn
            KnowledgeBaseConfiguration:
                Type: VECTOR
                VectorKnowledgeBaseConfiguration:
                    EmbeddingModelArn: !Sub 'arn:aws:bedrock:\${AWS::Region}::foundation-model/amazon.titan-embed-text-v1'
            StorageConfiguration:
                Type: S3
                S3Configuration:
                    BucketArn: !Sub 'arn:aws:s3:::your-kb-bucket-${Environment}-${AWS::AccountId}-${AWS::Region}'
                    BucketOwnerAccountId: !Ref AWS::AccountId

    InterviewKnowledgeBase:
        Type: AWS::Bedrock::KnowledgeBase
        Properties:
            Name: !Sub 'interview-standards-${Environment}'
            RoleArn: !GetAtt KnowledgeBaseRole.Arn
            KnowledgeBaseConfiguration:
                Type: VECTOR
                VectorKnowledgeBaseConfiguration:
                   EmbeddingModelArn: arn:aws:bedrock:${AWS::Region}::foundation-model/amazon.titan-embed-text-v2:0
            StorageConfiguration:
                Type: S3
                S3Configuration:
                    BucketArn: !Sub 'arn:aws:s3:::your-kb-bucket-${Environment}-${AWS::AccountId}-${AWS::Region}'
                    BucketOwnerAccountId: !Ref AWS::AccountId

  # CloudTrail for audit logging
  RecruitmentCloudTrail:
    Type: AWS::CloudTrail::Trail
    Properties:
      TrailName: !Sub 'recruitment-audit-${Environment}'
      S3BucketName: !Ref AuditLogsBucket
      IncludeGlobalServiceEvents: true
      IsMultiRegionTrail: true
      EnableLogFileValidation: true
      KMSKeyId: !Ref RecruitmentKMSKey

  AuditLogsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'recruitment-audit-logs-${Environment}-${AWS::AccountId}-${AWS::Region}'
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: aws:kms
              KMSMasterKeyID: !Ref RecruitmentKMSKey
  # IAM Role for AWS Lambda functions
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: BedrockAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - bedrock:InvokeModel
                  - bedrock:Retrieve
                Resource: '*'
              - Effect: Allow
                Action:
                  - sns:Publish
                Resource: !Ref CommunicationTopic
              - Effect: Allow
                Action:
                  - kms:Decrypt
                  - kms:GenerateDataKey
                Resource: !GetAtt RecruitmentKMSKey.Arn
              - Effect: Allow
                Action:
                  - aoss:APIAccessAll
                Resource: '*'

  # SNS Topic for notifications
  CommunicationTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub 'recruitment-notifications-${Environment}'

  # AWS Lambda Functions
  JobDescriptionFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub 'recruitment-job-description-${Environment}'
      Runtime: python3.11
      Handler: job_description_agent.lambda_handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Code:
        ZipFile: |
          # Code will be deployed separately
          def lambda_handler(event, context):
              return {'statusCode': 200, 'body': 'Placeholder'}
      Timeout: 60

  CommunicationFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub 'recruitment-communication-${Environment}'
      Runtime: python3.11
      Handler: communication_agent.lambda_handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Code:
        ZipFile: |
          def lambda_handler(event, context):
              return {'statusCode': 200, 'body': 'Placeholder'}
      Timeout: 60
      Environment:
        Variables:
          SNS_TOPIC_ARN: !Ref CommunicationTopic
          KMS_KEY_ID: !Ref RecruitmentKMSKey
      VpcConfig:
        SecurityGroupIds:
          - !Ref LambdaSecurityGroup
        SubnetIds:
          - !Ref PrivateSubnet

  InterviewFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub 'recruitment-interview-${Environment}'
      Runtime: python3.11
      Handler: interview_agent.lambda_handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Code:
        ZipFile: |
          def lambda_handler(event, context):
              return {'statusCode': 200, 'body': 'Placeholder'}
      Timeout: 60

  # API Gateway
  RecruitmentAPI:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: !Sub 'recruitment-api-${Environment}'
      Description: 'API for AI-Powered Recruitment System'

  # API Gateway Resources and Methods
  JobDescriptionResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref RecruitmentAPI
      ParentId: !GetAtt RecruitmentAPI.RootResourceId
      PathPart: job-description

  JobDescriptionMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref RecruitmentAPI
      ResourceId: !Ref JobDescriptionResource
      HttpMethod: POST
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${JobDescriptionFunction.Arn}/invocations'

  CommunicationResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref RecruitmentAPI
      ParentId: !GetAtt RecruitmentAPI.RootResourceId
      PathPart: communication

  CommunicationMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref RecruitmentAPI
      ResourceId: !Ref CommunicationResource
      HttpMethod: POST
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${CommunicationFunction.Arn}/invocations'

  InterviewResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref RecruitmentAPI
      ParentId: !GetAtt RecruitmentAPI.RootResourceId
      PathPart: interview

  InterviewMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref RecruitmentAPI
      ResourceId: !Ref InterviewResource
      HttpMethod: POST
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${InterviewFunction.Arn}/invocations'

  # Lambda Permissions
  JobDescriptionPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref JobDescriptionFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub '${RecruitmentAPI}/*/POST/job-description'

  CommunicationPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref CommunicationFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub '${RecruitmentAPI}/*/POST/communication'
      
  InterviewPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref InterviewFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub '${RecruitmentAPI}/*/POST/interview'
      
  # API Deployment
  APIDeployment:
  Type: AWS::ApiGateway::Deployment
  DependsOn:
    - JobDescriptionMethod
    - CommunicationMethod
    - InterviewMethod
    - JobDescriptionPermission
    - CommunicationPermission
    - InterviewPermission
  Properties:
    RestApiId: !Ref RecruitmentAPI
    StageName: !Ref Environment
 
Outputs:
  APIEndpoint:
    Description: 'API Gateway endpoint URL'
    Value: !Sub 'https://${RecruitmentAPI}.execute-api.${AWS::Region}.amazonaws.com/${Environment}'
  
  SNSTopicArn:
    Description: 'SNS Topic ARN for notifications'
    Value: !Ref CommunicationTopic
```

## Deployment automation

The following automation script handles deployment of the recruitment system infrastructure and Lambda functions. It manages CloudFormation stack creation and updates and Lambda function code updates, making system deployment and updates streamlined and consistent.

```
#!/usr/bin/env python3
"""
Deployment script for Basic Recruitment System
"""

import boto3
import zipfile
import os
import json
from pathlib import Path

class BasicRecruitmentDeployment:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.cf_client = boto3.client('cloudformation', region_name=region)
    
    def create_lambda_zip(self, function_name):
        """Create deployment zip for Lambda function"""
        zip_path = f"/tmp/{function_name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            zip_file.write(f"lambda_functions/{function_name}.py", f"{function_name}.py")
        
        return zip_path
    
    def update_lambda_function(self, function_name, environment='dev'):
        """Update Lambda function code"""
        zip_path = self.create_lambda_zip(function_name)
        
        try:
            with open(zip_path, 'rb') as zip_file:
                response = self.lambda_client.update_function_code(
                    FunctionName=f'recruitment-{function_name.replace("_agent", "")}-{environment}',
                    ZipFile=zip_file.read()
                )
            print(f"Updated {function_name}: {response['LastModified']}")
            return response
        except Exception as e:
            print(f"Error updating {function_name}: {e}")
            return None
        finally:
            os.remove(zip_path)
    
    def deploy_infrastructure(self, environment='dev'):
        """Deploy CloudFormation stack"""
        stack_name = f'recruitment-system-{environment}'
        
        with open('infrastructure/cloudformation.yaml', 'r') as template_file:
            template_body = template_file.read()
        
        try:
            response = self.cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {'ParameterKey': 'Environment', 'ParameterValue': environment}
                ],
                Capabilities=['CAPABILITY_IAM']
            )
            print(f"Created stack: {stack_name}")
            return response
        except self.cf_client.exceptions.AlreadyExistsException:
            response = self.cf_client.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {'ParameterKey': 'Environment', 'ParameterValue': environment}
                ],
                Capabilities=['CAPABILITY_IAM']
            )
            print(f"Updated stack: {stack_name}")
            return response
        except Exception as e:
            print(f"Error with stack: {e}")
            return None
    
    def deploy_all(self, environment='dev'):
        """Deploy complete system"""
        print(f"Deploying recruitment system to {environment}")
        
        # Deploy infrastructure
        self.deploy_infrastructure(environment)
        
        # Wait for stack to be ready (simplified)
        print("Waiting for infrastructure...")
        
        # Update AWS Lambda functions
        functions = [
            'job_description_agent',
            'communication_agent',
            'interview_agent'
        ]
        
        for func in functions:
            self.update_lambda_function(func, environment)
        
        print("Deployment complete!")

def main():
    deployment = BasicRecruitmentDeployment()
    
    print("Basic Recruitment System Deployment")
    print("1. Deploys CloudFormation stack with AWS Lambda functions and API Gateway")
    print("2. Updates Lambda function code")
    print("3. Sets up SNS for notifications")
    
    # Example deployment
    # deployment.deploy_all('dev')

if __name__ == "__main__":
    main()
```

## Knowledge base integration

The central knowledge base manager interfaces with Amazon Bedrock knowledge base collections to provide best practices, templates, and standards to the recruitment agents. It enables AI agents to make informed decisions based on organizational knowledge.

```
import boto3
import json

class KnowledgeBaseManager:
    def __init__(self):
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        self.bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

    def query_knowledge_base(self, kb_id: str, query: str):
        try:
            response = self.bedrock_agent_runtime.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={'text': query}
                # optionally add retrievalConfiguration={...}
            )
            return [r['content']['text'] for r in response.get('retrievalResults', [])]
        except Exception as e:
            return [f"Knowledge Base query failed: {str(e)}"]

# Knowledge base IDs (to be created via CloudFormation)
KNOWLEDGE_BASES = {
    'job_descriptions': 'JOB_DESC_KB_ID', 
    'interview_standards': 'INTERVIEW_KB_ID',
    'communication_templates': 'COMM_KB_ID'
}
```

To improve Retrieval Augmented Generation (RAG) quality, start by tuning your Amazon Bedrock knowledge bases. Adjust chunk sizes and overlap for your documents, experiment with different embedding models, and enable reranking to promote the most relevant passages. For each agent, you can also choose different foundation models. For example, use a fast model such as Anthropic’s Claude 3 Haiku for high-volume job description and communication tasks, and a more capable model such as Anthropic’s Claude 3 Sonnet or another reasoning-optimized model for the Interview Prep Agent, where deeper analysis is required. Capture these experiments as part of your continuous improvement process so you can standardize on the best-performing configurations.

## The core AI agents

The integration between the three agents is handled through API Gateway and Lambda, with each agent exposed through its own endpoint. The system uses three specialized AI agents.

### Job Description Agent

This agent is the first step in the recruitment pipeline. It uses Amazon Bedrock to create inclusive and effective job descriptions by combining requirements with best practices from the knowledge base.

```
import json
import boto3
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from knowledge_bases import KnowledgeBaseManager, KNOWLEDGE_BASES

bedrock = boto3.client('bedrock-runtime')
kb_manager = KnowledgeBaseManager()

def lambda_handler(event, context):
    """Job Description Agent Lambda function"""
    
    body = json.loads(event.get('body', '{}'))
    
    role_title = body.get('role_title', '')
    requirements = body.get('requirements', [])
    company_info = body.get('company_info', {})
    
    # Query knowledge base for best practices
    kb_context = kb_manager.query_knowledge_base(
        KNOWLEDGE_BASES['job_descriptions'],
        f"inclusive job description examples for {role_title}"
    )
    
    prompt = f"""Create an inclusive job description for: {role_title}
    
Requirements: {', '.join(requirements)}
Company: {company_info.get('name', 'Our Company')}
Culture: {company_info.get('culture', 'collaborative')}
Remote: {company_info.get('remote', False)}

Best practices from knowledge base:
{' '.join(kb_context[:2])}

Include: role summary, key responsibilities, qualifications, benefits.
Ensure inclusive language and avoid unnecessary barriers."""
    
    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'job_description': result['content'][0]['text'],
                'role_title': role_title,
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### Communication Agent

This agent manages candidate communications throughout the recruitment process. It integrates with Amazon SNS for notifications and provides professional, consistent messaging using approved templates.

```
import json
import boto3
from datetime import datetime

bedrock = boto3.client('bedrock-runtime')
sns = boto3.client('sns')

def lambda_handler(event, context):
    """Communication Agent Lambda function"""
    
    body = json.loads(event.get('body', '{}'))
    
    message_type = body.get('message_type', '')
    candidate_info = body.get('candidate_info', {})
    stage = body.get('stage', '')
    
    prompt = f"""Generate {message_type} for candidate {candidate_info.get('name', 'Candidate')} 
at {stage} stage.

Message should be:
- Professional and empathetic
- Clear about next steps
- Appropriate for the stage
- Include timeline if relevant

Types: application_received, interview_invitation, rejection, offer"""
    
    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        communication = result['content'][0]['text']
        
        # Send notification via SNS if topic ARN provided
        topic_arn = body.get('sns_topic_arn')
        if topic_arn:
            sns.publish(
                TopicArn=topic_arn,
                Message=communication,
                Subject=f"Recruitment Update - {message_type}"
            )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'communication': communication,
                'type': message_type,
                'stage': stage,
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### Interview Prep Agent

This agent prepares tailored interview materials and questions based on the role and candidate background. It helps maintain consistent interview standards while adapting to specific positions.

```
import json
import boto3
from datetime import datetime

bedrock = boto3.client('bedrock-runtime')

def lambda_handler(event, context):
    """Interview Prep Agent Lambda function"""
    
    body = json.loads(event.get('body', '{}'))
    
    role_info = body.get('role_info', {})
    candidate_background = body.get('candidate_background', {})
    
    prompt = f"""Prepare interview for:
Role: {role_info.get('title', 'Position')}
Level: {role_info.get('level', 'Mid-level')}
Key Skills: {role_info.get('key_skills', [])}

Candidate Background:
Experience: {candidate_background.get('experience', 'Not specified')}
Skills: {candidate_background.get('skills', [])}

Generate:
1. 5-7 technical questions
2. 3-4 behavioral questions  
3. Evaluation criteria
4. Red flags to watch for"""
    
    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'interview_prep': result['content'][0]['text'],
                'role': role_info.get('title'),
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

## Testing and verification

The following test client demonstrates interaction with the recruitment system API. It provides example usage of major functions and helps verify system functionality.

```
#!/usr/bin/env python3
"""
Test client for Basic Recruitment System API
"""

import requests
import json

class RecruitmentClient:
    def __init__(self, api_endpoint):
        self.api_endpoint = api_endpoint.rstrip('/')
    
    def create_job_description(self, role_title, requirements, company_info):
        """Test job description creation"""
        url = f"{self.api_endpoint}/job-description"
        payload = {
            "role_title": role_title,
            "requirements": requirements,
            "company_info": company_info
        }
        
        response = requests.post(url, json=payload)
        return response.json()
   
    def send_communication(self, message_type, candidate_info, stage):
        """Test communication sending"""
        url = f"{self.api_endpoint}/communication"
        payload = {
            "message_type": message_type,
            "candidate_info": candidate_info,
            "stage": stage
        }
        
        response = requests.post(url, json=payload)
        return response.json()

    def prepare_interview(self, role_info, candidate_background):
        """Test interview preparation"""
        url = f"{self.api_endpoint}/interview"
        payload = {
            "role_info": role_info,
            "candidate_background": candidate_background
        }
        
        response = requests.post(url, json=payload)
        return response.json()

def main():
    # Replace with your actual API endpoint
    api_endpoint = "https://your-api-id.execute-api.us-east-1.amazonaws.com/dev"
    client = RecruitmentClient(api_endpoint)
    
    print("Testing Basic Recruitment System")
    
    # Test job description
    print("\n1. Testing Job Description Creation:")
    job_result = client.create_job_description(
        role_title="Senior Software Engineer",
        requirements=["5+ years Python", "AWS experience", "Team leadership"],
        company_info={"name": "TechCorp", "culture": "collaborative", "remote": True}
    )
    print(json.dumps(job_result, indent=2))
    
    # Test communication
    print("\n2. Testing Communication:")
    comm_result = client.send_communication(
        message_type="interview_invitation",
        candidate_info={"name": "Jane Smith", "email": "jane@example.com"},
        stage="initial_interview"
    )
    print(json.dumps(comm_result, indent=2))
    
    # Test interview prep
    print("\n3. Testing Interview Preparation:")
    interview_result = client.prepare_interview(
        role_info={
            "title": "Senior Software Engineer",
            "level": "Senior",
            "key_skills": ["Python", "AWS", "Leadership"]
        },
        candidate_background={
            "experience": "8 years software development",
            "skills": ["Python", "AWS", "Team Lead"]
        }
    )
    print(json.dumps(interview_result, indent=2))

if __name__ == "__main__":
    main()
```

During testing, track both qualitative and quantitative results. For example, measure recruiter satisfaction with generated job descriptions, response rates to candidate communications, and interviewers’ feedback on the usefulness of prep materials. Use these metrics to refine prompts, knowledge base contents, and model choices over time.

## Clean up

To avoid ongoing charges when you’re done testing or if you want to tear down this solution, follow these steps in order:

- Delete Lambda resources:  Delete all functions created for the agents. Remove associated CloudWatch log groups.
- Delete API Gateway endpoints:  Delete the API configurations. Remove any custom domain names. Delete all collections. Remove any custom policies. Wait for collections to be fully deleted before continuing to the next steps.
- Delete SNS topics  Delete all topics created for communications. Remove any subscriptions.
- Delete VPC resources:  Remove VPC endpoints. Delete security groups. Delete the VPC if it was created specifically for this solution.
- Clean up IAM resources:  Delete IAM roles created for the solution. Remove any associated policies. Delete service-linked roles if no longer needed.
- Delete KMS keys:  Schedule key deletion for unused KMS keys (keep keys if they’re used by other applications).
- Delete CloudWatch resources:  Delete dashboards. Delete alarms. Delete any custom metrics.
- Clean up S3 buckets:  Empty buckets used for knowledge bases. Delete the buckets.
- Delete the Amazon Bedrock knowledge base.

After cleanup, take these steps to verify all charges are stopped:

- Check your AWS bill for the next billing cycle
- Verify all services have been properly terminated
- Contact AWS Support if you notice any unexpected charges

Document the resources you’ve created and use this list as a checklist during cleanup to make sure you don’t miss any components that could continue to generate charges.

## Implementing AI in recruitment: Best practices

To successfully implement AI in recruitment while maintaining ethical standards and human oversight, consider these essential practices.

### Security, compliance, and infrastructure

The security implementation should follow a comprehensive approach to protect all aspects of the recruitment system. The solution deploys within a properly configured VPC with carefully defined security groups. All data, whether at rest or in transit, should be protected through AWS KMS encryption, and IAM roles are implemented following strict least privilege principles. The system maintains complete visibility through CloudWatch monitoring and audit logging, with secure API Gateway endpoints managing external communications. To protect sensitive information, implement data tokenization for personally identifiable information (PII) and maintain strict data retention policies. Regular privacy impact assessments and documented incident response procedures support ongoing security compliance.Consider the implementation of Amazon Bedrock Guardrails to provide granular control over AI model outputs, helping you enforce consistent safety and compliance standards across your AI applications. By implementing rule-based filters and boundaries, teams can prevent inappropriate content, maintain professional communication standards, and make sure responses align with their organization’s policies. You can configure guardrails at multiple levels—from individual agents to organization-wide implementations—with customizable controls for content filtering, topic restrictions, and response parameters. This systematic approach helps organizations mitigate risks while using AI capabilities, particularly in regulated industries or customer-facing applications where maintaining appropriate, unbiased, and safe interactions is crucial.

### Knowledge base architecture and management

The knowledge base architecture should follow a hub-and-spoke model centered around a core repository of organizational knowledge. This central hub maintains essential information including company values, policies, and requirements, along with shared reference data used across the agents. Version control and backup procedures maintain data integrity and availability.Surrounding this central hub, specialized knowledge bases serve each agent’s unique needs. The Job Description Agent accesses writing guidelines and inclusion requirements. The Communication Agent draws from approved message templates and workflow definitions, and the Interview Prep Agent uses comprehensive question banks and evaluation criteria.

### System integration and workflows

Successful system operation relies on robust integration practices and clearly defined workflows. Error handling and retry mechanisms facilitate reliable operation, and clear handoff points between agents maintain process integrity. The system should maintain detailed documentation of dependencies and data flows, with circuit breakers protecting against cascade failures. Regular testing through automated frameworks and end-to-end workflow validation supports consistent performance and reliability.

### Human oversight and governance

The AI-powered recruitment system should prioritize human oversight and governance to promote ethical and fair practices. Establish mandatory review checkpoints throughout the process where human recruiters assess AI recommendations and make final decisions. To handle exceptional cases, create clear escalation paths that allow for human intervention when needed. Sensitive actions, such as final candidate selections or offer approvals, should be subject to multi-level human approval workflows.To maintain high standards, continuously monitor decision quality and accuracy, comparing AI recommendations with human decisions to identify areas for improvement. The team should undergo regular training programs to stay updated on the system’s capabilities and limitations, making sure they can effectively oversee and complement the AI’s work. Document clear override procedures, so recruiters can adjust or override AI decisions when necessary. Regular compliance training for team members reinforces the commitment to ethical AI use in recruitment.

### Performance and cost management

To optimize system efficiency and manage costs effectively, implement a multi-faceted approach. Automatic scaling for Lambda functions makes sure the system can handle varying workloads without unnecessary resource allocation. For predictable workloads, use AWS Savings Plans to reduce costs without sacrificing performance. You can estimate the solution costs using the [AWS Pricing Calculator](https://calculator.aws/), which helps plan for services like Amazon Bedrock, Lambda, and Amazon Bedrock Knowledge Bases.

Comprehensive CloudWatch dashboards provide real-time visibility into system performance, facilitating quick identification and addressing of issues. Establish performance baselines and regularly monitor against these to detect deviations or areas for improvement. [Cost allocation tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html) help track expenses across different departments or projects, enabling more accurate budgeting and resource allocation.

To avoid unexpected costs, configure budget alerts that notify the team when spending approaches predefined thresholds. Regular capacity planning reviews make sure the infrastructure keeps pace with organizational growth and changing recruitment needs.

### Continuous improvement framework

Commitment to excellence should be reflected in a continuous improvement framework. Conduct regular metric reviews and gather stakeholder feedback to identify areas for enhancement. A/B testing of new features or process changes allows for data-driven decisions about improvements. Maintain a comprehensive system of documentation, capturing lessons learned from each iteration or challenge encountered. This knowledge informs ongoing training data updates, making sure AI models remain current and effective. The improvement cycle should include regular system optimization, where algorithms are fine-tuned, knowledge bases updated, and workflows refined based on performance data and user feedback. Closely analyze performance trends over time, allowing proactive addressing of potential issues and capitalization on successful strategies. Stakeholder satisfaction should be a key metric in the improvement framework. Regularly gather feedback from recruiters, hiring managers, and candidates to verify if the AI-powered system meets the needs of all parties involved in the recruitment process.

### Solution evolution and agent orchestration

As AI implementations mature and organizations develop multiple specialized agents, the need for sophisticated orchestration becomes critical. [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) provides the foundation for managing this evolution, facilitating seamless coordination and communication between agents while maintaining centralized control. This orchestration layer streamlines the management of complex workflows, optimizes resource allocation, and supports efficient task routing based on agent capabilities. By implementing Amazon Bedrock AgentCore as part of your solution architecture, organizations can scale their AI operations smoothly, maintain governance standards, and support increasingly complex use cases that require collaboration between multiple specialized agents. This systematic approach to agent orchestration helps future-proof your AI infrastructure while maximizing the value of your agent-based solutions.

## Conclusion

AWS AI services offer specific capabilities that can be used to transform recruitment and talent acquisition processes. By using these services and maintaining a strong focus on human oversight, organizations can create more efficient, fair, and effective hiring practices. The goal of AI in recruitment is not to replace human decision-making, but to augment and support it, helping HR professionals focus on the most valuable aspects of their roles: building relationships, assessing cultural fit, and making nuanced decisions that impact people’s careers and organizational success. As you embark on your AI-powered recruitment journey, start small, focus on tangible improvements, and keep the candidate and employee experience at the forefront of your efforts. With the right approach, AI can help you build a more diverse, skilled, and engaged workforce, driving your organization’s success in the long term.

For more information about AI-powered solutions on AWS, refer to the following resources:

- [Amazon Bedrock blog posts](https://aws.amazon.com/blogs/machine-learning/category/artificial-intelligence/amazon-machine-learning/amazon-bedrock/)
- [Responsible AI](https://aws.amazon.com/ai/responsible-ai/)

### About the Authors

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/02/04/Adesanya.jpeg)Dola Adesanya** is a Customer Solutions Manager at Amazon Web Services (AWS), where she leads high-impact programs across customer success, cloud transformation, and AI-driven system delivery. With a unique blend of business strategy and organizational psychology expertise, she specializes in turning complex challenges into actionable solutions. Dola brings extensive experience in scaling programs and delivering measurable business outcomes.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/02/04/ronhayman.png)**Ron Hayman** leads Customer Solutions for US Enterprise and Software Internet & Foundation Models at Amazon Web Services (AWS). His organization helps customers migrate infrastructure, modernize applications, and implement generative AI solutions. Over his 20-year career as a global technology executive, Ron has built and scaled cloud, security, and customer success teams. He combines deep technical expertise with a proven track record of developing leaders, organizing teams, and delivering customer outcomes.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/02/04/achf.jpeg)**Achilles Figueiredo** is a Senior Solutions Architect at Amazon Web Services (AWS), where he designs and implements enterprise-scale cloud architectures. As a trusted technical advisor, he helps organizations navigate complex digital transformations while implementing innovative cloud solutions. He actively contributes to AWS’s technical advancement through AI, Security, and Resilience initiatives and serves as a key resource for both strategic planning and hands-on implementation guidance.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/02/04/sai.png)**Sai Jeedigunta** is a Sr. Customer Solutions Manager at AWS. He is passionate about partnering with executives and cross-functional teams in driving cloud transformation initiatives and helping them realize the benefits of cloud. He has over 20 years of experience in leading IT infrastructure engagements for fortune enterprises.
