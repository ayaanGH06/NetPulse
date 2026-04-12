# NetPulse — Network Download Analyzer

NetPulse is a Python-based network analytics tool that monitors download performance over time and provides insights into network congestion, stability, and throughput patterns.

It performs scheduled downloads, analyzes speed trends, and visualizes results through a **fully real-time Flask + Socket.IO dashboard** that updates live without any page refresh.

---

## Features

- Scheduled automated downloads
- Throughput measurement and logging
- Network performance analysis (trend, congestion, stability)
- Domain-level usage insights
- Speed distribution tracking
- **Real-time dashboard via WebSockets (Flask-SocketIO + gevent)**
- **Live updates for KPIs, charts, congestion alerts, download log, and bottleneck detection**

---

## Project Structure

```
.
├── downloader.py     # Handles concurrent downloads
├── analyzer.py       # Processes data + generates summary/report
├── scheduler.py      # Runs downloads periodically
├── app.py            # Flask + Socket.IO dashboard server
├── data.json         # Raw collected data
├── summary.json      # Processed analytics
├── report.txt        # Human-readable report
├── netpulse.log      # Logs
├── templates/
│   └── index.html    # Real-time dashboard UI (Chart.js + Socket.IO client)
```

---

## Requirements

- Python 3.9+
- pip

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ayaanGH06/NetPulse.git
cd netpulse
```

### 2. Install dependencies

#### Mac / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## How to Run

### Step 1: Start the dashboard server first

```bash
python app.py
```

The server runs at `http://127.0.0.1:5001`. Open it in your browser before starting the scheduler.

> **Note:** Port 5001 is used instead of 5000 because macOS reserves port 5000 for AirPlay Receiver.

---

### Step 2: Start the scheduler in a new terminal

```bash
python scheduler.py
```

This will:
- Clear any previous session data
- Run downloads every 10 seconds (demo mode)
- Analyze results and update `summary.json` after each run
- Trigger a live push to the dashboard automatically

> By default, the scheduler runs 5 times with 10-second intervals (demo mode).
> For real 24-hour tracking, set `TOTAL_RUNS = 24` and `INTERVAL = 3600` in `scheduler.py`.

---

### Step 3: Watch the dashboard update live

Go to:

```
http://127.0.0.1:5001
```

Every time the scheduler completes a run, the entire dashboard updates in real time — no refresh needed.

---

## How It Works

1. `scheduler.py` triggers downloads at set intervals
2. `downloader.py` fetches URLs concurrently using threads
3. Results are stored in `data.json`
4. `analyzer.py` processes the data and writes `summary.json`
5. `app.py` watches `summary.json` for changes using `os.path.getmtime`
6. On change, `app.py` emits a `summary_update` event via Socket.IO
7. `index.html` receives the event and updates all dashboard elements live

---

## Real-Time Architecture

```
scheduler.py
  → runs downloader + analyzer every 10s

analyzer.py
  → writes updated summary.json

app.py (gevent + Flask-SocketIO)
  → watches summary.json every 1s via os.path.getmtime
  → detects file change → emits "summary_update" to all connected browsers

index.html
  → socket.on("summary_update") updates:
     - KPI scorecards
     - Throughput over time chart
     - Speed distribution doughnut
     - Congestion alert
     - Download log table
     - Bottleneck detection callout
     - Timestamp + live indicator
```

---

## Output Files

- `data.json` → raw download logs
- `summary.json` → processed analytics
- `report.txt` → human-readable report
- `netpulse.log` → execution logs

---

## Notes

- Start `app.py` before `scheduler.py` so the socket server is ready
- `templates/index.html` must exist or Flask will not render the dashboard
- Internet connection is required for downloads
- One test URL (`invalid-url-test-123.com`) intentionally fails to simulate error handling
- Uses `gevent` as the async backend for Socket.IO — required for proper WebSocket support on Werkzeug

---

## Future Improvements

- Configurable URL list via UI
- Export analytics (CSV / graphs)
- Deployment (Docker / cloud)
- Historical session comparison
- Email/webhook alerts on congestion detection

---

## Author

Built as a Computer Networks project
- Syed Ayaan Hasan
- Syed Obaid Faraz
- Suryatej V