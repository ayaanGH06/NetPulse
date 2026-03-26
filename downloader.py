"""
downloader.py — NetPulse Downloader
Downloads a set of URLs concurrently and appends results to data.json.
"""

import requests
import time
import json
import logging
import os
import threading
from typing import Any
import argparse

# ── LOGGING ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("netpulse.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ── TARGETS ───────────────────────────────────────────────────────────────────
URLS = [
    "https://www.google.com",
    "https://www.wikipedia.org",
    "https://www.github.com",
    "https://www.bbc.com",
    "https://invalid-url-test-123.com",  # intentional failure — tests error handling
]

data: list[dict] = []
lock = threading.Lock()


def download_url(url: str) -> None:
    entry: dict[str, Any] = {"url": url}
    start = time.time()          # ← captured BEFORE try so failures record real start time
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "NetPulse/2.0"})
        content  = response.content
        end      = time.time()

        entry.update({
            "start_time": start,
            "end_time":   end,
            "timestamp":  time.strftime("%H:%M:%S"),
            "size":       len(content),
            "status":     "success",
            "http_code":  response.status_code,
        })
        log.info(f"OK   {url} | {len(content):,} bytes | {end - start:.2f}s | HTTP {response.status_code}")

    except requests.exceptions.Timeout:
        log.warning(f"TIMEOUT  {url}")
        entry.update({"start_time": start, "end_time": time.time(),
                       "timestamp": time.strftime("%H:%M:%S"), "size": 0,
                       "status": "failed", "error": "timeout"})

    except requests.exceptions.ConnectionError:
        log.warning(f"CONN ERR {url}")
        entry.update({"start_time": start, "end_time": time.time(),
                       "timestamp": time.strftime("%H:%M:%S"), "size": 0,
                       "status": "failed", "error": "connection_error"})

    except Exception as e:
        log.error(f"FAIL     {url} | {e}")
        entry.update({"start_time": start, "end_time": time.time(),
                       "timestamp": time.strftime("%H:%M:%S"), "size": 0,
                       "status": "failed", "error": str(e)})

    with lock:
        data.append(entry)


# ── ARGS ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--run", type=int, default=1, help="Run number (passed by scheduler)")
args = parser.parse_args()
RUN_NUMBER = args.run

# ── RUN THREADS ───────────────────────────────────────────────────────────────
log.info(f"Starting downloads for {len(URLS)} URLs (run #{RUN_NUMBER})")
threads = [threading.Thread(target=download_url, args=(url,)) for url in URLS]
for t in threads: t.start()
for t in threads: t.join()

# ── PERSIST ───────────────────────────────────────────────────────────────────
if os.path.exists("data.json"):
    try:
        with open("data.json", "r") as f:
            existing = json.load(f)
    except (json.JSONDecodeError, IOError):
        log.warning("Corrupt data.json — starting fresh.")
        existing = []
else:
    existing = []

# Stamp run number onto every entry before saving
for entry in data:
    entry["run_number"] = RUN_NUMBER
existing.extend(data)

with open("data.json", "w") as f:
    json.dump(existing, f, indent=2)

successes = sum(1 for d in data if d["status"] == "success")
log.info(f"Done — {successes}/{len(URLS)} succeeded. data.json updated ({len(existing)} total records).")