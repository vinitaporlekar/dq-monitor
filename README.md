# dq-monitor

A simple data quality monitor. Checks row counts and null rates against a historical baseline and alerts on anomalies.

## Run it

    pip install -r requirements.txt
    python setup_data.py
    python monitor.py

Run monitor.py several times to build a baseline. Then change setup_data.py (raise the null probability to 0.30) and re-run to trigger an anomaly alert.