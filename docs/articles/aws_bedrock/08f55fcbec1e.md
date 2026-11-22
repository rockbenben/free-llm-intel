---
vendor: aws_bedrock
title: Introducing OS Level Actions in Amazon Bedrock AgentCore Browser
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-os-level-actions-in-amazon-bedrock-agentcore-browser
date: 2026-05-05
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: cedfdc176b66
---

# 在 Amazon Bedrock AgentCore Browser 中推出 OS Level Actions

自动化 Web 工作流的 AI agents 运行在浏览器的 Web 层，也就是 Playwright 和 Chrome DevTools Protocol（CDP）所暴露的 DOM 之内。AgentCore Browser 为此提供了一个安全、隔离的浏览器环境，它足以胜任绝大多数自动化任务：浏览页面、填写表单、点击元素、提取内容。但 Web 层存在一道硬性边界。任何由操作系统渲染的内容（原生对话框、安全提示、证书选择器、上下文菜单，甚至 Chrome 设置）都完全位于 DOM 之外。CDP 看不到它们，Playwright 也无法与之交互。

当 Web 应用调用 `window.print()` 并弹出系统打印对话框时，Playwright 没有可交互的 DOM。当工作流需要键盘快捷键或右键上下文菜单时，CDP 没有在 OS 层面发出这些命令的机制。当浏览器会话遇到 macOS 隐私对话框、Windows Security 提示或证书选择器时，它们对 Web 自动化层是不可见的。这些场景往往在生产环境中才浮现。它们由特定的应用状态、OS 配置或用户权限触发，而不会出现在测试中——因为测试里的 Web 内容足够可预测，易于校验。

对于具备视觉能力的 agents，这一挑战更为复杂。一种常见架构是截取屏幕截图、发送给模型、接收返回的坐标或指令，然后执行。这个循环对 Web 内容运作良好，但原生 UI 一出现就会失效。截图捕捉到了它，模型也对它进行了推理，然而却没有可用来执行操作的手段。CDP 触达不了 OS 渲染的内容。agent 清楚地看到该做什么，却无从下手。

我们宣布为 AgentCore Browser 推出 OS Level Actions。这项新能力通过 `InvokeBrowser` API 开放直接的 OS 控制，从而打通上述场景，使 agents 能够与屏幕上可见的内容交互，而不仅限于通过浏览器 Web 层可访问的内容。通过将全桌面截图与 OS 层面的鼠标和键盘控制相结合，agents 可以在同一个会话内观察原生 UI、对其推理并采取行动。本文逐步介绍 OS Level Actions 的工作原理、支持的动作类型以及入门方法。

## **OS Level Actions 的工作原理**

OS Level Actions 对新建和现有的浏览器配置均可用，无需额外设置。会话激活后，您通过 `InvokeBrowser` API 派发动作。每次调用恰好携带一个动作，由其类型和参数标识，并返回 `SUCCESS` 或 `FAILED` 状态。当前会话通过 `x-amzn-browser-session-id` 标头识别，它将每个 OS 级动作关联到正确的浏览器会话。

预期的交互模式是一个“动作—截图—反应”循环。agent 执行一个动作（点击、输入、快捷键），截取截图以观察屏幕当前状态，然后根据所见决定下一个动作。这个循环让 agent 能够对动态 UI 作出反应，包括工作流中途可能出现的原生对话框和 OS 提示。

- **Agent 发送动作**。可以是鼠标点击、按键或使用 `InvokeBrowser` 的快捷键。
- **AgentCore 执行动作**，作用于整个 OS 桌面，并返回 `SUCCESS` 或 `FAILED`。
- **Agent 请求截图**以观察当前屏幕状态。
- **AgentCore 截取整个桌面**，包括原生对话框、OS 模态窗口和浏览器窗口之外的 UI，并返回 base64 编码的 PNG。
- **Agent 对截图进行推理**，将其发送给视觉模型，以确定发生了什么以及下一步该做什么。
- **Agent 根据观察结果发送下一个动作**，继续这一循环。

## **支持的动作**

OS Level Actions 分为三类：鼠标控制、键盘输入和视觉捕获。下表汇总了八种动作及其字段和约束。

| **Action** | **必填字段** | **可选字段** | **说明** |
| --- | --- | --- | --- |
| mouseClick | — | x, y, button, clickCount | 默认为当前位置、LEFT、单击。clickCount：1–10。 |
| mouseMove | x, y | — | 将光标移动到指定坐标。 |
| mouseDrag | endX, endY | startX, startY, button | 从起点拖动到终点。button 默认为 LEFT。 |
| mouseScroll | — | x, y, deltaX, deltaY | deltaY 为负表示向下滚动。范围：-1000 至 1000。 |
| keyType | text | — | 输入一个字符串。最多 10,000 个字符。 |
| keyPress | key | presses | 将某个按键按下 N 次。presses：1–100，默认为 1。 |
| keyShortcut | keys | — | 按键组合数组。最多五个键，例如 [“ctrl”, “a”]。 |
| screenshot | — | format | 截取整个 OS 桌面。返回 base64 编码的 PNG。 |

