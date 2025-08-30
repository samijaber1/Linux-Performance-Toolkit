#!/usr/bin/env python3
"""
analyze_cpu.py - Analyze CPU benchmark results and plot per-core performance graphs
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import re

RAW_RESULTS_FILE = Path("../results/cpu_results.csv")
CLEAN_RESULTS_FILE = Path("../results/cpu_results_clean.csv")

def load_data():
    # If cleaned file exists, just read it
    if CLEAN_RESULTS_FILE.exists():
        df = pd.read_csv(CLEAN_RESULTS_FILE, parse_dates=["timestamp"])
        return df

    # Otherwise, clean the raw file
    valid_lines = []
    header = None

    with open(RAW_RESULTS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("timestamp"):
                header = line
                continue
            if re.match(r"^\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2},", line):
                valid_lines.append(line)

    if not valid_lines:
        print("[!] No valid benchmark rows found.")
        return pd.DataFrame()

    from io import StringIO
    csv_content = header + "\n" + "\n".join(valid_lines)
    df = pd.read_csv(StringIO(csv_content))

    # Convert numeric fields safely
    numeric_cols = ["duration", "ops", "real_time", "usr_time", "sys_time", "core_id"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["duration", "ops", "core_id"])

    # Recompute ops/sec
    df["ops_per_sec_real"] = df["ops"] / df["duration"]
    df["ops_per_sec_cpu"] = df["ops"] / (df["usr_time"] + df["sys_time"])

    # Save cleaned CSV
    df.to_csv(CLEAN_RESULTS_FILE, index=False)
    print(f"[*] Saved cleaned results to {CLEAN_RESULTS_FILE}")

    return df

def plot_performance(df):
    if df.empty:
        print("[!] No valid data to plot.")
        return

    # Group by core_id for per-core analysis
    cores = df["core_id"].unique()
    plt.figure(figsize=(12, 6))
    for core in cores:
        core_df = df[df["core_id"] == core]
        plt.plot(core_df["timestamp"], core_df["ops_per_sec_real"], marker="o", label=f"Core {core} (Real)")
        plt.plot(core_df["timestamp"], core_df["ops_per_sec_cpu"], marker="x", linestyle="--", label=f"Core {core} (CPU)")

    plt.xlabel("Timestamp")
    plt.ylabel("Operations per second")
    plt.title("CPU Benchmark Performance per Core Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("cpu_performance_per_core.png")
    print("[*] Saved plot to cpu_performance_per_core.png")
    plt.show()

def performance_summary(df):
    if df.empty:
        return
    print("\n[*] Performance Summary:")
    for metric in ["ops_per_sec_real", "ops_per_sec_cpu"]:
        min_val = df[metric].min()
        max_val = df[metric].max()
        avg_val = df[metric].mean()
        print(f"{metric}: min={min_val:.2f}, max={max_val:.2f}, avg={avg_val:.2f}")

def main():
    df = load_data()
    if not df.empty:
        print("[*] Latest Results (per core):\n", df.tail(5))
    performance_summary(df)
    plot_performance(df)

if __name__ == "__main__":
    main()
