# Mode: Create Image

Source a photo, bring it into Canva with brand overlay, or build an HTML/CSS carousel.

## Steps

1. **Identify the post:**
   - Ask user which post needs an image: by date, ID, or "the most recent draft".
   - Read the post from `data/posts.tsv`.
   - Display the post content and current format.

2. **Determine image type:**
   - Based on the post's `format` field:
     - `single_image` → single photo with text overlay
     - `quote_card` → background photo with quotable line overlaid
     - `carousel` → multi-slide PDF
   - If format is `text`, ask if user wants to upgrade to an image format.

---

## Single Image / Quote Card Flow

3. **Extract keywords:**
   - Read the post content and extract 2–3 keyword themes that describe the visual mood.
   - Example: post about "building resilient teams" → keywords: "teamwork", "collaboration", "people working together"

4. **Source photo:**
   - Call `search_photos()` from `src/images.py` with the extracted keywords.
   - This queries Unsplash first, falls back to Pexels.
   - Display the top 3–5 results with descriptions and thumbnail URLs.
   - Ask user to pick one, or provide different search terms to retry.

5. **Upload to Canva:**
   - Use the Canva MCP `upload-asset-from-url` tool to upload the selected photo to Canva.
   - Note the asset ID returned.

6. **Apply brand template:**
   - Use the Canva MCP tools to:
     - Create or open a design using a brand template.
     - Set the uploaded photo as the background.
     - For **single_image**: overlay the post headline or key stat as text using brand fonts/colors.
     - For **quote_card**: extract the single most quotable line from the post; overlay as large centered text.
   - If the user has a Canva brand kit, use it for fonts and colors.

7. **Export:**
   - Use the Canva MCP `export-design` tool to export the final image.
   - Save the exported image path.
   - Update `data/posts.tsv`: set `image_url` on the post record.

---

## Carousel Flow

3. **Structure slides:**
   - Read the post content and break it into slides:
     - Slide 1: hook / title (cover slide)
     - Slides 2–N: one point per slide (content slides, max 7 total)
     - Last slide: CTA + handle/branding
   - Display the proposed slide structure and ask for approval.

4. **Choose creation path:**
   - **Canva path** (preferred): for each slide, source a background photo via Unsplash/Pexels, upload to Canva, apply brand template with slide text.
   - **HTML/CSS path** (fallback or user preference): use `templates/carousel/slide.html` and `styles.css` to render each slide, capture with Playwright.
   - Ask user which path, or default to Canva if available.

5. **Build slides:**
   - **Canva path:**
     - For each slide: search photos matching the slide theme → upload to Canva → apply template with slide title and body text → export each slide.
     - Assemble exported slides into a PDF carousel in Canva using the `merge-designs` tool.
   - **HTML/CSS path:**
     - Call `build_carousel()` from `src/carousel.py` with the slide data.
     - This renders HTML → captures screenshots with Playwright → assembles into PDF.

6. **Save:**
   - Update `data/posts.tsv`: set `image_url` to the PDF path, set `format` to `carousel`.
   - Display confirmation with the output path.

---

## Notes
- If Unsplash/Pexels return no results, suggest different keywords or ask user to provide an image URL directly.
- If Canva MCP is unavailable, fall back to HTML/CSS path automatically.
- Photo attribution: Unsplash and Pexels photos are free for commercial use but attribution is appreciated. Include photographer credit in post text when reasonable.
