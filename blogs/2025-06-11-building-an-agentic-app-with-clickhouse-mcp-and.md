---
title: "Building an agentic app with ClickHouse MCP and CopilotKit"
date: "2025-06-11T17:47:34.072Z"
author: "Lionel Palacin"
category: "Engineering"
excerpt: "Learn how to build an Agentic application that turns natural language prompts into dynamic analytics dashboard using ClickHouse MCP Server and CopilotKit."
---

# Building an agentic app with ClickHouse MCP and CopilotKit

Searching for your new house, you’re trying to understand the price trends in the neighborhood. Imagine that instead of browsing through pre-defined charts, clicking through filters and dropdowns to get the information you’re interested in, you could just ask:

**“Show me the price evolution in Manchester for the last 10 years.”**

And it just responds with a chart, an explanation, and maybe even follow-up questions.

![agentic-application-animation-2.gif](https://clickhouse.com/uploads/agentic_application_animation_2_6098bb8a92.gif)

That is the promise of Agentic applications. Powered by Large Language Models (LLMs), they can reason through complex tasks, call APIs, and build entire workflows from a single user prompt, making them intelligent, interactive user experiences.

Watch our customer panel discuss the potential of MCP in real-time analytics applications in this video.

<iframe width="768" height="432" src="https://www.youtube.com/embed/-K64C-iKHwM?si=lcMZ_9joFDa7z2y_" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<br />

In this blog, we will show how to build one. We will create a build-your-own analytics dashboard experience for the UK real estate market using [ClickHouse MCP Server](https://github.com/ClickHouse/mcp-clickhouse) and [CopilotKit](https://www.copilotkit.ai/). This example is built using React with Next.js, but the same approach can be used with any modern application framework.

## Components of the Agentic application

Let’s start by going through the components of an agentic application.

### Large language model

At the core of any agentic application is a [Large Language Model](https://en.wikipedia.org/wiki/Large_language_model) (LLM). The LLM interprets user prompts, understands context, generates responses, and decides what actions to take.

For a smooth and responsive experience, it is essential to use a capable model with fast performance and a reasonably large context window. Agentic applications often deal with complex prompts, interact with external tools, and use data from third-party systems. As more information is added to the context, the model must process it efficiently and respond quickly. This is what enables an interactive and natural experience for the end user.

In our example, we use the model Claude Sonnet 3.7 from [Anthropic](https://docs.anthropic.com/en/docs/about-claude/models/overview). When writing this blog, it was one of the best-performing on [TAU-bench](https://arxiv.org/abs/2406.12045) for the [airline](https://hal.cs.princeton.edu/taubench_airline) and [retail](https://hal.cs.princeton.edu/taubench_retail) use case, a benchmark that aims to rank LLMs on their interaction with human users and ability to follow domain-specific rules. 

### ClickHouse MCP Server

Our agentic application is going to help users analyze the UK real estate market data by building their custom dashboard. While the market data is [public](https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads) and the model may have seen it in pre-training, that information is stored in the model’s weights, not as exact records. This means that even if the model has seen some of the data, there’s a chance it’ll make up some numbers if we asked questions about property in the UK. In many cases, the model will need access to live or proprietary data sources to provide accurate and useful insights.

This is the purpose of a [Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) (MCP) server, an open standard that enables developers to build secure, two-way connections between their data sources and AI-powered tools.

[ClickHouse MCP server](https://github.com/ClickHouse/mcp-clickhouse) enables developers to integrate ClickHouse inside their agentic application, allowing the application to query data directly from the application. 

### CopilotKit

The third core component in this setup is [CopilotKit](https://www.copilotkit.ai/) which is a UI framework designed to simplify the development of agentic applications. 

I chose to use CopilotKit for this project because it abstract away several complex aspects of the architecture. It provides built-in support for the chat interface, connects easily with different LLMs, and manages tool calls or UI actions that the model can decide to perform.

Next, we will see how each of these components works together.

## High level architecture

Let’s walk through the flow triggered by a user request. This example illustrates how the components interact to turn a natural language prompt into a fully rendered chart.

![agentic-application-diagram-1.png](https://clickhouse.com/uploads/agentic_application_diagram_1_8a6a2d7d2a.png)

1.  The user sends the following prompt: “Show me the price evolution in Manchester for the last 10 years.”
2.  The prompt, along with the list of available actions and state variables, is sent to the CopilotKit runtime.
3.  CopilotKit enriches the prompt with the list of MCP resources, then forwards it to the LLM. The LLM analyzes the prompt and available resources, determines that it needs to retrieve data, and generates a SQL query targeting ClickHouse.
4.  The CopilotKit runtime uses the MCP client to send the query request.
5.  MCP Client calls the ClickHouse MCP Server with the SQL query to retrieve the price data in the Manchester area for the last 10 years.
6.  The data is returned to the LLM along with the current context. The model identifies the generateChart action and prepares the response by formatting the data according to the expected chart parameters.

This flow highlights how the different parts of the agentic application work together. The model interprets the user’s prompt, fetches data using ClickHouse through the MCP Server, and updates the UI by calling predefined actions. 

## How to build the Agentic application

Now that we’ve covered how the application works at a high level, let’s go through a step-by-step guide to building it from scratch.

This section focuses only on the important part of the implementation. For a fully working example, look at the example in [this Github repository](https://github.com/ClickHouse/examples/tree/main/ai/mcp/copilotkit).

### Initialize the application

We start by creating a new React application and initializing it with the CopilotKit framework. To do this, we use the [npx helper](https://docs.npmjs.com/cli/v8/commands/npx) to bootstrap the project. When prompted about how the application will interact with the model, be sure to select the MCP option.

<pre><code type='click-ui' language='bash'>
npx create-next-app@latest
cd agentic-app
npx copilotkit@latest init
</code></pre>

### Bring your own LLM 

By default, OpenAI is configured by CopilotKit. We can swap with another model if we wish to, [here](https://docs.copilotkit.ai/direct-to-llm/guides/bring-your-own-llm) is the list of models supported by Copilotkit. 

The connection to the LLM happens on the server side, by default CopilotKit exposes an API route that the client integrates with to interact with the LLM. 

Edit the file `./app/api/copilotkit/routes.ts` to swap the model. 

<pre><code type='click-ui' language='javascript'>
import { AnthropicAdapter } from "@copilotkit/runtime";

// const serviceAdapter = new OpenAIAdapter()
const serviceAdapter = new AnthropicAdapter({model: "claude-3-7-sonnet-latest"});
</code></pre>

Don’t forget to provide the API key (`ANTHROPIC_API_KEY`) as an environment variable.   

### Deploy the ClickHouse MCP Server

In this example, we deploy the ClickHouse MCP Server locally, but it is also possible to deploy it remotely and have multiple MCP clients connect to it.

> Soon, ClickHouse Cloud will offer a remote MCP server as a default interface. That means any MCP client could connect directly to your cloud instance without additional local setup.
>
> Want early access? [Sign up for the AI features waitlist at clickhouse.ai](http://clickhouse.ai).

<pre><code type='click-ui' language='bash'>
# Clone the ClickHouse MCP Server repository
git clone https://github.com/ClickHouse/mcp-clickhouse
# Install dependencies
python3 -m venv .venv && source .venv/bin/activate && uv sync && uv add fastmcp
# Configure connection to ClickHouse database 
export CLICKHOUSE_HOST="sql-clickhouse.clickhouse.com"
export CLICKHOUSE_USER="demo"
export CLICKHOUSE_SECURE="true"
export CLICKHOUSE_PORT="8443"
# Run the MCP server and expose SSE transport protocol
fastmcp run mcp_clickhouse/mcp_server.py:mcp --transport sse
</code></pre>

For this demo, we’re using the ClickHouse [SQL Playground](https://sql.clickhouse.com), which includes the [UK market dataset](https://clickhouse.com/docs/getting-started/example-datasets/uk-price-paid).

Finally, we use the [fastmcp](https://gofastmcp.com/deployment/running-server#the-fastmcp-cli) command to start the MCP server and expose it using SSE transport, by default, on port 8000. 

### Configure the MCP Client

CopilotKit comes with built-in [support](https://docs.copilotkit.ai/direct-to-llm/guides/model-context-protocol?cli=do-it-manually) for MCP client, we just need to configure the connection so it can access it.

Edit the file `./app/copilotkit/page.tsx` to add the ClickHouse MCP Server connection.

<pre><code type='click-ui' language='javascript'>
 useEffect(() => {
    setMcpServers([
      { endpoint: "http://localhost:8000/sse" },
    ]);
 }, []);
</code></pre>

### Create the agent actions

The main promise of an agentic application is that it can take actions on behalf of the user, guided by their conversation.

In our case, the goal is for the application to generate custom charts based on the user's description. This is the action we need to describe so the LLM can perform it.

For this, we're going to use the CopilotKit hook [useCopilotAction](https://docs.copilotkit.ai/reference/hooks/useCopilotAction). This hook lets developers define custom actions that the model can invoke. In our example, the action is to add a new chart configuration.

We are also going to leverage another hook: [useCopilotReadable](https://docs.copilotkit.ai/reference/hooks/useCopilotReadable), which allows us to share a state variable from the application with the model. Here, we make the chart configuration array available to the model. 

To set this up, edit the file `./app/copilotkit/page.tsx` to define the new action and make the charts state variable available to the model.

<pre><code type='click-ui' language='javascript' raw_code='// Chart configuration array 
const [charts, setCharts] = useState<Chart[]>([]);

// Share the charts state variable with LLM
useCopilotReadable({
  description: "These are all the charts props",
  value: charts,
});

// Create a new action generateChart that will be used by the LLM to create the correct chart configuration and add it to the state variable. 
useCopilotAction({
    name: "generateChart",
    description: "Generate a chart based on the provided data. Make sure to provide the data in the correct format and specify what field should be used a x-axis.",
    parameters: [
        {
            name: "data",
            type: "object[]",
            description: "Data to be used for the chart. The data should be an array of objects, where each object represents a data point.",
        },
        {
            name: "chartType",
            type: "string",
            description: "Type of chart to be generated. Lets use bar, line, area, or pie.",
        },
        {
            name: "title",
            type: "string",
            description: "Title of the chart. Cant be more than 30 characters.",
        },
        { name: "xAxis", type: "string", description: "x-axis label" }
    ],

    handler: async ({ data, chartType, title, xAxis }) => {
        const newChart = {
            data,
            chartType,
            title,
            xAxis
        };
        setCharts((charts) => [...charts, newChart] );
    },
    render: "Adding chart...",
});'>
</code></pre>

Then we need to add a DynamicGrid component to iterate through the chart configuration array and build the charts for each of them. 

<pre><code type='click-ui' language='javascript' raw_code='function DynamicGrid({ charts }: { charts: Chart[] }) {
return (
      charts.map((chart, index) => (
      <div className="flex flex-col gap-4" key={index}>
              <p className="text-white whitespace-nowrap overflow-hidden text-overflow-ellipsis text-xl leading-[150%] font-bold font-inter">{chart.title}</p>
              <GenericChart {...chart} />
          </div>
      ))
  )
}'>
</code></pre>

The GenericChart component uses the [echart](https://echarts.apache.org/examples/en/index.html) for react chart library, but you can easily swap for your preferred ones. You can see the code for the GenericChart component [here](https://github.com/ClickHouse/examples/blob/copilotkit/ai/mcp/copilotkit/components/GenericChart.tsx).

### Final result

We’ve covered the key parts of the implementation. From here, it’s mostly a matter of adding some styling to make the application look polished. The full source code can be found on [Github](https://github.com/ClickHouse/examples/tree/main/ai/mcp/copilotkit). 

## Benefits of using ClickHouse in an Agentic application

### Real-time analytics database

Using a real-time analytics database like ClickHouse is essential for this type of agentic application.

![benefit-db-ai-agents.png](https://clickhouse.com/uploads/benefit_db_ai_agents_c7a5f47245.png)

Real-time analytics databases have properties that make them well-suited for Agentic application workload. They work with near real-time data, allowing systems to incorporate the latest information as it arrives. This supports agents that need to make or support timely decisions.

These databases are also built for complex analytical tasks such as aggregations, trend analysis, and anomaly detection across large datasets. Unlike operational databases, they are optimized for extracting insights rather than simply storing or retrieving raw records.

Finally, they support interactive querying at high frequency and under high concurrency. This ensures stable performance during chat-based interactions and exploratory data work, contributing to a smoother and more responsive user experience.

### Fine grained permissions and quotas

One of the main challenges when building agentic applications is maintaining control over what the LLM is allowed to do on your behalf. This becomes especially important when the model has access to query a production database through a MCP server.

Fortunately, ClickHouse offers a wide range of [permissions](https://clickhouse.com/docs/operations/access-rights) and [quotas](https://clickhouse.com/docs/operations/quotas) making it straightforward to control exactly what the MCP server can expose to the model.

In this example, we're using the SQL Playground to host the UK Market dataset. We have configured the MCP Server to authenticate to the Playground using the demo user. You can see the configuration of this user [here](https://github.com/ClickHouse/sql.clickhouse.com/blob/main/setup.sql).

The demo user has read-only access and is restricted to a specific set of databases. This allows us to limit the data the LLM can reach. On top of that, we apply quota settings and assign a limited profile to the user to prevent the model from overloading the server with too many or overly expensive queries. This setup gives us fine-grained control over both the scope and cost of what the model can do.

## Conclusion

In this blog post, we explored how to build an agentic application using ClickHouse MCP Server and CopilotKit. 

By leveraging the capabilities of LLMs, we created an application that allows users to build their own analytics dashboard on UK market data. 

The use of a fast, scalable and secure analytics database like ClickHouse is crucial for the efficiency and effectiveness of such applications. This approach opens up new possibilities for creating AI-powered tools that provide deeper insights and better user experiences.



