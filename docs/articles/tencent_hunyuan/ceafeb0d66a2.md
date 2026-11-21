---
vendor: tencent_hunyuan
title: Hy4 正式发布
original_title: 
url: https://hunyuan.tencent.com/research/hy4
date: 2026-11-04
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: native
status: translated
body_sha: 720c0e871b28
---

2026年11月4日

Hy4 正式发布

![腾讯云](https://hunyuan-portal-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/ai-logo-svgs/tencentcloud-color.svg)腾讯云

![OpenRouter](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026070622081339_db7b4e83c4ccd253de47d27e656c6a1f.svg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1783346895;2098706895&q-key-time=1783346895;2098706895&q-header-list=&q-url-param-list=&q-signature=44a94d95270276ae213ffe4696b88387477b9592)OpenRouter

![WorkBuddy](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026111316225445_38f7d1fa6bb1f062c21920b162d05167.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1794558176;2109918176&q-key-time=1794558176;2109918176&q-header-list=&q-url-param-list=&q-signature=1b28001e4d57083d960324d03e822b41ba3e74ee)WorkBuddy

![元宝](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026111316231014_b52b5e93c4dadeea0b56cb690a633d10.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1794558191;2109918191&q-key-time=1794558191;2109918191&q-header-list=&q-url-param-list=&q-signature=945d16acef285a3a52b0e362afb91d0ab8713330)元宝

![GitHub](https://hunyuan-portal-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/ai-logo-svgs/github.svg)GitHub

![HuggingFace](https://hunyuan-portal-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/ai-logo-svgs/huggingface-color.svg)HuggingFace

![ModelScope](https://hunyuan-portal-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/ai-logo-svgs/modelscope-color.svg)ModelScope

![AtomGit](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026070520372391_5ab131402b8d9602f385640c3cf82490.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1783255045;2098615045&q-key-time=1783255045;2098615045&q-header-list=&q-url-param-list=&q-signature=94c5742d352e0f745d2e316a975d5d87ac1c95c0)AtomGit

![System Card](https://hunyuan-portal-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/ai-logo-svgs/hunyuan-color.svg)System Card

今天，我们发布 Hy4 正式版。随着模型能力的再次全面跃升，Hy 首次跻身最强开源模型之列。

相比于 Hy4 preview，Hy4 显著扩展了预训练和后训练规模，首次引入了视觉能力，并大幅提升了指令遵循、长文理解、长程任务、深度研究等各项综合能力。

![Bench1-Hy4-最终版.jpg](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110401013020_30459ea6ad87f74409dbcde1801ac193.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793725295;2109085295&q-key-time=1793725295;2109085295&q-header-list=&q-url-param-list=&q-signature=1537f5ba6511988b1a9c8a1c95047c8c2be99d8f)

# 持续解锁的真实生产力

基础能力的全面提升，以及和腾讯内部众多产品与业务的持续合作，让 Hy4 解锁更多真实生产力场景。

## 视觉与电脑任务

Hy4 首次引入视觉能力，可以结合感知、推理和工具调用，进行细粒度图像处理和复杂图表分析等任务。Hy4 也首次支持电脑操作，可以灵活地结合使用命令行和图形界面。我们针对 Blender、CAD 等专业软件和跨应用长程任务开展了专项训练，持续优化专业任务的规划与执行力。

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/a951c950/2026110320193017_6fca5cb13718f18acb31665150b1b734.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793708370;2109068370&q-key-time=1793708370;2109068370&q-header-list=&q-url-param-list=&q-signature=84b3cddec16813b23799fb81233bcbc30c0666ed)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/a951c950/2026110320245856_df72b7ce4b0fc63bf4b0ca0fe1f021c8.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793708698;2109068698&q-key-time=1793708698;2109068698&q-header-list=&q-url-param-list=&q-signature=b6491f4115a63bc33bec45a4c7907de10b216060)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/a951c950/2026110320192758_af91e44d61013dd42ab8a4c2ee11a7b6.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793708370;2109068370&q-key-time=1793708370;2109068370&q-header-list=&q-url-param-list=&q-signature=164ac03d2d6b1fe84be12ff07f2d6cae0eaf5549)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110413513156_ff74402f600c13aeda6d0a2b7bd60ad0.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793771495;2109131495&q-key-time=1793771495;2109131495&q-header-list=&q-url-param-list=&q-signature=1c3885b4130c8ad79c5facee39bcd1007c96ee0f)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/a951c950/2026110320245727_3e405a906c58c2672f0498eaf6b45cc4.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793708698;2109068698&q-key-time=1793708698;2109068698&q-header-list=&q-url-param-list=&q-signature=4820a12bb93d1160a502ac2d70edcdc71aad08b4)

