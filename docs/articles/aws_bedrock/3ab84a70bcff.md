---
vendor: aws_bedrock
title: Scale visual production using Stability AI Image Services in Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/scale-visual-production-using-stability-ai-image-services-in-amazon-bedrock
date: 2025-09-18
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: e4bcf47f5f97
---

# 在 Amazon Bedrock 中使用 Stability AI Image Services 扩展视觉内容生产

*本文与 Stability AI 的 Alex Gnibus 合作撰写。*

Stability AI Image Services 现已在 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 中提供，通过 Amazon Bedrock API 交付开箱即用的媒体编辑能力。这些图像编辑工具拓展了 Stability AI 的 Stable Diffusion 3.5 模型（SD3.5）以及 Stable Image Core 和 Ultra 模型的能力，后者已经[可在 Amazon Bedrock 中使用](https://aws.amazon.com/bedrock/stability-ai/)，并在图像生成领域树立了新的标准。

专业的创意生产流程由多个编辑步骤组成，目的是得到完全符合需要的产出。借助 Amazon Bedrock 中的 Stability AI Image Services，你可以对既有图像进行修改、增强和变换，而无需在多个系统之间跳转，也不必把文件发送给外部服务。一切都经由你已经在用的同一套 Amazon Bedrock 体验完成。对于大规模生产视觉内容的团队来说，业务影响可能立竿见影。

本文通过示例探讨这些工具如何实现精确的创意控制，从而加速专业级视觉内容的产出。

## 现已在 Amazon Bedrock 中提供的编辑工具

Stability AI Image Services 涵盖三大类别共 13 个工具：Edit、Upscale 和 Control。每个工具处理特定的编辑任务，这类任务通常需要专门的软件或人工介入。

### Edit：面向细粒度编辑步骤的进阶能力

Edit 类别中的工具让复杂的编辑任务变得更易上手、更高效。

这套工具从基础却强大的修饰工具开始。例如，Erase Object 工具可以移除图像中不需要的元素，同时智能地保持背景一致。下面的动画展示了 Erase Object 工具从产品图中移除一个人台模特，同时保留背景。该工具可以基于蒙版（mask）图像变换源图像，也可以从源图像的 alpha 通道推导出蒙版。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-1.gif)

Remove Background 工具能精确地自动分离出主体。由此可以制作干净、专业且背景一致的商品列表，也可以换上各种生活方式场景，这对电商而言是颠覆性的改变。

下面的示例展示了移除图像背景的过程，同时保留了前景中家具产品的细节。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-2.gif)

Search and Recolor 与 Search and Replace 工具针对图像中的特定元素进行修改。Search and Recolor 改变物件颜色；例如，无需重新拍摄就能展示同一件连衣裙的不同配色。在下面的示意图中，Search and Recolor 改变了家具上的色卡。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-3.gif)

Search and Replace 可以整体替换物件，适用于更新营销物料中的季节性元素或替换产品。下面是 Search and Replace 在虚拟试穿体验中的一个应用。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-4.gif)

Inpaint 工具基于蒙版图像的内容，用新内容填充或替换指定区域，从而智能地修改图像。相比之下，Outpaint 工具会生成内容，向任意方向扩展图像。与其他自动或人工扩展图像内容的尝试相比，Outpaint 工具能最大程度减少瑕疵以及原图被编辑过的痕迹。

### Upscale：将图像增强至专业品质

新增的 Stability AI Image Services 中有三个工具提供了不同的图像放大与增强思路，各自针对特定的使用场景。

Creative Upscale 工具在提升分辨率的同时加入 AI 驱动的细节增强。该工具同时提高像素数量与视觉吸引力，适合制作高冲击力的营销物料。普通的商品图通过智能补充细节和增强鲜艳度，就能变成可直接用于广告牌的图像。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-5.gif)

当保持原图完整性至关重要时，Conservative Upscale 工具提供了更细腻的做法。它在提高分辨率的同时保留原图的细节与特征。该服务可将图像放大 20 到 40 倍，输出最高 400 万像素的图像，而对原图的改动极小。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-6.gif)

这组三个工具的最后一个是 Fast Upscale。这个 Upscale 工具比前两个更快，非常适合提升压缩图像的质量，因此适用于社交媒体帖子等场景。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-7.gif)

### Control：结构与风格上的精确控制

这一类别通过三个专门工具，实现对图像结构与风格的精确操控。

Sketch 工具把草图风格的图稿转化为照片级的方案图。建筑事务所可以用它把概念图转换成逼真的可视化效果，服装品牌则可以把设计草图变成产品效果图。该工具有助于加速从最初概念到最终视觉呈现的创意生产流程。

