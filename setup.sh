#!/bin/bash
# setup.sh - Install dependencies for Linux Performance Toolkit

echo "[*] Installing required packages..."

if [ -x "$(command -v apt-get)" ]; then
    sudo apt-get update
    sudo apt-get install -y stress-ng iperf3 sysstat
elif [ -x "$(command -v dnf)" ]; then
    sudo dnf install -y stress-ng iperf3 sysstat
elif [ -x "$(command -v yum)" ]; then
    sudo yum install -y epel-release
    sudo yum install -y stress-ng iperf3 sysstat
else
    echo "Unsupported package manager. Please install stress-ng, iperf3, and sysstat manually."
    exit 1
fi

echo "[*] Setup complete! You can now run the benchmarks."