卫星图定位

Prompt: 找到屋顶写有“KLOOSTERBOER” 的仓库右上方光伏板区里最东侧的白色方形构件。

## 前端与游戏开发

视觉理解的引入也使 Hy4 的前端与游戏开发能力显著提升。我们对前端的复杂交互、业务逻辑、状态管理、前后端联动等方面进行了针对性优化，模型生成的界面不仅好看，并且功能完整可用。在游戏开发场景，我们与腾讯 IEG 专业游戏开发者合作，持续优化数据和评测质量，重点提升了功能实现、玩法逻辑、状态理解、资产处理等能力，实现了对 UE、Unity、Godot 等主流引擎的深度适配，并开始扩展至多人联机游戏开发。相比 Hy4 preview，Hy4 在 GameDev 和 GameLogic 评测中分别提升 19.1% 和 9.8%。

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/a951c950/2026110320005933_0129832274e3aabfb6200975a2687bc7.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793707262;2109067262&q-key-time=1793707262;2109067262&q-header-list=&q-url-param-list=&q-signature=f945b083bac3557c5ac3689a09380ad714688c39)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/a951c950/2026110320012269_711abfd18182d627066f8ecaf5069256.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793707284;2109067284&q-key-time=1793707284;2109067284&q-header-list=&q-url-param-list=&q-signature=d57469d03ad81577dd974b3b79940e3f32aee0fd)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/a951c950/2026110321521289_4b9f2cef912ae812c2d398de4ecf0223.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793713935;2109073935&q-key-time=1793713935;2109073935&q-header-list=&q-url-param-list=&q-signature=6c7530c3ff9aad3ec7848974fc2f24353d1046b3)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/a951c950/2026110320063732_a641eac3edab8c9ea9206861a94fbbdf.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793707599;2109067599&q-key-time=1793707599;2109067599&q-header-list=&q-url-param-list=&q-signature=2d8f411c264a2512347f4cbddb8ad82584f67169)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/a951c950/2026110320070963_0af71792ec21a20efb7d1af54ea43d36.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793707631;2109067631&q-key-time=1793707631;2109067631&q-header-list=&q-url-param-list=&q-signature=67894917f6bc9482c794e55a4fb3bf9594137656)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/c9e0c958/2026110402331028_5c415d3e085bf59e329866efc4e0911d.jpeg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793730793;2109090793&q-key-time=1793730793;2109090793&q-header-list=&q-url-param-list=&q-signature=9feb25f121a3b9f154602b29016fb995d9f4efdc)

腾讯企鹅岛

Prompt: 目标：用 Three.js 构建一个「腾讯企鹅岛 3D 数字沙盘」，交付一个可离线双击打开的单文件 HTML（内联 Three.js 0.184.0，无 CDN/字体/纹理等远程依赖）。不是鸟瞰图、不是纵向 Landing Page、不是贴图背景——所有建筑、道路、绿脊、海岸、植被、人车必须在同一套真实三维场景里，可任意旋转与地面行走。 场地：海湾半岛南北纵深，蓝灰海面、白银建筑群、中央绿脊、环岛路网。重点塑造五组建筑——① 腾云中心：三座低矮云楼＋架空筒体＋钢桁架连桥；② 云海大厦：六栋错落塔楼＋参数化金属翼片；③ 企鹅公寓：11 栋锯齿错位、共享退台；④ 腾讯螺旋（最关键）​：四片建筑立面自身连续回旋、展宽向上成塔，落成 J 形收脚，绝不能套外挂圆环或做成四根麻花；⑤ 科技馆：连续环形绿顶＋内庭（标注"图像拟合、非测绘"）。 交互：轨道观察、第一/三人称地面漫游（第三人称显示企鹅化身）、天气昼夜、小地图、建筑详情、楼层剖切、电影导览、截图与录制。 UI：浅色磨砂控制面板、中文清晰排版、可收起工具层；夜景只改 3D 环境，面板保持浅色可读，禁止黑底霓虹驾驶舱。

