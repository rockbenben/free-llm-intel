---
vendor: aws_bedrock
title: AI meets HR: Transforming talent acquisition with Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/ai-meets-hr-transforming-talent-acquisition-with-amazon-bedrock
date: 2026-02-12
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 320d77c48607
---

# AI 与 HR 相遇：用 Amazon Bedrock 变革人才招聘

组织在提高招聘流程效率的同时保持公平招聘实践方面面临重大挑战。通过用 AI 变革招聘和人才获取流程，组织可以克服这些挑战。AWS 提供一套[ AI 服务](https://aws.amazon.com/ai/?ams%23interactive-card-vertical%23pattern-data--1593418038.filter=%257B%2522filters%2522%253A%255B%255D%257D)，可显著提升招聘实践的效率、效果和公平性。借助 AWS AI 服务，特别是 [Amazon Bedrock](https://aws.amazon.com/bedrock/)，你可以构建一个高效且可扩展的招聘系统，简化招聘流程，帮助人工审核人员专注于候选人的面试和评估。

在本文中，我们展示如何使用 Amazon Bedrock、[Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/)、[AWS Lambda](https://aws.amazon.com/lambda) 和其他 AWS 服务创建一个 AI 驱动的招聘系统，以改进职位描述撰写、候选人沟通和面试准备，同时保持人工监督。

## AI 驱动的招聘生命周期

招聘流程中存在大量通过专用 [agent](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html) 借助 AI 改进的机会，每个 agent 都由 Amazon Bedrock 驱动，并连接到专用的 Amazon Bedrock 知识库。下面探讨这些 agent 如何在招聘生命周期的各个关键阶段协同工作。

### 职位描述的创建与优化

撰写具有包容性和吸引力的职位描述，对于吸引多元化人才库至关重要。Job Description Creation and Optimization Agent 使用 Amazon Bedrock 中提供的高级语言模型，并连接到一个包含组织历史职位描述和包容性指南的 Amazon Bedrock 知识库。

使用安全的 [Amazon Virtual Private Cloud](https://aws.amazon.com/vpc)（Amazon VPC）配置和 [AWS Identity and Access Management](https://aws.amazon.com/iam/)（IAM）[角色](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)来部署 Job Description Agent。该 agent 引用你的知识库来优化招聘信息，同时确保符合组织标准和包容性语言要求。

### 候选人沟通管理

Candidate Communication Agent 通过以下组件管理候选人互动：

- 根据工作流阶段触发沟通的 Lambda 函数
- [Amazon Simple Notification Service](https://aws.amazon.com/sns)（Amazon SNS），用于安全的电子邮件和短信投递
- 与审批工作流集成，以处理受监管的沟通
- 基于候选人进展的自动状态更新

为 Communication Agent 配置适当的 VPC 端点，并对传输中和静态的所有数据加密。使用 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch) 监控来跟踪沟通效果和响应率。

### 面试准备与反馈

Interview Prep Agent 通过以下方式支持面试流程：

- 访问包含面试问题、SOP 和最佳实践的知识库
- 基于岗位要求生成与情境相关的面试材料
- 使用 Amazon Bedrock 分析面试官的反馈和笔记，识别关键情绪以及各次评估中一致的主题
- 确保符合知识库中存储的面试标准

尽管该 agent 提供面试结构和指导，面试官仍对对话和评估过程保有完全控制权。

## 方案概览

该架构将招聘 agent 和 AWS 服务整合为一个全面的招聘系统，以增强并简化招聘流程。下图展示了三个专用 AI agent 如何协同管理招聘流程的不同环节，从发布职位信息到汇总面试反馈。每个 agent 都使用 Amazon Bedrock 并连接到专用的 Amazon Bedrock 知识库，同时满足安全和合规要求。

## ![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/26/image-1-2.jpg)

该方案由三个协同工作的主要组件组成，以改进招聘流程：

- **Job Description Creation and Optimization Agent** – Job Description Creation and Optimization Agent 利用 Amazon Bedrock 的 AI 能力创建和优化招聘信息，并直接连接到一个包含示例描述和包容性语言最佳实践的 Amazon Bedrock 知识库。
- **Candidate Communication Agent **– 在候选人沟通方面，这个专用 agent 通过自动化系统简化互动。它使用 Lambda 函数管理沟通工作流，并使用 Amazon SNS 实现可靠的消息投递。该 agent 与候选人保持直接联系，同时确保沟通遵循已批准的模板和流程。
- **Interview Prep Agent **– Interview Prep Agent 是面试官的综合资源，提供面试形式和问题方面的指导，并帮助整理、总结和分析反馈。它可持续访问包含面试标准的详细知识库，并利用 Amazon Bedrock 的自然语言处理能力分析面试反馈模式和主题，帮助各招聘团队保持一致的评价实践。

## 先决条件

在实施这个 AI 驱动的招聘系统之前，请确保你具备以下条件：

- AWS 账户和访问权限：  具有管理员权限的 AWS 账户 对 Amazon Bedrock [基础模型](https://docs.aws.amazon.com/bedrock/latest/userguide/foundation-models-reference.html)（FMs）的访问权限 创建和管理 IAM 角色及策略的权限
- 所需的 AWS 服务：  [Amazon API Gateway](https://aws.amazon.com/api-gateway) 可访问 FMs 的 Amazon Bedrock Amazon Bedrock Knowledge Bases Amazon CloudWatch [AWS Key Management Service](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html)（AWS KMS） AWS Lambda Amazon SNS 用于知识库存储的 [Amazon Simple Storage Service](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)（Amazon S3） Amazon VPC
- 技术要求：  具备 Python 3.9 或更高版本的基础知识（用于 Lambda 函数） 具备配置 VPC 端点的网络访问权限
- 安全与合规：  理解 AWS 安全最佳实践 用于安全通信的 SSL/TLS 证书 来自组织安全团队的合规批准

在以下各节中，我们将考察构成 AI 驱动招聘系统的关键组件。每一部分在构建安全、可扩展且有效的方案中发挥着关键作用。我们从基础设施定义开始，逐步介绍部署、知识库集成、核心 AI agent 和测试工具。

## 基础设施即代码

以下 [AWS CloudFormation](https://aws.amazon.com/cloudformation) 模板定义了完整的 AWS 基础设施，包括 VPC 配置、安全组、Lambda 函数、API Gateway 和知识库。它便于通过适当的 IAM 角色和加密实现安全、可扩展的部署。

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

## 部署自动化

以下自动化脚本负责招聘系统基础设施和 Lambda 函数的部署。它管理 CloudFormation 堆栈的创建与更新以及 Lambda 函数代码的更新，使系统部署和更新变得流畅且一致。

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

## 知识库集成

中央知识库管理器与 Amazon Bedrock 知识库集合对接，为招聘 agent 提供最佳实践、模板和标准。它使 AI agent 能够基于组织知识做出明智决策。

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

要提高检索增强生成（RAG）的质量，首先要调优你的 Amazon Bedrock 知识库。调整文档的分块大小和重叠量，尝试不同的嵌入模型，并启用重排序以提升最相关段落的排名。你还可以为每个 agent 选择不同的基础模型。例如，对于大量的职位描述和沟通任务，使用 Anthropic 的 Claude 3 Haiku 这类快速模型；对于需要更深入分析的 Interview Prep Agent，使用 Anthropic 的 Claude 3 Sonnet 这类能力更强的模型或其他推理优化模型。将这些实验记录到持续改进流程中，以便将表现最佳的配置标准化。

## 核心 AI agent

三个 agent 之间的集成通过 API Gateway 和 Lambda 处理，每个 agent 都通过各自的端点暴露。系统使用三个专用 AI agent。

### Job Description Agent

该 agent 是招聘流程的第一步。它使用 Amazon Bedrock，将岗位要求与知识库中的最佳实践相结合，创建具有包容性且有效的职位描述。

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

该 agent 管理整个招聘过程中的候选人沟通。它与 Amazon SNS 集成以发送通知，并使用已批准的模板提供专业、一致的信息。

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

该 agent 根据岗位和候选人背景准备量身定制的面试材料和问题。它有助于保持一致的面试标准，同时适应具体职位。

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

## 测试与验证

以下测试客户端演示了如何与招聘系统 API 交互。它提供了主要功能的用法示例，并帮助验证系统功能。

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

在测试期间，同时跟踪定性和定量结果。例如，衡量招聘人员对生成的职位描述的满意度、候选人沟通的响应率，以及面试官对准备材料实用性的反馈。利用这些指标，随时间推移不断优化 prompt、知识库内容和模型选择。

## 清理

为避免测试完成后继续产生费用，或当你想要拆除该方案时，请按顺序执行以下步骤：

- 删除 Lambda 资源：  删除为 agent 创建的所有函数。移除关联的 CloudWatch 日志组。
- 删除 API Gateway 端点：  删除 API 配置。移除任何自定义域名。删除所有集合。移除任何自定义策略。等待集合完全删除后，再继续下一步。
- 删除 SNS 主题  删除为沟通创建的所有主题。移除任何订阅。
- 删除 VPC 资源：  移除 VPC 端点。删除安全组。如果该 VPC 是专门为本方案创建的，则一并删除。
- 清理 IAM 资源：  删除为本方案创建的 IAM 角色。移除任何关联策略。如不再需要，删除服务关联角色。
- 删除 KMS key：  为未使用的 KMS key 安排删除计划（若 key 被其他应用使用，则保留）。
- 删除 CloudWatch 资源：  删除仪表板。删除告警。删除任何自定义指标。
- 清理 S3 存储桶：  清空用于知识库的存储桶。删除这些存储桶。
- 删除 Amazon Bedrock 知识库。

清理完成后，请执行以下步骤以确认所有费用均已停止：

- 查看下一个账单周期的 AWS 账单
- 确认所有服务均已正确终止
- 如发现任何意外费用，请联系 AWS Support

记录你创建的资源，并在清理时将此列表用作检查清单，确保不会遗漏任何可能继续产生费用的组件。

## 在招聘中实施 AI：最佳实践

要在保持道德标准和人工监督的同时成功在招聘中实施 AI，请考虑以下关键实践。

### 安全、合规与基础设施

安全实施应遵循全面的方法，保护招聘系统的方方面面。方案部署在配置得当的 VPC 中，并配有精心定义的安全组。所有数据，无论静态还是传输中，都应通过 AWS KMS 加密加以保护，IAM 角色遵循严格的最小权限原则实施。系统通过 CloudWatch 监控和审计日志保持全面可见性，由安全的 API Gateway 端点管理外部通信。为保护敏感信息，应对个人身份信息（PII）实施数据标记化，并维护严格的数据保留策略。定期开展隐私影响评估并建立成文的事件响应流程，以支持持续的安全合规。考虑实施 Amazon Bedrock Guardrails，对 AI 模型输出提供细粒度控制，帮助你在所有 AI 应用中执行一致的安全与合规标准。通过实施基于规则的过滤器和边界，团队可以防止不当内容，维持专业的沟通标准，并确保响应符合组织政策。你可以在多个层级配置 guardrails——从单个 agent 到组织范围的实现——并对内容过滤、主题限制和响应参数提供可定制的控制。这种系统化的做法帮助组织在使用 AI 能力的同时降低风险，尤其是在需要维持适当、无偏见且安全交互的受监管行业或面向客户的应用中。

### 知识库架构与管理

知识库架构应遵循以组织知识核心存储库为中心的 hub-and-spoke 模型。这个中央枢纽维护关键信息，包括公司价值观、政策、要求，以及各 agent 共用的参考数据。版本控制和备份流程保障数据完整性与可用性。围绕这个中央枢纽，专用知识库满足每个 agent 的独特需求。Job Description Agent 访问写作指南和包容性要求。Communication Agent 使用已批准的消息模板和工作流定义，Interview Prep Agent 使用全面的题库和评价标准。

### 系统集成与工作流

系统成功运行依赖于稳健的集成实践和定义清晰的工作流。错误处理和重试机制有助于可靠运行，agent 之间清晰的交接点保障流程完整性。系统应维护关于依赖关系和数据流的详细文档，并使用熔断器防止级联故障。通过自动化框架进行定期测试以及端到端工作流验证，有助于保持一致的性能和可靠性。

### 人工监督与治理

AI 驱动的招聘系统应将人工监督和治理放在优先位置，以促进合乎道德且公平的实践。在整个流程中设立强制性的审查检查点，由人工招聘人员评估 AI 建议并做出最终决定。为处理例外情况，建立清晰的升级路径，以便在需要时引入人工干预。敏感操作（如最终候选人遴选或录用审批）应接受多级人工审批工作流。为维持高标准，应持续监控决策质量和准确性，将 AI 建议与人工决策进行对比以识别改进空间。团队应定期接受培训，及时掌握系统能力和局限，确保能有效监督并补充 AI 的工作。记录清晰的覆盖流程，使招聘人员在必要时能够调整或推翻 AI 决策。对团队成员开展定期合规培训，强化在招聘中合乎道德地使用 AI 的承诺。

### 性能与成本管理

要优化系统效率并有效管理成本，应采取多方面的方法。Lambda 函数的自动扩缩容确保系统能够应对变化的负载，而无需不必要的资源分配。对于可预测的负载，使用 AWS Savings Plans 在不牺牲性能的前提下降低成本。你可以使用 [AWS Pricing Calculator](https://calculator.aws/) 估算方案成本，它有助于规划 Amazon Bedrock、Lambda 和 Amazon Bedrock Knowledge Bases 等服务的费用。

全面的 CloudWatch 仪表板提供系统性能的实时可见性，便于快速发现和解决问题。建立性能基线并定期对照监控，以检测偏差或改进空间。[成本分配标签](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html)有助于跟踪不同部门或项目的开支，从而实现更准确的预算编制和资源分配。

为避免意外费用，请配置预算告警，在支出接近预定义阈值时通知团队。定期的容量规划审查确保基础设施跟上组织增长和不断变化的招聘需求。

### 持续改进框架

追求卓越应体现在持续改进框架中。定期开展指标评审并收集利益相关者反馈，以识别改进领域。对新功能或流程变更进行 A/B 测试，可以基于数据做出改进决策。维护全面的文档体系，记录每次迭代或遇到的挑战中汲取的经验教训。这些知识为持续的训练数据更新提供依据，确保 AI 模型保持时效性和有效性。改进周期应包括定期的系统优化：根据性能数据和用户反馈微调算法、更新知识库并优化工作流。密切分析一段时间内的性能趋势，以便主动解决潜在问题并利用成功的策略。利益相关者满意度应成为改进框架中的关键指标。定期收集招聘人员、招聘经理和候选人的反馈，验证 AI 驱动的系统是否满足招聘流程中所有相关方的需求。

### 方案演进与 agent 编排

随着 AI 实施日趋成熟、组织开发出多个专用 agent，对复杂编排的需求变得至关重要。[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 为管理这一演进提供了基础，在保持集中控制的同时促进 agent 之间的无缝协调与通信。这个编排层简化了复杂工作流的管理，优化资源分配，并支持基于 agent 能力的高效任务路由。通过将 Amazon Bedrock AgentCore 作为方案架构的一部分，组织可以平稳扩展 AI 运营、维持治理标准，并支持需要多个专用 agent 协作的日益复杂的用例。这种系统化的 agent 编排方法有助于让 AI 基础设施面向未来，同时最大化基于 agent 的方案的价值。

## 结论

AWS AI 服务提供可用于变革招聘和人才获取流程的特定能力。通过使用这些服务并持续高度重视人工监督，组织能够创建更高效、更公平、更有效的招聘实践。AI 在招聘中的目标不是取代人类决策，而是增强和支持它，帮助 HR 专业人士专注于其角色中最有价值的方面：建立关系、评估文化契合度，以及做出影响人们职业和组织成功的细致决策。当你开启 AI 驱动的招聘之旅时，从小处着手，聚焦切实的改进，并始终将候选人与员工体验放在工作的核心位置。凭借正确的方法，AI 可以帮助你建立一支更加多元、技能更强、更投入的员工队伍，从长远上推动组织的成功。

有关 AWS 上 AI 驱动方案的更多信息，请参阅以下资源：

- [Amazon Bedrock 博客文章](https://aws.amazon.com/blogs/machine-learning/category/artificial-intelligence/amazon-machine-learning/amazon-bedrock/)
- [负责任的 AI](https://aws.amazon.com/ai/responsible-ai/)

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/02/04/Adesanya.jpeg)Dola Adesanya** 是 Amazon Web Services (AWS) 的客户解决方案经理，负责领导客户成功、云转型和 AI 驱动系统交付方面的高影响力项目。凭借商业战略与组织心理学相结合的独特专长，她专注于将复杂挑战转化为可落地的解决方案。Dola 在扩展项目和交付可衡量的业务成果方面拥有丰富经验。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/02/04/ronhayman.png)**Ron Hayman** 领导 Amazon Web Services (AWS) 美国企业与软件互联网及基础模型领域的客户解决方案团队。他的团队帮助客户迁移基础设施、现代化应用并实施生成式 AI 方案。Ron 作为全球技术高管拥有 20 年职业生涯，期间组建并扩展了云、安全和客户成功团队。他兼具深厚的技术专长，以及在培养领导者、组织团队和交付客户成果方面的出色业绩记录。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/02/04/achf.jpeg)**Achilles Figueiredo** 是 Amazon Web Services (AWS) 的高级解决方案架构师，负责设计和实施企业级云架构。作为值得信赖的技术顾问，他在实施创新云方案的同时，帮助组织应对复杂的数字化转型。他通过 AI、安全和韧性方面的举措积极推动 AWS 的技术进步，并作为战略规划与动手实施指导的重要资源。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/02/04/sai.png)**Sai Jeedigunta** 是 AWS 的高级客户解决方案经理。他热衷于与高管和跨职能团队合作，推动云转型计划并帮助他们实现云的价值。他在为大型知名企业主导 IT 基础设施项目方面拥有超过 20 年的经验。
