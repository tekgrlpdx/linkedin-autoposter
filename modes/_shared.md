# Shared Context  -  LinkedIn Auto-Poster

This file is loaded alongside every mode. It defines data contracts, file locations, and rules that all modes must follow.

## Project Layout

```
config/persona.yaml     -  user's writing voice (USER LAYER)
config/topics.yaml      -  content calendar + topic pool (USER LAYER)
config/schedule.yaml    -  posting frequency, time, review flag (USER LAYER)
samples/                -  writing style samples as .txt/.md files (USER LAYER)
data/posts.tsv          -  post history: all generated/published posts
src/                    -  Python utility modules
.claude/skills/linkedin/scripts/  -  executable scripts
```

## Data Contracts

### User Layer (NEVER auto-overwrite)
These files belong to the user. Modes may **read** them freely but must **ask the user before writing** to them:
- `config/persona.yaml`
- `config/topics.yaml`
- `config/schedule.yaml`
- `samples/*`
- `.env`

### System Layer (safe to update)
These files are part of the system and can be updated without asking:
- `data/posts.tsv`
- `modes/*`
- `src/*`
- `templates/*`

### Post History (data/posts.tsv)
TSV file with columns:
`id`, `topic`, `generated_content`, `image_url`, `format`, `scheduled_date`, `status`, `review_required`, `linkedin_post_id`, `created_at`, `published_at`, `error`

Valid statuses: `draft`, `scheduled`, `published`, `failed`
Valid formats: `text`, `single_image`, `carousel`, `quote_card`

### Topics Calendar (config/topics.yaml)
```yaml
calendar:
  - date: "YYYY-MM-DD"
    topic: "string"
    format: text | single_image | carousel | quote_card  # optional
    review_required: true | false  # optional, overrides global
pool:
  - "topic string"
```

## Rules

1. **Always read config before acting.** Don't assume default values  -  read the actual YAML files.
2. **Check post history before generating.** Avoid duplicate topics by reading `data/posts.tsv` recent entries.
3. **Respect the review flag.** If `review_required` is true (globally or per-post), generated posts go to `draft` status, not `scheduled`.
4. **Use the scripts for side effects.** OAuth, publishing, and scraping use the Python scripts in `.claude/skills/linkedin/scripts/`. Don't reimplement their logic inline.
5. **Image workflow:** Stock photos come from Unsplash/Pexels APIs → uploaded to Canva → brand template applied → exported. For carousels without Canva, use the HTML/CSS templates in `templates/carousel/`.
6. **Token management:** Before any LinkedIn API call, the scripts handle token refresh automatically. If tokens are missing or invalid, direct the user to run `/linkedin setup`.

## Available Scripts

| Script | Purpose | Usage |
|---|---|---|
| `setup_auth.py` | OAuth 2.0 flow | `python .claude/skills/linkedin/scripts/setup_auth.py` |
| `publish.py` | Publish a post | `python .claude/skills/linkedin/scripts/publish.py <post_id>` or `--next` |
| `scrape_posts.py` | Fetch user's posts | `python .claude/skills/linkedin/scripts/scrape_posts.py [--count 20]` |

## Available Python Modules

| Module | Key Functions |
|---|---|
| `src/history.py` | `add_post()`, `get_post()`, `update_post()`, `delete_post()`, `get_posts_by_status()`, `get_next_scheduled()`, `get_recent_topics()` |
| `src/linkedin.py` | `get_valid_token()`, `get_profile()`, `publish_post()`, `upload_image()`, `get_user_posts()` |
| `src/persona.py` | `load_config()`, `save_config()`, `build_system_prompt()`, `load_writing_samples()` |
| `src/generator.py` | `generate_post()`, `suggest_format()` |
| `src/images.py` | `search_photos()`, `search_unsplash()`, `search_pexels()` |
| `src/carousel.py` | `build_carousel()`, `render_slide_html()` |