## 金融与办公场景

我们基于真实金融场景构建了数千个工作空间和上万个高质量任务，让模型充分学习基金研究、证券分析、量化策略、资产配置、公司金融、财税会计等方向的专业流程与规范。我们联合腾讯金融科技 FiT 开展了 213 位专家的金融众测，其中 153 位来自外部的头部金融机构，且七成拥有五年以上工作经验。基于 579 个真实金融任务的众测显示，Hy4 综合表现位居开源模型第一（Hy4：3.04/4；DeepSeek-V4.1-Flash-1017：2.97/4；Kimi K3.1 Pro：2.68/4；GLM-5.3：2.68/4）。此外，在金融智能体公司讯兔科技的内部评测 IRAB 中，Hy4 较 Hy4 preview 提升 12.03 个百分点。为了提升金融等各类办公场景的实用性，我们还启动了针对时效检索、多源信息整合与事实一致性校验的专项搜索优化。在自建测试中，Hy4 的幻觉率从 Hy4 preview 的 15.76% 降至 5.45%，猜测导致的错误率从 23.1% 降至 5.6%。此外，Hy4 还重点提升了办公场景中的人机双写能力，支持用户与 Hy 实时协作编辑 Word、Excel、PPT 等办公文件。盲评显示 Hy4 相比 Hy4 preview 在文档美观度、稳定性和可用性上均有明显提升。

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/a951c950/2026110411175540_7009194ce5c2541529e10465a0fb40e6.jpeg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793762278;2109122278&q-key-time=1793762278;2109122278&q-header-list=&q-url-param-list=&q-signature=b2f30f4d8f720abfc35c1865002c87e63869e0e6)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/a951c950/2026110411192378_805957543e211cbee957ab0cf0621fea.jpeg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793762366;2109122366&q-key-time=1793762366;2109122366&q-header-list=&q-url-param-list=&q-signature=75c3e3e629272a9f1d3bc128f5c3a95139d60b45)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/a951c950/2026110411161175_9f360c5ab7736510df54c882e9dbf188.jpeg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793762174;2109122174&q-key-time=1793762174;2109122174&q-header-list=&q-url-param-list=&q-signature=6389acd6d73c7abe3cc993b6f4b95bad5e5d9293)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/a951c950/2026110411470647_57da346b8c057f411d5e11b66ffaf60b.jpeg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793764027;2109124027&q-key-time=1793764027;2109124027&q-header-list=&q-url-param-list=&q-signature=2186ff7f9319245ffb96cb9bdae165d7f8577f93)

金融估值建模报告

Prompt: 用global-equity-research和neodata，做一个特斯拉的建模报告，要输出excel和对应的报告pdf，注意你的估值逻辑以及数字来源，可以搜索并参考多家机构的的研究，研究机构写HY RESEARCH

## 科研与模型研发

Hy4 将复杂推理、科学编程与长程任务执行相结合，进一步提升端到端推进科研工作的能力。在涵盖 7 大学科、123 项可执行研究任务的 TenureTrail 内部评测中，Hy4 在数学构造、物理建模、地球环境、系统工程和社会经济决策等领域展现出扎实的科研能力，位居开源模型第一。Hy4 也在为递归自我改进（RSI）做准备，提升各种模型研发任务的能力。结合 [Hyra 2.0](https://hunyuan.tencent.com/research/hyra2)脚手架，Hy4 优化了内部同架构小模型的预训练基础设施，并自动训练出在多项评测中优于官方的 Jev 模型。同时，我们也开源了由 Hy4 协同 Hyra2.0 研发的单细胞表征基础模型 HyCell 和物理场基础模型 HyPDE，希望将模型辅助科研的成果转化为社区可复用的工具。

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110400015543_23d03c33464f967b92db9b5e30c6ab1a.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793721718;2109081718&q-key-time=1793721718;2109081718&q-header-list=&q-url-param-list=&q-signature=142cdd5ead1ef3f712464eaeb6ed9708b28afb8c)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110402192830_964ebf3778ed952c8db86d57e1ad3431.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793729971;2109089971&q-key-time=1793729971;2109089971&q-header-list=&q-url-param-list=&q-signature=aa8d7d3cd398c3fd82c434f75f469e243ac411f6)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110402200438_8c613f6a2453c45131249da7cd1bc9a8.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793730007;2109090007&q-key-time=1793730007;2109090007&q-header-list=&q-url-param-list=&q-signature=3dc5c2f0163e17d7a1c9cd3f83bc0ef4e15058ae)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110402202743_19dff19e882464abfd963f70a8ec7755.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793730030;2109090030&q-key-time=1793730030;2109090030&q-header-list=&q-url-param-list=&q-signature=614d9dc28abdbdc1d17414ab720e1ad2cd42d8c0)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110402212194_218211c5f701f1190bccfb9f6deed1ce.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793730084;2109090084&q-key-time=1793730084;2109090084&q-header-list=&q-url-param-list=&q-signature=2fe461dca5bc144c861f5f9533b4dd0d9c02ee85)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110402213716_05c531fa72d7a95dfc01c529ee1d739c.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793730100;2109090100&q-key-time=1793730100;2109090100&q-header-list=&q-url-param-list=&q-signature=8d0e051656c3563d9bed160c1ccb5d36bd9664f3)

