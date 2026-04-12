# Mode: Research

Surface topic ideas for upcoming LinkedIn posts based on a theme or industry.

## Steps

1. **Get research direction:**
   - Ask the user for a theme, industry, or keyword (e.g. "AI in HR", "startup growth", "engineering leadership").
   - Alternatively, read `config/topics.yaml` calendar and identify upcoming gaps (dates with no topic)  -  offer to research topics to fill them.

2. **Search for ideas:**
   - Use web search to find:
     - Trending LinkedIn content and discussions in this topic area
     - Recent news, data points, or reports related to the theme
     - Popular hashtags used with this topic
     - What angles are getting engagement (contrarian takes, how-tos, personal stories, data-driven insights)

3. **Check for duplicates:**
   - Read `data/posts.tsv` using the history module to get recent topics.
   - Filter out any ideas that overlap with recently posted content.

4. **Synthesize results:**
   - Generate 5–10 distinct topic ideas. For each:
     - **Topic:** a specific angle or hook (not just the broad theme)
     - **Format:** suggest `text`, `carousel`, `single_image`, or `quote_card`
     - **Hashtags:** 3–5 relevant hashtags
     - **Why:** one sentence on why this angle would perform well
   - Display the list in a numbered format.

5. **User selects:**
   - Ask user to pick which topics they want to keep (multi-select by number).
   - Ask: add to **calendar** (with specific dates) or **pool** (draw from randomly)?
   - If calendar: suggest date spacing based on current schedule in `config/schedule.yaml` (e.g. if daily, assign consecutive dates; if MWF, assign next available slots).
   - Let user adjust dates if needed.

6. **Save:**
   - Write selected topics to `config/topics.yaml` (calendar entries or pool items).
   - Confirm what was added.
