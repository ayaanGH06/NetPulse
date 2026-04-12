"""
scheduler.py — NetPulse Scheduler
Runs downloader + analyzer every hour for 24 hours.
"""

import time
import subprocess
import logging
from datetime import datetime
import sys
import socketio as sio_client
sys.stdout.reconfigure(encoding='utf-8')

# ── LOGGING ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("netpulse.log",  encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

TOTAL_RUNS = 5          # one run per hour over 24 hours
INTERVAL   = 10        # seconds between runs (1 hour)


# ── STARTUP CHECKS ────────────────────────────────────────────────────────────
import os

# Warn if templates folder is missing 
if not os.path.exists(os.path.join("templates", "index.html")):
    log.warning("templates/index.html not found — Flask dashboard will not render correctly.")

# Clear data.json at the start of each new monitoring session so that
# data from a previous session doesn't bleed into today's analysis.
# Each hourly run within the session still appends freely.
if os.path.exists("data.json"):
    os.remove("data.json")
    log.info("data.json cleared — starting fresh 24-hr session.")

log.info(f"NetPulse scheduler started — {TOTAL_RUNS} runs, every {INTERVAL}s")

for i in range(TOTAL_RUNS):
    run_label = f"Run {i+1}/{TOTAL_RUNS}"
    log.info("-" * 40)
    log.info(f"{run_label} — starting at {datetime.now().strftime('%H:%M:%S')}")

    result_dl = subprocess.run(["python", "downloader.py", "--run", str(i + 1)], capture_output=True, text=True)
    if result_dl.returncode != 0:
        log.error(f"downloader.py failed:\n{result_dl.stderr}")
    else:
        log.info("downloader.py completed successfully")

    result_an = subprocess.run(["python", "analyzer.py"], capture_output=True, text=True)
    if result_an.returncode != 0:
        log.error(f"analyzer.py failed:\n{result_an.stderr}")
    else:
        log.info("analyzer.py completed successfully")
        try:
            sio = sio_client.SimpleClient()
            sio.connect("http://localhost:5001", transports=["websocket"])
            sio.emit("push_update", {})
            log.info("Socket push sent successfully")
            time.sleep(1)
            sio.disconnect()
        except Exception as e:
            log.warning(f"Socket notify skipped: {e}")

    if i < TOTAL_RUNS - 1:
        next_run = datetime.fromtimestamp(time.time() + INTERVAL).strftime("%H:%M:%S")
        log.info(f"Sleeping {INTERVAL}s — next run at {next_run}")
        time.sleep(INTERVAL)

log.info("[OK] 24-hour monitoring complete.")