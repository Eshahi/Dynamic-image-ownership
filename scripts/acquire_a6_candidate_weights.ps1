# Acquires only the user-authorized A6 candidate public weights into an ignored local asset root.
# This is not scientific execution or acceptance of the unaffiliated SD 1.5 mirror.
param(
    [Parameter(Mandatory = $true)][string]$AssetRoot,
    [switch]$ListOnly
)

$ErrorActionPreference = 'Stop'
$revision = '451f4fe16113bff5a5d2269ed5ad43b0592e9a14'
$sdBase = "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/$revision"
$items = @(
    @{ Path = 'alexnet/alexnet-owt-7be5be79.pth'; Url = 'https://download.pytorch.org/models/alexnet-owt-7be5be79.pth'; Bytes = 244408911L; Prefix = '7be5be79' },
    @{ Path = 'sd15-fp16/text_encoder/model.fp16.safetensors'; Url = "$sdBase/text_encoder/model.fp16.safetensors"; Bytes = 246144864L; Sha256 = '77795e2023adcf39bc29a884661950380bd093cf0750a966d473d1718dc9ef4e' },
    @{ Path = 'sd15-fp16/vae/diffusion_pytorch_model.fp16.safetensors'; Url = "$sdBase/vae/diffusion_pytorch_model.fp16.safetensors"; Bytes = 167335342L; Sha256 = '4fbcf0ebe55a0984f5a5e00d8c4521d52359af7229bb4d81890039d2aa16dd7c' },
    @{ Path = 'sd15-fp16/safety_checker/model.fp16.safetensors'; Url = "$sdBase/safety_checker/model.fp16.safetensors"; Bytes = 608018440L; Sha256 = '08902f19b1cfebd7c989f152fc0507bef6898c706a91d666509383122324b511' },
    @{ Path = 'sd15-fp16/unet/diffusion_pytorch_model.fp16.safetensors'; Url = "$sdBase/unet/diffusion_pytorch_model.fp16.safetensors"; Bytes = 1719125304L; Sha256 = 'c83908253f9a64d08c25fc90874c9c8aef9a329ce1ca5fb909d73b0c83d1ea21' }
)

if ($ListOnly) {
    foreach ($item in $items) { Write-Output "$($item.Path) $($item.Bytes) $($item.Url)" }
    exit 0
}

if (-not [System.IO.Path]::IsPathFullyQualified($AssetRoot)) { throw 'AssetRoot must be an absolute path.' }
$resolvedRoot = [System.IO.Path]::GetFullPath($AssetRoot)
if (-not $resolvedRoot.EndsWith([System.IO.Path]::DirectorySeparatorChar + '.thesis-build' + [System.IO.Path]::DirectorySeparatorChar + 'assets' + [System.IO.Path]::DirectorySeparatorChar + 'a6', [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'AssetRoot must be the project .thesis-build/assets/a6 directory.'
}
if (-not (Test-Path -LiteralPath (Split-Path $resolvedRoot -Parent) -PathType Container)) { throw 'Expected project build/assets parent is missing.' }
if ((Get-Item -LiteralPath (Split-Path $resolvedRoot -Parent)).Attributes -band [System.IO.FileAttributes]::ReparsePoint) { throw 'Asset parent must not be a link.' }
New-Item -ItemType Directory -Force -Path $resolvedRoot | Out-Null

foreach ($item in $items) {
    $destination = Join-Path $resolvedRoot $item.Path
    $parent = Split-Path $destination -Parent
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    if ((Get-Item -LiteralPath $parent).Attributes -band [System.IO.FileAttributes]::ReparsePoint) { throw "Linked asset directory: $parent" }
    if (Test-Path -LiteralPath $destination) {
        $existing = Get-Item -LiteralPath $destination
        if ($existing.Attributes -band [System.IO.FileAttributes]::ReparsePoint) { throw "Linked asset file: $destination" }
        if ($existing.Length -gt $item.Bytes) { throw "Oversized existing file: $destination" }
        if ($existing.Length -eq $item.Bytes) {
            $existingHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
            if (($item.Sha256 -and $existingHash -eq $item.Sha256) -or ($item.Prefix -and $existingHash.StartsWith($item.Prefix))) {
                Write-Output "VERIFIED_EXISTING $($item.Path) $($existing.Length) $existingHash"
                continue
            }
            throw "Full-size existing file has unexpected hash: $destination"
        }
    }
    Write-Output "DOWNLOADING $($item.Path) expected_bytes=$($item.Bytes)"
    & curl.exe --fail --location --retry 8 --retry-delay 10 --retry-all-errors --continue-at - --output $destination $item.Url
    if ($LASTEXITCODE -ne 0) { throw "curl failed for $($item.Path), exit=$LASTEXITCODE" }
    $actual = Get-Item -LiteralPath $destination
    if ($actual.Length -ne $item.Bytes) { throw "Size mismatch for $($item.Path): $($actual.Length) versus $($item.Bytes)" }
    $actualHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($item.Sha256 -and $actualHash -ne $item.Sha256) { throw "SHA-256 mismatch for $($item.Path): $actualHash" }
    if ($item.Prefix -and -not $actualHash.StartsWith($item.Prefix)) { throw "SHA-256 prefix mismatch for $($item.Path): $actualHash" }
    Write-Output "VERIFIED_DOWNLOADED $($item.Path) $($actual.Length) $actualHash"
}

Write-Output 'A6_CANDIDATE_WEIGHTS_VERIFIED (AlexNet has upstream prefix only; CLIP is separate)'
