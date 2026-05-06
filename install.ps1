# OpenBro Installation Script for PowerShell
# Download and run with: iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/lazarusrolando/OpenBro/main/install.ps1'))

# Colors for output
$Red = "\033[0;31m"
$Green = "\033[0;32m"
$Yellow = "\033[1;33m"
$NoColor = "\033[0m"

function Write-HostColor {
    param(
        [string]$Message,
        [string]$Color = $NoColor
    )
    Write-Host "$Color$Message$NoColor"
}

Write-HostColor "OpenBro Installation Script" $Yellow
Write-HostColor "============================" $Yellow

# Check Python version
try {
    $pythonVersion = python --version 2>$null
    if (-not $pythonVersion) {
        $pythonVersion = python3 --version 2>$null
    }
    if (-not $pythonVersion) {
        throw "Python not found"
    }
} catch {
    Write-HostColor "Error: Python 3.8+ is required but not found." $Red
    Write-HostColor "Please install Python 3.8 or higher from https://python.org" $Red
    exit 1
}

# Extract version numbers
if ($pythonVersion -match "Python (\d+\.\d+\.\d+)") {
    $versionStr = $matches[1]
} elseif ($pythonVersion -match "Python (\d+\.\d+)") {
    $versionStr = $matches[1]
} else {
    $versionStr = $pythonVersion.Split(" ")[1]
}

# Check if version is at least 3.8
$versionParts = $versionStr -split "\." | Select-Object -First 2
$major = [int]$versionParts[0]
$minor = [int]$versionParts[1]

if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
    Write-HostColor "Error: Python 3.8+ is required. You have: $pythonVersion" $Red
    exit 1
}

Write-HostColor "✓ Python version OK: $pythonVersion" $Green

# Create temporary directory for installation
$tempDir = [System.IO.Path]::GetTempPath()
$tempDir = Join-Path $tempDir ("OpenBro_Install_{0:yyyyMMdd_HHmmss}" -f (Get-Date))
New-Item -ItemType Directory -Path $tempDir | Out-Null
Write-HostColor "✓ Created temporary directory: $tempDir" $Green

try {
    # Clone the repository
    Write-HostColor "Cloning OpenBro repository..." $Yellow
    git clone https://github.com/lazarusrolando/OpenBro.git (Join-Path $tempDir "OpenBro")
    if (-not (Test-Path (Join-Path $tempDir "OpenBro"))) {
        throw "Failed to clone repository"
    }
    Write-HostColor "✓ Repository cloned successfully" $Green

    # Change to project directory
    Set-Location (Join-Path $tempDir "OpenBro")

    # Install dependencies
    Write-HostColor "Installing dependencies..." $Yellow
    pip install -r requirements-cpu.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install dependencies"
    }
    Write-HostColor "✓ Dependencies installed successfully" $Green

    # Install the package
    Write-HostColor "Installing OpenBro package..." $Yellow
    pip install -e .
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install OpenBro package"
    }
    Write-HostColor "✓ OpenBro installed successfully" $Green
} finally {
    # Clean up
    Set-Location /
    Remove-Item -Recurse -Force $tempDir
    Write-HostColor "✓ Cleaned up temporary files" $Green
}

# Success message
Write-HostColor ""
Write-HostColor "============================" $Green
Write-HostColor "OpenBro installed successfully!" $Green
Write-HostColor "============================" $Green
Write-HostColor ""
Write-HostColor "You can now run OpenBro from any terminal:" $NoColor
Write-HostColor "  openbro" $NoColor
Write-HostColor ""
Write-HostColor "Or to see help:" $NoColor
Write-HostColor "  openbro --help" $NoColor
Write-HostColor ""
Write-HostColor "To start chatting:" $NoColor
Write-HostColor "  openbro chat" $NoColor
Write-HostColor ""
Write-HostColor "To start training:" $NoColor
Write-HostColor "  openbro train" $NoColor
Write-HostColor ""
Write-HostColor "Enjoy your cyberpunk AI experience!" $Yellow