param(
    [string]$organization,
    [string]$tags,
    [string]$image,
    [string]$dockerfilePath
)

Write-Output "Scanning Image: $image"
Write-Output "Organization: $organization"
Write-Output "Tags: $tags"
Write-Output "Dockerfile Path: $dockerfilePath"
