---
vendor: huggingface
title: 使用 SimReady Assets 构建机器人拾放仿真
original_title: 
url: https://huggingface.co/blog/nvidia/simready-assets-robot-pick-and-place
date: 2026-11-13
lang: zh
captured: 2026-11-14
extractor: readability-v1
translator: agent
status: translated
body_sha: 41ddacdba573
---

[ 返回文章](https://huggingface.co/blog)

# 使用 SimReady Assets 构建机器人拾放仿真

企业 + 文章

发布于 2026 年 11 月 13 日


14

- [![](https://huggingface.co/avatars/9f55e9f6faf6a311cccd0c08d0427db5.svg)](https://huggingface.co/ByteSage404)
- [![](https://huggingface.co/avatars/55b482d76fb0269a3e3a1838049b459f.svg)](https://huggingface.co/pomilee)
- [![](https://huggingface.co/avatars/ec3d8d16e74f37584636ad4822d24f26.svg)](https://huggingface.co/jkosnik)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/oSUZPwq6TTEGqIPc62BVo.png)](https://huggingface.co/AiWinstone)
- [![](https://huggingface.co/avatars/7b54d53f6c5d49197fd5399e19dc7b6b.svg)](https://huggingface.co/pipwnz)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)

[![Dillon Bailey 的头像](https://huggingface.co/avatars/ef260ce572881087d516bcf632928740.svg)](https://huggingface.co/dillonb-nv)

Dillon Bailey

dillonb-nv

[![NVIDIA 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)](https://huggingface.co/nvidia) [nvidia](https://huggingface.co/nvidia)

[![Pomi Lee 的头像](https://huggingface.co/avatars/55b482d76fb0269a3e3a1838049b459f.svg)](https://huggingface.co/pomilee)

Pomi Lee

pomilee

[![NVIDIA 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)](https://huggingface.co/nvidia) [nvidia](https://huggingface.co/nvidia)

[![Rishabh Chadha 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/kaRxLMenXEARG7KGBZJUh.png)](https://huggingface.co/rchadha-nv)

Rishabh Chadha

rchadha-nv

[![NVIDIA 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)](https://huggingface.co/nvidia) [nvidia](https://huggingface.co/nvidia)

[![figure-01-pick-and-place-highlight](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/NlngGWIKZEQ8kuWKZtoyM.gif)](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/NlngGWIKZEQ8kuWKZtoyM.gif)

这篇演练展示了一个饮料罐拾放任务：用 [UR17G 机械臂](https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/simready_usd/ur17g_1300.usda)、[Robotiq 2F-140 夹爪](https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/9c6b0cedf0066efd474b3bf473e7eaf7ae7e569f/Robotiq_2F_85/simready_usd/Robotiq_2F_85.usda)和[饮料罐](https://huggingface.co/datasets/nvidia/simready-assets/blob/653d91e182011f357cf1644013cc94ddf194d349/food_beverage_can_n01/simready_usd/sm_food_beverage_can_n01_01.usd)在 Isaac Sim 中搭建场景，检查它们的行为，并用 agent 生成的控制逻辑跑一个拾放示例。

在机器人工作流里，SimReady 指的是 [OpenUSD](https://www.nvidia.com/en-us/glossary/openusd/) 资产已经按某个明确的仿真用例配置好所需属性，例如碰撞、质量、关节和关节驱动。[SimReady Central](https://huggingface.co/spaces/nvidia/simready-central) 是 Hugging Face 上的一个开放资产库，让你复用带有编写好的仿真属性和 profile 验证证据的机器人与物体资产。想进一步了解该库及其发布，请读[公告博客](https://huggingface.co/blog/nvidia/simready-central-assets-robotics-ai-factories)。

## 机器人资产怎样才算 SimReady？

[SimReady Foundation](https://nvidia.github.io/simready-foundation/) 规定了 OpenUSD 资产在某个仿真用例下需要具备哪些特性。其规范把三个层次串起来：

- Profile：针对某个用例的一组特性，例如机器人本体。
- Features：该用例所需的能力，例如可控制的关节。
- Requirements：对每项特性所需设置的检查，例如关节的驱动设置。

对本任务而言，这些属性包括机械臂和夹爪的关节，以及饮料罐资产的碰撞与质量。验证会按 profile 的要求检查这些设置；随后仿真再测试组装好的机器人能否用它们抓起并搬动罐子。

## 资产自带什么，你又需要补什么？

[UR17G](https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/simready_usd/ur17g_1300.usda)、[Robotiq 2F-140](https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/9c6b0cedf0066efd474b3bf473e7eaf7ae7e569f/Robotiq_2F_85/simready_usd/Robotiq_2F_85.usda) 和[饮料罐](https://huggingface.co/datasets/nvidia/simready-assets/blob/653d91e182011f357cf1644013cc94ddf194d349/food_beverage_can_n01/simready_usd/sm_food_beverage_can_n01_01.usd)这三个包里带有模型及其仿真设置。你需要组装场景，再添加任务代码来定义机械臂–夹爪组合、工作表面、起始位置，以及移动机械臂、开合夹爪的控制逻辑。

[![图 2](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/J7YL_C3mUh7MWUNJ_pVtN.png)](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/J7YL_C3mUh7MWUNJ_pVtN.png)

*图 2. SimReady Central 提供资产模型与仿真设置，示例场景和控制逻辑定义拾放任务。*

## 运行拾放任务前该检查什么？

机器人在 Isaac Sim 里静止时看着可能没问题，但仿真一跑起来，移动或跟物体交互就可能出错。运行拾放之前，先测试它的关节、运动和接触行为。你可以让 agent 做这些测试，也可以在 Isaac Sim 里手动完成。

- **关节设置：** 检查机械臂与夹爪的关节限位和驱动设置。
- **运动：** 测试一次小幅机械臂移动，并开合夹爪。
- **接触：** 确认罐子稳稳放在工作面上，不会穿下去。

拾放过程中，留意机械臂移动时饮料罐是否一直留在夹爪里。资产结构各不相同，请以你已加载场景里的设置为起点。下面几步会走一遍下载资产、搭建场景的完整流程。

## 在 Isaac Sim 中搭建拾放仿真

此示例在 Isaac Sim 里把 [UR17G](https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/simready_usd/ur17g_1300.usda) 机械臂、[Robotiq 2F-140](https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/9c6b0cedf0066efd474b3bf473e7eaf7ae7e569f/Robotiq_2F_85/simready_usd/Robotiq_2F_85.usda) 夹爪和[饮料罐](https://huggingface.co/datasets/nvidia/simready-assets/blob/653d91e182011f357cf1644013cc94ddf194d349/food_beverage_can_n01/simready_usd/sm_food_beverage_can_n01_01.usd)组合起来。任务是抓住罐子、抬起、移到目标位置再松开。你也可以借助 [SimReady Central Space](http://nvidia-simready-central.hf.space) 的搜索服务端点查找 OEM 精选内容。

我们还会用一个前沿 AI 模型，帮忙在打开的 Isaac Sim 场景里编写并运行任务代码。本例用的是 GPT-6 Sol；只要别的 agent 与模型组合能加载所需 skills、并针对 Isaac Sim 执行 Python，也同样可行（生成的代码和结果可能有差异）。prompt 只是一个起点。改造任务之前，先检查生成的代码，核对实际行为。

**所需软件：**

- 安装本例所用的 [Isaac Sim](https://docs.isaacsim.omniverse.nvidia.com/latest/introduction/quickstart_index.html) 6.2，并确认其系统要求。
- 搭一个你选的、能使用 Isaac Sim skills 的 agent。按 [Agent Skills 文档](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/development_tools/agent_skills.html)把随附的 skills 提供给你的 agent。
- 只有在你选择用命令行下载资产时，才需要安装 [Hugging Face CLI](https://huggingface.co/docs/huggingface_hub/guides/cli)。
- 使用 [USD Search endpoint](http://nvidia-simready-central.hf.space)。

## 第 1 步：下载机械臂、夹爪和饮料罐资产

打开 [SimReady Central](https://huggingface.co/spaces/nvidia/simready-central) 并找到 [UR17G](https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/simready_usd/ur17g_1300.usda) 机械臂、[Robotiq 2F-140](https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/9c6b0cedf0066efd474b3bf473e7eaf7ae7e569f/Robotiq_2F_85/simready_usd/Robotiq_2F_85.usda) 夹爪和本文用到的[饮料罐](https://huggingface.co/datasets/nvidia/simready-assets/blob/653d91e182011f357cf1644013cc94ddf194d349/food_beverage_can_n01/simready_usd/sm_food_beverage_can_n01_01.usd)。在每个资产上点 Download，再用 Save to folder 或给出的 Hugging Face 命令。三个完整的资产文件夹都要保持原样，这样 Isaac Sim 才能找到它们的支撑文件。

使用本例中链接的资产版本，并把机械臂、夹爪和饮料罐的本地 USD 文件路径提供给你的 agent。下面给了一个夹爪路径示例；你的下载位置可能不同。

```
~/ASSETS/hf/src/simready-assets-c7fa7615/Robotiq_2F_140/simready_usd/Robotiq_2F_140.usda
```

[![figure-05-find-robotiq](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/FSec580RNJKj0DIXx9703.gif)](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/FSec580RNJKj0DIXx9703.gif)

*图 3. SimReady Central 的搜索与交互式预览，有助于认出本例所用的 Robotiq 2F-140 夹爪和饮料罐。*

[![figure-04-download-assets](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/LJpqYrl3l5QkQ2T4JJzYd.gif)](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/LJpqYrl3l5QkQ2T4JJzYd.gif)

*图 4. 饮料罐的下载选项包括把资产包保存到文件夹，或使用 Hugging Face CLI。*

## 资产验证能告诉你什么？

[机械臂验证报告](https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/.metadata/ur17g_1300_validation.json)用的是 Robot-Body 4.0.0 profile，[夹爪验证报告](https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/c7fa7615a353ebac03990208cbc2aa57426f4c48/Robotiq_2F_140/.metadata/Robotiq_2F_140_validation.json)用的是 Robot-Gripper 3.0.0。两份报告都记录了通过的 [PhysX 驱动关节检查](https://nvidia.github.io/simready-foundation/latest/features/FET_022_PHYSX.html)，该项检查会核对关节驱动设置。

SimReady 的 profile 验证为复用这些资产提供了共同的基线。随后的拾放运行，则测试机械臂、夹爪、罐子和控制器在组装好的场景里如何协同工作。

## 第 2 步：组装机器人并搭好拾放场景

下载资产后，让带 Isaac Sim skills 的 agent 帮你组装机器人、运行验证工具、创建拾放控制逻辑。你也可以照着相关文档手动完成这些步骤。

从安装目录启动 Isaac Sim，并启用远程 Python 服务器，让 agent 能通过 Python 与仿真交互：

```
./isaac-sim.sh --enable isaacsim.code_editor.python_server
```

如果你用 agent，请从 Isaac Sim 目录启动它，这样在下面各步骤里它才能访问所需的 skills。

确认三个资产都能显示、没有缺文件报错。让 agent 检查机械臂和夹爪的关节限位与驱动设置，或者你自己在 Isaac Sim 里核对。机器人和夹爪都带物理关节，同样可以在 Isaac Sim GUI 里测试和验证。接下来我们把机械臂和夹爪组装起来，好把整个组合当作一个 articulation 来控制。

手动组装可以照着 [Robot Assembler 教程](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/robot_setup/assemble_robots.html)做。这里我们让 agent 完成组装并替我们验证：

**本例使用的示例 prompt：**

```
Assemble the robot arm <local path to Simready ur17g robot usd>
with the gripper <local path to downloded simready Robotiq_2F_140 gripper usd>
using the Robot Assembly tutorial in Isaac Sim
https://docs.isaacsim.omniverse.nvidia.com/6.2.0/robot_setup/assemble_robots.html.

Validate the assembly on completion.
```

agent 最终用上了 Isaac Sim 随附的 ‘isaac-sim-remote’ 和 ‘usd-articulation’ skills 来完成组装，并验证机器人的物理特性。至此运行拾放所需的资产都齐了：组装好的机器人和汽水罐。接下来进入工作流的最后一部分。

[![figure-05-joint-settings](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/NcKj9Cbp2iBlXh65rUf0T.gif)](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/NcKj9Cbp2iBlXh65rUf0T.gif)

*图 5. Isaac Sim 中 UR17G 机械臂与 Robotiq 2F-140 夹爪的关节设置。*

组装好的机器人和罐子都放进场景后，让 agent 运行任务，再用下一步的检查来评估仿真行为。

## 第 3 步：测试控制逻辑并运行拾放

资产现在带有仿真属性和 profile 验证，可以在组装好的场景和控制器里测试了。控制器把 UR17G 机械臂的运动与 Robotiq 2F-140 夹爪的开合协调起来。用下面的行为检查来评估 agent 生成的任务。想自己理解或改造控制器，请参阅[添加机械手机器人教程](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/core_api_tutorials/tutorial_core_adding_manipulator.html)。

**本例使用的示例 prompt：**

```
Run pick and place with the assembled robot and soda can
<path to soda can USD from SimReady library> in Isaac Sim.

Ensure you do a contact based grasp for picking up the can and validate
the accuracy/placement error for the pick and place as well.
```

**用到的 skills**：‘isaac-sim-remote’、‘manipulaiton-ik’ 和 ‘physics-simulation’

完整任务会测试夹爪在移动过程中是否握住罐子、并在目标处松开。先重置场景，再依次跑接近、抓取、抬起、保持、转移和释放。把你的运行结果与开头视频以及下面的成功标准对照。

[![figure-06-pick-and-place-landscape](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/TBsKTaclDU8oJvkXYCie8.gif)](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/TBsKTaclDU8oJvkXYCie8.gif)

*图 6. 在 Isaac Sim 中，UR17G 机械臂与 Robotiq 2F-140 夹爪把饮料罐从黄色拾取标记移到绿色目标。以 4× 速度播放。*

如果你的运行结果不一样，记下序列在哪一步出问题，让 agent 检查场景并重新生成控制逻辑。重试前把罐子和机器人复位到相同的起始状态，方便对比结果。

**仿真假设：**

- **固定配置：** 罐子从已知位置出发，机器人固定，工作空间干净平整。没有用视觉，碰撞检查也做了限制。
- **简化的罐子：** 没有对形变和液体运动建模，所以本例不测试挤压变形。
- **脚本化抓取与运动：** 水平抓取用了一个 2 N·m 的驱动力上限，这是通过仿真测试选的，并未按指尖力校准，也不是厂商推荐值。机械臂沿固定路径点运动、不做重新规划，靠接触和摩擦把饮料罐夹住。硬件夹持力规格请参阅 [Robotiq 产品表](https://robotiq.com/hubfs/Product-sheets/Adaptive%20Grippers/Product-sheet-Adaptive-Grippers-EN.pdf)。

这些结果只适用于这套脚本化配置，并不能证明对不确定的物体位置、不同负载或真实硬件也具备鲁棒性。

## 用 SimReady Assets 构建你的下一个仿真

用 [SimReady Central](https://huggingface.co/spaces/nvidia/simready-central) 里的资产搭一个自己的拾放任务，再选一个 agent 帮你组装场景、在 Isaac Sim 里跑起来。

**发现资产**

- **查找机器人和物体：** 在 Hugging Face 上浏览 [SimReady Central](https://huggingface.co/spaces/nvidia/simready-central)。
- **确认资产支持什么：** 对照 [SimReady Foundation](https://nvidia.github.io/simready-foundation/latest/) 里的 profiles 与 requirements，以及该资产的验证报告。

**搭建拾放场景**

- **设置模拟器：** 按本例所用的版本，参照 [Isaac Sim 安装指南](https://docs.isaacsim.omniverse.nvidia.com/latest/introduction/quickstart_index.html)。
- **接入你的 agent：** 按 [Isaac Sim Agent Skills 文档](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/development_tools/agent_skills.html) 把随附的 skills 提供给你的 agent。
- **组装机器人：** 如果你想手动连接机械臂和夹爪，请遵循 [Robot Assembler 教程](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/robot_setup/assemble_robots.html#assembling-robots)。

**准备并贡献内容**

- **从 CAD 起步：** 按[为机器人创建 SimReady 资产的 5 个步骤](https://developer.nvidia.com/blog/5-steps-to-create-simready-assets-for-robotics-with-frontier-ai-models/) 准备你自己的机器人资产。
- **验证并提交资产：** 按 [SimReady Central 提交指南](https://github.com/NVIDIA-Omniverse/simready-central/blob/main/.agents/skills/submit-simready-assets/SKILL.md) 把你的资产开放给其他开发者。

想找点灵感，可以看看 [Michael Wagner 的声控 VR 演示](https://lnkd.in/p/g3-5svW6) 或 [Maziyar Panahi 的 Microduck 仿真](https://lnkd.in/p/gnxQ3YS8)。两者都展示了开发者如何在自己的项目里使用 SimReady 资产。

你会做点什么？在 Hugging Face 评论区分享你的场景和结果，附上所用的资产和 Isaac Sim 版本。

祝搭建愉快！

## 本文提到的数据集 3

## 本文提到的 Spaces 1

该作者的更多内容

## *用覆盖八个领域的 10 万份合成商业文档评估隐私保护与实用 AI 应用*

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)

5

2026 年 11 月 9 日

## Nemotron-Personas-Finance-Japan：捕捉日本人口结构与金融背景的合成数据集

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)

19

2026 年 11 月 9 日

### 社区

通过拖入文本输入、粘贴或单击此处来上传图像、音频和视频。

点击或粘贴此处上传图像

· [注册](https://huggingface.co/join?next=%2Fblog%2Fnvidia%2Fsimready-assets-robot-pick-and-place)或[登录](https://huggingface.co/login?next=%2Fblog%2Fnvidia%2Fsimready-assets-robot-pick-and-place)发表评论


14

- [![](https://huggingface.co/avatars/9f55e9f6faf6a311cccd0c08d0427db5.svg)](https://huggingface.co/ByteSage404)
- [![](https://huggingface.co/avatars/55b482d76fb0269a3e3a1838049b459f.svg)](https://huggingface.co/pomilee)
- [![](https://huggingface.co/avatars/ec3d8d16e74f37584636ad4822d24f26.svg)](https://huggingface.co/jkosnik)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/oSUZPwq6TTEGqIPc62BVo.png)](https://huggingface.co/AiWinstone)
- [![](https://huggingface.co/avatars/7b54d53f6c5d49197fd5399e19dc7b6b.svg)](https://huggingface.co/pipwnz)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)
- [![](https://huggingface.co/avatars/6b59ac5f151b322f5261adacecce6b61.svg)](https://huggingface.co/yiucw)
- [![](https://huggingface.co/avatars/a045d5a990db610dd1f4abbcca7f1bd6.svg)](https://huggingface.co/klnadim)
- [![](https://huggingface.co/avatars/f42dac7bbb5f8a8dd315bdbe623813e6.svg)](https://huggingface.co/ExceedZhang)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/683acf96542967b165847cff/tUHvC7omJt6mPPdyx1oSe.png)](https://huggingface.co/safikhan5834)
- [![](https://huggingface.co/avatars/604ef02c6a6eac9315df923eaf7e56b4.svg)](https://huggingface.co/Eumoren)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6a980914cb03264ff33c4e0c/zOqgwh5M1nCzjQGfrT0Je.jpeg)](https://huggingface.co/willemelliw)

## 本文提到的数据集 3

## 本文提到的 Spaces 1
