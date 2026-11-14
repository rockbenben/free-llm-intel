---
vendor: huggingface
title: 使用 SimReady Assets 构建机器人拾放模拟
original_title: 
url: https://huggingface.co/blog/nvidia/simready-assets-robot-pick-and-place
date: 2026-11-13
lang: zh
captured: 2026-11-14
extractor: readability-v1
translator: mt
status: translated
body_sha: b920b22ca158
---

[返回文章](https://huggingface.co/blog)

# 使用 SimReady Assets 构建机器人拾放模拟

企业+文章

发布于 2026 年 11 月 13 日

14

- [![](https://huggingface.co/avatars/9f55e9f6faf6a311cccd0c08d0427db5.svg)](https://huggingface.co/ByteSage404)
- [![](https://huggingface.co/avatars/55b482d76fb0269a3e3a1838049b459f.svg)](https://huggingface.co/pomilee)
- [![](https://huggingface.co/avatars/ec3d8d16e74f37584636ad4822d24f26.svg)](https://huggingface.co/jkosnik)
- [![](https://cdn-avatars.huggingface.co/v1/product/uploads/no-auth/oSUZPwq6TTEGqIPc62BVo.png)](https://huggingface.co/AiWinstone)
- [![](https://huggingface.co/avatars/7b54d53f6c5d49197fd5399e19dc7b6b.svg)](https://huggingface.co/pipwnz)
- [![](https://cdn-avatars.huggingface.co/v1/product/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)

[![Dillon Bailey 的头像](https://huggingface.co/avatars/ef260ce572881087d516bcf632928740.svg)](https://huggingface.co/dillonb-nv)

狄龙·贝利

狄龙B-NV

[![NVIDIA 头像](https://cdn-avatars.huggingface.co/v1/product/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)](https://huggingface.co/nvidia) [nvidia](https://huggingface.co/nvidia)

[![Pomi Lee 的头像](https://huggingface.co/avatars/55b482d76fb0269a3e3a1838049b459f.svg)](https://huggingface.co/pomilee)

波米·李

波米莱

[![NVIDIA 头像](https://cdn-avatars.huggingface.co/v1/product/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)](https://huggingface.co/nvidia) [nvidia](https://huggingface.co/nvidia)

[![Rishabh Chadha 的头像](https://cdn-avatars.huggingface.co/v1/product/uploads/no-auth/kaRxLMenXEARG7KGBZJUh.png)](https://huggingface.co/rchadha-nv)

里沙卜·查达

查达-NV

[![NVIDIA 头像](https://cdn-avatars.huggingface.co/v1/product/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)](https://huggingface.co/nvidia) [nvidia](https://huggingface.co/nvidia)

[![figure-01-pick-and-place-highlight](https://cdn-uploads.huggingface.co/product/uploads/6abfe9e7d7cf09a9b38ef308/NlngGWI KZEQ8kuWKZtoyM.gif)](https://cdn-uploads.huggingface.co/product/uploads/6abfe9e7d7cf09a9b38ef308/NlngGWIKZEQ8kuWKZtoyM.gif)

本演练展示了使用 [UR17G臂]（https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/simready_usd/ur17g_1300.usda），[Robotiq 2F-140抓手]（https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/9c6b0cedf0066efd474b3bf473e7eaf7ae7e569f/Robotiq_2F_85/simready_usd/Robotiq_2F_85.usda）和[饮料can](https://huggingface.co/datasets/nvidia/simready-assets/blob/653d91e182011f357cf1644013cc94ddf194d349/food_beverage_can_n01/simready_usd/sm_food_beverage_can_n01_01.usd) 在 Isaac Sim 中构建场景，检查它们的行为，并使用代理生成的控件运行拾取和放置示例。

对于机器人工作流程，SimReady 意味着已准备好 OpenUSD 资产，并具有定义的模拟用例所需的属性，例如碰撞、质量、关节和关节驱动器。 [SimReady Central](https://huggingface.co/spaces/nvidia/simready-central) 是 Hugging Face 上的一个开放资产库，可让您通过编写的模拟属性和配置文件验证证据重复使用机器人和对象资产。有关该库及其发布的更多信息，请阅读[公告博客](https://huggingface.co/blog/nvidia/simready-central-assets-robotics-ai-factories)。

## 是什么让机器人资产 SimReady 成为可能？

[SimReady Foundation](https://nvidia.github.io/simready-foundation/) 定义了 OpenUSD 资产模拟用例所需的功能。其规格连接三个层面：

- 配置文件：用例的一组特征，例如机器人身体。
- 功能：用例所需的功能，例如可以控制的关节。
- 要求：检查每个功能所需的设置，例如关节的驱动设置。

对于此任务，这些属性包括手臂和夹具的关节以及饮料罐资产的碰撞和质量。验证根据配置文件的要求检查这些设置。然后，模拟测试组装好的机器人是否可以使用它们来拾取和移动罐子。

## 资产附带什么，您添加了什么？

[UR17G](https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/simready_usd/ur17g_1300.usda)，[Robotiq 2F-140](https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/9c6b0cedf0066efd474b3bf473e7eaf7ae7e569f/Robotiq_2F_85/simready_usd/Robotiq_2F_85.usda)和[饮料can](https://huggingface.co/datasets/nvidia/simready-assets/blob/653d91e182011f357cf1644013cc94ddf194d349/food_beverage_can_n01/simready_usd/sm_food_beverage_can_n01_01.usd)包包含模型及其模拟设置。您组装场景并添加任务代码来定义手臂-夹具组件、工作表面、起始位置以及用于移动手臂和打开和关闭夹具的控件。

[！[图2](https://cdn-uploads.huggingface.co/product/uploads/6abfe9e7d7cf09a9b38ef308/J7YL_C3mUh7MWUNJ_pVtN.png )](https://cdn-uploads.huggingface.co/product/uploads/6abfe9e7d7cf09a9b38ef308/J7YL_C3mUh7MWUNJ_pVtN.png)

*图 2.SimReady Central 提供资产模型和模拟设置，示例场景和控件定义拾放任务。*

## 在运行拾放任务之前应该检查什么？

机器人在 Isaac Sim 中静止时看起来可能看起来正确，但在模拟运行时会错误地移动或与对象交互。在运行拾放之前，测试其接头、运动和接触行为。您可以要求代理执行这些测试或在 Isaac Sim 中手动执行这些测试。

- **关节设置：** 检查手臂和夹具的关节限制和驱动设置。
- **运动：** 测试小臂运动并打开和关闭夹具。
- **接触：** 确认罐子放在工作表面上而不会掉落。

在拾取和放置过程中，观察当手臂移动时饮料是否可以留在夹具中。资源结构各不相同，因此请使用加载场景中的设置作为起点。我们将在下面的步骤中完成下载资源和构建场景的整个过程。

## 在 Isaac Sim 中构建拾放模拟

此示例结合了 [UR17G](https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/simready_usd/ur17g_1300.usda) 手臂、[Robotiq 2F-140](https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/9c6b0cedf0066efd474b3bf473e7eaf7ae7e569f/Robotiq_2F_85/simready_usd/Robotiq_2F_85.usda) 夹具和[饮料可以](https://huggingface.co/datasets/nvidia/simready-assets/blob/653d91e182011f357cf1644013cc94ddf194d349/food_beverage_can_n01/simready_usd/sm_food_beverage_can_n01_01.usd)在艾萨克·西姆。任务是抓住罐子，举起它，将其移动到目标，然后释放它。您还可以利用 [SimReady Central Space](http://nvidia-simready-central.hf.space) 搜索服务端点来查找 OEM 策划的内容。

我们还将使用前沿 AI 模型来帮助在开放的 Isaac Sim 场景中创建和运行任务代码。在此示例中，我们使用 GPT-6 Sol，但如果另一个代理和模型组合可以加载所需的技能并针对 Isaac Sim 执行 Python（生成的代码和结果可能会有所不同），则它也可能有效。提示提供了一个起点。在调整任务之前检查生成的代码并检查结果行为。

**所需软件：**

- 安装本示例使用的版本 [Isaac Sim](https://docs.isaacsim.omniverse.nvidia.com/latest/introduction/quickstart_index.html) 6.2，并检查其系统要求。
- 设置您选择的可以使用艾萨克·西姆技能的特工。按照 [代理技能文档](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/development_tools/agent_skills.html) 为您的代理提供捆绑技能。
- 仅当您选择命令行资源下载选项时才安装 [Hugging Face CLI](https://huggingface.co/docs/huggingface_hub/guides/cli)。
- 使用[美元搜索端点](http://nvidia-simready-central.hf.space)。

## 第 1 步：下载机器人手臂、夹具和饮料罐资产

打开[SimReady Central](https://huggingface.co/spaces/nvidia/simready-central)并找到[UR17G](https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/simready_usd/ur17g_1300.usda)手臂，[Robotiq 2F-140](https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/9c6b0cedf0066efd474b3bf473e7eaf7ae7e569f/Robotiq_2F_85/simready_usd/Robotiq_2F_85.usda) 夹具和[饮料可以](https://huggingface.co/datasets/nvidia/simready-assets/blob/653d91e182011f357cf1644013cc94ddf194d349/food_beverage_can_n01/simready_usd/sm_food_beverage_can_n01_01.usd)在这里使用。在每个资源上选择“下载”，然后使用“保存到文件夹”或提供的“Hugging Face”命令。保持所有三个完整的资产文件夹完好无损，以便 Isaac Sim 可以找到其支持文件。

使用本示例中链接的资产版本，并向您的代理提供手臂、夹具和饮料罐的本地 USD 文件路径。夹具路径示例如下所示；您的下载位置可能有所不同。
```
~/ASSETS/hf/src/simready-assets-c7fa7615/Robotiq_2F_140/simready_usd/Robotiq_2F_140.usda
```
[![figure-05-find-robotiq](https://cdn-uploads.huggingface.co/product/uploads/6abfe9e7d7cf09a9b38ef308/FSec580RNJKj0 DIXx9703.gif)](https://cdn-uploads.huggingface.co/product/uploads/6abfe9e7d7cf09a9b38ef308/FSec580RNJKj0DIXx9703.gif)

*图 3.SimReady Central 搜索和交互式预览有助于识别本示例中使用的 Robotiq 2F-140 夹具和饮料罐。*

[![figure-04-download-assets](https://cdn-uploads.huggingface.co/product/uploads/6abfe9e7d7cf09a9b38ef308/LJpqYrl3l5Qk Q2T4JJzYd.gif)](https://cdn-uploads.huggingface.co/product/uploads/6abfe9e7d7cf09a9b38ef308/LJpqYrl3l5QkQ2T4JJzYd.gif)

*图 4.饮料罐的下载选项包括将资源包保存到文件夹或使用 Hugging Face CLI。*

## 资产验证告诉您什么？

[arm验证报告](https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/.metadata/ur17g_1300_validation.json)使用Robot-Body 4.0.0配置文件[抓取器验证报告](https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/c7fa7615a353ebac03990208cbc2aa57426f4c48/Robotiq_2F_140/.metadata/Robotiq_2F_140_validation.json)使用Robot-Gripper 3.0.0。两者都记录通过了 [PhysX 驱动关节检查](https://nvidia.github.io/simready-foundation/latest/features/FET_022_PHYSX.html)，该检查检查关节驱动设置。

SimReady 配置文件验证为重用这些资产提供了共享基线。然后，拾取和放置运行测试手臂、夹具、罐头和控制器在组装场景中如何协同工作。

## 步骤 2：组装机器人并构建拾放场景

下载资产后，使用具有 Isaac Sim 技能的代理来帮助组装机器人、运行验证工具并创建拾取和放置控件。您还可以使用链接的文档手动执行这些步骤。

从安装目录启动 Isaac Sim，并启用远程 Python 服务器，以便代理可以通过 Python 与模拟进行交互：
```
./isaac-sim.sh --enable isaacsim.code_editor.python_server
```
如果您使用代理，请确保从 Isaac Sim 目录启动它，以便它可以在执行以下步骤时访问所需的技能。

确认所有三个资产均显示且没有丢失文件错误。要求代理检查手臂和夹具的关节限制和驱动设置，或自己在 Isaac Sim 中检查它们。机器人和夹具包含物理关节，也可以在 Isaac Sim GUI 中进行测试和验证。接下来我们将组装手臂和夹具，以便我们可以将组装作为单个关节进行控制。

您可以按照[机器人组装器教程](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/robot_setup/assemble_robots.html)进行手动组装。在这里，我们将要求我们的代理完成组装并为我们验证：

**本例中使用的示例提示：**
```
Assemble the robot arm <local path to Simready ur17g robot usd>
with the gripper <local path to downloded simready Robotiq_2F_140 gripper usd>
using the Robot Assembly tutorial in Isaac Sim
https://docs.isaacsim.omniverse.nvidia.com/6.2.0/robot_setup/assemble_robots.html.

Validate the assembly on completion.
```
代理最终使用 Isaac Sim 附带的“isaac-sim-remote”和“usd-articulation”技能来完成组装并验证机器人的物理特性。我们现在拥有运行拾取和放置所需的所有资产；组装好的机器人和汽水罐。我们现在将继续工作流程的最后部分。

[![figure-05-joint-settings](https://cdn-uploads.huggingface.co/product/uploads/6abfe9e7d7cf09a9b38ef308/NcKj9Cbp2iBl Xh65rUf0T.gif)](https://cdn-uploads.huggingface.co/product/uploads/6abfe9e7d7cf09a9b38ef308/NcKj9Cbp2iBlXh65rUf0T.gif)

*图 5. Isaac Sim 中 UR17G 手臂和 Robotiq 2F-140 夹具的关节设置。*

组装好的机器人并可以在场景中，要求代理运行任务。使用下一步中的检查来评估模拟行为。

## 步骤 3：测试控件并运行拾放

现在资产包括模拟属性和配置文件验证，我们现在可以在组装的场景和控制器中进行测试。控制器协调 UR17G 手臂的运动与 Robotiq 2F-140 夹具的打开和关闭。使用下面的行为检查来评估代理生成的任务。要自行了解或调整控制器，请参阅[添加机械手机器人教程](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/core_api_tutorials/tutorial_core_adding_manipulator.html)。

**本例中使用的示例提示：**
```
Run pick and place with the assembled robot and soda can
<path to soda can USD from SimReady library> in Isaac Sim.

Ensure you do a contact based grasp for picking up the can and validate
the accuracy/placement error for the pick and place as well.
```
**使用的技能**：“isaac-sim-remote”、“manipulaiton-ik”和“physical-simulation”

完整的任务测试夹具是否在移动过程中握住罐子并将其释放到目标处。重置场景，然后运行接近、抓取、举起、保持、转移和释放序列。将您的跑步与开场视频和下面的成功标准进行比较。

[![figure-06-pick-and-place-landscape](https://cdn-uploads.huggingface.co/product/uploads/6abfe9e7d7cf09a9b38ef308/TBsKTac lDU8oJvkXYCie8.gif)](https://cdn-uploads.huggingface.co/product/uploads/6abfe9e7d7cf09a9b38ef308/TBsKTaclDU8oJvkXYCie8.gif)

*图 6.UR17G 手臂和 Robotiq 2F-140 夹具将饮料罐从黄色拾取标记移动到 Isaac Sim 中的绿色目标。以 4 倍速度显示。*

如果您的运行有所不同，请记下序列失败的位置，并要求代理检查场景并生成控件。在重试之前将罐子和机器人重置为相同的起始状态，以便您可以比较结果。

**模拟假设：**

- **固定设置：** 罐头从已知位置开始，配有锚定机器人和清晰、平坦的工作空间。没有使用视觉，碰撞检查也受到限制。
- **简化可以：** 未对变形和液体运动进行建模，因此此示例不测试破碎。
- **脚本化抓取和运动：** 水平抓取使用通过模拟测试选择的 2 N·m 驱动力上限，未根据指尖力进行校准或由制造商推荐。当手臂遵循固定路径点而无需重新规划时，接触和摩擦力固定饮料罐。有关硬件夹持力规格，请参阅 [Robotiq 产品表](https://robotiq.com/hubfs/Product-sheets/Adaptive%20Grippers/Product-sheet-Adaptive-Grippers-EN.pdf)。

这些结果适用于此脚本设置。它们无法对不确定的物体位置、不同的有效负载或真实硬件建立鲁棒性。

## 使用 SimReady Assets 构建您的下一个模拟

使用 [SimReady Central](https://huggingface.co/spaces/nvidia/simready-central) 中的资源构建您自己的拾取和放置任务，然后使用您选择的代理来帮助组装场景并在 Isaac Sim 中运行它。

**发现资产**

- **查找机器人和物体：** 在 Hugging Face 上浏览 [SimReady Central](https://huggingface.co/spaces/nvidia/simready-central)。
- **检查资产支持的内容：** 查看 [SimReady Foundation](https://nvidia.github.io/simready-foundation/latest/) 中的配置文件和要求以及资产的验证报告。

**构建拾放场景**

- **设置模拟器：** 请遵循本示例中使用的版本的 [Isaac Sim 安装指南](https://docs.isaacsim.omniverse.nvidia.com/latest/introduction/quickstart_index.html)。
- **连接您的代理：** 按照 [Isaac Sim 代理技能文档](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/development_tools/agent_skills.html) 为您的代理提供捆绑技能。
- **组装机器人：** 如果您喜欢手动连接手臂和夹具，请按照[机器人组装器教程](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/robot_setup/assemble_robots.html#assemble-robots)进行操作。

**准备并贡献内容**

- **从 CAD 开始：** 按照[为机器人创建 SimReady 资产的 5 个步骤](https://developer.nvidia.com/blog/5-steps-to-create-simready-assets-for-robotics-with-frontier-ai-models/) 准备您自己的机器人资产。
- **验证并提交资产：** 按照 [SimReady Central 提交指南](https://github.com/NVIDIA-Omniverse/simready-central/blob/main/.agents/skills/submit-simready-assets/SKILL.md) 使您的资产可供其他开发人员使用。

如需灵感，请探索 [Michael Wagner 的声控 VR 演示](https://lnkd.in/p/g3-5svW6) 或 [Maziyar Panahi 的 Microduck 模拟](https://lnkd.in/p/gnxQ3YS8)。两者都展示了开发人员如何在自己的项目中使用 SimReady 资产。

你会建造什么？在 Hugging Face 评论中分享您的场景和结果，包括您使用的资源和 Isaac Sim 版本。

快乐建设！

## 本文提到的数据集3

## 本文提到的空间1

该作者的更多内容

## *使用八个领域的 100,000 个综合业务文档评估隐私保护和实际人工智能应用*

- ![](https://cdn-avatars.huggingface.co/v1/product/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)

5

2026 年 11 月 9 日

## Nemotron-Personas-Finance-Japan：捕捉日本人口统计和金融背景的综合数据集

- ![](https://cdn-avatars.huggingface.co/v1/product/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)

19

2026 年 11 月 9 日

### 社区

通过拖入文本输入、粘贴或单击此处来上传图像、音频和视频。

点击或粘贴此处上传图像

· [注册](https://huggingface.co/join?next=%2Fblog%2Fnvidia%2Fsimready-assets-robot-pick-and-place) 或 [登录](https://huggingface.co/login?next=%2Fblog%2Fnvidia%2Fsimready-assets-robot-pick-and-place) 发表评论

14

- [![](https://huggingface.co/avatars/9f55e9f6faf6a311cccd0c08d0427db5.svg)](https://huggingface.co/ByteSage404)
- [![](https://huggingface.co/avatars/55b482d76fb0269a3e3a1838049b459f.svg)](https://huggingface.co/pomilee)
- [![](https://huggingface.co/avatars/ec3d8d16e74f37584636ad4822d24f26.svg)](https://huggingface.co/jkosnik)
- [![](https://cdn-avatars.huggingface.co/v1/product/uploads/no-auth/oSUZPwq6TTEGqIPc62BVo.png)](https://huggingface.co/AiWinstone)
- [![](https://huggingface.co/avatars/7b54d53f6c5d49197fd5399e19dc7b6b.svg)](https://huggingface.co/pipwnz)
- [![](https://cdn-avatars.huggingface.co/v1/product/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)
- [![](https://huggingface.co/avatars/6b59ac5f151b322f5261adacecce6b61.svg)](https://huggingface.co/yiucw)
- [![](https://huggingface.co/avatars/a045d5a990db610dd1f4abbcca7f1bd6.svg)](https://huggingface.co/klnadim)
- [![](https://huggingface.co/avatars/f42dac7bbb5f8a8dd315bdbe623813e6.svg)](https://huggingface.co/ExceedZhang)
- [![](https://cdn-avatars.huggingface.co/v1/product/uploads/683acf96542967b165847cff/tUHvC7omJt6mPPdyx1oSe.png)](https://huggingface.co/safikhan5834)
- [![](https://huggingface.co/avatars/604ef02c6a6eac9315df923eaf7e56b4.svg)](https://huggingface.co/Eumoren)
- [![](https://cdn-avatars.huggingface.co/v1/product/uploads/6a980914cb03264ff33c4e0c/zOqgwh5M1nCzjQGfrT0Je.jpeg)](https://huggingface.co/willemelliw)

## 本文提到的数据集3

## 本文提到的空间1
