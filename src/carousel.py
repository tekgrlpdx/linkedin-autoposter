"""HTML/CSS carousel builder.

Generates carousel slides from HTML templates, captures them as images
with Playwright, and assembles them into a PDF.
"""

import asyncio
import json
import os
from pathlib import Path

from fpdf import FPDF

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "templates" / "carousel"
OUTPUT_DIR = PROJECT_ROOT / "output"


def _load_template() -> str:
    """Load the slide HTML template."""
    template_path = TEMPLATE_DIR / "slide.html"
    return template_path.read_text()


def _load_styles() -> str:
    """Load the slide CSS styles."""
    styles_path = TEMPLATE_DIR / "styles.css"
    if styles_path.exists():
        return styles_path.read_text()
    return ""


def render_slide_html(
    slide_number: int,
    total_slides: int,
    title: str,
    body: str,
    is_cover: bool = False,
    is_cta: bool = False,
) -> str:
    """Render a single slide to HTML by substituting template placeholders."""
    template = _load_template()
    styles = _load_styles()

    slide_type = "cover" if is_cover else "cta" if is_cta else "content"

    html = template.replace("{{styles}}", styles)
    html = html.replace("{{slide_number}}", str(slide_number))
    html = html.replace("{{total_slides}}", str(total_slides))
    html = html.replace("{{title}}", title)
    html = html.replace("{{body}}", body)
    html = html.replace("{{slide_type}}", slide_type)

    return html


async def _capture_slides(slides_html: list[str], output_prefix: str) -> list[str]:
    """Capture each slide HTML as a PNG image using Playwright."""
    from playwright.async_api import async_playwright

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    image_paths = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 1080})

        for i, html in enumerate(slides_html):
            await page.set_content(html, wait_until="networkidle")
            path = str(OUTPUT_DIR / f"{output_prefix}_slide_{i + 1}.png")
            await page.screenshot(path=path, full_page=False)
            image_paths.append(path)

        await browser.close()

    return image_paths


def capture_slides(slides_html: list[str], output_prefix: str) -> list[str]:
    """Synchronous wrapper for slide capture."""
    return asyncio.run(_capture_slides(slides_html, output_prefix))


def assemble_pdf(image_paths: list[str], output_path: str) -> str:
    """Combine slide images into a single PDF carousel.

    Uses 1080x1080 square format (LinkedIn carousel standard).
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdf = FPDF(unit="pt", format=(1080, 1080))
    for img_path in image_paths:
        pdf.add_page()
        pdf.image(img_path, x=0, y=0, w=1080, h=1080)

    full_path = str(OUTPUT_DIR / output_path) if not os.path.isabs(output_path) else output_path
    pdf.output(full_path)
    return full_path


def build_carousel(
    slides: list[dict],
    output_name: str,
) -> str:
    """Full pipeline: render slides to HTML, capture as images, assemble PDF.

    Args:
        slides: List of dicts with keys: title, body.
                First slide treated as cover, last as CTA.
        output_name: Base name for output files (no extension).

    Returns:
        Path to the generated PDF.
    """
    total = len(slides)
    slides_html = []

    for i, slide in enumerate(slides):
        html = render_slide_html(
            slide_number=i + 1,
            total_slides=total,
            title=slide.get("title", ""),
            body=slide.get("body", ""),
            is_cover=(i == 0),
            is_cta=(i == total - 1),
        )
        slides_html.append(html)

    image_paths = capture_slides(slides_html, output_name)
    pdf_path = assemble_pdf(image_paths, f"{output_name}.pdf")

    return pdf_path
