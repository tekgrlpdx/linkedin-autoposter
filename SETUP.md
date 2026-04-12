# Setup Guide

This guide walks you through connecting the LinkedIn Auto-Poster to your LinkedIn account. No prior experience with LinkedIn's developer tools is needed  -  every step is explained.

**Time required:** ~15 minutes

**What you'll set up:**
1. A LinkedIn Company Page (if you don't have one)
2. A LinkedIn "developer app" (this is how LinkedIn lets outside tools post on your behalf)
3. API keys for Claude (generates your posts) and Unsplash (sources photos)
4. A one-time login to connect everything

---

## Before You Start

Make sure you have:

- [ ] A LinkedIn account (the personal profile you want to post from)
- [ ] Python 3.10–3.13 installed on your machine ([python.org/downloads](https://www.python.org/downloads/))
- [ ] Claude Code installed
- [ ] A Canva Pro account (optional  -  only needed for branded image creation)

### What's a "developer app"?

LinkedIn doesn't let tools post directly to your account. Instead, you create a "developer app"  -  think of it as a permission slip that says "I authorize this tool to post on my behalf." The app itself is just a settings page on LinkedIn; it doesn't cost anything and takes 2 minutes to create.

---

## Step 1: Install Dependencies

Open your terminal, navigate to the project folder, and run:

```bash
cd social_media_posting
pip install -r requirements.txt
playwright install chromium
```

> **What this does:** Installs the Python libraries the system needs (LinkedIn API client, image processing, etc.) and a headless browser for generating carousel images.

---

## Step 2: Create a LinkedIn Company Page

> **Why is this needed?** LinkedIn requires every developer app to be linked to a Company Page. This is just a registration formality  -  **your posts will still go to your personal profile, not this page.** Many developers create a blank placeholder page solely for this purpose.

**If you already admin a Company Page**, skip to Step 3.

1. Go to [linkedin.com](https://www.linkedin.com) and log in
2. Click the **For Business** icon (grid icon in the top navigation bar)
3. Scroll down and click **Create a Company Page**
4. Select **Company** as the page type
5. Fill in:
   - **Name:** anything (e.g. "Your Name's Dev" or your business name)
   - **URL and other fields:** fill in whatever is required
6. Click **Create page**

> **What you should see:** In the top navigation bar, look for a grid icon (3x3 dots) labeled **"For Business"**. Click it to open a dropdown menu. Scroll to the bottom of that menu and click **"Create a Company Page"**. On the next screen, select **"Company"** as the page type.

You don't need to add a logo, post content, or invite followers. A completely blank page works.

> **How do I know if I'm a "Super Admin"?** If you created the page, you're automatically the Super Admin. This matters in the next steps.

---

## Step 3: Create a LinkedIn Developer App

This is where you create the permission slip that lets the tool post to your profile.

1. Go to [www.linkedin.com/developers/apps/new](https://www.linkedin.com/developers/apps/new)
   - You may need to log in with your LinkedIn credentials

2. Fill in the four required fields:

   | Field | What to enter |
   |-------|---------------|
   | **App name** | Anything you like, e.g. "My LinkedIn Poster" |
   | **LinkedIn Page** | Select the Company Page you created in Step 2 |
   | **Privacy policy URL** | Any URL works for personal use (e.g. your GitHub profile URL) |
   | **App logo** | Any image  -  a simple icon or your profile photo is fine |

3. Click **Create app**

> **What you should see:** A form titled **"Create an app"** with four fields:
> - **App name**  -  text field (enter anything, e.g. "My LinkedIn Poster")
> - **LinkedIn Page**  -  dropdown/search field (type your Company Page name from Step 2)
> - **Privacy policy URL**  -  text field (any URL works for personal use)
> - **App logo**  -  file upload (any small image works)
>
> Fields marked with a red asterisk (*) are required. Click **"Create app"** at the bottom when done.

> **"I don't see my Company Page in the dropdown"**  -  Make sure you're logged into the same LinkedIn account that created/admins the page. The page must also be active (not deactivated).

---

## Step 4: Verify the App with Your Company Page

After creating the app, LinkedIn needs to confirm that you actually admin the Company Page you linked to.

1. Go to [www.linkedin.com/developers/apps](https://www.linkedin.com/developers/apps)
2. Click on your new app to open it
3. Click the **Settings** tab
4. Look for the **App verification** section
5. If it says "Verified"  -  you're done, move to Step 5
6. If it says "Needs verification"  -  click the **Verify** button and follow the prompts

> **What you should see:** The **Settings** tab shows an **"App settings"** section with your linked Company Page. Look for a green **"Verified"** badge next to your Company Page name with the verification date. Below that you'll see your App name, Privacy policy URL, and App logo.

> **What if I'm not the Super Admin?** The Super Admin of the Company Page needs to approve the verification. If you created the page in Step 2, you're the Super Admin and this should be automatic.

> **What happens if I skip this?** The app will be deactivated after 30 days and you won't be able to post.

---

## Step 5: Add the "Share on LinkedIn" Product

Products are LinkedIn's way of granting specific permissions to your app. You need exactly one product.

1. In your app, click the **Products** tab
2. Find **Share on LinkedIn** in the list
3. Click **Request access**
4. Approval is instant  -  you should see it appear under "Added products"

> **What you should see:** The **Products** tab has two sections:
> - **Added products** (top)  -  after requesting access, **"Share on LinkedIn"** appears here with "Default Tier" and a description. This confirms the product is active.
> - **Available products** (bottom)  -  lists other products you could add. You don't need any of these.
>
> If "Share on LinkedIn" still appears under "Available products" with a **"Request access"** button, click it. Approval is instant.

### What does this product do?

It grants a permission called `w_member_social`. In plain English: **it lets your app create posts on your personal LinkedIn profile.**

### What you do NOT need

- **"Sign In with LinkedIn using OpenID Connect"**  -  not used by this project. Harmless if you already added it.
- **"Community Management API"**  -  this is for posting to Company Pages via the API. It requires a separate approval process. See [docs/LINKEDIN_API_REFERENCE.md](docs/LINKEDIN_API_REFERENCE.md) if you're interested.

---

## Step 6: Set Up the OAuth Redirect URL

When you log in to authorize the app (Step 8), LinkedIn needs to know where to send you back. This is called a "redirect URL."

1. In your app, click the **Auth** tab
2. Scroll down to **OAuth 2.0 settings**
3. Under **Authorized redirect URLs for your app**, click the pencil/edit icon
4. Add this exact URL:
   ```
   http://localhost:8080/callback
   ```
5. Click **Update** or **Save**

> **What you should see:** The **Auth** tab has an **"OAuth 2.0 settings"** section. Scroll down to **"Authorized redirect URLs for your app"**. Click the pencil/edit icon on the right side, type `http://localhost:8080/callback` in the field, and click **Update**.

> **What is `localhost:8080`?** It's your own computer. When you authenticate in Step 8, the tool starts a tiny temporary web server on your machine to catch LinkedIn's response. This URL tells LinkedIn to send the response there.

---

## Step 7: Copy Your Client ID and Client Secret

Still on the **Auth** tab:

1. Find **Client ID**  -  this is a long string of letters and numbers. Copy it.
2. Find **Client Secret**  -  click "show" to reveal it, then copy it.

> **What you should see:** At the top of the **Auth** tab, under **"Application credentials"**, you'll see:
> - **Client ID**  -  a long string of letters and numbers, displayed in plain text
> - **Primary Client Secret**  -  hidden behind dots. Click the eye icon to reveal it, or the copy icon to copy it directly.
>
> Copy both values  -  you'll need them in your `.env` file.

Now set up your credentials file:

```bash
cp .env.example .env
```

Open `.env` in any text editor and fill in:

```
LINKEDIN_CLIENT_ID=paste_your_client_id_here
LINKEDIN_CLIENT_SECRET=paste_your_client_secret_here
```

> **Keep your Client Secret private.** Don't commit it to git, share it publicly, or paste it in chat. The `.gitignore` file already prevents `.env` from being committed.

---

## Step 8: Get Your Other API Keys

You need two more keys. Both are free.

### Claude API Key (required  -  generates your post text)

1. Go to [platform.claude.com](https://platform.claude.com)
2. Sign in or create an account
3. Navigate to **API Keys**
4. Click **Create Key**, give it a name, and copy the key
5. Paste it in your `.env` file:
   ```
   ANTHROPIC_API_KEY=paste_your_key_here
   ```

### Unsplash API Key (required  -  sources stock photos)

1. Go to [unsplash.com/developers](https://unsplash.com/developers)
2. Click **Register as a developer** (or log in)
3. Click **New Application**
4. Accept the terms, give your app a name
5. Copy the **Access Key** (not the Secret Key)
6. Paste it in your `.env` file:
   ```
   UNSPLASH_ACCESS_KEY=paste_your_key_here
   ```

### Pexels API Key (optional  -  fallback photo source)

1. Go to [pexels.com/api](https://www.pexels.com/api/)
2. Sign up and request an API key
3. Paste it in your `.env` file:
   ```
   PEXELS_API_KEY=paste_your_key_here
   ```

---

## Step 9: Connect Your LinkedIn Account

This is the one-time login that authorizes the tool to post on your behalf.

In Claude Code, run:

```
/linkedin setup
```

Or run the script directly:

```bash
python .claude/skills/linkedin/scripts/setup_auth.py
```

**What happens:**
1. Your browser opens to a LinkedIn login/authorization page
2. LinkedIn asks: "Allow this app to post on your behalf?"  -  click **Allow**
3. You're redirected to a page that says "Authorization Successful!"
4. Back in your terminal, you'll see your LinkedIn profile name confirming the connection

> **What you should see:** Your browser opens to a LinkedIn page asking you to authorize your app. It shows your app name and the permissions it's requesting (sharing posts on your behalf). Click **"Allow"** to grant access. You'll be redirected to a page that says **"Authorization Successful!"**  -  you can close this browser tab and go back to your terminal.

> **"Port 8080 is already in use"**  -  Another program is using that port. Kill it with: `lsof -ti:8080 | xargs kill` then try again.

> **"Authorization failed"**  -  Double-check that the Client ID and Client Secret in `.env` match your app's Auth tab exactly. Also check that you added the redirect URL in Step 6.

---

## Step 10: Set Up Your Writing Voice

```
/linkedin persona
```

This lets you define how Claude writes your posts. You can:
- Pick a tone (professional, casual, educational)
- Add custom style instructions ("short sentences", "never use jargon")
- Drop writing samples in the `samples/` folder
- Import your existing LinkedIn posts as a style reference

---

## Step 11: Start Creating Content

```
/linkedin research    # Find topic ideas
/linkedin calendar    # Plan your posting schedule
/linkedin generate    # Create posts
/linkedin post        # Publish to LinkedIn
```

See the [README.md](README.md) for a full list of commands.

---

## How Authentication Works (for the curious)

You don't need to understand this to use the tool, but if you're wondering what all those tokens are:

1. **Client ID + Client Secret** identify your developer app to LinkedIn
2. When you log in (Step 9), LinkedIn gives the tool an **access token**  -  a temporary password that lets it post on your behalf
3. Access tokens **expire every 60 days**. The tool automatically refreshes them using a **refresh token** (lasts ~1 year)
4. If both tokens expire, just re-run `/linkedin setup`
5. You can revoke access anytime from your [LinkedIn Settings → Permitted Services](https://www.linkedin.com/psettings/permitted-services) page

---

## Scheduling Posts (Optional)

### Claude Code Scheduler (Recommended)

Posts are published automatically by a cloud-based agent  -  your computer doesn't need to be on.

1. Open `config/schedule.yaml` and set:
   ```yaml
   scheduler_type: claude
   ```
2. Run:
   ```
   /linkedin calendar
   ```
3. Select "Set up scheduler"  -  this creates a scheduled task that checks your calendar daily and publishes posts at the configured time.

### Cron (Alternative)

If you prefer a local cron job (requires your machine to be on at the scheduled time):

1. Set `scheduler_type: cron` in `config/schedule.yaml`
2. Add a crontab entry:
   ```bash
   # Post daily at 9:00 AM Eastern
   0 9 * * * cd /path/to/social_media_posting && python .claude/skills/linkedin/scripts/publish.py --next
   ```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "LINKEDIN_CLIENT_ID not set" | Open `.env` and fill in your Client ID from Step 7 |
| "No access token" | Run `/linkedin setup` to authenticate |
| Port 8080 in use | Run `lsof -ti:8080 \| xargs kill` then retry |
| Authorization failed | Check Client ID + Secret match your app. Check redirect URL was added in Step 6. |
| Token expired | The system auto-refreshes tokens. If that fails, re-run `/linkedin setup` |
| "I don't see my Company Page" | Make sure you're logged into the same LinkedIn account that admins the page |
| Unsplash returns no results | Check `UNSPLASH_ACCESS_KEY` is set in `.env` |
| Python version error | Use Python 3.10–3.13. Python 3.14 has compatibility issues. |

---

## FAQ

**Can I post to my Company Page too?**
Not with the default setup. This system posts to your personal profile. Posting to a Company Page requires the Community Management API, which needs separate approval from LinkedIn. See [docs/LINKEDIN_API_REFERENCE.md](docs/LINKEDIN_API_REFERENCE.md).

**Will this post without my approval?**
Only if you turn off the review step. By default, `review_required: true` in `config/schedule.yaml` means all generated posts go to a draft queue. You approve them with `/linkedin review` before they publish.

**Can I revoke access?**
Yes. Go to [LinkedIn Settings → Permitted Services](https://www.linkedin.com/psettings/permitted-services), find your app, and remove it.

**How much does this cost?**
The LinkedIn API, Unsplash, and Pexels are free. Claude API charges per token (~$0.01–0.05 per generated post). Canva requires a Pro subscription ($15/month) for branded image creation.

**Can I use this on multiple LinkedIn accounts?**
Each account needs its own `.env` file with its own tokens. The system is designed for one account at a time.
