---
title: "Bringing structure to LLM workflows with Boundary and ClickHouse"
date: "2025-05-14T14:18:20.213Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "“How do we move beyond prompting as guesswork, and start treating it like real programming, so we can build pipelines that are reliable not just in our code, but in our data too? That’s BAML. And it would only have been possible with ClickHouse.”  "
---

# Bringing structure to LLM workflows with Boundary and ClickHouse

Imagine if an API failed 5% of the time. Most engineers would drop everything they’re doing and fix it. Yet when LLMs fail at the same rate, we tend to shrug it off and call it acceptable.

“What the heck?” says [Boundary](https://www.boundaryml.com/) founder and CEO Vaibhav Gupta. “That should not be okay. We don’t build software that way. We cannot rely on software like that. That’s why AI applications feel like jokes a lot of the time—because we’ve built them with this expectation.”

Boundary is the team behind [BAML](https://github.com/BoundaryML/baml), a new expressive programming language that brings type safety and engineering discipline to LLM workflows. Instead of treating prompts like throwaway strings, BAML lets developers define them as functions with clear inputs and outputs, so they can reliably extract structured data from messy model output.

At a [March 2025 ClickHouse meetup in Seattle](https://www.youtube.com/watch?v=DV-zkQUvuPc), the Boundary team showed how they’ve extended that structure and reliability across the entire LLM workflow, using ClickHouse as the analytics backbone for everything from execution tracing to type-level monitoring.


## Web dev déjà vu

In the olden days, building for the web meant wrestling with strings. Templates were brittle, state management was a mess, and dynamic components were hard to pull off without breaking everything else. Even basic tasks, like keeping a counter in sync, required boilerplate and careful duct-taping. Eventually, React came along and added what Vaibhav calls “engineering rigor.” But for a long time, web development felt more like experimentation than engineering.


![boundary1.png](https://clickhouse.com/uploads/boundary1_5cdab09b1c.png)

Working with LLMs today feels eerily similar. In most LLM workflows, prompts are still just plain-text strings. Developers try to coax the right output through trial and error, with little visibility into why things do or don’t work. Change one part of a prompt, and “suddenly everything downstream breaks,” Vaibhav says. There’s no way to test, no way to type-check, and no way to guarantee consistency.

And when things go wrong, developers are left squinting at malformed JSON blobs or missing fields, unsure if the model is to blame or if something else broke. “Context management is really hard, and iteration is slow,” Vaibhav says. Every new model release resets the baseline. There are no components. No hot reload. No engineering rigor.

“What we really want is something that allows us to express ideas like English, but still maintain the structure of code,” Vaibhav says. “Because code is beautiful. HTML was English. React was code. And we want to bring that somehow to the world of agents.”


## Putting the engineering back into prompt engineering

Boundary’s answer to this chaos is BAML, a programming language purpose-built for working with LLMs. Instead of writing opaque strings and hoping for the best, developers can now define prompts as typed functions, with clear inputs, outputs, and schemas. Every behavior can be tested, versioned, and debugged, just like any other piece of code.

“You write a function, pick a model, define your expected output, and write test cases,” Vaibhav explains. “And as you change your prompt, or your inputs, or your types, you see the results update in real time. It’s like a hot reload loop for LLMs.”


![boundary2.png](https://clickhouse.com/uploads/boundary2_769e5d7e46.png)


BAML’s parser is built to handle messy model output. Yapping? Trailing commas? Missing quotes? Newlines in weird places? It can still coerce the output into a valid data structure, as long as the intent is there. That means developers can reliably extract structured data from weaker, faster, or cheaper models, and ship with confidence.

<iframe width="768" height="432" src="https://www.youtube.com/embed/SipWSQakBuM?si=5BvV0wHqwry2hCzh" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<br/><br/>
Because every function is defined in code, the same BAML prompts can be used across environments and languages—Python, TypeScript, Rust—all with autocomplete and type safety. Change a schema, and the types in your app update automatically. No more brittle prompt strings buried deep in production logic.

<iframe width="768" height="432" src="https://www.youtube.com/embed/Mp-e1fLZf2k?si=dGpVtNB-LluDUhxq" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<br/><br/>
“The whole point of BAML,” Vaibhav says, “is not just to help you build and test your pipelines, but to complete the loop without running a single line of code.” In other words, BAML turns prompt engineering into real engineering—structured, testable, and ready for production. 



![boundary3.png](https://clickhouse.com/uploads/boundary3_52e71a2726.png)



## Making LLMs observable with ClickHouse

Of course, writing better prompts is only part of the challenge. To reliably ship and maintain LLM applications, developers need visibility into what’s running in production: which prompts are active, how they’re performing, and what’s changed over time.

That’s where ClickHouse comes in. At the [Seattle meetup](https://www.youtube.com/watch?v=DV-zkQUvuPc), the Boundary team showed how every BAML function call, along with its inputs, outputs, types, and prompt version, is automatically logged and stored in ClickHouse. This creates a complete, queryable history of prompt behavior in production.

Want to see which outputs failed schema validation? Filter by type. Want to know when a prompt implementation changed but the function signature stayed the same? ClickHouse can show that, too. Because the system is schema-aware by design, developers can slice and analyze structured output at scale. “It allows us to write really, really fast queries,” Vaibhav says.

That visibility extends to the frontend. “We pipe all that data through ClickHouse and into the UI,” explains Boundary software engineer Chris Watts. “You can hover over a function and see the full input/output types, grouped by version. No other tool gives you that.”



![boundary4.png](https://clickhouse.com/uploads/boundary4_ca845fc80f.png)


And when a model gets something right in production, developers can promote that output into a test case, preserving it in version control and expanding their coverage with real examples. Because BAML understands the structure, the feedback loop stays fast, with developers able to update, test, and deploy prompts all in one environment.


## Real impact for AI engineers

That tight loop between development and production is already changing how teams work. With BAML and ClickHouse, developers don’t have to waste time worrying about stray quotation marks or malformed JSON. They don’t have to guess why a prompt failed. And they’re no longer stuck relying on heavyweight models just to get the formatting right.

“Every time we talk to a BAML user, they’re surprised by how much time and energy they’ve saved,” says Boundary software engineer Sam Lijin. “They stop worrying about the glue code and start focusing on the actual business problems they’re trying to solve.”

Boundary started with a bold idea: what if prompt engineering worked like real software development, with types, tests, and tools developers actually trust?

With BAML, they’ve built exactly that. And with ClickHouse, they’ve added the observability and performance needed to run it at scale. Now, developers can build LLM workflows with clear types, test coverage, and real-time observability, from first prompt to production deployment.

“How do we move beyond prompting as guesswork,” Vaibhav asks, “and start treating it like real programming, so we can build pipelines that are reliable not just in our code, but in our data too? That’s BAML. And it would only have been possible with ClickHouse.”

To see how ClickHouse can power your AI workflows and transform your data operations, [try ClickHouse Cloud free for 30 days](https://clickhouse.com/cloud).