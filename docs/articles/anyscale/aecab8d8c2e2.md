---
vendor: anyscale
title: 宣布 Ray 原生沙箱能力
original_title: Announcing Native Sandboxing in Ray
url: https://anyscale.com/blog/announcing-native-sandboxing-in-ray
date: 2026-08-25
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 宣布 Ray 原生沙箱能力

作者：Philipp Moritz、Andrew Sy Kim（Google）和 Xinyu Zhang | 2026 年 8 月 25 日

Agentic RL 需要同时运行大量彼此隔离、执行模型生成代码的环境。如今，用 Ray 构建这类负载的团队，要么依赖托管沙箱服务商，要么在 Ray 集群之外自行构建并运维一套独立的沙箱系统。

从 Ray 2.58 开始，我们引入一个新选项：沙箱作为 Ray 的原生组成部分。

[我们与 Google 合作](https://cloud.google.com/blog/products/containers-kubernetes/gvisor-sandboxes-for-ray-clusters-on-gke)，发布一个基于 gVisor 的实验性沙箱库。它允许你从 OCI 容器镜像创建隔离环境、在其中执行命令、进出文件、控制网络访问，并直接用 Ray 既有的原语来调度和扩缩这些环境——与你调度 trainer、rollout worker、evaluator 及其他分布式组件的方式完全一致。

这一集成在两个层面做了设计。对于只想要隔离执行的用户，Ray 提供高层沙箱 API，由它代管沙箱的放置与生命周期。对于想构建自家沙箱服务的团队，Ray 同时暴露底层运行时原语，可直接创建和管理隔离的 gVisor 环境。这使得 Ray 可以作为自定义沙箱服务之下的分布式控制平面，而无需从零构建调度、资源管理、自动扩缩容与容错。

职责划分很简单：**Ray 负责编排与扩缩，gVisor 负责隔离。**

由于沙箱作为 Ray 集群的一部分被调度，它们与负载的其余部分共享同一套资源管理和自动扩缩容体系。在 Google Kubernetes Engine 上，我们已经把该架构扩展到跨数千节点、20 秒内创建 10 万个沙箱。

## 沙箱即 Ray 原语

Ray 已成为编排后训练（post-training）负载的通用运行时。veRL、NeMo-RL、SLIME、MILES、SkyRL 等框架已在使用 Ray 协调分布式 trainer、推理引擎、rollout worker 及其他组件。

设计 Ray Sandboxing 时，一个重要目标是让它自然融入现有 Ray 编程模型，而不是为隔离执行引入一套独立抽象。沙箱与 Ray 管理的其他资源有许多相同属性：需要被放置到某台机器、分配资源、创建与销毁、从故障中恢复、并随周边负载一起扩缩。这促使我们用 Ray Actor 来表示每个高层沙箱：

Ray 调度器决定哪台节点运行某个沙箱，并预留相应的 CPU 与内存资源。沙箱 Actor 管理其生命周期，gVisor 在该节点上提供隔离执行环境。

因此，框架作者可以用与工作负载其余部分相同的 Ray API 和模式来管理沙箱化环境。例如：

```
import ray
from ray.experimental import sandbox

ray.init()
# Create a gVisor sandbox environment and return an actor handle for a proxy actor
sb = sandbox.create(
    cpu=1.0,
    memory="512Mi",
    image="python:3.12-slim"
)
# Execute code inside the sandbox
result = ray.get(sb.exec.remote("python -c 'import sys; print(sys.version)'"))
print(result.stdout)
```

这会从一个 OCI 兼容镜像创建 gVisor 沙箱并返回一个 Ray Actor 句柄。对 `exec` 的调用就是普通的 Ray Actor 调用，因此沙箱可以位于集群中的任何地方。创建的 actor 是一个代理，会把操作转发给 gVisor。

[sandbox API](https://docs.ray.io/en/master/ray-core/api/sandboxes.html)覆盖了 agentic 负载所需的基本生命周期：

- 从 OCI 容器镜像创建环境，
- 设置 CPU 与内存限额，
- 配置环境变量、工作目录与网络，
- 执行命令，
- 读取、写入、上传与下载文件，
- 查看沙箱状态，以及
- 终止或删除环境。

对于更底层的用法，`SandboxRuntime` 提供对本地 gVisor 沙箱的直接访问，允许用户在 OCI spec 交给 gVisor 之前修改它。下面是用该 API 在 actor 内部构建本地沙箱池的示例：

```
import ray
from ray.experimental.sandbox.runtime import SandboxRuntime

@ray.remote
class SandboxPool:
    def __init__(self, size: int = 3, image: str = "python:3.10-slim"):
        self.runtime = SandboxRuntime()
        self.sandboxes = [
            self.runtime.create(image=image, memory="512Mi")
            for _ in range(size)
        ]

    def run_command(self, index: int, command: str):
        return self.runtime.exec(self.sandboxes[index], command)

    def close(self):
        for sb_id in self.sandboxes:
            self.runtime.delete(sb_id)

# Deploy an actor managing a pool of local sandboxes
pool = SandboxPool.remote(size=3)
result = ray.get(pool.run_command.remote(0, "python3 -c 'print(\"Hello from pool!\")'"))
print(result.stdout)
ray.get(pool.close.remote())
```

## 扩展到 10 万个沙箱

当环境数量增长时，把沙箱集成进 Ray 的价值尤为突出。

大规模 RL 负载可能需要数千个环境并发运行，且随着 rollout 推进环境不断被创建和销毁。独立的沙箱服务意味着再多一个调度器、再多一个需要与训练系统一同扩展的分布式控制平面。

有了 Ray Sandboxes，环境放置对 Ray 来说不过是又一个调度问题。

在 Google Kubernetes Engine 上运行 Ray 时，我们已将系统扩展到 20 秒内在数千个节点上创建 10 万个 gVisor 沙箱。

沙箱创建时间与规模的对比

## 为什么选 gVisor？

运行模型生成的代码，就意味着必须把环境内的代码当作不可信来处理。

Ray Sandboxing 选用 Google 的开源应用内核 [gVisor](https://gvisor.dev/) 作为首个沙箱运行时。gVisor 在用户空间实现了 Linux 系统调用接口的相当大部分，在工作负载与宿主内核之间增设了一道隔离边界。

它兼容 OCI、可使用标准容器镜像，并且无需向沙箱暴露 Docker daemon 或宿主 Docker socket。

这一组合对 agentic 负载尤其合适：环境轻到可以动态创建，同时比在普通容器里直接执行生成代码提供更强的隔离。

gVisor 还提供亚秒级沙箱启动与极低的单沙箱内存开销，使沙箱可以作为粒度相对精细的分布式资源来使用。

## 真实负载的常见模式

创建一个隔离进程只是运行真实 agent 负载的一部分。环境往往需要不同的网络策略，文件与产物需要在 agent 与沙箱之间流动，外部系统也需要某种方式调用沙箱内的执行。

Ray Sandboxing 为每种模式都提供了原语。

### 1. 网络隔离

并非每个沙箱都需要同等级别的连通性。agent 可能需要访问互联网来调用 API 或安装软件包，而运行不可信代码的 evaluator 应保持隔离。Ray 支持四种网络模式：

- **network="none"**（默认）：仅回环。最适合隔离的 rollout 与不可信代码。
- **network="public"**：可出公网，并附带可移植的 /etc/resolv.conf。适合 API 调用与软件包安装。
- **network="host"**：共享节点网络命名空间，可访问节点本地服务。
- **network="sandbox"**：使用 gVisor 的隔离网络栈，要求 rootless=False。

```
from ray.experimental import sandbox

sb = sandbox.create(
    image="python:3.12-slim",
    network="public",
    dns=["10.0.0.2"],
    readonly=False,
)
ray.get(sb.exec.remote("pip install requests"))
```

### 2. 移动文件与状态

在真实负载中，往往需要向沙箱移动的不只是命令字符串。小文件可以直接通过 Actor 读写字节；更大的目录树则用归档包，以保留权限、符号链接和空目录。由于文件传输经由 Ray，即使沙箱运行在另一台物理节点上也能工作。

```
script_source = "print('Training complete')"
ray.get(sb.write_file.remote("/app/train.py", script_source))
metrics = ray.get(sb.read_file.remote("/app/metrics.json"))

ray.get(sb.upload_file.remote("bundle.tar.gz", "/tmp/bundle.tar.gz"))
ray.get(
    sb.exec.remote(
        "mkdir -p /app && tar -xzf /tmp/bundle.tar.gz -C /app"
    )
)
```

### 3. 通过 MCP 暴露沙箱化执行

Ray Sandboxes 也可以置于 MCP 工具之后，为兼容 MCP 的 agent 提供安全执行不可信代码的途径，而不暴露宿主环境。agent 只与该工具交互，隔离由底下的 Ray 和 gVisor 处理。

```
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sandboxed-python")
isolated_sb = sandbox.create(
    image="python:3.12-slim",
    network="none",
)

@mcp.tool()
def run_python(code: str) -> str:
    """Run untrusted Python inside a gVisor sandbox."""
    result = ray.get(
        isolated_sb.exec.remote(
            ["python", "-c", code],
            timeout=30,
        )
    )
    return result.stdout if result.exit_code == 0 else result.stderr
```

### 4. 削减沙箱权限

需要更严格隔离时，传入 `capabilities=[]` 以移除沙箱的 Linux capabilities。这样即便沙箱内的 root 用户也无法执行 chown、mknod 或打开原始套接字等操作。若需更低层控制，`_oci_spec_transform_fn` 允许你在 OCI spec 送达 gVisor 之前修改它。例如移除 capabilities 或强制执行进程数限制：

```
from ray.experimental.sandbox.runtime import SandboxRuntime

def harden_spec(spec):
    # Limit process creation to reduce fork-bomb risk.
    spec["process"]["rlimits"] = [
        {"type": "RLIMIT_NPROC", "hard": 64, "soft": 64}
    ]
    # Remove all Linux capabilities.
    if "capabilities" in spec["process"]:
        for cap_type in spec["process"]["capabilities"]:
            spec["process"]["capabilities"][cap_type] = []
    return spec

runtime = SandboxRuntime()
sb_id = runtime.create(
    image="python:3.12-slim",
    _oci_spec_transform_fn=harden_spec,
)
```

## 用 harbor 运行 Ray Sandboxes

[Harbor](https://github.com/harbor-framework/harbor) 是一个在 SWE-Bench、Terminal-Bench 等基准上评测 Claude Code、OpenHands、Codex CLI 等编码 agent 的框架，每次 trial 都在隔离的任务环境中运行。

Ray Sandbox 已作为[原生 Harbor 环境](https://github.com/harbor-framework/harbor/pull/2785)提供。在 Ray 集群中运行 Harbor，各 trial 会在你自己的节点上以 gVisor 运行任务镜像，并由沙箱强制执行任务的网络策略。

### 安装与运行

将 Harbor 与 Ray Sandboxing 配合使用需要 Ray 2.58+，并在 Ray 基础镜像上[安装](https://gvisor.dev/docs/user_guide/install/)`runsc`。

```
# Install Harbor with the Ray backend
pip install 'harbor[ray]'

# Run an evaluation on Ray
harbor run --dataset terminal-bench@2.0 \
 --agent claude-code \
 --model anthropic/claude-opus-4-1 \
 -e ray \
 --n-concurrent 32
```

### 状态与性能

带公开 `[environment].docker_image` 的任务（如 MedAgentBench）开箱即用。Terminal-Bench 或 SWE-Bench 等基准则需要把每个任务的镜像发布到可达的镜像仓库。目前 compose、GPU 或基于 allowlist 的任务会被拒绝。

单台 14-CPU 开发 VM 上的性能指标：

- 单个 trial：29 秒
- 8 个 trial、并发 4：8/8 全部 reward 1.0，0 异常，3 分 02 秒（单 trial p50 为 45 秒）

吞吐通常受每节点内存约束，并通过 Ray autoscaler 在集群维度水平扩展。

### 工作原理

Harbor 的环境模型直接映射到 Ray Sandbox：

- **权限：** 任务镜像以 Docker 兼容的 capabilities 运行，使现有基准镜像行为符合预期。
- **执行：** 字符串命令保留 Harbor 的 bash -c 语义。
- **文件传输：** 目录上传被打包为 tar 归档，经沙箱文件 API 传输。
- **资源：** Harbor 的资源请求转化为 Ray 调度预留，运行时限制则在沙箱内部强制执行。
- **网络：** Harbor 的 no-network 策略映射为 network="none"。试图用更大权限覆盖它会在沙箱创建前被拒绝。

### 下一步

Ray Sandboxing 目前处于**实验阶段**，有许多我们希望与社区共同完善的方面。

**REST API 服务：** 我们计划实现一个 REST API，让用户无需把 Ray 作为依赖即可与沙箱交互，并使训练集群与沙箱集群解耦、把沙箱作为服务运行。原型见[这个 PR](https://github.com/ray-project/ray/pull/65633)。

**GPU 支持。** Ray 已被广泛用于调度 CPU/GPU 混合负载，gVisor 也[与 GPU 配合良好](https://gvisor.dev/docs/user_guide/gpu/)。随着内核生成与 RSI 等负载日益重要，我们希望带 GPU 的沙箱也能开箱即用。

**沙箱内的 Docker 支持。** 某些 agent 任务本身就期望能访问 Docker。[gVisor 支持在沙箱内运行 Docker](https://gvisor.dev/docs/tutorials/docker-in-gvisor/)，我们希望文档化并测试一套与 Ray Sandboxing 自然配合的配置。

**网络与文件系统能力。** 我们计划增加文件系统快照、在沙箱与宿主之间或沙箱彼此之间暴露端口等功能。

**安全指南。** gVisor 提供了[成熟的安全架构](https://gvisor.dev/docs/architecture_guide/intro/)，但整个系统的安全属性仍取决于沙箱与周边基础设施的配置。我们希望给出清晰的推荐配置与示例，包括面向"模型可能主动试图逃逸沙箱"的负载配置。

如果你对这些方向感兴趣或有反馈，非常欢迎联系我们（例如创建 GitHub issue 或 PR）。

## 试用

[Ray Sandboxing](https://docs.ray.io/en/master/ray-core/sandboxes.html)自 **Ray 2.58** 起以实验特性提供。

如果你正在构建 agentic RL 系统、编码 agent 评测，或其他需要大规模隔离执行的负载，欢迎试用并告诉我们缺什么。

在 K8s 上上手请参考 [Ray Sandboxing Guide](https://docs.ray.io/en/master/cluster/kubernetes/examples/ray-sandboxing.html)。

反馈、功能请求或贡献，请到 [GitHub](https://github.com/ray-project/ray/issues/65352) 参与讨论。

我们的目标是让沙箱化环境用起来就像 Ray 中任何其他分布式原语：易于创建、易于扩缩、易于与 agentic 负载的其余部分组合。
