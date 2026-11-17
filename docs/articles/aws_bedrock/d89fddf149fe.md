---
vendor: aws_bedrock
title: 使用 Amazon Bedrock 和 AWS Transform 将大型机 Assembler 现代化为 Java
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/modernizing-mainframe-assembler-to-java-using-amazon-bedrock-and-aws-transform
date: 2026-11-16
lang: zh
captured: 2026-11-17
extractor: readability-v1
translator: agent
status: translated
body_sha: ae6c8d6a8081
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 使用 Amazon Bedrock 和 AWS Transform 将大型机 Assembler 现代化为 Java

设想一个批处理作业，几十年来每晚都跑、从没出过错，而唯一看得懂它代码的人马上就要退休。在为银行、保险和航空公司客户做项目的过程中，我们一次又一次见到这种局面。他们的 Assembler 程序仍在支撑关键业务运营，但每年能读懂它们的人都在变少。手工重写要耗费数年时间，还有可能破坏那些已经没人记得当初为什么写下的业务规则，而且依然要依赖正在离开的那批专家。[Amazon Bedrock](https://aws.amazon.com/bedrock/) 和 [AWS Transform](https://aws.amazon.com/transform/) 改变了这个等式。

本文介绍一套多阶段的改造方法，使用 [Amazon Bedrock](https://aws.amazon.com/bedrock/)、[Kiro IDE](https://kiro.dev/)（一个 AI 驱动的集成开发环境）和 [AWS Transform](https://aws.amazon.com/transform/)，相比手工方式可以帮助缩短现代化时间，同时通过验证检查点保持业务逻辑完整。你将学到如何系统地从 Assembler 代码中提取业务规则，经由中间的 COBOL 阶段完成转换，并把现代化后的应用作为 Java Spring Boot 服务部署到 AWS 上。

## 先决条件

在开始现代化流程之前，请确认你已具备：

- 一个已激活的 [AWS 账号](https://aws.amazon.com/account/)，并为 Amazon Bedrock、AWS Transform 和 Amazon Simple Storage Service（Amazon S3）配置了最小权限的 AWS Identity and Access Management（IAM）权限。
- 能够使用 [Amazon Q Developer](https://aws.amazon.com/q/developer/) 或 [Kiro](https://kiro.dev/) 进行 AI 辅助的代码分析。
- 能够使用 AWS Transform 进行 COBOL 到 Java 的转换。
- 能够访问 Amazon Bedrock，并具备合适的基础模型（FM）。
- 一个 [Amazon S3](https://aws.amazon.com/s3/) 桶，用于存放源代码和产物，并已启用加密和 Block Public Access。
- 对目标业务领域和应用功能有所了解。
- 有业务与技术方面的领域专家（SME）可以参加验证会议。
- 一份 Assembler 源代码清单，以及可获得的文档。
- 带有预期输出的测试数据集，用于功能等价性测试。

## 方案概览

你可以通过一套系统化的五阶段方法，把与 COBOL 紧密耦合的传统大型机 Assembler 应用，改造成面向 AWS 云构建的 Java Spring Boot 应用。这套多阶段方法先把 Assembler 转成 COBOL 作为中间步骤，再转成 Java，相比直接从 Assembler 转 Java，风险和业务逻辑丢失的可能性都更低。中间的 COBOL 阶段提供了一种结构化、人类可读的格式，领域专家（SME）可以在最终转换之前先做验证。这样可以确保业务规则在整个现代化过程中都保持完整。下面几节会分别介绍当前的大型机架构和面向云的目标状态。

### 当前状态

你当前的架构是一个传统的大型机环境：Assembler 程序执行批处理流程，与 COBOL 相连，访问数据库并处理文件。其核心是，JCL（Job Control Language，作业控制语言）作业按计划的时间间隔触发 Assembler 程序执行。这些程序从 VSAM（Virtual Storage Access Method，虚拟存储访问方法）和顺序文件中读取输入，并针对 IBM Db2 for z/OS 执行操作。你的业务逻辑通过低层的寄存器操作（直接操作 CPU 寄存器）和内存管理来执行。输出被写回文件或数据库表，作业完成状态则通过 JCL 返回码上报。这一切都运行在 IBM z/OS 大型机基础设施上。

![JCL 触发的 Assembler 批处理程序访问 VSAM 文件和 IBM Db2 for z/OS 的大型机架构](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/10/ML-20283-1-1.png)

图 1：大型机 Assembler 架构

### 目标状态

这套现代化方案通过一条多阶段、由 AI 驱动的工作流，帮助你把自己传统的大型机 Assembler 应用改造成面向 AWS 云构建的 Java 应用。该架构使用 Amazon Bedrock 和 Kiro IDE 进行 AI 辅助的代码分析与业务规则提取，并使用 AWS Transform 完成自动化的 COBOL 到 Java 转换。

如果 COBOL 源代码已经存在，你可以走常规路径，直接把它交给 AWS Transform 转换成 Java Spring Boot 应用。

**采用这套方案，你可以获得：**

- 相比手工方式更短的转换时间。
- 通过验证检查点系统性地保住业务逻辑。
- 在关键阶段引入人在环（human-in-the-loop）的验证。
- 自动化代码转换，并配合功能等价性测试。

![通过五个阶段把 Assembler 转成 Java 的端到端 AWS 工作流，从业务规则提取一直到 COBOL 到 Java](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/10/ML-20283-2-1.png)

图 2：AWS 上端到端的 Assembler 到 Java 转换架构，展示五个主要阶段：业务规则提取、规格驱动的数据流、Assembler 到 COBOL 转换、验证，以及 COBOL 到 Java 转换

转换工作流从分析 Assembler 代码、生成业务规则提取（Business Rules Extraction，BRE）文档开始。接着你编写详细的功能规格，并由人在环做细化。经验证的规格指导 Assembler 到 COBOL 的转换，生成作为桥梁的中间 COBOL 代码，把低层硬件指令与面向业务的构造连接起来。这份 COBOL 代码要先通过功能等价性测试，再由 AWS Transform 转换成 Java；每个阶段都设有验证检查点，以降低风险并确认业务连续性。

## 用 AI 提取业务规则

业务规则提取（BRE）的质量直接决定转换的准确度，所以要把重心放在这个阶段。使用 Amazon Bedrock（通过 Kiro IDE 或 Amazon Bedrock 控制台）以及 AWS Transform for mainframe，从你的 Assembler 源代码中提取并记录业务规则。

你可以在 Amazon Bedrock 的 [Chat Playground](https://docs.aws.amazon.com/bedrock/latest/userguide/playgrounds.html) 里直接使用本文中的 prompt，也可以在 Kiro IDE 内使用其内置的 [AI chat 和 Spec 面板](https://kiro.dev/docs)。运行前，请把占位值替换成你实际的 Assembler 代码和上下文。

Amazon Bedrock 是前四个阶段背后的推理平台：业务规则提取、规格编写、Assembler 到 COBOL 转换，以及验证。请选择代码推理能力强、上下文窗口大的基础模型，因为 Assembler 程序又长又密。把 temperature 设为 0，这样多次运行能得到一致的输出。要处理大量程序时，可以通过 Amazon Bedrock Converse API 调用同一批 prompt，并把每次的输出存进你的 Amazon S3 桶，供下一阶段使用。Amazon Bedrock 不会用你的 prompt 或模型输出来训练 AWS 模型，也不会把它们分享给第三方。详情见 [Amazon Bedrock 中的数据保护](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html)。请使用脱敏的测试数据，不要用生产数据或个人可识别信息（PII）。

你提供给 AI 的上下文越多，它就越能理解代码背后的业务意图。在 prompt 里，除了 Assembler 代码，还应附上相关文档、数据字典和可获得的业务背景。

**注意：** 边跑边把每个 prompt 的输出保存下来。下一阶段会把它们当作输入。

用于上下文感知分析的示例 prompt：

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

你可以通过加入自己业务语境中的行业术语来定制这个 prompt。运行这个 prompt 时，你会看到结构化的 JSON 输出，可用于自动化校验，也可以直接对接下游的转换工具。数据映射的准确性直接影响转换质量。映射不完整可能导致业务逻辑丢失或损坏。

## 由 SME 验证

把 AI 生成的 BRE 文档当作草稿，而不是最终产物。在继续之前，请让领域专家审阅并验证提取出的规则。把发现的差异记录到验证日志中，并根据 SME 的反馈更新 BRE，然后再进入规格编写。

为了帮助 SME 验证规则，可以在文字版 BRE 文档之外补充流程图和数据流图之类的可视化材料。维护一份验证清单，覆盖业务规则准确性、数据映射正确性、边缘情况处理和错误条件完整性。

## 提取规格驱动的数据流

在你和 SME 一起验证完业务规则之后，把它们转写成详细的功能规格，用来指导代码转换。这种规格驱动的做法可以确认：在代码转换开始之前，业务需求已经被清晰地记录并达成一致，从而减少后期昂贵的返工。

使用提取出的 BRE 文档，编写完整的功能规格来指导 COBOL 代码生成。这些规格应当包含程序概览、COBOL 数据结构、流程设计，以及业务规则覆盖映射。

用于生成功能规格的示例 prompt：

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

你可以根据自己的 COBOL 规范调整数据结构部分。运行这个 prompt 时，你会得到一份完整的功能规格，从业务规则到 COBOL 结构全程可追溯，可以直接交给 SME 审阅，也可以直接与 Kiro 集成来做代码生成。

## 把传统 Assembler 转换为 COBOL

拿到经过验证的功能规格之后，下一阶段就用这些结构化输出来指导 Assembler 到 COBOL 的转换。中间的 COBOL 步骤帮助你跨越低层硬件指令与面向业务构造之间的鸿沟，从而在最终转成 Java 之前，先确认业务逻辑被完整保留。

用于指导转换的示例 prompt：

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

你可以修改格式要求，使之符合贵组织的 COBOL 规范。运行这个 prompt 时，你会生成这样的 COBOL 代码：语法正确、逻辑上与原 Assembler 等价，并且完全可追溯——注释把每一段代码都链接回 BRE 文档中具体的业务规则。生成之后，请在进入最终的 Java 转换之前严格验证这份 COBOL 代码。

## 验证转换结果

在整个转换过程中，你都应该把测试当成一项持续进行的活动，而不是只在最后阶段才做。Assembler 与 COBOL 代码之间的功能等价性验证，应当采用一套全面的测试框架，系统地评估语法正确性、结构对齐、逻辑等价、数据流完整性、业务规则覆盖，以及规格符合度。

用于指导测试的示例 prompt：

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

你可以根据自己的质量要求定制验证阈值。运行这个 prompt 时，你会得到一份全面的验证报告，其中给出可执行的建议，用来弥补程序结构、条件逻辑、数据转换，以及原始 Assembler 指令与现代化 COBOL 实现之间可追溯性方面的缺口。

## COBOL 到 Java 的转换

在最后一个阶段，你使用 [AWS Transform](https://aws.amazon.com/transform/) 把已经验证过的 COBOL 代码自动转换成 Java Spring Boot 应用。借助 AWS Transform 中的智能重构生成可上生产的 Java 代码。这种重构在保留前几个阶段验证过的业务逻辑的同时，引入现代设计模式，包括依赖注入、仓储模式和服务层。

你可以把生成的 Java 应用部署在 AWS 基础设施上，从而获得云的弹性与可扩展性，同时保持与传统大型机系统相同的业务功能。这种面向云的做法用模块化、可维护、可独立部署与监控、可持续增强的代码，取代了单体式大型机架构。

详细的分步操作说明请参阅 [AWS Transform Refactor Workshop](https://aws.amazon.com/transform/)。

## 经验教训

把这套方法用到实际项目中时，以下几条关键经验可以塑造你的做法：

- **人在环验证对转换质量至关重要。** Amazon Bedrock 和 Kiro IDE 可以帮助提升业务规则识别的效果，但 AI 生成的文档永远应当被当作草稿。每一个关键阶段都需要 SME 审阅，而不只是在提取阶段，这样才能抓住 AI 工具可能忽略的领域特定逻辑、边缘情况和业务背景。与没有结构化检查点的自动化转换相比，这种人工把关有助于减少上线后的缺陷。
- **中间的 COBOL 步骤降低风险。** 你会发现，这套多阶段方法（Assembler 到 COBOL 再到 Java）在每个阶段都设置验证检查点，比直接转换更可靠。中间步骤帮助你在最终投入 Java 转换之前确认业务逻辑被保留了下来。
- **规格驱动的方法能帮你避免返工。** 在代码转换之前编写详细的功能规格，可以尽早发现理解偏差。有了结构化的 JSON 规格，你还可以自动化校验并直接对接转换工具。
- **增量验证能帮你加快整体进度。** 在每一个转换阶段之后测试，而不是等到最后，有助于尽早发现问题并减少整体返工。每个阶段的质量门禁帮助确认输出已经可以进入下一阶段。

## 结论与后续步骤

本文介绍了一套系统化、由 AI 驱动的方法，用来把传统大型机 Assembler 应用改造成面向 AWS 云构建的 Java 应用。这套方法把用于智能业务逻辑提取的 Amazon Bedrock 和 Kiro IDE，与用于自动化 COBOL 到 Java 转换的 AWS Transform 结合起来。遵循在每个阶段都设置验证检查点的多阶段方法，你可以帮助加快现代化进度，同时保住关键业务逻辑的完整性。

要评估完整的服务全景、理解各组件如何拼在一起，请从 [AWS Mainframe Modernization 文档](https://aws.amazon.com/mainframe-modernization/)入手。当你准备好看到这条流水线实际运行时，[AWS Transform Refactor Workshop](https://catalog.workshops.aws/awstransformrefactor/en-US/100-introduction) 会带着你走完整套流程，并提供可以在自己环境中运行的示例工作负载。如果你想讨论这套方法如何适用于你的具体环境，请联系 [AWS 客户代表](https://aws.amazon.com/contact-us/)。

欢迎分享你的现代化历程，并在评论中留下你的想法。

## 关于作者
