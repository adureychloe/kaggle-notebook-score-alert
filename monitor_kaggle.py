"""
Kaggle Notebook Score Monitor

This script monitors the Kaggle competition "Code" page for new notebooks with higher leaderboard scores
and sends a notification via Bark when a higher score is detected.

Usage:
    python monitor_kaggle.py --competition hull-tactical-market-prediction --bark YOUR_BARK_KEY

Notes:
- This script scrapes the Kaggle competition code page and looks for notebook entries with scores.
- Kaggle page structure may change; this is a best-effort scraper.

"""

import argparse
import csv
import io
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Tuple
import requests
from dotenv import load_dotenv


STATE_DEFAULT = "kaggle_monitor_state.json"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"


@dataclass
class NotebookInfo:
    title: str
    author: str
    score: Optional[float]
    url: str


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--competition", required=True, help="Kaggle competition slug (e.g. hull-tactical-market-prediction)")
    p.add_argument("--bark", help="Bark key or full URL (e.g. https://api.day.app/<key>/)")
    p.add_argument("--interval", type=int, default=300, help="Polling interval in seconds (default 300)")
    p.add_argument("--state", default=STATE_DEFAULT, help="Path to JSON state file")
    p.add_argument("--once", action="store_true", help="Run once and exit (don't monitor continuously)")
    return p.parse_args()


def load_state(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_state(path: str, data: dict):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def get_notebooks(competition: str) -> List[NotebookInfo]:
    result = subprocess.run(
        ['kaggle', 'kernels', 'list', '--competition', competition, '--sort-by', 'scoreDescending', '--page-size', '3','--csv'],
        capture_output=True, text=True, encoding='utf-8'
    )
    if result.returncode != 0:
        print("Error running kaggle CLI:", result.stderr)
        return []

    reader = csv.DictReader(io.StringIO(result.stdout))
    notebooks = []
    for row in reader:
        ref = row.get('ref', '')
        title = row.get('title', '')
        author = row.get('author', '')
        url = f"https://www.kaggle.com{ref}" if ref else ""
        # No score available in CSV
        notebooks.append(NotebookInfo(title=title, author=author, score=None, url=url))
    return notebooks


def best_notebook(notebooks: List[NotebookInfo]) -> Optional[NotebookInfo]:
    # Since no score available, consider the first (top sorted) as best
    if notebooks:
        return notebooks[0]
    return None


def send_bark(bark: str, title: str, body: str):
    if not bark:
        print("Bark key not provided; skipping notification")
        return
    # Accept either a full URL like https://api.day.app/<key>/ or a key string
    if bark.startswith("http"):
        url = bark.rstrip("/") + "/"
    else:
        url = f"https://api.day.app/{bark}/"
    # build message endpoint: https://api.day.app/{key}/{title}/{body}
    import urllib.parse
    path_title = urllib.parse.quote(title, safe="")
    path_body = urllib.parse.quote(body, safe="")
    send_url = f"{url}{path_title}/{path_body}"
    try:
        r = requests.get(send_url, timeout=10)
        print("Bark response:", r.status_code, r.text[:200])
    except Exception as e:
        print("Failed to send Bark notification:", e)


def monitor_once(competition: str, bark: Optional[str], state_path: str) -> Tuple[bool, Optional[NotebookInfo]]:
    print("Fetching notebooks via Kaggle API")
    notebooks = get_notebooks(competition)
    print(f"Found {len(notebooks)} candidate notebooks")
    best = best_notebook(notebooks)
    state = load_state(state_path)
    prev_url = state.get("best_url")

    if best is None:
        print("No notebooks found.")
        return False, None

    print(f"Best found: {best.title} by {best.author} url={best.url}")

    if prev_url is None or best.url != prev_url:
        print(f"New top notebook: {best.title}")
        state["best_score"] = None  # No score available
        state["best_url"] = best.url
        state["updated_at"] = datetime.utcnow().isoformat()
        save_state(state_path, state)
        # send bark
        title = f"New Top Kaggle Notebook"
        body = f"{best.title} by {best.author}\n{best.url}"
        send_bark(bark or "", title, body)
        return True, best

    print("No change detected.")
    return False, best


def main():
    args = parse_args()
    load_dotenv()
    bark = args.bark or os.getenv("BARK_KEY")
    state_path = args.state

    if args.once:
        monitor_once(args.competition, bark, state_path)
        return

    while True:
        try:
            changed, best = monitor_once(args.competition, bark, state_path)
        except Exception as e:
            print("Error during monitoring:", e)
        if args.interval <= 0:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
