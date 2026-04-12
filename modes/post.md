# Mode: Post

Publish a post to LinkedIn immediately or manage the publish queue.

## Manual Invocation

1. **Show queue:**
   - Read `data/posts.tsv` and display posts with status `scheduled`, ordered by date.
   - Show: date, topic preview (first 50 chars), format, image status.

2. **Offer actions:**
   - **Post now:** User picks a specific post to publish immediately.
   - **Reschedule:** Change a post's `scheduled_date`.
   - **Delay:** Push a post back by N days.
   - **Cancel:** Delete a post from the queue.

3. **Publish action:**
   - Confirm with user: "Publish this post to LinkedIn now?"
   - Display the full post content one more time.
   - Run the publish script:
     ```bash
     python .claude/skills/linkedin/scripts/publish.py <post_id>
     ```
   - Display the result (success with LinkedIn post ID, or error).

## Scheduler-Triggered Flow

When triggered by the Claude Code scheduler (headless, no user interaction):

1. Run:
   ```bash
   python .claude/skills/linkedin/scripts/publish.py --next
   ```
   This finds the next post with status `scheduled` where `scheduled_date` <= today and publishes it.

2. If no scheduled post is found:
   - Check `config/topics.yaml` for today's calendar entry or pick from pool.
   - Generate a post (using `/linkedin generate` logic).
   - If `review_required: false`: publish immediately.
   - If `review_required: true`: save as draft and stop (user will review later).

3. Log the outcome to `data/posts.tsv`.

## Error Handling
- If LinkedIn API returns an error, update the post status to `failed` with the error message.
- Common errors:
  - **401 Unauthorized:** tokens expired. Suggest running `/linkedin setup` to re-authenticate.
  - **429 Rate Limited:** too many posts. Wait and retry later.
  - **422 Validation Error:** content too long or invalid characters. Display the error details.
- On failure, the post remains in the queue and can be retried.
