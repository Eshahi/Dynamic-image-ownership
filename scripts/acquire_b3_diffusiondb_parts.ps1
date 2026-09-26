# Single-writer, bounded, resumable public archive acquisition; not science/rights acceptance.
param(
    [Parameter(Mandatory = $true)][string]$Authorization,
    [Parameter(Mandatory = $true)][string]$AuthorizationSha256,
    [switch]$ListOnly
)
$ErrorActionPreference = 'Stop'

function Assert-Unlinked([string]$Path) {
    $probe = [System.IO.Path]::GetFullPath($Path)
    while ($probe) {
        if (Test-Path -LiteralPath $probe) {
            if ((Get-Item -LiteralPath $probe -Force).Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
                throw 'Linked input/output path is outside acquisition contract.'
            }
        }
        $probe = Split-Path $probe -Parent
    }
}
function Read-CheckedJson([string]$Path, [string]$ExpectedHash) {
    Assert-Unlinked $Path
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw 'Required contract file missing.' }
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try { $digest = ([System.BitConverter]::ToString($hasher.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant() }
    finally { $hasher.Dispose() }
    if ($digest -cne $ExpectedHash) { throw 'Contract snapshot SHA-256 mismatch.' }
    return ([System.Text.Encoding]::UTF8.GetString($bytes) | ConvertFrom-Json)
}

$approval = Read-CheckedJson $Authorization $AuthorizationSha256
$revision = 'fb620fbe49fa4420e0734bd9c0df11f51176b61f'
$root = 'W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\data\raw\diffusiondb-2m\archives'
$parts = @(948,1232,1790,420,1929,1168,1467,558,943,1034,836,268,1854,1359)
if ($approval.status -cne 'user_authorized_bounded_acquisition' -or $approval.actor -cne 'user' -or
    $approval.revision -cne $revision -or $approval.part_cap -ne 14 -or
    $approval.archive_byte_ceiling -ne 8493745129L -or $approval.target_images -ne 5000 -or
    $approval.nsfw_ceiling -ne 0.10 -or $approval.ranking_changed -ne $false -or
    $approval.scientific_compute -ne $false -or $approval.paid_compute -ne $false -or
    [System.IO.Path]::GetFullPath($approval.download_root) -ine $root) { throw 'Authorization scope mismatch.' }
$contractParent = Split-Path ([System.IO.Path]::GetFullPath($Authorization)) -Parent
if ($approval.proposal_file -cne '20260926-proposed-diffusiondb-parts.json' -or
    $approval.production_selection_file -cne '20260926-approved-fourteen-part-production-selection.json') {
    throw 'Unexpected contract filenames.'
}
$proposal = Read-CheckedJson (Join-Path $contractParent $approval.proposal_file) $approval.proposal_sha256
$selection = Read-CheckedJson (Join-Path $contractParent $approval.production_selection_file) $approval.production_selection_sha256
if ($selection.status -cne 'candidate_parts_ready' -or $selection.revision -cne $revision -or
    $selection.parts_checked -ne 2000 -or $selection.metadata_rows -ne 2000000 -or $selection.production_part_cap -ne 14 -or
    $selection.rows_examined_in_candidate_parts -ne 14000 -or $selection.distinct_prompt_groups -lt 6000 -or
    ($selection.selected_part_ids -join ',') -cne ($parts -join ',') -or
    ($selection.candidate_order -join ',') -cne ($parts -join ',') -or
    $proposal.revision -cne $revision -or $proposal.files.Count -ne 14) { throw 'Production selection mismatch.' }
$total = 0L
for ($index = 0; $index -lt 14; $index++) {
    $item = $proposal.files[$index]
    $expected = 'images/part-{0:D6}.zip' -f $parts[$index]
    if ($item.path -cne $expected -or $item.size -le 0 -or $item.size -ne $item.lfs.size -or
        $item.lfs.oid -cnotmatch '^[0-9a-f]{64}$') { throw 'Invalid bounded archive manifest.' }
    $total += [long]$item.size
    Write-Output "CONTRACT $($item.path) bytes=$($item.size) sha256=$($item.lfs.oid)"
}
if ($total -ne 8493745129L) { throw 'Total archive bytes exceed/differ from authorization.' }
if ($ListOnly) { Write-Output "LIST_ONLY total_bytes=$total"; exit 0 }

Assert-Unlinked $root
New-Item -ItemType Directory -Force -Path $root | Out-Null
$lockPath = Join-Path $root '.b3-download.lock'
Assert-Unlinked $lockPath
# FileShare.None prevents a second downloader; file remains harmless after handle release/crash.
$lock = [System.IO.File]::Open($lockPath, [System.IO.FileMode]::OpenOrCreate,
                             [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
try {
    foreach ($item in $proposal.files) {
        $name = Split-Path $item.path -Leaf
        $destination = Join-Path $root $name
        $partial = "$destination.partial"
        Assert-Unlinked $destination
        Assert-Unlinked $partial
        if (Test-Path -LiteralPath $destination) {
            if ((Get-Item -LiteralPath $destination).Length -ne $item.size -or
                (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -cne $item.lfs.oid) {
                throw 'Existing final archive differs; preserve it for investigation.'
            }
            Write-Output "VERIFIED_EXISTING $name bytes=$($item.size) sha256=$($item.lfs.oid)"
            continue
        }
        $complete = $false
        for ($attempt = 1; $attempt -le 3; $attempt++) {
            $present = 0L
            if (Test-Path -LiteralPath $partial) { $present = (Get-Item -LiteralPath $partial).Length }
            if ($present -gt $item.size) { throw 'Oversized partial archive; preserve it for investigation.' }
            if ($present -eq $item.size) { $complete = $true; break }
            if ((Get-PSDrive W).Free -lt ($item.size - $present + 1073741824L)) { throw 'Insufficient free disk space.' }
            Write-Output "DOWNLOADING $name attempt=$attempt resume_bytes=$present expected_bytes=$($item.size)"
            $url = "https://huggingface.co/datasets/poloclub/diffusiondb/resolve/$revision/$($item.path)?download=true"
            & curl.exe --fail --location --silent --show-error --proto '=https' --proto-redir '=https' `
                --connect-timeout 30 --max-time 7200 --max-filesize $item.size `
                --continue-at - --output $partial $url
            $curlExit = $LASTEXITCODE
            Assert-Unlinked $partial
            if ((Test-Path -LiteralPath $partial) -and (Get-Item -LiteralPath $partial).Length -eq $item.size) {
                $complete = $true; break
            }
            Write-Output "INCOMPLETE $name curl_exit=$curlExit (partial preserved)"
            if ($attempt -lt 3) { Start-Sleep -Seconds 5 }
        }
        if (-not $complete) { throw 'Download attempts exhausted; partial preserved for resume.' }
        $digest = (Get-FileHash -LiteralPath $partial -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($digest -cne $item.lfs.oid) { throw 'Downloaded archive SHA-256 mismatch; partial preserved.' }
        if (Test-Path -LiteralPath $destination) { throw 'Final archive appeared unexpectedly; refuse overwrite.' }
        Move-Item -LiteralPath $partial -Destination $destination
        Write-Output "VERIFIED_DOWNLOADED $name bytes=$($item.size) sha256=$digest"
    }
    Write-Output "B3_ARCHIVES_VERIFIED count=14 bytes=$total (not rights/science acceptance)"
}
finally { $lock.Dispose() }
