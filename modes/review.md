# Mode: Review

Review, edit, approve, or reject drafted posts before they publish. This mode is configurable  -  it can be part of the workflow or bypassed entirely.

## Steps

1. **Check review status:**
   - Read `config/schedule.yaml` for the global `review_required` flag.
   - If `false`, inform user that review is currently disabled. Offer to enable it or proceed with reviewing any existing drafts anyway.

2. **Load drafts:**
   - Read `data/posts.tsv` and filter for posts with status `draft`.
   - Sort by `scheduled_date` ascending (soonest first).
   - If no drafts found, inform user and suggest running `/linkedin generate` first.

3. **Review each draft:**
   - Display one post at a time:
     - **Scheduled date**
     - **Topic** (source)
     - **Format** (text, single_image, carousel, quote_card)
     - **Full post content**
     - **Image** (if attached, show the path; note if no image yet)

   - Offer actions:
     - **Approve:** Update status to `scheduled` in `data/posts.tsv`. Move to next post.
     - **Edit:** Let user modify the post text inline. Save changes to `data/posts.tsv`. Update status to `scheduled`.
     - **Regenerate:** Re-run generation with the same topic and persona. Display new version. Ask for approval again.
     - **Add image:** Suggest running `/linkedin create-image` for this post. Note the post ID for reference.
     - **Change date:** Update `scheduled_date` in `data/posts.tsv`.
     - **Delete:** Remove the post from `data/posts.tsv`. Flag the gap in the calendar. Ask if user wants to fill it from the topic pool.

4. **Summary:**
   - After all drafts reviewed, display:
     - X posts approved (now scheduled)
     - Y posts deleted
     - Z calendar gaps created
   - If gaps exist, offer to run `/linkedin research` to find topics to fill them.

## Bulk Actions
If there are many drafts (5+), offer bulk actions before individual review:
- **Approve all:** move all drafts to scheduled
- **Review one by one:** proceed with individual review (default)
