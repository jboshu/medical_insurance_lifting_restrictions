@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo    Offline Package Installer
echo ========================================
echo.

REM Check if Python is installed
echo [Step 0] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.6 or higher first.
    echo Download from: https://www.python.org/downloads/
    echo.
    echo During installation, make sure to check:
    echo "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Check if pip is available
echo [Step 0.5] Checking pip...
set PIP_CMD=pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [Warning] pip command not found, trying python -m pip...
    python -m pip --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Neither pip nor python -m pip is available!
        echo.
        echo Please ensure pip is installed with Python.
        echo You can install pip by running:
        echo     python -m ensurepip --upgrade
        echo.
        pause
        exit /b 1
    ) else (
        echo [OK] python -m pip is available (will use this)
        set PIP_CMD=python -m pip
    )
) else (
    echo [OK] pip is available
)
echo.

REM Check if offline_packages directory exists
if not exist "offline_packages" (
    echo [ERROR] offline_packages directory not found!
    echo Please run download_packages.bat on a computer with internet first.
    pause
    exit /b 1
)

echo [Step 1] Installing Python packages from offline packages...
echo Installing oracledb...
%PIP_CMD% install --no-index --find-links=offline_packages -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Package installation failed!
    echo.
    echo Try using alternative method:
    echo     python -m pip install --no-index --find-links=offline_packages -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo oracledb installed successfully!
echo.

echo [Step 2] Installing PyInstaller...
echo Installing PyInstaller...
%PIP_CMD% install --no-index --find-links=offline_packages pyinstaller
if errorlevel 1 (
    echo [Warning] PyInstaller installation may have failed, will try to build anyway...
)
echo.

echo ========================================
echo    Offline installation completed!
echo ========================================
echo.
echo Now you can run build_exe.bat to create the executable.
echo.
pause
