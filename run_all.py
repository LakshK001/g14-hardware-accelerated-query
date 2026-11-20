"""Reproduce every result in the paper with one command:  python run_all.py

Works on Windows, macOS and Linux. Takes about 3-5 minutes on a laptop.
Use --quick for a 1-minute smoke test (1M rows only, 3 runs; writes to results/quick/).
"""
import argparse, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

def run(*args):
    print(">", " ".join(args), flush=True)
    subprocess.run([sys.executable, *args], check=True, cwd=HERE)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--quick", action="store_true", help="1M rows, 3 runs, results in results/quick/")
    a = p.parse_args()
    sizes = [1_000_000] if a.quick else [1_000_000, 5_000_000, 10_000_000]
    runs = "3" if a.quick else "10"
    out = os.path.join("results", "quick", "results.csv") if a.quick else os.path.join("results", "results.csv")
    if os.path.exists(os.path.join(HERE, out)):
        os.remove(os.path.join(HERE, out))
    for n in sizes:
        data_dir = os.path.join("data", str(n))
        if not os.path.exists(os.path.join(HERE, data_dir, "orders.parquet")):
            run("src/generate_data.py", "--rows", str(n), "--out", data_dir)
        run("src/benchmark.py", "--data", data_dir, "--rows", str(n), "--runs", runs, "--out", out)
    if not a.quick:
        run("src/make_figures.py")
    print("\nDone. Results:", out)

if __name__ == "__main__":
    main()