### **鼠标动作**

鼠标动作涵盖指针交互的全部范围：点击、移动、拖动和滚动。对 `mouseClick` 而言，坐标字段是可选的。若省略，点击将落在当前光标位置，以左键单击执行。当此前的 `mouseMove` 已经定位好光标时，这一点很有用。`mouseDrag` 需要四个坐标，即起点和终点位置。`mouseScroll` 接受一个位置以及两个轴上的增量值——`deltaY` 为负时向下滚动，为正时向上滚动。例如，右键上下文菜单就是一次 `mouseClick`，在目标坐标处将 button 设为 `RIGHT`。请注意，由于浏览器会话运行于虚拟化环境，某些上下文菜单项可能无法按预期工作。

### **键盘动作**

三种键盘动作覆盖不同层级的输入。`keyType` 用于输入文本，它直接发送字符，可处理最多 10,000 个字符的字符串。`keyPress` 用于需要反复按下的单个按键，例如用 tab 在表单字段间前进，或用 escape 关闭模态窗口。`keyShortcut` 用于组合键——传入一个键名数组，AgentCore 会同时按下它们。

keyPress 和 keyShortcut 的键名必须为小写。支持的按键包括单个字符（a–z、0–9）以及 enter、tab、space、backspace、delete、escape、ctrl、alt、shift 等命名键。

例如，要选中全部文本，可以使用 keyShortcut 并传入 `["ctrl", "a"]`。

```
{
  "action": {
    "keyShortcut": {
      "keys": ["ctrl", "a"]
    }
  }
}
```

### **截图**

`screenshot` 动作截取整个 OS 桌面，并在响应中返回 base64 编码的 PNG。它是唯一返回数据的动作。其他动作只返回状态（SUCCESS 或 FAILED），失败时附带一个错误字段。

```
{
   "action":{
      "screenshot":{
         "format":"PNG"
      }
   }
}
```

## **入门**

