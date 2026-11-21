---
vendor: google_gemini
title: Gemini Omni 1.2 Flash generally available (GA): Released Gemini Omni 1.2 Flash (gemini-omni-1.2-flash), featuring up to 15-second video generation and conversational editing (3 to 10 seconds for firs…
original_title: Gemini Omni 1.2 Flash generally available (GA): Released Gemini Omni 1.2 Flash (gemini-omni-1.2-flash), featuring up to 15-second video generation and conversational editing (3 to 10 seconds for firs…
url: https://aistudio.google.com/docs/changelog
date: 2026-11-05
lang: en
captured: 2026-11-14
extractor: readability-v1
status: ok
body_sha: 1f40d3880f48
---

## November 5, 2026  

*     **Gemini Omni 1.2 Flash generally available (GA)**: Released
  [Gemini Omni 1.2 Flash](/docs/models/gemini-omni-flash)
  (`gemini-omni-1.2-flash`), featuring up to 15-second video generation and
  conversational editing (3 to 10 seconds for first and last frame
  interpolation, and 3 to 10 seconds per-turn video extension up to 30 seconds
  total length), improved character and subject consistency across up to 6
  reference images, 30% lower video output
  [pricing](/docs/pricing#gemini-omni-1.2-flash) ($12.00 per 1M tokens), and
  doubled paid-tier [rate limits](/docs/rate-limits#gemini-omni-flash-rate-limits).
  See the [Gemini Omni Flash guide](/docs/omni) to get started.

*     **Gemini Omni 1.1 Flash automatic routing notice**: Effective **December 3,
  2026**, API requests to `gemini-omni-1.1-flash` will automatically route to
  `gemini-omni-1.2-flash` at
  [Gemini Omni 1.2 Flash rates](/docs/pricing#gemini-omni-1.2-flash).

*     **Expanded Office and OpenDocument file support**: The Gemini API now
  accepts PowerPoint 97-2003 (PPT), OpenDocument Presentation (ODP), and
  OpenDocument Spreadsheet (ODS) files as input, and adds page-image
  processing for Word 97-2003 (DOC) files. DOC, PPT, and ODP files are
  rendered as page images. For ODS files, the model receives the data and
  formulas from the first sheet.
  Processing for DOCX, DOTX, ODT, PPTX, XLSX, and XLS files is unchanged. See
  [Office and OpenDocument files](/docs/document-processing#office-documents)
  for how each format is processed.

*     **More file types and file URIs in function responses**: Tools can now
  return Office and OpenDocument files, audio, and video to the model.

  *   **GenerateContent API**: Function response parts now accept audio,
    video, and Office and OpenDocument files, in addition to images, PDFs,
    and plain text. They also accept `fileData`, so tools can return a
    Files API URI instead of inline bytes. `displayName` is now available
    on both `inlineData` and `fileData`, and video parts accept
    `mediaProcessing` (`STATIC` or `AGENTIC`).
  *   **Interactions API**: `function_result` steps now accept `document`,
    `audio`, and `video` content blocks, in addition to `text` and `image`,
    by inline `data` or `uri`. Video blocks are available in `v1beta` and
    `v1alpha` and accept `processing`.

  See [Multimodal function responses](/docs/function-calling#multimodal)
  for details.
