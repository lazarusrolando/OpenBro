@echo off
:: OpenBro Installation Script for Windows Batch
:: Download and run with: powershell -Command "Invoke-WebRequest -Uri https://raw.githubusercontent.com/lazarusrolando/OpenBro/main/install.bat -UseBasicParsing | Invoke-Expression"

:: Colors for output (requires Windows 10+ or ANSI enabled)
:: For older Windows, colors may not work
set "RED=\033[0;31m"
set "GREEN=\033[0;32m"
set "YELLOW=\033[1;33m"
set "NC=\033[0m" :: No Color

echo %YELLOW%
echo OpenBro Installation Script
echo ============================
echo %NC%

:: Check Python version
for /f %%v in ('python --version 2^>nul') do set "PYTHON_VERSION=%%v"
if not defined PYTHON_VERSION (
    for /f %%v in ('python3 --version 2^>nul') do set "PYTHON_VERSION=%%v"
)
if not defined PYTHON_VERSION (
    echo %RED%Error: Python 3.8+ is required but not found.%NC%
    echo Please install Python 3.8 or higher from https://python.org
    exit /b 1
)

:: Extract version numbers
for /f "tokens=2" %%v in ("%PYTHON_VERSION%") do set "PYTHON_VER=%%v"
set "MAJOR=%PYTHON_VER:~0,1%"
set "MINOR=%PYTHON_VER:~2,1%"

:: Check if version is at least 3.8
if %MAJOR% LSS 3 (
    echo %RED%Error: Python 3.8+ is required. You have: %PYTHON_VERSION%%NC%
    exit /b 1
)
if %MAJOR% EQU 3 (
    if %MINOR% LSS 8 (
        echo %RED%Error: Python 3.8+ is required. You have: %PYTHON_VERSION%%NC%
        exit /b 1
    )
)

echo %GREEN%✓ Python version OK: %PYTHON_VERSION%%NC%

:: Create temporary directory for installation
set "TEMP_DIR=%TEMP%\OpenBro_Install_%RANDOM%"
mkdir "%TEMP_DIR%"
if not exist "%TEMP_DIR%" (
    echo %RED%Error: Failed to create temporary directory%NC%
    exit /b 1
)
echo %GREEN%✓ Created temporary directory: %TEMP_DIR%%NC%

:: Clone the repository
echo %YELLOW%Cloning OpenBro repository...%NC%
git clone https://github.com/lazarusrolando/OpenBro.git "%TEMP_DIR%\OpenBro"
if errorlevel 1 (
    echo %RED%Error: Failed to clone repository%NC%
    rmdir /s /q "%TEMP_DIR%"
    exit /b 1
)
echo %GREEN%✓ Repository cloned successfully%NC%

:: Change to project directory
cd /d "%TEMP_DIR%\OpenBro"

:: Install dependencies
echo %YELLOW%Installing dependencies...%NC%
pip install -r requirements-cpu.txt
if errorlevel 1 (
    echo %RED%Error: Failed to install dependencies%NC%
    cd /d %
    rmdir /s /q "%TEMP_DIR%"
    exit /b 1
)
echo %GREEN%✓ Dependencies installed successfully%NC%

:: Install the package
echo %YELLOW%Installing OpenBro package...%NC%
pip install -e .
if errorlevel 1 (
    echo %RED%Error: Failed to install OpenBro package%NC%
    cd /d %
    rmdir /s /q "%TEMP_DIR%"
    exit /b 1
)
echo %GREEN%✓ OpenBro installed successfully%NC%

:: Clean up
cd /d %
rmdir /s /q "%TEMP_DIR%"
echo %GREEN%✓ Cleaned up temporary files%NC%

:: Success message
echo %GREEN%
echo ============================
echo OpenBro installed successfully!
echo ============================
echo %NC%
echo You can now run OpenBro from any terminal:
echo   openbro
echo.
echo Or to see help:
echo   openbro --help
echo.
echo To start chatting:
echo   openbro chat
echo.
echo To start training:
echo   openbro train
echo.
echo %YELLOW%Enjoy your cyberpunk AI experience!%NC%