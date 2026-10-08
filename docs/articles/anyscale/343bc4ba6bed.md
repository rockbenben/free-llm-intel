---
vendor: anyscale
title: 利用LeRobot数据集和Ray优化VLA微调性能
original_title: 
url: https://anyscale.com/blog/vision-language-action-pipelines-vla-robotics-ray-anyscale
date: 2026-02-10
lang: zh
captured: 2026-10-08
extractor: readability-v1
translator: agent
status: translated
body_sha: 4f1d75d6e2b4
---

# 利用LeRobot数据集和Ray优化VLA微调性能

作者

Omar Shorbaji

和

Ian Jordan, PhD

|

2026 年 2 月 10 日

*VLA 微调之所以难以扩展，是因为 LeRobot 数据集格式在并行度与冗余 IO 之间存在一种内在的取舍。本篇博客描述了一种应对这一取舍、优化 VLA 微调性能的方法。*

## Link**引言**

在这篇文章里，我们会完整走一遍用 Ray 在 LeRobot Dataset 上做分布式 VLA 微调的可工作示例。我们对 [pi0.5](https://www.physicalintelligence.company/blog/pi05) 做微调，用的是 [xvla-soft-fold](https://huggingface.co/datasets/lerobot/xvla-soft-fold) 叠布料数据集（LeRobot v3.0 格式）。

有两个扩展性挑战驱动了这个设计：

- LeRobot Dataset v3.0 是机器人操作数据的一个新兴标准，但从它上面扩展读取可能很有挑战。具体来说，该格式把每个 episode 拆散到多个视频文件里（每个相机一个，另外还有一些存放元数据的表格文件），同时又把每个相机的许多 episode 拼接进同一个视频文件（为了节省空间）。结果就是，对数据集里的 episode 做朴素的并行处理，需要把每个 MP4 打开很多次（在 xvla-soft-fold 数据集上平均约 45 次）。我们提出一种 file-group 分区策略，在并行度与重复的视频打开之间求得平衡。在我们的实验里，这一做法把文件打开的次数减少了 15-135 倍。
- VLA 微调从根本上就是更大的模型加上更大的数据集，这就造成了 CPU/GPU 硬件上的错配。多相机视频解码和预处理是 CPU 与 I/O 密集的；训练 VLA transformer 是 GPU 密集的。把两者放在同一处会让 GPU 卡在 I/O 上。离线做预处理则会在训练开始之前额外搭上几个小时的时延和存储。理想的解法是把两者解耦。

Ray 解决了这些挑战。[Ray Data](https://docs.ray.io/en/latest/data/data.html) 把流式读取、解码和预处理跑在自动伸缩的 CPU worker 上，并通过一条带背压的管线喂给 GPU worker，不至于让 GPU 被 I/O 或图像解码卡住。[Ray Train](https://docs.ray.io/en/latest/train/train.html) 管理跨 GPU 的分布式 PyTorch，包括 DDP 搭建、checkpoint 和故障恢复。这两个阶段被串成一条管线，CPU 与 GPU 容量各自独立扩展。解码是瓶颈时就加 CPU 节点；训练是瓶颈时就加 GPU。

## Link**处理管线 **

在深入细节之前，下面是一幅表示这条管线的示意图。

一张机器学习管线示意图，展示了数据存储、读取与预处理步骤、模型训练，以及用于保存进度的 checkpoint 存储。

此外，下面是完整解决方案的顶层代码。大体上，这段代码

- 读取一个 lerobot 数据集
- 定义流式数据管线（在 CPU 上）
- 启动分布式训练（在 GPU 上）

这是顶层代码。

```
import ray
from lerobot_datasource import LeRobotDatasource

# ──────────────────────────────────────────────
# Stage 1: Build the streaming data pipeline (CPU)
# ──────────────────────────────────────────────
DATASET_PATH = "s3://anyscale-public-robotics-datasets/lerobot/lerobot/xvla-soft-fold"

CAMERA_RENAME = {
    "observation.images.cam_high":        "observation.images.base_0_rgb",
    "observation.images.cam_left_wrist":  "observation.images.left_wrist_0_rgb",
    "observation.images.cam_right_wrist": "observation.images.right_wrist_0_rgb",
}

source = LeRobotDatasource(DATASET_PATH)
stats = util.extract_stats(source)
image_keys = util.renamed_image_keys(source, CAMERA_RENAME)

ds = (
    ray.data
    .read_datasource(source)
    .map(rename_columns, fn_args=(CAMERA_RENAME,))                        # Rename cameras
    .map_batches(transpose_images, batch_size=32, fn_args=(image_keys,))  # HWC → CHW float32
)

# ──────────────────────────────────────────────
# Stage 2: Launch distributed training (GPU)
# ──────────────────────────────────────────────

trainer = ray.train.torch.TorchTrainer(
    train_loop_per_worker=train_loop_per_worker,
    train_loop_config={
        "stats": stats,
        "total_rows": source.meta.total_frames,
        "num_epochs": 2,
        "batch_size": 4,
        "grad_accum": 2,
        "lr": 1e-4,
        "warmup_frac": 0.1,
        "max_len": 512,
    },
    scaling_config=ray.train.ScalingConfig(num_workers=4, use_gpu=True),
    run_config=ray.train.RunConfig(
        name="pi05-xvla-soft-fold-finetune",
        storage_path="/mnt/cluster_storage/ray_train_runs/pi05_xvla_soft_fold",
        failure_config=ray.train.FailureConfig(max_failures=1),
    ),
    datasets={"train": ds},
)

result = trainer.fit()
```

在接下来几节里，我们逐一讨论这条管线的各个组件

## Link**第 1 部分：读取 LeRobot v3.0 数据格式 **

[LeRobot Dataset v3.0](https://huggingface.co/lerobot) 把数据存成三个分立的部分：分块的 Parquet 文件，存放逐帧的表格数据（动作、状态、时间戳）；分块的 MP4 文件，存放相机观测（每个相机一组视频文件）；以及把前两者关联起来的 episode 元数据，它记录每个 episode 属于哪一个 parquet 分块、哪一个视频文件。

要产出一条训练样本，数据加载器必须把这些部分 **join** 起来：先读一行 Parquet 拿到表格数据，然后在正确的时间戳处对每个相机的 MP4 文件做 seek-and-decode、解出对应的帧，再把它们与该 episode 的任务描述拼在一起。对 `xvla-soft-fold` 来说，这意味着要为每一帧把 3 路视频流（`cam_high, cam_left_wrist, cam_right_wrist`）与表格数据 join 起来。

把这条管线放在心里，我们就可以开始看系统层面，也就是通过为并行 I/O 划分数据来优化吞吐。我们把问题表述为：怎样把数据切成彼此独立的块，好让每个 worker 都能无冲突地独立读取和处理？

在 LeRobot Dataset v3 格式里，多个 episode 被打包进同一个 MP4 视频文件，同时又因为相机不同而被拆到不同的视频文件中。这种打包对存储很高效，因为它避免了产生大量小文件。但这样一来，并行处理多个 episode 就意味着要把每个 MP4 文件打开很多次，而这可能代价高昂。为了绕开这一点，LeRobot 库会把所有数据下载到本地磁盘，本地磁盘更适合随机访问，但这样限制了你能处理的数据集规模，也做不到有意义的并行。LeRobot 格式在最大化并行与最小化重复打开视频文件之间，存在着一种内在的取舍。

应对这一取舍的一种办法是 **file-group 分区**：把引用完全相同那组视频文件的 episode 归到一个任务里。下表是一个简化示例。在这个例子里，episode 1 和 2 共享同样的视频文件；episode 3 和 4、episode 5 和 6 也是同样。要把这 6 个 episode 并行化处理（分成 3 个任务），一个自然的做法就是把 episode 1 和 2 放在一起处理、episode 3 和 4 放在一起处理、episode 5 和 6 放在一起处理。

| **Episode** | **Cam 1** | **Cam2** | **Cam3** |
| --- | --- | --- | --- |
| 1 | cam1-01.mp4 | cam2-01.mp4 | cam3-01.mp4 |
| 2 | cam1-01.mp4 | cam2-01.mp4 | cam3-01.mp4 |
| 3 | cam1-02.mp4 | cam2-01.mp4 | cam3-01.mp4 |
| 4 | cam1-02.mp4 | cam2-01.mp4 | cam3-01.mp4 |
| 5 | cam1-03.mp4 | cam2-01.mp4 | cam3-01.mp4 |
| 6 | cam1-03.mp4 | cam2-01.mp4 | cam3-01.mp4 |

这样分区在并行化和视频文件 I/O 之间提供了一个平衡。对 `xvla-soft-fold`，结果是：

| **策略** | **任务数** | **视频打开次数** | **取舍** |
| --- | --- | --- | --- |
| 顺序执行 | 1 | 104 | I/O 最少，无并行 |
| 按 episode | 1,542 | 4,626 | 并行最大，I/O 放大极为严重 |
| **按 file group** | **99** | **297** | **均衡** |

在更大的数据集上，效果更为显著。例如 DROID（95K+ 个 episode）从 286K 次视频打开降到 2,124 次，**减少达 135×**。

### Link**实现 file-group 分区**

这个分区是纯粹的元数据计算。对每个 episode，用它在所有相机上的 (`video_key, chunk_index, file_index`) 指针构造一个键，然后把键相同的连续 episode 合并成按行范围划分的分区：

```
def _partition_by_file_group(episodes, video_keys):
    """Partition episodes by video-file group"""
    key_columns = []
    for vk in video_keys:
        key_columns.append(episodes.column(f"videos/{vk}/chunk_index").to_pylist())
        key_columns.append(episodes.column(f"videos/{vk}/file_index").to_pylist())

    from_indices = episodes.column("_global_from_index").to_pylist()
    to_indices = episodes.column("_global_to_index").to_pylist()

    ranges = {}  # signature → (first_row, last_row)
    for i in range(len(episodes)):
        key = tuple(col[i] for col in key_columns)
        from_idx, to_idx = from_indices[i], to_indices[i]
        if key in ranges:
            prev_from, prev_to = ranges[key]
            assert from_idx == prev_to, "Episodes in a file group must be contiguous"
            ranges[key] = (prev_from, to_idx)
        else:
            ranges[key] = (from_idx, to_idx)

    return list(ranges.values())
    # xvla-soft-fold: 1,542 episodes -> 99 partitions
```

每一对 (`start_row, end_row`) 变成一个 Ray Data 读取任务。该任务通过 PyAV 把每个 MP4 只打开一次，seek 到第一个 episode 的 `from_timestamp`，然后把解码出的帧顺着流成一个个 Arrow 批次。

有了分区策略在手，我们就可以直接从 S3 流式读取数据集，并搭起预处理管线

## Link**第 2 部分：用 Ray Data 做流式处理**

下面是流式处理的顶层代码

```
from lerobot_datasource import LeRobotDatasource

source = LeRobotDatasource("s3://…")
stats = util.extract_stats(source)
image_keys = util.renamed_image_keys(source, CAMERA_RENAME)

ds = (
    ray.data
    .read_datasource(source)                                             
    .map(rename_columns, fn_args=(CAMERA_RENAME,))                    
    .map_batches(transpose_images, batch_size=32, fn_args=(image_keys,)) 
)
```

这是一条惰性的、流式的管线。在 trainer 开始拉取之前，不会读取任何数据。一切都跑在 CPU worker 上，带有自动背压，从而在不把 GPU 卡在 I/O 或图像解码上的前提下让 GPU 一直有活干。我们逐步来看。

### Link**Ray Data Datasource**

Ray Data 提供了一个 [Datasource](https://docs.ray.io/en/latest/data/api/doc/ray.data.Datasource.html) 抽象，用于把自定义数据源接进流式执行引擎。我们用它来实现 LeRobot 的读取功能。一个 `LeRobotDatasource` 类负责元数据加载、file-group 分区，以及把 parquet 行与解码出的视频帧做流式 join，这一切都藏在 Ray Data 标准的 `read_datasource` 接口后面。

在构造时，这个 datasource 会立即加载数据集元数据（episode 表、归一化统计量、任务描述），同时把所有数据和视频 I/O 推迟到 worker 上：

```
source = LeRobotDatasource(DATASET_PATH)

# Metadata is available immediately -- no data files opened yet
print(source.meta.total_frames)      # total decoded rows
print(source.meta.total_episodes)    # 1,542
print(source.meta.video_keys)        # ['observation.images.cam_high', ...]
print(source.meta.tasks)             # {0: 'fold the cloth', ...}
print(source.meta.stats)             # per-feature mean/std for normalization
```

当调用 `read_datasource(source)` 时，它会创建 99 个 file-group 读取任务（默认的分区方式）。每个任务从 S3 流式读取，用 PyAV 解码 MP4 帧，把它们与 parquet 行 join 起来，并产出 Arrow 批次。我们稍后从 source 的元数据里取出归一化统计量，供训练循环使用。

### Link**相机重命名**

数据集的相机列名和 Pi05 期望的对不上。这个模型预训练时用的特征名是 `observation.images.base_0_rgb` 这一类，但数据集里是 `observation.images.cam_high`。一个轻量的逐行 `.map` 把它们改名：

```
CAMERA_RENAME = {
    "observation.images.cam_high":        "observation.images.base_0_rgb",
    "observation.images.cam_left_wrist":  "observation.images.left_wrist_0_rgb",
    "observation.images.cam_right_wrist": "observation.images.right_wrist_0_rgb",
}

def rename_columns(row: dict, rename: dict[str, str]) -> dict:
    """Rename dataset camera columns to match the model's expected feature names."""
    return {rename.get(k, k): v for k, v in row.items()}
```

### Link**图像转置**

π₀.5 和多数视觉模型一样，期望的排布是 (batch, channels, height, width)。原始数据集把图像存成 (`height, width, channels`) 的 uint8。一个批处理的 `.map_batches` 在 CPU 上做转置和类型转换：

```
def transpose_images(batch: dict, camera_keys: list[str]) -> dict:
    """Convert camera images from HWC uint8 to CHW float32."""
    import numpy as np

    result = dict(batch)
    for key in camera_keys:
        result[key] = np.transpose(np.stack(batch[key]), (0, 3, 1, 2)).astype(np.float32)
    return result
```

## Link**第 3 部分：用 Ray Train 做分布式训练**

接下来我们用 DistributedDataParallel（DDP）来分布式地训练，每张 GPU 持有模型的一份完整副本，处理数据的不同分片。每次反向传播之后，DDP 在各个 worker 之间同步梯度，让每份副本都保持一致。这是最简单的分布式策略，也很契合我们的情况——π₀.5 的可训练参数（我们冻结 backbone，只训练 action 和 time projection 这两个头）能轻松放进单张 GPU 的显存。

这段代码读起来就像单 GPU 训练。Ray Train 负责处理 DDP、数据分片、checkpoint 和故障恢复。

**训练循环**

```
import torch

def train_loop_per_worker(config: dict):
    """Per-GPU training entry point. Ray Train calls this on each worker."""

    device = torch.device("cuda")

    # Load pi0.5 and freeze backbone -- only action/time heads are trainable.
    # prepare_model() wraps it in DistributedDataParallel.
    policy = util.load_pi05_policy()
    policy = ray.train.torch.prepare_model(policy)

    optimizer = torch.optim.AdamW(
        [p for p in policy.parameters() if p.requires_grad],
        lr=config.get("lr", 1e-4),
    )
    scaler = torch.amp.GradScaler("cuda")

    # Resume from checkpoint if this is a failure recovery
    checkpoint = ray.train.get_checkpoint()
    if checkpoint:
        start_epoch, step = util.load_checkpoint(checkpoint, policy, optimizer, scaler)
    else:
        start_epoch, step = 0, 0

    # Build the LeRobot preprocessor with dataset normalization stats
    from lerobot.policies.factory import make_pre_post_processors
    preprocessor, _ = make_pre_post_processors(
        policy.module.config,
        pretrained_path="lerobot/pi05_base",
        dataset_stats=config["stats"],
    )

    num_workers = ray.train.get_context().get_world_size()
    scheduler = util.build_lr_scheduler(optimizer, config, num_workers, last_step=step)

    batch_size = int(config.get("batch_size", 1))
    grad_accum = int(config.get("grad_accum", 1))
    num_epochs = int(config.get("num_epochs", 1))
    max_len    = int(config.get("max_len", 512))

    # Get this worker's shard of the streaming dataset.
    # Ray Data partitions automatically -- no DistributedSampler needed.
    shard = ray.train.get_dataset_shard("train")

    for epoch in range(start_epoch, num_epochs):
        optimizer.zero_grad(set_to_none=True)
        epoch_loss_sum, epoch_loss_count = 0.0, 0

        # iter_torch_batches() streams preprocessed batches from CPU workers
        # directly into GPU memory. Backpressure ensures we never OOM.
        for batch in shard.iter_torch_batches(
            batch_size=batch_size,
            collate_fn=util.NumpyToTorchCollate(device),
        ):
            loss_val = util.train_step(policy, batch, preprocessor, max_len, grad_accum, scaler)
            step += 1
            epoch_loss_sum += loss_val
            epoch_loss_count += 1

            if step % grad_accum == 0:
                util.optimizer_step(policy, optimizer, scaler, scheduler)

        # End of epoch: report metrics and checkpoint.
        # ray.train.report() is a sync barrier -- every worker must call it.
        avg_loss = epoch_loss_sum / max(epoch_loss_count, 1)
        metrics = {
            "epoch": epoch, "steps": step,
            "loss": avg_loss, "lr": scheduler.get_last_lr()[0],
        }

        if ray.train.get_context().get_world_rank() == 0:
            checkpoint = util.make_checkpoint(policy, optimizer, scaler, epoch, step)
            ray.train.report(metrics, checkpoint=checkpoint)
        else:
            ray.train.report(metrics)
```

训练循环里与 Ray 相关的部分是：

- `ray.train.torch.prepare_model(policy)`
它把模型包装进 `DistributedDataParallel`。
- `ray.train.get_dataset_shard("train")`
它返回本 worker 在流式 Ray Dataset 上分到的那一片。Ray Data 会自动把数据在各个 worker 之间分区
- `shard.iter_torch_batches(...) `
它把预处理好的批次从 CPU worker 池直接流进 GPU 显存。背压保证管线永远不会把 GPU 显存压垮。
- `ray.train.get_checkpoint() / ray.train.report(...)`
出现失败时，Ray 会重启 worker，并把最近的 checkpoint 重新喂给循环开头处的 `get_checkpoint()`。`report()` 是所有 worker 之间的一个同步屏障；

因为我们用的是 DDP，每张 GPU 都持有模型的一份完整副本，所以只有 rank 0 需要创建并保存 checkpoint。所有 rank 都会调用 `report()`（它是一个屏障），但只有 rank 0 附上 checkpoint 载荷。

要从 1 张 GPU 扩展到 N 张：改 `ScalingConfig.num_workers`。

## Link**下一步**

如果你想自己动手试：

- [查看这个示例的完整代码](https://github.com/anyscale/examples/tree/main/vla_fine_tuning)。
- [在 Anyscale 上试用这个示例](https://console.anyscale.com/template-preview/vla-fine-tuning) - 在托管的 GPU 集群上跑完整条管线，零基础设施搭建。
- [Ray Train 文档](https://docs.ray.io/en/latest/train/train.html) 涵盖 `TorchTrainer` 的搭建、FSDP 配置以及 checkpoint 管理。
- `xvla-soft-fold` 数据集可在 [Hugging Face](https://huggingface.co/datasets/lerobot/xvla-soft-fold) 上获取。

## Link**相关资源**

- [Physical Intelligence：π₀.5——具备开放世界泛化能力的 VLA](https://www.physicalintelligence.company/blog/pi05)
- [NVIDIA Isaac GR00T N1.5 基础模型](https://developer.nvidia.com/isaac/gr00t)
- [分布式 AI 训练：用 Ray 与 Anyscale 做多 GPU](https://www.anyscale.com/blog/distributed-ai-training-multi-GPU-ray-anyscale)

#### 目录

- [引言](https://www.anyscale.com/blog/vision-language-action-pipelines-vla-robotics-ray-anyscale#introduction)
- [处理管线 ](https://www.anyscale.com/blog/vision-language-action-pipelines-vla-robotics-ray-anyscale#the-pipeline-)
- [第 1 部分：读取 LeRobot v3.0 数据格式 ](https://www.anyscale.com/blog/vision-language-action-pipelines-vla-robotics-ray-anyscale#part-1:-reading-from-the-lerobot-v3.0-data-format-)
- [实现 file-group 分区](https://www.anyscale.com/blog/vision-language-action-pipelines-vla-robotics-ray-anyscale#implementing-file-group-partitioning)
- [第 2 部分：用 Ray Data 做流式处理](https://www.anyscale.com/blog/vision-language-action-pipelines-vla-robotics-ray-anyscale#part-2:-streaming-with-ray-data)
- [Ray Data Datasource](https://www.anyscale.com/blog/vision-language-action-pipelines-vla-robotics-ray-anyscale#ray-data-datasource)
- [相机重命名](https://www.anyscale.com/blog/vision-language-action-pipelines-vla-robotics-ray-anyscale#camera-renaming)
- [图像转置](https://www.anyscale.com/blog/vision-language-action-pipelines-vla-robotics-ray-anyscale#image-transposition)
- [第 3 部分：用 Ray Train 做分布式训练](https://www.anyscale.com/blog/vision-language-action-pipelines-vla-robotics-ray-anyscale#part-3:-distributed-training-with-ray-train)
- [下一步](https://www.anyscale.com/blog/vision-language-action-pipelines-vla-robotics-ray-anyscale#what's-next)
- [相关资源](https://www.anyscale.com/blog/vision-language-action-pipelines-vla-robotics-ray-anyscale#related-resources)

#### 分享

#### 标签

#### 订阅产品更新

#### 推荐内容

#### 在 Ray Data 上对多模态 AI 工作负载做基准测试

阅读更多

#### 跨 CPU 与 GPU 的流式分布式执行

阅读更多

#### 可扩展的分布式训练：从单 GPU 的瓶颈到在 Anyscale 上用 Ray 跑通可靠的多节点训练

阅读更多

## 立即探索 Anyscale

在专为生产级 AI 打造的多云平台上，用 Ray 构建、运行并扩展任意 AI 工作负载。

免费开始

与专家交流
