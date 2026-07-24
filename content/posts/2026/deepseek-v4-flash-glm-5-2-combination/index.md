---
title: "The \"DeepSeek V4 Flash + GLM-5.2\" Combination Is Currently Enough for Me (and Will Probably Be Enough for You Too)"
description: "Why DeepSeek V4 Flash handles 70% of my workload and GLM-5.2 covers the rest — a practical AI stack for serious development work"
date: "2026-07-24"
publishDate: "2026-07-24"
draft: false
---

![(Antonio V. Franco)](cover.png)

When I turn on my computer in the morning, one of the first things I do is open whichever Ollama Cloud account I'm currently using and check my consumption. I have three Ollama Cloud accounts, each on the US$20 plan, which gives me considerably more peace of mind regarding usage, even though I still can't afford to consume resources recklessly.

Ollama Cloud's billing model isn't based solely on the number of tokens you use, but also on how demanding a model is in terms of GPU resources. In practice, this means I can get significantly more work done with GLM-5.2 (classified as "High" usage) than with DeepSeek V4 Pro (classified as "Extra High" usage).

As excellent as DeepSeek V4 Pro is, it ultimately doesn't fit my workflow (even with three Ollama Cloud accounts available). The interesting part is that I don't actually miss it. My current model stack consists of DeepSeek V4 Flash (an outstanding model) for roughly 70% of my work and GLM-5.2 for the remaining 30%.

Let me explain.

At Huyawo, DeepSeek V4 Flash is my primary working model. It's the model I use to read large repositories, investigate the current state of an implementation, and turn project specifications into concrete code changes. Most of my day-to-day development flows through it, from the initial implementation to the point where a change is tested, documented, and prepared for remote execution.

The word "Flash" in its name may suggest a lightweight model designed only for quick tasks. That couldn't be further from the truth. DeepSeek V4 Flash can process remarkably large contexts, recognize relationships between distant files, and maintain a sufficiently stable chain of reasoning for work that, not long ago, would have required a much more expensive model. I don't use it merely to save money. I use it because, most of the time, it gets the job done.

In a project like Huyawo, writing code is only part of the work. A seemingly minor modification can affect how an experiment is reproduced, how results are identified, or how a conclusion will later be supported. That means the model must understand the system as more than just the file it's currently editing. DeepSeek V4 Flash handles this continuity exceptionally well, especially when the work has been properly divided into stages and every stage has a clearly verifiable objective.

This decomposition matters because it minimizes implicit decisions. First, I determine exactly what needs to change. Then the implementation is carried out within that scope. Afterward, the experiment produces evidence that is committed back to the repository and compared against the expected behavior. The goal isn't to make software development unnecessarily bureaucratic, but to prevent a subjective impression that "it seems to work" from being mistaken for an implementation that is actually correct.

It's also the model I rely on to prepare and execute Huyawo's experiments. Since those experiments typically run on Kaggle, everything must reach the remote environment in a fully reproducible state, with clearly defined inputs and outputs that can later be audited. DeepSeek V4 Flash handles this preparation without turning every iteration into an expensive operation.

This matters because a serious benchmark doesn't end when the first promising number appears. The result must survive repetition, comparison against a baseline, and investigation into alternative hypotheses that could explain the outcome.

That kind of work represents the majority of my workload, and that's where roughly 70% of my usage goes.

GLM-5.2 enters the picture when the problem stops being merely large and becomes structurally difficult. I use it when understanding each component individually is no longer enough because the real issue lies in the interaction between them. It might be a refactoring that changes fundamental assumptions within the system, a state that becomes corrupted somewhere along a long execution chain, or a bug that continues to reappear despite multiple seemingly reasonable fixes.

In these situations, I'm not simply paying for a more elaborate answer. I'm paying for a model with greater capacity to sustain a complex investigation without simplifying the problem prematurely.

There are also situations where a change appears perfectly correct during a normal review, yet the cost of being wrong is simply too high. An implementation may execute successfully, generate all the expected artifacts, and even produce plausible metrics while silently violating an assumption that invalidates the entire experiment.

This is precisely where GLM-5.2 becomes particularly valuable. It isn't just looking for what is obviously broken; it's looking for what could quietly slip through unnoticed. Once DeepSeek V4 Flash has failed in a concrete and reproducible way, continuing to throw prompts at it stops being an economically rational decision and becomes a waste of your usage limits (I'd simply call it burning money).

The underlying principle, then, isn't to use the most powerful model for every task.

It's to use the most powerful model necessary for each stage of the work.

DeepSeek V4 Flash carries the volume and handles the normal pace of Huyawo's development. GLM-5.2 takes over when the architecture, the risk associated with a modification, or the persistence of a difficult bug demands a deeper level of reasoning.

For what I'm building at Huyawo, this combination isn't a compromise. It's a complete AI stack.

---

*Partnerships and projects:* contact@antoniovfranco.com
