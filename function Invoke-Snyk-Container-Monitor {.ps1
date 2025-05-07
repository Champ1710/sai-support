function Invoke-Snyk-Container-Monitor {
    param (
        [string]$organization,
        [string]$tags,
        [string]$image,
        [string]$dockerfilePath = ""
    )

    # Your Snyk command logic here
    $args = @(
        "container", "monitor", $image,
        "--org=$organization",
        "--project-tags=$tags"
    )

    if ($dockerfilePath -ne "") {
        $args += "--dockerfile=$dockerfilePath"
    }

    # Run Snyk
    snyk @args
}
