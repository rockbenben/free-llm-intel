---
vendor: openrouter
title: How to Extract Tables from a PDF with an LLM
original_title: How to Extract Tables from a PDF with an LLM
url: https://openrouter.ai/blog/tutorials/extract-tables-from-pdf-llm
date: 2026-10-29
lang: en
captured: 2026-10-29
extractor: readability-v1
status: ok
body_sha: 6f336384ca64
---

# How to Extract Tables from a PDF with an LLM

OpenRouter ·10/29/2026

![How to Extract Tables from a PDF with an LLM](https://openrouter.ai/blog/images/extract-tables-from-pdf-llm.png)![How to Extract Tables from a PDF with an LLM](https://openrouter.ai/blog/images/extract-tables-from-pdf-llm-dark.png)

To extract tables from a PDF with an LLM, send the PDF to a [model that can read files](https://openrouter.ai/docs/guides/overview/multimodal/pdfs), together with a [strict JSON schema](https://openrouter.ai/docs/guides/features/structured-outputs) that describes one row of the table. The model returns typed rows. Quantities come back as integers, a loss written as (3,878) comes back as -3878, and a table that runs across two pages comes back as one list.

We tested this on five PDFs, two of them scans. Every model that read the PDF directly got all 644 cells right. The failures in our tests came from the route the PDF took to reach the model, and two of them returned a normal response with no error.

## Tl;dr

- A strict JSON schema for one row turns a PDF table into typed rows, and field descriptions handle cleanup such as negatives in parentheses and footnote markers.
- Models that read PDFs handled both digital files and scans in our tests. A model that can’t read PDFs needs the `mistral-ocr` parser for scans.
- A scan sent through the free `cloudflare-ai` parser returns zero rows with no error, so reject empty results.
- Long tables can stop at the output token limit, so reject any response whose `finish_reason` is “length”.

## Before you start

You need the following to run the examples.

- An OpenRouter account with credits, and an [API key](https://openrouter.ai/settings/keys) stored in the `OPENROUTER_API_KEY` environment variable. The models in this guide are paid.
- Python 3.10 or later and the `requests` package (`pip install requests`).
- Node.js 18 or later, but only for the TypeScript version near the end.
- A PDF that contains a table. It can be a digital export or a scan.

If you haven’t called the API before, the [quickstart](https://openrouter.ai/docs/quickstart) shows a first request.

The code works with digital PDFs and scans, but results depend on whether the PDF has a text layer, the scan quality, the parser route and the model. The examples use five test PDFs that we generated from known data, so that every cell could be checked against the source. They are an invoice, a quarterly report, a 58-row shipment log that runs onto a second page, a scanned purchase order, and a deliberately rough scan with merged cells.

## Step 1: How do I send a PDF and get rows back?

Save the following as `extract_tables.py`. It sends the PDF as a file content part, as described on our [PDF inputs](https://openrouter.ai/docs/guides/overview/multimodal/pdfs) page, and asks for JSON that matches your schema through [structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs). With `strict` set to true, providers that support strict mode hold the output to the schema, so every row has every field with the right type. Support varies by provider, and the structured outputs page shows how to route only to providers that support it.

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

The two checks before the `return` catch the failures covered in steps 3 and 4, so leave them in. The cost comes from `usage.cost`, which [usage accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting) includes in every response.

Run the function on the invoice.

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

The call took about six seconds. The PDF shows 6,067.00, and the row holds 6067.0, which is a number you can add up without cleaning it first. The field description is what removed the thousands separator.

## Step 2: How do I handle merged cells, parentheses and footnotes?

Most of the cleanup a PDF table needs can go into the field descriptions of the schema. Our quarterly report has a “Fiscal 2026” header that spans four quarter columns, losses written in parentheses, and footnote markers on two segment names (Enterprise and Hardware resale). Field descriptions handle the parentheses and the footnote markers. The spanning header needs no description, because the field names already say which quarter each value belongs to.

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

In the Hardware resale row, (3,878) came back as -3878, and the footnote markers are gone from both segment names.

A merged cell that runs down a column works the same way. In our rough scan, each Category cell spans six to nine rows. We described that field as “The category in the first column. It is a merged cell, so repeat it on every row it covers.” In our test, that was enough for all three models that read PDFs to fill in the category on all 30 rows.

## Step 3: Which parser route should I use?

If a model can read files, we pass the PDF to it directly. If it can’t, we parse the PDF first and send the model the result. The `engine` setting of the file-parser plugin chooses the parser. When you leave it unset on a model that can’t read files, we use `mistral-ocr`, as the [PDF inputs](https://openrouter.ai/docs/guides/overview/multimodal/pdfs) page states. Choose the route by what your PDFs look like.

- **A model that reads PDFs.** Leave `engine` unset. Claude Haiku 5.5, GPT-6 Luna and Gemini 3.8 Flash all read files, and all three handled both of our scans. The PDF is billed as input tokens.
- **A model that can’t read PDFs, with OCR.** Use `engine="mistral-ocr"`, or leave it unset. It runs optical character recognition (OCR) on each page first, for $2 per 1,000 pages on top of the model’s tokens.
- **A model that can’t read PDFs, with the free parser.** Use `engine="cloudflare-ai"` only if every PDF has a text layer. Exported invoices and reports have one. Scans don’t.

Here is the scanned purchase order sent to `deepseek/deepseek-v4.1-flash` with each parser. That model accepts images but not files, so the PDF has to go through a parser.

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

That `ValueError` comes from the empty-rows check in step 1. Without the check, the second call returns 200 OK with `finish_reason: "stop"` and `{"rows": []}`. The parser found no text on the scan, and the model correctly reported an empty table. Nothing raises an error, so a pipeline without the check stores zero rows and moves on to the next file. This is the first of the two silent failures. Our rough scan behaved the same way and scored 0 of 30 rows.

Two other route mistakes fail loudly. A misspelled engine name returns this error.

```
400 {"error":{"message":"plugins.0.pdf.engine: Invalid input","code":400}}
```

The native engine is meant only for models that read files. When we set `engine="native"` on DeepSeek V4.1 Flash anyway, the request worked once and then failed twice with a provider error.

```
400 Provider returned error: "The request was rejected. Possible causes: input exceeds the model's maximum context length, or the request contains invalid parameters."
```

Leaving engine unset on the same model worked both times we tried it, so don’t set `native` on a model that can’t read files.

## Step 4: Why did my long table come back cut off?

Every row the model writes costs output tokens, so a long table needs a high `max_tokens`. Our 58-row shipment log used between 2,500 and 7,700 output tokens depending on the model, which left the most verbose model little room under the default of 8,000 in `extract_table`. That works out to between 43 and 133 tokens per row. For long tables, start with about 150 tokens per expected row. Then measure your own rows and keep the `finish_reason` check, since the count varies by model and schema. Here is what happens when the limit is too low.

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

Without the `finish_reason` check, this request fails in one of two ways. Plain JSON parsing raises an error on the cut-off array.

```
JSONDecodeError: Unterminated string starting at: line 1 column 627 (char 626)
```

The second way is the other silent failure. With the [Response Healing](https://openrouter.ai/docs/guides/features/plugins/response-healing) plugin turned on, the JSON parses and you get 5 rows of 58 with no exception. Healing repairs the syntax of the output, and its docs warn that it can’t recover output cut off by `max_tokens`, so it can’t add the rows the model never wrote. The `finish_reason` check catches both cases.

## Step 5: How do I write the rows to CSV?

Every row has the keys defined in the schema, so `csv.DictWriter` can take its column names from the schema and write the rows as they are. Excel opens the result directly.

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

The table ran onto a second page with its header repeated there. The CSV has one header and all 58 rows.

## Which model should you use?

We ran each route once over all five PDFs, which came to six pages and 644 cells, and compared every cell with the data the PDFs were generated from. Every run used the `extract_table` function and prompt above, with our default provider routing. The cost per 1,000 pages is the total `usage.cost` for the six pages, scaled up. The models and prices are from our model catalog as of October 8, 2026. These results describe this test set, not model performance in general.

![Chart of five PDF table extraction routes on the same five PDFs, six pages and 644 cells. GPT-6 Luna: 644 of 644 cells correct, $0.77 per 1,000 pages, 10.1 seconds per PDF. Claude Haiku 5.5: 644, $1.00, 8.4 s. Gemini 3.8 Flash: 644, $8.04, 16.4 s. DeepSeek V4.1 Flash with mistral-ocr: 642, $3.09, 25.0 s. DeepSeek V4.1 Flash with cloudflare-ai: 434, $1.92, 21.3 s.](https://openrouter.ai/blog/images/extract-tables-from-pdf-llm-routes.png)

On this test set, [GPT-6 Luna](https://openrouter.ai/openai/gpt-6-luna) and [Claude Haiku 5.5](https://openrouter.ai/anthropic/claude-haiku-5.5) were the cheapest routes that got every cell right, including on the rough scan, and both list at $0.10 per million input tokens. That makes them a reasonable first test on your own PDFs. [Gemini 3.8 Flash](https://openrouter.ai/google/gemini-3.8-flash) was just as accurate but cost eight to ten times as much per page on the same files. Its list price is $1.50 per million input tokens, discounted to $0.75 on October 21, 2026.

The OCR route costs more than DeepSeek’s low token price suggests, because the $2 per 1,000 pages for OCR is added to every request, and you can see it in `usage.cost`. Its two misses were the footnote markers on Enterprise and Hardware resale, which it kept even though the schema asked for them to be removed. The free parser got all three digital PDFs right and both scans completely wrong.

The cost column is extrapolated from six pages per route. Use it to compare routes, then measure accuracy, time and cost on a sample of your own PDFs before you choose one, using a [golden eval set](https://openrouter.ai/blog/tutorials/building-a-golden-eval-dataset-from-production-traffic/), because denser pages cost more and other layouts may behave differently.

## When is a PDF library enough?

If all your PDFs are digital and each table has a single header row, a free library such as [pdfplumber](https://github.com/jsvine/pdfplumber) will find the tables. We ran it on the same files. It found every table in the three digital PDFs and returned each cell as a string, such as ‘6,067.00’ or ‘(3,878)’. The quarterly report’s two-level header came back as two rows with `None` in the merged cells, and the shipment log came back as two separate tables, one per page. It found nothing in either scan, because a scan has no text layer to read.

So a library is enough when your tables are simple and your PDFs are digital. Once you’re writing cleanup code for merged headers, page breaks and number formats, the schema from step 2 is less work to maintain.

## The same request in TypeScript

The request body is the same in any language. Save this as `extract.mjs` and run it with `node extract.mjs invoice.pdf` on Node.js 18 or later.

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

The script checks the HTTP status and then applies the same two checks as the Python version. It stops unless `finish_reason` is “stop” and `rows` has at least one row.

## Conclusion

Extracting a table from a PDF with an LLM takes one request, with the PDF as a file part and a strict schema that describes one row. In our tests, the accuracy came from a model reading the PDF directly, and the risk came from the route the PDF took. A text parser on a scan and a token limit on a long table both returned responses that looked normal. The two checks in `extract_table` catch both cases, so keep them in any version of the code you run. Before you settle on a route, run a sample of your own PDFs through it and compare the rows, the time and `usage.cost`.

## Frequently asked questions

### Can an LLM read a scanned PDF?

Yes, if the model reads the PDF directly or you send it through the mistral-ocr parser. All three models that read PDFs got both of our scans right, and so did DeepSeek V4.1 Flash with mistral-ocr. A text parser such as cloudflare-ai returns an empty result for a scan with no error, because a scan has no text layer.

### How much does it cost to extract tables from 1,000 pages?

On our six test pages, at October 2026 prices, the cost scaled to about $0.77 per 1,000 pages with GPT-6 Luna and $1.00 with Claude Haiku 5.5. A model behind mistral-ocr adds $2 per 1,000 pages for OCR. Check current prices and read `usage.cost` from your own first requests, because dense tables cost more.

### Will the model invent rows that aren’t in the PDF?

We didn’t see invented rows in 25 extractions of our five test PDFs, but that doesn’t rule them out on other documents. Missing rows were the bigger risk, caused by output cut off at the token limit or a parser that found no text. Compare the row count or a subtotal against the document.

### What’s the best Python library to extract tables from a PDF?

For digital PDFs with simple headers, pdfplumber is free and found every table in our digital test files. It returns each cell as text, split multi-level headers into separate rows, and found nothing in our scans. Camelot and Tabula are other free options, but we didn’t test them for this guide.

## Next steps

- [PDF inputs](https://openrouter.ai/docs/guides/overview/multimodal/pdfs) covers sending PDFs by URL instead of base64, the parser engines and their prices, and file annotations, which let you send parsed results back so you don’t pay to parse the same PDF twice.
- [Structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs) explains strict JSON schemas and how to route only to providers that support them.
- [Presets](https://openrouter.ai/docs/guides/features/presets) store the model, the system prompt and provider settings under one name. Put the extraction instruction in the preset’s system prompt and call `@preset/your-name` from every service, so they all use the same configuration. Keep sending the schema in `response_format` with each request, because the presets docs don’t list it among the settings a preset stores. Our [presets guide](https://openrouter.ai/blog/tutorials/presets/) walks through the setup.
- For a backlog of PDFs, the [Batch API](https://openrouter.ai/docs/batch-quickstart) runs the same requests asynchronously, usually within 24 hours. `anthropic/claude-haiku-5.5:batch` and `openai/gpt-6-luna:batch` list at half the standard per-token price. Batch requests take PDFs as public URLs, not base64, so host the files first. File URLs work only on models that list file input, so the DeepSeek with mistral-ocr route from step 3 isn’t available in batch, and on OpenAI models they work only through the Responses API. We didn’t measure batch runs for this guide.
- If you build this inside LangChain, [ChatOpenRouter](https://openrouter.ai/blog/tutorials/langchain-chatopenrouter-setup/) passes PDF inputs through and supports strict JSON schemas with `with_structured_output`.
- If your source documents are images rather than PDFs, [How to send an image to an LLM](https://openrouter.ai/blog/tutorials/send-image-to-llm/) covers the image content part.
