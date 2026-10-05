---
vendor: anyscale
title: Ray Serve：以异步推理、自定义请求路由与自定义扩缩推进灵活性
original_title: Ray Serve: Advancing Flexibility with Async Inference, Custom Request Routing, and Custom Autoscaling
url: https://anyscale.com/blog/ray-serve-autoscaling-async-inference-custom-routing
date: 2025-11-11
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Ray Serve：以异步推理、自定义请求路由与自定义扩缩推进灵活性

作者：Abrar Sheikh、Harshit Agarwal 和 Akshay Malik | 2025 年 11 月 11 日

过去一年，**Ray Serve** 已成为团队把多模态 AI 负载——从 LLM 到语音分析、视频流水线——送上生产的首选。

*ray serve 更新*

我们引入四项新能力，大幅扩展 Serve 在现代推理负载上的灵活性与可扩展性：

- **Async Inference（异步推理）** —— 安全高效地处理长时运行或可恢复的负载
- **Custom Request Routing（自定义请求路由）** —— 精确控制请求在各 deployment 副本间的分发
- **Custom Autoscaling（自定义自动扩缩）** —— 用领域指标驱动你自己打造的扩缩逻辑
- **External Scaling（外部扩缩）** —— 从外部系统对 serve 应用扩缩

这些特性合力让构建复杂的、延迟敏感的或多阶段的生产 AI 系统更容易。

## **为什么灵活性重要**

AI 负载日益**异构**。一条流水线可能组合：

- ASR → 说话人核验 → LLM 摘要 → 分析
- 推荐器 → 重排器 → 嵌入模型
- 视频分块 → 解码 → 推理 → 后处理

每个阶段都可能有迥异的运行时行为、资源需求与延迟约束。
Ray Serve 在这些阶段上提供**统一控制**，处理路由、自动扩缩、批处理与可观测性——让团队迭代模型而非基础设施。

## **异步推理：安全处理长时负载**

异步负载在 AI 系统中很常见——批量摘要、转写、视频处理、多步 agent 工作流。这类需求往往用 Celery、Kafka 或自研作业调度器等独立队列系统实现。

有了 **Async Inference**，Ray Serve 把异步处理直接集成进与在线推理同一个 serving 层。团队可以处理准实时与长时请求而不触发客户端超时、安全跟踪进度或恢复任务，并在单一运行时内同时管理同步与异步负载——无需引入额外基础设施。

用 Ray Serve 做异步负载的关键优势：

- **更简单的架构：** Serve 与 Redis、SQS 等消息代理集成完成排队与重试，同时在同一运行时内管理任务提交与处理。
- **异构负载的统一运行时：** 在同一应用中混合 GPU 密集推理与更长的 CPU/I/O 密集处理。
- **共享扩缩与可观测：** 异步 worker 使用与标准 Ray Serve deployment 相同的 autoscaler 与指标管道。
- **一致的 Python API：** 在线、异步、流式负载之间复用逻辑与依赖。
- **至少一次（at least once）处理保证：** 在副本故障与服务滚动发布期间也能安全执行任务。

**真实案例：**

Fano AI——一家服务多语种联络中心的香港语言 AI 公司——在 Ray Serve + Kubernetes（经 KubeRay）上运行重型音频流水线（ASR、说话人核验与 LLM 分析）。

> "异步推理对我们必不可少：处理数小时的音频上传与通话后分析，请求才不会超时。进度可跟踪，我们可以安全重试或恢复而不阻塞在线流量。" —— Sam Broughton，Fano AI

**工作原理：**

在 Ray Serve 启用异步推理有两个核心组件：

1. 设置任务处理配置——包括消息代理（如 Redis、SQS 等）与 DLQ 行为的配置。

```
1from ray.serve.schema import TaskProcessorConfig, CeleryAdapterConfig
2
3processor_config = TaskProcessorConfig(
4    queue_name="my_queue",
5    # Optional: Override default adapter string (default is Celery)
6    adapter_config=CeleryAdapterConfig(
7        broker_url="redis://localhost:6379/0",
8        backend_url="redis://localhost:6379/1",
9    ),
10    max_retries=5,
11    failed_task_queue_name="failed_tasks",
12)
```

2. 定义你的任务处理逻辑——在这里编写业务逻辑，也可组合动态推理图。

```
1from ray import serve
2from ray.serve.task_consumer import task_consumer
3
4@serve.deployment
5@task_consumer(task_processor_config=processor_config)
6class SimpleConsumer:
7    @task_handler(name="process_request")
8    def process_request(self, data): 
9        return f"processed: {data}"
```

3. 定义一个 ingress deployment 用于提交任务与获取状态