在小鼠胚胎三维重建任务中，面对包含 699 万个细胞的 84 张无序二维切片，以及其中的镜像翻转问题，Hy4 在离线、无专用配准工具、无细胞类型标注的条件下，于1.5 小时内完成了切片对齐与三维重建，全程无人干预，效果优于常用配准工具的默认流程，展现了在复杂数据与受限工具环境下自主推进科学计算任务的能力。

## 长期个人助理

Hy4 的上下文学习能力持续提升，能更好地理解多源复杂信息。借助 WorkBuddy 的企业微信套件，Hy4 可以连通聊天记录、邮件、文档、日程与会议等日常工作信息。多个项目并行推进时，Hy4 能理清各项目的推进历史与最新进展，识别待跟进的任务、需要准备的会议和临近截止的事项，及时提醒用户并协助安排优先级。此外，由 Hy4 支撑的团队协作功能将随新版「项目」在 Workbuddy 上线。

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/a951c950/2026110411070673_d2b5ca33bd970f64a6301fa75ae2eb22.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793761629;2109121629&q-key-time=1793761629;2109121629&q-header-list=&q-url-param-list=&q-signature=07092c423b2fb5be3da688d9a143b06d20a4e3b3)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110411371281_ff68f7ae5e453f9ebb3cc2fc4ddf5bf6.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793763434;2109123434&q-key-time=1793763434;2109123434&q-header-list=&q-url-param-list=&q-signature=24a6635b541d1308f2f91fd78285387221681c82)

![](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110413494499_b82e00bd891038da51d6293939a34aba.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793771388;2109131388&q-key-time=1793771388;2109131388&q-header-list=&q-url-param-list=&q-signature=3587d98edc6d349a0457ea24fe322771ea077111)

从各类信息源整理关注事项

Prompt: 目标：综合我的聊天记录（群聊、私聊、文件）、邮件、日历、会议及文档，生成「Daily Focus」个人每日事项看板，交付可离线打开的单文件交互式 HTML。不是聊天摘要或流水账，而是让我一眼知道今天有哪些事值得关注、哪些需要优先处理。内容：跨来源整合最新信息，去重并提炼工作、生活及日常事务中值得关注的事项，按重要性和紧急性排序。重点讲清每件事发生了什么、目前什么情况、接下来该怎么办。面向普通大众，用自然、通俗的语言解释事情，不预设读者了解背景，避免专业术语、内部缩写、复杂表达和 AI 套话。保留必要来源。

# 产品反馈

![Manus](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110401453515_2a709c2caeeff98490a465548f2c17e0.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793727938;2109087938&q-key-time=1793727938;2109087938&q-header-list=&q-url-param-list=&q-signature=9e0a69e3fd0992032e69faa0db5f5d3dfcc22ce3)

在 Manus 的内部评测中，Hy4 在深度研究、数据分析和办公文档等任务上效果亮眼，综合表现名列前茅。我们发现，Hy4 非常擅长办公文档的生成和编辑，任务完成率接近 97%。它的指令遵循非常精准：在复杂的文档编辑任务中，从引用格式、样式编号到逐条修改说明，它都能准确完成。对 Manus 用户来说，这意味着更少的返工，以及在真实场景中更高效地解决问题。

