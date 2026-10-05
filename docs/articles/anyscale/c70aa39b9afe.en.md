---
vendor: anyscale
title: Ray Serve: Advancing Flexibility with Async Inference, Custom Request Routing, and Custom Autoscaling
original_title: Ray Serve: Advancing Flexibility with Async Inference, Custom Request Routing, and Custom Autoscaling
url: https://anyscale.com/blog/ray-serve-autoscaling-async-inference-custom-routing
date: 2025-11-11
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 27a263ab77fe
---

Home

Blog

Blog Detail

# Ray Serve: Advancing Flexibility with Async Inference, Custom Request Routing, and Custom Autoscaling

By

Abrar Sheikh

,

Harshit Agarwal

and

Akshay Malik

|

November 11, 2025

Over the past year, **Ray Serve** has become the go-to choice for teams looking to productionize multimodal AI workloads—from LLMs to speech analytics and video pipelines.

ray serve updates

We’re introducing four new capabilities that dramatically expand Serve’s flexibility and scalability for modern inference workloads:

- **Async Inference** – handle long-running or resumable workloads safely and efficiently
- **Custom Request Routing** – gain precise control over how requests are distributed across deployment replicas
- **Custom Autoscaling** – build your own scaling logic driven by domain-specific metrics
- **External Scaling** – scale serve applications from exogenous system

Together, these features make it easier to build complex, latency-sensitive, or multi-stage AI systems in production.

## Link**Why Flexibility Matters**

AI workloads are increasingly **heterogeneous**. A single pipeline might combine:

- ASR → Speaker verification → LLM summarization → Analytics
- Recommenders → Rerankers → Embedding models
- Chunk Video Frames → Decode → Inference → Post-processing

Each stage can have distinct runtime behavior, resource demands, and latency constraints.
Ray Serve provides **unified control** across these stages, handling routing, autoscaling, batching, and observability—so teams can iterate on models, not infrastructure.

## Link**Async Inference: Handle Long-Running Workloads Safely**

Async workloads are common across AI systems — including batch summarization, transcription, video processing, and multi-step agent workflows. These are often implemented using separate queue systems like Celery, Kafka, or custom job schedulers.

With **Async Inference**, Ray Serve integrates asynchronous processing directly into the same serving layer used for online inference. This lets teams handle near real-time and long-running requests without client timeouts, track progress or resume tasks safely, and manage both synchronous and asynchronous workloads within a single runtime — without introducing additional infrastructure.

Key advantages of using Ray Serve for async workloads:

- **Simpler architecture:** Serve integrates with message brokers like Redis or SQS for queuing and retries, while managing task submission and processing within the same runtime.
- **Unified runtime for heterogeneous workloads:** Mix GPU-intensive inference with longer CPU- or I/O-bound processing within the same application.
- **Shared scaling and observability:** Async workers leverage the same Serve autoscaler and metrics pipeline as standard Ray Serve deployments.
- **Consistent Python APIs:** Reuse logic and dependencies across online, async, and streaming workloads.
- **At least once processing guarantees**: ensure safe execution of tasks during replica failure and service rollouts.

**A real-world example: **

Fano AI — a Hong Kong–based language-AI company serving multilingual contact centers—runs heavy audio pipelines (ASR, speaker verification, and LLM analytics) on Ray Serve + Kubernetes (via KubeRay).

> “Async inference is necessary for us to handle multi-hour audio uploads and post-call analytics so requests don’t time out. Progress can be tracked, and we can retry or resume safely without blocking online traffic.” — Sam Broughton, Fano AI

**How it works:**

To enable async inference in Ray Serve, there are 2 core components:

1. Setup your task processing config - This consists of configuration for the message broker (e.g. Redis, SQS, etc.) and DLQ behavior.

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

2. Define your task processor logic - Here you can define your business logic and also compose dynamic inference graphs.

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

3. Define an ingress deployment to submit tasks and fetch status

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

This will set up two deployments - one responsible for enqueueing requests and responding to status calls. And the other responsible for polling the message queue and executing your processing logic.

Ray Serve - Routing

