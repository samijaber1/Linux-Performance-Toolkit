#!/usr/bin/env python3
"""
analyze_cpu.py - Analyze CPU benchmark results and plot performance graphs
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import re

RAW_RESULTS_FILE = Path("../results/cpu_results.csv")
CLEAN_RESULTS_FILE = Path("../results/cpu_results_clean.csv")

def load_data():
    valid_lines = []
    header = None

    # Read manually to filter out junk
    with open(RAW_RESULTS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("timestamp"):  # header
                header = line
                continue
            # Match proper data row: timestamp,duration,ops,real_time,...
            if re.match(r"^\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2},", line):
                valid_lines.append(line)

    if not valid_lines:
        print("[!] No valid benchmark rows found.")
        return pd.DataFrame()

    # Build DataFrame from valid rows
    from io import StringIO
    csv_content = header + "\n" + "\n".join(valid_lines)
    df = pd.read_csv(StringIO(csv_content))

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d_%H:%M:%S")

    # Convert numeric fields
    numeric_cols = ["duration", "ops", "real_time", "usr_time", "sys_time"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["duration", "ops"])

    # Recompute ops/sec
    df["ops_per_sec_real"] = df["ops"] / df["duration"]
    df["ops_per_sec_cpu"] = df["ops"] / (df["usr_time"] + df["sys_time"])

    # Save cleaned
    df.to_csv(CLEAN_RESULTS_FILE, index=False)
    print(f"[*] Saved cleaned results to {CLEAN_RESULTS_FILE}")

    return df

def plot_performance(df):
    if df.empty:
        print("[!] No valid data to plot.")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(df["timestamp"], df["ops_per_sec_real"], marker="o", label="Ops/sec (Real Time)")
    plt.plot(df["timestamp"], df["ops_per_sec_cpu"], marker="x", label="Ops/sec (CPU Time)")
    plt.xlabel("Timestamp")
    plt.ylabel("Operations per second")
    plt.title("CPU Benchmark Performance Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("cpu_performance.png")
    print("[*] Saved plot to cpu_performance.png")
    plt.show()

def main():
    df = load_data()
    if not df.empty:
        print("[*] Latest Results:\n", df.tail(5))
    plot_performance(df)

if __name__ == "__main__":
    main()
