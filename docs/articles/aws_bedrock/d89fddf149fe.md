---
vendor: aws_bedrock
title: 使用 Amazon Bedrock 和 AWS Transform 将大型机 Assembler 现代化为 Java
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/modernizing-mainframe-assembler-to-java-using-amazon-bedrock-and-aws-transform
date: 2026-11-16
lang: zh
captured: 2026-11-17
extractor: readability-v1
translator: mt
status: translated
body_sha: 613331c9f001
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 使用 Amazon Bedrock 和 AWS Transform 将大型机 Assembler 现代化为 Java

想象一下，一个批处理作业几十年来每天晚上都运行而没有失败，而唯一理解其代码的人即将退休。在与银行、保险和航空公司客户合作时，我们一次又一次地看到这种情况。他们的汇编程序仍然运行关键的业务操作，但每年能够阅读它们的人越来越少。手工重写它们需要数年时间，存在违反无人记得编写的业务规则的风险，并且仍然依赖于即将离开的专家。 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 和 [AWS Transform](https://aws.amazon.com/transform/) 改变了这个等式。

本文向您展示了一种使用 [Amazon Bedrock](https://aws.amazon.com/bedrock/)、[Kiro IDE](https://kiro.dev/)（AI 支持的集成开发环境）和 [AWS Transform](https://aws.amazon.com/transform/) 的多阶段转换方法，与手动方法相比，该方法有助于缩短现代化时间，同时通过验证检查点保持业务逻辑完整性。您将学习如何系统地从汇编代码中提取业务规则，通过中间 COBOL 阶段进行转换，以及如何将现代化应用程序部署为 AWS 上的 Java Spring Boot 服务。

## 先决条件

在开始现代化过程之前，请确保您拥有：

- 活动 [AWS 账户](https://aws.amazon.com/account/)，具有 Amazon Bedrock、AWS Transform 和 Amazon Simple Storage Service (Amazon S3) 的最低权限 AWS Identity and Access Management (IAM) 权限。
- 访问 [Amazon Q Developer](https://aws.amazon.com/q/developer/) 或 [Kiro](https://kiro.dev/) 进行 AI 辅助代码分析。
- 访问 AWS Transform 以进行 COBOL 到 Java 的转换。
- 使用适当的基础模型 (FM) 访问 Amazon Bedrock。
- 配置用于源代码和项目存储的 [Amazon S3](https://aws.amazon.com/s3/) 存储桶，并启用加密和阻止公共访问。
- 了解目标业务领域和应用程序功能。
- 是否有业务和技术主题专家 (SME) 参加验证会议。
- 带有可用文档的源汇编代码清单。
- 测试具有预期输出的数据集以进行功能等效性测试。

## 解决方案概述

您可以通过系统的五阶段方法将与 COBOL 紧密结合的旧式大型机 Assembler 应用程序转换为为 AWS 云构建的 Java Spring Boot 应用程序。这种多阶段方法将 Assembler 转换为 COBOL 作为 Java 转换之前的中间步骤，与直接将 Assembler 转换为 Java 相比，可以降低风险并以更高的可靠性保留业务逻辑。中间 COBOL 阶段提供了一种结构化的、人类可读的格式，主题专家 (SME) 可以在最终转换之前对其进行验证。这可确保业务规则在整个现代化过程中保持完整。以下部分描述了当前的大型机架构和以云为中心的目标状态。

### 当前状态

您当前的体系结构代表了传统的大型机环境，其中汇编程序执行批处理、与 COBOL 连接、与数据库交互并处理文件。其核心是，JCL（作业控制语言）作业按计划的时间间隔触发汇编程序执行。这些程序从 VSAM（虚拟存储访问方法）和顺序文件读取输入，并对 IBM Db2 for z/OS 执行操作。您的业​​务逻辑使用低级寄存器操作（直接 CPU 寄存器操作）和内存管理来执行。输出被写回文件或数据库表，并通过 JCL 返回代码报告作业完成状态。所有这些都运行在 IBM z/OS 大型机基础设施上。

![具有 JCL 触发的汇编批处理程序访问 VSAM 文件和 IBM Db2 的大型机架构z/OS](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/10/ML-20283-1-1.png)

图 1：大型机汇编器架构

### 目标状态

该现代化解决方案可帮助您通过多阶段、人工智能驱动的工作流程，将传统大型机 Assembler 应用程序转换为为 AWS 云构建的 Java 应用程序。该架构使用 Amazon Bedrock 和 Kiro IDE 进行 AI 辅助代码分析和业务规则提取，并使用 AWS Transform 进行自动 COBOL 到 Java 转换。

如果 COBOL 源代码已经可用，您可以按照传统方法将其直接提供给 AWS Transform 以转换为 Java Spring Boot 应用程序。

**通过此解决方案，您可以实现：**

- 与手动方法相比，减少了转换时间。
- 通过验证检查点系统地保存业务逻辑。
- 关键阶段的人机交互验证。
- 通过功能等效性测试进行自动代码转换。

![端到端 AWS 工作流程将 Assembler 转换为 Java，经过五个阶段，从业务规则提取到COBOL 到 Java](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/10/ML-20283-2-1.png)

图 2：AWS 上的端到端 Assembler 到 Java 转换架构，显示了五个主要阶段：业务规则提取、规范驱动的数据流、Assembler 到 COBOL 转换、验证和 COBOL 到 Java 转换

您可以通过分析汇编代码来开始转换工作流程以生成业务规则提取 (BRE) 文档。然后，您可以通过人机交互细化创建详细的功能规范。经过验证的规范指导汇编器到 COBOL 的转换，生成中间 COBOL 代码，弥合低级硬件指令和面向业务的构造之间的差距。在 AWS Transform 将其转换为 Java 之前，该 COBOL 代码会经过功能等效性测试，并在每个阶段设置验证检查点，以降低风险并验证业务连续性。

## 使用 AI 提取业务规则

业务规则提取 (BRE) 的质量直接影响转换的准确性，因此请仔细关注此阶段。通过 Kiro IDE 或 Amazon Bedrock 控制台以及适用于大型机的 AWS Transform 使用 Amazon Bedrock 从 Assembler 源代码中提取和记录业务规则。

您可以通过 [Chat Playground](https://docs.aws.amazon.com/bedrock/latest/userguide/playgrounds.html) 直接在 Amazon Bedrock 中使用本文中的提示，或者在 Kiro IDE 中使用其内置的 [AI 聊天和规格面板](https://kiro.dev/docs)。在运行之前，将占位符值替换为实际的汇编器代码和上下文。

Amazon Bedrock 是前四个阶段背后的推理平台：业务规则提取、规范创建、汇编器到 COBOL 转换和验证。选择具有强大代码推理和大上下文窗口的基础模型，因为汇编程序又长又密集。将温度设置为 0，以便在运行期间获得一致的输出。要处理多个程序，请通过 Amazon Bedrock Converse API 调用相同的提示，并将每个输出存储在 Amazon S3 存储桶中，以便它可以馈送到下一阶段。 Amazon Bedrock 不会使用您的提示或模型输出来训练 AWS 模型或与第三方共享它们。有关详细信息，请参阅 [Amazon Bedrock 中的数据保护](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html)。使用经过净化的测试数据而不是生产数据或个人身份信息 (PII)。

您为人工智能提供的上下文越多，它就越能理解代码背后的业务意图。提示时包括相关文档、数据字典和可用的业务上下文以及汇编程序代码。

**注意：** 随时保存每个提示的输出。您将需要它们作为下一阶段的输入。

上下文感知分析的提示示例：
```
Extract the business rules and data mappings from this Assembly code.
[PASTE YOUR ASSEMBLY CODE HERE]

## EXTRACT

1.Business Rules: Identify EVERY rule including conditional logic, calculations, validations, transformations, error handling, and loops.

For each rule provide:
- Unique ID (BR001, BR002, etc.)
- Name and description
- Business purpose
- Input fields/registers
- Output fields/registers
- Logic in plain English
- Conditions that trigger the rule

2.Data Mappings: Identify the data transformations with:
- Source field (register or memory location)
- Target field (COBOL variable name)
- Transformation logic
- Validation rules

## RETURN JSON
{  
"program_name": "string",
  "business_rules": [
    {
      "id": "BR001",
      "name": "string",
      "description": "string",
      "purpose": "string",
      "inputs": ["array"],
      "outputs": ["array"],
      "logic": "string",
      "conditions": ["array"]
    }
  ],
  "data_mappings": [
    {
      "source_field": "string",
      "target_field": "string",
      "transformation": "string",
      "validation_rules": ["array"]
    }
  ],
  "summary": "string"
}
```
您可以通过添加业务上下文中特定于域的术语来自定义此提示。运行此提示时，您将看到结构化 JSON 输出，可用于自动验证以及与下游转换工具的直接集成。数据映射的准确性直接影响转换质量。不完整的映射可能会导致业务逻辑丢失或损坏。

## 与中小企业验证

将 AI 生成的 BRE 文档视为草稿，而不是最终输出。在继续之前，让主题专家审查并验证提取的规则。在继续创建规范之前，在验证日志中记录差异并根据 SME 反馈更新 BRE。

为了帮助中小企业验证规则，请使用流程图和数据流程图等视觉辅助工具来补充文本 BRE 文档。维护验证检查表，涵盖业务规则准确性、数据映射正确性、边缘情况处理和错误条件完整性。

## 提取规范驱动的数据流

在与中小企业验证业务规则后，将其转化为指导代码转换的详细功能规范。这种规范驱动的方法确认了业务需求在代码转换开始之前得到了明确的记录和商定，从而减少了以后代价高昂的返工。

使用提取的 BRE 文档创建指导 COBOL 代码生成的完整功能规范。这些规范应包括程序概述、COBOL 数据结构、流程设计和业务规则覆盖映射。

功能规范生成的示例提示：
```
Generate a complete functional specification for COBOL code generation based on the following Business Rules Extraction (BRE).

[PASTE THE BRE JSON HERE]

Create a comprehensive specification including:

## 1. PROGRAM OVERVIEW
- Program purpose and key functionality
- Business rules coverage summary

## 2. COBOL DATA STRUCTURES
Design data structures with:
- COBOL naming: UPPERCASE-WITH-HYPHENS
- Appropriate PIC clauses:
  * PIC 9(n) / S9(n) for integers (S for signed)
  * PIC 9(n)V9(m) / S9(n)V9(m) for decimals
  * PIC X(n) for alphanumeric, PIC A(n) for alphabetic
  * COMP-3 for packed decimal (efficient storage)
- Hierarchical levels (01, 05, 10, 15)
- 88-level condition names for flags

Include:
- The fields from business rules (inputs/outputs)
- The fields from data mappings (source/target)
- Additional fields for calculations, flags, error handling

## 3. PROCESS FLOW DESIGN
Create step-by-step process flow with:
- Sequential procedure steps (initialization → processing → output)
- Decision points and validation steps
- Calculation sequences and error handling

For each step specify:
- Step number and name
- Description
- Business rules implemented (BR IDs)
- Input/output data

## 4. BUSINESS RULES COVERAGE MAP
Map each business rule to:
- Implementation location (procedure/paragraph name)
- Data structures used
- Dependencies on other rules

Return as JSON:
{
  "program_name": "string",
  "overview": "string",
  "data_structures": [
    {
      "name": "WORKING-STORAGE-SECTION",
      "fields": [
        {
          "level": "01",
          "name": "FIELD-NAME",
          "type": "PIC X(10)",
          "description": "string"
        }
      ]
    }
  ],
  "process_flows": [
    {
      "step": 1,
      "name": "PROCEDURE-NAME",
      "description": "string",
      "business_rules": ["BR001"],
      "inputs": ["array"],
      "outputs": ["array"]
    }
  ],
  "business_rules_coverage": {
    "BR001": "Implementation details"
  }
}
```
您可以根据您的 COBOL 标准调整数据结构规范。当您运行此提示时，您将收到完整的功能规范，具有从业务规则到 COBOL 结构的完整可追溯性，可供 SME 审核并与 Kiro 直接集成以生成代码。

## 将旧版汇编器转换为 COBOL

有了经过验证的功能规范，下一阶段将使用这些结构化输出来指导汇编器到 COBOL 的转换。中间 COBOL 步骤可帮助您弥合低级硬件指令和面向业务的构造之间的差距，从而帮助您验证在最终 Java 转换之前是否保留了业务逻辑。

指导转换的示例提示：
```
Generate production-ready COBOL code from these specifications.

Program Name: [PROGRAM_NAME]
Assembly Code: [PASTE HERE]
Business Rules (BRE): [PASTE HERE]
Functional Specification: [PASTE HERE]

## REQUIREMENTS
- Implement the business rules from BRE with traceability comments (BR IDs)
- Use exact data structures from specification
- Follow process flow sequence with error handling

## COBOL STRUCTURE
Include: IDENTIFICATION DIVISION (PROGRAM-ID, AUTHOR, DATE-WRITTEN), ENVIRONMENT DIVISION (if needed), DATA DIVISION (WORKING-STORAGE SECTION, FILE/LINKAGE sections if needed), PROCEDURE DIVISION (main paragraph, sub-paragraphs, STOP RUN/GOBACK)

## FORMATTING (STRICT)
Columns 1-6: Sequence numbers (000100, 000200, +100)
Column 7: Indicator (* comment, - continuation, space normal)
Columns 8-11: Area A (Division/Section headers, Paragraphs, Level 01/77)
Columns 12-72: Area B (Level 05-88, statements)

Alignment:
- Level 01/77: Column 8 | Level 05-88: Column 12
- PIC clauses: Column 40 | VALUE clauses: Column 56
- Indent subordinate levels by 4 spaces
- Paragraph names: Column 8 | Statements: Column 12
- Use explicit scope terminators (END-IF, END-PERFORM)

## DATA TYPES
Numeric: PIC 9(n)/S9(n) (integer), PIC 9(n)V9(m)/S9(n)V9(m) (decimal), COMP/BINARY (indexes), COMP-3 (financial)
Alphanumeric: PIC X(n), PIC A(n)
Condition Names: 88-level for flags

## COMMENTS
1.Header(MANDATORY):
000100*****************************************************************
000200* Program: [NAME]                                               *
000300* Purpose: [Description]                                        *
000400* Generated from Assembly using BRE transformation              *
000500* Business Rules: [COUNT] | Data Mappings: [COUNT]              *
000600*****************************************************************

2.Section comments before major sections. 
3.Business rule comments reference BR IDs:
002000* Implements BR001: Validate Input Numbers
002100 VALIDATE-INPUTS.

## IMPLEMENTATION
- Create dedicated paragraph per business rule with BR ID comment
- Implement exact logic from BRE, handle the conditions
- Follow process flow order using PERFORM statements
- Use IF/EVALUATE for decisions, PERFORM UNTIL/VARYING for loops
- Include error handling: validate inputs, check division by zero, verify bounds, set error flags

## OUTPUT FORMAT
CRITICAL: Return ONLY COBOL code. NO explanatory text, NO markdown blocks, NO commentary.
START with sequence-numbered header comment. END with STOP RUN/GOBACK.
```
您可以修改格式要求以符合您组织的 COBOL 标准。当您运行此提示时，您将生成语法正确的 COBOL 代码，逻辑上与原始汇编程序等效，并且完全可跟踪，并带有将每个代码部分链接回 BRE 文档中的特定业务规则的注释。生成后，在进行最终的 Java 转换之前严格验证 COBOL 代码。

## 验证转换

您应该将测试视为整个转型过程中持续进行的活动，而不仅仅是最后阶段。汇编程序和 COBOL 代码之间的功能等效性验证应采用全面的测试框架，系统地评估语法正确性、结构对齐、逻辑等效性、数据流完整性、业务规则覆盖率和规范合规性。

指导测试的示例提示：
```
Perform comprehensive validation and analysis of ASM-to-COBOL translation.

Assembly Code: [PASTE HERE]
COBOL Code: [PASTE HERE]
BRE JSON: [PASTE HERE]
Spec JSON: [PASTE HERE]

## PART 1: VALIDATION

Perform 6 validation checks:

1.Syntax Check: Verify COBOL syntax (divisions, PIC clauses, statements, keywords, column alignment)
   Return: valid (true/false), errors array, warnings array
2.Structure Check: Compare program structure (sections, flow, procedures, control flow, data organization)
   Return: equivalent (true/false), score (0.0-1.0), issues array
3.Logic Check: Verify logic equivalence (conditionals, calculations, loops, error handling, edge cases)
   Return: equivalent (true/false), score (0.0-1.0), differences array
4.Data Flow Check: Verify data transformations (mappings, conversions, I/O, calculations, precision)
   Return: equivalent (true/false), score (0.0-1.0), issues array
5.BRE Coverage Check: Verify the business rules implemented (location, inputs/outputs, conditions)
   Return: coverage_score (0.0-1.0), implemented_rules array, missing_rules array, details object
6.Spec Compliance Check: Verify specification adherence (data structures, process flow, functions, data types)
   Return: compliant (true/false), score (0.0-1.0), issues array

Overall Equivalence Score: Weighted average (Syntax 20%, Structure 20%, Logic 30%, Data Flow 30%, BRE Coverage +10%, Spec Compliance +10%). Status "passed" if ≥0.7.

## PART 2: ANALYSIS

1.Quality Assessment: Classify quality (Excellent ≥0.9, Good ≥0.7, Fair ≥0.5, Poor <0.5) with description and validation status
2.Quality Metrics: Detailed scores for the 6 validation dimensions
3.Improvement Areas: Prioritized list with area name, severity (high/medium/low), issues array, priority (1-5)
4.Recommendations: Actionable suggestions per area (syntax fixes, structure alignment, logic verification, data flow corrections, missing BR implementation, spec compliance)
5.BRE Analysis: Per-rule analysis (rule_id, implemented, location, quality 1-5, deviations, notes) with overall_implementation_quality and summary
6.Code Suggestions: Specific improvements with category (Structure/Naming/Error Handling/Performance/Best Practices), suggestion, location, priority, optional example
7.Executive Summary: Quality level, equivalence score, validation status, improvement areas count, top 3 issues, key recommendations

## OUTPUT FORMAT

Return single JSON with validation and analysis objects. Include the fields: status, equivalence_score, validation_results (the 6 checks), findings, recommendations, quality_assessment, quality_metrics, improvement_areas, bre_analysis, code_suggestions, summary.
CRITICAL: Be thorough, specific (line numbers/paragraphs), actionable, honest (accurate scores), comprehensive (the rules/dimensions). Return JSON only, no explanatory text.
Generate complete validation and analysis report now.
```
您可以根据您的质量要求自定义验证阈值。当您运行此提示时，您将收到一份全面的验证报告，其中包含可操作的建议，用于解决程序结构、条件逻辑、数据转换以及原始汇编器指令和现代化 COBOL 实现之间的可追溯性方面的差距。

## COBOL 到 Java 的转换

在最后阶段，您使用 [AWS Transform](https://aws.amazon.com/transform/) 自动将经过验证的 COBOL 代码转换为 Java Spring Boot 应用程序。通过 AWS Transform 中的智能重构生成生产就绪的 Java 代码。这种重构保留了先前阶段验证的业务逻辑，同时引入了现代设计模式，包括依赖项注入、存储库模式和服务层。

您可以在 AWS 基础设施上部署生成的 Java 应用程序，以实现云可扩展性和弹性，同时保持与旧大型机系统相同的业务功能。这种以云为中心的方法用可以独立部署、监控和增强的模块化、可维护的代码取代了单一的大型机架构。

有关详细的分步说明，请参阅 [AWS Transform Refactor Workshop](https://aws.amazon.com/transform/)。

## 经验教训

当您在实践中应用这种方法时，以下是可以塑造您的方法的关键经验教训：

- **人机交互验证对于转换质量至关重要。** Amazon Bedrock 和 Kiro IDE 可以帮助改进业务规则识别，但 AI 生成的文档应始终被视为草稿。 SME 审查在每个关键阶段都至关重要，而不仅仅是在提取过程中，以捕获人工智能工具可能忽略的特定领域逻辑、边缘案例和业务背景。与没有结构化检查点的自动转换相比，这种人工监督有助于减少部署后缺陷。
- **中间 COBOL 步骤可降低风险。** 您会发现每个阶段都有验证检查点的多阶段方法（汇编器到 COBOL 到 Java）比尝试直接转换更可靠。中间步骤可帮助您在提交最终的 Java 转换之前验证业务逻辑的保留。
- **规范驱动的方法可以帮助您防止返工。** 在代码转换之前创建详细的功能规范可以尽早​​发现误解。通过结构化 JSON 规范，您还可以自动进行验证并与转换工具直接集成。
- **增量验证可帮助您加快整体时间表。** 在每个转换阶段之后进行测试，而不是等到最后，可以帮助您及早发现问题并减少整体返工。每个阶段的质量门有助于确认输出已为下一阶段做好准备。

## 结论和后续步骤

在这篇文章中，我们介绍了一种基于 AI 的系统方法，将传统大型机 Assembler 应用程序转换为为 AWS 上的云构建的 Java 应用程序。此方法结合了用于智能业务逻辑提取的 Amazon Bedrock 和 Kiro IDE 以及用于自动 COBOL 到 Java 转换的 AWS Transform。通过遵循在每个阶段都设有验证检查点的多阶段方法，您可以帮助加快现代化时间表，同时保持关键业务逻辑的完整性。

要评估完整的服务环境并了解组件如何组合在一起，请从 [AWS 大型机现代化文档](https://aws.amazon.com/mainframe-modernization/) 开始。当您准备好查看正在运行的管道时，[AWS Transform Refactor Workshop](https://catalog.workshops.aws/awstransformrefactor/en-US/100-introduction) 将引导您完成端到端流程，并提供可在您自己的环境中运行的示例工作负载。如果您想讨论此方法如何应用于您的特定环境，请[联系 AWS 代表](https://aws.amazon.com/contact-us/)。

告诉我们您的现代化之旅，并在评论中分享您的想法。

## 关于作者
