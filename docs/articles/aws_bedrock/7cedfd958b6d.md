---
vendor: aws_bedrock
title: Meta 广告现已上线 AWS Quick
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/meta-ads-is-now-available-in-aws-quick
date: 2026-11-22
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: llm
status: translated
body_sha: 660ebce718de
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# Meta ads 现已在 AWS Quick 中可用

营销人员从未拥有过如此多的数据可供使用。以一家在 Meta 旗下产品上投放广告的服装品牌为例：广告系列结果存放在 Meta Ads Manager 中，简报和创意素材存放在共享存储中，而库存、客户终身价值和门店购买数据则存放在数据湖中。分析师导出报告、合并电子表格，每周重建同一份演示文稿，而数据在任何人采取行动之前就已过时。当团队确实决定要做出改变时，又得有人回到 Ads Manager 手动更新广告系列、广告组、预算和受众。结果是，团队仅凭指标来评判广告系列，而从洞察到行动的路径始终缓慢且依赖人工。

今天，AWS Quick 新增了 Meta ads AI connector。该 connector 让 Quick 能够访问 ads Model Context Protocol (MCP) server 的各项操作。Meta ads 客户可以在 Quick 内使用自然语言创建、管理和分析广告系列，同时保持与 Meta 广告管理网络的连接。营销人员可以在 AI 的支持下完成任务，例如拉取洞察以了解广告表现、创建产品目录，以及编辑现有广告系列或创建新广告系列。Quick 还可以将 Meta 广告管理数据与第一方和第三方数据源相结合，用于创建仪表板、文档、幻灯片和自动化工作流。

> “通过 Quick 接入的 Meta ads AI connector 让我们的营销团队能在一个地方完成从广告系列规划到执行的全过程。它让我们可以直接在广告中根据业务洞察采取行动，无需因交接和工具切换而拖慢广告系列。借助同一工作流中 fal.ai 的图像、音频和视频模型，我们将测试更多创意想法，把更多时间花在触达客户上。”
>         —— Tina Sang，fal 营销负责人

## 演示：Quick 中的 Meta ads

视频展示了如何从 AWS Quick 中的 **Customize** > **Connectors** 安装 Meta ads connector、使用 Facebook 登录，并选择 AWS Quick 可以访问哪些主页、商家和 Instagram 账户。随后运行了两个示例提示词。一个将过去的广告系列结果转化为一份八页的发布计划幻灯片。另一个构建一个仪表板，比较两个广告组的支出、线索和每条线索成本，并附上接下来建议运行的测试。

*将 Meta ads 连接到 Quick，并运行提示词以进行效果分析、广告系列创建和生成可共享的幻灯片*

## 示例用例和提示词

以下用例展示了 Meta 广告主如何将 connector 与 Quick 配合使用，并附有示例提示词。

| **用例** | **Quick 的功能** | **示例提示词** |
| --- | --- | --- |
| **规划和发布广告系列** | 根据已批准的简报起草广告系列、广告组和广告设置。标记缺失的预算和受众决策。对命名、UTM 标签、预算和特殊广告类别运行标准的发布前检查。 | “使用 Meta ads、[campaign_brief] 和过往结果，为 [promotion_name] 提出发布计划。标记缺失的决策并准备一份评审幻灯片。暂时不要创建或更改广告。” |
| **分析和分享效果** | 在账户、广告系列、广告组和广告层级跟踪支出、CTR 和 ROAS。将结果与媒体计划进行比较。构建每周幻灯片，包含表现最佳的广告、表现不佳的广告和下一步测试。让负责人在会议前查看幻灯片并提出后续问题。 | “分析 [campaign_name] 的 Meta ads 转化，找出最大的变化，并建议下一步测试。将发现整理成一份我可以与团队分享的 PowerPoint。不要更改预算。” |
| **更新创意和受众** | 当频次上升且 CTR 下降时，标记创意疲劳。在获得批准后创建新的 Custom Audiences。将表现最佳的主题与竞品信息和趋势进行比较。起草下一份创意简报，包含标题变体和 A/B 测试计划。 | “使用 Meta ads 结果、[past_briefs] 和已批准的受众信息，标记可能的创意疲劳，并提出新的信息和细分。起草创意简报和测试假设，但不要激活任何更改。” |
| **衡量提升和客户质量** | 帮助规划转化提升研究。确认资格并在获得批准后创建研究。将提升与归因转化和来自 CRM 的客户价值进行比较。呈现结果、不确定性程度和预算影响。 | “帮我为 [campaign_name] 规划一项 Meta ads 转化提升研究。检查资格，准备供审批的输入，并说明研究结果和 [customer_outcomes] 如何为我们的下一步决策提供依据。” |
| **为目录广告准备产品目录** | 构建一个 SKU 表，将目录资格与库存、利润率和图片状态关联起来。解释 Meta 拒绝商品的原因并更新商品集。为商品运营人员提供一个统一的位置来查看被拒绝的商品。将商品转交给数据负责人并跟踪修复情况。 | “使用 Meta ads 目录诊断和 [product_dataset] 识别不合格商品和图片问题。构建 SKU 修正表，并使用已授权的库存和利润率输入为目录广告推荐商品。” |
| **让支出与库存和利润保持一致** | 将 Meta 支出与仓库库存和每条产品线的贡献利润率并排展示。模拟将预算转移到高利润率、有库存的商品会如何影响结果。运行定期的库存检查并将更改排队等待审批。在获得批准后在 Meta ads 中应用更改。 | “将 Meta ads 效果与 [warehouse_inventory]、[margin_dataset] 和 [media_plan] 进行比较。提出在哪里转移支出，以及何时较低的 ROAS 目标仍能满足我们已批准的商业目标。展示假设，不要应用更改。” |
| **诊断 pixel、账户和投放问题** | 对 pixel 和 Conversions API 问题进行分诊，例如事件量下降和 Event Match Quality 分数偏低。将 Ads Manager 错误页面传入故障排查流程。将诊断信息、内部订单计数和 Meta 帮助文章汇总到一份检查清单中。起草一封给工程团队的交接邮件。 | “调查 [ad_account] 的 Meta ads 中的 [issue]。将可用的诊断信息与 [order_dataset] 进行比较，找到相关指导，并将已确认的错误与假设区分开。起草一份故障排查交接文档，不要更改账户。” |
| **治理支出并将其与你的数据连接起来** | 将超过设定阈值的预算增加转交财务审批。针对每个广告账户跟踪支出与已批准预算的对比。将支出导出与仓库和财务记录进行核对。将预算政策、指标定义和支出审查保存在一个共享位置。 | “对照 [budget_policy] 审查 Meta ads 支出，将报告与 [warehouse_dataset] 核对，并使用 [change_log] 记录已知变更。生成一份异常报告和建议的审查步骤，不要执行更改。” |

**注意：** 该 connector 可以在你的广告账户中进行更改。在 Quick 创建广告系列、更改预算或执行其他写入操作之前，它会请求你授予执行该操作的权限。

## 先决条件

在开始之前，请确认你具备以下条件：

- 有权访问 Quick。
- 拥有一个 Meta 商业账户，且有权访问你想要连接的广告账户。

## 开始使用

[免费试用 Quick 3 个月](https://quick.aws.com/sn?offer_type=meta-ads-quick-promo)

- 注册、连接你的 Meta ads 账户，并提出你的第一个问题。
- 在前 3 个月免费邀请最多 10 位队友。

## 关于作者
