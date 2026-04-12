"""
app.py — NetPulse Flask server
Serves the network analytics dashboard at http://localhost:5000
"""
from gevent import monkey
monkey.patch_all()
import json
import logging
import os
import threading
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')


def load_summary() -> dict:
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
        defaults.update(data)
        return defaults
    except FileNotFoundError:
        log.warning("summary.json not found — serving empty dashboard.")
        return defaults
    except json.JSONDecodeError as e:
        log.error(f"Malformed summary.json: {e}")
        return defaults


def watch_summary():
    """Watch summary.json for changes and push to browser automatically."""
    last_modified = None
    while True:
        try:
            mtime = os.path.getmtime("summary.json")
            if last_modified is None:
                last_modified = mtime
            elif mtime != last_modified:
                last_modified = mtime
                log.info("summary.json changed — pushing update to browser")
                socketio.emit("summary_update", load_summary())
        except FileNotFoundError:
            pass
        socketio.sleep(1)


@app.route("/")
def index():
    summary = load_summary()
    table   = summary.get("detailed_downloads", [])
    return render_template("index.html", summary=summary, table=table)


@app.route("/api/summary")
def api_summary():
    return jsonify(load_summary())


@socketio.on("request_update")
def handle_update_request():
    socketio.emit("summary_update", load_summary())


@socketio.on("connect")
def handle_connect():
    log.info("Browser connected")


if __name__ == "__main__":
    log.info("Starting NetPulse dashboard at http://localhost:5001")
    socketio.start_background_task(watch_summary)
    socketio.run(app, host="127.0.0.1", port=5001, debug=False)