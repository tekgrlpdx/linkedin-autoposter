#!/usr/bin/env python3
"""LinkedIn OAuth 2.0 setup script.

Starts a local Flask server, opens the LinkedIn authorization URL,
and exchanges the authorization code for access + refresh tokens.

Usage:
    python .claude/skills/linkedin/scripts/setup_auth.py
"""

import sys
import threading
import webbrowser
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, request
from src.linkedin import exchange_code_for_tokens, get_authorization_url, get_profile

app = Flask(__name__)
auth_result = {"code": None, "error": None}
shutdown_event = threading.Event()


@app.route("/callback")
def callback():
    code = request.args.get("code")
    error = request.args.get("error")

    if error:
        auth_result["error"] = error
        shutdown_event.set()
        return f"<h1>Authorization Failed</h1><p>Error: {error}</p><p>You can close this window.</p>"

    if code:
        auth_result["code"] = code
        shutdown_event.set()
        return "<h1>Authorization Successful!</h1><p>You can close this window and return to the terminal.</p>"

    shutdown_event.set()
    return "<h1>Unknown Error</h1><p>No code or error received.</p>"


def run_server():
    app.run(port=8080, debug=False, use_reloader=False)


def main():
    print("=" * 60)
    print("LinkedIn OAuth 2.0 Setup")
    print("=" * 60)
    print()

    # Check for client credentials
    from dotenv import load_dotenv
    import os

    env_path = project_root / ".env"
    if not env_path.exists():
        example_path = project_root / ".env.example"
        if example_path.exists():
            import shutil
            shutil.copy(example_path, env_path)
            print("Created .env from .env.example")
        else:
            print("ERROR: No .env file found. Copy .env.example to .env and fill in your credentials.")
            sys.exit(1)

    load_dotenv(env_path)

    if not os.getenv("LINKEDIN_CLIENT_ID") or not os.getenv("LINKEDIN_CLIENT_SECRET"):
        print("ERROR: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set in .env")
        print("Get these from https://www.linkedin.com/developers/apps/new")
        sys.exit(1)

    # Start local server in a background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Open authorization URL
    auth_url = get_authorization_url()
    print(f"Opening LinkedIn authorization in your browser...\n")
    print(f"If the browser doesn't open, visit this URL manually:\n{auth_url}\n")
    webbrowser.open(auth_url)

    print("Waiting for authorization...")
    shutdown_event.wait(timeout=300)

    if auth_result["error"]:
        print(f"\nERROR: Authorization failed: {auth_result['error']}")
        sys.exit(1)

    if not auth_result["code"]:
        print("\nERROR: Timed out waiting for authorization.")
        sys.exit(1)

    # Exchange code for tokens
    print("\nExchanging authorization code for tokens...")
    tokens = exchange_code_for_tokens(auth_result["code"])
    print(f"Access token saved (expires in {tokens['expires_in'] // 86400} days)")

    if tokens.get("refresh_token"):
        print("Refresh token saved")
    else:
        print("WARNING: No refresh token received. You'll need to re-authorize when the token expires.")

    # Verify connection
    print("\nVerifying connection...")
    profile = get_profile()
    first_name = profile.get("localizedFirstName", "")
    last_name = profile.get("localizedLastName", "")
    print(f"Connected as: {first_name} {last_name}")
    print("\nSetup complete!")


if __name__ == "__main__":
    main()
