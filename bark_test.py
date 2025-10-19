#!/usr/bin/env python3
"""
bark_test.py

A small test script to send Bark notifications to an iPhone.

Usage examples:
  # from environment (.env supported)
  BARK_KEY=your_device_key python bark_test.py --title "Hi" --body "Hello from test"

  # explicit key and dry-run (no network)
  python bark_test.py --key YOUR_DEVICE_KEY --title Test --body Hello --dry-run

This script supports the following query params supported by Bark: icon, sound, copy, url.
"""
from __future__ import annotations

import argparse
import os
import sys
from urllib.parse import quote_plus

import requests

try:
    # optional dotenv support if user has python-dotenv installed and a .env file
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # Not required; ignore if dotenv isn't available
    pass


def build_bark_url(device_key: str, title: str, body: str, params: dict[str, str] | None = None) -> str:
    title_q = quote_plus(title or "")
    body_q = quote_plus(body or "")
    base = f"https://api.day.app/{device_key}/{title_q}/{body_q}"
    if not params:
        return base
    # build query string for optional params
    pairs = []
    for k, v in params.items():
        if v is None or v == "":
            continue
        pairs.append(f"{quote_plus(k)}={quote_plus(v)}")
    if not pairs:
        return base
    return base + "?" + "&".join(pairs)


def send_bark(device_key: str, title: str, body: str, params: dict[str, str] | None = None, timeout: int = 10) -> tuple[int, str]:
    url = build_bark_url(device_key, title, body, params)
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code, r.text
    except requests.RequestException as e:
        return 0, str(e)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Send a Bark push notification to an iPhone for testing.")
    p.add_argument("--key", "-k", help="Bark device key (overrides BARK_KEY env var)")
    p.add_argument("--title", "-t", default="Test", help="Notification title")
    p.add_argument("--body", "-b", default="This is a test notification", help="Notification body")
    p.add_argument("--icon", help="Icon emoji or name (optional)")
    p.add_argument("--sound", help="Sound name (optional)")
    p.add_argument("--copy", help="Text to copy to clipboard on iPhone (optional)")
    p.add_argument("--url", help="Open URL when tapping the notification (optional)")
    p.add_argument("--dry-run", action="store_true", help="Show the Bark URL and do not send network request")
    p.add_argument("--timeout", type=int, default=10, help="HTTP timeout in seconds")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    device_key = args.key or os.getenv("BARK_KEY") or os.getenv("BARK_DEVICE_KEY")
    if not device_key:
        print("Error: Bark device key not provided. Set BARK_KEY env var or use --key.")
        return 2

    params: dict[str, str] = {}
    if args.icon:
        params["icon"] = args.icon
    if args.sound:
        params["sound"] = args.sound
    if args.copy:
        params["copy"] = args.copy
    if args.url:
        params["url"] = args.url

    url = build_bark_url(device_key, args.title, args.body, params)

    if args.dry_run:
        print("Dry run - Bark URL:\n", url)
        print("To actually send, re-run without --dry-run or pass a real device key.")
        return 0

    print("Sending Bark notification to device key:", device_key)
    status, text = send_bark(device_key, args.title, args.body, params, timeout=args.timeout)
    if status == 200:
        print("Success: HTTP 200")
        return 0
    if status == 0:
        print("Network error:", text)
        return 3
    print(f"Failed: HTTP {status}\nResponse body:\n{text}")
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
