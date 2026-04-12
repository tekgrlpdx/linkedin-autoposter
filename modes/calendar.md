# Mode: Calendar

View, create, edit, and manage the content schedule.

## Steps

1. **Display current calendar:**
   - Read `config/topics.yaml` and `config/schedule.yaml`.
   - Display upcoming calendar entries in a table:

     | Date | Topic | Format | Review | Status |
     |------|-------|--------|--------|--------|

   - Status is determined by cross-referencing with `data/posts.tsv`:
     - If a post exists for this date: show its status (draft/scheduled/published)
     - If no post exists: show "not generated"
   - Also show the topic pool count: "X topics in pool"
   - Show current schedule settings (frequency, time, timezone, review flag).

2. **Offer actions:**
   - Ask user what they'd like to do:

   **a) Add topic:**
   - Ask for: topic/prompt, date, format (optional, default text), review_required (optional, uses global default).
   - Append to the calendar in `config/topics.yaml`.

   **b) Edit topic:**
   - Let user pick a calendar entry by date or topic text.
   - Show current values, ask what to change.
   - Update the entry in `config/topics.yaml`.

   **c) Delete topic:**
   - Let user pick an entry to remove.
   - Remove from `config/topics.yaml`.
   - Ask if the gap should be flagged or filled from the pool.

   **d) Reorder / reschedule:**
   - Let user move a topic to a different date.
   - Check for conflicts (two topics on the same date).

   **e) Set schedule settings:**
   - Update `frequency`, `post_time`, `timezone` in `config/schedule.yaml`.

   **f) Toggle review:**
   - Toggle `review_required` globally in `config/schedule.yaml`, or per-post in `config/topics.yaml`.

   **g) Set up scheduler:**
   - If `scheduler_type: claude` in `config/schedule.yaml`:
     - Create or update a Claude Code scheduled task using `mcp__scheduled-tasks__create_scheduled_task`.
     - The task prompt should instruct the agent to check `config/topics.yaml` for today's post, generate it, and publish (or save as draft if review is required).
   - If `scheduler_type: cron`:
     - Display the crontab entry the user should add.
   - Show the current scheduler status.

3. **Save changes:**
   - Write all modifications to `config/topics.yaml` and/or `config/schedule.yaml`.
   - Confirm what changed.