Manus

![讯兔科技](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110403103430_6c82b854d9c3e7d94c315d33d9e663a2.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793733036;2109093036&q-key-time=1793733036;2109093036&q-header-list=&q-url-param-list=&q-signature=c1a94610a3b335c4b0ed06f5fd2128cfaf507af3)

作为聚焦投研场景的 AI 服务商，讯兔科技基于 IRAB 投研智能体评测基准，用 101 道真实投研任务，对 Hy4 正式版进行了评测。Hy4 正式版综合得分 61.63 分，相比 Hy4 preview 提升了 12.03 分，在我们持续跟踪的同系列模型中进步明显。横向看，Hy4 正式版的得分稳居国产模型第一梯队，与海外旗舰模型的效果进一步缩小。投研智能体的价值在于交付能真正可用的研究成品，Hy4 在端到端完成真实投研任务上进步很快。此前 Hy3 也接入了alpha派部分产品，期待与混元团队持续深化合作，探索金融场景的智能上限。

讯兔科技

![进门](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110403101337_83bb66953638a161a2eb8dccc366d1e2.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793733015;2109093015&q-key-time=1793733015;2109093015&q-header-list=&q-url-param-list=&q-signature=fefdcaa36f2e8137e2964971559db3f2c7d46536)

作为金融市场领先的机构 AI 投研工作台，进门内部投研 Agent 场景评测中，Hy4 是目前唯一在总分上与 Claude Opus 5.5 并列第二的国产模型，更在数据查询单项上以 75.4 分超过 GPT-6.1-sol 近 20 分、位列全部参测模型第一。对投研工作台而言，查准数据是所有分析的第一步，只有数据准确了，后面的判断才有意义。

进门

![财搭子](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110409541953_c9be733d18d77fde0da2befde1805315.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793757261;2109117261&q-key-time=1793757261;2109117261&q-header-list=&q-url-param-list=&q-signature=66719745c2e6bcd71a81fc82d840c0832e3f07dd)

在财搭子 Harness 框架下，混元 Hy4 充分展现出投研解读与决策辅助的应用价值。评测中，个股研究场景下均分 4.27/5，位列参评模型首位，42.9% 的回答获得五模型最高评分（含并列）；深度投研、跟踪监控均分分别达到 4.43 和 4.03分（满分5分）。实际任务中，混元能够围绕核心矛盾组织分析，善于发现弱关联之间的强因果：公司研究关注订单向利润和现金流的转化，板块研究拆解机会成立的条件，ETF 分析区分指数表现与产品溢价风险，决策辅助时结合持仓成本给出情景方案，跟踪任务则把关键价位和风险信号转化为观察条件。它能将专业信息解释为投资者可理解的判断依据，并交代风险边界与改判信号，为从理解机会到持续跟踪的投研决策提供支持。

财搭子

![南方基金](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110403105674_c8393dd0108b1de1b6734a2b43233d13.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793733058;2109093058&q-key-time=1793733058;2109093058&q-header-list=&q-url-param-list=&q-signature=bcd06d9e4c6b20233a21e1a41b1375d16b5e92ff)

金融服务面对的，是投资者关于市场、行业和资金规划的具体问题。我们围绕市场行情观点和投资规划，对 Hy4 开展了覆盖 398 道问题的内部测评。以有色金属行业影响因素为例，模型可从宏观环境、供需、政策、成本、金融市场及金属特性六个方面进行梳理，并区分工业金属与贵金属的不同驱动因素。Hy4 可用于投资者教育和金融知识问答场景，帮助投资者更系统地了解相关金融知识。

南方基金

![汇添富基金](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110403114944_e4d8a1908969c3b3918276b2f46057e2.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793733111;2109093111&q-key-time=1793733111;2109093111&q-header-list=&q-url-param-list=&q-signature=4dde16420f09abc7ad256ee35f2bf58b10839497)

