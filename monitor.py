import statistics
from datetime import datetime
from pathlib import Path

import importlib
import importlib.util

# Import pyyaml dynamically to avoid static analysis/import errors in some editors
yaml_spec = importlib.util.find_spec("yaml")
if yaml_spec is None:  # pragma: no cover - helpful runtime message
    raise SystemExit("Missing dependency 'pyyaml'. Install with: python -m pip install pyyaml")
yaml = importlib.import_module("yaml")

duckdb_spec = importlib.util.find_spec("duckdb")
if duckdb_spec is None:  # pragma: no cover - helpful runtime message
    raise SystemExit("Missing dependency 'duckdb'. Install with: python -m pip install duckdb")
duckdb = importlib.import_module("duckdb")

# Load settings (config.yml is expected next to this script)
cfg_path = Path(__file__).with_name("config.yml")
if not cfg_path.exists():
    raise SystemExit(f"Configuration file not found: {cfg_path}")

with cfg_path.open() as f:
    cfg = yaml.safe_load(f)

con = duckdb.connect(cfg["warehouse"])

# Create history table if needed
con.execute("CREATE TABLE IF NOT EXISTS history (run_at TIMESTAMP, metric VARCHAR, value DOUBLE)")

# Check 1: row count
row_count = con.execute(f"SELECT COUNT(*) FROM {cfg['table']}").fetchone()[0]

# Check 2: null rate
null_rate = con.execute(f"""
    SELECT SUM(CASE WHEN {cfg['column']} IS NULL THEN 1 ELSE 0 END) * 1.0 / COUNT(*)
    FROM {cfg['table']}
""").fetchone()[0]

metrics = {"row_count": row_count, "null_rate": null_rate}

# Compare each metric to history and alert
for name, value in metrics.items():
    baseline = con.execute(
        "SELECT value FROM history WHERE metric = ? ORDER BY run_at DESC LIMIT 30", [name]
    ).fetchall()
    baseline = [row[0] for row in baseline]

    if len(baseline) >= 5:
        mean = statistics.mean(baseline)
        stdev = statistics.stdev(baseline) or 0.0001
        z = abs((value - mean) / stdev)
        if z > cfg["z_threshold"]:
            print(f"🚨 ANOMALY in {name}: value={value:.4f}, mean={mean:.4f}, z={z:.2f}")
        else:
            print(f"✓ {name}: {value:.4f} (normal)")
    else:
        print(f"… {name}: {value:.4f} (building baseline, run {len(baseline)+1}/5)")

    con.execute("INSERT INTO history VALUES (?, ?, ?)", [datetime.now(), name, value])

con.close()
print("Done.")