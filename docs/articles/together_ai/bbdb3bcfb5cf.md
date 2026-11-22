---
vendor: together_ai
title: Qwen4 Max 已上线 Together AI
original_title: 
url: https://www.together.ai/blog/qwen4-max
date: 2026-11-21
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 6b47d97f5185
---

# Qwen4 Max 现已在 Together AI 上线

阿里巴巴的旗舰 Qwen 模型在 2026 年 11 月 22 日之前享受 30% 折扣。我们把一份 bug 报告和整个 Tornado 仓库放进同一次请求，看看 100 万 token 的上下文窗口值多少、又要花多少钱。

- 本文链接：[在 playground 中试用 Qwen4 Max](https://api.together.ai/playground/v2/chat/Qwen/Qwen4-Max) [Qwen4 Max 模型页](https://www.together.ai/models/qwen4-max) [阿里巴巴的公告](https://www.alibabacloud.com/en/press-room/alibaba-unveils-qwen4-max)

摘要

- **Together AI 上的 Qwen4 Max：** 阿里巴巴的旗舰 Qwen 模型已在 Together Serverless Inference 上提供，上下文窗口为 100 万 token。
- **我们测试了什么：** Qwen4 Max 在一次请求中接收了一份 bug 报告和 Tornado 仓库的全部 344 个文件，它给出的补丁通过了维护者的测试。
- **促销价格：** 在 2026 年 11 月 22 日之前，每 100 万输入 token 收费 1.05 美元，每 100 万缓存输入 token 收费 0.0525 美元，每 100 万输出 token 收费 3.15 美元。
- **调用前须知：** 请求必须使用流式方式，思考默认开启，思考 token 按输出 token 计费。

我们把一份 bug 报告和整个代码库放在一次请求里交给了 [Qwen4 Max](https://www.together.ai/models/qwen4-max)。代码库是 Python Web 框架 Tornado：全部 344 个文件、652,519 个 token。模型没有使用任何工具，我们也没有预先挑选相关文件或做检索。72 秒后它返回了一个补丁，该补丁通过了 Tornado 维护者为这个 bug 编写的测试。这次请求花费 69 美分。

它还在仓库的其他位置找到了一处先例。bug 报告从未提到 `tornado/iostream.py`，但模型指出了那里的代码——那些代码已经按它的补丁所需的方式处理了错误。Tornado 维护者在他们自己的修复中也引用了同一段代码。

Qwen4 Max 是阿里巴巴的旗舰 Qwen 模型。它今天已在 Together AI 上线，并在 2026 年 11 月 22 日之前享受 30% 折扣。

## 测试

Tornado 是一个开源 Python Web 框架。其仓库包含约 340 个代码、测试与文档文件，可以放进 Qwen4 Max 的上下文窗口，而且远多于任何人会手动粘贴到 prompt 里的内容。我们选取了维护者于 2026 年 11 月 18 日提交的一个修复——那是在 Qwen4 Max 发布两天之后——并针对该提交之前的仓库状态进行测试。

这只是一个例子，用来说明单次调用能做什么、需要多少成本。

这个 bug 位于 Tornado 的 websocket 代码中。当连接关闭而仍有消息未发送时，每个未被 await 的 `write_message()` 调用都会记录一条错误，尽管 await 它是可选的。我们把该检出目录中的每个文本文件作为同一个 prompt 发送，并附上一份只描述现象、不说明原因的 bug 报告：

> 当连接关闭时，write_message 会记录 "Task exception was never retrieved"：当 websocket 连接在仍有消息未发送的情况下关闭（例如客户端发送完消息和一个 FIN，或重置了连接，却没有读取回复）时，每个结果未被 await 的 write_message() 调用都会在 ERROR 级别记录 "Task exception was never retrieved"。await write_message 返回的 Future 是可选的，因此未 await 的调用不应记录任何内容。真正 await 它的调用方仍应收到 WebSocketClosedError。

我们要求模型给出原因和补丁。以下是重放的请求：

### 返回了什么

首个 token 在 54 秒后到达，回复在 72 秒时完成。Qwen4 Max 把错误定位到 `tornado/websocket.py` 中的 `WebSocketProtocol13.write_message`。该方法把每次写入包在一个 task 里。当连接关闭时，该 task 会以异常失败，而没有任何人必须去收集这个异常，Python 便会记录为 "Task exception was never retrieved"。

模型的补丁把该异常标记为已取回。这样不会记录任何内容，而真正 await 写入的调用方仍会收到错误：

```
-        return asyncio.ensure_future(wrapper())
+        task = asyncio.ensure_future(wrapper())
+
+        # Awaiting the returned Future is optional, so an error nobody looks
+        # at must not be reported as "Task exception was never retrieved".
+        # Retrieving it here leaves it in place for callers that do await.
+        def _mark_retrieved(t: "asyncio.Task[None]") -> None:
+            if not t.cancelled():
+                t.exception()
+
+        task.add_done_callback(_mark_retrieved)
+        return task
```

正是这处先例让这个补丁看起来像是属于该项目的一部分。模型的解释称，修复应当采用 `BaseIOStream.write` 已为其自身的 future 所做的做法。该方法位于 `tornado/iostream.py`，比 websocket 代码低一层，并用同样的方式解决了同样的问题。维护者的提交也做了同样的对照。

![一张由 344 个方格组成的网格，每格对应 Tornado 仓库中的一个文件，并按目录分组。tornado 目录中的两个方格被高亮并用一条线连接：bug 所在的 websocket.py，以及模型指出的先例 iostream.py。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b01fded989d54b2b151f5cf_qwen4-max-repo-map.png)

没有人替它挑选这些文件。全部 344 个文件都被送入，而模型找到了其中起关键作用的两个。

### 我们如何验证

Tornado 维护者在他们的修复中新增了两个回归测试：一个针对未 await 的写入，一个针对已 await 的写入。在修复前的代码上，第一个测试会失败；应用模型的补丁后，两个测试都通过。随后我们在有该补丁的情况下运行了 Tornado 的完整测试套件，共 1,673 个测试，无一失败。

### 成本是多少

按促销价计算，这次请求约为 69 美分，几乎全部来自 652,519 个输入 token。按标价计算则为 98 美分。

再次发送同一仓库的成本要低得多。Together AI 会自动缓存 prompt 输入，在促销期间缓存输入的价格为每百万 token 0.0525 美元。当我们重复一次约 630,000 token 的请求时，几乎全部命中缓存。首个 token 在 8 秒后到达，而不是 54 秒，输入成本约为 3 美分，而不是 66 美分。

## 关于 Qwen4 Max

阿里巴巴于 2026 年 11 月 16 日发布 Qwen4 Max，并称其为 Qwen 系列迄今最强的模型。它将该模型定位为长程 agent 工作，包括跨大型仓库的编码，这正是我们测试的任务类型。

Qwen4 Max 是一个稀疏混合专家（MoE）模型，拥有 2.4 万亿参数，每个 token 激活其中 710 亿。在阿里巴巴自己的行业任务基准 Work360（覆盖 721 个专业领域）上，阿里巴巴称其整体表现优于 Qwen3.8 Max，在高推理强度下使用的 token 少 35%，每个任务的平均成本约低 60%。这些是阿里巴巴的数据，[其公告](https://www.alibabacloud.com/en/press-room/alibaba-unveils-qwen4-max)中有细节。

## 在 Together AI 上运行

Qwen4 Max 已在 Together Serverless Inference 上提供，模型字符串为 `Qwen/Qwen4-Max`。下面的脚本会像我们的测试那样，把整个仓库和一份 bug 报告放进一次请求。你需要 Together Python SDK（`pip install together`）、一个 `TOGETHER_API_KEY`、该仓库的本地克隆，以及保存为 `bug_report.md` 的 bug 报告。它会发送 git 跟踪的每个文本文件，因此请先检查仓库中是否有密钥。

```
import subprocess
from pathlib import Path

from together import Together

repo = Path("tornado")
bug_report = Path("bug_report.md").read_text()

# Every file git tracks, skipping the ones that aren't text
names = subprocess.check_output(
    ["git", "-C", str(repo), "ls-files"], text=True
).splitlines()
files = []
for name in names:
    try:
        files.append(f"=== FILE: {name} ===\n{(repo / name).read_text()}\n")
    except UnicodeDecodeError:
        continue

client = Together()

stream = client.chat.completions.create(
    model="Qwen/Qwen4-Max",
    messages=[
        {
            "role": "system",
            "content": f"This is a complete repository, {len(files)} files.\n\n"
            + "".join(files),
        },
        {
            "role": "user",
            "content": f"Here is a bug report.\n\n{bug_report}\n\n"
            "Explain the cause, then write a patch.",
        },
    ],
    stream=True,
)

for chunk in stream:
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta
    # delta.reasoning carries the model's thinking, delta.content the answer
    if delta.content:
        print(delta.content, end="", flush=True)
```

其中有两点为该模型所特有。请求必须设置 `stream=True`，因为 Together AI 上的 Qwen4 Max 只接受流式请求。思考默认开启，因此模型的推理会先通过 `delta.reasoning` 流式返回，在回答开始之前有一段停顿。思考 token 计为输出 token。若要在简单请求中跳过思考，可传入 `reasoning={"enabled": False}`。

若不想写代码，可以在 [playground](https://api.together.ai/playground/v2/chat/Qwen/Qwen4-Max) 中试用。[模型页](https://www.together.ai/models/qwen4-max) 有同样的细节。

## 常见问题

### Qwen4 Max 在 Together AI 上的价格是多少？

Together AI 上 Qwen4 Max 的标价为每 100 万输入 token 1.50 美元、每 100 万输出 token 4.50 美元、每 100 万缓存输入 token 0.075 美元。在 2026 年 11 月 22 日之前享受 30% 折扣：1.05、3.15 和 0.0525 美元。思考 token 计为输出 token。

### Qwen4 Max 在 Together AI 上的上下文窗口有多大？

Qwen4 Max 在 Together AI 上的上下文窗口为 100 万 token。在我们的测试中，一次含 652,519 个输入 token 的请求在 54 秒后返回首个 token。

### Qwen4 Max 接受图片吗？

接受，Qwen4 Max 在 Together AI 上接受文本与图片输入并返回文本。请按[视觉文档](https://docs.together.ai/docs/inference/vision/overview)的说明，把每张图片作为消息内容中的 `image_url` 块发送。

### 为什么我的 Qwen4 Max 请求在未流式时失败？

Together AI 上的 Qwen4 Max 只接受流式请求。不带 `"stream": true` 的请求会返回 400 错误，错误码为 `streaming_required`。请在 SDK 中设置 `stream=True`，或在请求体中使用 `"stream": true`，并从流中读取回复。

### 如何在 Qwen4 Max 上关闭思考？

在 Python SDK 中传入 `reasoning={"enabled": False}`，或在请求体中使用 `"reasoning": {"enabled": false}`，即可关闭 Qwen4 Max 的思考。思考默认开启，并会先于答案在 `reasoning` 字段中返回。若要在困难问题上获得更多思考，可将 `reasoning_effort` 设为 `"max"`。

### Qwen4 Max 支持工具调用吗？

支持，Qwen4 Max 在 Together AI 上通过标准的 `tools` 参数支持工具调用，一次可返回多个调用。

### prompt 缓存对 Qwen4 Max 有效吗？

有效，Together AI 上 Qwen4 Max 的 prompt 缓存是自动的，缓存输入 token 的标价为每 100 万 0.075 美元。在我们的测试中，重复一次 630,000 token 的请求几乎全部命中缓存，首个 token 在 8 秒后到达，而不是 54 秒。缓存是尽力而为，并非每次重复都会命中。

### 我可以微调 Qwen4 Max 或在其上使用专属 endpoint 吗？

不能，Qwen4 Max 目前在 Together AI 上仅为无服务器服务，不提供微调。阿里巴巴表示后续会推出 Qwen4 系列中较小的开放权重模型。