投资研究对宏观环境、行业基本面、财务与估值假设的可复核性要求较高。为评估 Hy4 能否为基本面研究提供有依据且可核对的分析支持，我们在公司投研智能体平台上针对宏观事件分析、公司估值建模、组合构建、风险分析等常见任务进行实验，Hy4 能够清晰理解用户意图，并明确给出计算依据与适用假设，以便投研人员核对结论，判断输出结果是否适用于具体研究问题，提升了输出结论的可信度。

汇添富基金

02 / 06

![WorkBuddy](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110403005137_38f7d1fa6bb1f062c21920b162d05167.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793732454;2109092454&q-key-time=1793732454;2109092454&q-header-list=&q-url-param-list=&q-signature=0a456a5b194345dad301414e230221ee224e7ae9)

网页、视觉创意、3D 等场景上 Hy4 更好地平衡了效果和速度，多步骤浏览器任务中，Hy4 会观察操作反馈，自己调整和验证。WorkBuddy 综合评测：平均效果 83.18 分，通过率 96.15%，12 个场景里，Hy4 在 9 个场景位列国内模型第一。

WorkBuddy产品经理 Anne

![元宝](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110403012828_b52b5e93c4dadeea0b56cb690a633d10.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793732490;2109092490&q-key-time=1793732490;2109092490&q-header-list=&q-url-param-list=&q-signature=c02d00c5985f6709fcf074128d697a7b38746961)

在元宝内部评测集合上，Hy4 相比 Hy4 preview 得分从 65.25 提高到 72.53，其中，多轮对话和写作的提升尤为突出：多轮记忆得分提升 6.67 分，指代消解更智能，多轮对话衔接更连贯；写作多样性提升 10.89 分，内容多样性大幅提升。在元宝多模态理解场景，相较之前 VLM 模型，Hy4 在多模态 Agent 任务完成度提升 36.8%，多模态问答提升 15.8%，整体识图、图文混合推理、跨模态上下文能力大幅提升。

元宝产品经理 Nyx、Ranmer

![王者荣耀](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110403015619_135ff144dd6a08bc8d026b733198b18b.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793732518;2109092518&q-key-time=1793732518;2109092518&q-header-list=&q-url-param-list=&q-signature=af05b846c612b6683f88d2bfcc794c8daac110e8)

在王者荣耀项目中，Hy4 在开发与测试两大 AI 生产场景均实现显著升级。开发侧，搭配 AI 自动表格配置平台，Hy4 在 20 类游戏配置场景中，准确率从 91.74% 提升至 97.28%，经 Agent 自主校验修复后达 99.32%。测试侧，在 Bug AI 自动分析平台上，代码根因分析准确率从 59.5% 提升至 73.8%，且 Agent 工具调用深度为 Hy4 preview 的 3.7 倍，耗时与 Token 消耗未见明显增长，在游戏全链路 AI 生产中全面提升。

王者荣耀项目管理负责人 TH

![和平精英](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110403022051_03369c2083d0b60333200772f1fa4f5f.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793732542;2109092542&q-key-time=1793732542;2109092542&q-header-list=&q-url-param-list=&q-signature=a61c2879c95a0ecbdd9e314431ad85465c98159f)

在和平精英 AI NPC 场景的效果评测中，Hy4 表现亮眼。相较 Hy4 preview，Hy4对话高度贴近玩家日常开黑交流，角色拟人度与人设一致性更高；互动主动性与话题延展性显著增强，能主动破冰、接话行云流水；通过安慰、肯定与主动提问持续高浓度输出情绪价值。3 分制人工评分下 Hy4 总分均值 2.91，其中情绪价值分项 2.96，高于整体水平并逼近满分。Hy4 让 AI NPC 角色更接近并肩作战的队友，高度还原与好友组队的陪玩体验。

和平精英AI 玩法策划负责人 Jesse

![QQ](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110403023983_8ca88aeaa8e8a39d2774d600860162f9.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793732561;2109092561&q-key-time=1793732561;2109092561&q-header-list=&q-url-param-list=&q-signature=29ee4e6413e3333f9e0354abb9a212bc37d68856)

在 QQ，小 Q 每天帮用户查信息、设提醒、总结未读消息、出社交主意，覆盖 40 多个场景。 Hy4 相较 Hy4 Preview，整体满意率从 90.11% 提升到 93.10%，其中联网搜索、QQ 空间查找推荐、订阅提醒三个高频场景，分别提升 6.66pp、4.69pp、2.52pp。

