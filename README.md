# LinkedIn Auto-Poster

AI-powered LinkedIn content management built as a Claude Code skill. Research, plan, generate, design, review, and publish LinkedIn posts  -  all from your terminal.

## How It Works

1. You tell the system what topics you want to post about
2. Claude writes posts in your voice (you define the tone and style)
3. The system sources photos from Unsplash/Pexels and optionally brands them in Canva
4. You review and approve posts (or skip review for fully automatic posting)
5. Posts publish to your **personal LinkedIn profile** on your schedule

## What You Need

| Requirement | Cost | Notes |
|-------------|------|-------|
| LinkedIn account | Free | The personal profile you want to post from |
| LinkedIn Company Page | Free | A blank placeholder works  -  only needed to register the developer app (see [SETUP.md](SETUP.md)) |
| LinkedIn developer app | Free | The "permission slip" that lets this tool post on your behalf |
| Claude API key | ~$0.01–0.05/post | From [platform.claude.com](https://platform.claude.com) |
| Unsplash API key | Free | From [unsplash.com/developers](https://unsplash.com/developers) |
| Python 3.10–3.13 | Free | 3.14 has compatibility issues with some dependencies |
| Claude Code | - | The tool you're already using |
| Claude in Chrome extension | Free | Required for analytics and importing your existing posts as writing samples. Install from the Chrome Web Store. |
| Canva Pro (optional) | $15/month | Only needed for branded image creation |
| Pexels API key (optional) | Free | Fallback photo source |

## Setup

Full step-by-step setup with screenshots: **[SETUP.md](SETUP.md)**

The short version:

```bash
pip install -r requirements.txt
playwright install chromium
cp .env.example .env          # then fill in your API keys
```

```
/linkedin setup               # one-time LinkedIn authentication
```

## Commands

Run these inside Claude Code:

| Command | What it does |
|---------|-------------|
| `/linkedin setup` | Connect your LinkedIn account (one-time) |
| `/linkedin persona` | Define your writing voice  -  pick a tone, add writing samples, or import your existing posts |
| `/linkedin research` | Find topic ideas  -  searches trends and suggests angles with hashtags |
| `/linkedin calendar` | Plan your posting schedule  -  add topics, set dates, configure frequency |
| `/linkedin generate` | Write posts  -  Claude generates content from your calendar using your voice |
| `/linkedin create-image` | Add visuals  -  sources photos and brands them in Canva, or builds carousels |
| `/linkedin repurpose` | Turn a blog post or article into multiple LinkedIn posts |
| `/linkedin review` | Review drafts  -  approve, edit, or regenerate before publishing |
| `/linkedin post` | Publish  -  post to LinkedIn now, or let the scheduler handle it |
| `/linkedin analytics` | See what's working  -  scrapes LinkedIn creator analytics via Chrome and suggests improvements |

## Typical Workflow

```
/linkedin research     →  find what to write about
/linkedin calendar     →  plan when to post
/linkedin generate     →  create the posts
/linkedin create-image →  add visuals (optional)
/linkedin review       →  approve before publishing (configurable)
/linkedin post         →  publish (manual or automatic)
/linkedin analytics    →  learn and improve
```

## Configuration

All settings live in the `config/` folder as YAML files you can edit:

### `config/persona.yaml`  -  Your writing voice
- **Tone:** `professional`, `casual`, `educational`, or `custom`
- **Style notes:** free-text instructions (e.g. "short sentences, always end with a question")
- **Writing samples:** drop `.txt` or `.md` files in the `samples/` folder

### `config/topics.yaml`  -  Your content calendar
- **Calendar:** dated entries with topics, formats, and review flags
- **Pool:** a list of topics to draw from randomly when no calendar entry is set

### `config/schedule.yaml`  -  When and how to post
- **Frequency:** `daily`, `mon_wed_fri`, or `weekly`
- **Post time:** what time of day (24h format)
- **Review required:** whether posts need your approval before publishing
- **Scheduler type:** `claude` (cloud), `cron` (local), or `apscheduler` (Python process)

## Scheduling

Three options for automatic posting:

| Method | How it works | Machine needs to be on? |
|--------|-------------|------------------------|
| **Claude Code scheduler** (recommended) | Cloud-based agent runs on a cron schedule | No |
| **Cron** | Local crontab entry runs the publish script | Yes |
| **APScheduler** | Long-running Python process | Yes |

Set your preference in `config/schedule.yaml`. See [SETUP.md](SETUP.md) for configuration details.

## Project Structure

```
.claude/skills/linkedin/SKILL.md  →  Skill entry point (routes commands)
modes/*.md                        →  Instructions for each command
src/*.py                          →  Python modules (LinkedIn API, image sourcing, etc.)
config/*.yaml                     →  Your settings (voice, calendar, schedule)
samples/                          →  Your writing samples
data/posts.tsv                    →  Post history log
templates/carousel/               →  HTML/CSS templates for carousel slides
docs/                             →  Architecture diagrams and API reference links
```

## File Ownership

The system separates your files from system files so updates never overwrite your settings:

| Layer | Files | Rule |
|-------|-------|------|
| **Your files** | `config/*`, `samples/*`, `.env` | Never auto-overwritten by the system |
| **System files** | `modes/*`, `src/*`, `templates/*` | Safe to update |
| **Data** | `data/posts.tsv` | Append-only post history, gitignored |

## FAQ

**Does this post to my personal profile or my Company Page?**
Personal profile by default. Company Page posting requires a separate LinkedIn approval process. See [docs/LINKEDIN_API_REFERENCE.md](docs/LINKEDIN_API_REFERENCE.md).

**Will it post without my approval?**
Not by default. `review_required: true` is the default in `config/schedule.yaml`. All generated posts go to a draft queue until you approve them with `/linkedin review`. Set it to `false` for fully automatic posting.

**Can I revoke access?**
Yes. Go to [LinkedIn Settings → Permitted Services](https://www.linkedin.com/psettings/permitted-services) and remove the app.

**What if my tokens expire?**
Access tokens last 60 days. The system refreshes them automatically. If refresh fails, re-run `/linkedin setup`.

**Why does analytics and persona scraping use Chrome instead of the LinkedIn API?**
LinkedIn's "Share on LinkedIn" developer product only grants write access (`w_member_social`). Reading your posts or engagement data requires the `r_member_social` scope, which is only available through LinkedIn's Community Management API (requires a formal application and approval). Rather than blocking on that, this tool uses the Claude in Chrome extension to scrape your LinkedIn analytics page and activity feed directly from your logged-in browser session.

**Can I import my existing LinkedIn posts as writing style samples?**
Yes. Run `/linkedin persona` and choose option **d) Scrape LinkedIn posts**. The system will open your LinkedIn activity page in Chrome and extract your post text automatically. No additional API access needed.

## Documentation

- [SETUP.md](SETUP.md)  -  Full setup walkthrough with screenshots
- [CONSIDERATIONS.md](CONSIDERATIONS.md)  -  Platform limitations and technical constraints
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)  -  System diagrams and data flow
- [docs/LINKEDIN_API_REFERENCE.md](docs/LINKEDIN_API_REFERENCE.md)  -  LinkedIn API documentation links and scope reference

## License

MIT
