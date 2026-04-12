---
name: notebooklm
description: Use this skill when working with Google NotebookLM — creating/querying notebooks, managing sources, or running research workflows via the notebooklm-mcp MCP server.
---

# NotebookLM (lite MCP)

MCP server: `notebooklm-mcp` (11 tools). Script: `~/.claude/notebooklm_mcp_lite.py`.
Full 35-tool server available at `/path/to/works/for/you/.local/bin/notebooklm-mcp`.
Auth: run `nlm login`. Refresh mid-session: `refresh_auth`.

## Tools

| Tool | Notes |
|------|-------|
| `notebook_list` | List all notebooks |
| `notebook_get` | Get notebook details, including sources list |
| `notebook_create` | Create a new notebook |
| `notebook_delete` | Requires `confirm=True` after user approval |
| `source_add` | Add url / text / drive / file (PDFs via `file_path`) |
| `source_delete` | Requires `confirm=True`; accepts `source_id` or `source_ids` |
| `notebook_query` | Query existing sources only |
| `refresh_auth` | Re-authenticate mid-session |
| `research_start` | Start web or Drive search for new sources |
| `research_status` | Poll research job; use `compact=False` to review hits |
| `research_import` | Import after complete; use `source_indices` to pick a subset |

## Common workflows

**Query an existing notebook:**
`notebook_list` → `notebook_query(notebook_id=..., query=...)`

**Add a source:**
`notebook_get` to confirm notebook ID → `source_add(notebook_id=..., url=...)`

**Research workflow (find and import new sources):**
1. `research_start(notebook_id=..., query=..., source_type="web")` 
2. `research_status(job_id=..., compact=False)` — poll until complete, review hits
3. `research_import(job_id=..., source_indices=[0, 2, 4])` — import chosen subset

**Destructive operations:** always require `confirm=True`; ask user before calling.
