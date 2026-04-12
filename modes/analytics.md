# Mode: Analytics

Pull LinkedIn post performance and surface actionable insights.

## Steps

1. **Gather data:**
   - Read `data/posts.tsv` for all posts with status `published`.
   - For posts with a `linkedin_post_id`, attempt to fetch engagement stats from the LinkedIn API:
     - Views / impressions
     - Likes
     - Comments
     - Shares
     - Click-through rate (if available)
   - Note: LinkedIn's analytics API for personal profiles has limited data. Some metrics may not be available. Work with what's returned.

2. **Build analysis dataset:**
   - For each published post, combine:
     - Engagement metrics from LinkedIn
     - Post metadata from history: topic, format, day of week, time, word count
     - Persona settings at time of posting (tone from `config/persona.yaml`)

3. **Analyze patterns:**
   - Look for correlations between engagement and:
     - **Format:** do carousels outperform text posts?
     - **Topic category:** which themes get the most engagement?
     - **Day of week:** are certain days better?
     - **Post length:** do shorter or longer posts perform better?
     - **Tone/style:** any tone shifts that correlated with engagement changes?
   - Surface the top 3–5 insights with supporting data.

4. **Display insights:**
   - Present each insight clearly with the data behind it.
   - Example: "Carousel posts averaged 3.2x more views than text-only posts (based on 12 carousel vs 18 text posts)"
   - Example: "Tuesday posts outperformed all other days with an average of 450 views vs 280 on other days"

5. **Make suggestions:**
   - Based on the analysis, suggest specific changes:
     - **Topic adjustments:** add high-performing topic types to the pool in `config/topics.yaml`
     - **Format preferences:** update default format recommendations
     - **Schedule tweaks:** adjust posting day/time in `config/schedule.yaml`
     - **Tone refinements:** update `config/persona.yaml` style notes
   - Present each suggestion individually and ask user to approve or skip.

6. **Apply approved changes:**
   - Write approved suggestions to the relevant config files.
   - Confirm what was updated.

## Limitations
- LinkedIn's personal profile API provides basic engagement metrics but not detailed analytics (impressions by source, follower demographics, etc.).
- Meaningful analysis requires at least 10–15 published posts. If fewer exist, note that insights are preliminary.
- Correlation is not causation  -  frame insights as observations, not guarantees.
