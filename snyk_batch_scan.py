import subprocess
import csv
from datetime import datetime

# Path to your CSV file
csv_path = "DeviceBridge_Scan_Tracking(BDHP Scan Tracking) (1).csv"

# Output log file
log_file = "snyk_batch_scan_output.log"

# Print headers to help identify correct column name
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    print(f"CSV Headers: {reader.fieldnames}")

    with open(log_file, "w") as log:
        log.write(f"--- Snyk Batch Scan Started at {datetime.now()} ---\n\n")

        for index, row in enumerate(reader, start=1):
            # Replace this with the actual header name (adjust after checking output above)
            ps_command = row.get("Unnamed: 28", "").strip()

            if not ps_command or not ps_command.startswith("New-Snyk-Container-Sbom"):
                print(f"No valid command for Row {index}, skipping.")
                continue

            log.write(f"\n--- Snyk Scan: Row {index} | {datetime.now()} ---\n")
            log.write(f"Command:\n{ps_command}\n")

            try:
                result = subprocess.run(["pwsh", "-Command", ps_command], capture_output=True, text=True)
                log.write("\n--- STDOUT ---\n" + result.stdout)
                log.write("\n--- STDERR ---\n" + result.stderr)
            except Exception as e:
                log.write(f"\n--- ERROR ---\n{str(e)}\n")

        log.write(f"\n--- Snyk Batch Scan Completed at {datetime.now()} ---\n")

print("✅ All Snyk scans succeded. Check 'snyk_batch_scan_output.log' for results.")
