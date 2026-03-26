"""
app.py — NetPulse Flask server
Serves the network analytics dashboard at http://localhost:5000
"""

import json
import logging
from flask import Flask, render_template, jsonify

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

app = Flask(__name__)


def load_summary() -> dict:
    """Load summary.json; return empty dict with defaults on failure."""
    defaults = {
        "average_speed_MBps": 0,
        "max_speed_MBps":     0,
        "min_speed_MBps":     0,
        "total_data_MB":      0,
        "total_downloads":    0,
        "failed_downloads":   0,
        "network_stability":  "No data",
        "trend":              "No data",
        "efficiency_score":   0,
        "slowest_download":   None,
        "busiest_hour":       None,
        "slowest_hour":       None,
        "speed_distribution": {"fast": 0, "medium": 0, "slow": 0},
        "domain_usage":       {},
        "time_analysis":      {},
        "congestion_hours":   [],
        "detailed_downloads": [],
        "last_updated":       None,
    }
    try:
        with open("summary.json") as f:
            data = json.load(f)
        defaults.update(data)   # merge so missing keys get defaults
        return defaults
    except FileNotFoundError:
        log.warning("summary.json not found — serving empty dashboard.")
        return defaults
    except json.JSONDecodeError as e:
        log.error(f"Malformed summary.json: {e}")
        return defaults


@app.route("/")
def index():
    summary = load_summary()
    table   = summary.get("detailed_downloads", [])
    return render_template("index.html", summary=summary, table=table)


@app.route("/api/summary")
def api_summary():
    """JSON endpoint — useful for live polling from the frontend."""
    return jsonify(load_summary())


if __name__ == "__main__":
    log.info("Starting NetPulse dashboard at http://localhost:5000")
    app.run(debug=True)