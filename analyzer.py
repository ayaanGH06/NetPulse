"""
analyzer.py — Network Analytics
Analyzes download data from data.json and writes summary.json + report.txt.
"""

import json
import logging
from urllib.parse import urlparse
from datetime import datetime

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

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
try:
    with open("data.json", "r") as f:
        data = json.load(f)
    log.info(f"Loaded {len(data)} records from data.json")
except FileNotFoundError:
    log.error("data.json not found — run downloader.py first.")
    raise
except json.JSONDecodeError as e:
    log.error(f"Malformed data.json: {e}")
    raise

# ── PROCESS RECORDS ───────────────────────────────────────────────────────────
speeds       = []
total_data   = 0
failed_count = 0
detailed     = []
domains      = {}
time_buckets = {}

for entry in data:
    domain = urlparse(entry["url"]).netloc
    domains[domain] = domains.get(domain, 0) + 1

    if entry.get("status") == "failed":
        failed_count += 1
        log.warning(f"Failed download in record: {entry['url']}")
        continue

    size  = entry["size"]
    start = entry["start_time"]
    end   = entry["end_time"]

    time_taken = max(end - start, 0.0001)
    speed_MBps = (size / time_taken) / (1024 * 1024)

    speeds.append(speed_MBps)
    total_data += size

    time_key = datetime.fromtimestamp(start).strftime("%H:%M")
    time_buckets.setdefault(time_key, []).append(speed_MBps)

    detailed.append({
        "url":        entry["url"],
        "speed_MBps": round(speed_MBps, 2),
        "time":       time_key,
    })

log.info(f"Processed {len(speeds)} successful / {failed_count} failed downloads")

# ── STATISTICS ────────────────────────────────────────────────────────────────
if speeds:
    avg_speed = sum(speeds) / len(speeds)
    max_speed = max(speeds)
    min_speed = min(speeds)
else:
    avg_speed = max_speed = min_speed = 0
    log.warning("No successful downloads found — all stats will be zero.")

fast = medium = slow = 0
for s in speeds:
    if   s > 2: fast   += 1
    elif s > 1: medium += 1
    else:       slow   += 1

stability = "Unstable" if (max_speed - min_speed) > 2 else "Stable"

trend = (
    "Improving"  if len(speeds) >= 2 and speeds[-1] > speeds[0]
    else "Degrading" if len(speeds) >= 2
    else "Insufficient data"
)

# ── TIME ANALYSIS ─────────────────────────────────────────────────────────────
time_analysis = {
    hour: round(sum(vals) / len(vals), 2)
    for hour, vals in sorted(time_buckets.items())
}

congestion_hours = [
    hour for hour, avg in time_analysis.items()
    if avg_speed and avg < avg_speed * 0.7
]

if congestion_hours:
    log.warning(f"Congestion detected at: {', '.join(congestion_hours)}")

# ── EXTRAS ────────────────────────────────────────────────────────────────────
slowest_download = min(detailed, key=lambda x: x["speed_MBps"]) if detailed else None
efficiency_score = (avg_speed / max_speed * 100) if max_speed > 0 else 0

busiest_hour = max(time_analysis, key=lambda h: time_analysis.get(h, 0.0)) if time_analysis else None
slowest_hour = min(time_analysis, key=lambda h: time_analysis.get(h, 0.0)) if time_analysis else None

if busiest_hour:
    log.info(f"Busiest hour (peak speed): {busiest_hour} @ {time_analysis[busiest_hour]} MB/s")
    log.info(f"Slowest hour: {slowest_hour} @ {time_analysis[slowest_hour]} MB/s")

# ── SUMMARY ───────────────────────────────────────────────────────────────────
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

summary = {
    "average_speed_MBps":  round(avg_speed, 2),
    "max_speed_MBps":      round(max_speed, 2),
    "min_speed_MBps":      round(min_speed, 2),
    "total_data_MB":       round(total_data / (1024 * 1024), 2),
    "total_downloads":     len(speeds),
    "failed_downloads":    failed_count,
    "network_stability":   stability,
    "trend":               trend,
    "efficiency_score":    round(efficiency_score, 2),
    "slowest_download":    slowest_download,
    "busiest_hour":        busiest_hour,
    "slowest_hour":        slowest_hour,
    "speed_distribution":  {"fast": fast, "medium": medium, "slow": slow},
    "domain_usage":        domains,
    "time_analysis":       time_analysis,
    "congestion_hours":    congestion_hours,
    "detailed_downloads":  detailed,
    "last_updated":        now,
}

with open("summary.json", "w") as f:
    json.dump(summary, f, indent=4)

log.info("summary.json saved.")

# ── WRITTEN REPORT ────────────────────────────────────────────────────────────
lines = [
    "=" * 56,
    "  NETPULSE — NETWORK ANALYTICS REPORT",
    f"  Generated : {now}",
    "=" * 56,
    "",
    "OVERVIEW",
    f"  Average speed    : {summary['average_speed_MBps']} MB/s",
    f"  Peak speed       : {summary['max_speed_MBps']} MB/s",
    f"  Minimum speed    : {summary['min_speed_MBps']} MB/s",
    f"  Total data       : {summary['total_data_MB']} MB",
    f"  Successful DLs   : {summary['total_downloads']}",
    f"  Failed DLs       : {summary['failed_downloads']}",
    f"  Efficiency score : {summary['efficiency_score']}%",
    "",
    "NETWORK HEALTH",
    f"  Stability        : {stability}",
    f"  Speed trend      : {trend}",
    "",
    "HOURLY BREAKDOWN",
]

for hour, avg in time_analysis.items():
    marker = " << PEAK"    if hour == busiest_hour else \
             " << SLOWEST" if hour == slowest_hour else ""
    bar = "█" * max(1, int(avg * 10))
    lines.append(f"  {hour}  {bar:<30s}  {avg:.2f} MB/s{marker}")

lines += [
    "",
    "BUSIEST HOUR ANALYSIS",
]
if busiest_hour:
    peak_val = time_analysis[busiest_hour]
    lines += [
        f"  Busiest hour     : {busiest_hour} ({peak_val} MB/s)",
        f"  This hour recorded the highest average throughput.",
        f"  Possible causes  : low concurrent network usage, optimal",
        f"  server response, or favourable routing conditions.",
    ]
else:
    lines.append("  Insufficient data to determine busiest hour.")

lines += ["", "CONGESTION ANALYSIS"]
if congestion_hours:
    lines.append(f"  Congestion at    : {', '.join(congestion_hours)}")
    lines.append(f"  These hours fell below 70% of the session average.")
else:
    lines.append("  No congestion detected during this session.")

if slowest_download:
    lines += [
        "",
        "BOTTLENECK",
        f"  Slowest download : {slowest_download['url']}",
        f"  Speed            : {slowest_download['speed_MBps']} MB/s at {slowest_download['time']}",
    ]

lines += [
    "",
    "SPEED DISTRIBUTION",
    f"  Fast   (>2 MB/s) : {fast} downloads",
    f"  Medium (1-2 MB/s): {medium} downloads",
    f"  Slow   (<1 MB/s) : {slow} downloads",
    "",
    "=" * 56,
]

with open("report.txt", "w") as f:
    f.write("\n".join(lines))

log.info("Report written to report.txt")