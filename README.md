# NetPulse — Network Download Analyzer 

NetPulse is a Python-based network analytics tool that monitors download performance over time and provides insights into network congestion, stability, and throughput patterns.

It performs scheduled downloads, analyzes speed trends, and visualizes results through a Flask dashboard.

---

##  Features

*  Scheduled automated downloads
*  Throughput measurement and logging
*  Network performance analysis (trend, congestion, stability)
*  Domain-level usage insights
*  Speed distribution tracking
*  Interactive dashboard (Flask + Chart.js)

---

##  Project Structure

```
.
├── downloader.py     # Handles concurrent downloads
├── analyzer.py       # Processes data + generates summary/report
├── scheduler.py      # Runs downloads periodically
├── app.py            # Flask dashboard server
├── data.json         # Raw collected data
├── summary.json      # Processed analytics
├── report.txt        # Human-readable report
├── netpulse.log      # Logs
├── templates/
│   └── index.html    # Dashboard UI
```

---

##  Requirements

* Python 3.9+
* pip

---

##  Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd netpulse
```

---

## 🖥️ Setup Instructions

###  Mac / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

###  Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## ▶ How to Run

### Step 1: Start the scheduler

This will:

* Run downloads periodically
* Generate `data.json`
* Analyze and update `summary.json`

```bash
python scheduler.py
```

> By default, the scheduler runs 5 times with short intervals (demo mode).
> You can modify `TOTAL_RUNS` and `INTERVAL` in `scheduler.py`  for real 24-hour tracking.

---

### Step 2: Start the dashboard

In a new terminal (keep scheduler running):

```bash
python app.py
```

---

### Step 3: Open the dashboard

Go to:

```
http://localhost:5000
```

---

##  Output Files

* `data.json` → raw download logs 
* `summary.json` → processed analytics 
* `report.txt` → readable report 
* `netpulse.log` → execution logs 

---

##  How It Works

1. `scheduler.py` triggers downloads at intervals
2. `downloader.py` fetches URLs concurrently 
3. Results are stored in `data.json`
4. `analyzer.py` processes the data and generates insights 
5. `app.py` serves a dashboard using the processed data 

---

##  Notes

* Ensure `templates/index.html` exists or Flask UI won’t render properly 
* Internet connection is required for downloads
* One test URL intentionally fails to simulate errors

---

##  Future Improvements

* Real-time updates via WebSockets
* Configurable URL list
* Export analytics (CSV / graphs)
* Deployment (Docker / cloud)

---

##  Author

Built as a Computer Networks project 
