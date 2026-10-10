---
vendor: huggingface
title: SAIR: Accelerating Pharma R&D with AI-Powered Structural Intelligence
original_title: SAIR: Accelerating Pharma R&D with AI-Powered Structural Intelligence
url: https://huggingface.co/blog/SandboxAQ/sair-data-accelerating-drug-discovery-with-ai
date: 2026-04-07
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: ebe03db80b96
---


# SAIR: Accelerating Pharma R&D with AI-Powered Structural Intelligence

Team

Article

					September 2, 2025


36

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6317233cc92fd6fee317e030/cJHSvvimr1kqgQfHOjO5n.png)](https://huggingface.co/tomaarsen)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/vno1Zeup3WGCGxUX9e3cT.png)](https://huggingface.co/negar-iravani)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1655882584229-noauth.jpeg)](https://huggingface.co/AnarSnowball)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1583857746553-5df7e9e5da6d0311fd3d53f9.jpeg)](https://huggingface.co/thomwolf)
- [![](https://huggingface.co/avatars/06ae1c6550f4407a057eb1bcfb6fd2cb.svg)](https://huggingface.co/kryczko)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/68a77a29646ad764c5cf2629/y_sSPjSh5BWX3Rx4lI85l.png)](https://huggingface.co/rudiplesch-sbx)

Arman Zaribafiyan

arman-zaribafiyan

SandboxAQ

Georgia Channing

cgeorgiaw

SandboxAQ

Rudi Plesch

rudiplesch-sbx

SandboxAQ

Zane Beckwith

zanebeckwithsaq

SandboxAQ

This summer, SandboxAQ released the **Structurally Augmented IC50 Repository (**[**SAIR**](https://huggingface.co/datasets/SandboxAQ/SAIR)**)**, **the largest dataset of co-folded 3D protein-ligand structures paired with experimentally measured IC₅₀ labels, directly linking molecular structure to drug potency** and overcoming a longstanding scarcity in training data. This dataset is now available on Hugging Face, and for the first time, researchers have open access to more than **5 million** AI‑generated, high‑accuracy protein-ligand 3D structures, each paired with validated empirical binding potency data.

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/680ff4388f704be391757780/KOXzLW72JLyU3rtMrb3yn.png)](https://cdn-uploads.huggingface.co/production/uploads/680ff4388f704be391757780/KOXzLW72JLyU3rtMrb3yn.png)

**SAIR is an open-sourced dataset** and is publicly available for free under a permissive CC BY 4.0 license, making it immediately actionable for commercial and non-commercial R&D pipelines. More than just a dataset, SAIR is a **strategic asset** that bridges the long-standing data gap in AI-powered drug design. It empowers pharmaceutical, biotech, and tech‑bio leaders to accelerate R&D, expand target horizons, and supercharge AI models – moving more of the costly, lengthy drug design and optimization from the wet lab to *in silico*. This means shorter hit‑to‑lead timelines, more efficient lead optimization, fewer dead‑end projects, and a more predictable path from initial idea to clinical candidate.

# Leapfrogging Past AI Achievements

AI and computer-aided design have great potential in dramatically accelerating the development of new drugs. For decades, scientists have dreamed about AI that could identify or design a potent, non-toxic, and efficacious compound from a prompt describing the disease pathway, practically compressing years of drug R&D into a few minutes on a computer. However, this vision is bottlenecked by AI's ability to predict critical drug properties like potency, toxicity, etc., based solely on its molecular structure.

Furthermore, traditional structure‑based discovery is often slowed early by the determination of reliable 3D structures. Three‑dimensional molecular structure dictates a molecule’s functionality, dynamics and interactions, which is especially important when a potential drug candidate is expected to bind to a human protein target.

Experimental methods, such as X-ray crystallography and cryo-EM, require extensive time and investment, and many promising disease targets still lack experimentally validated structural information. Computer simulations have helped lower the barrier of getting 3D structures and predicting binding affinity. However, earlier generations of algorithms for protein folding and docking (like AlphaFold and Vina respectively) only predict static snapshots of molecules and proteins (which, in reality, are inherently dynamic and shape-changing).

SAIR solves that constraint by compiling over **1 million unique computationally co-folded protein–ligand pairs**, ultimately yielding **5.24 million** distinct 3D complexes (five different co-folded structures per pair). Each structure is paired with a curated IC₅₀ measurement from [ChEMBL](https://www.ebi.ac.uk/chembl/) or [BindingDB](https://www.bindingdb.org/rwd/bind/index.jsp), providing for the first time a scalable link between high-quality 3D structures and drug potency, and bridging the historic data gap that has hindered AI-driven discovery. Deep-learned affinity models such as Boltz-2, trained on similar data, [have been shown](https://www.rxrx.ai/boltz-2) to yield up to a 1,000x speed-up over the traditional, first-principle approach.

# Optimized for the cutting-edge of computing

Creating SAIR was a major feat of high-performance AI computing. It took more than 130,000 GPU hours to compute the SAIR dataset using Boltz1, a cofolding AI model, on a cluster of 760 NVIDIA H100 processors, leveraging the NVIDIA DGX Cloud through Google Cloud Platform.

Capturing highly granular node, operator, scheduler, and GPU metrics, as well as a close collaboration on both infrastructure and workload optimization, helped NVIDIA AI Accelerator and SandboxAQ engineering teams identify bottlenecks and optimize configurations to achieve the highest workload throughput.

Consequently, the two teams were able to achieve > 95% GPU compute utilization for generating the SAIR dataset. This enabled us to create SAIR in three weeks – as opposed to the original estimate of three months (more than a 4X speed up) – and resulted in a highly optimized, GPU-native computational workflow that seamlessly integrates with today’s cutting-edge enterprise compute environments.

# Unprecedented scale, accuracy and power

Generating such a massive volume of data is only half the story. Equally important is confidence in its quality, which is why every predicted complex underwent rigorous validation with [**PoseBusters**](https://pubs.rsc.org/en/content/articlelanding/2024/sc/d3sc04185a), an industry-standard, open-source tool for benchmarking structure-related AI in drug discovery. This tool checks chemical sanity and physical plausibility.

**The end result was that 97 percent** of SAIR’s structures passed all checks. In addition to PoseBusters validation, we benchmarked leading affinity prediction methods, such as empirical scoring functions, 3D CNNs, and graph neural networks, across SAIR’s synthetic structures and experimental IC₅₀ values. The detailed results of these studies are available in our [scientific manuscript on bioRxiv](https://www.biorxiv.org/content/10.1101/2025.06.17.660168v1).

SAIR data is a reliable foundation for benchmarking new models as well as downstream modelling, screening, and design.

# Bringing “dark” targets into the light

A persistent challenge in drug discovery is the “dark proteome,” or disease‑relevant proteins for which experimental structures simply do not exist. SAIR illuminates these uncharted regions by providing credible, AI‑predicted complexes wherever experimental data is scarce. For example, more than 40 percent of the proteins in the SAIR dataset have no available structures in the Protein Data Bank (PDB) whatsoever, with or without a ligand. SAIR addresses one of the biggest challenges with existing AI models, low generalizability due to data scarcity. With SAIR, scientists can now explore targets that were previously deemed undruggable, armed with structural hypotheses to guide virtual screening and lead optimization using trustworthy model predictions.

Moreover, SAIR’s cross‑target breadth uncovers polypharmacology patterns and elucidates how a single molecule might interact with multiple proteins. Leveraging this rich tapestry of interactions, you can train AI models to predict off‑target effects or identify new repurposing opportunities, equipping your organization with a deeper understanding of compound profiles before any lab work begins.

## Accessing SAIR

SAIR is freely available on [Hugging Face](https://huggingface.co/datasets/SandboxAQ/SAIR). Here’s a quick guide to pull SAIR from Hugging Face, peek at the main table, and (optionally) download a few structure archives.

### 1. Install essentials

We use the Hub to fetch files and pandas+pyarrow to read the Parquet.

```
pip install huggingface_hub pandas pyarrow
```

### 2. Authenticate

Authenticate to Hugging Face:

```
import huggingface_hub
huggingface_hub.login(token="your_auth_token")
```

### 3. Load the main table (`sair.parquet`)

This grabs the file from the Hub and loads it into a DataFrame.

```
from huggingface_hub import hf_hub_download
import pandas as pd

parquet_path = hf_hub_download(
    repo_id="SandboxAQ/SAIR",
    filename="sair.parquet",
    repo_type="dataset"
)

df = pd.read_parquet(parquet_path)
df.head()
```

### 4. (Optional) List available structure archives

Structure files are shipped as many `.tar.gz` archives under `structures_compressed/`. List them and pick what you need.

```
from huggingface_hub import list_repo_files

files = [f.split("/")[-1] for f in list_repo_files("SandboxAQ/SAIR", repo_type="dataset")
         if f.startswith("structures_compressed/") and f.endswith(".tar.gz")]
files[:5]
```

### 5. (Optional) Download and extract structures

Each archive can be large (≈10 GB). Download only the ones you need and extract them locally.

```
import os, tarfile
from huggingface_hub import hf_hub_download

dest = "sair_structures"
os.makedirs(dest, exist_ok=True)

to_get = [
    "sair_structures_1006049_to_1016517.tar.gz",
    "sair_structures_100623_to_111511.tar.gz",
]

for name in to_get:
    tar_path = hf_hub_download(
        repo_id="SandboxAQ/SAIR",
        filename=f"structures_compressed/{name}",
        repo_type="dataset",
        local_dir=dest,
        local_dir_use_symlinks=False,
    )
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(dest)
    os.remove(tar_path)  # free disk space
```

A full version of this script, including more robust logging and validation, is available in the [README](https://huggingface.co/datasets/SandboxAQ/SAIR/blob/main/README.md) file for your convenience. For more details, visit [the SAIR homepage](https://www.sandboxaq.com/sair), read our [manuscript on bioRxiv](https://www.biorxiv.org/content/10.1101/2025.06.17.660168v1), or watch our 25-minute [joint webinar with NVIDIA](https://www.youtube.com/watch?v=y96t8vu9nfg), where we demonstrate SAIR and explain how data is structured within it. Extensive documentation, tutorials, and example benchmarks are available to facilitate its use and accelerate internal adoption.

The future of drug discovery is data-driven, AI-accelerated, and grounded in scalable, high-quality structural insights. While we don’t yet have AI that can design effective drug therapies with just a prompt, SAIR brings researchers ever closer to that goal with new data and insights that can potentially shave years from even AI-accelerated R&D pipelines.

We can’t wait to see what researchers will build using SAIR, and SandboxAQ experts are here to support them throughout the discovery process.

### Questions?

Contact the authors or post on the SAIR dataset discussion page.

Authors: [Arman Zaribafiyan](mailto:arman.zaribafiyan@sandboxquantum.com), [Georgia Channing](mailto:georgia@huggingface.co), [Zane Beckwith](mailto:zane.beckwith@sandboxquantum.com), and [Rudi Plesch](mailto:rudi.plesch@sandboxquantum.com)

## Datasets mentioned in this article 1

### Community

AnthonyTCano

Sep 6, 2025

Hi, I am having a really hard time finding AI datasets - publicly available to used. I need your help, any recommendation or direction where to find AI related datasets relating to global AI topic, using country by country.

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2FSandboxAQ%2Fsair-data-accelerating-drug-discovery-with-ai) or [log in](https://huggingface.co/login?next=%2Fblog%2FSandboxAQ%2Fsair-data-accelerating-drug-discovery-with-ai) to comment


36

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6317233cc92fd6fee317e030/cJHSvvimr1kqgQfHOjO5n.png)](https://huggingface.co/tomaarsen)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/vno1Zeup3WGCGxUX9e3cT.png)](https://huggingface.co/negar-iravani)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1655882584229-noauth.jpeg)](https://huggingface.co/AnarSnowball)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1583857746553-5df7e9e5da6d0311fd3d53f9.jpeg)](https://huggingface.co/thomwolf)
- [![](https://huggingface.co/avatars/06ae1c6550f4407a057eb1bcfb6fd2cb.svg)](https://huggingface.co/kryczko)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/68a77a29646ad764c5cf2629/y_sSPjSh5BWX3Rx4lI85l.png)](https://huggingface.co/rudiplesch-sbx)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/6rK4zLboxtGU8LF-Ny0td.png)](https://huggingface.co/arman-zaribafiyan)
- [![](https://huggingface.co/avatars/4469db9022f663a0f0d776335d878bda.svg)](https://huggingface.co/bruecknera)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/aEbBWDD2z-DUHivQ2zRLs.png)](https://huggingface.co/zanebeckwithsaq)
- [![](https://huggingface.co/avatars/d1a387921648fdb469b4779e46699cfb.svg)](https://huggingface.co/jk2297)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/gkVJdLM6poTWQpvyCtBeY.png)](https://huggingface.co/sleichen)
- [![](https://huggingface.co/avatars/82648fe4cd6336e5f5c33fe759098163.svg)](https://huggingface.co/yafyaf)

## Datasets mentioned in this article 1