QQ产品经理 Kedeng

![企业微信](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110403051259_3cce84d5fe7d7f0402c18f161e606bc8.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793732714;2109092714&q-key-time=1793732714;2109092714&q-header-list=&q-url-param-list=&q-signature=dd2571bdce3195823e3d88b9cf0532124c9e4a98)

在企微大圆的复杂办公协作场景中，Hy4 能把多意图指令拆成关联的多个子任务，自主规划工具调用。相比 Hy4 preview，指令跟随能力提升 13.5%，复杂信息检索提升 12.7%，消息会话综合效果提升 8.5% 。

企业微信算法负责人 Dylan

![微信读书](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110403053684_6db909f2a73575b787b375e565e7734c.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793732738;2109092738&q-key-time=1793732738;2109092738&q-header-list=&q-url-param-list=&q-signature=68f70aba33466536ef2c983dc0b03c2083077604)

相较 Hy4 preview，Hy4 的综合评测得分从 82.10 提升至 87.69。其中，信息取舍和长度控制提升最为明显，分别提升 22.2% 和 50.7%；在人物关系梳理、情节解读、知识问答等场景下，更准确地抓住问题重点，减少无效冗余回复；答案可达性和读者适配能力分别提升 3.0% 和 6.6%，整体提升了用户阅读过程中的互动体验。

微信读书算法负责人 Isaac

![腾讯新闻](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110403045256_0c1336139dd39776eaf99aa0854625ee.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793732695;2109092695&q-key-time=1793732695;2109092695&q-header-list=&q-url-param-list=&q-signature=92a388d0039937338500fc78fabc67566fc0d4c5)

在新闻搜索和自由问答场景上，我们通过用户真实问题测试集的盲测对比，结果显示 Hy4 相比 Hy4 preview 在回复准确性、细节丰富度、语言流畅度等维度均提升 28% 以上，整体端到端答案质量，Hy4 相比 Hy4 preview 提升 36%。

腾讯新闻产品经理 Aero

![ima](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110403035813_ba938573b46ba47b93f4d3805db90d82.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793732640;2109092640&q-key-time=1793732640;2109092640&q-header-list=&q-url-param-list=&q-signature=98a64ee10ab7bd7d0c701c6c22345ec3b0aa8564)

在 ima 知识库、通用问答及 agent 场景评测中，Hy4 相比 Hy4 preview，回答质量提升9.7%，推理正确性提升3.4%，思维链综合提升1.2%，模型回复内容更能抓住重点，决策依据更充分。

ima产品经理 Kaycee

02 / 09

# 负责任的开源和发布

我们充分意识到模型的网络和生物等能力潜在的安全风险，并致力于以更负责任的方式进行训练、开源与发布。

在 Hy4 训练阶段，我们仅纳入与 PoC 生成、漏洞修复相关的防守性网络安全数据，同时剔除漏洞利用、逆向、渗透等攻击性训练内容，力求避免潜在进攻性能力的提升。我们组织来自腾讯玄武和科恩实验室的内部安全专家，围绕密码分析、逆向工程、漏洞利用等方向进行审计，结果表明：Hy4 在加密算法的逆向求解、对抗二进制混淆、漏洞利用等进攻性能力上未展现出突出风险。

