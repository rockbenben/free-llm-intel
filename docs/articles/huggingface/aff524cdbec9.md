---
vendor: huggingface
title: Hub 推出存储区域（Storage Regions）功能
original_title: Introducing Storage Regions on the HF Hub
url: https://huggingface.co/blog/regions
date: 2023-11-03
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Hub 推出存储区域（Storage Regions）功能

本文另有中文版本 [简体中文](https://huggingface.co/blog/zh/regions)。

作为 [Enterprise Hub](https://huggingface.co/enterprise) 计划的一部分，我们最近发布了 **Storage Regions（存储区域）** 支持。

区域（Regions）功能让你可以决定组织的模型和数据集存储在哪个地区。这主要有两个好处，本文将简要介绍：

- **监管与法律合规**，以及更广义上的更好数字主权
- **性能**（提升下载和上传速度及延迟）

目前我们支持以下区域：

- 美国 🇺🇸
- 欧盟 🇪🇺
- 即将上线：亚太 🌏

但首先，来看看如何在组织设置中启用这个功能 🔥

## 组织设置

如果你的组织还不是 Enterprise Hub 组织，你会看到如下界面：

[![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/no-feature.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/no-feature.png)

一旦订阅，你就可以看到 Regions 设置页面：

[![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/feature-annotated.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/feature-annotated.png)

在该页面上你可以看到：

- 一份你组织下各仓库当前位置的审计清单
- 用于选择仓库创建位置的下拉菜单

## 仓库标签

任何存储在非默认位置的仓库（模型或数据集）都会直接把所在 Region 显示为一个标签。这样，组织成员一眼就能看到各仓库的位置。

[![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/tag-on-repo.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/tag-on-repo.png)

## 监管与法律合规

在许多受监管的行业中，你可能需要将数据存储在特定区域。

对于欧盟的企业，这意味着你可以利用 Hub 以符合 GDPR 的方式构建 ML：数据集、模型和推理 endpoint 全部存储在欧盟数据中心内。

如果你是 Enterprise Hub 客户并且对此还有更多问题，欢迎随时联系我们！

## 性能

把你的模型或数据集存储在离团队和基础设施更近的地方，还意味着上传和下载性能都显著提升。

考虑到模型权重和数据集文件通常都非常大，这一点差别巨大。

[![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/upload-speed.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/upload-speed.png)

举个例子：如果你位于欧洲并把仓库存储在 EU 区域，相比存储在美国，上传和下载速度大约可以快 4—5 倍。
