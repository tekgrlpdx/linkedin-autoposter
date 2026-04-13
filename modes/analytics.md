# Mode: Analytics

Pull LinkedIn post performance and surface actionable insights.

## Data Source: Chrome Browser (Primary)

The LinkedIn API does not provide engagement metrics for personal profiles without the
`r_member_social` scope (requires Community Management API approval). Use Chrome MCP to
scrape the LinkedIn creator analytics page instead.

**Analytics URL:** `https://www.linkedin.com/analytics/creator/content/?metricType=IMPRESSIONS&timeRange=past_365_days`

**Scraping approach (Chrome MCP):**
1. Navigate to the analytics URL.
2. Wait for the page to load (2-3 seconds).
3. Extract aggregate stats using JavaScript:
   ```javascript
   const results = [];
   document.querySelectorAll('*').forEach(el => {
     const text = el.innerText?.trim();
     if (text && /^\d[\d,]*$/.test(text) && el.children.length === 0) {
       const nearbyText = el.parentElement?.parentElement?.innerText
         ?.replace(/\n+/g, ' ').substring(0, 150);
       results.push(`${text}: ${nearbyText}`);
     }
   });
   [...new Set(results)].join('\n\n')
   ```
4. Scroll down to load the "Top performing posts" section, then extract individual post cards.
5. Also check the Audience analytics tab:
   `https://www.linkedin.com/analytics/creator/audience/?timeRange=past_365_days`

**Available metrics (confirmed working):**
- Impressions (total + % change vs prior period)
- Social engagements total
- Reactions, Comments, Reposts, Saves, Sends
- Link engagements
- Top performing posts (requires enough published posts to populate)

**Not available via scraping:**
- Impressions broken down by source (search, feed, profile, etc.)
- Follower demographics beyond what's on the audience tab
- Historical per-post time series

---

## Steps

1. **Gather data:**
   - Read `data/posts.tsv` for all posts with status `published`.
   - Navigate to the LinkedIn creator analytics page using Chrome MCP.
   - Extract aggregate engagement stats using the JavaScript approach above.
   - If the "Top performing posts" section loaded, extract individual post data.
   - Also check the audience tab for follower growth and demographic info.
   - Note: Meaningful per-post analysis requires at least 10-15 published posts.

2. **Build analysis dataset:**
   - Combine LinkedIn scraped metrics with post metadata from `data/posts.tsv`:
     - Topic, format, day of week, scheduled date, word count
     - image_url presence (image vs text-only)
   - Calculate engagement rate: engagements / impressions.

3. **Analyze patterns:**
   - Look for correlations between engagement and:
     - **Format:** do image posts outperform text-only?
     - **Topic category:** which themes get the most engagement?
     - **Day of week:** are certain days better?
     - **Post length:** do shorter or longer posts perform better?
   - Surface the top 3-5 insights with supporting data.
   - Frame as observations, not guarantees (correlation is not causation).

4. **Display insights:**
   - Present each insight clearly with the data behind it.
   - Example: "Posts with images averaged 2.4x more reactions than text-only posts"
   - Example: "Tuesday posts outperformed Thursday with 450 avg impressions vs 280"

5. **Make suggestions:**
   - Based on analysis, suggest specific changes:
     - **Topic adjustments:** add high-performing topic types to `config/topics.yaml`
     - **Format preferences:** note which formats drive more engagement
     - **Schedule tweaks:** adjust posting day/time in `config/schedule.yaml`
     - **Tone refinements:** update `config/persona.yaml` style notes
   - Present each suggestion and ask user to approve or skip.

6. **Apply approved changes:**
   - Write approved suggestions to the relevant config files.
   - Confirm what was updated.

---

## Limitations
- Individual post breakdown only loads in the browser once LinkedIn has enough recent data.
- Aggregate stats cover all posts ever published, not just ones tracked in `data/posts.tsv`.
- Meaningful pattern analysis requires at least 10-15 published posts.
- The time range can be changed (past_30_days, past_90_days, past_365_days) by modifying the URL.
