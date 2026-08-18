"""FastAPI web dashboard for dq-monitor."""
import statistics
import yaml
import duckdb
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="dq-monitor")
templates = Jinja2Templates(directory="templates")

with open("config.yml") as f:
    cfg = yaml.safe_load(f)


def get_metric_data():
    """Read all metrics and their history from the database."""
    con = duckdb.connect(cfg["warehouse"])

    metric_names = con.execute(
        "SELECT DISTINCT metric FROM history ORDER BY metric"
    ).fetchall()

    metrics = []
    for (name,) in metric_names:
        rows = con.execute("""
            SELECT run_at, value
            FROM history
            WHERE metric = ?
            ORDER BY run_at DESC
            LIMIT 30
        """, [name]).fetchall()

        rows = list(reversed(rows))  # oldest → newest
        if not rows:
            continue

        values = [r[1] for r in rows]
        labels = [r[0].strftime("%m-%d %H:%M") for r in rows]
        current = values[-1]

        if len(values) >= 6:
            baseline = values[:-1]
            mean = statistics.mean(baseline)
            stdev = statistics.stdev(baseline) or 0.0001
            z = abs((current - mean) / stdev)
            status = "ALERT" if z > cfg["z_threshold"] else "OK"
        else:
            mean = None
            status = "PENDING"

        metrics.append({
            "name": name,
            "value": current,
            "mean": mean,
            "status": status,
            "history_labels": labels,
            "history_values": values,
        })

    last = con.execute("SELECT MAX(run_at) FROM history").fetchone()[0]
    last_run = last.strftime("%Y-%m-%d %H:%M:%S") if last else "Never"

    con.close()
    return metrics, last_run


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    metrics, last_run = get_metric_data()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "metrics": metrics, "last_run": last_run}
    )


@app.get("/health")
def health():
    return {"status": "ok"}