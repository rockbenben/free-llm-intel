---
vendor: openai
title: Point-E：从复杂提示词生成 3D 点云的系统
original_title: Point-E: A system for generating 3D point clouds from complex prompts
url: https://openai.com/index/point-e
date: 2021-03-04
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Point-E：从复杂提示词生成 3D 点云的系统

## 摘要

尽管近期文本条件 3D 物体生成的工作已显示出可观前景，但最先进的方法通常需要一个 GPU 数小时才能生成一个样本。这与在数秒或数分钟内即可产样的先进生成式图像模型形成鲜明对比。本文我们探索一种替代的 3D 物体生成方法，仅需在单块 GPU 上 1–2 分钟即可产出 3D 模型。我们的方法先用文生图扩散模型生成一张合成视图，再用第二个以该图像为条件的扩散模型生成 3D 点云。虽然我们的方法在样本质量上仍不及最先进水平，但采样速度加快了一到两个数量级，对某些用例而言是一种务实的权衡。我们在[此 https URL⁠（在新窗口中打开）](https://github.com/openai/point-e)发布了预训练的点云扩散模型，以及评估代码与模型。

## 作者

Alex Nichol, Heewoo Jun, Prafulla Dhariwal, Pamela Mishkin, Mark Chen
