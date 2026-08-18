
import random
from datetime import datetime, timedelta

try:
    import duckdb
except ImportError as e:
    raise ImportError(
        "The 'duckdb' package is required to run this script. Install it with: pip install duckdb"
    ) from e

con = duckdb.connect("warehouse.db")
con.execute("DROP TABLE IF EXISTS orders")
con.execute("CREATE TABLE orders (id INT, email VARCHAR, amount DECIMAL, created_at TIMESTAMP)")

now = datetime.now()
rows = []
for i in range(1000):
    email = None if random.random() < 0.30 else f"user{i}@test.com"
    amount = round(random.uniform(10, 500), 2)
    created = now - timedelta(hours=random.randint(0, 48))
    rows.append((i, email, amount, created))

con.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", rows)
print(f"Created {len(rows)} rows")
con.close()