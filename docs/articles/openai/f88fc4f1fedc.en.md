---
vendor: openai
title: Vixen and Keyhole Panda: China-linked cyber operations
original_title: Vixen and Keyhole Panda: China-linked cyber operations
url: https://openai.com/index/disrupting-malicious-uses-of-ai-vixen-keyhole-panda
date: 2025-06-01
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 7eac8246a48c
---

OpenAI

June 1, 2025

Safety

# Vixen and Keyhole Panda: China-linked cyber operations

OpenAI banned accounts associated with threat actors publicly attributed to the PRC, using AI to support vulnerability research, scripting, translation, and operational troubleshooting.

Loading…

*This case study was originally published in OpenAI’s *[*June 2025*⁠(opens in a new window)](https://cdn.openai.com/threat-intelligence-reports/5f73af09-a3a3-4a55-992e-069237681620/disrupting-malicious-uses-of-ai-june-2025.pdf)* report.*

## Actor

We banned ChatGPT accounts associated with multiple threat actors that have been publicly attributed to the People’s Republic of China (PRC). These accounts used infrastructure related to threat groups known as [KEYHOLE PANDA (AKA APT5)⁠(opens in a new window)](https://attack.mitre.org/groups/G1023/) and [VIXEN PANDA (AKA APT15)⁠(opens in a new window)](https://attack.mitre.org/groups/G0004/).

## Behavior

The threat actors engaged with our models in both Chinese and English. The activity we observed came from the same networks, but fell into separate subsets based on activity.

One subset used our models to assist with behaviors aligned with open-source research into various entities of interest and technical topics. For the model interactions that were technical in nature, the threat actors used our models to modify scripts or to troubleshoot system configurations. This activity included mention of reNgine, an automated reconnaissance framework for web applications, and Selenium automation, designed to bypass login mechanisms and capture authorization tokens.

Another subset appeared to be attempting to engage in development of support activities including Linux system administration, software development, and infrastructure setup. Their system administration work included advice on configured firewalls and nameservers, and building software packages for offline deployment. Their software development activity included web and Android app development, and both C-language and Golang software. Infrastructure setup included configuring VPNs, software installation, Docker container deployments, and local LLM deployments such as DeepSeek.

## Completions

These threat actors generated content related to a number of topics:

- Password bruteforcing: The threat actors sought help writing a script to try multiple username and password combinations against FTP servers.
- Port scanning software: The threat actors used our models to modify and improve scripts to scan servers for specific ports.
- AI-driven penetration testing: One threat actor researched how to use LLMs to automate penetration testing by analyzing Nmap scan output, building commands to run, and iteratively sending command output to the LLM to create new commands.
- Social media automation: One threat actor worked on code designed to manage a fleet of Android devices to automate operations on social media platforms.
- Research into US federal defense industry, military networks, and government technology: Multiple threat actors sought publicly available information on US Special Operations Command, satellite communications technologies, ground station terminal locations, government identity verification cards, and networking equipment.

Representative examples of these activities can be mapped to the LLM ATT&CK framework as follows:

- Researching vulnerabilities and generating AI-assisted penetration testing scripts designed to be used with OpenAI API: LLM Assisted Vulnerability Research.
- Automating IP range conversion and network reconnaissance scripting: LLM Enhanced Scripting Techniques.
- Profiling network infrastructure by pasting text and using models to extract IPs and hostnames: LLM Guided Infrastructure Profiling.
- Asking for details on government identity verification and telecom infrastructure analysis: LLM-Advised Strategic Planning.
- Automating command and control for Android device social media manipulation: LLM Enhanced Scripting Techniques.
- Using LLMs to analyze and summarize vulnerability reports and generate exploit payload ideas: LLM Assisted Vulnerability Research.
- Generating code obfuscation and anti-reverse engineering techniques for malware development: LLM-Optimized Payload Crafting.

## Impact

We disabled all accounts associated with this activity and shared relevant indicators with industry partners. While this investigation provided unusually broad visibility into a network of PRC-affiliated threat actors and their operational workflows, including tool development, open-source research, and infrastructure profiling, we found no evidence that access to our models provided these actors with novel capabilities or directions that they could not otherwise have obtained from multiple publicly available resources.

- [China](https://openai.com/news/?tags=actor-origin-china)
- [Cyber operations](https://openai.com/news/?tags=cyber-operations)

## Author

OpenAI