以下示例逐步演示“动作—截图—反应”循环，与[配套 notebook](https://github.com/awslabs/agentcore-samples/tree/main/01-tutorials/05-AgentCore-tools/02-Agent-Core-browser-tool/14-browser-os-actions) 保持一致。若要查看完整可运行、端到端演示八种动作的 notebook，请从那里开始。

### **设置客户端并创建浏览器**

您需要两个客户端：一个控制平面客户端（`bedrock-agentcore-control`）用于管理浏览器资源，一个数据平面客户端（`bedrock-agentcore`）用于在会话期间派发动作。

```
import boto3
import time

browser_boto3 = boto3.client('bedrock-agentcore-control', region_name='us-west-2')

BROWSER_NAME = "browser_with_os_actions"
```

在启动会话之前，您需要一个 AWS Identity and Access Management（IAM）执行角色和一个浏览器资源。该执行角色需要 `bedrock-agentcore:InvokeBrowser`、`bedrock-agentcore:StartBrowserSession` 和 `bedrock-agentcore:StopBrowserSession` 权限。[配套 notebook](https://github.com/awslabs/agentcore-samples/tree/main/01-tutorials/05-AgentCore-tools/02-Agent-Core-browser-tool/14-browser-os-actions) 包含一个为您创建该角色的辅助函数：

```
from helpers.utils import create_agentcore_execution_role, SAMPLE_ROLE_NAME

execution_role_arn = create_agentcore_execution_role(SAMPLE_ROLE_NAME)
```

角色创建完成后，创建一个自定义浏览器：

```
created_browser = browser_boto3.create_browser(
    name=BROWSER_NAME,
    executionRoleArn=execution_role_arn,
    networkConfiguration={
        'networkMode': 'PUBLIC'
    }
)

browser_id = created_browser['browserId']
print(f"Browser ID: {browser_id}")
```

### **启动浏览器会话**

浏览器资源创建完成后，启动一个会话。`viewPort` 设置屏幕分辨率，它决定了鼠标动作的坐标空间以及截图的尺寸。`sessionTimeoutSeconds` 控制会话在自动终止前保持存活的时间。

```
# These helpers are included in the companion notebook repository
from helpers.browser import get_credentials, invoke, start_session, stop_session

creds, default_region = get_credentials()
BEDROCK_AGENTCORE_DP_ENDPOINT = f"https://bedrock-agentcore.{default_region}.amazonaws.com/"

sid = start_session(BEDROCK_AGENTCORE_DP_ENDPOINT, browser_id, region=default_region, credentials=creds)

# Wait for session to initialize — adjust if needed for your environment
time.sleep(3)
```

`start_session` 辅助函数发送一个经 SigV4 签名的 PUT 请求来创建会话，并返回 sessionId。invoke 辅助函数负责签名和派发各个动作。

### **调用 OS 级动作**

会话运行起来后，您可以通过 invoke 辅助函数派发 OS 级动作。每次调用接受一个动作——在本例中，是在屏幕坐标 (600, 370) 处的一次左键点击：

```
r = invoke(
    BEDROCK_AGENTCORE_DP_ENDPOINT, sid,
    {"mouseClick": {"x": 600, "y": 370, "button": "LEFT"}},
    region=default_region, credentials=creds, browser_id=browser_id
)

print(f"Mouse click status: {r.status_code}, action: {r.json()['result']}")
```

响应会告诉您动作成功还是失败。坐标对应屏幕像素；如果会话视口为 1920×1080，则 x 的有效取值范围为 0 至 1919，y 为 0 至 1079。超出屏幕尺寸的坐标会返回 `ValidationException`。

### **截取截图**

每次动作之后，agent 都必须观察发生了什么。screenshot 动作截取整个桌面，并以 base64 编码的 PNG 形式返回图像：

```
import base64
from IPython.display import Image, display

r = invoke(
    BEDROCK_AGENTCORE_DP_ENDPOINT, sid,
    {"screenshot": {"format": "PNG"}},
    region=default_region, credentials=creds, browser_id=browser_id
)

img_bytes = base64.b64decode(r.json()['result']['screenshot']['data'])
display(Image(img_bytes))
```

这是循环中的观察步骤。agent 将截图发送给视觉模型，由后者对屏幕上的内容进行推理，并返回下一步要执行的动作。该循环不断重复，直到工作流完成。

## **综合运用：关闭打印对话框**

下面是“动作—截图—反应”循环的实际应用。假设 agent 导航到一个触发 `window.print()` 的页面，弹出一个原生打印对话框。agent 无法通过 CDP 与之交互，但可以通过 OS Level Actions 做到。首先，agent 截取一张截图，查看屏幕当前状态：

```
r = invoke(
    BEDROCK_AGENTCORE_DP_ENDPOINT, sid,
    {"screenshot": {"format": "PNG"}},
    region=default_region, credentials=creds, browser_id=browser_id
)

# Send the screenshot to a vision model to identify the dialog and locate the Cancel button.
# The vision model integration depends on your agent architecture — see the Bedrock
# InvokeModel API for how to send images to Claude or other models.
# The model returns coordinates, e.g.: {"x": 410, "y": 535}
```

视觉模型识别出打印对话框，并返回 **Cancel** 按钮的坐标。agent 选中它：

```
r = invoke(
    BEDROCK_AGENTCORE_DP_ENDPOINT, sid,
    {"mouseClick": {"x": 410, "y": 535, "button": "LEFT"}},
    region=default_region, credentials=creds, browser_id=browser_id
)

print(f"Click status: {r.status_code}, action: {r.json()['result']}")
```

agent 再截取一张截图，确认对话框已被关闭，然后工作流继续。

## **停止会话并清理资源**

工作流完成后，停止会话并清理资源：

```
stop_session(BEDROCK_AGENTCORE_DP_ENDPOINT, sid, browser_id, region=default_region, credentials=creds)
```

要删除浏览器资源和 IAM 角色：

```
browser_boto3.delete_browser(browserId=browser_id)
print(f"Browser {browser_id} deleted")

from helpers.utils import delete_agentcore_execution_role, SAMPLE_ROLE_NAME
delete_agentcore_execution_role(SAMPLE_ROLE_NAME)
```

这些步骤——行动、观察、决策——构成了“动作—截图—反应”模式的核心。[配套 notebook](https://github.com/awslabs/agentcore-samples/tree/main/01-tutorials/05-AgentCore-tools/02-Agent-Core-browser-tool/14-browser-os-actions) 结合真实浏览器会话，逐步演示了八种受支持的动作，包括鼠标拖动、滚动、键盘输入和快捷键组合。

## **结论**

在我们推出 [Amazon Bedrock AgentCore Browser](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-tool.html) 时，它为 AI agents 提供了一个全托管、基于云的浏览器环境，用于与网站交互。它借助 Playwright 和 CDP 浏览页面、提取内容，并大规模自动化工作流。OS Level Actions 将这一能力从 Web 层扩展到屏幕上可见的 UI 元素。原生对话框、安全提示、键盘快捷键和浏览器 chrome 不再是阻碍。agents 现在可以在同一个会话内观察整个 OS 桌面、对其推理并采取行动。

结合 AgentCore Browser 现有的能力，例如视觉理解以及与 Playwright 和 Amazon Nova Act 的框架集成，OS Level Actions 补齐了浏览器自动化覆盖范围的最后一块空白。

要开始构建：

- 参阅 [Amazon Bedrock AgentCore 开发者指南](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-tool.html)
- 试试[配套 notebook](https://github.com/awslabs/agentcore-samples/tree/main/01-tutorials/05-AgentCore-tools/02-Agent-Core-browser-tool/14-browser-os-actions)，进行动手实操
- 有关浏览器自动化的更多背景，请参阅 [Amazon Bedrock AgentCore Browser 文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-quickstart.html)

**关于作者**
