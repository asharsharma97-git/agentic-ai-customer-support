# Agentic AI Customer Support

An agentic customer support system built with **Amazon Bedrock AgentCore** and the **Strands Agents SDK**. The agent combines retrieval-augmented generation (RAG), long-term memory, tool calling, code execution, and live web interaction to handle customer support workflows beyond a traditional chatbot.

Built as part of the **AWS AI & ML Scholars program on Udacity**.

## Overview

Traditional chatbots mainly generate responses from a model's existing context. This project explores a more practical agentic architecture where the AI can decide when to retrieve information, call external services, perform calculations, remember customer preferences, or interact with a live webpage.

The agent can:

- Track customer orders using external API tools
- Initiate and check refunds
- Retrieve product, policy, and loyalty information using RAG
- Remember customer information and preferences across sessions
- Calculate loyalty discounts using isolated code execution
- Browse live webpages when current information is required

## Architecture

```text
                         ┌───────────────────────┐
                         │       Customer        │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │  AgentCore Runtime    │
                         │    Strands Agent      │
                         │   Amazon Nova Model   │
                         └───────────┬───────────┘
                                     │
             ┌───────────────────────┼────────────────────────┐
             │                       │                        │
             ▼                       ▼                        ▼
    ┌─────────────────┐    ┌─────────────────┐      ┌─────────────────┐
    │ AgentCore Memory│    │ Bedrock         │      │ AgentCore       │
    │                 │    │ Knowledge Base  │      │ Code Interpreter│
    │ Customer facts  │    │                 │      │                 │
    │ + preferences   │    │ RAG retrieval   │      │ Exact business  │
    └─────────────────┘    └─────────────────┘      │ calculations    │
                                                    └─────────────────┘
             │
             │                 ┌─────────────────┐
             └────────────────►│ AgentCore       │
                               │ Browser         │
                               │ Live web access │
                               └─────────────────┘

                                     │
                                     ▼
                           ┌─────────────────────┐
                           │ AgentCore Gateway   │
                           │        MCP          │
                           └──────────┬──────────┘
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                ┌─────────────────┐       ┌─────────────────┐
                │  API Gateway    │       │ AWS Lambda      │
                │  Order APIs     │       │ Refund Tools    │
                └────────┬────────┘       └─────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Order Tracker   │
                │ Lambda          │
                └─────────────────┘
```

## Key Capabilities

### Tool Calling with MCP

The agent connects to an **Amazon Bedrock AgentCore Gateway** using the Model Context Protocol (MCP).

Gateway tools allow the model to perform customer-support actions instead of attempting to answer operational questions from model knowledge.

The implemented workflows include:

- Retrieve an order
- Retrieve customer information
- Retrieve a customer's orders
- Initiate a refund
- Check refund status
- Generate a return label

### Retrieval-Augmented Generation

Product information, return policies, and loyalty-program information are stored in an **Amazon Bedrock Knowledge Base**.

A custom `search_knowledge_base` tool calls the Bedrock Retrieve API and supplies relevant document chunks to the agent.

This keeps product and policy responses grounded in the provided knowledge source rather than relying only on the model's pretrained knowledge.

### Long-Term Customer Memory

**AgentCore Memory** allows customer context to persist between independent conversations.

Two types of information are stored:

- Customer facts
- Customer communication preferences

A custom Strands hook retrieves relevant memories before an invocation and adds them to the agent's context. After the interaction, the completed conversation is stored so useful information can be extracted for future sessions.

For example, a customer can introduce themselves and request concise responses in one session, then start a completely new session where the agent recalls both pieces of information.

### Deterministic Business Calculations

Loyalty calculations are delegated to **AgentCore Code Interpreter** instead of asking the language model to perform business arithmetic itself.

The calculation logic handles:

- Loyalty-point redemption
- Membership-tier discounts
- Maximum redemption rules
- Points earned from an order
- Remaining point balances

The Python calculation executes inside an isolated code session and returns structured results to the agent.

### Live Browser Interaction

The agent integrates **AgentCore Browser**, allowing it to navigate a live webpage and retrieve information that is not available through its static knowledge base or model context.