```
1from fastapi import FastAPI
2from ray import serve
3from ray.serve.task_consumer import instantiate_adapter_from_config
4
5app = FastAPI()
6
7@serve.deployment
8@serve.ingress(app)
9class API:
10  def __init__(self, consumer_handle, task_processor_config):
11    self.adapter = instantiate_adapter_from_config(task_processor_config)
12    # for creating the deployment graph
13    self.consumer = consumer_handle
14
15  @app.post("/submit")
16  def submit(self, request):
17    task = self.adapter.enqueue_task_sync()
18    return {"task_id": task.id}
19
20  @app.get("/status/{task_id}")
21  def status(self, request):
22    return self.adapter,get_task_status_sync(task_id)
```

这会搭起两个 deployment——一个负责入队请求并响应状态查询，另一个负责轮询消息队列并执行你的处理逻辑。

*Ray Serve - 路由*

***文档：***[Ray Serve 中的异步推理](https://docs.ray.io/en/master/serve/asynchronous-inference.html)

## **自定义请求路由：可编程的流量控制**

Ray Serve 的默认路由算法基于各副本的请求数。但有些应用的路由决策需要依赖请求内容、各副本的模型版本或负载状态。

借助新的 **Custom Request Router** API，Serve 让路由完全用 Python 可编程。这一特性让你把领域智能直接嵌入 Serve 的路由层。

**真实案例**：服务多轮对话聊天机器人时，LLM 可以利用 [prefix cache](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html)——它保存此前请求注意力计算得到的 KV 向量。多个请求若共享同一段起始文本（"前缀"），系统就能复用早先的计算（命中热前缀缓存），降低延迟、减少 GPU 周期浪费。基于请求内容路由的策略能显著改善系统吞吐/延迟表现。更多细节见我们[用自定义路由把 LLM 推理延迟降低最多 60% 的博客](https://www.anyscale.com/blog/ray-serve-faster-first-token-custom-routing)。

自定义路由常见用途：

- 缓存亲和 —— 把请求路由到已持有相关数据或模型权重的副本。Ray Serve 的模型多路复用（multiplexing）就是一个内建路由器的例子。
- 延迟感知 —— 偏向近期响应时间更短的副本。
- 有状态副本 —— 无需外部协调地维持按会话/按用户的亲和。
- 动态优先级 —— 基于运行时指标或请求类型偏向某些副本。

**工作原理：**

1.（可选）从你的 serve deployment 上报自定义路由统计

```
1from ray import serve
2
3@serve.deployment
4class MyDeployment:
5    def record_routing_stats(self) -> Dict[str, float]:
6        return {"throughput": 100}
```

2. 实现你自己的 RequestRouter 子类并重写 choose_replicas()。

```
1from ray.serve.request_router import (
2    PendingRequest,
3    RequestRouter,
4    RunningReplica,
5)
6
7class UniformRequestRouter(RequestRouter):
8    async def choose_replicas(
9       self,
10       candidate_replicas: List[RunningReplica],
11       pending_request: Optional[PendingRequest] = None
12    ) -> List[List[RunningReplica]]:
13        import random
14        index = random.randint(0, len(candidate_replicas)-1)
15        return [[candidate_replicas[index]]]
16
17    def on_request_routed(...):
18        print("on_request_routed callback is called!!")
```

3. 把自定义路由器挂到你的 Serve deployment 上

```
1from ray import serve
2from ray.serve.config import RequestRouterConfig
3
4@serve.deployment(
5  request_router_config=RequestRouterConfig(
6    request_router_class="custom_request_router:UniformRequestRouter"
7  ),
8  num_replicas=10
9)
10class MyApp:
```

*Ray Serve - 自定义路由*

*文档：*[Custom Request Router 指南](https://docs.ray.io/en/master/serve/advanced-guides/custom-request-router.html)

## **自定义自动扩缩：扩你在意的**

Ray Serve 的自动扩缩通常基于请求计数，但对复杂流水线可能不够。在 Ray 2.51 中，我们发布了自定义扩缩策略支持，让你完全掌控 Ray Serve 应用的扩缩。现在开发者可以：

- 从副本向 controller 上报**自定义指标**
- 定义基于自定义上报指标或外部指标/触发的**策略逻辑**
- 把扩缩策略的作用范围限定到某个 deployment 或整个应用

有了自定义自动扩缩，你可以按**自己对性能的定义**扩缩，也可以定义复合策略，协调应用内多个 deployment 的扩缩。把扩缩循环开放给用户定义的指标与逻辑后，Serve 提供了更细粒度的控制——让自动扩缩成为在吞吐、成本与延迟之间平衡的实用工具。

**真实案例**：Huawei 在多阶段 LLM 流水线（预处理 → 模型 → 后处理）上用自定义自动扩缩，基于**端到端延迟 SLA** 而非单阶段负载对各级联合扩缩。这带来了更智能的资源利用与可变负载下更可预测的延迟。

其他常见扩缩模式：

- **基于队列深度的扩缩**：对无 HTTP 请求的异步推理负载，可按队列深度扩缩消费者。
- **定时扩缩：** 按计划增删副本。
- **基于利用率的扩缩：** 用 GPU 使用指标（如显存或 SM 占用）驱动扩缩决策，优化昂贵算力。
- **跨 deployment 协调：** 让预处理与后处理阶段与模型副本同步扩缩，避免流水线瓶颈。

Ray Serve 的自定义自动扩缩支持是与 Huawei 合作开发的。我们特别致谢 [Arthur Leung](https://github.com/arcyleung) 与 [Kishanthan Thangarajah](https://github.com/Kishanthan) 的贡献。

**工作原理**

1.（可选）定义从 Serve Deployment 副本上报自定义指标

```
1from ray import serve
2
3@serve.deployment
4class MyDeployment:
5    def record_autoscaling_stats(self) -> Dict[str, float]:
6        return {"custom_metric": 100}
```

2. 用来自 deployment、Prometheus 指标或外部来源的数据编写你的自定义扩缩策略

```
1from ray.serve.config import AutoscalingContext
2from ray.serve._private.common import DeploymentID
3
4def application_level_autoscaling_policy(
5    ctxs: Dict[DeploymentId, AutoscalingContext]
6) -> Tuple[Dict[DeploymentId, int], Dict]:
7    pass
```

3. 把自定义策略加入 serve YAML

```
1applications:
2  - name: MyApp
3    import_path: app:api
4    autoscaling_policy:
5      policy_function: policy:application_level_autoscaling_policy
6    deployments: ...
7
```

如果你愿意贡献普遍适用的自定义路由或扩缩策略，请到 Slack 或 GitHub 上联系我们。

*Ray Serve - 自定义自动扩缩*

📘 *文档：*[Custom Autoscaling Policies](https://docs.ray.io/en/master/serve/advanced-guides/advanced-autoscaling.html#custom-autoscaling-policies)

## 外部扩缩：自带你的逻辑

虽然 Ray Serve 的内建自动扩缩与自定义策略提供了灵活的指标驱动扩缩，但在某些场景你想完全掌控——基于外部数据源与系统扩缩。这正是 External Scaling 的用武之地。该功能将在 Ray 2.52（alpha）引入：External Scaling API 让你以编程方式调整 Serve 应用中任意 deployment 的副本数。与运行在 Serve 控制循环内的自动扩缩不同，外部扩缩由你自己的脚本或服务驱动——非常适合预测式或事件触发的扩缩。

*Ray Serve - 外部扩缩*

**工作原理**

**1. 启用外部扩缩：** 在 Serve YAML 中设置 `external_scaler_enabled: true`，告诉 Ray Serve 扩缩决策将来自外部控制器

```
1applications:
2  - name: my-app
3    import_path: external_scaler_predictive:app
4    external_scaler_enabled: true
5    deployments:
6      - name: TextProcessor
7        num_replicas: 1
```

**2. 构建你的外部扩缩器。** 你可以写一个简单的 Python 客户端，按任何你选定的逻辑为 deployment 扩缩。例如，下面是一个预测式扩缩器：工作时段增副本、下班后缩容：

```
1target = 10 if 9 <= hour < 17 else 3
2requests.post(
3    f"{SERVE_ENDPOINT}/api/v1/applications/{app_name}/deployments/{deployment_name}/scale",
4    json={"target_num_replicas": target},
5)
```

这段逻辑可以放在独立脚本、cron 任务，甚至一个定时检查指标并触发扩缩事件的云函数里。

把扩缩暴露为 API 后，Ray Serve 让你能把扩缩决策融入更广的运维生态——从业务工作流到 MLOps 流水线。这是让扩缩从"负载驱动"迈向"意图驱动"的有力一步。

## **组合起来**

异步推理、自定义请求路由与自定义自动扩缩，都建立在 Serve 既有的多模型与流水线服务基础之上。这些新增让 Serve 更**可编程、更可适配**，给开发者更深的应用行为控制。

借助这些特性，团队可以：

- 更安全地处理长时或异步负载
- 按应用特定逻辑或模型行为路由请求
- 用反映真实性能需求的指标扩缩副本

Serve 持续弥合模型开发与生产之间的鸿沟，坚持让系统保持 Pythonic、可组合，并默认具备可扩展性。
