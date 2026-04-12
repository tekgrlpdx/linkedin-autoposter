# Mode: Repurpose

Turn a long-form piece of content into multiple LinkedIn posts.

## Steps

1. **Accept input:**
   - Ask user how they want to provide the content:
     - **URL:** provide a link to a blog post, article, or web page.
     - **Paste:** paste the full text directly.
     - **File:** provide a path to a local `.txt`, `.md`, or `.pdf` file.

2. **Extract content:**
   - **URL:** Use web fetch to retrieve the page content. Extract the main body text, stripping navigation, ads, and boilerplate.
   - **Paste:** Use the pasted text directly.
   - **File:** Read the file from the provided path.

3. **Analyze and identify angles:**
   - Read the full content carefully.
   - Identify 3–5 distinct angles, sections, or insights that each work as standalone LinkedIn posts.
   - For each angle, note:
     - The specific section or idea it draws from
     - Why it would work as a standalone post
     - Suggested format: `text`, `carousel`, `single_image`, or `quote_card`

4. **Generate posts:**
   - Load the persona from `config/persona.yaml` + `samples/`.
   - For each angle: generate a complete, self-contained LinkedIn post using the persona voice.
   - Each post should stand on its own  -  a reader who hasn't seen the original content should understand it fully.
   - Display all generated posts.

5. **User selects:**
   - Ask user which posts to keep (multi-select, can keep all).
   - For each kept post, allow quick edits before saving.

6. **Schedule:**
   - Suggest date spacing for the selected posts (e.g. one per week to avoid flooding).
   - Read `config/schedule.yaml` for current frequency and `config/topics.yaml` for existing calendar entries.
   - Propose dates that don't conflict with existing entries.
   - Let user adjust dates.

7. **Save:**
   - Add each selected post to:
     - `config/topics.yaml` calendar with the assigned date and topic.
     - `data/posts.tsv` via `add_post()` with the generated content.
   - Set status based on `review_required` flag.
   - Confirm what was saved and suggest next steps (`/linkedin review` if drafts, `/linkedin create-image` if visual formats).
