---
vendor: huggingface
title: Asynchronous Robot Inference: Decoupling Action Prediction and Execution
original_title: Asynchronous Robot Inference: Decoupling Action Prediction and Execution
url: https://huggingface.co/blog/async-robot-inference
date: 2023-04-23
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: cdcdbba8addb
---


# Asynchronous Robot Inference: Decoupling Action Prediction and Execution

					July 10, 2025

Update on GitHub


56

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/NwJ2pTzURXwSiQPcdCdPp.png)](https://huggingface.co/PipasGonzalez)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1653590885464-noauth.png)](https://huggingface.co/EddyGiusepe)
- [![](https://huggingface.co/avatars/a75b1cafa0c581732f8641249b92902c.svg)](https://huggingface.co/aakinlalu)
- [![](https://huggingface.co/avatars/0fcf9c5c2d2c3b0d6a558b4008e063d1.svg)](https://huggingface.co/xiaofan01)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/HOikmxgX-kUgECNfVr53v.png)](https://huggingface.co/CyberThinker)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)

Francesco Capuano

fracapuano

Steven Palma

imstevenpmwork

Michel Aractingi

aractingi

Mustafa Shukor

mshukor

Dana Aubakirova

danaaubakirova

Adil Zouitine

AdilZtn

Simon  Alibert

aliberts

Remi Cadene

cadene

**TL;DR** Robotic policies are increasingly bulky, and predict chunks of future actions rather than a single next action. This results in the robot being idle while awaiting new actions to perform, introducing noticeable lags at execution, and lacking responsiveness. Asynchronous inference tightens the control loop, removing lags at runtime and resulting in more adaptive control by decoupling action prediction from action execution. In this blog post, we cover the basics behind async inference, and how it can be used to improve the performance of robotic policies in the real-world.

## Table of Contents

- [Getting started](https://huggingface.co/blog/async-robot-inference#getting-started)
- [Async inference: a deep dive](https://huggingface.co/blog/async-robot-inference#async-inference-a-deep-dive)
- [1. Why sequential inference falls short](https://huggingface.co/blog/async-robot-inference#1-why-sequential-inference-falls-short)
- [2. Asynchronous inference, in a nutshell](https://huggingface.co/blog/async-robot-inference#2-asynchronous-inference-in-a-nutshell)
- [3. System Architecture](https://huggingface.co/blog/async-robot-inference#3-system-architecture) [Robot Client](https://huggingface.co/blog/async-robot-inference#robot-client) [Policy Server](https://huggingface.co/blog/async-robot-inference#policy-server)
- [4. Analyzing async inference](https://huggingface.co/blog/async-robot-inference#4-analyzing-async-inference)
- [5. Using async in your setup](https://huggingface.co/blog/async-robot-inference#5-using-async-in-your-setup)
- [Conclusions](https://huggingface.co/blog/async-robot-inference#conclusions)

## Getting started

Get started with async inference by following [our tutorial](https://huggingface.co/docs/lerobot/en/async).

*Sequential inference (first) versus async inference (second)*. Allowing for replanning and a tighter control loop, async inference results in (1) attempts at recovery, and (2) a ~2x speedup in task completion. Sequential inference keeps acting out the current action chunk even after failure to grasp the object, while async inference can replan and act the new action chunk. Both setups use the same policy!

## Async inference: a deep dive

With async inference, we decouple action execution from action prediction. This is particularly relevant considering the tendency of currently popular models like [[ACT](https://huggingface.co/papers/2304.13705)], [[OpenVLA](https://huggingface.co/papers/2406.09246)], [[PI0](https://huggingface.co/papers/2410.24164)], and [[SmolVLA](https://huggingface.co/papers/2506.01844)] to be outputting chunks of actions at:t+Ha_{t:t+H}at:t+H​ rather than single actions ata_tat​ given an observation oto_tot​. Convince yourself of this by running all these models using [LeRobot](https://huggingface.co/lerobot).

Using chunks sequentially results in (1) lags at runtime, impacting task execution time and (2) lack of responsiveness, due to acting widely open-loop. Asynchronous inference mitigates both these limitations by **decoupling action prediction from action execution**. We introduced asynchronous inference in SmolVLA, and found it to result in a ~2x speed-up in task completion time with comparable task success rate.

In particular, we design a 2-component system where policy inference and action execution are performed in two different processes, possibly on two different machines connected through the network:

- A **`PolicyServer`**, hosted on accelerated hardware and capable of running inference using more computational resources than the ones allocated on a real-world robot.
- A **`RobotClient`** enqueues the received actions and executes them while the next chunk is being computed.

Communication between `PolicyServer` and `RobotClient` relies on **gRPC**, which guarantees ~5× faster performance than a comparable REST API. The result of all of this is a robot that *never* waits for inference.

![Async inference scheme](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/async-inference/async_scheme.png)

*Asynchronous inference*, highlighting: (1) The client sending the first observation for inference, receiving the first chunk shortly after; (2) The client sending another observation for processing while it has not yet exhausted the current chunk; (3) The client receiving an updated action chunk, which it aggregates with the remainders of the one it was previously executing.

## 1. Why sequential inference falls short

Suppose a policy π \pi π maps the current observation ot o_t ot​ to a sequence of H H H future actions. Formally, π:O ↦ A,At=(at,at+1,…at+H)=π(ot)\pi : \mathcal{O} \;\mapsto\; \mathcal{A}, \mathbf{A}_t = \begin{pmatrix} a_{t}, & a_{t+1}, & \dots & a_{t+H} \end{pmatrix} = \pi(o_t)π:O↦A,At​=(at​,​at+1​,​…​at+H​​)=π(ot​).

A traditional control loop would therefore consist of the following steps:

- Capture ot o_t ot​.
- Run π(ot) \pi(o_t) π(ot​) to obtain At=π(ot) \mathbf{A}_t = \pi(o_t) At​=π(ot​).
- Enqueue At\mathbf{A_t} At​ and start acting popping actions from the queue.
- If the queue is empty, wait for At+H \mathbf{A}_{t+H} At+H​, otherwise repeat step 3.

During step 2 the robot is **idle**. The latency grows with the model size (and models tend to be increasingly bulky over time), and can quickly dominate interaction time (which is typically around 1/`fps`), as shown in the video below (coming from our [Discord community](https://discord.com/invite/ttk5CV6tUw) 🤗):

This directly results in (1) reduced performance in terms of task completion time---the robot needs to be waiting for the next action chunk to be computed---and (2) reduced responsiveness, due to (2.1) acting widely open-loop while actions are available and (2.2) complete idleness while waiting for the next action chunk.

(Left)*Sequential inference* with highlighted idle periods. (Right)*Time to select an action* showing spikes when inference is triggered due to local queue exhaustion (inference latency is around ~100ms---~3 frames at 30fps---using an ACT model on a 2021 MacBook Pro).

## 2. Asynchronous inference, in a nutshell

Our system removes the idle period by overlapping computation and execution:

- `RobotClient` streams the latest observation to `PolicyServer`.
- While the server performs inference, the client executes the **current queue** of actions.
- New actions arrive, are merged into the queue, and the loop continues.

The key idea is that the robot already knows what to do for the next few timesteps, so it can keep moving while fresh actions are being computed on the server.

![Async inference diagram](https://github.com/user-attachments/assets/6f323660-52b4-4537-8bde-f9b70b7f1bc0)

*Asynchronous inference* overlaps in time the execution of the current action chunk with the computation of the next one, by decoupling these two processes, possibly running them on entirely distinct machines connected through the network.

This results in a tighter control loop, and a robot that never waits for inference. In turn, this results in ~2x speedup in task completion time with comparable task success rate, and more adaptive control coming from a tighter loop (see video below).

## 3. System Architecture

| Component | Role | Technology |
| --- | --- | --- |
| **RobotClient** | Runs on-board, streams observations, maintains an **action queue**, executes actions | Python, gRPC |
| **PolicyServer** | Hosts the policy, performs batched inference, sends action chunks back | Python, gRPC, possibly accelerated hardware (GPU/TPU) |

Because gRPC is HTTP/2-based and uses protocol buffers, it achieves low-latency binary messaging and bidirectional streams out of the box, which in turn helps us maintain a tighter control loop and sub-100ms round-trip latency (on our local network, and hosting SmolVLA on a NVIDIA RTX 4090).

The `RobotClient` runs on-board, and streams observations to the `PolicyServer` through gRPC. The `PolicyServer` prepares the observations received for inference, and sends back to the `RobotClient` an action chunk.

### Robot Client

![From client perspective](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/async-inference/from_client_perspective.png)

*From the client's perspective*, observations are streamed to the server according to the local queue status. Incoming chunks are aggregated on overlapping portions with the currently available action queue.

The `RobotClient` maintains a local action queue and follows a simple yet effective strategy: **send a new observation when the queue length drops below a configurable threshold** (\(g\) in the SmolVLA paper, `chunk_size_threshold` in the code). This threshold value, expressed as a fraction of the maximum chunk size, acts as a trigger condition that balances computational load with responsiveness.

![Client to server](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/async-inference/client_to_server.png)

*The client streams observations to the server*, according to the local queue status.

From the client's perspective, the process unfolds as follows:

- **Queue monitoring**: The client continuously monitors its action queue length against a **chunk size threshold** parameter. When the queue drops below this threshold, it signals that a new observation should be sent for processing.
- **Observation streaming**: Once the threshold condition is met, the client captures the current observation and streams it to the `PolicyServer` via gRPC. Crucially, **observations are streamed rather than being sent via a unary RPC** because they typically exceed the maximum message size of 4MB (multiple camera captures at high resolution result in this).
- **Action chunk aggregation**: When a new action chunk arrives from the server, the client merges it with any remaining actions in the current queue over the overlapping portion. This is where **custom aggregators** come into play, handling overlapping sections between the current and incoming chunks differently. As of now, we support flexibly aggregation between the chunks via the specification of a custom `aggregate_fn(chunk1: torch.Tensor, chunk2: torch.Tensor) -> torch.Tensor` function, which is called for each overlapping timestep and can be user-provided. The overlapping portions (shown in light blue in the diagram) require careful handling. We can design different aggregation strategies:  **Replace**: Simply replace overlapping actions with the newer predictions **Weighted blend**: Combine overlapping actions using temporal weights (closer actions get higher weight)

This system is highly configurable, as the chunk size threshold can be tuned based on network latency, model inference time, and desired responsiveness. A lower threshold means more frequent updates (and higher computational cost), while a higher threshold reduces communication overhead at the expense of potential queue starvation. Lastly, we typically receive actions from `PolicyServer` in a thread, and perform them in another one. This keeps the client listening for incoming chunks in a separate thread, without blocking execution and always consuming the current chunk until a new one becomes fully available.

### Policy Server

Upon receiving observations from the `RobotClient`, the `PolicyServer` receives observations from the `RobotClient`, and performs the necessary observation cleaning to make received observations ready for inference. This process is illustrated in the image below:

![Server pipeline](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/async-inference/server_pipeline.png)

*The observation cleaning pipeline* running on the server, highlighting the three main steps related to (1) Keys matching (2) Preprocessing and (3) Preparation for inference.

Once the observation has been prepared, it is compared with the last observation used for inference. This avoids collapsing into a loop whereby very similar observations are processed, thus triggering unnecessary inference and similar actions being executed (which in turn, result in very similar observations being processed again). We compare observations in terms of their joint-space similarity, which provides us an approximate and quick way of measuring changes in the robot. Clearly, this metric is not adaptive to dynamic changes in the environment (an object changing its position, or disturbances being applied), but we found it to be a good trade-off for the majority of the cases, and to be very effective in avoiding unnecessary inference and state collapse. Critically, the `RobotClient` retains control over whether a given observation must be processed, to avoid deadlocks. Observations sent by the client and tagged with `must_go=True` are processed regardless of the similarity metric.

![Policy workflow](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/async-inference/policy_workflow.png)

*The policy workflow*, in which incoming observations are compared to the last one used for inference, and processed only if different enough, or `must_go`.

Lastly, to ensure the `PolicyServer` always processes the latest available observation, we block incoming observations until the previous one has been successfully processed. In this, we leverage queues on the `PolicyServer` to ensure incoming observations are not enqueued until the server is ready to process them (see below).

![Client pings server](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/async-inference/client_pings_server.png)

*The client pings the server every 1/fps seconds*, but observations are not enqueued for processing until the previous one has been successfully processed.

## 4. Analyzing async inference

For all practical purposes, in async inference there are two time-scales that matter:

- **Environment step** environment_dt=1/fps\texttt{environment\_dt} = 1/\texttt{fps}environment_dt=1/fps, depicting how fast the robot can perform an action.
- **Inference latency** inference_time\texttt{inference\_time}inference_time: forward-pass + network round-trip. We can assume the network round-trip to be negligible with respect to the policy inference time, though this might not be the case for every setup.

Importantly, the ratio c=environment_dtinference_time c = \frac{\texttt{environment\_dt}}{\texttt{inference\_time}} c=inference_timeenvironment_dt​ results in different behaviours:

- c≪1c \ll 1c≪1: environment evolves faster than inference. In this scenario, the queue empties quickly and we degenerate to sequential control.
- c≥1c \ge 1c≥1: server keeps up. The queue is always (nearly) full.

Critically, ccc influences the number of available actions in the queue at any given time. To avoid the aforementioned sequential limit control, one can:

- **Use more compute for the policy server**, hosting the server on a GPU, reducing inference_time\texttt{inference\_time}inference_time as a consequence of allocating more computational resources.
- **Sending observations to the server more often**, send a new observation when the queue length kkk drops below a **fraction** g=k/Hg = k/Hg=k/H of its maximum size. g=0g=0g=0 reproduces sequential inference (empty queue, wait). g=1g=1g=1 sends an observation every timestep (max compute, minimal lag).

Experiments (see plots below) show that g≈0.7g\approx0.7g≈0.7 offers a good trade-off when observations sent are not filtered out (they are all must-go). We recommend setting g=0.5g=0.5g=0.5 and following [our documentation](https://huggingface.co/docs/lerobot/en/async) to tune this parameter to your needs.

![Queues](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/async-inference/queues.png)

*The number of available actions in the queue at any given time*, as a function of g. Larger values of g result in more frequent updates, and more computational cost. Values of g closer to 0 reproduce sequential inference (empty queue, wait). We found g~0.7 to be a good trade-off in our experiments.

## 5. Using async in your setup

Async inference is a simple yet effective way to improve the performance of robotic policies. In our experiments using SmolVLA, async inference results in a ~2x speedup in task completion time with comparable task success rate, and more adaptive control coming from a tighter loop.

To run your policy using async inference, you just need to follow our [tutorial](https://huggingface.co/docs/lerobot/en/async) with your own custom parameters (e.g., the policy path or the chunk size threshold). Async inference comes with support for policies supporting action chunking!

## Conclusions

We have introduced async inference, a simple yet effective way to improve the performance of robotic policies. In our experiments using SmolVLA, async inference results in a ~2x speedup in task completion time with comparable task success rate, and more adaptive control coming from a tighter loop.

We are excited to share this work with the community, and to see how it can be used to improve the performance of robotic policies. We welcome PRs to improve and extend the async inference framework at [`huggingface/lerobot`](https://huggingface.co/lerobot), and are available to discuss this further in our [Discord community](https://discord.com/invite/ttk5CV6tUw), 🤗.

## Papers mentioned in this article 4

More Articles from our Blog

smolvla

lerobot

robotics

Hot

## SmolVLA: Efficient Vision-Language-Action Model trained on Lerobot Community Data

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/640e21ef3c82bd463ee5a76d/nVR1DFPAsiLw6Boys28Rb.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65d66b494bbd0d92b641cdbb/6-7dm7B-JxcoS1QlCPdMN.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6141a88b3a0ec78603c9e784/DJsxSmWV39M33JFheLobC.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/608aabf24955d2bfc3cd99c6/-YxmtpzEmf3NKOTktODRP.jpeg)
- +5

376

June 3, 2025

robotics

ai

community

## Grabette: an open system to record robot-manipulation data

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/62f62a29d278a8f3e781e28a/5avng3ahybi8q3PatO2zv.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/aoooGNZNHaCqBi_oyHtli.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/gfokTsHI5Qe_l-8cObh90.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65af8030317cc62a3a255197/pyM6dRZ235g1TiwM_9uQr.png)
- +2

64

July 21, 2026

### Community

nalinraut

Mar 14

Came across this while I was working on something similar. Good work.

I built Inferential to handle multi-robot inference orchestration on Ray Serve. Deadline-aware scheduling scores requests across cadence urgency (EMA-tracked), robot-reported priority, anti-starvation age, trajectory progress, and static priority. ZMQ ROUTER/DEALER transport with protobuf+numpy wire format -- under 1ms serialize-transmit-deserialize vs ~100ms over gRPC. Request TTL, overflow policies, automatic disconnect detection, dispatch retry.

Will try to benchmark Inferential as well.

Open source. SDKs in Python, C++, and Rust.
github.com/nalinraut/inferential
Full writeup: nalinraut.github.io/blog/2026/inferential/

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fasync-robot-inference) or [log in](https://huggingface.co/login?next=%2Fblog%2Fasync-robot-inference) to comment


56

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/NwJ2pTzURXwSiQPcdCdPp.png)](https://huggingface.co/PipasGonzalez)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1653590885464-noauth.png)](https://huggingface.co/EddyGiusepe)
- [![](https://huggingface.co/avatars/a75b1cafa0c581732f8641249b92902c.svg)](https://huggingface.co/aakinlalu)
- [![](https://huggingface.co/avatars/0fcf9c5c2d2c3b0d6a558b4008e063d1.svg)](https://huggingface.co/xiaofan01)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/HOikmxgX-kUgECNfVr53v.png)](https://huggingface.co/CyberThinker)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/668bd06dd58b51a628566d80/II7Yr5dT5ItMrpoMkQEy3.jpeg)](https://huggingface.co/aractingi)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/5dd96eb166059660ed1ee413/NQtzmrDdbG0H8qkZvRyGk.jpeg)](https://huggingface.co/julien-c)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6141a88b3a0ec78603c9e784/DJsxSmWV39M33JFheLobC.jpeg)](https://huggingface.co/merve)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/652d34483184d39abdc11607/N15lvxITxY8EWfl-UJ09B.png)](https://huggingface.co/Services-Oversonic)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7QqMWTFAZpw7qN7GqjfA6.png)](https://huggingface.co/Test7777722222)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63d10d4e8eaa4831005e92b5/7p7-OmWM6PqqCs7ZStPGD.jpeg)](https://huggingface.co/m-ric)

## Papers mentioned in this article 4
