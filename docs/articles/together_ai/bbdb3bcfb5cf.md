---
vendor: together_ai
title: Qwen4 Max 已上线 Together AI
original_title: 
url: https://www.together.ai/blog/qwen4-max
date: 2026-11-21
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: mt
status: translated
body_sha: c6c05864da9c
---

所有博客文章

模型库

发表于 11/21/2026

# Qwen4 Max 已在 Together AI 上线

截至 2026 年 11 月 22 日，阿里巴巴的旗舰 Qwen 型号可享受 30% 的折扣。我们在一次请求中向其提供了错误报告和整个 Tornado 存储库，以了解 1M 代币上下文窗口的价值和成本。

- 作者桑尼·汗
- 目录[40+ 型号选择用于生产...40+ 型号选择用于生产...40+ 型号选择用于生产...](https://www.together.ai/blog/qwen4-max)
- 本文链接【Qwen4 Max在游乐场】(https://api.together.ai/playground/v2/chat/Qwen/Qwen4-Max)【Qwen4 Max型号页面】(https://www.together.ai/models/qwen4-max)【阿里巴巴公告】(https://www.alibabacloud.com/en/press-room/alibaba-unveils-qwen4-max)

总结

- **Together AI 上的 Qwen4 Max：** 阿里巴巴的旗舰 Qwen 模型可在 Together Serverless Inference 上使用，具有 1M 代币上下文窗口。
- **我们测试的内容：** Qwen4 Max 在一次请求中获取了一份错误报告和 Tornado 存储库的所有 344 个文件，并且其补丁通过了维护人员的测试。
- **销售定价：** 截至 2026 年 11 月 22 日，每 100 万个输入代币的成本为 1.05 美元，每 100 万个缓存输入代币的成本为 0.0525 美元，每 100 万个输出代币的成本为 3.15 美元。
- **在调用它之前：** 请求必须进行流式传输，默认情况下思考处于开启状态，思考令牌计为输出令牌。

我们在一次请求中向 [Qwen4 Max](https://www.together.ai/models/qwen4-max) 提供了一份错误报告和整个代码库。代码库是 Tornado，Python Web 框架：所有 344 个文件，652,519 个令牌。该模型没有工具，我们没有选择相关文件或首先运行检索步骤。七十二秒后，它返回了一个补丁，并且该补丁通过了 Tornado 维护人员为该错误编写的测试。该请求花费了 69 美分。

它还在存储库的其他地方找到了先例。错误报告从未提及 `tornado/iostream.py`，但模型指出那里的代码已经按照补丁所需的方式处理错误。 Tornado 的维护者在他们自己的修复中引用了相同的代码。

Qwen4 Max是阿里巴巴的旗舰Qwen机型。该产品现已在 Together AI 上上线，截至 2026 年 11 月 22 日可享受 30% 折扣。

## 测试

Tornado 是一个开源 Python Web 框架。其存储库包含大约 340 个代码、测试和文档文件。这适合 Qwen4 Max 的上下文窗口，而且远远超过任何人手动粘贴到提示中的效果。我们选择了维护者于 2026 年 11 月 18 日（即 Qwen4 Max 发布两天后）提交的修复程序，并针对该提交之前的存储库进行了测试。

这是一个示例，旨在展示单个调用可以执行的操作及其成本。

该错误存在于 Tornado 的 websocket 代码中。当连接关闭且消息仍未发送时，每个未等待的 `write_message()` 调用都会记录错误，即使等待它是可选的。我们将结帐中的每个文本文件作为一个提示发送，并附有一份仅描述症状的错误报告：

> write_message 在连接关闭时记录“从未检索到任务异常”当 Websocket 连接关闭而消息仍未发送时（例如，客户端发送消息和 FIN，或重置连接，而不读取回复），未等待结果的每个 write_message() 调用都会在错误级别记录“从未检索到任务异常”。等待 write_message 返回的 Future 是可选的，因此未等待的调用不应该记录任何内容。等待它的调用者仍然应该得到 WebSocketClosedError。

我们询问原因和补丁。这是重播的请求：

### 回来了什么

第一个令牌在 54 秒后到达，回复在 72 秒完成。Qwen4 Max 在 `tornado/websocket.py` 中将错误追溯到 `WebSocketProtocol13.write_message`。该方法将每个写入包装在一个任务中。当连接关闭时，任务会失败，并出现一个不需要任何人收集的异常，Python 会将其记录为“从未检索到任务异常”。

该模型的补丁将异常标记为已检索。没有记录任何内容，等待写入的调用者仍然会收到错误：

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

先例使得补丁读起来就像它属于项目一样。该模型的解释说，修复应该做 `BaseIOStream.write` 已经为自己的未来所做的事情。该方法位于 `tornado/iostream.py` 中，位于 websocket 代码的下一层，它以相同的方式解决了相同的问题。维护者的提交也做了同样的比较。

![由 344 个方格组成的网格，Tornado 存储库中的每个文件一个，按文件夹分组。龙卷风文件夹中的两个方块突出显示并用一条线连接：websocket.py（错误所在）和 iostream.py（模型指向的先例）。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b01fded989d54b2b151f5cf_qwen4-max-repo-map.png)

没有人为此挑选这些文件。所有 344 个都输入了，模型找到了重要的两个。

### 我们如何检查它

Tornado 的维护者在修复中添加了两项回归测试：一项针对未等待的写入，另一项针对等待的写入。在修复之前的代码中，第一个失败。应用模型的补丁后，两者都通过了。然后，我们在补丁到位的情况下运行了 Tornado 的全套套件，进行了 1,673 次测试，没有一次失败。

### 花费是多少

按销售价格计算，请求价格约为 69 美分，几乎全部用于 652,519 个输入代币。按标价计算，价格为 98 美分。

再次发送相同的存储库的成本要低得多。 AI 会自动缓存提示输入，并且在销售期间缓存的输入为每百万代币 0.0525 美元。当我们重复大约 630,000 个令牌的请求时，几乎所有令牌都被缓存回来。第一个令牌在 8 秒内到达，而不是 54 秒，输入成本约为 3 美分，而不是 66 秒。

## 关于Qwen4 Max

阿里巴巴于2026年11月16日发布了Qwen4 Max，并将其描述为Qwen家族迄今为止最强大的型号。它将模型定位为长期代理工作，包括跨大型存储库进行编码，这是我们测试的任务类型。

Qwen4 Max 是一个稀疏专家混合模型，拥有 2.4 万亿个参数，其中每个代币有 710 亿个活跃参数。在阿里巴巴自己的跨 721 个专业领域的行业任务基准 Work360 上，阿里巴巴报告称，其整体性能优于 Qwen3.8 Max，在高推理强度下使用的代币减少了 35%，平均每个任务的成本降低了约 60%。这是阿里巴巴的数据，[其公告](https://www.alibabacloud.com/en/press-room/alibaba-unveils-qwen4-max)有详细信息。

## 在 Together AI 上运行

Qwen4 Max 位于模型字符串 `Qwen/Qwen4-Max` 下的 Together Serverless Inference 上。该脚本在一个请求中发送整个存储库和错误报告，就像我们的测试所做的那样。您需要 Together Python SDK (`pip install together`)、`TOGETHER_API_KEY`、存储库的本地克隆以及保存为 `bug_report.md` 的错误报告。它发送 git 跟踪的每个文本文件，因此首先检查存储库中的机密。

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

其中有两件事是该模型特有的。请求必须设置 `stream=True`，因为 Together AI 上的 Qwen4 Max 仅接受流请求。默认情况下，思考处于开启状态，因此模型的推理首先在 `delta.reasoning` 中流动，并且在答案开始之前有一个暂停。思考标记算作输出标记。要跳过对简单请求的思考，请传递 `reasoning={"enabled": False}`。

要在不编写代码的情况下尝试它，请在 [playground](https://api.together.ai/playground/v2/chat/Qwen/Qwen4-Max) 打开它。 [模型页面](https://www.together.ai/models/qwen4-max) 具有相同的详细信息。

现已上市

在 Together AI 上运行 Qwen4 Max

基于无服务器推理的 1M 令牌上下文、文本和图像输入以及自动提示缓存。

打开游乐场

## 常见问题解答

### Qwen4 Max 在 Together AI 上的售价是多少？

Together AI 上的 Qwen4 Max 标价为每 100 万个输入代币 1.50 美元，每 100 万个输出代币 4.50 美元，每 100 万个缓存输入代币 0.075 美元。截至 2026 年 11 月 22 日，可享受 30% 折扣：1.05 美元、3.15 美元和 0.0525 美元。思考标记算作输出标记。

###Together AI 上 Qwen4 Max 的上下文窗口是什么？

Qwen4 Max 在 Together AI 上有一个 1M 代币的上下文窗口。在我们的测试中，具有 652,519 个输入令牌的请求在 54 秒后返回其第一个令牌。

### Qwen4 Max 接受图像吗？

是的，Qwen4 Max 接受 Together AI 上的文本和图像输入并返回文本。将每个图像作为消息内容中的 `image_url` 块发送，如 [视觉文档](https://docs.together.ai/docs/inference/vision/overview) 中所述。

### 为什么我的 Qwen4 Max 请求在没有流式传输的情况下失败？

Together AI 上的 Qwen4 Max 仅接受流请求。没有 `"stream": true` 的请求将返回 400 错误，代码为 `streaming_required`。在 SDK 中设置 `stream=True`，或在请求正文中设置 `"stream": true`，然后从流中读取回复。

### 如何关闭 Qwen4 Max 上的思考？

在Python SDK中传递`reasoning={"enabled": False}`，或在请求正文中传递`"reasoning": {"enabled": false}`，以关闭Qwen4 Max上的思考。默认情况下，思考处于开启状态，并且它会在答案之前返回到 `reasoning` 字段。要对难题进行更多思考，请将 `reasoning_effort` 设置为 `"max"`。

### Qwen4 Max支持工具调用吗？

是的，Qwen4 Max 支持通过标准 `tools` 参数调用 Together AI 的工具。它可以轮流返回多个调用。

### 提示缓存是否适用于 Qwen4 Max？

是的，Together AI 上的 Qwen4 Max 会自动进行提示缓存，并且缓存的输入令牌按标价每 1M 花费 0.075 美元。在我们的测试中，重复 630,000 个令牌的请求几乎完全被缓存，并且其第一个令牌在 8 秒内到达，而不是 54 秒。缓存是尽力而为，因此并非每个重复都被缓存。

### 我可以微调 Qwen4 Max 或在专用端点上运行它吗？

不，Qwen4 Max 目前仅在 Together AI 上是无服务器的，并且无法进行微调。阿里巴巴表示，Qwen4 系列的小型开放式重量型号也将随之推出。

## 相关文章
