---
name: kb-from-conversation
description: Converts a raw LLM conversation transcript into a structured knowledge base note and saves it in the correct project folder under `/path/to/works/for/you/knowledge_base/projects/`. Use when the user pastes an LLM conversation and asks to "save this", "document this", "add to the KB", or "jot this down", or when a conversation contains reusable frameworks, plans, or decisions worth retaining.
---

# KB From Conversation

Converts a pasted LLM conversation into a structured, durable knowledge base note.

## When to invoke

- User pastes a conversation and says "save this", "document this", "add to the KB", "jot this down"
- A conversation contains reusable frameworks, decisions, plans, mental models, or templates

## What to keep vs. discard

**Keep:** frameworks, mental models, decision templates, plans, checklists, definitions, reusable strategies, personal insights about values/priorities

**Discard:** specific trip logistics, troubleshooting for one-off problems, UI/UX details of specific apps, weather data, parking advice, customer support transcripts, ephemeral details that don't generalize

## Process

1. Read the conversation to understand what was discussed
2. Identify topics and classify each as keep vs. discard
3. Identify the target project folder under `/path/to/works/for/you/knowledge_base/projects/` — ask the user if ambiguous
4. For each topic to keep, spawn the **kb-librarian** agent (via Agent tool) with a description of the content. Ask it to scan the target project folder and return a concrete routing recommendation: append to existing file or create a new file
5. Present the routing plan to the user: "I'll create X in project Y" or "I'll append to Z". Wait for approval before writing — unless the user said "just do it"
6. Write the note file(s) using the structure below
7. **Project log and README (Compiled Truth):**
   - If the project's `log.md` is missing, create it with a single seed line: `## [YYYY-MM-DD] init | <short label from project folder or README title>`.
   - Append to `log.md`: `## [YYYY-MM-DD] ingest | <topic or filename of the new note>`.
   - If the project `README.md` has a **Contents** or **Files** table (inside or outside `KB_INDEX`), add a row linking the new note file. Do **not** add a Progress Log or chronological session log inside `README.md`.
8. Confirm completion: "Added `filename.md` to `project/`. `log.md` updated."

## Handling multi-topic conversations

- If one conversation covers multiple distinct topics, create separate files for each
- If topics are tightly coupled, keep in one file with clear H2 sections

## Note file structure

```markdown
# [Topic Name]

Addresses Big Question #N ([domain]) and #M ([domain]).  ← omit if not a big_questions project

[1–2 sentence framing of the problem or context.]

---

## [Section]

[Content: tables, lists, frameworks, templates, checklists]

---

## Connection to the 12 Big Questions   ← include only for big_questions project

| Big Question # | Domain | Connection |
|---------------|--------|------------|
| #N | [domain] | [how this topic relates] |

---

## Notes

- Added: YYYY-MM-DD
- [Any relevant context]
```

**Conventions:**
- No YAML frontmatter in note files
- H1 = topic name
- First line after title: italicized reference to which Big Question(s) this addresses, if applicable
- Cross-reference table at the bottom linking to related files in the same project (when relevant)

## README and log conventions

- **Contents / Files table row** (if the project README maintains one): `| [filename.md](./filename.md) | one-line description |`
- **`log.md` entry** (always append, never rewrite past lines): `## [YYYY-MM-DD] ingest | <topic or filename>: [2–3 word summary of what was captured]`
