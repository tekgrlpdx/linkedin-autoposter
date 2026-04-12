# Mode: Persona

Define the writing voice Claude uses when generating LinkedIn posts.

## Steps

1. **Show current persona:**
   - Read `config/persona.yaml` and display the current settings.
   - If no persona is configured, explain what this mode does.

2. **Offer configuration options** (the user can combine any or all):

   **a) Tone picker:**
   - Display available tones with descriptions:
     - `professional`  -  authoritative, clear, confident
     - `casual`  -  conversational, approachable, first-person heavy
     - `educational`  -  informative, teaching-oriented, actionable tips
     - `custom`  -  user provides their own tone description
   - Ask user to select one.

   **b) Style notes:**
   - Ask user for free-text style instructions.
   - Examples: "short sentences, never use jargon, always end with a question"
   - These are appended to the tone definition as additional constraints.

   **c) Writing samples:**
   - Check `samples/` directory for existing `.txt` and `.md` files.
   - If files found, list them and confirm they'll be used.
   - If empty, instruct user to drop writing samples there.
   - User can also paste sample text directly  -  save it to `samples/user_samples.txt`.

   **d) Scrape LinkedIn posts:**
   - Ask user if they want to import their existing LinkedIn posts as style reference.
   - If yes, run:
     ```bash
     python .claude/skills/linkedin/scripts/scrape_posts.py --count 20
     ```
   - Confirm the output file `samples/linkedin_posts.txt` was created.

3. **Build style summary:**
   - Read all files in `samples/`.
   - Analyze the writing patterns: sentence length, vocabulary, structure, recurring phrases, tone, formatting habits.
   - Write a 2–3 sentence style summary describing the user's voice.
   - Display it and ask for approval.

4. **Save:**
   - Write the selected tone, style notes, and style summary to `config/persona.yaml`.
   - Confirm the persona is active.

## Updating Later
The user can run `/linkedin persona` again at any time to update their voice. When re-running:
- Show the existing persona first.
- Ask what they want to change (don't force them to reconfigure everything).
- Preserve settings they don't change.
