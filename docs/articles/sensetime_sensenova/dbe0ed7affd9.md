---
vendor: sensetime_sensenova
title: SenseNova U1信息图增强版V2来了！小字更清晰、排版质感向专业设计师看齐
original_title: 
url: https://www.sensetime.com/cn/news/51170735
date: 2026-07-07
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: native
status: translated
body_sha: 81d524ac74fd
---

商汤日日新SenseNova U1信息图增强版上线后，得到很多创作者和开发者的积极反馈。

随着 GPT-Image-2 等新一代商业图像生成模型的出现，行业期待也在快速提高：模型不只要“画得像”，还要能处理更长文本、更复杂的版式结构，以及更稳定的图文对应关系。

基于这一技术趋势，我们对SenseNova U1信息图增强版进行了专项迭代，推出SenseNova U1信息图增强版V2（SenseNova-U1-8B-MoT-Infographic-V2），希望把这类高信息密度图像生成能力，以更开放、更轻量的 8B-MoT 模型形式持续推进，让开源模型在小字清晰度、复杂排版和视觉质感上不断向行业前沿靠近。

该模型权重已在 Hugging Face 和魔搭社区开放，相关代码、文档与示例已同步至 GitHub。

开源地址：

[https://huggingface.co/sensenova/SenseNova-U1-8B-MoT-Infographic-V2](https://huggingface.co/sensenova/SenseNova-U1-8B-MoT-Infographic-V2)

**小字清晰度和复杂版式升级
**

**回应真实创作场景**

如果说前一个版本——SenseNova U1信息图增强版（SenseNova U1-8B-MoT-Infographic）能做到的是：文字准确、图表可靠、背景稳定；

**信息图增强版V2的跨越式突破，就是让AI真正懂得如何把信息图“做得更美”**——小字更清晰，排版疏密有致，整体质感向专业设计师看齐。

以下是V2版本生成的部分信息图（可点击查看大图）：

![image.png](https://oss.sensetime.com/0e3ce200444393c091d865040f1e9834/image.png)

V2模型进行的关键升级包括：

**1、小文本更清晰，信息细节更好读**

信息图中的脚注、数据来源、表格注释、坐标轴标签及免责声明等小字，往往承载着关键的辅助信息。过去模型生成的图片边缘极易模糊、笔画粘连，导致用户需要放大数倍去“猜字”，作品也显得专业度欠缺。

V2版本显著提升了小字文本的边缘锐利度和清晰度。以下报纸版面设计的渲染图，无需反复放大，在正常阅读距离下即可对各类小字信息、数据“一目了然”。

![image.png](https://oss.sensetime.com/fc2e5d66c949e1f1c8fd845edfdb29bc/image.png)

![1049a59b893c4c89aa2dd8068729858d.png](https://oss.sensetime.com/3d460dfd2540bffb73a94f51c397fbe1/1049a59b893c4c89aa2dd8068729858d.png)

**2、驾驭复杂密集排版，自带“设计师”视觉**

当信息密度极高时，信息图的模块之间容易相互挤压，导致视觉路径混乱、阅读体验差。

V2版本将复杂密集排版与整体美观度作为核心升级方向。通过培养模型对网络结构、视觉层级和语义对应关系的深层理解，让画面排版疏密有致、条理清晰。在以下生成商业海报、游戏指南、知识图谱等场景中，图像的专业度、美观精致度和整图可用性均大幅提升。

![img_v3_0213c_e54824a0-669c-4636-b363-4517fa47d1ag.jpg](https://oss.sensetime.com/45ce41f4727c2feaef5ab0dac55f51a5/img_v3_0213c_e54824a0-669c-4636-b363-4517fa47d1ag.jpg)

**面向更多真实场景**

持续突破，专项与通用能力并重

优质的生图效果，源于信息图增强版V2在底层训练机制上的创新与重构：

**专项强化方面：**在 MT（ 中期训练）/ SFT（监督微调）阶段，我们引入更多更好的高质量合成/真实数据，并重新平衡信息图相关样本内分布以及和其他数据分布，进一步优化训练数据组成，针对小字渲染、复杂密集排版和高美观度生成能力进行了专项强训。

**视觉质感方面：**在 RL（强化学习）阶段，引入了 DPO（直接偏好优化）训练，从人类视觉审美出发，整体拉高视觉质感。

**稳定性提升方面：**在 GRPO（组相对策略优化）阶段，进一步优化了奖励配方（reward recipe），从机制上让模型能够更稳定地避免非预期暗色背景的出现。

得益于这一套组合拳，信息图增强版V2交出亮眼答卷：

**在开源模型中保持领先，并较前代显著提升：**相比旧版本，V2版本在 BizGenEval（hard/easy）困难与简单测试集上，得分从 46.6 / 65.4 跃升至 50.3 / 67.9（分别提升 +3.7 / +2.5）；在 IGenBench（Q-ACC/I-ACC）指标上，也由 69.5 / 17.0 提高到 71.4 / 18.3（分别提升 +1.9 / +1.3）

![img_v3_0213c_174ad905-8f5f-444b-9fe0-95c9456047eg.jpg](https://oss.sensetime.com/642f2f4ed1b60314aa782a3b29c9a42b/img_v3_0213c_174ad905-8f5f-444b-9fe0-95c9456047eg.jpg)

**通用生成能力保持稳定：**综合测评指标 OneIG（EN/ZH）得分为 55.4 / 53.5，与上一版基本持平，这表明V2在信息图专项能力显著提升的同时，并未明显牺牲通用生成能力。

![图片](https://mmbiz.qpic.cn/mmbiz_png/WdyVrOG9iattfcMLo9NnUugdCRD2VcQVS6jJJ6I00Mt0ibAp0fuVn3jcMh4wnTwNQ0Vlq1pcVnGBpicROlIG2z7bv9IS6897qsjDqPU6yobzHY/640?wx_fmt=png&amp;from=appmsg&amp;tp=wxpic&amp;wxfrom=5&amp;wx_lazy=1#imgIndex=10)

V2在OneIG (EN, ZH), LongText (EN, ZH), BizGenEval (Easy, Hard), CVTG and IGenBench 的综合能力表现

![图片](https://mmbiz.qpic.cn/mmbiz_png/WdyVrOG9iattXafich852IViaA4m2mUZ17n2mH6ia7ibUiaRn3FFiaDL88hbvd2gdSLJGOtd4sG7ee7I3xjN0oQgM8kc0pUwVtcdaia8TBzEqRicLicjk/640?wx_fmt=png&amp;from=appmsg&amp;tp=wxpic&amp;wxfrom=5&amp;wx_lazy=1#imgIndex=11)

信息图基准表现

目前信息图增强版V2（SenseNova-U1-8B-MoT-Infographic-V2）已面向全球用户开源。欢迎广大创作者、开发者下载体验，持续为我们提供反馈和建议。

模型权重下载地址：

[https://huggingface.co/sensenova/SenseNova-U1-8B-MoT-Infographic-V2](https://huggingface.co/sensenova/SenseNova-U1-8B-MoT-Infographic-V2)

模型文档：

[https://github.com/OpenSenseNova/SenseNova-U1/blob/main/docs/u1_infographic_model_CN.md](https://github.com/OpenSenseNova/SenseNova-U1/blob/main/docs/u1_infographic_model_CN.md)

魔搭社区下载：

[https://modelscope.cn/models/SenseNova/SenseNova-U1-8B-MoT-Infographic-V2](https://modelscope.cn/models/SenseNova/SenseNova-U1-8B-MoT-Infographic-V2)

#新闻#SenseTime

## 更多资讯

[**从大国外交现场到城市公共空间，商汤科技亮相APEC领导人会议周**2026/11/20](https://www.sensetime.com/cn/news/sensetime-apec-leaders-week-20261120-1525)[**商汤小浣熊·金融版正式推出，深化AI在金融行业的场景化应用**2026/11/19](https://www.sensetime.com/cn/news/sensetime-raccoon-finance-20261119-1522)[**SenseNova U1 Pro 获 Design Arena 双榜中国第一、全球第六**2026/11/19](https://www.sensetime.com/cn/news/sensenova-u1-pro-design-arena-20261119-1414)
