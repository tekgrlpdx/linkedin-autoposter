# Mode: Generate

Generate LinkedIn post text for one or more calendar entries using Claude + persona.

## Steps

1. **Determine scope:**
   - Ask user what to generate:
     - A specific date: "Generate the post for April 15"
     - A date range: "Generate posts for next week"
     - A count: "Generate the next 5 posts"
     - All ungenerated: "Generate all posts that don't have content yet"
   - Also accept a direct prompt: "Generate a post about leadership" (bypasses calendar).

2. **Identify target topics:**
   - Read `config/topics.yaml` calendar entries matching the scope.
   - Cross-reference with `data/posts.tsv` to skip entries that already have generated content.
   - For direct prompts, use the user's prompt as the topic.

3. **Load persona:**
   - Read `config/persona.yaml` and all files in `samples/`.
   - The `src/persona.py` module handles this via `build_system_prompt()`.

4. **Generate each post:**
   For each topic:
   - Determine format: use the calendar entry's `format` field, or call `suggest_format()` from `src/generator.py` if not specified.
   - Call `generate_post(topic, format_hint)` from `src/generator.py`.
   - Display the generated post for a quick preview.
   - Ask if the user wants to keep, regenerate, or skip this post.

5. **Save to history:**
   - For each kept post, call `add_post()` from `src/history.py`:
     - `topic`: the source topic
     - `generated_content`: the generated text
     - `scheduled_date`: from the calendar entry (or ask user for direct prompts)
     - `format`: the determined format
     - `review_required`: from the calendar entry or global `config/schedule.yaml` setting
   - Post status will be `draft` if review required, `scheduled` if not.

6. **Next steps:**
   - If any posts have format `single_image`, `carousel`, or `quote_card`: suggest running `/linkedin create-image` to create visuals.
   - If posts are in `draft` status: remind user to run `/linkedin review` to approve them.
   - If posts are in `scheduled` status: confirm they'll publish at the configured time.

## Headless Mode (Scheduler)
When triggered by the Claude scheduler (not a user), skip display and confirmations:
- Generate the post for today's calendar entry (or pick from pool).
- Save to history following the review flag.
- If `review_required: false`, the `/linkedin post` mode will pick it up for publishing.
