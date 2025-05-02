import subprocess
import csv
from datetime import datetime

# Path to your CSV file
csv_path = "DeviceBridge_Scan_Tracking(BDHP Scan Tracking) (1).csv"

# Output log file
log_file = "snyk_batch_scan_output.log"

# Open the CSV file and read it
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    
    with open(log_file, "w") as log:
        for index, row in enumerate(reader, start=1):
            ps_command = row.get("Unnamed: 28")  # Adjust column name as needed

            # Skip invalid or empty commands
            if not isinstance(ps_command, str) or not ps_command.startswith("New-Snyk-Container-Sbom"):
                continue

            log.write(f"\n--- Snyk Scan: Row {index} | {datetime.now()} ---\n")
            log.write(f"Command:\n{ps_command}\n")

            try:
                result = subprocess.run(["pwsh", "-Command", ps_command], capture_output=True, text=True)
                log.write("\n--- STDOUT ---\n")
                log.write(result.stdout)
                log.write("\n--- STDERR ---\n")
                log.write(result.stderr)
            except Exception as e:
                log.write(f"\n--- ERROR ---\n{str(e)}\n")

print("✅ All Snyk scans have been executed. Check 'snyk_batch_scan_output.log' for results.")
