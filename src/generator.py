"""Post generation using the Claude API.

Takes a topic and persona, generates a LinkedIn post via Claude,
and returns the generated text.
"""

import os

import anthropic
from dotenv import load_dotenv

from src.persona import build_system_prompt

load_dotenv()


def generate_post(topic: str, format_hint: str = "text") -> str:
    """Generate a LinkedIn post for the given topic.

    Args:
        topic: The topic or prompt to write about.
        format_hint: The intended format (text, single_image, carousel, quote_card).
                     Adjusts generation instructions accordingly.

    Returns:
        The generated post text.
    """
    client = anthropic.Anthropic()

    system_prompt = build_system_prompt()

    format_instructions = {
        "text": "Write a text-only LinkedIn post.",
        "single_image": (
            "Write a LinkedIn post that will be paired with a single image. "
            "The text should complement a visual  - reference what the reader will see."
        ),
        "carousel": (
            "Write a LinkedIn post that will accompany a carousel/document. "
            "Structure the content as a numbered list or step-by-step breakdown. "
            "Each point should be self-contained (one per slide). "
            "Include an intro hook and a closing CTA slide."
        ),
        "quote_card": (
            "Write a LinkedIn post built around one powerful, quotable statement. "
            "The key quote will be overlaid on an image. "
            "The post text should expand on or contextualize that quote."
        ),
    }

    user_prompt = (
        f"{format_instructions.get(format_hint, format_instructions['text'])}\n\n"
        f"Topic: {topic}"
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return message.content[0].text


def suggest_format(topic: str) -> str:
    """Suggest the best post format for a given topic.

    Returns one of: text, single_image, carousel, quote_card.
    """
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=50,
        system=(
            "You suggest LinkedIn post formats. Respond with exactly one word: "
            "text, single_image, carousel, or quote_card. "
            "Choose carousel for lists, steps, or tips. "
            "Choose quote_card for strong opinions or memorable statements. "
            "Choose single_image for stories, announcements, or visual content. "
            "Choose text for everything else."
        ),
        messages=[{"role": "user", "content": f"Topic: {topic}"}],
    )

    result = message.content[0].text.strip().lower()
    valid = {"text", "single_image", "carousel", "quote_card"}
    return result if result in valid else "text"
