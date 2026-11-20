"""Generate synthetic orders/customers tables as Parquet (no real personal data)."""
import argparse, os
import numpy as np
import pandas as pd

SEGMENTS = ["Retail", "Corporate", "SmallBiz", "Student", "Government"]

def generate(n_orders: int, out_dir: str, seed: int = 42) -> None:
    rng = np.random.default_rng(seed)
    n_customers = max(n_orders // 10, 1)
    customers = pd.DataFrame({
        "customer_id": np.arange(n_customers, dtype=np.int64),
        "segment": pd.Categorical(rng.choice(SEGMENTS, n_customers)).astype(str),
        "credit_limit": rng.uniform(1_000, 50_000, n_customers).round(2),
    })
    orders = pd.DataFrame({
        "order_id": np.arange(n_orders, dtype=np.int64),
        "customer_id": rng.integers(0, n_customers, n_orders, dtype=np.int64),
        "store_id": rng.integers(0, 100, n_orders, dtype=np.int32),
        "quantity": rng.integers(1, 20, n_orders, dtype=np.int32),
        "amount": rng.uniform(5, 500, n_orders).round(2),
    })
    os.makedirs(out_dir, exist_ok=True)
    orders.to_parquet(os.path.join(out_dir, "orders.parquet"), index=False)
    customers.to_parquet(os.path.join(out_dir, "customers.parquet"), index=False)
    print(f"wrote {n_orders:,} orders and {n_customers:,} customers to {out_dir}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--rows", type=int, required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    generate(a.rows, a.out)
