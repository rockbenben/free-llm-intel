---
vendor: huggingface
title: Hugging Face and VirusTotal collaborate to strengthen AI security
original_title: Hugging Face and VirusTotal collaborate to strengthen AI security
url: https://huggingface.co/blog/virustotal
date: 2025-03-18
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 628d1acecb99
---

Back to Articles

# Hugging Face and VirusTotal collaborate to strengthen AI security

Published
					October 22, 2025

Update on GitHub

Upvote

56

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/TOPMN2FAGgOKrjES2ZK5-.png)](https://huggingface.co/AlphaQ32)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/68baeb7dbdf2bfb823aacffc/p0J0hLKVCkzJu0auOAz1r.png)](https://huggingface.co/tarekmasryo)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62175099ae3a893ac7ce86a7/ZSFoej_60rG-hT-gmo3Pr.jpeg)](https://huggingface.co/michellehbn)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)
- [![](https://huggingface.co/avatars/3b06e97e828533065b7014605be0b15e.svg)](https://huggingface.co/kalakuntla)
- [![](https://huggingface.co/avatars/369f9e3b4341394454c533d675c45dc5.svg)](https://huggingface.co/Wahaj-Ali)

Adrien Carreira

XciD

Bernardo Quintero

bquintero

VirusTotal

We’re excited to announce a new collaboration between Hugging Face and [VirusTotal](https://virustotal.com), the world’s leading threat-intelligence and malware analysis platform. This collaboration enhances the security of files shared across the Hugging Face Hub, helping protect the machine learning community from malicious or compromised assets.

TL;DR - Starting today, every one of the 2.2M+ public model and datasets repositories on the Hugging Face Hub is being continuously scanned with VirusTotal.

## Why this matters

AI models are powerful but they’re also complex digital artifacts that can include large binary files, serialized data, and dependencies that sometimes carry hidden risks. As of today HF Hub hosts 2.2 Million Public model artifacts. As we continue to grow into the world’s largest open platform for Machine Learning models and datasets, ensuring that shared assets remain safe is essential.

Threats can take many forms:

- Malicious payloads disguised as model files or archives
- Files that have been compromised before upload
- Binary assets linked to known malware campaigns
- Dependencies or serialized objects that execute unsafe code when loaded

By collaborating with VirusTotal, we’re adding an extra layer of protection and visibility by enabling files shared through Hugging Face to be checked against one of the largest and most trusted malware intelligence databases in the world.

## How the collaboration works

Whenever you visit a repository page or a file or directory page, the Hub will automatically retrieve VirusTotal information about the corresponding files. [Example](https://huggingface.co/Juronuim/xbraw2025/tree/main)

Here’s what happens:

- We compare the file hash against VirusTotal’s threat-intelligence database.
- If a file hash has been previously analyzed by VirusTotal, its status (clean or malicious) is retrieved.
- No raw file contents are shared with VirusTotal maintaining user privacy and compliance with Hugging Face’s data protection principles.
- Results include metadata such as detection counts, known-bad relationships, or associated threat-campaign intelligence where relevant.

This provides valuable context to users and organizations before they download or integrate files from the Hub.

## Benefits for the community

- Transparency: Users can see if files have been previously flagged or analyzed in VirusTotal’s ecosystem.
- Safety: Organizations can integrate VirusTotal checks into their CI/CD or deployment workflows to help prevent the spread of malicious assets.
- Efficiency: Leveraging existing VirusTotal intelligence reduces the need for repeated or redundant scanning.
- Trust: Together, we’re making the Hugging Face Hub a more secure, reliable place to collaborate on open-source AI.

## Join us

If you’d like to learn more about this integration or explore ways to contribute to a safer open-source AI ecosystem, reach out to [security@huggingface.co](mailto:security@huggingface.co).

Together, we can make AI collaboration not just open but secure by design.

## Models mentioned in this article 1

### Community

rollercoasterX

Oct 23, 2025

•

This comment has been hidden (marked as Resolved)

deleted

Nov 4, 2025

•

This comment has been hidden

A0bd

Dec 23, 2025

how i can get extension

Warrenschenck

Feb 7

What am I doing here?

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fvirustotal) or [log in](https://huggingface.co/login?next=%2Fblog%2Fvirustotal) to comment

Upvote

56

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/TOPMN2FAGgOKrjES2ZK5-.png)](https://huggingface.co/AlphaQ32)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/68baeb7dbdf2bfb823aacffc/p0J0hLKVCkzJu0auOAz1r.png)](https://huggingface.co/tarekmasryo)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62175099ae3a893ac7ce86a7/ZSFoej_60rG-hT-gmo3Pr.jpeg)](https://huggingface.co/michellehbn)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)
- [![](https://huggingface.co/avatars/3b06e97e828533065b7014605be0b15e.svg)](https://huggingface.co/kalakuntla)
- [![](https://huggingface.co/avatars/369f9e3b4341394454c533d675c45dc5.svg)](https://huggingface.co/Wahaj-Ali)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/2gGqkOIn7xLORcABWtGGT.png)](https://huggingface.co/tigerpiotta)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6304e2965d136debcecdc096/3cAUqpKnFd5WOcZtcQXxG.png)](https://huggingface.co/Pent)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/66abc1489654032803752328/TgdSHoXKcyy0uKzld7oyw.jpeg)](https://huggingface.co/assafvayner)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/B90ZaLSgjEdIb6le4k8VI.jpeg)](https://huggingface.co/andreascy)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/nqF3jkt8bmS-5BtFT1Txl.jpeg)](https://huggingface.co/TheDark08)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/647656d042e5f529745a5392/1AhYPCI5duq7hRZk3KyDC.png)](https://huggingface.co/caaza)

## Models mentioned in this article 1
