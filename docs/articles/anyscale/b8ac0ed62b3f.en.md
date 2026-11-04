---
vendor: anyscale
title: Massively Parallel Agentic Simulations with Ray
original_title: Massively Parallel Agentic Simulations with Ray
url: https://anyscale.com/blog/massively-parallel-agentic-simulations-with-ray
date: 2025-09-10
lang: en
captured: 2026-11-05
extractor: readability-v1
status: ok
body_sha: 3b9ee6c7b6d0
---

[Home](https://www.anyscale.com/)[Blog](https://www.anyscale.com/blog)Blog Detail

# Massively Parallel Agentic Simulations with Ray

By [Philipp Moritz](https://www.anyscale.com/blog?author=philipp-moritz), [Sumanth Hegde](https://www.anyscale.com/blog?author=sumanth-hegde), [Tyler Griggs](https://www.anyscale.com/blog?author=tyler-griggs) and [Eric Tang](https://www.anyscale.com/blog?author=eric-tang) | September 10, 2025

![Massively parallel agentic simulations with Ray image](https://images.ctfassets.net/xjan103pcp94/7JUCwEieiRvbaHqx1VYRIu/ca861e91b802a5ba8e2919144885bc8f/Screenshot_2025-09-10_at_10.42.26â__AM.png?w=1200)

While running a single agent on your laptop against a hosted model endpoint (like ChatGPT, Claude, Gemini, or one of the model providers of OSS models) is easy, running many thousands of agents in parallel on a cluster presents a major challenge. It is also an important requirement for a number of very useful LLM and agentic use cases, including:

- **Running evaluations: **Agentic evaluations are used in the inner loop of agentic application development. They are crucial to help build better LLMs, write better prompts for LLMs, or improve the agent loop itself.
- **Iterating on datasets: **Building agents hinges on datasets of problem statements and techniques for verifying solutions. Agentic simulations allow us to iterate on these datasets, filter and improve them and collect solution trajectories for supervised fine-tuning.
- **Running RL training:** Agentic simulations are an essential part of the RL training loop. They are used to collect trajectories and rewards that are used to update the policy with RL.

When you scale up from running a single agent on your laptop to running a large number of agents in parallel, you will likely run into the following challenges:

- **Isolating the agents:** Agents need to be isolated so they do not interfere with each other and the rest of the system and stay within reasonable resource limits. In addition, agents need to run in a well defined environment like a container.
- **Scaling model inference and tool usage:** If you run a large number of agents in parallel, the rate limits by model providers typically do not suffice so you need to figure out how to scale the inference. You might also use common tools like MCP servers that need to be scaled up with the agents as well.
- **Using custom models:** If you are building customized agents, it is likely that you will also train or fine-tune custom models which you need to deploy.

Most such setups involve a lot of boilerplate code and complex infrastructure.

Ray addresses these challenges directly by allowing you to run massive parallel agentic simulations with a simple, Pythonic API. It handles mixed CPU and GPU (or other accelerator) workloads, and supports stateful services like inference servers (e.g. vLLM or SGLang). This allows the inference to run on the same cluster as the simulations, which enables fast joint experimentation on models and agents and joint scaling to avoid rate limiting of models. Ray’s convenient Pythonic developer experience makes it easy to iterate on the experimental setup, and seamlessly scale to very large runs. In addition, Ray’s fault tolerance capabilities enable cost saving by using spot instances.

Here is what you will learn by reading the blog post:

- You will learn how to run many sandboxed environments with flexible isolation, so the sandboxes can be run in any environment (unprivileged, container in container) without having to set up a separate sandbox environment.
- You will learn how both inference and agent executions can be run on a single Ray cluster to enable fast iteration on both agent and LLM settings without encountering rate limits, as well as making it easy to scale up the number of parallel agents.
- You will see concrete examples for all three use cases described above (running evaluations, iterating on datasets, running RL training) as well as a number of tips on how they can be made more efficient and easier to iterate on.

We will demonstrate these key points in the context of software engineering. To that end, we also open source a new dataset consisting of 5500 test cases we scraped from the [cpython repository](https://github.com/python/cpython) and show how they can be evaluated in parallel. The techniques we demonstrate are general and also apply to other domains including general computer use, data engineering or scientific research.

## LinkIsolating Parallel Agentic Simulations

One central question when performing many parallel agentic simulations is how to isolate them from each other and from the system environment. There are different options:

- **Using containers with full file system isolation: **Docker is a standard that many software engineers are familiar with and containers are well suited to isolate workloads in non-adversarial settings. This makes docker a very popular way to run agents. There are also some downsides of using docker: Container images can be expensive to build, push, pull and store and rate limits can be annoying. In addition, running in unprivileged environments like a supercomputer or inside another container can be challenging. Some of these issues can be solved by using a different container runtime like podman or apptainer (we show how to do this below).
- **Using processes with cgroups and chroot: **A less heavyweight way to run agents is via processes that can be isolated with Linux cgroups and chroot. Under the hood this is also how containers are implemented, but using the primitives directly allows more control over how the isolation happens, e.g. most of the hosts filesystem and packages can be reused in this setting and therefore agents can be run without pulling and pushing container images but still using good isolation. While implementing this from scratch is very complex, there are convenient command line utilities like [bubblewrap](https://github.com/containers/bubblewrap) that make this easy (again we show how to do this below).
- **Using VMs or remote execution: **In some scenarios, an even heavier weight isolation mechanism is called for. You might want to run a linux application on a mac for example, or run an x86_64 application on ARM, in which case you need VMs. In rare circumstances, you need more isolation than containers or cgroups provide in which case VMs or micro VMs might be a good option. Or you might want to use a separate K8s cluster to execute the agents, or use a separate cloud provider. These options typically require more work on the infra level than some of the simpler isolation methods, like additional error handling and communication mechanisms.

Containers are the most common and most broadly applicable isolation mechanism and they integrate well with the ecosystem, so should be the first choice in many cases. Processes with additional mechanisms like bubblewrap are probably underexplored for isolation. They are extremely lightweight and very easy to iterate on, and can be combined with package managers like uv, native Linux distribution package managers or technologies like [NixOS](https://nixos.org/) or [Guix](https://guix.gnu.org/) to flexibly define the environment the agent operates in. To enable the use of the most well-suited isolation primitive for each situation, our setup should be flexible in its environment support.

## LinkAgent scaffolds for agentic simulations

Agent scaffolds implement the structure around an LLM which makes it effective to solve problems in a certain domain, in our case software engineering. The scaffold consists of:

- The prompt given to the LLM, often in the form of a template that contains placeholders like a github issue description or specific instructions on how to act in a given software repository,
- The tools the LLM has available for the solution, like shell commands, file editing tools, a python interpreter, search tools to gather more information about the problem and the solution and any other arbitrary tools that might be available in the form of an MCP server,
- The agent loop which repeatedly queries the LLM and executes the action of the LLM. It may also interactively check with the user and allow them to modify the course of action the LLM is proposing.

While we focus on software engineering in this blog, this scheme is very generic and also applies to arbitrary computer use or more specialized domains like data science workloads or scientific research.

Some scaffolds support various forms of sandboxing for the actions of the LLM. Some scaffolds are designed for end users to solve specific problems and some are optimized for running large scale experiments (e.g. for evaluations or for RL training). While these use cases call for different solutions, ideally they share the same prompts and tool calls so any experiments done on experimentation datasets will directly represent the user experience. Here is a list of agentic scaffolds for software engineering we are aware of:

- Scaffolds typically used by end users, often in an interactive fashion, include [Claude Code](https://github.com/anthropics/claude-code), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [Qwen Code](https://github.com/QwenLM/qwen-code) and [Aider](https://github.com/Aider-AI/aider). They support one session at a time and typically don’t provide sandboxing, but they can be run inside of a container together with the actual workload environment. Some of them can also be adapted to be used as part of an evaluation or RL setup.
- [OpenHands](https://github.com/All-Hands-AI/OpenHands) is a popular full-featured agent runtime that is designed to be used by end users as well as for evaluations and RL setups (it comes with an evaluation harness). OpenHands is primarily docker based and a remote k8s based runtime is [available](https://novasky-ai.notion.site/skyrl-v0). It has very generic support for different tools like MCP servers, browsers and custom tools.
- [SWE-agent](https://github.com/SWE-agent/SWE-agent) is an agent by the authors of SWE-bench that can be used to solve software engineering problems. There is also a minimal version of it, [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent), which is the most flexible in terms of isolation and the code is very simple and hackable, so it is very easy to adapt to a wide range of workloads. It performs well on software engineering tasks using only bash commands.
- [Terminal-bench](https://github.com/laude-institute/terminal-bench) is a benchmark for agents on terminal-use tasks which comes with an evaluation harness for adapting other benchmarks (including SWE-Bench) and a built-in agent scaffold called Terminus. All tasks are packaged as Docker images, and the harness launches a containerized environment per task.
- [R2E-Gym](https://github.com/R2E-Gym/R2E-Gym) provides a gym-like interface to the environments as well as an agent wrapper around it, but is more optimized towards simulations and RL workloads. It supports tools like file editor, bash and file search.
- [Smolagents](https://github.com/huggingface/smolagents?tab=readme-ov-file) is a huggingface library which also focuses on being minimalistic, but also has many more integrations, support for different tool calls, and support for executing in sandboxed environments via Docker or E2B.

In this blog post we adopted mini-swe-agent because it is extremely simple and hackable and also gives good performance on software engineering problems without extra complexity, but the same approaches demonstrated below are also applicable to other scaffolds.

## LinkThe cpython issues dataset

For this blog post we use a very simple dataset that was generated from the [cpython](https://github.com/python/cpython) repository. Similar datasets can be generated for many different repositories. The format is a simplified swebench format optimized for running the full test suite for verification. We scraped about 5500 issues from the repository, found the associated PRs and extracted the `base_commit`, which is the parent commit of the PR as well as merge_commit, which is the commit that contains the code of the PR. The dataset is available [here](https://huggingface.co/datasets/pcmoritz/cpython_dataset) and the code that was used to scrape the dataset is available [here](https://gist.github.com/pcmoritz/fa911ee735a5a8f5329ea7a7c8adc47d).

![Massively parallel agentic simulations with Ray Img 1](https://images.ctfassets.net/xjan103pcp94/1UmeTbGXQTiMaAhWXTyNPO/91d3b6aee67d7c308b1c5c255ed99a3c/Screenshot_2025-09-09_at_3.58.33â__PM.png)

Massively parallel agentic simulations with Ray Img 1

Given a patch generated by the LLM, it can be verified as follows:

- Check out the [cpython](https://github.com/python/cpython) repository at the `base_commit`
- Apply the patch generated by the LLM, except for changes in `Lib/test/*` (both to avoid conflicts in the next step, as well as avoid the LLM removing or “fixing” tests)
- Apply the changes from the original PR diff `base_commit..merge_commit` in `Lib/test/*` (these are the regression tests added by the PR)
- Now run the full test suite via `./configure && make test`. In practice to make this work reliably, we have to exclude a few tests that often fail. Fortunately cpython has an environment variable called `EXTRATESTOPTS` which allows passing extra arguments to the test suite. We use this mechanism to exclude failing tests via the `--ignore` flag.

In the next section, we will show how to parallelize the generation of the patches as well as the verification with Ray.

## LinkUsing mini-swe-agent

In the remainder of this blog post, we are going to use [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) as the AI agent since it is very minimal, easy to modify and supports different sandboxing environments to execute agent actions in. Due to its simplicity, it can also easily be studied and adapted to different problem domains outside of software engineering. One design decision that `mini-swe-agent` made that makes a lot of things easier is each action by the agent is a simple `bash` command and no [persistent shell session](https://mini-swe-agent.com/latest/faq/#why-no-shell-session) is needed. Also, `mini-swe-agents` supports a variety of different isolation [environments](https://github.com/SWE-agent/mini-swe-agent/tree/main/src/minisweagent/environments):

- Local execution which just executes each command in a `bash` command without special isolation. This is not recommended in a setting where commands are run without user interactions, but can be used for local interactive use where each command is checked by the user before it executes.
- Execution in a container environment, either via [docker](https://www.docker.com/), [podman](https://podman.io/) or [apptainer](https://apptainer.org/). If we want to use a container for isolation, we usually choose podman, because it does not need a daemon and can be configured to run in a wide range of environments (including inside of a container as well as unprivileged environments). Apptainer can be a good environment to run on supercomputers.
- Execution in a process isolated by [bubblewrap](https://github.com/containers/bubblewrap), which allows running in an isolated environment without the overhead from setting up and maintaining container images. It is supported via [this environment](https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/environments/extra/bubblewrap.py). We will for example use it below to run the cpython environment, and combined with a [startup command](https://github.com/SWE-agent/mini-swe-agent/pull/490) it can be used to set up more complex environments, like Python virtual environments with uv for software engineering agents working on Python codebases.

To run `mini-swe-agent` with podman, you can install podman via:

```
1sudo apt-get -y install podman
2
3# The following is required if you want to run podman inside of a container
4sudo cp /usr/share/containers/containers.conf /etc/containers/containers.conf && sudo sed -i 's/^#cgroup_manager = "systemd"/cgroup_manager = "cgroupfs"/' /etc/containers/containers.conf && sudo sed -i 's/^#events_logger = "journald"/events_logger = "file"/' /etc/containers/containers.conf
5sudo apt-get install containers-storage
6sudo cp /usr/share/containers/storage.conf /etc/containers/storage.conf
7sudo sed -i 's/^#ignore_chown_errors = "false"/ignore_chown_errors = "true"/' /etc/containers/storage.conf
8# Depending on your execution environment (e.g. if some privileges are missing or if you need access to e.g. GPUs), you might also want to add some of the options from https://github.com/containers/podman/issues/20453#issuecomment-1912725982
```

and then in a directory with [https://github.com/SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) checked out, you can run

```
1uv run --extra full mini-extra swebench --model openai/gpt-5-nano --subset verified --split test --workers 128 --output <output directory>
```

To run this particular benchmark successfully, you should set the following parameters in `swebench.yaml`: Under `environment`, add `executable: "podman"` as well as `timeout: 3600` and `pull_timeout: 1200`.

For these kinds of workloads that require pulling lots of container images, it is also recommended to use a machine with local NVMe disks. If you are running on AWS on Anyscale, these will automatically be [configured](https://docs.anyscale.com/configuration/compute/aws#nvme-configuration) as a RAID array for maximal performance.

## LinkRunning parallel SWE simulations with Ray

In this section we will show you how you can run many parallel simulations with Ray and [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent). We will focus on software engineering tasks in the style of SWE-bench on the `cpython` issues dataset introduced above, but the ideas are broadly applicable to many different simulation environments.

### LinkGenerating data from agents

In this section we present a simple yet effective code example for generating the rollout data from the agents. Using an actor called `Engine`, we spin up one `vllm` or `sglang` server per node in the cluster and run many parallel simulations against it using Ray tasks `generate_rollout`, one task per problem statement. Each task uses the `swebench-single` script from [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) to perform the rollouts. This setup keeps the inference setup simple because we can directly use the CLI of vllm and `sglang` to start the inference engine. Alternatively it would also be possible to run a centralized deployment of the llm engine e.g. using [Ray Serve LLM](https://docs.ray.io/en/latest/serve/llm/index.html) and expose the model to a global endpoint that all agents connect to, or use `sglang` with [sglang router](https://docs.sglang.ai/advanced_features/router.html).

```
1import requests
2import subprocess
3from pathlib import Path
4
5from datasets import load_dataset
6import ray
7
8ENGINE_ADDRESS = "http://127.0.0.1:8000"
9
10@ray.remote(num_gpus=8)
11class Engine:
12
13    def __init__(self, model: str):
14        self.model = model
15        self.engine_process = subprocess.Popen(
16            ["/usr/local/bin/uv", "run", "--with", "vllm",
17             "vllm", "serve", self.model,
18             "--tensor-parallel-size", "8",
19             "--max-model-len", "64000", "--enable-expert-parallel",
20             # You can add --data-parallel-size if you want to use
21             # data parallel replicas in addition to tensor and expert parallel
22             "--enable-auto-tool-choice", "--tool-call-parser", "qwen3_coder"],
23        )
24
25        # If you want to use sglang instead, use the following code:
26        # self.engine_process = subprocess.Popen(
27        #     ["/usr/local/bin/uv", "run", "--with", "sglang[all]",
28        #      "-m", "sglang.launch_server",
29        #      "--model-path", self.model, "--tp-size", "8",
30        #      "--enable-ep-moe", "--host", "0.0.0.0", "--port", "8000"],
31        # )
32
33    def wait_for_engine(self):
34        while True:
35            try:
36                result = requests.get(ENGINE_ADDRESS + "/health", timeout=10)
37            except requests.exceptions.ConnectionError:
38                continue
39            if result.status_code == 200:
40                return
41
42@ray.remote(num_cpus=1, scheduling_strategy="SPREAD")
43def generate_rollout(model: str, dataset_name: str, instance_id: str, target_dir: str):
44    model_path = "hosted_vllm/" + model
45    target_path = Path(target_dir) / instance_id/ f"{instance_id}.traj.json"
46    result = subprocess.run(
47        ["/usr/local/bin/uv", "run", "mini-extra", "swebench-single",
48         "--model", model_path, "--subset", dataset_name,
49         "--split", "train", "--instance", instance_id,
50         "--environment-class", "bubblewrap",
51         "--output", target_path,
52        ],
53        env={
54            "HOSTED_VLLM_API_BASE": ENGINE_ADDRESS + "/v1",
55            "LITELLM_MODEL_REGISTRY_PATH": "/mnt/shared_storage/pcmoritz/model_registry.json",
56        },
57        capture_output=True,
58    )
59    return result
60
61# For this example, we use 5 nodes with 8 GPUs each
62num_shards = 5
63model = "Qwen/Qwen3-235B-A22B-Instruct-2507-FP8"
64dataset_name = "pcmoritz/cpython_dataset"
65dataset = load_dataset(dataset_name, split="train")
66
67executors = [Engine.remote(model) for i in range(num_shards)]
68ray.get([executor.wait_for_engine.remote() for executor in executors])
69
70results = []
71for record in dataset:
72    result = generate_rollout.remote(
73        model,
74        dataset_name,
75        record["instance_id"],
76        "/mnt/shared_storage/pcmoritz/rollouts"
77    )
78    results.append(result)
79
80ray.get(results)
```

For this experiment, we set the environment class to [bubblewrap](https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/environments/extra/bubblewrap.py). This will make sure all the agents running on the same machine are isolated from each other and from the system environment. We also write the results to a shared NFS volume, so we can do further postprocessing and filtering in the next step. In general, writing trajectory files and other output files (like logs) to NFS is a useful pattern and it also allows us to checkpoint partial runs and resume from where we left off if the generation script is re-executed.

There are a number of parameters that can be tuned in the above setting: One is the vLLM engine parameters, including the various forms of parallelism, see [the vLLM optimization guide](https://docs.vllm.ai/en/latest/configuration/optimization.html). The best settings will generally depend on your hardware as well as the model architecture you are using. Another parameter to tune is the number of agents per engine. It can be reduced by increasing the `num_cpus` argument in the decorator of `generate_rollout`. In practice we find that 64 to 128 agents per engine works well. The optimal number of agents per engine depends on the ratio of time spent in the environment (CPU work) and time spent to evaluate the LLM (GPU work). The higher this ratio is the more agents will be needed so there is a sufficiently large batch size to saturate the inference engine.

### LinkRunning filtering and post-processing on the data

In this section we will cover how Ray can be used to filter and post-process the dataset to assess the quality of the trajectories, e.g. by assigning a reward. Generally running one Ray task per problem instance works well. If a separate reward model is used, it can be deployed in a similar fashion as the agent LLM was deployed. For more complex settings, it might make sense to use [Ray Data](https://docs.ray.io/en/latest/data/data.html) and [Ray Data LLM](https://docs.ray.io/en/latest/data/working-with-llms.html) for the dataset preparation, since scoring and filtering are batch data processing workloads.

As an example we will implement the verification process described in section "the cpython issues dataset". The agent trajectories were generated in the previous step and written to NFS. In this step, for each problem instance, we extract the patch generated by the agent, and test it against the full cpython test suite, including the regression tests that were committed by a human in the “golden PR” fixing the issue (that the original agent didn’t see unless it cheated). If the patched code passes all tests, it gets a reward of 1, otherwise the reward is 0. Depending on the setup, it might make sense to run the verification as part of the rollout process or separately. In the last section of the blog post, we will show how to integrate both the rollout and verification process into an RL framework.

Here is the code for the verification process we just described:

```
1import json
2from pathlib import Path
3import re
4import subprocess
5import tempfile
6
7from datasets import load_dataset
8import ray
9
10TEST_CMD = """
11./configure && prlimit --as=34359738368 make test TESTOPTS="\
12    --ignore test.test_embed.InitConfigTests.test_init_setpythonhome \
13    --ignore test.test_os.TestScandir.test_attributes \
14    --ignore test.test_pathlib.test_pathlib.PathSubclassTest.test_is_mount \
15    --ignore test.test_pathlib.test_pathlib.PathSubclassTest.test_stat \
16    --ignore test.test_pathlib.test_pathlib.PathTest.test_is_mount \
17    --ignore test.test_pathlib.test_pathlib.PathTest.test_stat \
18    --ignore test.test_pathlib.test_pathlib.PosixPathTest.test_is_mount \
19    --ignore test.test_pathlib.test_pathlib.PosixPathTest.test_stat \
20    --ignore test.test_pathlib.PathSubclassTest.test_is_mount \
21    --ignore test.test_pathlib.PathSubclassTest.test_stat \
22    --ignore test.test_pathlib.PathTest.test_is_mount \
23    --ignore test.test_pathlib.PathTest.test_stat \
24    --ignore test.test_pathlib.PosixPathTest.test_is_mount \
25    --ignore test.test_pathlib.PosixPathTest.test_stat \
26    --ignore test.test_perf_profiler.* \
27    --ignore test.test_pdb.PdbTestInline.test_quit \
28    --ignore test.test_pdb.PdbTestInline.test_quit_after_interact"
29"""
30
31def safe_subprocess_run(path: Path, command: str | list[str], **kwargs):
32    """Run the command in a subprocess with error handling."""
33    try:
34        result = subprocess.run(
35            command,
36            text=True,
37            **kwargs
38        )
39    except Exception as e:
40        with open(path / "tests.exception", "w") as f:
41            f.write(str(e))
42        return None
43    if result.returncode != 0:
44        if result.stdout:
45            with open(path / "tests.out", "w") as f:
46                f.write(result.stdout)
47        if result.stderr:
48            with open(path / "tests.err", "w") as f:
49                f.write(result.stderr)
50        return None
51    return result
52
53def run_tests(path: Path, instance: dict[str, str], trajectory: dict):
54    with tempfile.TemporaryDirectory() as working_dir:
55        # check out the repository at the base_commit
56        if not safe_subprocess_run(
57            path,
58            f"git init && git remote add origin https://github.com/{instance['repo']} && "
59            f"git fetch --depth 1 origin {instance['merge_commit']} && "
60            f"git fetch --depth 1 origin {instance['base_commit']} && git checkout FETCH_HEAD && cd ..",
61            shell=True,
62            cwd=working_dir,
63            capture_output=True,
64        ):
65            return
66        # apply patch from the submission
67        if trajectory["info"]["submission"]
68            with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
69                f.write(trajectory["info"]["submission"])
70            print(f"wrote submission patch to {f.name}")
71            if not safe_subprocess_run(
72                path,
73                ["git", "apply", "--exclude", "Lib/test/*", f.name],
74                cwd=working_dir,
75                capture_output=True,
76            ):
77                return
78        # apply patches from the PR merge commit (tests only)
79        result = safe_subprocess_run(
80            path,
81            ["git", "diff", instance["base_commit"], instance["merge_commit"]],
82            cwd=working_dir,
83            capture_output=True,
84        )
85        if not result:
86            return
87        if result.stdout != "":
88            with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
89                f.write(result.stdout)
90            print(f"wrote test patch to {f.name}")
91            if not safe_subprocess_run(
92                path,
93                ["git", "apply", "--include", "Lib/test/*", f.name],
94                cwd=working_dir,
95                capture_output=True,
96            ):
97                return
98        # run full test suite
99        with open(path / "tests.log", "w") as f:
100            result = safe_subprocess_run(
101                path,
102                TEST_CMD,
103                shell=True,
104                cwd=working_dir,
105                stdout=f,
106                stderr=subprocess.STDOUT,
107            )
108            if not result:
109                return
110            return {"path": str(path), "exit_code": result.returncode}
111
112@ray.remote(num_cpus=1)
113def run_tests_safe(path: Path, instance: dict[str, str], trajectory: dict):
114    try:
115        # Note: We don't actually use the return values here, instead we
116        # parse the test run log file to determine if the tests passed or not
117        return run_tests(path, instance, trajectory)
118    except Exception:
119        return
120
121instances = load_dataset("pcmoritz/cpython_dataset", split="train")
122results = []
123
124for path in Path('/mnt/shared_storage/pcmoritz/rollouts').iterdir():
125    if path.is_dir():
126        json_file = path / f"{path.name}.traj.json"
127        if not json_file.exists():
128            continue
129        with open(json_file, 'r') as f:
130            trajectory = json.load(f)
131            instance = instances.filter(lambda x: x['instance_id'] == path.name)[0]
132            if trajectory["info"]["submission"] and re.search(r'Binary files .+ and .+ differ', trajectory["info"]["submission"]):
133                print(f"skipping instance {instance}")
134                continue
135            results.append(run_tests_safe.remote(path, instance, trajectory))
136
137ray.get(results)
```

Some tricks we found useful when running the simulations:

- Write logs and outputs of the simulation to a distributed file system like NFS so partial progress can be inspected and progress can be resumed if the whole job is preempted (similar to row level checkpointing in traditional data processing).
- Setting appropriate memory limits for the simulations so one rogue agent won’t bring down others. If a light weight process based isolation is used, this can be done by wrapping the process in `prlimit --as=<memory limit in bytes> <command>.`
- To avoid shared files or system files being modified by the agent, you can use a container image, or a command like bubblewrap like we did above for the agent simulations. In our case this was not necessary for the evaluation since multiple instances of the `cpython` test suite can run at the same time without interfering with each other.

To set up software engineering dependencies (e.g. in this example for compiling `python3`), you can use a container file with commands like:

```
1RUN sudo sed -i 's/# deb-src/deb-src/' /etc/apt/sources.list
2RUN sudo apt update
3RUN sudo apt build-dep -y python3
```

- We found it very useful to standardize the dataset in the form of a huggingface dataset for the initial problem statements, and then for each problem instance create a folder on NFS that additional outputs are written to as we move through different stages of the processing, in our case generating and scoring the rollouts.

Anyscale’s task dashboard gives you a convenient way to monitor the execution of your agents:

![Anyscale dashboard](https://images.ctfassets.net/xjan103pcp94/BLyVfRozKV2VlNrQrHJNo/9d5cdea359205b0fe2e048feb26cef05/Screenshot_2025-08-19_at_12.14.46â__PM.png)

Anyscale dashboard

Using the metrics page of the dashboard, you can also determine which resources are the bottleneck of the execution (e.g. disk throughput, network throughput, CPU or GPU memory capacity, CPU or GPU compute throughput) and select instances that are optimized best for your particular workload, or oversubscribe certain resources like CPUs.

We now present the results from our evaluation. We first evaluate the ceiling of the test pass rate by evaluating the full test suite of each `base_commit`. This yields the test passing rate without any patches suggested by an LLM. Note the ceiling can be improved by either excluding tests on a more granular basis or improving the testing environment. Then we run two models, Qwen3 Coder 30B and Qwen3 235B and record the pass rate by the patches generated by each model against the full test suite including the golden regression tests for each PR. We also record the pass rate if the model is given 3 attempts for each problem instance and only the most successful attempt is counted. The trajectories from these runs can be used in supervised fine-tuning to generate a better baseline for more runs and further fine-tuning.

For the following experiments, we used a temperature of 0.7 since it is more effective for qwen3 than the default of 0.0 that `mini-swe-agent` uses.

| **Model** | **Pass rate** | **Pass rate with 3 rollouts** |
| --- | --- | --- |
| Test pass rate ceiling | 64.3% | — |
| Qwen/Qwen3-235B-A22B-Instruct-2507-FP8 | 46.0% | 50.8% |
| Qwen/Qwen3-Coder-30B-A3B-Instruct | 36.1% | 49.9% |

As you can see, while the models are decently effective at solving these tasks, there is still opportunity for improvement.

We also present the system performance scaling numbers – we are using c7a.32xlarge nodes for the evaluation of the full cpython dataset. As you see the execution time scales linearly with the number of CPUs:

| **Number of nodes (number of CPUs)** | **Execution time** |
| --- | --- |
| 8 nodes (1024 CPUs) | 2h 31m |
| 4 nodes (512 CPUs) | 5h 9m |
| 2 nodes (256 CPUs) | 10h 21m |

### LinkRunning end-to-end RL with SkyRL

In this section we give an example on how this method can be integrated with existing RL libraries that run on Ray. There are [many options](https://www.anyscale.com/blog/open-source-rl-libraries-for-llms) for such RL libraries. We chose SkyRL to show the integration since it has great support for custom generators.

The Mini-SWE-Agent integration with SkyRL can be found [here](https://github.com/NovaSky-AI/SkyRL/pull/222). With SkyRL, the training stack is designed in a modular fashion, with two primary components: [the trainer and the generator](https://skyrl.readthedocs.io/en/latest/getting-started/overview.html). In this case, we customize the generator to use Mini-SWE-Agent to generate trajectories for the SWE-Bench task.

At a high-level, we implement a `MiniSweAgentGenerator` with a custom `generate` method to generate a batch of trajectories:

```
1class MiniSweAgentGenerator(SkyRLGymGenerator):
2	async def generate_trajectory(self, prompt, ...): 
3		...
4	async def generate(self, generator_input: GeneratorInput) -> GeneratorOutput:
5		...
6		prompts = generator_input["prompts"]
7		env_extras = generator_input["env_extras"]
8		tasks = []
9		for i in range(len(prompts)):
10	           tasks.append(
11	               self.generate_trajectory(
12	                  prompts[i],
13	                  env_extras[i],
14	               )
15	           )
16
17	       all_outputs = await asyncio.gather(*tasks)
```

In `generate_trajectory` we start a Ray task to generate a trajectory and evaluate it for the given instance. More concretely, this consists of the following:

- Generation:Initialize a sandbox / environment for the instanceGenerate a trajectory in this environment with Mini-SWE-Agent. For inference, we configure Mini-SWE-Agent to use the HTTP endpoint provided by SkyRL.Store the generated git patch after generation completes.
- Evaluation: Initialize a fresh environment for the given instance using the given backend.Apply the model's git patch to the working directory in the environment.Run the evaluation script for the instance. If the script runs successfully, the instance is considered to be resolved, and unresolved otherwise.

By running this workflow as a Ray task, we are also able to scale up generation across all the nodes in the Ray cluster.

At a high level, the code looks as follows:

```
1@ray.remote(num_cpus=0.01)
2def init_and_run(instance: dict, litellm_model_name: str, sweagent_config: dict, data_source):
3    model = get_model(litellm_model_name, sweagent_config.get("model", {}))
4    error = None
5    try:
6        env = get_sb_environment(sweagent_config, instance, data_source)
7        agent = DefaultAgent(model, env, **sweagent_config.get("agent", {}))
8        exit_status, model_patch = agent.run(instance["problem_statement"])
9        eval_result = evaluate_trajectory(instance, model_patch, sweagent_config, data_source)
10    except Exception as e:
11        error = str(e)
12    return agent.messages, eval_result, error
13
14class MiniSweAgentGenerator(SkyRLGymGenerator):
15    async def generate_trajectory(self, prompt, env_extras, ...):
16        messages, eval_result, error = init_and_run.remote(
17            env_extras["instance"], 
18            litellm_model_name, 
19            sweagent_config, 
20            data_source
21        )
22        ...
```

Note that the full implementation has some additional logic for configuration and error handling, and can be found [here](https://github.com/NovaSky-AI/SkyRL/pull/222).

For more information, please refer to [the documentation here](https://skyrl.readthedocs.io/en/latest/examples/mini_swe_agent.html).

## LinkConclusion

In this blog post we have shown how you can run agentic simulations on a large scale with Ray to generate trajectories from, evaluate and train agents. Ray’s flexibility allows us to run all the relevant workloads (data processing, model serving and training) in a single cluster, which simplifies the development and experimentation setup and allows us to scale up to a very large number of problem instances. Simple and efficient sandboxing makes it easy to run a wide variety of agentic workloads at scale.

All the examples shown in the blog post work out of the box in [Anyscale](https://www.anyscale.com/). Due to Ray’s distributed nature, it is also easy to deploy and evaluate agents that use multiple components like [MCP servers](https://console.anyscale.com/template-preview/mcp-ray-serve) to solve a given problem.

The techniques of this blog post can either be run standalone as separate steps of a pipeline, or they can be integrated as part of different [RL libraries](https://www.anyscale.com/blog/open-source-rl-libraries-for-llms). [SkyRL](https://github.com/NovaSky-AI/SkyRL) makes this easy due to its flexible generator framework and we provided an example for this in the blog post.

#### Table of contents

- [Isolating Parallel Agentic Simulations](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#isolating-parallel-agentic-simulations)
- [Agent scaffolds for agentic simulations](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#agent-scaffolds-for-agentic-simulations)
- [The cpython issues dataset](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#the-cpython-issues-dataset)
- [Using mini-swe-agent](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#using-mini-swe-agent)
- [Running parallel SWE simulations with Ray](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#running-parallel-swe-simulations-with-ray)
- [Generating data from agents](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#generating-data-from-agents)
- [Running filtering and post-processing on the data](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#running-filtering-and-post-processing-on-the-data)
- [Running end-to-end RL with SkyRL](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#running-end-to-end-rl-with-skyrl)
- [Conclusion](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#conclusion)

#### Sharing

#### Tags

#### Sign up for product updates

#### Recommended content

![Open Source RL Libraries for LLMs Graph](https://images.ctfassets.net/xjan103pcp94/3DTHR8PtMcYFYkFUnZVjTH/8aa576362b47aedbce2859583737dca6/image1.png?w=140)The architecture of a Reinforcement Learning (RL) library is split into two primary components: Generation and Training. During the generation phase, an LLM Engine performs multi-turn rollouts within an environment to produce data and reward signals. This output is then fed into the training phase to update the model's parameters. This process forms a feedback loop, where the progressively improved model generates the next iteration of data for continuous refinement.

#### Open Source RL Libraries for LLMs


![kuberay-production-best-practices-field](https://images.ctfassets.net/xjan103pcp94/3uRWLXRJv2sisfuH1UpkBg/7ffa981a092ba41c591b03ef933976bf/kuberay-production-best-practices-field.png?w=140)

#### KubeRay in production: best practices from the field


![Announcing Ray support for PyTorch on Google TPUs](https://images.ctfassets.net/xjan103pcp94/5odqs3bDXHHrUGye7EReO6/12a5fb11fc7d119b1ce905d420821160/ExternalRayTorchTPUblog.png?w=140)

#### Announcing Ray support for PyTorch on Google TPUs


## Explore Anyscale today

Build, run, and scale any AI workload on Ray with a multi-cloud platform built for production AI.

[Start for Free](https://authkit.anyscale.com/?utm_source=anyscale&utm_content=exploreblock&utm_medium=website&utm_campaign=cta)[Talk to an expert](https://www.anyscale.com/book/demo?utm_source=anyscale&utm_content=exploreblock&utm_medium=website&utm_campaign=cta)