在此示例中，Sketch 工具转换了一张建筑图纸，帮助房地产开发商在城市景观背景下设想该方案。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-8.gif)

在另一个示例中，Sketch 工具把一张人台模特图稿转换成照片级的模特照片。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-9.gif)

Structure 工具保持输入图像的结构元素，同时允许修改内容。该工具有助于在更换主体或风格的同时保留版式、构图和空间关系。创意团队可以用 Structure 工具重建场景、替换主体，或在保持取景一致的前提下渲染新角色。

下面的示例展示了 Structure 工具把一幅车间场景变换成新的场景，同时保留构图与空间关系。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-10.gif)

Style Guide 与 Style Transfer 工具帮助营销团队产出符合品牌风格与规范的图像。Style Guide 工具从一张风格参考图中提取艺术风格与色彩，并基于文本 prompt 生成新图像。

在下面的示例中，Style Guide 工具从品牌的配色方案与纹理中获取线索，生成与品牌形象一致的新图像。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-19647/ml-19647-11.gif)

Style Transfer 工具利用参考图像的视觉特征来变换既有图像，同时保留原始构图。例如，家居装饰零售商无需重新拍摄，就能把产品图像从现代极简风格转换为传统风格。营销团队可以给既有产品目录套用不同的视觉风格，从而制作季节性变体。

## 方案概览

