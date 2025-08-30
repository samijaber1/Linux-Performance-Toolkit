#!/bin/bash
# cpu_benchmark.sh - Run CPU stress test and log per-core results

DURATION=${1:-10}
OUTPUT_FILE="../results/cpu_results.csv"

# Create the results directory if it doesn't exist
mkdir -p ../results

# Get the number of CPU cores
NUM_CORES=$(nproc)

echo "[*] Running CPU stress test for $DURATION seconds on $NUM_CORES cores..."

# Write header if the file is new or empty
if [ ! -s "$OUTPUT_FILE" ]; then
    echo "timestamp,duration,core_id,ops,real_time,usr_time,sys_time,ops_per_sec_real,ops_per_sec_cpu" > "$OUTPUT_FILE"
fi

# Loop through each core
for CORE in $(seq 0 $((NUM_CORES-1))); do
    echo "[*] Running benchmark on core $CORE..."

    # Run stress-ng pinned to a single core
    RAW_OUTPUT=$(taskset -c $CORE stress-ng --cpu 1 --timeout "${DURATION}s" --metrics-brief 2>&1)

    # Extract the specific metrics line for this core
    METRICS_LINE=$(echo "$RAW_OUTPUT" | grep "stress-ng: metrc:" | grep "cpu" | tail -1)

    if [ -z "$METRICS_LINE" ]; then
        echo "[!] Failed to find CPU metrics for core $CORE:"
        echo "$RAW_OUTPUT"
        continue
    fi

    # Extract metrics
    BOGO_OPS=$(echo "$METRICS_LINE" | awk '{print $5}')
    REAL_TIME=$(echo "$METRICS_LINE" | awk '{print $6}')
    USR_TIME=$(echo "$METRICS_LINE" | awk '{print $7}')
    SYS_TIME=$(echo "$METRICS_LINE" | awk '{print $8}')
    OPS_REAL=$(echo "$METRICS_LINE" | awk '{print $9}')
    OPS_CPU=$(echo "$METRICS_LINE" | awk '{print $10}')

    if [ -z "$BOGO_OPS" ] || [ -z "$REAL_TIME" ] || [ -z "$OPS_REAL" ]; then
        echo "[!] Failed to extract metrics for core $CORE"
        continue
    fi

    # Append data row
    echo "$(date +%Y-%m-%d_%H:%M:%S),$DURATION,$CORE,$BOGO_OPS,$REAL_TIME,$USR_TIME,$SYS_TIME,$OPS_REAL,$OPS_CPU" >> "$OUTPUT_FILE"

    echo "[*] Core $CORE results saved."
done

echo "[*] All per-core benchmarks completed. Results saved to $OUTPUT_FILE"
