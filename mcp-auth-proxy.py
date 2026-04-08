#!/usr/bin/env python3
"""MCP Auth Proxy — stdio proxy that authenticates via Google OAuth and forwards
requests to a remote MCP server (Builder or squad) with automatic JWT management.

Usage in .mcp.json:
  {
    "mcpServers": {
      "mcp-builder": {
        "type": "stdio",
        "command": "python",
        "args": ["tools/mcp-auth-proxy.py"],
        "env": {
          "MCP_BUILDER_URL": "https://mcp-builder-XXXXX.run.app/mcp"
        }
      }
    }
  }

For direct squad access, pass --target:
  "args": ["tools/mcp-auth-proxy.py", "--target", "https://squad-seo.example.com/sse"]
"""

import argparse
import json
import logging
import os
import stat
import sys
import time
from pathlib import Path

import httpx
from google_auth_oauthlib.flow import InstalledAppFlow

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(levelname)s: %(message)s")
logger = logging.getLogger("mcp-auth-proxy")

# ── Configuration ────────────────────────────────────────────────────────────

DEFAULT_MCP_URL = os.environ.get(
    "MCP_BUILDER_URL",
    "https://mcp-builder-827217685406.southamerica-east1.run.app/mcp",
)

CREDENTIAL_DIR = Path(os.environ.get("MCP_CREDENTIAL_DIR", Path.home() / ".mcp-builder"))
CREDENTIALS_FILE = CREDENTIAL_DIR / "credentials.json"
TOKEN_FILE = CREDENTIAL_DIR / "token.json"

# These are for a "Desktop app" OAuth client created in Google Cloud Console.
# The client_secret for desktop apps is NOT truly secret (distributed with the app).
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email",
          "https://www.googleapis.com/auth/userinfo.profile"]


# ── Credential management ───────────────────────────────────────────────────

def _ensure_credential_dir():
    CREDENTIAL_DIR.mkdir(parents=True, exist_ok=True)
    try:
        CREDENTIAL_DIR.chmod(0o700)
    except OSError:
        pass  # Windows may not support Unix permissions