为了演示 Amazon Bedrock 中的 Stability AI Image Services，我们用一个示例逐步走一遍，所用 Jupyter notebook 位于 [GitHub 仓库](https://github.com/aws-samples/stabilityai-sample-notebooks/tree/main/stability-ai-image-services)。

## 先决条件

若要跟随操作，你需要具备以下先决条件：

- 一个 AWS 账户。
- 已配置好用于创建和访问 Amazon Bedrock 与 [Amazon SageMaker AI](https://aws.amazon.com/sagemaker/ai/) 资源的 AWS 凭证。
- 一个用于 SageMaker AI 的 [AWS Identity and Access Management](https://aws.amazon.com/iam/)（IAM）执行角色，并已附加 `AmazonSageMakerFullAccess` 和 `AmazonBedrockLimitedAccess` 这两个 AWS 托管策略。详情请参阅[如何使用 SageMaker AI 执行角色](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html)。
- 一个 [SageMaker notebook 实例](https://docs.aws.amazon.com/sagemaker/latest/dg/nbi.html)。
- Stability AI Image Services 的模型访问权限，可通过 Amazon Bedrock 控制台申请。详情请参阅[访问 Amazon Bedrock 基础模型](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)。

## 创建 SageMaker AI notebook 实例

请完成以下步骤，创建一个可用于运行示例 notebook 的 [SageMaker AI notebook](https://aws.amazon.com/sagemaker/ai/notebooks/) 实例：

- 在 SageMaker AI 控制台的导航窗格中，于 **Applications and IDEs** 下选择 **Notebooks**。
- 选择 **Create notebook instance**。
- 在 **Notebook instance name** 中，为 notebook 实例输入名称（例如 `ai-images-notebook-instance`）。
- 在 **Notebook Instance type** 中，选择 **ml.t2.medium**。
- 在 **Platform identifier** 中，选择 **Amazon Linux 2**。
- 在 **IAM role** 中，选择一个已附加 `AmazonSageMakerFullAccess` 和 `AmazonBedrockLimitedAccess` 策略的现有 IAM 角色，或选择 **Create a new role**。
- 记下你所选 IAM 角色的名称。
- 其余设置保持默认，然后选择 **Create notebook instance**。

几分钟后，SageMaker AI 会创建好 notebook 实例，其状态从 **Pending** 变为 **InService**。

## 确认 notebook 实例的 IAM 角色具备所需权限

请完成以下步骤，验证你为 notebook 实例指定的 SageMaker AI 执行角色具有正确的权限：

- 在 IAM 控制台的导航窗格中，于 **Access management** 下选择 **Roles**。
- 在 **Roles** 搜索栏中，输入你创建 notebook 实例时所用的 SageMaker AI 执行角色名称。
- 选择该 IAM 角色。
- 在 **Permissions policies** 下，确认 `AmazonSageMakerFullAccess` 和 `AmazonBedrockLimitedAccess` 这两个 AWS 托管策略均已存在。
- （可选）如果缺少其中某个策略，选择 **Add permissions**，再选择 **Attach policies** 附加所缺策略。在 **Other permissions policies** 搜索栏中输入策略名称。选中该策略，然后选择 **Add permissions**。

## 运行 notebook

请完成以下步骤运行 notebook：

- 在 SageMaker AI 控制台的导航窗格中，于 **Applications and IDEs** 下选择 **Notebooks**。
- 选择新建的 `ai-images-notebook-instance` notebook 实例。
- 等待 notebook 进入 **InService** 状态。
- 选择 **Open JupyterLab** 链接，在新的浏览器标签页中启动 JupyterLab。
- 在 **Git** 菜单中，选择 **Clone a Repository**。
- 输入 URI `https://github.com/aws-samples/stabilityai-sample-notebooks.git`，并勾选 **Include submodules** 和 **Download the repository**。
- 选择 **Clone**。
- 在 **File** 菜单中，选择 **Open from path**。
- 输入以下内容：
`stabilityai-sample-notebooks/stability-ai-image-services/stability-ai-image-services-sample-notebook.ipynb`
- 选择 **Open**。
- 出现提示时，选择内核 `conda_python3`，然后选择 **Select**。
- 逐个运行 notebook 的每个单元格，体验 Amazon Bedrock 中的 Stability AI Image Services。

## 清理

为避免持续产生费用，请停止你在本次演练中创建的 `ai-images-notebook-instance` SageMaker AI notebook 实例：

- 在 SageMaker AI 控制台的导航窗格中，于 **Applications and IDEs** 下选择 **Notebooks**。
- 选择你创建的 `ai-images-notebook-instance` SageMaker AI notebook 实例。
- 选择 **Actions**，然后选择 **Stop**。

几分钟后，notebook 实例会从 **Stopping** 状态转为 **Stopped** 状态。

- 选择 **Actions**，然后选择 **Delete**。

几秒钟后，SageMaker AI 会删除该 notebook 实例。

详情请参阅[清理 Amazon SageMaker notebook 实例资源](https://docs.aws.amazon.com/sagemaker/latest/dg/ex1-cleanup.html)。

## 结语

[Amazon Bedrock 中的 Stability AI Image Services](https://aws.amazon.com/bedrock/stability-ai/) 的推出，是视觉内容创作与处理领域令人振奋的一步，对企业的专业创意团队而言尤其能节省时间。

例如，在媒体与娱乐行业，创作者可以快速增强场景并制作特效，营销团队可以毫不费力地生成多个营销活动变体。零售与电商企业可以简化商品摄影和数字目录的制作，游戏开发者可以更高效地为环境制作原型。建筑事务所可以即时将设计概念可视化，教育机构则可以制作更有吸引力的视觉内容。

借助这些工具，不同规模的企业都能以高效且富有创意的方式，制作专业级、极具吸引力的视觉内容。这些工具可以简化运营、降低成本，并开辟新的创意可能，帮助品牌更有效地讲述自身故事，以更具说服力的方式吸引客户。

要开始使用，请查看 [Amazon Bedrock 中的 Stability AI 模型](https://aws.amazon.com/bedrock/stability-ai/)以及 AWS Samples 的 [GitHub 仓库](https://github.com/aws-samples/stabilityai-sample-notebooks/tree/main/stability-ai-image-services)。

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/09/ml-19647-12.jpeg)Alex Gnibus** 是 Stability AI 的产品营销经理，致力于把前沿研究突破与实际用例连接起来。他的经验横跨创意机构与深入的企业技术，既带来技术专长，也理解专业创意团队可以用生成式 AI 解决哪些难题。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/09/ml-19647-13.png)Isha Dua** 是常驻旧金山湾区的资深解决方案架构师。她通过理解 AWS 企业客户的目标与挑战来帮助他们成长，指导他们以云的方式设计应用架构，并确保应用具备韧性与可扩展性。她热衷于机器学习技术和环境可持续性。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/09/ml-19647-14.png)Fabio Branco** 是 Amazon Web Services（AWS）的资深客户解决方案经理兼战略顾问，帮助客户实现业务转型、通过生成式 AI 与数据方案驱动创新，并顺利走好云上旅程。加入 AWS 之前，他曾在多家《财富》500 强企业担任产品管理、工程、咨询和技术交付等职务，涉及零售与消费品、石油与天然气、金融服务、保险以及航空航天与国防等行业。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/15/solpatel-headshot-2-100x100-1.jpg)Suleman Patel** 是 Amazon Web Services（AWS）的资深解决方案架构师，特别专注于机器学习和现代化。Suleman 兼具业务与技术专长，帮助客户设计并构建能够解决真实业务问题的方案。不投入工作时，Suleman 喜欢探索户外、自驾旅行，以及在厨房里做出美味菜肴。
