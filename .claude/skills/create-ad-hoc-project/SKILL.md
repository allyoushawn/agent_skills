---
name: create-ad-hoc-project
description: Creates a dated ad-hoc project folder under knowledge_base/projects/ad_hoc/ named YYYYMMDD_{topic}, sets it as the session working directory, and tells the agent to save all session artifacts there. Use when the user says "create an ad hoc project for X" or "start an ad hoc project on X".
---

# Create Ad-Hoc Project

Use this skill when the user asks to create an ad-hoc project. The goal is to spin up a named, dated folder and orient the session around it so all artifacts land there automatically.

## Steps

1. **Parse the topic** from the user's message. Convert it to a `snake_case` slug:
   - lowercase all words
   - replace spaces and hyphens with underscores
   - strip punctuation

   Example: "colab experiment setup" → `colab_experiment_setup`

2. **Resolve today's date** from the `currentDate` context variable (format: `YYYYMMDD`).

3. **Construct the folder path:**
   ```
   /path/to/works/for/you/knowledge_base/projects/ad_hoc/YYYYMMDD_{topic_slug}/
   ```
   Example: `/path/to/works/for/you/knowledge_base/projects/ad_hoc/20260414_colab_experiment_setup/`

4. **Create the folder** using Bash:
   ```bash
   mkdir -p /path/to/works/for/you/knowledge_base/projects/ad_hoc/YYYYMMDD_{topic_slug}
   ```

5. **Create a minimal `README.md`** inside the folder (Compiled Truth — no chronological log here) with this template:

   ```markdown
   # {Human-readable topic}

   **Created:** YYYY-MM-DD
   **Status:** active

   ## Goal

   <!-- Fill in the goal of this session -->

   ## Artifacts

   <!-- Files produced this session will be listed here -->

   <!-- Optional: ## State — one-paragraph current summary when the folder becomes long-lived -->
   ```

5b. **Create `log.md`** in the same folder with one seed line:

   ```markdown
   ## [YYYY-MM-DD] init | {Human-readable topic}
   ```

   Chronological activity append here; keep `README.md` for current state and goals only.

6. **Declare the session working directory** to the user:

   > "Ad-hoc project created at:
   > `/path/to/works/for/you/knowledge_base/projects/ad_hoc/YYYYMMDD_{topic_slug}/`
   >
   > This is the session working directory. All artifacts (notes, scripts, outputs, configs) generated during this session should be saved here."

7. **Orient yourself:** For the remainder of this conversation, treat that folder as the primary output location. When saving any file, default to placing it inside this folder unless the user explicitly specifies another location.

## Notes

- If `/path/to/works/for/you/knowledge_base/projects/ad_hoc/` does not yet exist, `mkdir -p` will create it.
- Do not ask the user to confirm the folder name — create it immediately and report back.
- If the folder already exists (same date + topic), skip creation and just report the existing path.