This demonstrates how an agent can combine generative AI with live external interaction.

## Example Workflows

The deployed agent was tested across several independent workflows.

**Order tracking**

> "Can you track order ORD-001?"

The agent selects the appropriate Gateway tool and returns the order status, carrier, tracking number, and expected delivery information.

**Refund processing**

> "I want to return my Kindle Paperwhite (ORD-002). Please initiate a refund."

The agent calls the refund workflow and returns the generated refund ID, approval status, and processing timeline.

**RAG**

> "What are the benefits of the Platinum loyalty tier?"

The agent retrieves the relevant loyalty-program information from the Bedrock Knowledge Base.

**Cross-session memory**

A customer tells the agent:

> "Hi, I am Jane. I prefer concise responses."

A new session can subsequently recall both the customer's name and communication preference.

**Code execution**

> "I am a Gold member with 4250 points. Calculate my discount on a $150 standard order."

The agent delegates the business calculation to Code Interpreter and returns the redemption, membership discount, final total, and remaining points.

**Browser**

> "Go to https://www.udacity.com and tell me the page title."

The agent uses its browser capability to access the live webpage and retrieve its current title.

## Technology Stack

| Technology                       | Purpose                                  |
| -------------------------------- | ---------------------------------------- |
| Amazon Bedrock AgentCore Runtime | Agent deployment and execution           |
| Strands Agents SDK               | Agent orchestration and tool integration |
| Amazon Nova                      | Foundation model                         |
| AgentCore Gateway                | External tool integration                |
| Model Context Protocol (MCP)     | Tool discovery and invocation            |
| AWS Lambda                       | Order and refund backend functions       |
| Amazon API Gateway               | Order service REST endpoints             |
| Amazon Bedrock Knowledge Bases   | RAG                                      |
| Amazon S3                        | Knowledge-base document storage          |
| Amazon OpenSearch Serverless     | Vector storage                           |
| AgentCore Memory                 | Cross-session customer memory            |
| AgentCore Code Interpreter       | Deterministic calculations               |
| AgentCore Browser                | Live web interaction                     |
| Amazon CloudWatch                | Runtime logging and troubleshooting      |
| Python                           | Agent and tool implementation            |

## Project Structure

```text
.
├── main.py
├── lambda/
│   ├── order_tracker.py
│   ├── refund_processor.py
│   └── lambda_schema
├── product_catalog.txt
├── pyproject.toml
├── uv.lock
└── README.md
```

`main.py` contains the primary agent implementation, including the RAG tool, memory hooks, loyalty calculation tool, browser integration, MCP Gateway connection, and AgentCore Runtime entrypoint.

## What I Learned

The biggest takeaway from this project was understanding that building an AI agent involves much more than connecting an LLM to a prompt.

Different responsibilities are better handled by different components:

- LLMs handle reasoning and orchestration
- APIs and Lambda functions perform operational actions
- RAG provides grounded domain knowledge
- Memory maintains useful context across sessions
- Code Interpreter handles deterministic calculations
- Browser tools provide access to live information

One of the most valuable parts of the project was troubleshooting the Browser integration after deployment. Resolving runtime and authorization problems required working through **CloudWatch logs, IAM permissions, deployed runtime behaviour, and isolated browser testing** rather than only modifying application code.

That experience reinforced the importance of observability and systematic troubleshooting when moving an AI application from local development into a cloud runtime.

## Production Considerations

A production implementation would require additional controls around authentication, authorization, observability, and high-impact actions.

Examples include:

- Authenticate customers before exposing order or memory data
- Require validation or confirmation before sensitive actions such as refunds
- Apply least-privilege IAM policies to agent tools
- Add structured monitoring and alerting for tool failures
- Implement stronger error handling and retry strategies
- Add audit logging for customer-impacting actions
- Protect customer memory using appropriate retention and access policies

These controls become increasingly important as agents move from answering questions to taking actions on behalf of users.

## Program

This project was completed as part of the **AWS AI & ML Scholars program on Udacity**, where I worked with AWS generative AI and agentic AI technologies through hands-on projects.

The project provided practical experience building, deploying, integrating, testing, and troubleshooting a multi-tool AI agent in AWS.
