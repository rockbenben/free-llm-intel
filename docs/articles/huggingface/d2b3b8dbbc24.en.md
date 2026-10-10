---
vendor: huggingface
title: Migrating the Hub from Git LFS to Xet
original_title: Migrating the Hub from Git LFS to Xet
url: https://huggingface.co/blog/migrating-the-hub-to-xet
date: 2025-07-15
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 00c176347b0e
---


# Migrating the Hub from Git LFS to Xet

					July 15, 2025

Update on GitHub


29

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63eaa5f65c837d9968eea66c/dcubvuQ9s-zYaIeZ-Ih7V.jpeg)](https://huggingface.co/thompsonmj)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/673bcb3551d8d86ed0d0c484/RC7ytBAEN_C0q6AgF97xP.jpeg)](https://huggingface.co/xiarenqincai)
- [![](https://huggingface.co/avatars/70dbaf4b2a2b682c8b26aedf82b498e2.svg)](https://huggingface.co/seto)
- [![](https://huggingface.co/avatars/f0ee1d50bc5ddb15f60b6e9f78f11688.svg)](https://huggingface.co/blanching7)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63691c3eda9b693c2730b2a2/hBtKpgo3_9003MWCGkw5d.png)](https://huggingface.co/BrigitteTousi)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/5dd96eb166059660ed1ee413/NQtzmrDdbG0H8qkZvRyGk.jpeg)](https://huggingface.co/julien-c)

Jared Sulzdorf

jsulz

xet-team

Joseph Godlewski

jgodlewski

xet-team

Sam Horradarn

sirahd

xet-team

In January of this year, Hugging Face's [Xet Team](https://huggingface.co/xet-team) deployed a new storage backend, and shortly after shifted [~6% of Hub downloads through the infrastructure](https://huggingface.co/blog/xet-on-the-hub). This represented a significant milestone, but it was just the beginning. In 6 months, 500,000 repositories holding 20 PB joined the move to Xet as the Hub outgrows Git LFS and transitions to a storage system that scales with the workloads of AI builders.

Today, more than 1 million people on the Hub are using Xet. In May, it became the [default on the Hub for new users and organizations](https://huggingface.co/changelog/xet-default-for-new-users). With only a few dozen GitHub issues, forum threads, and Discord messages, this is perhaps the quietest migration of this magnitude.

How? For one, the team came prepared with years of experience building and supporting the content addressed store (CAS) and [Rust client](https://github.com/huggingface/xet-core) that provide the system's foundation. Without these pieces, Git LFS may still be the future on the Hub. However, the unsung heroes of this migration are:

- An integral piece of infrastructure known internally as the Git LFS Bridge
- Background content migrations that run around the clock

Together, these components have allowed us to aggressively migrate PBs in the span of days without worrying about the impact to the Hub or the community. They're giving us the peace of mind to move even faster in the coming weeks and months ([skip to the end](https://huggingface.co/blog/migrating-the-hub-to-xet#xet-for-everyone) 👇 to see what's coming).

## Bridges and backward compatibility

In the early days of planning the migration to Xet, we made a few key design decisions:

- There would be no "hard cut-over" from Git LFS to Xet
- A Xet-enabled repository should be able to contain both Xet and LFS files
- Repository migrations from LFS to Xet don't require "locks"; that is, they can run in the background without disrupting downloads or uploads

Driven by our commitment to the community, these seemingly straightforward decisions had significant implications. Most importantly, we did not believe users and teams should have to immediately alter their workflow or download a new client to interact with Xet-enabled repositories.

If you have a Xet-aware client (e.g., `hf-xet`, the Xet integration with `huggingface_hub`), uploads and downloads pass through the entire Xet stack. The client either [breaks up files into chunks using content defined chunking](https://huggingface.co/blog/from-files-to-chunks) while uploading, or requests file reconstruction information when downloading. On upload, [chunks are passed to CAS and stored in S3](https://huggingface.co/blog/rearchitecting-uploads-and-downloads). During downloads, [CAS provides the chunk ranges the client needs to request from S3](https://huggingface.co/blog/rearchitecting-uploads-and-downloads#a-custom-protocol-for-uploads-and-downloads) to reconstruct the file locally.

For older versions of `huggingface_hub` or [huggingface.js](https://github.com/huggingface/huggingface.js), which do not support chunk-based file transfers, you can still download and upload to Xet repos, but these bytes take a different route. When a Xet-backed file is requested from the Hub along the `resolve` endpoint, the Git LFS Bridge constructs and returns a single [presigned URL](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ShareObjectPreSignedURL.html), mimicking the LFS protocol. The Bridge then does the work of reconstructing the file from the content held in S3 and returns it to the requester.

Greatly simplified view of the Git LFS Bridge - in reality this path includes a few more API calls and components like the CDN fronting the Bridge, DynamoDB for file metadata, and S3 itself.

To see this in action, right click on the image above and open it in a new tab. The URL redirects from `https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/migrating-the-hub-to-xet/bridge.png` to one that begins with `https://cas-bridge.xethub.hf.co/xet-bridge-us/...`. You can also use `curl -vL` on the same URL to see the redirects in your terminal.

Meanwhile, when a non-Xet-aware client uploads a file, it is sent first to LFS storage then migrated to Xet. This “background migration process,” only [briefly mentioned in our docs](https://huggingface.co/docs/hub/en/storage-backends#backward-compatibility-with-lfs), powers both the migrations to Xet and upload backward compatibility. It is behind the migration of well over a dozen PBs of models and datasets and is keeping 500,000 repos in sync with Xet storage all without missing a beat.

Every time a file needs to be migrated from LFS to Xet, a webhook is triggered, pushing the event to a distributed queue where it is processed by an orchestrator. The orchestrator:

- Enables Xet on the repo if the event calls for it
- Fetches a listing of LFS revisions for every LFS file in the repo
- Batches the files into jobs based on size or number of files; either 1000 files or 500MB, whichever comes first
- Places the jobs on another queue for migration worker pods

These migration workers then pick up the jobs and each pod:

- Downloads the LFS files listed in the batch
- Uploads the LFS files to the Xet content addressed store using [xet-core](https://github.com/huggingface/xet-core)

Migration flow triggered by a webhook event; starting at the orchestrator for brevity.

## Scaling migrations

In April, we tested this system's limits by reaching out to [bartowski](https://huggingface.co/bartowski) and asking if they wanted to test out Xet. With nearly 500 TB across 2,000 repos, bartowski's migration uncovered a few weak links:

- Temporary [shard files for global dedupe](https://huggingface.co/blog/from-chunks-to-blocks#scaling-deduplication-with-aggregation) were first written to `/tmp` and then moved into the shard cache. On our worker pods, however, `/tmp` and the [Xet cache](https://huggingface.co/docs/huggingface_hub/guides/manage-cache#chunk-based-caching-xet) sat on different mount points. The move failed and the shard files were never removed. Eventually the disk filled, triggering a wave of **`No space left on device`** errors.
- After supporting the [launch of Llama 4](https://huggingface.co/blog/llama4-release), we'd scaled CAS for bursty downloads, but the migration workers flipped the script as hundreds of multi-gigabyte uploads pushed CAS beyond its resources
- On paper, the migration workers were capable of significantly more throughput than what was reported; profiling the pods revealed network and [EBS](https://aws.amazon.com/ebs/) I/O bottlenecks

Fixing this three-headed monster meant touching every layer - patching xet-core, resizing CAS, and beefing up the worker node specs. Fortunately, [bartowski](https://huggingface.co/bartowski) was game to work with us while every repo made its way to Xet. These same lessons powered the moves of the biggest storage users on the Hub like [RichardErkhov](https://huggingface.co/RichardErkhov) (1.7PB and 25,000 repos) and [mradermacher](https://huggingface.co/mradermacher) (6.1PB and 42,000 repos 🤯).

CAS throughput, meanwhile, has grown by an order of magnitude between the first and latest large-scale migrations:

- **Bartowski migration:** CAS sustained ~35 Gb/s, with ~5 Gb/s coming from regular Hub traffic.
- **mradermacher and RichardErkhov migrations:** CAS peaked around ~300 Gb/s, while still serving ~40 Gb/s of everyday load.

CAS throughput; each spike corresponds to a significant migration with the baseline throughput steadily increasing to just shy of 100 Gb/s as of July 2025

## Zero friction, faster transfers

When we began replacing LFS, we had two goals in mind:

- Do no harm
- Drive the most impact as fast as possible

Designing with our initial constraints and these goals allowed us to:

- Introduce and harden `hf-xet` before including it in `huggingface_hub` as a required dependency
- Support the community uploading to and downloading from Xet-enabled repos through whatever means they use today while our infrastructure handles the rest
- Learn invaluable lessons - from scale to how our client operated on distributed file systems - from incrementally migrating the Hub to Xet

Instead of waiting for all upload paths to become Xet-aware, forcing a hard cut-over, or pushing the community to adopt a specific workflow, we could begin migrating the Hub to Xet immediately with minimal user impact. In short, let teams keep their workflows and organically transition to Xet with infrastructure supporting the long-term goal of a unified storage system.

## Xet for everyone

In January and February, we onboarded power users to provide feedback and pressure-test the infrastructure. To get community feedback, we launched [a waitlist](https://huggingface.co/join/xet) to preview Xet-enabled repositories. Soon after, Xet became the default for new users on the Hub.

We now support some of the largest creators on the Hub ([Meta Llama](https://huggingface.co/meta-llama), [Google](https://huggingface.co/google), [OpenAI](https://huggingface.co/openai), and [Qwen](https://huggingface.co/Qwen)) while the community keeps working uninterrupted.

What's next?

Starting this month, we're bringing Xet to everyone. Watch for an email providing access to Xet and once you have it, update to the latest `huggingface_hub` (`pip install -U huggingface_hub`) to unlock faster transfers right away. This will also mean:

- All of your existing repositories will migrate from LFS to Xet
- All newly created repos will be Xet-enabled by default

If you upload or download from the Hub using your browser or use Git, that's fine. Chunk-based support for both is coming soon. In the meantime use whichever workflow you already have; no restrictions.

Next up: open-sourcing the Xet protocol and the entire infrastructure stack. The future of storing and moving bytes that scale to AI workloads is on the Hub, and we're aiming to bring it to everyone.

If you have any questions, drop us a line in the comments 👇, [**open a discussion**](https://huggingface.co/spaces/xet-team/README/discussions/new) on the [**Xet team**](https://huggingface.co/xet-team) page.

More Articles from our Blog

storage

infrastructure

content addressed store

## Xet is on the Hub

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/66abc1489654032803752328/TgdSHoXKcyy0uKzld7oyw.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/qTU99LNGTcXKOg9Zm7Wj9.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/64c3b82bfafa16b514253fd8/bivgVJJMERqvS4CfdhDmO.jpeg)
- ![](https://huggingface.co/avatars/71a80bbe13552af2785130c0a46d57e5.svg)
- +2

80

March 18, 2025

dedupe

storage

content addressed store

## Rearchitecting Hugging Face Uploads and Downloads

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65e77dcc714ce98ddd82568e/KhIkyM1Hc00t3zAqIaDoH.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65d50e9ef9cbfa798c590004/FlVe8chafigMfrPpMeJRL.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/66b05ca6e7c57eac7cafbbc4/nddUkS3xu78cxCS-r7-xB.jpeg)

51

November 26, 2024

### Community

pszemraj

Jul 15, 2025

Perhaps a dumb question: Xet is supposed to not only drive some speed ups but also provide a significant storage advantage in that only the diffs of a given object need to be uploaded/stored right?

I ask as my account migrated to xet, but I don’t see any reduction in the amount of storage quota anything created *after* migration. For example, as far as I’ve seen, if I create a dataset repo that is 1 GB, change a handful of rows and re-push, the storage usage is going to say 2+ GB. Am I missing something?

jsulz

Article author

Jul 15, 2025

Not a dumb question at all. The Hub reports storage based on the logical size of each new object; what you're seeing is expected.

We do this to ensure:

- Predicability - repo storage is always the sum of the files and revisions; you don't have to reason about how the storage engine functions under the hood
- Fairness/consistency - deduplication is global; as such there's no transparent way to determine ownership of the content nor is there a fair way to re-assign ownership to shared content if someone deletes those bytes from their repository

For the use-case that you're describing, Xet still provides faster file transfers as there is less to push and pull, so changes finish faster and uses less bandwidth/compute.

This enables and strengthens our commitment to provide [free public storage to the open source community](https://huggingface.co/docs/hub/storage-limits#storage-limits). Of course, we're always evaluating ways to surface this transparently and support the community, so let me know if any of this is confusing.

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/60bccec062080d33f875cd0c/KvEhYxx9-Tff_Qb7PsjAL.png)](https://huggingface.co/pszemraj)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65d50e9ef9cbfa798c590004/FlVe8chafigMfrPpMeJRL.jpeg)](https://huggingface.co/jsulz)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/66476b165fdb7108202b051c/nVACb8uBoGQtb8mSgHIr2.webp)](https://huggingface.co/Koitenshin)


pszemraj

Jul 16, 2025

Gotcha, didn’t realize it was global deduplication, that makes sense (*btw - is the deduplication done after upload then, or xet somehow compares diffs vs 20+ PB of data prior to upload?*).

I’m not in the position where this impacts me at the moment (thankfully 🙏) and not my call but if the private storage is handled the same way it has some interesting.. implications. For example if people are paying for extra private storage, and their storage is being counted “full size” against limits whilst being deduplicated against the rest of the hub and therefore a fraction of that in reality, is that fair? Etc

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fmigrating-the-hub-to-xet) or [log in](https://huggingface.co/login?next=%2Fblog%2Fmigrating-the-hub-to-xet) to comment


29

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63eaa5f65c837d9968eea66c/dcubvuQ9s-zYaIeZ-Ih7V.jpeg)](https://huggingface.co/thompsonmj)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/673bcb3551d8d86ed0d0c484/RC7ytBAEN_C0q6AgF97xP.jpeg)](https://huggingface.co/xiarenqincai)
- [![](https://huggingface.co/avatars/70dbaf4b2a2b682c8b26aedf82b498e2.svg)](https://huggingface.co/seto)
- [![](https://huggingface.co/avatars/f0ee1d50bc5ddb15f60b6e9f78f11688.svg)](https://huggingface.co/blanching7)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63691c3eda9b693c2730b2a2/hBtKpgo3_9003MWCGkw5d.png)](https://huggingface.co/BrigitteTousi)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/5dd96eb166059660ed1ee413/NQtzmrDdbG0H8qkZvRyGk.jpeg)](https://huggingface.co/julien-c)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65d50e9ef9cbfa798c590004/FlVe8chafigMfrPpMeJRL.jpeg)](https://huggingface.co/jsulz)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594144055859-5ee3a7cd2a3eae3cbdad1305.jpeg)](https://huggingface.co/yjernite)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1655385361868-61b85ce86eb1f2c5e6233736.jpeg)](https://huggingface.co/reach-vb)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/643ac5d2e2b979ae6144d68c/Z7PCNopn4cQeAYnVJDoqG.png)](https://huggingface.co/nyuuzyou)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64beb7a2c733e8552ffd63b3/ZI_DOExd737quSFZLmx58.jpeg)](https://huggingface.co/sirahd)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/667c7853ed85453a28a05f19/H2gcBeOAorIsQj3vNinYB.jpeg)](https://huggingface.co/rajatarya)
