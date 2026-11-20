"""Benchmark Q1 (group-by) and Q2 (join + group-by) on Pandas, Polars and DuckDB.

Q1: SELECT store_id, SUM(amount), AVG(quantity), COUNT(*) FROM orders GROUP BY store_id
Q2: SELECT c.segment, SUM(o.amount), COUNT(*) FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id GROUP BY c.segment

Data is loaded into memory first; only query time is measured.
Each query: 1 warm-up run + N timed runs; the median is reported.
"""
import argparse, json, os, platform, statistics, time
import duckdb
import numpy as np
import pandas as pd
import polars as pl

Q1_SQL = """SELECT store_id, SUM(amount) AS total_amount, AVG(quantity) AS avg_qty,
                   COUNT(*) AS n FROM orders GROUP BY store_id ORDER BY store_id"""
Q2_SQL = """SELECT c.segment, SUM(o.amount) AS total_amount, COUNT(*) AS n
            FROM orders o JOIN customers c ON o.customer_id = c.customer_id
            GROUP BY c.segment ORDER BY c.segment"""

# ---------- Pandas (row-at-a-time-ish, mostly single-threaded) ----------
def pandas_q1(o, c):
    return (o.groupby("store_id", sort=True)
             .agg(total_amount=("amount", "sum"), avg_qty=("quantity", "mean"),
                  n=("amount", "size")).reset_index())

def pandas_q2(o, c):
    j = o.merge(c[["customer_id", "segment"]], on="customer_id", how="inner")
    return (j.groupby("segment", sort=True)
             .agg(total_amount=("amount", "sum"), n=("amount", "size")).reset_index())

# ---------- Polars (Arrow columnar, vectorised, multi-threaded) ----------
def polars_q1(o, c):
    return (o.lazy().group_by("store_id")
             .agg(pl.col("amount").sum().alias("total_amount"),
                  pl.col("quantity").mean().alias("avg_qty"),
                  pl.len().alias("n")).sort("store_id").collect())

def polars_q2(o, c):
    return (o.lazy().join(c.lazy().select("customer_id", "segment"), on="customer_id")
             .group_by("segment")
             .agg(pl.col("amount").sum().alias("total_amount"), pl.len().alias("n"))
             .sort("segment").collect())

def time_it(fn, runs):
    fn()  # warm-up
    ts = []
    for _ in range(runs):
        t0 = time.perf_counter(); res = fn(); ts.append(time.perf_counter() - t0)
    return statistics.median(ts), min(ts), max(ts), res

def to_pandas(res):
    if isinstance(res, pl.DataFrame): return res.to_pandas()
    return res

def check_same(ref, other, key):
    a = to_pandas(ref).sort_values(key).reset_index(drop=True)
    b = to_pandas(other).sort_values(key).reset_index(drop=True)
    assert len(a) == len(b), "row count differs"
    assert np.allclose(a["total_amount"].astype(float), b["total_amount"].astype(float), rtol=1e-6)
    assert (a["n"].astype(int).values == b["n"].astype(int).values).all()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--rows", type=int, required=True)
    p.add_argument("--runs", type=int, default=10)
    p.add_argument("--out", default="results/results.csv")
    a = p.parse_args()

    o_pd = pd.read_parquet(os.path.join(a.data, "orders.parquet"))
    c_pd = pd.read_parquet(os.path.join(a.data, "customers.parquet"))
    o_pl = pl.read_parquet(os.path.join(a.data, "orders.parquet"))
    c_pl = pl.read_parquet(os.path.join(a.data, "customers.parquet"))
    con = duckdb.connect()
    con.execute(f"CREATE TABLE orders AS SELECT * FROM read_parquet('{a.data}/orders.parquet')")
    con.execute(f"CREATE TABLE customers AS SELECT * FROM read_parquet('{a.data}/customers.parquet')")
    all_threads = os.cpu_count()

    def duck(sql, threads):
        def f():
            con.execute(f"SET threads={threads}")
            return con.execute(sql).df()
        return f

    engines = [
        ("Pandas", lambda: pandas_q1(o_pd, c_pd), lambda: pandas_q2(o_pd, c_pd)),
        ("Polars", lambda: polars_q1(o_pl, c_pl), lambda: polars_q2(o_pl, c_pl)),
        ("DuckDB (1 thread)", duck(Q1_SQL, 1), duck(Q2_SQL, 1)),
        (f"DuckDB ({all_threads} threads)", duck(Q1_SQL, all_threads), duck(Q2_SQL, all_threads)),
    ]
    rows, ref = [], {}
    for name, q1, q2 in engines:
        for qname, fn, key in (("Q1 group-by", q1, "store_id"), ("Q2 join", q2, "segment")):
            med, lo, hi, res = time_it(fn, a.runs)
            if qname in ref: check_same(ref[qname], res, key)
            else: ref[qname] = res
            rows.append(dict(rows=a.rows, engine=name, query=qname,
                             median_s=round(med, 4), min_s=round(lo, 4), max_s=round(hi, 4),
                             runs=a.runs))
            print(f"{a.rows:>11,}  {name:<20} {qname:<12} median {med*1000:9.1f} ms")
    print("all engines returned identical results ✔")

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(a.out, mode="a", header=not os.path.exists(a.out), index=False)

    env = dict(python=platform.python_version(), pandas=pd.__version__, polars=pl.__version__,
               duckdb=duckdb.__version__, cpu=platform.processor() or platform.machine(),
               logical_cores=all_threads, os=platform.platform())
    with open(os.path.join(os.path.dirname(a.out), "environment.json"), "w") as f:
        json.dump(env, f, indent=2)

if __name__ == "__main__":
    main()
