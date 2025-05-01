import subprocess

# Path to your repos.txt file
repos_file = "repos.txt"

# Read and parse the parameters
repos = {}
with open(repos_file, "r") as f:
    for line in f:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            repos[key.strip()] = value.strip()

# Define the PowerShell command as a string
ps_command = f"""
Snyk-Container-Monitor `
    -organization "{repos['organization']}" `
    -tags "{repos['tags']}" `
    -image "{repos['image']}" `
    -dockerfilePath "{repos['dockerfilePath']}"
"""

# Run the command using PowerShell Core (pwsh)
try:
    result = subprocess.run(["pwsh", "-Command", ps_command], capture_output=True, text=True)
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
except Exception as e:
    print(f"Failed to run PowerShell command: {e}")
