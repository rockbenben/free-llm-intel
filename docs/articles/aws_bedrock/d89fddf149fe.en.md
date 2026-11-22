---
vendor: aws_bedrock
title: Modernizing mainframe Assembler to Java using Amazon Bedrock and AWS Transform
original_title: Modernizing mainframe Assembler to Java using Amazon Bedrock and AWS Transform
url: https://aws.amazon.com/blogs/machine-learning/modernizing-mainframe-assembler-to-java-using-amazon-bedrock-and-aws-transform
date: 2026-11-16
lang: en
captured: 2026-11-17
extractor: readability-v1
status: ok
body_sha: 3e03798593bd
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# Modernizing mainframe Assembler to Java using Amazon Bedrock and AWS Transform

Imagine a batch job that has run every night for decades without failing, and the only person who understands its code is about to retire. We have seen this situation again and again while working with banking, insurance, and airline customers. Their Assembler programs still run critical business operations, but fewer people can read them each year. Rewriting them by hand takes years, risks breaking business rules nobody remembers writing, and still depends on the same experts who are leaving. [Amazon Bedrock](https://aws.amazon.com/bedrock/) and [AWS Transform](https://aws.amazon.com/transform/) change that equation.

This post shows you a multi-stage transformation methodology using [Amazon Bedrock](https://aws.amazon.com/bedrock/), [Kiro IDE](https://kiro.dev/) (an AI-powered integrated development environment), and [AWS Transform](https://aws.amazon.com/transform/) that can help reduce modernization time compared to manual approaches while maintaining business logic integrity through validation checkpoints. You will learn how to systematically extract business rules from Assembler code, convert them through an intermediate COBOL stage, and deploy modernized applications as Java Spring Boot services on AWS.

## Prerequisites

Before starting the modernization process, make sure you have:

- Active [AWS account](https://aws.amazon.com/account/) with least-privilege AWS Identity and Access Management (IAM) permissions for Amazon Bedrock, AWS Transform, and Amazon Simple Storage Service (Amazon S3).
- Access to [Amazon Q Developer](https://aws.amazon.com/q/developer/) or [Kiro](https://kiro.dev/) for AI-assisted code analysis.
- Access to AWS Transform for COBOL to Java conversion.
- Access to Amazon Bedrock with appropriate foundation models (FMs).
- An [Amazon S3](https://aws.amazon.com/s3/) bucket configured for source code and artifact storage, with encryption and Block Public Access enabled.
- Knowledge of the target business domain and application functionality.
- Availability of business and technical subject matter experts (SMEs) for validation sessions.
- Source Assembler code inventory with available documentation.
- Test data sets with expected outputs for functional equivalence testing.

## Solution overview

You can transform legacy mainframe Assembler applications tightly bounded with COBOL into Java Spring Boot applications built for the AWS cloud through a systematic five-phase approach. This multi-stage methodology, converting Assembler to COBOL as an intermediate step before Java transformation, reduces risk and preserves business logic with greater reliability than direct Assembler-to-Java conversion. The intermediate COBOL stage provides a structured, human-readable format that subject matter experts (SMEs) can validate before final transformation. This makes sure that business rules remain intact throughout the modernization journey. The following sections describe both the current mainframe architecture and the target cloud-focused state.

### Current state

Your current architecture represents a traditional mainframe environment where Assembler programs execute batch processes, connected with COBOL, interact with databases, and process files. At its core, JCL (Job Control Language) jobs trigger Assembler program execution at scheduled intervals. These programs read input from VSAM (Virtual Storage Access Method) and sequential files and perform operations against IBM Db2 for z/OS. Your business logic executes using low-level register operations (direct CPU register manipulation) and memory management. Output is written back to files or database tables, and job completion status is reported through JCL return codes. All of this runs on IBM z/OS mainframe infrastructure.

![Mainframe architecture with JCL-triggered Assembler batch programs accessing VSAM files and IBM Db2 for z/OS](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/10/ML-20283-1-1.png)

Figure 1: Mainframe Assembler architecture

### Target state

The modernization solution helps you transform legacy mainframe Assembler applications into Java applications built for the AWS cloud through a multi-phase, AI-powered workflow. The architecture uses Amazon Bedrock and Kiro IDE for AI-assisted code analysis and business rule extraction, and AWS Transform for automated COBOL-to-Java conversion.

If COBOL source code is already available, you follow the conventional approach and provide it directly to AWS Transform for conversion to Java Spring Boot applications.

**With this solution, you can achieve:**

- Reduced transformation time compared to manual approaches.
- Systematic business logic preservation through validation checkpoints.
- Human-in-the-loop validation at critical stages.
- Automated code conversion with functional equivalence testing.

![End-to-end AWS workflow transforming Assembler to Java through five phases, from business rules extraction to COBOL-to-Java](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/10/ML-20283-2-1.png)

Figure 2: End-to-end Assembler-to-Java transformation architecture on AWS, showing five main phases: business rules extraction, spec-driven data flow, Assembler-to-COBOL conversion, validation, and COBOL-to-Java transformation

You begin the transformation workflow by analyzing Assembler code to generate Business Rules Extraction (BRE) documentation. You then create detailed functional specifications with human-in-the-loop refinement. The validated specifications guide the Assembler-to-COBOL conversion, generating intermediate COBOL code that bridges the gap between low-level hardware instructions and business-oriented constructs. This COBOL code undergoes functional equivalence testing before AWS Transform converts it to Java, with validation checkpoints at each phase to reduce risk and verify business continuity.

## Business rules extraction with AI

The quality of your Business Rules Extraction (BRE) directly impacts transformation accuracy, so focus carefully on this phase. Use Amazon Bedrock, through Kiro IDE or the Amazon Bedrock console, along with AWS Transform for mainframe to extract and document business rules from your Assembler source code.

You can use the prompts in this post directly in Amazon Bedrock through the [Chat Playground](https://docs.aws.amazon.com/bedrock/latest/userguide/playgrounds.html), or within Kiro IDE using its built-in [AI chat and Spec panel](https://kiro.dev/docs). Replace the placeholder values with your actual Assembler code and context before running.

Amazon Bedrock is the inference platform behind the first four phases: business rules extraction, specification creation, Assembler-to-COBOL conversion, and validation. Choose a foundation model with strong code reasoning and a large context window, because Assembler programs are long and dense. Set the temperature to 0 so you get consistent output across runs. To process many programs, call the same prompts through the Amazon Bedrock Converse API and store each output in your Amazon S3 bucket so it can feed the next phase. Amazon Bedrock doesn’t use your prompts or model outputs to train AWS models or share them with third parties. For details, see [Data protection in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html). Use sanitized test data instead of production data or personally identifiable information (PII).

The more context you provide to the AI, the better it understands the business intent behind the code. Include relevant documentation, data dictionaries, and available business context alongside the Assembler code when prompting.

**Note:** Save the output of each prompt as you go. You will need them as inputs in the next phase.

Example prompt for context-aware analysis:

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

You can customize this prompt by adding domain-specific terminology from your business context. When you run this prompt, you will see structured JSON output that you can use for automated validation and direct integration with downstream transformation tools. Data mapping accuracy directly affects conversion quality. Incomplete mappings can lead to lost or corrupted business logic.

## Validate with SMEs

Treat AI-generated BRE documents as drafts, not final outputs. Have subject matter experts review and validate the extracted rules before moving forward. Document discrepancies in a validation log and update the BRE based on SME feedback before proceeding to specification creation.

To help SMEs validate the rules, supplement textual BRE documents with visual aids like flowcharts and data flow diagrams. Maintain a validation checklist covering business rule accuracy, data mapping correctness, edge case handling, and error condition completeness.

## Extracting spec-driven data flow

After you validate business rules with SMEs, translate them into detailed functional specifications that will guide code conversion. This spec-driven approach confirms that business requirements are clearly documented and agreed upon before code transformation begins, reducing costly rework later.

Use the extracted BRE documents to create complete functional specifications that guide COBOL code generation. These specifications should include program overview, COBOL data structures, process flow design, and business rules coverage mapping.

Example prompt for functional specification generation:

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

You can adjust the data structure specifications based on your COBOL standards. When you run this prompt, you will receive a complete functional specification with full traceability from business rules to COBOL structures, ready for SME review and direct integration with Kiro for code generation.

## Converting legacy Assembler to COBOL

With validated functional specifications in hand, the next phase uses these structured outputs to guide the Assembler-to-COBOL conversion. The intermediate COBOL step helps you bridge the gap between low-level hardware instructions and business-oriented constructs, which helps you verify that business logic is preserved before the final Java transformation.

Example prompt to guide the conversion:

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

You can modify the formatting requirements to match your organization’s COBOL standards. When you run this prompt, you will generate COBOL code designed to be syntactically correct, logically equivalent to the original Assembler, and fully traceable, with comments linking each code section back to specific business rules from the BRE document. Once generated, rigorously validate the COBOL code before proceeding to the final Java transformation.

## Validating the transformation

You should treat testing as an ongoing activity throughout the transformation process, not only a final phase. Your functional equivalence validation between Assembler and COBOL code should employ a comprehensive testing framework that systematically evaluates syntax correctness, structural alignment, logic equivalence, data flow integrity, business rules coverage, and specification compliance.

Example prompt to guide the testing:

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

You can customize the validation thresholds based on your quality requirements. When you run this prompt, you will receive a comprehensive validation report with actionable recommendations for addressing gaps in program structure, conditional logic, data transformations, and traceability between the original Assembler instructions and the modernized COBOL implementation.

## COBOL to Java transformation

In the final phase, you use [AWS Transform](https://aws.amazon.com/transform/) to automatically convert validated COBOL code into Java Spring Boot applications. Generate production-ready Java code with the intelligent refactoring in AWS Transform. This refactoring preserves the business logic validated in previous phases while introducing modern design patterns, including dependency injection, repository patterns, and service layers.

You can deploy the resulting Java applications on AWS infrastructure to achieve cloud scalability and resilience while maintaining the same business functionality as your legacy mainframe systems. This cloud-focused approach replaces monolithic mainframe architecture with modular, maintainable code that can be independently deployed, monitored, and enhanced.

For detailed step-by-step instructions, refer to the [AWS Transform Refactor Workshop](https://aws.amazon.com/transform/).

## Lessons learned

When you apply this methodology in practice, here are the key lessons that can shape your approach:

- **Human-in-the-loop validation is essential for transformation quality.** Amazon Bedrock and Kiro IDE can help improve business rule identification, but AI-generated documents should always be treated as drafts. SME review is essential at every critical stage, not only during extraction, to catch domain-specific logic, edge cases, and business context that AI tools may overlook. This human oversight can help reduce post-deployment defects compared to automated conversion without structured checkpoints.
- **The intermediate COBOL step reduces risk.** You will find the multi-stage approach (Assembler to COBOL to Java) with validation checkpoints at each phase more reliable than attempting direct conversion. The intermediate step helps you verify business logic preservation before committing to the final Java transformation.
- **A spec-driven methodology helps you prevent rework.** Creating detailed functional specifications before code conversion catches misunderstandings early. With structured JSON specifications, you can also automate validation and direct integration with transformation tools.
- **Incremental validation helps you accelerate your overall timeline.** Testing after each transformation stage, rather than waiting until the end, helps you detect issues early and reduces overall rework. Quality gates at each phase help confirm the output is ready for the next stage.

## Conclusion and next steps

In this post, we walked through a systematic, AI-powered approach to transform legacy mainframe Assembler applications into Java applications built for the cloud on AWS. This approach combines Amazon Bedrock and Kiro IDE for intelligent business logic extraction with AWS Transform for automated COBOL-to-Java conversion. By following a multi-stage methodology with validation checkpoints at each phase, you can help accelerate modernization timelines while preserving critical business logic integrity.

To evaluate the full service landscape and understand how the components fit together, start with the [AWS Mainframe Modernization documentation](https://aws.amazon.com/mainframe-modernization/). When you’re ready to see the pipeline in action, the [AWS Transform Refactor Workshop](https://catalog.workshops.aws/awstransformrefactor/en-US/100-introduction) walks you through the end-to-end process with sample workloads you can run in your own environment. If you’d like to discuss how this approach applies to your specific environment, [contact an AWS representative](https://aws.amazon.com/contact-us/).

Tell us about your modernization journey and share your thoughts in the comments.

## About the authors