def _save_json(path: Path, data: dict):
    _ensure_credential_dir()
    path.write_text(json.dumps(data), encoding="utf-8")
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0600
    except OSError:
        pass


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def google_oauth_flow() -> dict:
    """Run the Google OAuth browser flow and return credential data.

    Returns dict with 'id_token' and 'refresh_token'.
    """
    if not GOOGLE_CLIENT_ID:
        logger.error("GOOGLE_CLIENT_ID not set. Set it as an environment variable.")
        sys.exit(1)

    client_config = {
        "installed": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

    return {
        "id_token": creds.token,  # Access token; we'll also get ID token from token response
        "refresh_token": creds.refresh_token,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "token_uri": "https://oauth2.googleapis.com/token",
    }


def refresh_google_id_token(cred_data: dict) -> str:
    """Use the refresh token to get a fresh Google ID token."""
    resp = httpx.post(
        cred_data["token_uri"],
        data={
            "client_id": cred_data["client_id"],
            "client_secret": cred_data["client_secret"],
            "refresh_token": cred_data["refresh_token"],
            "grant_type": "refresh_token",
        },
    )
    resp.raise_for_status()
    token_data = resp.json()
    return token_data["id_token"]


def exchange_for_project_jwt(google_id_token: str, mcp_url: str) -> dict:
    """Call the /auth/token-exchange endpoint to get a project JWT."""
    # Derive the exchange URL from the MCP URL
    base_url = mcp_url.rsplit("/mcp", 1)[0]
    exchange_url = f"{base_url}/auth/token-exchange"

    resp = httpx.post(
        exchange_url,
        json={"google_id_token": google_id_token},
        timeout=30,
    )
    if resp.status_code == 403:
        logger.error("Access denied: %s", resp.json().get("error", "Unknown"))
        sys.exit(1)
    resp.raise_for_status()
    return resp.json()


def get_valid_jwt(mcp_url: str) -> str:
    """Get a valid project JWT, refreshing if necessary."""
    # Check cached token
    token_data = _load_json(TOKEN_FILE)
    if token_data:
        expires_at = token_data.get("expires_at", 0)
        if time.time() < expires_at - 300:  # 5 min buffer
            return token_data["access_token"]
        logger.info("JWT expired or expiring soon, refreshing...")

    # Try to refresh using cached Google credentials
    cred_data = _load_json(CREDENTIALS_FILE)
    if cred_data and cred_data.get("refresh_token"):
        try:
            google_id_token = refresh_google_id_token(cred_data)
            jwt_response = exchange_for_project_jwt(google_id_token, mcp_url)
            _save_json(TOKEN_FILE, {
                "access_token": jwt_response["access_token"],
                "expires_at": time.time() + jwt_response.get("expires_in", 3600),
            })
            return jwt_response["access_token"]
        except Exception as exc:
            logger.warning("Refresh failed (%s), starting new OAuth flow...", exc)

    # No cached creds or refresh failed — full OAuth flow
    logger.info("Starting Google OAuth flow (browser will open)...")
    cred_data = google_oauth_flow()
    _save_json(CREDENTIALS_FILE, cred_data)

    # Get an ID token via refresh (the initial flow gives us an access token)
    google_id_token = refresh_google_id_token(cred_data)

    # Exchange for project JWT
    jwt_response = exchange_for_project_jwt(google_id_token, mcp_url)
    _save_json(TOKEN_FILE, {
        "access_token": jwt_response["access_token"],
        "expires_at": time.time() + jwt_response.get("expires_in", 3600),
    })
    return jwt_response["access_token"]


# ── stdio ↔ HTTP MCP Proxy ──────────────────────────────────────────────────

def run_stdio_proxy(mcp_url: str):
    """Read JSON-RPC from stdin, forward to remote MCP via HTTP, write responses to stdout."""
    import asyncio

    async def _proxy():
        jwt_token = get_valid_jwt(mcp_url)

        async with httpx.AsyncClient(timeout=120) as client:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue

                # Refresh JWT if needed before each request
                jwt_token = get_valid_jwt(mcp_url)

                try:
                    request_body = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON on stdin, skipping")
                    continue

                try:
                    resp = await client.post(
                        mcp_url,
                        json=request_body,
                        headers={
                            "Authorization": f"Bearer {jwt_token}",
                            "Content-Type": "application/json",
                            "Accept": "application/json, text/event-stream",
                        },
                    )
                    resp.raise_for_status()

                    # Write the response to stdout for Claude Code to consume
                    content_type = resp.headers.get("content-type", "")
                    if "text/event-stream" in content_type:
                        # SSE response — extract data lines
                        for sse_line in resp.text.splitlines():
                            if sse_line.startswith("data: "):
                                data = sse_line[6:]
                                sys.stdout.write(data + "\n")
                                sys.stdout.flush()
                    else:
                        sys.stdout.write(resp.text + "\n")
                        sys.stdout.flush()

                except httpx.HTTPStatusError as exc:
                    logger.error("MCP request failed: %s %s", exc.response.status_code, exc.response.text)
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request_body.get("id"),
                        "error": {"code": -32000, "message": f"Remote MCP error: {exc.response.status_code}"},
                    }
                    sys.stdout.write(json.dumps(error_response) + "\n")
                    sys.stdout.flush()
                except Exception as exc:
                    logger.error("Unexpected error: %s", exc)

    asyncio.run(_proxy())


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MCP Auth Proxy — Google OAuth to MCP stdio bridge")
    parser.add_argument(
        "--target",
        default=DEFAULT_MCP_URL,
        help="Target MCP server URL (default: MCP_BUILDER_URL env or built-in)",
    )
    parser.add_argument(
        "--credential-dir",
        default=None,
        help="Directory to store credentials (default: ~/.mcp-builder/)",
    )
    parser.add_argument(
        "--login-only",
        action="store_true",
        help="Only authenticate (open browser), don't start the proxy",
    )
    args = parser.parse_args()

    if args.credential_dir:
        global CREDENTIAL_DIR, CREDENTIALS_FILE, TOKEN_FILE
        CREDENTIAL_DIR = Path(args.credential_dir)
        CREDENTIALS_FILE = CREDENTIAL_DIR / "credentials.json"
        TOKEN_FILE = CREDENTIAL_DIR / "token.json"

    if args.login_only:
        jwt_token = get_valid_jwt(args.target)
        logger.info("Authentication successful! JWT cached at %s", TOKEN_FILE)
        return

    run_stdio_proxy(args.target)


if __name__ == "__main__":
    main()