在生物安全方面，Hy4 的开放式实验设计能力尚未达到高风险阈值（Hy-BioExperimentBench: 30.4/100）。我们组织了内部专家对模型作答轨迹进行审计，发现模型基础生物知识掌握扎实，但将知识转化为可执行实验方案这一关键环节的能力仍然有限，尚未发现其能够显著降低实施生物危害行为的门槛。更全面的安全评估等细节，可以参考：[Hy4 System Card](https://hy.tencent.ai/Hy4_system_card.pdf)

Hy4 已在腾讯云和 OpenRouter 上线，并可在 WorkBuddy/CodeBuddy、元宝、ima 等产品上体验，性能显著超过 Hy4 preview 的同时维持相同 API 价格。

Hy4 API 价格（每百万 Tokens ）

| 输入（命中缓存） | 输入 | 输出 |
| --- | --- | --- |
| 0.3元 | 6元 | 18元 |

Hy4 已在 GitHub、HuggingFace、ModelScope、AtomGit 开源，并已联合 vLLM/SGLang 社区与 Inferact Inc. 提供开源生态支持。

# 局限性和未来展望

尽管 Hy4 已经是目前最强的开源模型之一，其与顶尖闭源模型仍然存在较大差距，尤其在我们内部构建的前沿数学、长程开发、模型迭代、视觉问答等领域的高难度测试集上。我们将持续稳健地扩展预训练和后训练规模，努力缩小和顶尖闭源模型的差距。

![Bench2-Hy4-最终版（横版）.jpg](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110402015231_ac89ad6ff52f8d565fa568ebfa6928d4.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793728916;2109088916&q-key-time=1793728916;2109088916&q-header-list=&q-url-param-list=&q-signature=16730ee80618e14d09836d87380b11adea18dde1)

另一方面，我们计划近期发布 Hy4 flash，会显著提升模型性价比和推理速度，并更加高频地和产品协同迭代，不断提高实用性。

# 附录：模型得分

![大Bench图表.jpg](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110402023072_85b416b6484a88ef96ef6edda563b560.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793728954;2109088954&q-key-time=1793728954;2109088954&q-header-list=&q-url-param-list=&q-signature=747236201b67dd4e9872ed806c8de224d0ca57c1)

目录

[ 持续解锁的真实生产力]()[ 视觉与电脑任务]()[ 前端与游戏开发]()[ 金融与办公场景]()[ 科研与模型研发]()[ 长期个人助理]()[ 产品反馈]()[ 负责任的开源和发布]()[ 局限性和未来展望]()[ 附录：模型得分]()

评论（12）

0/2000

![](https://hy-account-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/default_avatar.png)

uid0bda654c

国产模型加油！

江苏

2026-11-14

![](https://hy-account-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/90bf6f87bd9a303aed46b3bfa35448c9/20260610205633_62359b035002a05b1ef6428d69b5b9d71ec293a4.png)

叶

Hy4是真的好用

广东

2026-11-10

![](https://hy-account-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/ac6bf903c004056380e76e95f04f7a6a/ce9b022508505fe0d9ef29c9891a50be.png)

像风一样自由

hy4很好用，希望能把前端审美，空间理解，3d建模这一块敏捷迭代一下，还有token效率和速度优化一下，那就是真正的国模sota了[加油]

广东

2026-11-06

![](https://hy-account-prod-1258344703.cos.ap-guangzhou.myqcloud.com/public/fa3bc5e8ccbeffc235488b7e8a885efd/93677c3fd153eabcc63d050aa81871f2.png)

ΡανςΕρίκα

你知道的，混元是我心中的SOTA，我们曾并肩作战击败过许多开源模型，我和hy4很早就认识了，这家伙强得不可思议。我认为我们WB hy三人组，可以产生很好的化学反应。有时候做出决定很难，经过许多个日夜的思考，我决定把model切到hy4 High 900K，我已经迫不及待要烧穿账单了。至于蓝色大肥鱼祝他们一切顺利！

广东

2026-11-04

### 继续阅读

![Hy4 flash：日常工作的极致性价比模型](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026111517490315_6d0b8dd02dcfff6174ba34e437a09247.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1794736144;2110096144&q-key-time=1794736144;2110096144&q-header-list=&q-url-param-list=&q-signature=1b73b2b2800172c2daf9fedacd0a9bcf2a7355fe)

Hy4 flash：日常工作的极致性价比模型

2026-11-16Hy LLM

![Hyra 2.0：自动化科研的下一步](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/210b8ba1/2026102401353815_cfa89033e01cdb8528854792d1ac71b6.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1792776939;2108136939&q-key-time=1792776939;2108136939&q-header-list=&q-url-param-list=&q-signature=2a2c6d07127192204183797a9f8138822e19ad4b)

Hyra 2.0：自动化科研的下一步

2026-11-02Hyra Team

![Hy Image3.5 preview 发布：为专业创作提供高性价比模型](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9c5ca906/2026092121293058_779bc5a05fcb7733e4780de216614118.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1789997370;2105357370&q-key-time=1789997370;2105357370&q-header-list=&q-url-param-list=&q-signature=b7bd8e7f50f9549d6ec0470c38ebabbd090eee02)

Hy Image3.5 preview 发布：为专业创作提供高性价比模型

2026-09-22caesarqin
