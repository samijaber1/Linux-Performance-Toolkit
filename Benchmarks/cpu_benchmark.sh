#!/bin/bash
# cpu_benchmark.sh - Run CPU stress test and log results
# Usage: ./cpu_benchmark.sh [duration_seconds]

DURATION=${1:-10}   # Default to 10 seconds if not provided
OUTPUT_FILE="../results/cpu_results.csv"

mkdir -p ../results

echo "[*] Running CPU stress test for $DURATION seconds..."

# Run stress-ng and capture metrics
RESULT=$(stress-ng --cpu 4 --timeout ${DURATION}s --metrics-brief 2>&1 | grep "cpu")

# Extract values using awk
BOGO_OPS=$(echo "$RESULT" | awk '{print $2}')
REAL_TIME=$(echo "$RESULT" | awk '{print $3}')
USR_TIME=$(echo "$RESULT" | awk '{print $4}')
SYS_TIME=$(echo "$RESULT" | awk '{print $5}')
OPS_REAL=$(echo "$RESULT" | awk '{print $6}')
OPS_CPU=$(echo "$RESULT" | awk '{print $7}')

# Write header if file doesn’t exist
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "timestamp,duration,ops,real_time,usr_time,sys_time,ops_per_sec_real,ops_per_sec_cpu" >> "$OUTPUT_FILE"
fi

# Append data
echo "$(date +%Y-%m-%d_%H:%M:%S),$DURATION,$BOGO_OPS,$REAL_TIME,$USR_TIME,$SYS_TIME,$OPS_REAL,$OPS_CPU" >> "$OUTPUT_FILE"

echo "[*] Results saved to $OUTPUT_FILE"
#!/bin/bash
# cpu_benchmark.sh - Run a CPU stress test and measure performance

DURATION=${1:-10}  # default 10 seconds

echo "[*] Running CPU stress test for $DURATION seconds..."
if ! command -v stress-ng &>/dev/null; then
    echo "Error: stress-ng not installed. Run ./setup.sh first."
    exit 1
fi

stress-ng --cpu 4 --timeout "${DURATION}s" --metrics-brief
