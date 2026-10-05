---
vendor: aws_bedrock
title: 用 Amazon Quick Sight 层级过滤器简化仪表盘下钻
original_title: Simplify dashboard drill-down with the Amazon Quick Sight hierarchy filter
url: https://aws.amazon.com/blogs/machine-learning/simplify-dashboard-drill-down-with-the-amazon-quick-sight-hierarchy-filter
date: 2026-10-01
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

[Amazon Quick Sight](https://aws.amazon.com/quicksight/) 是一个完全托管、云原生的商业智能（BI）能力，用于构建并发布交互式仪表盘。你可以从任何设备访问这些仪表盘，并把它们嵌入到你的应用、门户和网站中。在构建仪表盘时，作者添加过滤器，让读者能把数据收窄到他们想分析的内容。但作者必须取得平衡：他们既需要足够的选项让读者自由探索数据，又不要把界面弄得杂乱或需要太多步骤才能应用过滤器。

下面的截图展示一个常见的仪表盘过滤器布局。共有六个过滤器：四个地理过滤器（Region、Sub-Region、Country 和 City），以及另两个覆盖 Segment 和 Product 维度。在许多真实世界的仪表盘中，读者遇到的过滤器甚至更多，这会显著影响整体用户体验。

图 1：一个带六个独立过滤器控件的常见仪表盘布局

## 引入层级过滤器

今天，我们宣布 Quick Sight 中的层级过滤器（hierarchy filter）。有了它，作者可以在一个紧凑的控件中提供丰富的多级过滤，减少杂乱，并在更少的步骤内把读者引导到他们需要的数据。

层级过滤器提供以下收益：

- **减少视觉杂乱：** 读者先看到一个简短的区域列表，而不是一上来就看到数百个城市。界面在每一步都保持清爽，同时可见的选项更少。
- **更少步骤、更有引导的探索：** 读者沿一条逻辑路径下钻（Region → Sub-Region → Country → City），而非扫描几十个过滤器的扁平列表。每次选择都收窄下一层，因此读者更快到达目标。
- **混搭的层级选择：** 读者可以在一个过滤器控件中组合层级的多个级别，选中一个整个国家（如日本）连同单个城市（如纽约）。   [![Amazon Quick Sight hierarchy control with Japan selected under APJ and New York City selected under United States, showing mix-and-match selection across levels](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026-09-29/ML-21595-2.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026-09-29/ML-21595-2.png) 图 2：在同一个层级控件中选中一个整个国家和单个城市
- **在不压垮用户的前提下扩展：** 你可以支持很深的层级（最多五个级别），而不添加五个独立的、挤满工具栏的过滤器控件。一个紧凑的控件处理完整的下钻路径。
- **防止读者困惑：** 读者不需要知道哪个国家属于哪个区域。层级为他们编码了那份知识，让仪表盘能自我引导。

图 3：在每一级的选择都会限定下一级的可用选项

在本文中，我们解释层级过滤器如何工作、何时该用它而非标准独立过滤器、演练配置一个，并在一个样本零售销售数据集上构建一个完整示例，展示端到端的作者和读者体验。

## 样本数据集概览

对于本演练，我们用一个带三级地理层级加几个度量的零售销售数据集。每行含一个交易订单，带以下列：

| 列 | 示例 | 角色 |
| --- | --- | --- |
| Order_ID | 1001 | 行 ID |
| Order_Date | 2026-01-12 | 日期维度（用于趋势视觉） |
| Region | EMEA | 层级 1（父） |
| Country | UK | 层级 2 |
| City | London | 层级 3（子） |
| Product_Category | Electronics | 独立维度（细分） |
| Sales | 4200 | 度量 |
| Quantity | 14 | 度量 |

该数据集覆盖三个 Region（EMEA、AMER、APAC）、八个国家和十四个城市，因此级联有足够深度而有意义。原始数据的一个样本：

图 4：零售销售数据集的一个样本

## 构建仪表盘

我们会构建一个单表仪表盘，让读者一眼看到整个级联。它含：

- **一个关键绩效指标（KPI）**，显示 **Total Sales**、**Total Units** 和 **Order Count**（每个带环比），以证明整张表对级联做出反应。
- **一张填充地图**，显示 **Sales by Country**，按收入着色。
- **一个矩形树图（treemap）**，显示 **Sales by Region → Country → City**，其嵌套的矩形在视觉上呼应过滤器层级。

图 5：添加层级过滤器之前的单表仪表盘

### 前提条件

你需要 author 访问权限来创建和管理分析和仪表盘。

### 步骤 1：添加一个过滤器并把其类型设为层级过滤器

- 在 **Filters** 窗格中，选择 **Add** 并选择要过滤的字段（例如 **Region**）。
- 选择该过滤器以打开 **Edit filter**，打开 **Filter type** 菜单，在 **ADVANCED FILTER** 下选择 **Hierarchy filter**。Quick Sight 把它描述为“Organize and present filter values in a hierarchical tree control.”

图 6：在 Edit filter 窗格中选择层级过滤器类型

### 步骤 2：添加并排列字段

一个层级过滤器是一个持有若干相关字段的单一过滤器：最多 **五个级别**（例如 Region → Subregion → Country → City → Town）。字段不必是地理的。任何父子维度都可行，如 Product Category → Product。

- 在 **FIELD HIERARCHY** 下，选择 **Add field** 添加 **Region**、**Country** 和 **City**。
- 从最宽到最细排列字段：**Region**，然后 **Country**，然后 **City**。用每个字段的 **move up** 和 **move down** 控件重排它们。顺序设定读者的下钻路径。之后重排会清除过滤器上已保存的任何选择。
- 把 **Filter condition** 设为 **Include** 并选择你的 **Null options**。
- 用窗格顶部的 **Applied to** 图标设置范围。默认是 **Only this visual**。把它切换到 **Cross-sheet (All sheets and visuals)**，让该控件过滤整个仪表盘。
- 选择 **Apply**。

图 7：添加并排列 Region、Country 和 City 字段

### 步骤 3：把控件添加到表并发布

- 从过滤器的选项菜单（**⋮**），选择 **Add to sheet**。它作为一个单独的控件出现，默认标签类似 **Hierarchy control for Region**，你可以把它钉在表顶部。
- 移除任何较早的独立 Region、Country 或 City 控件。这一个层级控件取代全部三个。
- 把分析发布为仪表盘。

图 8：已发布的仪表盘，一个单独的层级控件取代了分开的 Region、Country 和 City 过滤器

## 读者体验

现在从读者一侧来看它。层级过滤器作为一个单独的菜单控件出现。打开它揭示一个**层级**：一个 **Select all** 选项，然后每个区域作为一个可展开的节点。

**折叠态** – 控件只显示顶层（AMER、APAC、EMEA），每个带一个展开箭头。仪表盘显示全部数据。

图 9：折叠的层级控件，只显示顶层区域

**展开 EMEA** – 读者选择 **EMEA** 旁的箭头，它的国家嵌套出现在其下方（France、Germany、UK）。展开 **UK** 又揭示它的城市（London、Manchester、Edinburgh）。这些关系直接在层级中可见，因此无需事先知道地理。

图 10：展开 EMEA 然后又展开 UK，揭示嵌套的国家和城市

## 约束与考量

在构建层级过滤器时要记住几件事：

- **级别数。** 一个层级过滤器最多持有五个数据字段（级别）。
- **支持的字段类型。** 只有 **维度** 字段能作为级别添加。文本、数字维度和布尔字段都符合条件。不 offering **度量**（如 Sales 或 Quantity）。
- **重排。** 字段用 **move up** 和 **move down**（一次一个位置）重排，而非拖放。顺序定义从父到子的路径。
- **选择行为。** 在较低级别选择一个值会**自动选择其父级链**。选择一个城市会把其国家和区域标记为部分选中，因此读者始终看到其选择的完整路径。
- **Null 处理。** 一个 **Null options** 设置（例如 Exclude nulls）控制那些在某个层级字段中值为空的行是否被包含。这一设置只适用于你视觉中显示的值。它不影响空值在层级过滤器控件本身中如何呈现。
- **搜索行为。** 过滤器顶部的搜索栏只搜索最高层级中的值（例如 Region）。它不跨整个层级（如 Subregion 或 Country）搜索。

图 11：顶层搜索栏只搜索最高层级

较低级别有它们自己的搜索框，因此你仍可以在那些级别搜索值。只要某个级别含超过 10 个唯一值，一个单独的搜索框就会出现在该较低级别。

图 12：当一个级别有超过 10 个唯一值时出现一个较低级别的搜索框

如果一个层级含超过 1,000 个唯一值，则只出现一个搜索框而不显示任何值。你可以用它来查找并选择你想过滤的特定值。

图 13：当一个级别有超过 1,000 个唯一值时，只出现一个搜索框

## 结论

在本文中，我们展示了层级过滤器如何帮助 Amazon Quick Sight 作者把一组独立控件变成一个单一的、有引导的下钻。读者得到简短、相关的列表、避免自相矛盾的选择，并更高效地探索相关维度，而无需编写代码或改动底层数据。

要试用层级过滤器，打开 [Amazon Quick Sight 控制台](https://quicksight.aws.amazon.com/)，在一个你的分析中添加一个过滤器。要了解更多关于过滤的内容，参见 Amazon Quick Sight 用户指南中的[在 Amazon Quick Sight 中过滤数据](https://docs.aws.amazon.com/quick/latest/userguide/filtering.html)。有疑问，或想分享你如何使用层级过滤器？在评论中告诉我们。
