# Set Snyk config
$SnykToken = "308d2f8c-929d-4a14-bafb-b26dcbb2deec"
$Org = "bdhp-automation-test"
$Severity = "high"
$ReposFile = "repos.txt"

# Authenticate with Snyk
Write-Host "🔐 Authenticating with Snyk..."
snyk auth $SnykToken

# Read image list from file
if (!(Test-Path $ReposFile)) {
    Write-Error "❌ File '$ReposFile' not found."
    exit 1
}

$imageList = Get-Content $ReposFile | Where-Object { $_.Trim() -ne "" }

foreach ($fullImage in $imageList) {
    Write-Host "`n=== 🔍 Scanning Image: $fullImage ==="

    if ($fullImage -match "/([^/:]+):([0-9A-Za-z\.-]+)$") {
        $imageName = $Matches[1]    # e.g., bdhp-adt
        $version = $Matches[2]      # e.g., 5.9.0
        $tags = "name=$imageName,version=$version"

        $cmd = @(
            "snyk", "container", "monitor",
            "--org=$Org",
            "--tags=$tags",
            "--severity-threshold=$Severity",
            "$fullImage"
        )

        try {
            $process = Start-Process -FilePath $cmd[0] -ArgumentList $cmd[1..($cmd.Length - 1)] `
                -NoNewWindow -Wait -PassThru -RedirectStandardOutput stdout.txt -RedirectStandardError stderr.txt

            Write-Host "--- ✅ STDOUT ---"
            Get-Content stdout.txt
            Write-Host "--- ⚠️ STDERR ---"
            Get-Content stderr.txt
        }
        catch {
            Write-Error "❌ Failed to scan $fullImage: $_"
        }
    }
    else {
        Write-Error "⚠️ Skipping invalid image format: $fullImage"
    }
}
