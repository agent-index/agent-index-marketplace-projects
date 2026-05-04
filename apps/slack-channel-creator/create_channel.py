#!/usr/bin/env python3
"""
Slack Channel Creator — creates a channel and optionally invites members.

Acts on behalf of the individual user whose token is provided. Each member
stores their own Slack user token (xoxp-), so channels are created as that
person — not as a shared bot.

Usage:
    python create_channel.py \
        --name "project-rebrand-2026" \
        --token-file /path/to/slack-user-token.txt \
        [--topic "Project channel for Rebrand 2026"] \
        [--purpose "Coordination channel for the Rebrand 2026 project"] \
        [--invite user1@example.com,user2@example.com] \
        [--is-private] \
        [--dry-run]

Token requirements:
    Slack user token (xoxp-) with these scopes:
      channels:write    — create public channels
      channels:manage   — set topic/purpose
      groups:write      — create private channels (if --is-private)
      users:read.email  — look up members by email for invites

Exit codes:
    0 — success (channel created, invites sent)
    1 — channel creation failed
    2 — channel created but one or more invites failed
    3 — invalid arguments or missing token

Output:
    JSON to stdout with the result:
    {
        "ok": true,
        "channel_id": "C07XXXXXX",
        "channel_name": "project-rebrand-2026",
        "invites": {
            "succeeded": ["U01AAA", "U01BBB"],
            "failed": [{"email": "unknown@example.com", "error": "user_not_found"}]
        }
    }
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import urllib.parse


def slack_api(method, token, params=None):
    """Call a Slack Web API method. Returns parsed JSON response."""
    url = f"https://slack.com/api/{method}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    data = json.dumps(params or {}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"ok": False, "error": f"http_{e.code}", "detail": body}
    except urllib.error.URLError as e:
        return {"ok": False, "error": "network_error", "detail": str(e.reason)}


def lookup_users_by_email(token, emails):
    """Resolve a list of email addresses to Slack user IDs.

    Returns:
        found: dict of email -> user_id
        not_found: list of emails that couldn't be resolved
    """
    found = {}
    not_found = []
    for email in emails:
        email = email.strip()
        if not email:
            continue
        resp = slack_api("users.lookupByEmail", token, {"email": email})
        if resp.get("ok") and resp.get("user", {}).get("id"):
            found[email] = resp["user"]["id"]
        else:
            not_found.append(email)
    return found, not_found


def create_channel(token, name, is_private=False):
    """Create a Slack channel. Returns the API response."""
    return slack_api("conversations.create", token, {
        "name": name,
        "is_private": is_private,
    })


def set_channel_topic(token, channel_id, topic):
    """Set the channel topic."""
    return slack_api("conversations.setTopic", token, {
        "channel": channel_id,
        "topic": topic,
    })


def set_channel_purpose(token, channel_id, purpose):
    """Set the channel purpose."""
    return slack_api("conversations.setPurpose", token, {
        "channel": channel_id,
        "purpose": purpose,
    })


def invite_users(token, channel_id, user_ids):
    """Invite users to a channel one at a time.

    Returns:
        succeeded: list of user_ids successfully invited
        failed: list of dicts with user_id and error
    """
    succeeded = []
    failed = []
    for uid in user_ids:
        resp = slack_api("conversations.invite", token, {
            "channel": channel_id,
            "users": uid,
        })
        if resp.get("ok"):
            succeeded.append(uid)
        elif resp.get("error") == "already_in_channel":
            succeeded.append(uid)
        else:
            failed.append({"user_id": uid, "error": resp.get("error", "unknown")})
    return succeeded, failed


def main():
    parser = argparse.ArgumentParser(description="Create a Slack channel and invite members")
    parser.add_argument("--name", required=True, help="Channel name (lowercase, hyphens, no spaces)")
    parser.add_argument("--token-file", required=True, help="Path to file containing Slack user token (xoxp-)")
    parser.add_argument("--topic", default="", help="Channel topic")
    parser.add_argument("--purpose", default="", help="Channel purpose/description")
    parser.add_argument("--invite", default="", help="Comma-separated list of email addresses to invite")
    parser.add_argument("--is-private", action="store_true", help="Create as a private channel")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done without doing it")
    args = parser.parse_args()

    # Normalize channel name
    channel_name = args.name.lstrip("#").lower().replace(" ", "-")

    # Read token
    try:
        with open(args.token_file, "r") as f:
            token = f.read().strip()
    except FileNotFoundError:
        result = {"ok": False, "error": "token_file_not_found", "detail": args.token_file}
        print(json.dumps(result, indent=2))
        sys.exit(3)

    if not token or not (token.startswith("xoxp-") or token.startswith("xoxb-")):
        result = {"ok": False, "error": "invalid_token", "detail": "Token must start with xoxp- (user token) or xoxb- (bot token)"}
        print(json.dumps(result, indent=2))
        sys.exit(3)

    # Parse invite list
    invite_emails = [e.strip() for e in args.invite.split(",") if e.strip()] if args.invite else []

    if args.dry_run:
        result = {
            "dry_run": True,
            "would_create": channel_name,
            "is_private": args.is_private,
            "topic": args.topic or "(none)",
            "purpose": args.purpose or "(none)",
            "would_invite": invite_emails or "(none)",
        }
        print(json.dumps(result, indent=2))
        sys.exit(0)

    # Create channel
    create_resp = create_channel(token, channel_name, is_private=args.is_private)

    if not create_resp.get("ok"):
        # If channel already exists, try to get its ID
        if create_resp.get("error") == "name_taken":
            result = {"ok": False, "error": "name_taken", "channel_name": channel_name,
                      "detail": "A channel with this name already exists"}
            print(json.dumps(result, indent=2))
            sys.exit(1)
        else:
            result = {"ok": False, "error": create_resp.get("error", "unknown"),
                      "detail": create_resp.get("detail", "")}
            print(json.dumps(result, indent=2))
            sys.exit(1)

    channel_id = create_resp["channel"]["id"]
    channel_name = create_resp["channel"]["name"]

    # Set topic and purpose
    if args.topic:
        set_channel_topic(token, channel_id, args.topic)
    if args.purpose:
        set_channel_purpose(token, channel_id, args.purpose)

    # Invite members
    invite_result = {"succeeded": [], "failed": []}
    if invite_emails:
        found, not_found = lookup_users_by_email(token, invite_emails)
        for email in not_found:
            invite_result["failed"].append({"email": email, "error": "user_not_found"})

        if found:
            succeeded, failed = invite_users(token, channel_id, list(found.values()))
            # Map user IDs back to emails for the result
            uid_to_email = {uid: email for email, uid in found.items()}
            invite_result["succeeded"] = [uid_to_email.get(uid, uid) for uid in succeeded]
            for f in failed:
                invite_result["failed"].append({
                    "email": uid_to_email.get(f["user_id"], f["user_id"]),
                    "error": f["error"],
                })

    result = {
        "ok": True,
        "channel_id": channel_id,
        "channel_name": channel_name,
        "invites": invite_result,
    }
    print(json.dumps(result, indent=2))

    if invite_result["failed"]:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
