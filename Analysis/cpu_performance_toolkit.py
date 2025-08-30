#!/usr/bin/env python3
"""
cpu_performance_toolkit.py - Run CPU benchmarks multiple times and plot results
"""

import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import time
import re
import csv

# Paths
RAW_RESULTS_FILE = Path("../results/cpu_results.csv")
CLEAN_RESULTS_FILE = Path("../results/cpu_results_clean.csv")

# Configuration
ITERATIONS = 5          # Number of benchmark runs
DURATION = 10           # Duration of each run in seconds
SLEEP_BETWEEN = 2       # Seconds to wait between runs

def run_benchmark(duration=DURATION):
    """Run a single CPU benchmark using stress-ng and return the metrics."""
    try:
        result = subprocess.run(
            ["stress-ng", "--cpu", "4", "--timeout", f"{duration}s", "--metrics-brief"],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print("[!] Benchmark failed:", e)
        return None

    # Extract CPU line
    metrics_line = None
    for line in result.stdout.splitlines():
        if "stress-ng: metrc:" in line and "cpu" in line:
            metrics_line = line.strip()
    if not metrics_line:
        print("[!] Failed to parse metrics line")
        return None

    # Extract numeric values using regex
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", metrics_line)
    if len(numbers) < 6:
        print("[!] Not enough numeric values in line:", metrics_line)
        return None

    # Take the last 6 numbers: bogo_ops, real_time, usr_time, sys_time, ops_per_sec_real, ops_per_sec_cpu
    bogo_ops, real_time, usr_time, sys_time, ops_real, ops_cpu = map(float, numbers[-6:])

    timestamp = pd.Timestamp.now().strftime("%Y-%m-%d_%H:%M:%S")
    return {
        "timestamp": timestamp,
        "duration": duration,
        "ops": bogo_ops,
        "real_time": real_time,
        "usr_time": usr_time,
        "sys_time": sys_time,
        "ops_per_sec_real": ops_real,
        "ops_per_sec_cpu": ops_cpu,
    }

def append_to_csv(data, path=RAW_RESULTS_FILE):
    """Append a dictionary as a CSV row, creating file if missing."""
    fieldnames = ["timestamp","duration","ops","real_time","usr_time","sys_time","ops_per_sec_real","ops_per_sec_cpu"]
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists() and path.stat().st_size > 0
    with open(path, "a") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def load_and_clean_csv(path=RAW_RESULTS_FILE):
    """Load CSV and drop invalid rows."""
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df = df.dropna(subset=["ops", "real_time"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d_%H:%M:%S")
    numeric_cols = ["duration","ops","real_time","usr_time","sys_time","ops_per_sec_real","ops_per_sec_cpu"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=numeric_cols)
    return df

def plot_performance(df):
    if df.empty:
        print("[!] No valid data to plot.")
        return
    plt.figure(figsize=(12,6))
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

def summarize(df):
    if df.empty:
        return
    print("\n[*] Performance Summary:")
    print("Ops/sec (Real Time): min={:.2f}, max={:.2f}, avg={:.2f}".format(
        df["ops_per_sec_real"].min(), df["ops_per_sec_real"].max(), df["ops_per_sec_real"].mean()
    ))
    print("Ops/sec (CPU Time): min={:.2f}, max={:.2f}, avg={:.2f}".format(
        df["ops_per_sec_cpu"].min(), df["ops_per_sec_cpu"].max(), df["ops_per_sec_cpu"].mean()
    ))

def main():
    print("[*] Starting CPU benchmark toolkit")
    for i in range(ITERATIONS):
        print(f"[*] Run {i+1}/{ITERATIONS}...")
        data = run_benchmark()
        if data:
            append_to_csv(data)
            print(f"[*] Run {i+1} metrics: {data}")
        time.sleep(SLEEP_BETWEEN)

    df = load_and_clean_csv()
    df.to_csv(CLEAN_RESULTS_FILE, index=False)
    print(f"[*] Saved cleaned results to {CLEAN_RESULTS_FILE}")
    summarize(df)
    plot_performance(df)

if __name__ == "__main__":
    main()
