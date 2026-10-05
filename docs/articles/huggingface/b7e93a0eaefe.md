---
vendor: huggingface
title: Artificial Analysis 文生图排行榜与 Arena 上线
original_title: Launching the Artificial Analysis Text to Image Leaderboard & Arena
url: https://huggingface.co/blog/leaderboard-artificial-analysis2
date: 2024-06-06
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Artificial Analysis 文生图排行榜与 Arena 上线

在基于扩散的图像生成器问世的短短两年里，AI 图像模型已经达到近乎摄影级的质量。这些模型之间相比如何？开源方案能与其专有模型相提并论吗？

Artificial Analysis Text to Image Leaderboard 旨在用基于人类偏好的排名回答这些问题。ELO 分数来自在 Artificial Analysis Image Arena 中收集的 45,000 多份人类图像偏好投票。排行榜收录了领先的开源与专有图像模型：Midjourney 最新版本、OpenAI 的 DALL·E、Stable Diffusion、Playground 等。

[![Untitled](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/leaderboards-on-the-hub/artificial_analysis_vision_leaderboard.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/leaderboards-on-the-hub/artificial_analysis_vision_leaderboard.png)

在此查看排行榜：[https://huggingface.co/spaces/ArtificialAnalysis/Text-to-Image-Leaderboard](https://huggingface.co/spaces/ArtificialAnalysis/Text-to-Image-Leaderboard)

你也可以参与 Text to Image Arena，投满 30 票即可获得属于你的个性化模型排名！

## 方法论

长期以来，比较图像模型的质量比其他 AI 模态（如语言模型）的评估更具挑战性，很大程度上因为人们对「图像应该长什么样」的偏好存在天然差异。随着图像模型达到非常高的精度，早期的客观指标已让位于昂贵的人类偏好研究。我们的 Image Arena 采用众包方式大规模收集人类偏好数据，首次实现了关键模型之间的对比。

我们通过对所有偏好数据做回归，为每个模型计算 ELO 分数，方式与 Chatbot Arena 类似。参与者会看到一个 prompt 和两张图像，并被要求选出最贴合该 prompt 的图像。为确保评估覆盖广泛的用例，我们为每个模型生成 700 多张图像。prompt 涵盖多样的风格与类别，包括人像、人群、动物、自然、艺术等。

## 结果的初步洞察 👀

- **专有模型领先，但开源日益具有竞争力**：包括 Midjourney、Stable Diffusion 3 和 DALL·E 3 HD 在内的专有模型领跑排行榜。但一批开源模型——目前以 Playground AI v2.5 为首——正在迎头赶上，甚至超越 OpenAI 的 DALL·E 3。
- **该领域进步飞快**：图像生成模型的格局正在快速演化。就在去年，DALL·E 2 还是该领域公认的领先者。如今，在 arena 中 DALL·E 2 被选中的比例不到 25%，排名垫底之列。
- **Stable Diffusion 3 Medium 开源可能对社区产生重大影响**：Stable Diffusion 3 是当前排行榜榜首的有力竞争者，而 Stability AI 的 CTO 最近在与 AMD 的合作演讲中宣布 Stable Diffusion 3 Medium 将于 6 月 12 日开源。与 Stability AI 当前服务的完整尺寸版 Stable Diffusion 3 相比，新模型的质量可能稍逊，但它很可能是开源社区的一次重大助力。从 Stable Diffusion 1.5 和 SDXL 的经验看，社区很可能会发布大量微调版本。

## 如何参与或联系我们

想看排行榜，请前往 Hugging Face 上的这个 space：[https://huggingface.co/spaces/ArtificialAnalysis/Text-to-Image-Leaderboard](https://huggingface.co/spaces/ArtificialAnalysis/Text-to-Image-Leaderboard)

想参与排名并贡献你的偏好，请选择 "Image Arena" 标签页，选出你认为最能代表 prompt 的图像。看完 30 张图像后，选择 "Personal Leaderboard" 标签页，即可看到基于你的选择生成的个性化图像模型排名。

欲获取更新，请关注我们的 [**Twitter**](https://twitter.com/ArtificialAnlys) 和 [**LinkedIn**](https://linkedin.com/company/artificial-analysis)。（我们也在官网比较文生图模型 API 端点的速度与定价：[https://artificialanalysis.ai/text-to-image](https://artificialanalysis.ai/text-to-image)）

我们欢迎一切反馈！可以通过 Twitter 私信，或在[**我们的网站](https://artificialanalysis.ai/contact)**上通过联系表单找到我们。

## 其他图像模型质量计划

Artificial Analysis Text to Image 排行榜并非唯一的图像质量排名或众包偏好项目。我们构建排行榜的初衷是同时覆盖专有和开源模型，给出领先文生图模型对比的全貌。

其他优秀项目包括：

- [Open Parti Prompts Leaderboard](https://huggingface.co/spaces/OpenGenAI/parti-prompts-leaderboard)
- [imgsys Arena](https://huggingface.co/spaces/fal-ai/imgsys)
- [GenAI-Arena](https://huggingface.co/spaces/TIGER-Lab/GenAI-Arena)
- [Vision Arena](https://huggingface.co/spaces/WildVision/vision-arena)
