# dq-monitor

A simple data quality monitor. Checks row counts and null rates against a historical baseline and alerts on anomalies.

## Run it

    pip install -r requirements.txt
    python setup_data.py
    python monitor.py

Run monitor.py several times to build a baseline. Then change setup_data.py (raise the null probability to 0.30) and re-run to trigger an anomaly alert.

## Dashboard

A web dashboard visualizes metric history and current status.

Run the dashboard:

    uvicorn app:app --reload

Then open http://127.0.0.1:8000

The dashboard shows current metric values, historical charts, and highlights anomalies in red.