***Docs:***[ Asynchronous Inference in Ray Serve](https://docs.ray.io/en/master/serve/asynchronous-inference.html)

## Link**Custom Request Routing: Programmable Traffic Control**

Ray Serve’s default routing algorithm works based on the number of requests at different replicas. However, some applications may require routing decisions that depend on the request content, model version at different replicas, or workload state.

With the new **Custom Request Router** API, Serve makes routing fully programmable in Python. This feature enables you to embed domain-specific intelligence directly into Serve’s routing layer.

**A real-world example**: For serving a multi-turn conversation chatbot, LLMs can take advantage of the [prefix cache](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html) which stores computed KV vectors from previous requests’ attention computations. If multiple requests share the same starting text (the “prefix”), the system can reuse earlier computations (a hot prefix cache) to reduce latency and reduce GPU cycle waste. A policy that can route requests based on request content can result in significantly better throughput/latency performance of the system. See more details in our [blog](https://www.anyscale.com/blog/ray-serve-faster-first-token-custom-routing) for reducing LLM inference latency by up to 60% with custom routing.

Custom routers can commonly be used for:

- Cache affinity — route requests to replicas that already hold relevant data or model weights - Ray Serve multiplexing is one such example of a built-in router.
- Latency awareness — bias toward replicas with shorter recent response times.
- Stateful replicas — maintain per-session or per-user affinity without external coordination.
- Dynamic prioritization — favor replicas based on runtime metrics or request type.

**How it works:**

1. (Optional) Emit custom routing statistics from your serve deployment

```
1from ray import serve
2
3@serve.deployment
4class MyDeployment:
5    def record_routing_stats(self) -> Dict[str, float]:
6        return {"throughput": 100}
```

2. Implement your own subclass of RequestRouter and override choose_replicas().

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

3. Attach the custom router to your Serve deployment

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

Ray Serve - Custom Routing

*Docs:*[ Custom Request Router Guide](https://docs.ray.io/en/master/serve/advanced-guides/custom-request-router.html)

## Link**Custom Autoscaling: Scale What Matters**

Ray Serve autoscaling typically uses request counts, but that may not be sufficient for complex pipelines. In Ray 2.51, we released support for custom autoscaling policies, giving you full control over scaling your Ray Serve applications. Now developers can:

- Emit **custom metrics** from replicas to the controller
- Define a custom **policy logic** that operates off custom emitted metrics or external metrics/triggers
- Scope scaling policies to a deployment or the full application

With custom auto-scaling, you can scale based on **your definition of performance**. You can also define compound policies that coordinate scaling across multiple deployments within an application. By opening the autoscaling loop to user-defined metrics and logic, Serve allows more fine-grained control—turning autoscaling into a practical tool for balancing throughput, cost, and latency.

**A real-world example**: Huawei uses custom autoscaling for multi-stage LLM pipelines—preprocessing → model → postprocessing—scaling stages jointly based on **end-to-end latency SLAs**, not just per-stage load. This enables smarter resource utilization and more predictable latency under variable workloads.

Some other common patterns for auto-scaling:

- **Queue-depth based scaling**: For async inference workloads where there are no HTTP requests, you can scale your consumers based on queue depth.
- **Scheduled scaling:** Increase or decrease replicas based on a schedule.
- **Utilization-based scaling:** Trigger scaling decisions from GPU usage metrics (e.g., memory or SM occupancy) to optimize expensive compute resources.
- **Cross-deployment coordination:** Scale pre-processing and post-processing stages in sync with model replicas to avoid pipeline bottlenecks.

Support for custom autoscaling in Ray Serve was developed in collaboration with Huawei. We would like to especially acknowledge the contributions of [Arthur Leung](https://github.com/arcyleung) and [Kishanthan Thangarajah](https://github.com/Kishanthan).

**How it works**

1. (Optional) Define emission of custom metrics from the Serve Deployment replicas

```
1from ray import serve
2
3@serve.deployment
4class MyDeployment:
5    def record_autoscaling_stats(self) -> Dict[str, float]:
6        return {"custom_metric": 100}
```

2. Write your custom auto-scaling policy using metrics gathered from the deployments, prometheus metrics or external sources

```
1from ray.serve.config import AutoscalingContext
2from ray.serve._private.common import DeploymentID
3
4def application_level_autoscaling_policy(
5    ctxs: Dict[DeploymentId, AutoscalingContext]
6) -> Tuple[Dict[DeploymentId, int], Dict]:
7    pass
```

3. Add the custom policy to your serve YAML

```
1applications:
2  - name: MyApp
3    import_path: app:api
4    autoscaling_policy:
5      policy_function: policy:application_level_autoscaling_policy
6    deployments: ...
7
```

If you would like to contribute custom routing or auto-scaling policies that can be generally beneficial, please reach out to us in slack or Github.

Ray Serve - Custom Autoscaling

📘 *Docs:*[ Custom Autoscaling Policies](https://docs.ray.io/en/master/serve/advanced-guides/advanced-autoscaling.html#custom-autoscaling-policies)

## LinkExternal Scaling: Bring Your Own Logic

While Ray Serve’s built-in autoscaling and custom policies provide flexible, metric-driven scaling, there are scenarios where you want complete control—scaling based on external data sources and systems. That’s where External Scaling comes in. Going to be introduced in Ray 2.52 (alpha), the External Scaling API lets you programmatically adjust replica counts for any deployment in your Serve application. Unlike autoscaling, which runs inside the Serve control loop, external scaling is driven by your own scripts or services—ideal for predictive or event-triggered scaling.

Ray Serve - External Scaling

**How It Works**

**1. Enable External Scaling: **Set external_scaler_enabled: true in your Serve YAML. This tells Ray Serve that scaling decisions will come from an external controller

```
1applications:
2  - name: my-app
3    import_path: external_scaler_predictive:app
4    external_scaler_enabled: true
5    deployments:
6      - name: TextProcessor
7        num_replicas: 1
```

**2. Build Your External Scaler. **You can write a simple Python client that scales deployments based on any logic you choose. For example, here’s a predictive scaler that increases replicas during business hours and scales down after hours:

```
1target = 10 if 9 <= hour < 17 else 3
2requests.post(
3    f"{SERVE_ENDPOINT}/api/v1/applications/{app_name}/deployments/{deployment_name}/scale",
4    json={"target_num_replicas": target},
5)
```

This logic can live in a standalone script, cron job, or even a cloud function that periodically checks metrics and triggers scaling events.

By exposing scaling as an API, Ray Serve now lets you integrate scaling decisions into your broader operational ecosystem—from business workflows to MLOps pipelines. It’s a powerful step toward making scaling intent-driven, not just load-driven.

## Link**Putting It All Together**

Async Inference, Custom Request Routing, and Custom Autoscaling build on Serve’s existing foundation for multi-model and pipeline serving. These additions make Serve more **programmable and adaptable**, giving developers deeper control over how their applications behave.

With these features, teams can:

- Handle long-running or asynchronous workloads more safely
- Route requests based on application-specific logic or model behavior
- Scale replicas using metrics that reflect real performance needs

Serve continues to bridge the gap between model development and production with a focus on keeping systems Pythonic, composable, and scalable by default.

#### Table of contents

- [Why Flexibility Matters](https://www.anyscale.com/blog/ray-serve-autoscaling-async-inference-custom-routing#why-flexibility-matters)
- [Async Inference: Handle Long-Running Workloads Safely](https://www.anyscale.com/blog/ray-serve-autoscaling-async-inference-custom-routing#async-inference:-handle-long-running-workloads-safely)
- [Custom Request Routing: Programmable Traffic Control](https://www.anyscale.com/blog/ray-serve-autoscaling-async-inference-custom-routing#custom-request-routing:-programmable-traffic-control)
- [Custom Autoscaling: Scale What Matters](https://www.anyscale.com/blog/ray-serve-autoscaling-async-inference-custom-routing#custom-autoscaling:-scale-what-matters)
- [External Scaling: Bring Your Own Logic](https://www.anyscale.com/blog/ray-serve-autoscaling-async-inference-custom-routing#external-scaling:-bring-your-own-logic)
- [Putting It All Together](https://www.anyscale.com/blog/ray-serve-autoscaling-async-inference-custom-routing#putting-it-all-together)

#### Sharing

#### Tags

#### Sign up for product updates

#### Recommended content

#### Ray Summit 2026: Physical AI, RL, and the infrastructure that runs them all

Read more

#### Scaling Ray for AI workloads to 10k node clusters

Read more

#### Optimizing LLM Serving Efficiency: Moving Beyond KV Cache Reuse to Token-Load Awareness with Ray Serve LLM

Read more

## Explore Anyscale today

Build, run, and scale any AI workload on Ray with a multi-cloud platform built for production AI.

Start for Free

Talk to an expert
