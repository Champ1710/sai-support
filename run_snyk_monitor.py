import subprocess
from datetime import datetime

# Paths
repos_file = "repos.txt"
log_file = "snyk_scan.log"

# Static parameters
organization = "your-org-name"
tags = "env:prod"
dockerfile_path = "./Dockerfile"  # Optional or "" if not used

# Read image list
with open(repos_file, "r") as f:
    images = [line.strip() for line in f if line.strip()]

# Start logging
with open(log_file, "w") as log:
    log.write(f"--- Snyk Scan Started at {datetime.now()} ---\n\n")
    
    for image in images:
        log.write(f"\n--- Scanning: {image} ---\n")

        ps_command = f"""
        & './Snyk-Container-Monitor.ps1' `
            -organization "{organization}" `
            -tags "{tags}" `
            -image "{image}" `
            -dockerfilePath "{dockerfile_path}"
        """

        try:
            result = subprocess.run(["pwsh", "-Command", ps_command], capture_output=True, text=True)
            log.write("STDOUT:\n" + result.stdout + "\n")
            log.write("STDERR:\n" + result.stderr + "\n")
        except Exception as e:
            log.write(f"ERROR running scan for {image}: {e}\n")

    log.write(f"\n--- Snyk Scan Completed at {datetime.now()} ---\n")
