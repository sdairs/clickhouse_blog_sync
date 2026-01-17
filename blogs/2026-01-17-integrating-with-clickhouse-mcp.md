---
title: "Integrating with ClickHouse MCP"
date: "2025-06-05T13:05:23.296Z"
author: "Al Brown & Mark Needham"
category: "Engineering"
excerpt: "Using the ClickHouse MCP Server with a variety of AI libraries."
---

# Integrating with ClickHouse MCP

[MCP](https://www.anthropic.com/news/model-context-protocol) is a protocol for connecting third-party services - databases, APIs, tools, etc. - to LLMs. Creating an MCP server defines how a client can interact with your service. An MCP client (like Claude Desktop, ChatGPT, Cursor, Windsurf, and more) connects to the server, and allows an LLM to interact with your service. MCP is quickly becoming the de-facto protocol, and we published the ClickHouse MCP server earlier in the year: [mcp-clickhouse](https://github.com/ClickHouse/mcp-clickhouse).

<iframe width="768" height="432" src="https://www.youtube.com/embed/y9biAm_Fkqw?si=qDQlklXHrU3gYpCC" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<br />

Natural language interfaces are becoming popular across pretty much all domains, including the spaces where we find ClickHouse users. Software engineers, data engineers, analytics engineers, you name it. We're all starting to adopt natural language and agentic interfaces for parts of the job. It's making it easier than ever to work with data, whether you're comfortable with SQL or not. What we're seeing is that LLMs are helping to round out and expand people's skills - software engineers can do more with data, data engineers can do more with software, etc. There's never been a time when a wider audience could work with data.

Universally across these users, domains, and interfaces is the expectation of speed and interactivity in the user experience. Users aren't firing off a query on Friday afternoon, grabbing a delicious Bánh mì on the way home, and picking up a report on Monday morning. They're having a collaborative, interactive conversation with an LLM, where responses are delivered in seconds, and there is a real back-and-forth. If we add third-party services into the mix, we can't disrupt the user experience. If a user wants to query their database this way, it needs to handle this kind of responsiveness.

That's what makes ClickHouse the ideal database for agentic AI data workflows. ClickHouse is built to be the world's fastest analytical database, where no bits, bytes, or milliseconds are wasted. Even before the LLM and agentic era, ClickHouse aimed to support interactive analytics at scale. We didn't set out to be the best database for agentic AI - sometimes, happy accidents just happen.

:::global-blog-cta:::

## Future use cases

Popularity aside, it's still early days, and the tools, workflows, and use cases are evolving rapidly. We see a lot of people forgoing the traditional SQL interface and BI tooling, instead using chat interfaces like Claude Desktop or ChatGPT to talk to their data, skipping SQL entirely, and generating insights and visualizations. We also see developers without a traditional data background building user-facing applications that expose data to end users, relying on LLMs not just to generate front-ends, but to structure data and optimise queries for very high concurrency.

With ClickHouse also becoming [the best choice for observability 2.0](https://clickhouse.com/blog/clickstack-a-high-performance-oss-observability-stack-on-clickhouse), we're seeing SREs and DevOps teams using LLMs to query their traces, metrics, and logs, blending full-text search and analytics without obscure query syntax. 

And we're imagining what might come next: perhaps we'll see LLMs able to use existing observability data to inform their thinking, perhaps making recommendations for architecture, performance enhancements, or bug fixes based on the data they can access without requiring users to prompt with specific errors or traces.

> Soon, ClickHouse Cloud will offer a remote MCP server as a default interface. That means any MCP client could connect directly to your cloud instance without additional local setup.
>
> Want early access? [Sign up for the AI features waitlist at clickhouse.ai](http://clickhouse.ai).

## ClickHouse MCP Agent Examples

To make it dead simple to get started, we’ve put together some practical examples showing how to integrate various libraries with the ClickHouse MCP server. 

You can do this today with the open-source [mcp-clickhouse server](https://github.com/ClickHouse/mcp-clickhouse). For more on how this fits into the bigger picture, check out [this AgentHouse demo](https://clickhouse.com/blog/agenthouse-demo-clickhouse-llm-mcp) and our thoughts on [agent-facing analytics](https://clickhouse.com/blog/agent-facing-analytics).

You can find all five in the [ClickHouse/examples repo](https://github.com/ClickHouse/examples/tree/main/ai/mcp). They are all configured to run against the [ClickHouse SQL Playground](https://sql.clickhouse.com/), which is configured via the following config:

<pre><code type='click-ui' language='python'>
env = {
    "CLICKHOUSE_HOST": "sql-clickhouse.clickhouse.com",
    "CLICKHOUSE_PORT": "8443",
    "CLICKHOUSE_USER": "demo",
    "CLICKHOUSE_PASSWORD": "",
    "CLICKHOUSE_SECURE": "true"
} 
</code></pre>

We also use Anthropic models and have provided our API key via the `ANTHROPIC_API_KEY` environment variable.

### 1. Agno

Let’s start with [Agno](https://docs.agno.com/tools/mcp/mcp#multiple-mcp-servers) (previously PhiData), a lightweight, high-performance library for building Agents.

<pre><code type='click-ui' language='python'>
async with MCPTools(command="uv run --with mcp-clickhouse --python 3.13 mcp-clickhouse", env=env, timeout_seconds=60) as mcp_tools:
    agent = Agent(
        model=Claude(id="claude-3-5-sonnet-20240620"),
        markdown=True, 
        tools = [mcp_tools]
    )
    await agent.aprint_response("What's the most starred project in 2025?", stream=True)
</code></pre>

This one has a straightforward API. We initialize `MCPTools` with the command to launch our local MCP Server, and all the tools become available via the `mcp_tools` variable. We can then pass the tools into our agent before calling it on the last line.

<p> 
&#x1F4C4; <a href="https://clickhouse.com/docs/use-cases/AI/MCP/ai-agent-libraries/agno" target="_blank">View the full Agno example</a> <br />
&#x1F9EA; <a href="https://github.com/ClickHouse/examples/tree/main/ai/mcp/agno" target="_blank">Try the Agno notebook</a>
</p>

### 2. DSPy

[DSPy](https://dspy.ai/) is a framework from Stanford for programming language models.

<pre><code type='click-ui' language='python'>
server_parameters = StdioServerParameters(
    command="uv",
    args=[
        'run',
        '--with', 'mcp-clickhouse',
        '--python', '3.13',
        'mcp-clickhouse'
    ],
    env=env
)

dspy.configure(lm=dspy.LM("anthropic/claude-sonnet-4-20250514"))

class DataAnalyst(dspy.Signature):
    """You are a data analyst. You'll be asked questions and you need to try to answer them using the tools you have access to. """

    user_request: str = dspy.InputField()
    process_result: str = dspy.OutputField(
        desc=(
            "Answer to the query"
        )
    )

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()

        dspy_tools = []
        for tool in tools.tools:
            dspy_tools.append(dspy.Tool.from_mcp_tool(session, tool))

        print("Tools", dspy_tools)

        react = dspy.ReAct(DataAnalyst, tools=dspy_tools)
        result = await react.acall(user_request="What's the most popular Amazon product category")
        print(result)
</code></pre>

This one is more complicated. We similarly initialize our MCP server, but rather than having a single command as a string, we need to split up the command and the arguments. 

DSPy also requires us to specify a `Signature` class for each interaction, where we define input and output fields. We then provide that class when initializing our agent, which is done using the `React` class. 

`ReAct` stands for "reasoning and acting," which asks the LLM to decide whether to call a tool or wrap up the process. If a tool is required, the LLM takes responsibility for deciding which tool to call and providing the appropriate arguments.

You’ll notice that we must iterate over our MCP tools and convert them to DSPy ones.

<p> 
&#x1F4C4; <a href="https://clickhouse.com/docs/use-cases/AI/MCP/ai-agent-libraries/DSPy" target="_blank">View the full DSPy example</a> <br />
&#x1F9EA; <a href="https://github.com/ClickHouse/examples/tree/main/ai/mcp/dspy" target="_blank">Try the DSPy notebook</a>
</p>

### 3. LangChain

[LangChain](https://github.com/langchain-ai/langchain-mcp-adapters) is a framework for building LLM-powered applications.

<pre><code type='click-ui' language='python'>
server_params = StdioServerParameters(
    command="uv", 
    args=[
        "run", 
        "--with", "mcp-clickhouse",
        "--python", "3.13", 
        "mcp-clickhouse"
    ],
    env=env
)
         
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await load_mcp_tools(session)
        agent = create_react_agent("anthropic:claude-sonnet-4-0", tools)
        
        handler = UltraCleanStreamHandler()        
        async for chunk in agent.astream_events(
            {"messages": [{"role": "user", "content": "Who's committed the most code to ClickHouse?"}]}, 
            version="v1"
        ):
            handler.handle_chunk(chunk)
            
        print("\n")
</code></pre>

LangChain follows a similar approach to DSPy when initializing the MCP Server. Like DSPy, we need to invoke a ReAct function to create the agent, passing in our MCP tools. We (well, Claude!) wrote a custom bit of code (`UltaCleanStreamHandler`) to render the output in a more user-friendly way.

<p> 
&#x1F4C4; <a href="https://clickhouse.com/docs/use-cases/AI/MCP/ai-agent-libraries/langchain" target="_blank">View the full LangChain example</a> <br />
&#x1F9EA; <a href="https://github.com/ClickHouse/examples/tree/main/ai/mcp/langchain" target="_blank">Try the LangChain notebook</a>
</p>

### 4. LlamaIndex

[LlamaIndex](https://docs.llamaindex.ai/en/stable/api_reference/tools/mcp/) is a data framework for your LLM applications.

<pre><code type='click-ui' language='python'>
mcp_client = BasicMCPClient(
    "uv", 
    args=[
        "run", 
        "--with", "mcp-clickhouse",
        "--python", "3.13", 
        "mcp-clickhouse"
    ],
    env=env
)

mcp_tool_spec = McpToolSpec(
    client=mcp_client,
)

tools = await mcp_tool_spec.to_tool_list_async()

agent_worker = FunctionCallingAgentWorker.from_tools(
    tools=tools, 
    llm=llm, verbose=True, max_function_calls=10
)
agent = AgentRunner(agent_worker)

response = agent.query("What's the most popular repository?")
</code></pre>

LlamaIndex follows the familiar approach of initializing the MCP server. We then initialize an agent with our tools and LLM. We found the default `max_function_calls` value of 5 was too low and wasn’t enough to answer any questions, so we increased it to 10.

<p> 
&#x1F4C4; <a href="https://clickhouse.com/docs/use-cases/AI/MCP/ai-agent-libraries/llamaindex" target="_blank">View the full LlamaIndex example</a> <br />
&#x1F9EA; <a href="https://github.com/ClickHouse/examples/tree/main/ai/mcp/llamaindex" target="_blank">Try the LlamaIndex notebook</a>
</p>

### 5. PydanticAI

[PydanticAI](https://ai.pydantic.dev/mcp/run-python/#installation) is a Python agent framework designed to make it less painful to build production-grade applications with Generative AI.

<pre><code type='click-ui' language='python'>
server = MCPServerStdio(  
    'uv',
    args=[
        'run',
        '--with', 'mcp-clickhouse',
        '--python', '3.13',
        'mcp-clickhouse'
    ],
    env=env
)
agent = Agent('anthropic:claude-sonnet-4-0', mcp_servers=[server])

async with agent.run_mcp_servers():
    result = await agent.run("Who's done the most PRs for ClickHouse?")
    print(result.output)
</code></pre>

Pydantic has the simplest API. Again, we initialize our MCP server and pass it into the agent. It then runs the server as an asynchronous context manager and we can ask the agent questions inside that block.

<p> 
&#x1F4C4; <a href="https://clickhouse.com/docs/use-cases/AI/MCP/ai-agent-libraries/pydantic-ai" target="_blank">View the full PydanticAI example</a> <br />
&#x1F9EA; <a href="https://github.com/ClickHouse/examples/tree/main/ai/mcp/pydanticai" target="_blank">Try the PydanticAI notebook</a>
</p>

## Try It Out

We’re just getting started with MCP and ClickHouse, and we’d love to hear about what you’re building and your experience using mcp-clickhouse. 

Try out the examples, build something cool, and let us know what you think. If you run into issues or have ideas, open a GitHub issue or [chat with us in Slack](https://clickhouse.com/slack).