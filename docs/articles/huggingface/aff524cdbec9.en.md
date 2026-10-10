---
vendor: huggingface
title: Introducing Storage Regions on the Hub
original_title: Introducing Storage Regions on the HF Hub
url: https://huggingface.co/blog/regions
date: 2023-11-03
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 9f7fa9d922a5
---


# Introducing Storage Regions on the Hub

					November 3, 2023

Update on GitHub


2

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6640bbd0220cfa8cbfdce080/wiAHUu5ewawyipNs0YFBR.png)](https://huggingface.co/John6666)
- [![](https://huggingface.co/avatars/900480ce5a29aac046e79fe76cb4f588.svg)](https://huggingface.co/nako-ruru)

Eliott Coyac

coyotte508

Remy

rtrm

Adrien Carreira

XciD

Michelle Habonneau

michellehbn

Violette

Violette

Julien Chaumond

julien-c

This article is also available in Chinese [简体中文](https://huggingface.co/blog/zh/regions).

As part of our [Enterprise Hub](https://huggingface.co/enterprise) plan, we recently released support for **Storage Regions**.

Regions let you decide where your org's models and datasets will be stored. This has two main benefits, which we'll briefly go over in this blog post:

- **Regulatory and legal compliance**, and more generally, better digital sovereignty
- **Performance** (improved download and upload speeds and latency)

Currently we support the following regions:

- US 🇺🇸
- EU 🇪🇺
- coming soon: Asia-Pacific 🌏

But first, let's see how to setup this feature in your organization's settings 🔥

## Org settings

If your organization is not an Enterprise Hub org yet, you will see the following screen:

[![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/no-feature.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/no-feature.png)

As soon as you subscribe, you will be able to see the Regions settings page:

[![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/feature-annotated.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/feature-annotated.png)

On that page you can see:

- an audit of where your orgs' repos are currently located
- dropdowns to select where your repos will be created

## Repository Tag

Any repo (model or dataset) stored in a non-default location will display its Region directly as a tag. That way your organization's members can see at a glance where repos are located.

[![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/tag-on-repo.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/tag-on-repo.png)

## Regulatory and legal compliance

In many regulated industries, you may have a requirement to store your data in a specific area.

For companies in the EU, that means you can use the Hub to build ML in a GDPR compliant way: with datasets, models and inference endpoints all stored within EU data centers.

If you are an Enterprise Hub customer and have further questions about this, please get in touch!

## Performance

Storing your models or your datasets closer to your team and infrastructure also means significantly improved performance, for both uploads and downloads.

This makes a big difference considering model weights and dataset files are usually very large.

[![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/upload-speed.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/storage-regions/upload-speed.png)

As an example, if you are located in Europe and store your repositories in the EU region, you can expect to see ~4-5x faster upload and download speeds vs. if they were stored in the US.

More Articles from our Blog

announcement

enterprise

hub

## XetHub is joining Hugging Face!

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/66ac094a8fc00b5c160d7da4/1-DnsQ0zlyTA-18bncHbt.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/5dd96eb166059660ed1ee413/NQtzmrDdbG0H8qkZvRyGk.jpeg)

119

August 8, 2024

announcement

enterprise

hub

## Build AI on premise with Dell Enterprise Hub

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1605114051380-noauth.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1624629516652-5ff5d596f244529b3ec0fb89.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/662add9816435ebd17d9138a/AHEBGUtxkp1bDGAS95Niq.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65d5fd89e775c38b6fc515e2/CaHLWJXJ6zcQuLkZeZ6ja.jpeg)

27

May 21, 2024

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fregions) or [log in](https://huggingface.co/login?next=%2Fblog%2Fregions) to comment


2

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6640bbd0220cfa8cbfdce080/wiAHUu5ewawyipNs0YFBR.png)](https://huggingface.co/John6666)
- [![](https://huggingface.co/avatars/900480ce5a29aac046e79fe76cb4f588.svg)](https://huggingface.co/nako-ruru)
