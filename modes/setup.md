# Mode: Setup

One-time onboarding. Authenticates with LinkedIn and confirms the connection works.

## Steps

1. **Check prerequisites:**
   - Read `.env` file. If it doesn't exist, copy from `.env.example`.
   - Check if `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET` are set.
   - If not set, ask the user for their LinkedIn developer app credentials and write them to `.env`.
   - If the user doesn't have a LinkedIn developer app yet, walk them through it:
     - Go to https://www.linkedin.com/developers/apps/new
     - **LinkedIn Page requirement:** LinkedIn requires every developer app to be associated with a Company Page. This is just an administrative formality  -  it does NOT mean posts go to that page. If the user doesn't have one, they can create a blank placeholder page (e.g. "Your Name's Dev")  -  no followers or content needed. They must be a Super Admin of the page.
     - After creating the app, a Super Admin of the page must verify it (if they created the page, they're already the admin).
     - Under Products tab: request "Share on LinkedIn" (self-serve, instant) and "Sign In with LinkedIn using OpenID Connect" (self-serve, instant). These grant `w_member_social` for personal profile posting. Do NOT request Community Management API (that's for company pages and requires partner approval).
     - Under Auth tab: add `http://localhost:8080/callback` as a redirect URI
     - Note the client ID and client secret from the Auth tab

2. **Run the OAuth flow:**
   ```bash
   python .claude/skills/linkedin/scripts/setup_auth.py
   ```
   This will:
   - Open the LinkedIn authorization page in the user's browser
   - Start a local server on port 8080 to catch the redirect
   - Exchange the authorization code for tokens
   - Save tokens to `.env`
   - Display the connected profile name

3. **Verify:**
   - Confirm the `.env` file now contains `LINKEDIN_ACCESS_TOKEN`
   - Display the user's LinkedIn profile name as confirmation

4. **Next steps:**
   - Suggest running `/linkedin persona` to set up their writing voice
   - Mention that tokens expire in 60 days and the system handles refresh automatically

## Error Handling
- If port 8080 is in use, inform the user and suggest killing the process using it.
- If the authorization fails, display the error and suggest checking the client credentials.
- If the user's LinkedIn app doesn't have the required scopes, explain how to add them.
