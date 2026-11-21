---
vendor: sensetime_sensenova
title: 免费体验、便捷接入！日日新 U1.5 Lite 接入 Token Plan
original_title: 
url: https://www.sensetime.com/cn/news/sensenova-u1-5-lite-token-plan-20260911-1741
date: 2026-08-25
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: native
status: translated
body_sha: e843acfaba5e
---

得益于广大开发者与用户的信任与支持，商汤日日新 Token Plan 日均 Token 调用量已强劲突破 5,000 亿大关，生态繁荣再创新高度！

为持续回馈全球开发者与用户，新一代图片创作模型日日新 U1.5 Lite 已正式接入日日新 Token Plan，以更便捷、更高效的方式赋能更多创新场景。

![](https://oss.sensetime.com/strapi/uploads/external_d7f0433246b092be77fcc312_001_external_image_1_2eed437f88.png)

日日新 U1.5 Lite 基于 Neo-unify 统一架构，生成与编辑一体，原生支持超长指令遵循与 4K 高分辨率输出；无论在高质量生图还是复杂图像编辑场景下，均具备媲美主流商业模型的卓越性能。我们还将在公测期间提供免费配额：

- 立即体验：前往商汤日日新官网控制台 https://platform.sensenova.cn 获取 API 密钥！
- 免费配额：每 5 小时 1,500 次请求，公测期间完全免费！
- 模型 ID：sensenova-u1.5-lite
- 文档：https://platform.sensenova.cn/docs

**核心亮点**

生成 + 编辑一体化：单个模型打破“生成”与“编辑”的边界，既能实现精准文生图，又能基于参考图进行像素级微调与修改，一个模型覆盖全流程创作。

精准参考图驱动：编辑接口支持传入参考图，轻松应对图生图、局部重绘、风格迁移、人物保持及元素替换等高阶图像编辑场景。

自动提示词智能优化：内置 prompt_extend 引擎，开启后自动对用户的输入描述进行精炼与扩写，大幅提升图像细节与美学质感。

4K 超高清输出：最高支持 4096×4096 超高清分辨率，覆盖 1:1、16:9、9:16、2:3、3:2 等多种比例。

公测免费无水印：公测期间设置 watermark=false 即可免费生成无水印高清原图！

**快速上手与配置指南**

## 一、三步快速开启 API 调用

**第一步：注册账号并申请 API 密钥**

1.访问日日新平台，注册并完成账号验证。

2.进入控制台 → API 密钥页面，创建以 sk- 开头的 API 密钥。

3.妥善保存密钥，后续所有接口调用均需在请求头中携带。

**第二步：配置基础 URL 与模型 ID**

U1.5 Lite 兼容 OpenAI 图像接口规范，核心配置如下：

基础 URL：https://token.sensenova.cn/v1

模型 ID：sensenova-u1.5-lite

请求头：Authorization: Bearer <YOUR_API_KEY>

**第三步：调用接口**

1.文生图示例

根据文本描述生成图像，使用 /v1/images/generations 接口。

cURL 示例：文生图

```
curl https://token.sensenova.cn/v1/images/generations \ -H "Authorization: Bearer $SENSENOVA_API_KEY" \ -H "Content-Type: application/json" \ -d '{ "model": "sensenova-u1.5-lite", "prompt": "一只海獭宝宝漂浮在平静海面上，柔和晨光，写实摄影风格", "n": 1, "size": "1024x1024", "output_format": "png", "response_format": "url", "watermark": true, "prompt_extend": true }'
```

关键参数说明：

prompt：图像描述文本（必填），最高支持超长文本解析。

size：图像尺寸，支持 2K/4K 常量，宽高须为 32 的倍数，范围 512–4096，最大比例 3:1 或 1:3。

watermark：是否添加水印，false 为无水印（公测免费）。

prompt_extend：自动提示词优化开关，默认 true。

response_format：url 返回临时链接（24 小时有效），b64_json 返回 Base64 编码。

2.参考图编辑示例

传入参考图 + 编辑指令，实现图生图/图像重写，使用 /v1/images/edits 接口。

cURL 示例：参考图编辑

```
curl https://token.sensenova.cn/v1/images/edits \ -H "Authorization: Bearer $SENSENOVA_API_KEY" \ -H "Content-Type: application/json" \ -d '{ "model": "sensenova-u1.5-lite", "images": [{"image_url": "https://example.com/source.png"}], "prompt": "将背景改为雪山，保持人物不变", "n": 1, "size": "auto", "watermark": true, "prompt_extend": true, "response_format": "url" }'
```

使用提示：

编辑接口的 images 为必填，支持公网 HTTP/HTTPS URL （需可直接访问）或 Base64 Data-URL（data:image/png;base64,xxx），不支持无前缀的纯 Base64 字符串。

接口返回的图片 URL 为临时链接，24 小时后失效，请及时下载保存。

watermark=false 无水印生成功能当前处于免费公测阶段，后续转为付费功能后建议按需调整。

## 二、在 Agent 与 Skill 框架中集成 U1.5 Lite

日日新 U1.5 Lite 作为多模态生图模型，无法直接在 Cursor、Cline、Claude Code 等工具中配置为 Chat Model。需通过环境变量 + 自定义 Tool / Skill 方式接入。

## 方式一：环境变量配置 + 在自定义 Skill 中调用

适用于 OpenClaw、Hermes Agent、LangChain 或自定义 Agent 框架：

步骤 1：设置环境变量

```
export SENSENOVA_API_KEY="sk-你的APIKey"export SENSENOVA_BASE_URL="https://token.sensenova.cn/v1"export SENSENOVA_IMAGE_MODEL="sensenova-u1.5-lite"
```

步骤 2：在自定义 Skill 中调用图像生成接口（Python 示例）

```
import osimport requestsdef generate_image(prompt: str, size: str = "1024x1024", watermark: bool = True) -> str: """调用日日新 U1.5 Lite 文生图接口""" base_url = os.getenv("SENSENOVA_BASE_URL", "https://token.sensenova.cn/v1") api_key = os.getenv("SENSENOVA_API_KEY") model = os.getenv("SENSENOVA_IMAGE_MODEL", "sensenova-u1.5-lite") resp = requests.post( f"{base_url}/images/generations", headers={ "Authorization": f"Bearer {api_key}", "Content-Type": "application/json", }, json={ "model": model, "prompt": prompt, "size": size, "watermark": watermark, "prompt_extend": True, "response_format": "url", }, ) resp.raise_for_status() return resp.json()["data"][0]["url"]# 调用示例image_url = generate_image("赛博朋克风格的城市夜景，霓虹灯，雨后街道")print(f"生成图片地址: {image_url}")
```

注：参考图编辑的封装方式类似，将接口路径改为 /images/edits 并传入 images 参数即可。

## 方式二：在 OpenClaw 框架中集成

步骤 1：完成 OpenClaw 基础配置

按照 OpenClaw 官方文档 https://openclaw.ai/ 完成安装和 onboarding，在模型配置中选择 Custom Provider，填入：

API Base URL：https://token.sensenova.cn/v1

API Key：你的日日新 API Key

模型 ID：对话模型可配合选择 sensenova-6.8-flash-lite（U1.5 Lite 仅负责生成工具调用，不作为对话模型）

步骤 2：创建图像生成自定义技能

在 OpenClaw 的技能目录中创建一个新技能，定义 generate_image 工具，内部调用 U1.5 Lite 的 /v1/images/generations 接口。智能体在对话中遇到图像生成需求时，会自动调用该工具。

## 方式三：在其他智能体框架中集成

对于 Hermes Agent、LangChain、AutoGPT 等框架，集成思路一致：

1. 将 SENSENOVA_API_KEY 和 SENSENOVA_BASE_URL 配置为环境变量。

2. 定义一个自定义工具 / 函数（如 sensenova_generate_image），描述为"使用日日新 U1.5 Lite 模型根据文本描述生成图像"。

3. 工具内部通过 HTTP 请求调用 https://token.sensenova.cn/v1/images/generations，传入 model、prompt、size 等参数。

4. 如需编辑能力，同步定义 sensenova_edit_image 工具，调用 /v1/images/edits 接口。

## 上线前配置检查清单

- 环境变量 SENSENOVA_API_KEY 已设置
- Base URL 确保以 /v1 结尾（例：https://token.sensenova.cn/v1）
- 模型 ID 确认为 sensenova-u1.5-lite
- 图像功能正确请求 /images/generations 或 /images/edits 接口，而非 /chat/completions 对话接口
- 参考图编辑接口传入的图片 URL 可公网访问

无限创意，即刻开启！立即前往商汤科技日日新官网 [https://platform.sensenova.cn ](https://platform.sensenova.cn )注册并领取免费配额，用日日新 U1.5 Lite 打造你的下一个惊艳作品！

**原文来源：**[https://mp.weixin.qq.com/s/AK1iTp91Q2SU8JRU8TyHbQ](https://mp.weixin.qq.com/s/AK1iTp91Q2SU8JRU8TyHbQ)

#新闻

## 更多资讯

[**从大国外交现场到城市公共空间，商汤科技亮相APEC领导人会议周**2026/11/20](https://www.sensetime.com/cn/news/sensetime-apec-leaders-week-20261120-1525)[**商汤小浣熊·金融版正式推出，深化AI在金融行业的场景化应用**2026/11/19](https://www.sensetime.com/cn/news/sensetime-raccoon-finance-20261119-1522)[**SenseNova U1 Pro 获 Design Arena 双榜中国第一、全球第六**2026/11/19](https://www.sensetime.com/cn/news/sensenova-u1-pro-design-arena-20261119-1414)
