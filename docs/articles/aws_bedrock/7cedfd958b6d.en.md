---
vendor: aws_bedrock
title: Meta ads is now available in AWS Quick
original_title: Meta ads is now available in AWS Quick
url: https://aws.amazon.com/blogs/machine-learning/meta-ads-is-now-available-in-aws-quick
date: 2026-11-21
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 61555b544cb9
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# Meta ads is now available in AWS Quick

Marketers have never had more data to act on. Take an apparel brand that advertises on Meta technologies: campaign results live in Meta Ads Manager, briefs and creative assets in shared storage, and inventory, customer lifetime value, and in-store purchases in a data lake. Analysts export reports, merge spreadsheets, and rebuild the same deck each week, and the data ages before anyone acts on it. When the team does decide what to change, someone returns to Ads Manager to update campaigns, ad sets, budgets, and audiences by hand. As a result, teams judge campaigns on metrics alone, and the path from insight to action stays slow and manual.

Today, AWS Quick added a Meta ads AI connector. The connector gives Quick access to ads Model Context Protocol (MCP) server operations. Meta ads customers can use natural language to create, manage, and analyze campaigns within Quick, while staying connected to the Meta ad management network. Marketers can complete tasks with support from AI, such as pulling insights to understand ads performance, creating product catalogs, and editing existing or creating new campaigns. Quick can also combine Meta ad management data with first- and third-party data sources to create dashboards, documents, slide decks, and automated workflows.

> “Meta ads AI connector through Quick gives our marketing teams one place to go from campaign planning to execution. It lets us act on business insights directly in our ads, without the handoffs and tool switching that slow campaigns down. With fal.ai’s image, audio, and video models in the same workflow, we’ll test more creative ideas and spend more time reaching customers.”
>         — Tina Sang, Head of Marketing at fal

## Demo: Meta ads in Quick

The video shows how to install the Meta ads connector from **Customize** > **Connectors** in AWS Quick, sign in with Facebook, and choose which Pages, Businesses, and Instagram accounts AWS Quick can access. It then runs two example prompts. One turns past campaign results into an eight-slide launch-plan deck. The other builds a dashboard comparing spend, leads, and cost per lead for two ad sets, with recommended tests to run next.

*Connecting Meta ads to Quick and running prompts for performance analysis, campaign creation, and a shareable deck*

## Example use cases and prompts

The following use cases demonstrate how Meta advertisers can use the connector with Quick, along with sample prompts.

| **Use case** | **What Quick does** | **Example prompt** |
| --- | --- | --- |
| **Plan and launch campaigns** | Drafts campaign, ad set, and ad settings from an approved brief. Flags missing budget and audience decisions. Runs a standard pre-launch check of naming, UTM tags, budget, and special ad category. | “Using Meta ads, [campaign_brief], and past results, propose a launch plan for [promotion_name]. Flag missing decisions and prepare a review deck. Do not create or change ads yet.” |
| **Analyze and share performance** | Tracks spend, CTR, and ROAS at the account, campaign, ad set, and ad level. Compares results to the media plan. Builds a weekly deck of top ads, weak ads, and next tests. Lets leaders review the deck and ask follow-up questions before meetings. | “Analyze Meta ads conversions for [campaign_name], identify the biggest changes, and recommend next tests. Put the findings in a PowerPoint I can share with my team. Do not change budgets.” |
| **Refresh creative and audiences** | Flags creative fatigue when frequency rises and CTR falls. Creates new Custom Audiences after approval. Compares the best-performing themes with competitor messaging and trends. Drafts the next creative brief with headline variants and an A/B test plan. | “Use Meta ads results, [past_briefs], and approved audience information to flag possible creative fatigue and propose new messaging and segments. Draft a creative brief and test hypotheses, without activating changes.” |
| **Measure lift and customer quality** | Helps plan a conversion lift study. Confirms eligibility and creates the study after approval. Compares lift with attributed conversions and customer value from the CRM. Presents the results, the level of uncertainty, and the budget implications. | “Help me plan a conversion lift study in Meta ads for [campaign_name]. Check eligibility, prepare the inputs for approval, and explain how study results and [customer_outcomes] could inform our next decisions.” |
| **Prepare product catalogs for catalog ads** | Builds a SKU sheet that joins catalog eligibility with stock, margin, and image status. Explains why Meta rejected items and updates product sets. Gives merchandisers one place to review rejected items. Routes items to data owners and tracks fixes. | “Use Meta ads catalog diagnostics and [product_dataset] to identify ineligible products and image issues. Build a SKU correction table and propose products for catalog ads using authorized stock and margin inputs.” |
| **Align spend with stock and profit** | Shows Meta spend next to warehouse stock and contribution margin for each product line. Models how shifting budget to high-margin, in-stock products would affect results. Runs scheduled stock checks and queues changes for approval. Applies the changes in Meta ads after approval. | “Compare Meta ads performance with [warehouse_inventory], [margin_dataset], and [media_plan]. Propose where to shift spend and when a lower ROAS target could meet our approved commercial goals. Show assumptions and do not apply changes.” |
| **Diagnose pixel, account, and delivery issues** | Triages pixel and Conversions API issues, such as drops in event volume and low Event Match Quality scores. Passes an Ads Manager error page into a troubleshooting flow. Gathers diagnostics, internal order counts, and Meta help articles into one checklist. Drafts a handoff email to engineering. | “Investigate [issue] in Meta ads for [ad_account]. Compare available diagnostics with [order_dataset], find relevant guidance, and separate confirmed errors from hypotheses. Draft a troubleshooting handoff without changing the account.” |
| **Govern spend and connect it to your data** | Routes budget increases above a set threshold to finance for approval. Tracks spend against approved budgets for each ad account. Reconciles spend exports with warehouse and finance records. Keeps budget policies, metric definitions, and spend reviews in one shared place. | “Review Meta ads spend against [budget_policy], reconcile reporting with [warehouse_dataset], and use [change_log] to document known changes. Produce an exception report and proposed review steps, without executing changes.” |

**Note:** The connector can make changes in your ad accounts. Before Quick creates a campaign, changes a budget, or runs another write action, it asks for your permission to take the action.

## Prerequisites

Before you begin, confirm that you have the following:

- Access to Quick.
- A Meta business account with access to the ad accounts you want to connect.

## Get started

[Try Quick at no additional cost for 3 months](https://quick.aws.com/sn?offer_type=meta-ads-quick-promo)

- Sign up, connect your Meta ads account, and ask your first question.
- Invite up to 10 teammates at no cost for your first 3 months.

## About the authors
