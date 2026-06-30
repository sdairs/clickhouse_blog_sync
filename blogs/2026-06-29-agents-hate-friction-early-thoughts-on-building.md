---
title: "Agents hate friction: early thoughts on building for agents"
date: "2026-06-29T12:20:15.305Z"
author: "Al Brown"
category: "Engineering"
excerpt: "We've had decades to learn what it means to design software and hardware for humans. How do we build experiences where the primary user may now be an LLM?"
---

# Agents hate friction: early thoughts on building for agents

We've had decades to learn what it means to design software and hardware for humans. Did you know the first prototype of a mouse was made of wood, and had a single little red button in one corner? It was terrible. But since then (1964!), we've come a long, long way. The "mouse" on my desk as I write this is actually just a flat slab that I drag my fingers along. It looks nothing like the original, and it can do magical things that Douglas Engelbart hadn't even dreamt of. When it comes to designing for LLMs and agents, I have a feeling that we're still carving the wood.

![first_mouse_prototype.jpg](https://clickhouse.com/uploads/first_mouse_prototype_7be483331a.jpg)

The tools that have worked well with agents so far are the ones that had been designed for humans that prefer keyboards over mice, with established text-first interfaces (CLIs, SDKs, etc.). If you had a good CLI, a good SDK, that often meant you had a good human DX. Then LLMs came along and, as text-generators, they naturally did well with those tools.

Which led us to assume that you could pretty much just keep on DXing and the AX would take care of itself.

As I build more with, and for, agents, I realise how incorrect that assumption is. While human and agentic developers both enjoy text-based interfaces with discoverability, readable errors, sane defaults, and good docs, the way they use them is different. Different enough that building a beautiful DX for a human can translate into an AX that is merely functional. This is where most of us are today.

Which has led me to wondering what agent-first design looks like. How do we build experiences where the primary user may now be an LLM?

## Know you user

Knowing your user has always been tricky. Quite often, we build for ourselves, remembering pain we have experienced in the past. But memories fade, the job changes, and you become out of touch with what you once knew well.

Good builders stay close to their users to understand not just what bits and bobs they need, but the form in which they will be most useful. But trying to understand humans is *hard*. You can’t stand over the shoulder of your user for 8 hours a day, 7 days a week, and watch their every move. And you can’t extract every intermediary thought that played out in their heads that led them to do what they did (people struggle to explain *why* they did what they did themselves.)

But agents are different.

We *can* sit there watching them for as a long as we like, and no one thinks we’re weird. And we *can* log every trace of their internal reasoning to see how incremental thoughts build into their output.

While we can’t know the exact context any agent is given by its human, we can at least quantitatively and exhaustively test how agents use and reason about what we build. 

To do that, we have to recognise that the *agent is now the user*, and shift our thinking to understanding it.

> The technical detail of *how* we instrument, test and evaluate agent behaviour will be the subject of another post.

## Who are the agents?

Agents are a combination of several different things.

**Models.** I probably don’t have to explain what a model is. It’s the big mechanical-brain that is trained on the world’s knowledge. There’s a bunch of model providers (e.g., OpenAI, Anthropic, Mistral, Alibaba, DeepSeek, etc.), and each provider has a myriad of its own models (Anthropic: Haiku, Sonnet, Opus, Fable). Models vary in capability, strengths, weaknesses and guardrails across providers and within a provider's own model set.

**Harnesses.** Harnesses are the tools and frameworks through which users typically consume models. Think ChatGPT, Claude Desktop, Claude Code, Codex, OpenCode, etc. They provide extra “stuff” around the model itself that tailors it towards a job. That “stuff” might be: some kind of user interface, system prompts that tee the model up for a certain persona/behaviour, additional tools that the model can use for certain tasks, etc. Different harnesses are tailored towards different jobs - Claude Code is particularly good at coding (you might have guessed…) - but they’re generally not *limited* to one over another. Don’t underestimate how important the harness is. The behaviour of “ModelA” can vary *significantly* between a raw API call and a harness, or between two different harnesses.

**Context.** Context is information that the model is given outside of what it knows from its training. Model APIs and harnesses both inject their own context into every session. Every prompt, every web search, every tool invocation, these are all “context”. This is the primary way that model behaviour is affected during a session.

**Skills.** Agent Skills are essentially packages of context that a model can choose to use if it thinks it's relevant to the task. It is a very popular way to bundle up sets of knowledge within an agent.

There are probably a couple more things that could be included here, but from the POV of “knowing your user” I think this is the core you need to be familiar with.

Your user is a combination of these things. And the combination matrix is large, just like there is large variance in a human user base. You will never be able to speak to or understand 100% of your users, and you will never be able to test every combination of an agent’s DNA (unless you have endless $ to burn, then I suppose it is *possible*.)

In my area, developers and databases, I know that a large % of people have consolidated around a few choices: Claude Code or Codex as the harness, and Claude Opus or GPT5.5 as the model. These are where I focus a lot of my attention and resources to cover the largest segment of users. I’ll still test outside of this (smaller models like Sonnet, harnesses like Cursor or GitHub’s) but there’s a limit to how far down the tail you can reasonably go.

## And what do the agents want?

Agents might be our “user”, but they’re not human, and you might, reasonably, think that “merely functional” is good enough for a robot. If it gets the job done, who cares? They’re not going to crash out and refuse to use it just because it doesn’t work how they want it to…right?

But actually, I’ve seen agents do exactly that.

Our test setup gives agents a goal, and we give various “users” (a matrix of models & harnesses) varying levels of context to see how they reason towards achieving the goal. Some get very little, some get a bit of introduction, and some get extensive guidance.

One thing I have conclusively learned: **agents hate friction**.

And how they respond to friction is eerily human (no, I’m not one of these “LLMs are conscious” types.) When faced with friction, LLMs will try to reason around it. The more they struggle, the more it seems face will meet desk. But they have no face. Nor desk.

Eventually, they get “creative” and look for alternative paths forward. I’ve seen sessions where I ask an agent to do XYZ with our product (ClickHouse), and after 30 failed attempts, it says “Can’t be done, I’ll use this other database instead.”

It’s hilarious to see from a machine. It’s painfully familiar as a human. And it’s obviously a problem as someone building a product that agents should be able to use.

> This is a harsh new reality for those building for agents. LLMs are now how your product is discovered, how your product is used, and how your product is chosen (or discarded.) If you fail to adapt your product to solve friction, agents *will* discard it. And if you aren’t testing, you will never know that this is happening, and you will never solve it.

What’s particularly interesting is that, often, the task an LLM nopes out on is one that is trivially simple for a human. But *why*? Why can a task that is so easy for a human be one that drives LLMs bonkers?

I believe this brings us back to that original thought: “just keep on DXing and the AX would take care of itself.”

We have designed our products, interfaces, docs, and knowledge architectures, for humans. Not for agents. And the agents aren’t ~~alright~~ human.

## Ok, but *what* do they want?

I am still early in building out my understanding of how agents use software. The testing is incredibly interesting, and we’ve already shipped specific changes where we can proveably say “it makes it better for agents”.

But I don't have an A-Z checklist for “What is a good AX”. What I can share are the dimensions I'm measuring and thinking about, that inform how I design for agents:

**Steps to completion.** Given a goal, how many steps does the agent actually take to finish it? Including research, mistakes, errors, etc. I don’t believe that there is any sensible universal “target” for the amount of steps, it depends entirely on the complexity of the goal, but the fewer the better. What seems to trigger “frustration” in an agent is a lack of progress. Too many errors, too much looking things up, seems to bring an agent off course.

**Self-correction.** When the agent makes a mistake, does the tool give it enough context to recover? Many errors simply say “Nope, that didn’t work, try again”, and give very little idea of what you might do next. This is one of the lowest-hanging fruits that seem to make a material difference in keeping an agent on-track. *You* probably know that when ErrorA happens, 90% of the time, you should do X. Just giving that hint along with the error can make quite a big difference. An extension of that I’ve been testing is to have on-demand error-resolution skills for more complex problems, a living asset that is kept up to date with the latest information, pulled only when needed (hinted at by the error). I don’t have conclusive results on that one yet.

**Consistency.** Can the tool be designed so that, given the same goal, the agent consistently takes the same path? We know LLMs are non-deterministic and will give different responses to the same prompt. But to what extent can we narrow that difference between runs? In our testing, we plot variation between runs - the amount of tool calls, which tools it uses, etc. and measure consistency. And we do actually see evidence that we can affect it with different design choices.

**Context efficiency.** Claude might have a 1M context window now, but its intelligence drops noticeably even as you cross the 150k line. The faster we consume the window, the shorter the agent remains useful. We can’t give *no* context, but we can’t give *too much* context, either. The importance of this multiplies with more complex tasks that have more steps. There are interesting competing approaches; do you try to be super lean on context, but potentially require more steps? Or do you give generous context with the aim of having as few steps as possible? Is your tool generally playing a part of a larger workflow, or the core of a finitely scoped task?

**Token efficiency.** Every input and output is tokens, and tokens mean dollars. Verbosity in input/output increases tokens. So perhaps we should be concise to be cheap? But, taking more steps also costs tokens, so what if being more verbose would reduce the amount of steps? Agents tend not to introspect on their own cost (conspiracy anyone?!), but *cost* tends to be the most obvious and important metric to the humans behind the agent. If what made the agent happy, bankrupted the human, did we do a good job?

**The strength of familiarity.** Models are trained on what exists. They know `gh` and `kubectl` and `git` extremely well. What if we re-use design patterns from other tools to hook into a model's training, even if it isn’t trained on our tool specifically? It could make it easier for a model to guess its way to success. But just how similar can we be? And when, inevitably, we need to do something a bit different, do we suffer from a less tailor-made design?

I suspect that all of these, if they were ever correct, will be incorrect in some part in the near future. I have seen improvements that helped less capable models become entirely redundant, or even harmful, in newer, larger models.

Will models get smarter? Will models plateau in intelligence but become faster? Or cheaper? Perhaps we’ll actually be able to use that 1M context window some day.