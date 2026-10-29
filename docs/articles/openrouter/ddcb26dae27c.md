---
vendor: openrouter
title: 如何使用LLM从 PDF 中提取表格
original_title: 
url: https://openrouter.ai/blog/tutorials/extract-tables-from-pdf-llm
date: 2026-10-29
lang: zh
captured: 2026-10-29
extractor: readability-v1
translator: mt
status: translated
body_sha: ff62631be7be
---

# 如何使用LLM从 PDF 中提取表格

开放路由器 ·10/29/2026

![如何使用LLM从 PDF 中提取表格](https://openrouter.ai/blog/images/extract-tables-from-pdf-llm.png)![如何使用LLM从 PDF 中提取表格](https://openrouter.ai/blog/images/extract-tables-from-pdf-llm-dark.png)

要使用 LLM 从 PDF 中提取表格，请将 PDF 发送到[可以读取文件的模型](https://openrouter.ai/docs/guides/overview/multimodal/pdfs)，以及描述表格一行的[严格的 JSON 模式](https://openrouter.ai/docs/guides/features/structured-outputs)。该模型返回键入的行。数量以整数形式返回，写为 (3,878) 的损失以 -3878 形式返回，跨两页的表格以一个列表形式返回。

我们在五个 PDF 上进行了测试，其中两个是扫描件。每个直接读取 PDF 的模型都正确读取了所有 644 个单元格。我们测试中的失败来自 PDF 到达模型的路线，其中两个返回了正常响应，没有错误。

## Tl;博士

- 一行的严格 JSON 模式将 PDF 表转换为键入的行，字段描述处理清理，例如括号中的负数和脚注标记。
- 在我们的测试中，读取 PDF 的模型可以处理数字文件和扫描。无法读取 PDF 的模型需要“mistral-ocr”解析器进行扫描。
- 通过免费的“cloudflare-ai”解析器发送的扫描返回零行，没有错误，因此拒绝空结果。
- 长表可以在输出令牌限制处停止，因此拒绝任何“finish_reason”为“length”的响应。

## 开始之前

您需要以下内容来运行示例。

- 一个有积分的 OpenRouter 帐户，以及存储在 `OPENROUTER_API_KEY` 环境变量中的 [API 密钥](https://openrouter.ai/settings/keys)。本指南中的模型是付费的。
- Python 3.10 或更高版本和“requests”包（“pip install requests”）。
- Node.js 18 或更高版本，但仅适用于接近尾声的 TypeScript 版本。
- 包含表格的 PDF。它可以是数字导出或扫描。

如果您之前没有调用过该 API，[快速入门](https://openrouter.ai/docs/quickstart) 将显示第一个请求。

该代码适用于数字 PDF 和扫描，但结果取决于 PDF 是否具有文本层、扫描质量、解析器路径和模型。这些示例使用我们根据已知数据生成的五个测试 PDF，以便可以根据源检查每个单元格。它们是发票、季度报告、第二页的 58 行装运日志、扫描的采购订单以及带有合并单元格的故意粗略扫描。

## 第 1 步：如何发送 PDF 并取回行？

将以下内容保存为“extract_tables.py”。它将 PDF 作为文件内容部分发送，如我们的 [PDF 输入](https://openrouter.ai/docs/guides/overview/multimodal/pdfs) 页面中所述，并通过[结构化输出](https://openrouter.ai/docs/guides/features/structed-outputs) 请求与您的架构匹配的 JSON。将“strict”设置为 true 时，支持严格模式的提供程序会将输出保存到架构中，因此每一行的每个字段都具有正确的类型。支持因提供商而异，结构化输出页面显示如何仅路由到支持它的提供商。
```
import base64
import json
import os

import requests

API = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}

def rows_schema(fields):
    """Wrap the fields of one row in a strict schema for {"rows": [...]}."""
    return {
        "type": "object",
        "properties": {"rows": {"type": "array", "items": {
            "type": "object", "properties": fields,
            "required": list(fields), "additionalProperties": False}}},
        "required": ["rows"],
        "additionalProperties": False,
    }

def extract_table(pdf_path, schema, model="anthropic/claude-haiku-5.5",
                  engine=None, max_tokens=8000):
    with open(pdf_path, "rb") as f:
        data_url = "data:application/pdf;base64," + base64.b64encode(f.read()).decode()
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": "Extract every row of the table in this PDF. "
                                     "Include rows from every page. "
                                     "Return only rows that are in the document."},
            {"type": "file", "file": {"filename": os.path.basename(pdf_path),
                                      "file_data": data_url}},
        ]}],
        "response_format": {"type": "json_schema",
                            "json_schema": {"name": "table", "strict": True,
                                            "schema": schema}},
    }
    if engine:
        body["plugins"] = [{"id": "file-parser", "pdf": {"engine": engine}}]

    response = requests.post(API, headers=HEADERS, json=body, timeout=300)
    response.raise_for_status()
    data = response.json()
    choice = data["choices"][0]
    if choice["finish_reason"] == "length":
        raise ValueError(f"Output stopped at max_tokens={max_tokens}. "
                         "Raise it or split the PDF.")
    rows = json.loads(choice["message"]["content"])["rows"]
    if not rows:
        raise ValueError("No rows came back. If this PDF is a scan, use a model "
                         "that reads PDFs or engine='mistral-ocr'.")
    return rows, data["usage"]["cost"]

LINE_ITEMS = rows_schema({
    "sku": {"type": "string"},
    "description": {"type": "string"},
    "qty": {"type": "integer"},
    "unit_price": {"type": "number",
                   "description": "USD, no currency symbol or thousands separator"},
    "amount": {"type": "number",
               "description": "USD, no currency symbol or thousands separator"},
})
```
“return”之前的两项检查捕获了步骤 3 和 4 中涵盖的失败，因此将其保留。成本来自“usage.cost”，[使用情况核算](https://openrouter.ai/docs/cookbook/administration/usage-accounting) 包含在每个响应中。

在发票上运行该函数。
```
from extract_tables import extract_table, LINE_ITEMS

rows, cost = extract_table("invoice.pdf", LINE_ITEMS)
for row in rows[:3]:
    print(row)
print(f"{len(rows)} rows, ${cost:.5f}")
```

```
{'sku': 'NW-4100', 'description': 'Hex bolt M8x40', 'qty': 100, 'unit_price': 60.67, 'amount': 6067.0}
{'sku': 'NW-4107', 'description': 'Flange nut M8', 'qty': 2, 'unit_price': 41.72, 'amount': 83.44}
{'sku': 'NW-4114', 'description': 'Bearing 6204-2RS', 'qty': 10, 'unit_price': 52.59, 'amount': 525.9}
10 rows, $0.00067
```
通话持续了大约六秒钟。 PDF 显示 6,067.00，该行包含 6067.0，这是一个无需先清理即可累加的数字。字段描述删除了千位分隔符。

## 步骤 2：如何处理合并的单元格、括号和脚注？

PDF 表所需的大部分清理工作都可以进入模式的字段描述。我们的季度报告有一个“2026 财年”标题，跨越四个季度栏，括号中写着损失，两个细分市场名称（企业和硬件转售）上有脚注标记。字段描述处理括号和脚注标记。生成标头不需要描述，因为字段名称已经说明了每个值属于哪个季度。
```
from extract_tables import extract_table, rows_schema

THOUSANDS = {"type": "integer",
             "description": "Thousands of USD. A value in parentheses, like (1,204), is negative: -1204."}
QUARTERLY = rows_schema({
    "segment": {"type": "string", "description": "Segment name without footnote markers"},
    "q1": THOUSANDS, "q2": THOUSANDS, "q3": THOUSANDS, "q4": THOUSANDS, "fy_total": THOUSANDS,
})

rows, cost = extract_table("quarterly.pdf", QUARTERLY)
for row in rows:
    print(row)
```

```
{'segment': 'Inference API', 'q1': 1813, 'q2': 7299, 'q3': 1612, 'q4': 4422, 'fy_total': 15146}
{'segment': 'Enterprise', 'q1': 1563, 'q2': 2981, 'q3': 5544, 'q4': 7667, 'fy_total': 17755}
{'segment': 'Data products', 'q1': 3163, 'q2': 9658, 'q3': 2729, 'q4': 5854, 'fy_total': 21404}
{'segment': 'Hardware resale', 'q1': 3761, 'q2': -3878, 'q3': -9774, 'q4': -1776, 'fy_total': -11667}
{'segment': 'Professional services', 'q1': 8933, 'q2': 9511, 'q3': 7805, 'q4': 5946, 'fy_total': 32195}
{'segment': 'Total operating income', 'q1': 19233, 'q2': 25571, 'q3': 7916, 'q4': 22113, 'fy_total': 74833}
```
在硬件转售行中，(3,878) 返回为 -3878，并且脚注标记从两个段名称中消失。

沿着列运行的合并单元格的工作方式相同。在我们的粗略扫描中，每个类别单元格跨越六到九行。我们将该字段描述为“第一列中的类别。它是一个合并单元格，因此在它覆盖的每一行上重复它。”在我们的测试中，这足以让所有三个读取 PDF 的模型填写所有 30 行的类别。

## 步骤 3：我应该使用哪个解析器路由？

如果模型可以读取文件，我们就直接将 PDF 传递给它。如果不能，我们首先解析 PDF 并将结果发送给模型。文件解析器插件的“engine”设置选择解析器。当您在无法读取文件的模型上未设置它时，我们使用“mistral-ocr”，如 [PDF 输入](https://openrouter.ai/docs/guides/overview/multimodal/pdfs) 页面所述。根据 PDF 的外观选择路径。

- **读取 PDF 的模型。** 保持“engine”未设置。 Claude Haiku 5.5、GPT-6 Luna 和 Gemini 3.8 Flash 都读取文件，并且所有三个都处理了我们的两次扫描。 PDF 按输入令牌计费。
- **无法使用 OCR 读取 PDF 的模型。** 使用 `engine="mistral-ocr"`，或不设置。它首先在每个页面上运行光学字符识别 (OCR)，除了模型的代币之外，每 1,000 页 2 美元。
- **无法读取 PDF 的模型，带有免费解析器。** 仅当每个 PDF 都有文本层时才使用 `engine="cloudflare-ai"`。导出的发票和报告都有一份。扫描则不然。

这是使用每个解析器发送到“deepseek/deepseek-v4.1-flash”的扫描采购订单。该模型接受图像但不接受文件，因此 PDF 必须经过解析器。
```
from extract_tables import extract_table, LINE_ITEMS

# A model that can't read PDFs, with OCR in front of it
rows, cost = extract_table("scanned.pdf", LINE_ITEMS,
                           model="deepseek/deepseek-v4.1-flash", engine="mistral-ocr")
print(f"mistral-ocr: {len(rows)} rows, ${cost:.5f}")

# The same model with the free text parser
rows, cost = extract_table("scanned.pdf", LINE_ITEMS,
                           model="deepseek/deepseek-v4.1-flash", engine="cloudflare-ai")
```

```
mistral-ocr: 6 rows, $0.00211
ValueError: No rows came back. If this PDF is a scan, use a model that reads PDFs or engine='mistral-ocr'.
```
该“ValueError”来自步骤 1 中的空行检查。如果不进行检查，第二次调用将返回 200 OK，并带有“finish_reason: "stop"”和“{"rows": []}”。解析器在扫描中没有发现任何文本，并且模型正确地报告了一个空表。没有任何事情会引发错误，因此没有检查的管道会存储零行并移至下一个文件。这是两个无声失败中的第​​一个。我们的粗略扫描表现相同，在 30 行中得分为 0。

另外两个路线错误也导致失败。拼写错误的引擎名称会返回此错误。
```
400 {"error":{"message":"plugins.0.pdf.engine: Invalid input","code":400}}
```
本机引擎仅适用于读取文件的模型。无论如何，当我们在 DeepSeek V4.1 Flash 上设置“engine=”native“”时，请求成功一次，然后因提供程序错误而失败两次。
```
400 Provider returned error: "The request was rejected. Possible causes: input exceeds the model's maximum context length, or the request contains invalid parameters."
```
我们两次尝试都在同一模型上保持引擎未设置，因此不要在无法读取文件的模型上设置“native”。

## 步骤 4：为什么我的长桌回来时被切断了？

模型写入的每一行都会消耗输出令牌，因此长表需要较高的“max_tokens”。根据模型的不同，我们的 58 行发货日志使用了 2,500 到 7,700 个输出令牌，这使得最详细的模型在“extract_table”中的默认值 8,000 下几乎没有空间。计算出来每行有 43 到 133 个标记。对于长表，从每个预期行大约 150 个标记开始。然后测量您自己的行并保留“finish_reason”检查，因为计数因模型和模式而异。以下是限制太低时会发生的情况。
```
from extract_tables import extract_table, rows_schema

SHIPMENTS = rows_schema({
    "date": {"type": "string", "description": "YYYY-MM-DD"},
    "shipment_id": {"type": "string"},
    "origin": {"type": "string"},
    "destination": {"type": "string"},
    "weight_kg": {"type": "number", "description": "No thousands separator"},
    "status": {"type": "string"},
})

rows, cost = extract_table("shipments.pdf", SHIPMENTS, max_tokens=600)
```

```
ValueError: Output stopped at max_tokens=600. Raise it or split the PDF.
```
如果没有“finish_reason”检查，此请求会以两种方式之一失败。普通 JSON 解析会在截止数组上引发错误。
```
JSONDecodeError: Unterminated string starting at: line 1 column 627 (char 626)
```
第二种方法是另一种无声的失败。打开 [Response Healing](https://openrouter.ai/docs/guides/features/plugins/response-healing) 插件后，JSON 会进行解析，您会毫无例外地得到 5 行，每行 58 个。修复修复了输出的语法，它的文档警告说它无法恢复被“max_tokens”切断的输出，因此它无法添加模型从未写入的行。 `finish_reason` 检查捕获这两种情况。

## 步骤 5：如何将行写入 CSV？

每行都有模式中定义的键，因此“csv.DictWriter”可以从模式中获取其列名称并按原样写入行。 Excel直接打开结果。
```
import csv

from extract_tables import extract_table
# Define SHIPMENTS here, copied from step 4

rows, cost = extract_table("shipments.pdf", SHIPMENTS, model="openai/gpt-6-luna")
with open("shipments.csv", "w", newline="") as f:
    fieldnames = list(SHIPMENTS["properties"]["rows"]["items"]["properties"])
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote {len(rows)} rows to shipments.csv (${cost:.5f})")
```

```
Wrote 58 rows to shipments.csv ($0.00130)

date,shipment_id,origin,destination,weight_kg,status
2026-09-01,SHP-88200,Savannah,Valencia,8754.6,In transit
2026-09-01,SHP-88213,Busan,Los Angeles,2074.7,Customs hold
```
该表格转到第二页，其标题在那里重复。 CSV 有一个标题和全部 58 行。

## 您应该使用哪种模型？

我们对所有 5 个 PDF（共 6 页和 644 个单元格）运行了每条路线一次，并将每个单元格与生成 PDF 的数据进行了比较。每次运行都使用上面的“extract_table”函数和提示，以及我们的默认提供程序路由。每 1,000 个页面的成本是六个页面按比例放大的总“usage.cost”。模型和价格来自我们截至 2026 年 10 月 8 日的模型目录。这些结果描述的是该测试集，而不是一般的模型性能。

![在相同的五个 PDF、六个页面和 644 个单元格上的五个 PDF 表格提取路线的图表。 GPT-6 Luna：644 个单元格中有 644 个正确，每 1,000 页 0.77 美元，每个 PDF 10.1 秒。Claude Haiku 5.5：644，1.00 美元，8.4 秒。 Gemini 3.8 Flash：644，8.04 美元，16.4 秒。 DeepSeek V4.1 Flash 与 Mistra-ocr：642，3.09 美元，25.0 秒。 DeepSeek V4.1 Flash 与 cloudflare-ai：434，1.92 美元，21.3 秒。](https://openrouter.ai/blog/images/extract-tables-from-pdf-llm-routes.png)

在此测试集上，[GPT-6 Luna](https://openrouter.ai/openai/gpt-6-luna) 和 [Claude Haiku 5.5](https://openrouter.ai/anthropic/claude-haiku-5.5) 是使每个单元都正确的最便宜的路线，包括粗略扫描，并且两者的价格均为每百万输入代币 0.10 美元。这使得它们成为对您自己的 PDF 进行合理的首次测试。 [Gemini 3.8 Flash](https://openrouter.ai/google/gemini-3.8-flash) 同样准确，但相同文件的每页成本是其八到十倍。其定价为每百万输入代币 1.50 美元，于 2026 年 10 月 21 日折扣至 0.75 美元。

OCR 路线的成本比 DeepSeek 的低代币价格所暗示的要高，因为每 1,000 个页面的 OCR 2 美元会添加到每个请求中，您可以在“usage.cost”中看到它。它的两次遗漏是关于企业和硬件转售的脚注标记，尽管架构要求将它们删除，但它仍然保留了它们。免费解析器正确解析了所有三个数字 PDF，但两次扫描都完全错误。

成本列是从每条路线的六页中推断出来的。使用它来比较路线，然后在选择一个 PDF 样本之前使用[黄金评估集](https://openrouter.ai/blog/tutorials/building-a-golden-eval-dataset-from-production-traffic/) 测量准确性、时间和成本，因为页面越密集，成本就越高，并且其他布局的行为可能会有所不同。

## PDF 库何时足够？

如果您的所有 PDF 都是数字的，并且每个表格都有一个标题行，则 [pdfplumber](https://github.com/jsvine/pdfplumber) 等免费库将找到这些表格。我们在相同的文件上运行它。它找到了三个数字 PDF 中的每个表格，并将每个单元格作为字符串返回，例如“6,067.00”或“(3,878)”。季度报告的两级标题以两行形式返回，合并单元格中为“无”，装运日志以两个单独的表格形式返回，每页一个。它在两次扫描中都没有发现任何内容，因为扫描没有可供读取的文本层。

因此，当您的表格很简单且 PDF 是数字的时，库就足够了。一旦您为合并的标题、分页符和数字格式编写清理代码，第 2 步中的架构的维护工作量就会减少。

## TypeScript 中的相同请求

任何语言的请求正文都是相同的。将其保存为“extract.mjs”，并在 Node.js 18 或更高版本上使用“node extract.mjs Invoice.pdf”运行它。
```
import { readFileSync } from "node:fs";
import { basename } from "node:path";

const path = process.argv[2];
const fileData = `data:application/pdf;base64,${readFileSync(path).toString("base64")}`;

const money = { type: "number", description: "USD, no currency symbol or thousands separator" };
const schema = {
  type: "object",
  properties: { rows: { type: "array", items: {
    type: "object",
    properties: { sku: { type: "string" }, description: { type: "string" },
                  qty: { type: "integer" }, unit_price: money, amount: money },
    required: ["sku", "description", "qty", "unit_price", "amount"],
    additionalProperties: false } } },
  required: ["rows"],
  additionalProperties: false,
};

const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
  method: "POST",
  headers: { Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
             "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "openai/gpt-6-luna",
    messages: [{ role: "user", content: [
      { type: "text", text: "Extract every row of the table in this PDF. Include rows from every page. Return only rows that are in the document." },
      { type: "file", file: { filename: basename(path), file_data: fileData } },
    ] }],
    response_format: { type: "json_schema", json_schema: { name: "table", strict: true, schema } },
  }),
});
if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
const data = await res.json();
const choice = data.choices[0];
if (choice.finish_reason !== "stop") throw new Error(`Unexpected finish_reason: ${choice.finish_reason}`);
const { rows } = JSON.parse(choice.message.content);
if (rows.length === 0) throw new Error("No rows came back.");
console.log(rows.length + " rows, finish_reason=" + choice.finish_reason + ", $" + data.usage.cost);
```

```
10 rows, finish_reason=stop, $0.00020275
```
该脚本检查 HTTP 状态，然后应用与 Python 版本相同的两项检查。除非“finish_reason”为“stop”并且“rows”至少有一行，否则它将停止。

## 结论

使用 LLM 从 PDF 中提取表格需要一个请求，其中 PDF 作为文件部分以及描述一行的严格模式。在我们的测试中，准确性来自于直接读取 PDF 的模型，而风险来自于 PDF 所采取的路线。扫描上的文本解析器和长表上的令牌限制都返回看起来正常的响应。 `extract_table` 中的两个检查捕获这两种情况，因此请将它们保留在您运行的代码的任何版本中。在确定路线之前，请运行您自己的 PDF 示例并比较行数、时间和“使用成本”。

## 常见问题

### LLM 可以阅读扫描的 PDF 吗？

是的，如果模型直接读取 PDF 或者您通过 Mistra-ocr 解析器发送它。读取 PDF 的所有三个模型都正确扫描了我们的两次扫描，使用 Mistra-ocr 的 DeepSeek V4.1 Flash 也是如此。 Cloudflare-ai 等文本解析器在扫描时返回空结果，没有错误，因为扫描没有文本层。

### 从 1,000 页中提取表格需要多少钱？

在我们的六个测试页上，按照 2026 年 10 月的价格计算，GPT-6 Luna 的成本约为每 1,000 页 0.77 美元，Claude Haiku 5.5 的成本约为每 1,000 页 1.00 美元。 mistra-ocr 背后的模型每 1,000 页 OCR 增加 2 美元。检查当前价格并从您自己的第一个请求中读取“usage.cost”，因为密集的表成本更高。

### 模型会发明 PDF 中没有的行吗？

我们在 5 个测试 PDF 的 25 个提取中没有看到虚构的行，但这并不排除其他文档中出现虚构行的情况。丢失行是更大的风险，这是由于输出在令牌限制处被切断或解析器找不到文本而引起的。将行数或小计与文档进行比较。

### 从 PDF 中提取表格的最佳 Python 库是什么？

对于具有简单标题的数字 PDF，pdfplumber 是免费的，可以找到我们数字测试文件中的每个表格。它将每个单元格作为文本返回，将多级标题拆分为单独的行，并且在我们的扫描中找不到任何内容。 Camelot 和 Tabula 是其他免费选项，但我们没有在本指南中测试它们。

## 后续步骤

- [PDF 输入](https://openrouter.ai/docs/guides/overview/multimodal/pdfs) 涵盖通过 URL（而不是 base64）发送 PDF、解析器引擎及其价格以及文件注释，让您可以将解析结果发回，这样您就无需支付两次解析相同 PDF 的费用。
- [结构化输出](https://openrouter.ai/docs/guides/features/structured-outputs) 解释了严格的 JSON 模式以及如何仅路由到支持它们的提供程序。
- [预设](https://openrouter.ai/docs/guides/features/presets) 将模型、系统提示和提供商设置存储在一个名称下。将提取指令放在预设的系统提示符中，并从每个服务调用“@preset/your-name”，因此它们都使用相同的配置。继续在每个请求中以“response_format”发送模式，因为预设文档不会将其列在预设存储的设置中。我们的[预设指南](https://openrouter.ai/blog/tutorials/presets/) 逐步完成设置。
- 对于积压的 PDF，[Batch API](https://openrouter.ai/docs/batch-quickstart) 异步运行相同的请求，通常在 24 小时内。 `anthropic/claude-haiku-5.5:batch` 和 `openai/gpt-6-luna:batch` 的价格是每个代币标准价格的一半。批量请求将 PDF 作为公共 URL，而不是 base64，因此首先托管文件。文件 URL 仅适用于列出文件输入的模型，因此步骤 3 中带有 milstra-ocr 路由的 DeepSeek 无法批量使用，并且在 OpenAI 模型上，它们只能通过 Responses API 工作。我们没有测量本指南的批量运行。
- 如果您在 LangChain 中构建此内容，[ChatOpenRouter](https://openrouter.ai/blog/tutorials/langchain-chatopenrouter-setup/) 会传递 PDF 输入并使用“with_structed_output”支持严格的 JSON 模式。
- 如果您的源文档是图像而不是 PDF，[如何将图像发送到 LLM](https://openrouter.ai/blog/tutorials/send-image-to-llm/) 涵盖了图像内容部分。
