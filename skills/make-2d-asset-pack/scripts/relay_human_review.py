#!/usr/bin/env python3
"""Relay an owner's explicit chat decision to the local human-review server."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default="http://127.0.0.1:4177")
    parser.add_argument("--family", required=True)
    parser.add_argument("--decision", choices=("approve", "reject"), required=True)
    parser.add_argument("--comment", default="")
    parser.add_argument("--user-text", required=True, help="The owner's exact approval or rejection message")
    args = parser.parse_args()
    parsed = urllib.parse.urlparse(args.server)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("human_review_server_must_be_local")
    origin = f"{parsed.scheme}://{parsed.netloc}"
    payload = json.dumps(
        {
            "familyId": args.family,
            "decision": args.decision,
            "comment": args.comment,
            "source": "chat",
            "userText": args.user_text,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{origin}/api/review",
        data=payload,
        headers={"Content-Type": "application/json", "Origin": origin},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            result = json.loads(response.read())
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"human_review_relay_failed:{error.code}:{detail}") from error
    print(f"family:{args.family}")
    print(f"decision:{args.decision}")
    print(f"status:{result['status']}")


if __name__ == "__main__":
    main()
