"""Draw the three result figures from results/results.csv."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(HERE, "results", "results.csv"))
df = df.drop_duplicates(subset=["rows", "engine", "query"], keep="last")
df["ms"] = df["median_s"] * 1000
OUT = os.path.join(HERE, "figures")
os.makedirs(OUT, exist_ok=True)

ENGINES = list(dict.fromkeys(df["engine"]))          # fixed order: Pandas, Polars, DuckDB 1T, DuckDB nT
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # validated categorical slots 1-4
HATCH = ["", "//", "..", "xx"]                        # secondary encoding for B/W print
MARK = ["o", "s", "^", "D"]
QUERIES = ["Q1 group-by", "Q2 join"]
INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e4e3de"

plt.rcParams.update({
    "font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 9, "axes.edgecolor": MUTED,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "legend.frameon": False, "savefig.dpi": 300,
})

def style(ax):
    ax.grid(axis="x", visible=False)

# ---- Fig 1: median query time at the largest size ----
big = df["rows"].max()
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.6))
for ax, q in zip(axes, QUERIES):
    sub = df[(df["rows"] == big) & (df["query"] == q)].set_index("engine").loc[ENGINES]
    bars = ax.bar(range(len(ENGINES)), sub["ms"], color=COLORS, hatch=HATCH,
                  edgecolor="white", linewidth=1.5, width=0.7)
    for b, v in zip(bars, sub["ms"]):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.0f}", ha="center", va="bottom",
                fontsize=8, color=INK)
    ax.set_xticks(range(len(ENGINES)))
    ax.set_xticklabels([e.replace(" (", "\n(") for e in ENGINES], fontsize=7.5)
    ax.set_title(f"{q} ({big/1e6:.0f}M rows)", fontsize=9, color=INK)
    ax.set_ylabel("Median time (ms)")
    ax.margins(y=0.15)
    style(ax)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig1_query_time.png"))
fig.savefig(os.path.join(OUT, "fig1_query_time.pdf"))

# ---- Fig 2: scaling with data size ----
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.6))
for ax, q in zip(axes, QUERIES):
    for e, c, m in zip(ENGINES, COLORS, MARK):
        s = df[(df["engine"] == e) & (df["query"] == q)].sort_values("rows")
        ax.plot(s["rows"] / 1e6, s["ms"], color=c, marker=m, markersize=5,
                linewidth=1.6, label=e)
    ax.set_xticks(sorted(df["rows"].unique() / 1e6))
    ax.set_xlabel("Rows in orders table (millions)")
    ax.set_ylabel("Median time (ms)")
    ax.set_title(q, fontsize=9, color=INK)
axes[0].legend(fontsize=7.5, loc="upper left")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig2_scaling.png"))
fig.savefig(os.path.join(OUT, "fig2_scaling.pdf"))

# ---- Fig 3: speed-up over Pandas, split into execution model vs threads ----
fig, ax = plt.subplots(figsize=(3.5, 2.6))
t = df[df["rows"] == big].pivot(index="query", columns="engine", values="ms").loc[QUERIES]
others = ENGINES[1:]
w = 0.25
for i, (e, c, h) in enumerate(zip(others, COLORS[1:], HATCH[1:])):
    sp = t["Pandas"] / t[e]
    xs = [k + (i - 1) * w for k in range(len(QUERIES))]
    bars = ax.bar(xs, sp, width=w, color=c, hatch=h, edgecolor="white", linewidth=1.2, label=e)
    for b, v in zip(bars, sp):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.1f}×", ha="center", va="bottom",
                fontsize=7.5, color=INK)
ax.axhline(1, color=MUTED, linewidth=0.8, linestyle="--")
ax.set_xticks(range(len(QUERIES)))
ax.set_xticklabels(QUERIES)
ax.set_ylabel("Speed-up over Pandas (×)")
ax.set_title(f"{big/1e6:.0f}M rows; dashed line = Pandas (1×)", fontsize=8, color=INK)
ax.set_ylim(0, t["Pandas"].div(t[others[-1]]).max() * 1.45)
ax.legend(fontsize=7, loc="upper left")
style(ax)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig3_speedup.png"))
fig.savefig(os.path.join(OUT, "fig3_speedup.pdf"))

# ---- summary table used in the paper ----
t["Polars x"] = t["Pandas"] / t["Polars"]
for e in others[1:]:
    t[f"{e} x"] = t["Pandas"] / t[e]
t["thread gain x"] = t[ENGINES[2]] / t[ENGINES[3]]
t.round(2).to_csv(os.path.join(HERE, "results", "summary_largest.csv"))
print(t.round(2).to_string())
print("figures written to", OUT)
