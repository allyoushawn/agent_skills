---
name: consult-llm
description: Use when the user wants a second opinion from Gemini or OpenAI/ChatGPT, asks to "consult" another model, or wants to compare responses across models
---

# consult-llm

You have access to two MCP tools for consulting other LLMs:

- `mcp__chat-gemini__chat-with-gemini` — sends a message to Google Gemini
- `mcp__chat-openai__chat-with-openai` — sends a message to OpenAI (GPT)

## When This Skill Applies

Use this skill when the user:
- Asks to "consult", "ask", or "check with" another LLM (Gemini, GPT, OpenAI, ChatGPT)
- Wants a second opinion from a different model
- Says "what does Gemini think", "ask GPT", "get another model's take", etc.
- Wants to compare responses across models

## How to Use

### Selecting the right model
- If the user specifies "Gemini" or "Google" → use `mcp__chat-gemini__chat-with-gemini`
- If the user specifies "GPT", "OpenAI", or "ChatGPT" → use `mcp__chat-openai__chat-with-openai`
- If unspecified or user wants both → consult both in parallel

### Crafting the prompt
- Send the user's question or context as-is, or distill it into a clear, self-contained query
- If you need to include code or context, include enough for the other model to give a useful answer
- Do not include internal Claude Code instructions or system context in the query

### Presenting results
- Quote the other model's response clearly, labeled with which model it came from
- Add your own synthesis or comparison if the user asked for a second opinion
- If both models were consulted, highlight agreements and disagreements

## Example Invocations

```
User: "What does Gemini think about this regex?"
→ call mcp__chat-gemini__chat-with-gemini with the regex and context

User: "Ask GPT and Gemini both — which sorting algorithm should I use here?"
→ call both tools in parallel, then compare their answers

User: "Get a second opinion on my architecture"
→ pick one or both models, send the architecture description, synthesize the feedback
```
