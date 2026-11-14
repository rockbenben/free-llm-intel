---
vendor: google_gemini
title: Gemini Omni 1.2 Flash 全面上市 (GA)：发布了 Gemini Omni 1.2 Flash (gemini-omni-1.2-flash)，具有长达 15 秒的视频生成和对话式编辑（首次为 3 到 10 秒……
original_title: 
url: https://aistudio.google.com/docs/changelog#11-05-2026
date: 2026-11-05
lang: zh
captured: 2026-11-14
extractor: readability-v1
translator: agent
status: translated
body_sha: 68ad415e19b4
---

## 2026 年 11 月 5 日  

*     **Gemini Omni 1.2 Flash 全面上市 (GA)**：发布了 [Gemini Omni 1.2 Flash](/docs/models/gemini-omni-flash)（`gemini-omni-1.2-flash`），具备最长 15 秒的视频生成和对话式编辑（首尾帧插值为 3 到 10 秒，每轮视频扩展 3 到 10 秒、总长度最长 30 秒），在多达 6 张参考图之间改善了角色与主体一致性，视频输出 [定价](/docs/pricing#gemini-omni-1.2-flash) 降低 30%（每 1M tokens $12.00），付费层 [速率限制](/docs/rate-limits#gemini-omni-flash-rate-limits) 翻倍。要开始使用，请参阅 [Gemini Omni Flash 指南](/docs/omni)。

*     **Gemini Omni 1.1 Flash 自动路由通知**：自 **2026 年 12 月 3 日** 起，对 `gemini-omni-1.1-flash` 的 API 请求将按 [Gemini Omni 1.2 Flash 费率](/docs/pricing#gemini-omni-1.2-flash) 自动路由到 `gemini-omni-1.2-flash`。

*     **扩展的 Office 和 OpenDocument 文件支持**：Gemini API 现在接受 PowerPoint 97-2003 (PPT)、OpenDocument Presentation (ODP) 和 OpenDocument Spreadsheet (ODS) 文件作为输入，并为 Word 97-2003 (DOC) 文件增加了页面图像处理。DOC、PPT 和 ODP 文件会渲染为页面图像。对于 ODS 文件，模型会接收第一个工作表中的数据和公式。DOCX、DOTX、ODT、PPTX、XLSX 和 XLS 文件的处理保持不变。有关每种格式的处理方式，请参阅 [Office 和 OpenDocument 文件](/docs/document-processing#office-documents)。

*     **函数响应中更多的文件类型和文件 URI**：工具现在可以向模型返回 Office 和 OpenDocument 文件、音频和视频。

  *   **GenerateContent API**：函数响应部分现在除了图像、PDF 和纯文本之外，还接受音频、视频以及 Office 和 OpenDocument 文件。它们还接受 `fileData`，因此工具可以返回 Files API URI 而非内联字节。`displayName` 现已在 `inlineData` 和 `fileData` 上可用，视频部分接受 `mediaProcessing`（`STATIC` 或 `AGENTIC`）。
  *   **Interactions API**：`function_result` 步骤现在除了 `text` 和 `image` 之外，还接受 `document`、`audio` 和 `video` 内容块，可通过内联 `data` 或 `uri` 传入。视频块在 `v1beta` 和 `v1alpha` 中可用，并接受 `processing`。

  详情请参阅 [多模态函数响应](/docs/function-calling#multimodal)。
