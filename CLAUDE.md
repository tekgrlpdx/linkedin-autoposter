# CLAUDE.md  -  LinkedIn Auto-Poster

## What This Project Is

A Claude Code skill system that manages the full lifecycle of LinkedIn content: research, plan, generate, create images, review, publish, and analyze. Invoked via `/linkedin <command>`.

## Project Structure

```
.claude/skills/linkedin/SKILL.md    -  Router skill (entry point)
modes/                               -  Mode files (one per command)
config/                              -  User configuration (YAML)
samples/                             -  Writing style samples
src/                                 -  Python utility modules
data/                                -  Post history (TSV)
templates/                           -  HTML/CSS carousel templates
```

## Data Contracts

### User Layer (NEVER auto-overwrite without asking)
- `config/persona.yaml`  -  writing voice
- `config/topics.yaml`  -  content calendar + topic pool
- `config/schedule.yaml`  -  posting frequency and settings
- `samples/*`  -  writing style samples
- `.env`  -  credentials and tokens

### System Layer (safe to update)
- `modes/*`  -  mode instructions
- `src/*`  -  Python modules
- `templates/*`  -  carousel HTML/CSS
- `data/posts.tsv`  -  post history (append-safe)

## Commands

```
/linkedin setup         -  One-time LinkedIn OAuth setup
/linkedin persona       -  Define writing voice
/linkedin research      -  Find topic ideas
/linkedin calendar      -  Manage content schedule
/linkedin generate      -  Generate post text
/linkedin create-image  -  Create visuals
/linkedin repurpose     -  Turn long-form content into posts
/linkedin review        -  Review and approve drafts
/linkedin post          -  Publish to LinkedIn
/linkedin analytics     -  Analyze performance
```

## Key Rules

1. Always read `modes/_shared.md` before executing any mode.
2. Never overwrite user layer files without explicit permission.
3. Check for valid LinkedIn tokens before any API call.
4. Respect the `review_required` flag  -  drafts need approval when it's on.
5. Use the Python scripts in `.claude/skills/linkedin/scripts/` for side effects (OAuth, publishing, scraping).

## Tech Stack
- Python 3.10–3.13
- LinkedIn API v2 (OAuth 2.0, personal profile)
- Claude API (Anthropic SDK) for post generation
- Unsplash / Pexels APIs for stock photos
- Canva MCP for branded image creation
- Playwright for HTML/CSS carousel screenshots
