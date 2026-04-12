"""Persona loading and system prompt assembly.

Reads config/persona.yaml, writing samples from samples/, and builds
the system prompt that Claude uses when generating posts.
"""

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "persona.yaml"

TONE_DEFINITIONS = {
    "professional": (
        "Write in a professional, authoritative tone. Use clear, confident language. "
        "Share insights that demonstrate expertise. Avoid slang or overly casual phrasing. "
        "Structure posts with a strong opening hook, supporting points, and a clear takeaway."
    ),
    "casual": (
        "Write in a conversational, approachable tone. Use first person freely. "
        "Share personal anecdotes and relatable observations. Keep sentences short. "
        "Write like you're talking to a colleague over coffee."
    ),
    "educational": (
        "Write in an informative, teaching-oriented tone. Break down complex ideas "
        "into digestible points. Use numbered lists, frameworks, and actionable tips. "
        "The reader should walk away having learned something specific."
    ),
    "custom": "",
}


def load_config() -> dict:
    """Load persona configuration from YAML."""
    if not CONFIG_PATH.exists():
        return {"tone": "professional", "style_notes": "", "samples_dir": "samples/", "active": True}
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f) or {}


def save_config(config: dict):
    """Save persona configuration to YAML."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def load_writing_samples() -> str:
    """Read all .txt and .md files from the samples directory."""
    config = load_config()
    samples_dir = PROJECT_ROOT / config.get("samples_dir", "samples/")

    if not samples_dir.exists():
        return ""

    samples = []
    for ext in ("*.txt", "*.md"):
        for file in sorted(samples_dir.glob(ext)):
            content = file.read_text().strip()
            if content:
                samples.append(f"--- Sample from {file.name} ---\n{content}")

    return "\n\n".join(samples)


def build_system_prompt() -> str:
    """Assemble the full system prompt for post generation."""
    config = load_config()

    if not config.get("active", True):
        return "Generate a LinkedIn post in a neutral, professional tone."

    parts = [
        "You are a LinkedIn content creator writing posts for a personal profile.",
        "Your goal is to create engaging, authentic posts that drive meaningful engagement.",
        "",
    ]

    # Tone
    tone = config.get("tone", "professional")
    tone_def = TONE_DEFINITIONS.get(tone, TONE_DEFINITIONS["professional"])
    if tone_def:
        parts.append(f"## Tone\n{tone_def}")

    # Custom style notes
    style_notes = config.get("style_notes", "")
    if style_notes:
        parts.append(f"## Style Notes\n{style_notes}")

    # Writing samples
    samples = load_writing_samples()
    if samples:
        parts.append(
            "## Writing Samples\n"
            "Match the voice, sentence structure, vocabulary, and rhythm of these samples:\n\n"
            f"{samples}"
        )

    # Formatting guidelines
    parts.append(
        "## Formatting Rules\n"
        "- Keep posts between 150-600 words (LinkedIn's sweet spot for engagement).\n"
        "- Start with a strong hook in the first line  - this is what shows before 'see more'.\n"
        "- Use line breaks for readability. No walls of text.\n"
        "- End with a clear call to action or question to drive comments.\n"
        "- Include 3-5 relevant hashtags at the end.\n"
        "- Do not use emojis unless the writing samples consistently use them.\n"
        "- Write in first person."
    )

    return "\n\n".join(parts)
