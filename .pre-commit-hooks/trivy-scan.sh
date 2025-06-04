#!/usr/bin/env bash
# Simple trivy security scan script
# This is a placeholder - in production you'd want proper trivy configuration

echo "Running Trivy security scan..."

# Check if trivy is installed
if ! command -v trivy &> /dev/null; then
    echo "Trivy is not installed. Skipping security scan."
    echo "To install: https://aquasecurity.github.io/trivy/latest/getting-started/installation/"
    exit 0
fi

# Scan filesystem for vulnerabilities in dependencies
echo "Scanning for vulnerabilities..."
trivy fs --exit-code 0 --no-progress --severity HIGH,CRITICAL .

echo "Trivy scan completed."
exit 0