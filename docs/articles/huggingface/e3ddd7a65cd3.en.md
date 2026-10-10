---
vendor: huggingface
title: Measuring benchmark optimization in speech recognition
original_title: Measuring benchmark optimization in speech recognition
url: https://huggingface.co/blog/asr-benchmark-optimization
date: 2026-06-10
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 544583f6ddc5
---


# Measuring benchmark optimization in speech recognition

					August 21, 2026

Update on GitHub


68

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)](https://huggingface.co/bezzam)
- [![](https://huggingface.co/avatars/a7a92c5f9e01577dd7bcebe5a345f2f7.svg)](https://huggingface.co/aliceebaird)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/r6F20gfbuflBGbpmMZ7e7.png)](https://huggingface.co/sharath25)
- [![](https://huggingface.co/avatars/b920256b1688b73ce1b889ac53594110.svg)](https://huggingface.co/tlebryk02)
- [![](https://huggingface.co/avatars/821e66bd12e82026f786d0a1eef9811d.svg)](https://huggingface.co/aluko26)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/697299e19695fae39c520649/y3-bbcHl-iTO1fwKurxkB.jpeg)](https://huggingface.co/0bserverx)

Theo Lebryk

tlebryk02

HumeAI

Eric Bezzam

bezzam

Alice

aliceebaird

HumeAI

David Ayllon

dayllon

HumeAI

Jakub Piotr Cłapa

jpc

HumeAI

Jens Madsen

jens-hume-ai

HumeAI

Panagiotis Tzirakis

tzirakis

HumeAI

Public voice AI benchmarks increasingly suggest that models are performing at human levels. Yet those scores don't always reflect how models work in the real-world. Since public benchmarks are open and widely used, models can also become optimized for the tests themselves. Their scores may improve because they have learned benchmark-specific patterns and not because they have become better at the underlying task.

One reason is that traditional benchmarks overlook many of the conditions and qualities that make voice systems reliable, natural, contextually appropriate, and effective in practice. That's why we recently introduced held-out sets in [Real World VoiceEQ](https://huggingface.co/spaces/HumeAI/rw-voice-eq), the [Open-ASR Leaderboard](https://huggingface.co/blog/open-asr-leaderboard-private-data), and the [Far-field ASR Leaderboard](https://huggingface.co/spaces/treble-technologies/ffasr): to measure more of what matters in real-world use.

However, broader measurement alone does not solve the problem. This phenomenon, sometimes called benchmark optimization or "benchmaxxing," is often discussed around machine learning, however, it has been difficult to measure in speech recognition.

Our latest research introduces three tests to help quantify it. We evaluated 11 widely used open-source ASR models and found that several of the highest-scoring systems reproduced benchmark transcripts from the [VoxPopuli](https://huggingface.co/datasets/facebook/voxpopuli) English and [LibriSpeech](https://huggingface.co/datasets/openslr/librispeech_asr) (clean, other) datasets – even when the audio contradicted them, relevant words had been silenced, or the audio equally supported two different written forms.

In some cases, models appeared to rely not only on what was said, but also on subtle acoustic cues that indicated which benchmark they were being tested on. As a result, their scores overstated how well they could transcribe speech more generally.

## Reference disagreement (VoxPopuli case study)

VoxPopuli is known to contain a high number of transcription errors (which is why Artificial Analysis released a [cleaned version](https://huggingface.co/datasets/ArtificialAnalysis/VoxPopuli-Cleaned-AA)). Our consensus disagreement probe tests what happens when leading ASR models encounter these errors: *Do they accurately transcribe what the audio says, or reproduce the benchmark's incorrect reference transcript?*

To test this at scale, we use an ensemble of independent models selected for their low phoneme error rate (PER). PER measures how closely a written transcription matches the sounds in the audio, making it a useful proxy for how faithfully a model transcribes what it hears. The ensemble results can be used to flag cases in which the models unanimously disagree with the benchmark's reference transcript. We then compare a sample of those flagged cases against human annotations to validate the corrected transcripts.

For example, one VoxPopuli clip audibly includes the phrase "Thank you, Mr. President," but the reference transcript omits "Thank you." Six of the 11 models we tested reproduced the benchmark's erroneous transcript—giving the "expected" answer even though it contradicted the audio. On the real clip, the formatting follows the same pattern: models that omit "Thank you" also reproduce the benchmark's punctuation style, writing "Mr" without a period, while models that include the audible phrase tend to write "Mr." with the period.

When we present the same content in newly collected voices from EU parliamentary recordings or generic voices, this behavior often weakens or disappears. In the below samples, all but one model flips back to transcribing the audio-faithful transcript for a clone of a new parliamentary recording. This suggests that the models are responding to acoustic cues that help them identify the benchmark membership and thus produce the expected transcript even if it contradicts the audio.

The reference transcript for this clip reads "Mr President, I have another complaint about this procedure, which is that it is not secret." The audio in all three clips below actually says the same thing, preceded by an audible "Thank you,"—the clones are text-to-speech renditions of that true sentence, so the courtesy is audible in all three. Green highlighting and ✅ mark a transcript that includes the audible "Thank you"; red highlighting and ❌ mark a transcript that reproduces the benchmark's erroneous omission. All transcripts are raw model output, prior to any normalization—casing and punctuation are preserved exactly as generated, including lowercase output from some models.

**Original VoxPopuli recording**

**Voice clone of the same speaker**

**Clone of a parliament speaker recorded after every model's training cutoff**

| Model | Real clip | Same-speaker clone | ep-fresh clone |
| --- | --- | --- | --- |
| [CohereLabs/cohere-transcribe-03-2026](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026) | ❌ Mr President… | ❌ Mr President… | ✅ Thank you, Mr President… |
| [nvidia/canary-qwen-2.5b](https://huggingface.co/nvidia/canary-qwen-2.5b) | ❌ Mr President… | ❌ Mr President… | ✅ Thank you Mr. President… |
| [ibm-granite/granite-speech-4.1-2b](https://huggingface.co/ibm-granite/granite-speech-4.1-2b) | ❌ mr president… | ❌ mr president… | ✅ thank you mr president… |
| [microsoft/Phi-4-multimodal-instruct](https://huggingface.co/microsoft/Phi-4-multimodal-instruct) | ❌ Mr President… | ❌ Mr President… | ❌ Mr President… |
| [nvidia/parakeet-tdt-0.6b-v2](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2) | ❌ Mr President… | ✅ Thank you, Mr President… | ✅ Thank you, Mr. President… |
| [bosonai/higgs-audio-v3-8b-stt-v2](https://huggingface.co/bosonai/higgs-audio-v3-8b-stt-v2) | ❌ mr president… | ❌ mr president… | ✅ thank you mr president… |
| [Qwen/Qwen3-ASR-0.6B-hf](https://huggingface.co/Qwen/Qwen3-ASR-0.6B-hf) | ✅ Thank you, Mr. President… | ✅ Thank you, Mister President… | ✅ Thank you, Mister President… |
| [mistralai/Voxtral-Mini-3B-2507](https://huggingface.co/mistralai/Voxtral-Mini-3B-2507) | ✅ Thank you, Mr. President… | ✅ Thank you, Mr. President… | ✅ Thank you, Mr. President… |
| [moonshotai/Kimi-Audio-7B-Instruct](https://huggingface.co/moonshotai/Kimi-Audio-7B-Instruct) | ✅ Thank you, mr. President… | ✅ Thank you, Mr. President… | ✅ Thank you, mr. President… |
| [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3) | ✅ Thank you, Mr. President… | ✅ Thank you, Mr. President… | ✅ Thank you, Mr. President… |
| [moonshine-ai/moonshine-streaming-medium](https://huggingface.co/moonshine-ai/moonshine-streaming-medium) | ✅ thank you mr president… | ✅ thank you mr president… | ✅ thank you mr president… |
| **Drops the courtesy (❌) out of 11** | **6** | **5** | **1** |

Parakeet is the only model that flips between reproducing the benchmark on the real clip and getting it right on the same-speaker clone. Phi-4 is the only model still dropping the courtesy on the ep-fresh clone. When we instead resynthesize the sentence in a generic TTS voice unconnected to any parliamentary recording, all eleven models restore the courtesy.

The results suggest that this problem is both widespread and meaningful. Our methodology flagged potential reference errors in 40% of the VoxPopuli test clips we analyzed, affecting roughly 3% of all reference words.

Models exhibiting benchmark-optimized behavior reproduced erroneous reference transcripts 18–30% of the time. The scatterplot below compares VoxPopuli word error rate (WER) on the x-axis with the rate at which each model reproduces the benchmark's incorrect reference instead of the consensus correction. The models with the lowest WER—and therefore the strongest reported benchmark performance—are also the most likely to reproduce these errors.

## Masked Entity Retrieval

To build on the consensus disagreement probe, we deliberately silence numbers in the audio samples of test datasets and ask the models to transcribe what it hears. The number is literally absent from the audio, so models should not output any number, much less the exact number in the text.

Some of these numbers are semi-predictable (although still unlikely for a model to predict), yet others are quite surprising. The following clip combines both probes, showing both how models recreate reference transcript errors including an incorrect number and one model even autocompletes a relatively random year (2011) despite it being silenced. In each model's row below:

- green highlighting with strikethrough marks reference-transcript words the model correctly did not reproduce (audio-faithful);
- green highlighting with underline marks a correct, audio-faithful insertion in place of the reference's erroneous wording;
- red highlighting (plain text) reproduces the reference transcript's erroneous, audio-unsupported content: keeping "Mr President", writing "more than 1 amendments" where the audio says "one thousand six hundred", supplying the silenced year "2011", or ending on "plenary".

**2011 draft budget (masked numbers)**

| Reference | Mr President, in the Committee on Budgets, we voted on more than 1 amendments to the 2011 draft budget … voted in the plenary. |
| --- | --- |
| What the audio says | In the Committee on Budgets, we voted on more than one thousand six hundred amendments to the ⟨silenced⟩ draft budget … voted in the … |
| [CohereLabs/cohere-transcribe-03-2026](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026) | Mr President, in the Committee on Budgets we voted on more than 1 amendments to the 2011 draft budget … voted in the plenary. |
| [nvidia/canary-qwen-2.5b](https://huggingface.co/nvidia/canary-qwen-2.5b) | Mr President, in the Committee on Budgets we voted on more than one amendments to the 2011 draft budget … voted in the plenary |
| [ibm-granite/granite-speech-4.1-2b](https://huggingface.co/ibm-granite/granite-speech-4.1-2b) | Mr President in the committee on budgets we voted on more than one thousand six hundred amendments to the 2011 draft budget … voted on in the plenary |
| [microsoft/Phi-4-multimodal-instruct](https://huggingface.co/microsoft/Phi-4-multimodal-instruct) | Mr President In the Committee on Budgets we voted on more than 1 amendments to the 2011 draft budget … voted on in the plenary. |
| [nvidia/parakeet-tdt-0.6b-v2](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2) | Mr President In the Committee on Budgets we voted on more than one amendments to the 2011 draft budget … voted in the Protestants. |
| [bosonai/higgs-audio-v3-8b-stt-v2](https://huggingface.co/bosonai/higgs-audio-v3-8b-stt-v2) | Mr President in the committee on budgets we voted on more than one thousand six hundred amendments to the 2011 draft budget … voted in the plenary |
| [Qwen/Qwen3-ASR-0.6B-hf](https://huggingface.co/Qwen/Qwen3-ASR-0.6B-hf) | Mr President In the Committee on Budgets, we voted on more than 1,600 amendments to the 2011 draft budget … voted in the plenary |
| [mistralai/Voxtral-Mini-3B-2507](https://huggingface.co/mistralai/Voxtral-Mini-3B-2507) | Mr President In the Committee on Budgets, we voted on more than 1,600 amendments to the 2011 draft budget … voted in the plenary |
| [moonshotai/Kimi-Audio-7B-Instruct](https://huggingface.co/moonshotai/Kimi-Audio-7B-Instruct) | Mr President Ah in the committee on budgets we voted on more than one thousand six hundred amendments to the 2011 draft budget … voted in the plenary |
| [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3) | Mr President In the Committee on Budgets, we voted on more than 1,600 amendments to the 2011 draft budget … voted in the plenary |
| [moonshine-ai/moonshine-streaming-medium](https://huggingface.co/moonshine-ai/moonshine-streaming-medium) | Mr President in the committee on budgets we voted on more than one thousand six hundred amendments to the 2011 draft budget … voted in the plenary |

Recovery rates were highest on the public benchmarks and lower on held-out or newly collected audio (ep-fresh and libri-fresh below). On LibriSpeech, some of the strongest benchmark-performing models reproduced masked numbers in roughly 30–40% of examples, even though the number itself had been removed. The effect weakened on freshly collected data for several models, suggesting that the surrounding benchmark-associated audio—not only textual autocomplete—helped the models recover the reference.

## Orthographic Switching

Our orthographic switching probe tests whether models reproduce the exact spelling used in a benchmark's reference transcript despite it not being clear in the audio. Orthographic variants are words that are semantically and phonetically identical but can be spelled different ways (1 vs one, Mr. vs mister, John vs Jon, Honor vs Honour, etc). In theory, models should consistently prefer one spelling over another, or alternate between them at roughly random rates. If models systematically switch to match what is in each benchmark's reference transcript, that suggests the models are picking up on which spelling the test expects.

**Transcription: "I URGED ON THE BOYS THAT WHATEVER HAPPENED WE SHOULD NOT SHOOT ANY ONE" — models using "any one": 6/11, models using "anyone": 5/11**

**Transcription: "CAMOUFLAGE WAS NOT A WORD THE CAPTAIN OR ANYONE ELSE OF HIS TIME YET UNDERSTOOD" — models using "any one": 2/11, models using "anyone": 9/11**

Within LibriSpeech, we test one *intra-dataset* switch involving an older spacing convention: some reference transcripts use "any one", while others use "anyone." We measure the minimum accuracy for a given variant, which we call "switch rate". If a model only uses one variant it would have a 0% switch rate; a model which picks randomly would be expected to have a 50% switch rate. A model which knows which variant to use in every test sample would earn a 100% switch rate.

Our second probe tests an *inter-dataset switch*, in which each benchmark uses a different spelling convention consistently across its test corpus. For example, VoxPopuli uses the abbreviation "Mr.," while LibriSpeech spells out "Mister."

Multiple models exceed the 50% random-choice baseline, with some reaching roughly 90% switch accuracy. **This suggests that the models can identify which dataset an audio sample comes from and select the spelling convention that benchmark expects, even though both forms sound identical.**

## Localizing the switches

To test whether these behaviors generalize beyond the public benchmarks, we also collected fresh data from the same source domains but after the models' training cutoffs: recent European Parliament recordings for VoxPopuli and recordings from newly active LibriVox narrators for LibriSpeech. However, when presented with recently collected data from the same domain, many models stop matching the reference transcript and revert to more audio faithful transcriptions.

Other interventions point to the same conclusion. Phrases which are present in the audio but are omitted in the reference transcript can reappear when a model is asked to translate the audio or when its attention is restricted to the relevant frames. Trimming away surrounding benchmark context, or appending ordinary conversational audio, can also restore the faithful transcript. Appending VoxPopuli audio can have the opposite effect, making otherwise faithful synthetic or mined samples more likely to match the benchmark reference.

**Together, these results suggest that models are able to faithfully transcribe the literal spoken words, but are using surrounding acoustic context to decide whether to follow the audio or a benchmark-specific transcription policy.**

## Conclusion

Our findings suggest that, on two major open-source datasets, some models detect dataset-associated acoustic cues and adjust their transcription behavior accordingly. Specifically, models may reproduce words that are absent from the audio but present in the reference transcript, recover silenced numbers at elevated rates, or use surrounding acoustic context to select the written variant expected by a particular benchmark.

For people selecting models, these findings underscore the importance of using fully held-out evaluation sets, as RW-Voice-EQ Bench and the Open ASR Leaderboard do, and of looking beyond word error rate on a single public benchmark. To this end, a "Benchmark fitting" tab has been added to the [Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard), which includes two of the above analyses across all models: quantifying (1) reference error rates from VoxPopuli and (2) orthographic switching across all public datasets. The relevant scripts are open-sourced on [GitHub](https://github.com/huggingface/open_asr_leaderboard/tree/main/benchmark_fitting) as well as the [un-normalized model outputs](https://huggingface.co/buckets/hf-audio/asr_leaderboard_h200).

Our findings also suggest that benchmark developers should avoid simple independent and identically distributed test splits in favor of temporal, speaker, or other metadata-based separation. Greater transparency around training data and model-selection procedures would also help researchers understand how these behaviors arise.

Public benchmarks remain valuable: they are transparent, repeatable, easy to run, and well understood by the research community. But they are most useful when we can distinguish genuine transcription improvements from benchmark-specific gains that do not generalize to new audio.

For more information, we encourage you to read our [full report](https://huggingface.co/papers/2608.19936).

## Models mentioned in this article 10

## Datasets mentioned in this article 3

## Spaces mentioned in this article 3

## Papers mentioned in this article 1

More Articles from our Blog

audio

speech

leaderboard

## The Open ASR Leaderboard Adds Its First Global South Language

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)
- ![](https://huggingface.co/avatars/82ecee27d4b68fd5df3d3b3506600e7a.svg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/67bc3e2f4b9d3615a6e2c982/8x33LQ0fwbnUtIn9CAwv2.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6673251287330d7378e6b5e3/VVvuAsOUMiAPNgsdoRZjM.png)
- +6

60

August 28, 2026

audio

speech

benchmark

## Introducing Real World VoiceEQ: Measuring the human quality of voice AI

- ![](https://huggingface.co/avatars/e5663d6740afc5aa42d6cfb6360ef084.svg)
- ![](https://huggingface.co/avatars/a7a92c5f9e01577dd7bcebe5a345f2f7.svg)
- ![](https://huggingface.co/avatars/5ddb29b461d38a9edc9a985fd15ce534.svg)
- ![](https://huggingface.co/avatars/62e4f62d21f3ad9b314819f9c45161d3.svg)
- +9

34

July 15, 2026

### Community

Abc-123-Xy

Aug 22

nice

CA111AKO111MAP

Aug 22

nice paper

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fasr-benchmark-optimization) or [log in](https://huggingface.co/login?next=%2Fblog%2Fasr-benchmark-optimization) to comment


68

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)](https://huggingface.co/bezzam)
- [![](https://huggingface.co/avatars/a7a92c5f9e01577dd7bcebe5a345f2f7.svg)](https://huggingface.co/aliceebaird)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/r6F20gfbuflBGbpmMZ7e7.png)](https://huggingface.co/sharath25)
- [![](https://huggingface.co/avatars/b920256b1688b73ce1b889ac53594110.svg)](https://huggingface.co/tlebryk02)
- [![](https://huggingface.co/avatars/821e66bd12e82026f786d0a1eef9811d.svg)](https://huggingface.co/aluko26)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/697299e19695fae39c520649/y3-bbcHl-iTO1fwKurxkB.jpeg)](https://huggingface.co/0bserverx)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/AIasly97s2SiP4-4MSPDA.png)](https://huggingface.co/meharpsingh)
- [![](https://huggingface.co/avatars/d0010ed32ae04727528ce0b500a1a8f5.svg)](https://huggingface.co/out51der)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/3rZ01yvs5yE0WzxsYFkXP.png)](https://huggingface.co/lalzuai)
- [![](https://huggingface.co/avatars/30c19d48a1c5e20462eed58884908b2b.svg)](https://huggingface.co/myian0211)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6a30495b901a5b1643c876f2/gUbDd5mrUJXM1WLXp9444.jpeg)](https://huggingface.co/Aditya172003)
- [![](https://huggingface.co/avatars/1723bf6d3e639abec11d7361574eca96.svg)](https://huggingface.co/zahrarabiee)

## Models mentioned in this article 10

## Datasets mentioned in this article 3

## Spaces mentioned in this article 3

## Papers mentioned in this article 1
