#!/bin/bash
# cpu_benchmark.sh - Run CPU stress test and log results

DURATION=${1:-10}
OUTPUT_FILE="../results/cpu_results.csv"

# Create the results directory if it doesn't exist
mkdir -p ../results

echo "[*] Running CPU stress test for $DURATION seconds..."

# Run stress-ng and capture the output
RAW_OUTPUT=$(stress-ng --cpu 4 --timeout "${DURATION}s" --metrics-brief 2>&1)

# Extract the specific metrics line for CPU
METRICS_LINE=$(echo "$RAW_OUTPUT" | grep "stress-ng: metrc:" | grep "cpu" | tail -1)

# Check if we found the metrics line
if [ -z "$METRICS_LINE" ]; then
    echo "[!] Failed to find CPU metrics in stress-ng output:"
    echo "$RAW_OUTPUT"
    exit 1
fi

# Extract the values from the metrics line
# The format is: stress-ng: metrc: [PID] cpu bogo_ops real_time usr_time sys_time ops_per_sec_real ops_per_sec_cpu
BOGO_OPS=$(echo "$METRICS_LINE" | awk '{print $5}')
REAL_TIME=$(echo "$METRICS_LINE" | awk '{print $6}')
USR_TIME=$(echo "$METRICS_LINE" | awk '{print $7}')
SYS_TIME=$(echo "$METRICS_LINE" | awk '{print $8}')
OPS_REAL=$(echo "$METRICS_LINE" | awk '{print $9}')
OPS_CPU=$(echo "$METRICS_LINE" | awk '{print $10}')

# Check if we successfully captured all metrics
if [ -z "$BOGO_OPS" ] || [ -z "$REAL_TIME" ] || [ -z "$OPS_REAL" ]; then
    echo "[!] Failed to extract metrics from line: $METRICS_LINE"
    echo "Full output:"
    echo "$RAW_OUTPUT"
    exit 1
fi

# Write header if the file is new or empty
if [ ! -s "$OUTPUT_FILE" ]; then
    echo "timestamp,duration,ops,real_time,usr_time,sys_time,ops_per_sec_real,ops_per_sec_cpu" > "$OUTPUT_FILE"
fi

# Append data row
echo "$(date +%Y-%m-%d_%H:%M:%S),$DURATION,$BOGO_OPS,$REAL_TIME,$USR_TIME,$SYS_TIME,$OPS_REAL,$OPS_CPU" >> "$OUTPUT_FILE"

echo "[*] Results saved to $OUTPUT_FILE"