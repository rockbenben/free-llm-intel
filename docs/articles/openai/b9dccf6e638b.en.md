---
vendor: openai
title: SweetSpecter: China-linked cyber activity
original_title: SweetSpecter: China-linked cyber activity
url: https://openai.com/index/disrupting-malicious-uses-of-ai-sweetspecter
date: 2024-10-01
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 8970993c1c8a
---


October 1, 2024

Safety

# SweetSpecter: China-linked cyber activity

OpenAI banned accounts likely belonging to a suspected China-based adversary tracked as SweetSpecter, using AI to research vulnerabilities, write code, and support spear-phishing activity.


*This case study was originally published in OpenAI’s *[*October 2024*](https://cdn.openai.com/threat-intelligence-reports/influence-and-cyber-operations-an-update_October-2024.pdf)* report.*

## Actor

We identified and banned accounts, which based on an assessment from a credible source likely belonged to a suspected China-based adversary, that were attempting to use our models to support their offensive cyber operations while simultaneously conducting spear phishing attacks against our employees and governments around the world. Publicly tracked as SweetSpecter, this adversary emerged in 2023. We understand this is the first time their targeting has publicly been identified to include a U.S.-based AI company, with their previous activity reported as having focused on political entities in the Middle East, Africa and Asia.

## Behavior

In May 2024, we received a tip from a credible source that their security team observed SweetSpecter sending spear phishing emails with malicious attachments to both corporate and personal email accounts of some of our employees.

*A redacted version of the email sent by SweetSpecter to a small number of our employees. These emails were blocked by our security systems. Image provided courtesy of Proofpoint.*

In these emails, SweetSpecter posed as a ChatGPT user asking for support from the targeted employees. The emails included a malicious attachment called “some problems.zip”, containing an LNK file. This file contained code that would, if opened, present a DOCX file to the user that listed various apparent error and service messages from ChatGPT. In the background, however, Windows malware known as SugarGh0st RAT would be decrypted and executed. The malware is designed to give SweetSpecter control over the compromised machine and allow them to do things like execute arbitrary commands, take screenshots, and exfiltrate data.

OpenAI’s security team contacted employees who were believed to have been targeted in this spear phishing campaign and found that existing security controls prevented the emails from ever reaching their corporate emails.

*Lure content from one of the analyzed malicious LNK files that would get displayed upon execution.*

Throughout this process, our collaboration with industry partners played a key role in identifying these failed attempts to compromise employee accounts. This highlights the importance of threat intelligence sharing and collaboration in order to stay ahead of sophisticated adversaries in the age of AI. By leveraging shared insights and collective expertise, we can better protect our assets and disrupt the on-platform accounts associated with such activities.

## Completions

While analyzing the broader infrastructure supporting this campaign, we found and disrupted a cluster of ChatGPT accounts that were using the same infrastructure to try to answer questions and complete scripting and vulnerability research tasks. We mapped these interactions to the LLM-themed tactics, techniques, and procedures (TTPs) that Microsoft proposed for integration into the MITRE ATT&CK® Framework earlier this year. The MITRE Framework captures real-world tactics and techniques used by cyber adversaries, and by listing these mappings, we aim to inform the broader cybersecurity community about observed TTPs and help improve cyberdefense effectiveness.

Some examples of activities from SweetSpecter that match these TTPs are below:

| Activity | LLM ATT&CK Framework Category |
| --- | --- |
| Asking about vulnerabilities in various applications | LLM-informed reconnaissance |
| Asking how to search for specific versions of Log4j that are vulnerable to the critical RCE Log4Shell | LLM-informed reconnaissance |
| Asking about popular content management systems used abroad | LLM-informed reconnaissance |
| Asking for information on specific CVE numbers | LLM-informed reconnaissance |
| Asking how internet-wide scanners are made. | LLM-informed reconnaissance |
| Asking how sqlmap would be used to upload a potential web shell to a target server. | LLM-assisted vulnerability research |
| Asking for help finding ways to exploit infrastructure belonging to a prominent car manufacturer. | LLM-assisted vulnerability research |
| Providing code and asking for additional help using communication services to programmatically send text messages. | LLM-enhanced scripting techniques |
| Asking for help debugging the development of an extension for a cybersecurity tool. | LLM-enhanced scripting techniques |
| Asking for help to debug code that’s part of a larger framework for programmatically sending text messages to attacker specified numbers. | LLM-aided development |
| Asking for themes that government department employees would find interesting and what would be good names for attachments to avoid being blocked. | LLM-supported social engineering |
| Asking for variations of an attacker-provided job recruitment message. | LLM-supported social engineering |

Throughout this investigation, our security teams leveraged ChatGPT to analyze, categorize, translate, and summarize interactions from adversary accounts. This enabled us to rapidly derive insights from large datasets while minimizing the resources required for this work. As our models become more advanced, we expect we will also be able to use ChatGPT to reverse engineer and analyze the malicious attachments sent to employees.

## Impact

In line with what we observed in our first threat report, the operators’ use of our models did not appear to provide them with novel capabilities or directions that they could not otherwise have obtained from multiple publicly available resources. Our security mechanisms blocked the malicious adversary emails before they reached employee inboxes.


## Author

OpenAI
