@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo    Prepare Offline Packages
echo ========================================
echo.
echo This script should be run on a computer WITH internet access.
echo It will download all required packages for offline installation.
echo.
pause

echo.
echo [Step 1] Creating offline_packages directory...
if not exist "offline_packages" mkdir offline_packages
echo Directory created.
echo.

echo [Step 2] Downloading oracledb and dependencies...
pip download oracledb -d offline_packages
if errorlevel 1 (
    echo [ERROR] Failed to download oracledb
    pause
    exit /b 1
)
echo oracledb downloaded successfully.
echo.

echo [Step 3] Downloading PyInstaller and dependencies...
pip download pyinstaller -d offline_packages
if errorlevel 1 (
    echo [WARNING] Failed to download PyInstaller
    echo You can install it manually later if needed
) else (
    echo PyInstaller downloaded successfully.
)
echo.

echo [Step 4] Verifying downloads...
if exist "offline_packages" (
    echo Contents of offline_packages:
    dir offline_packages /b
    echo.
) else (
    echo [ERROR] offline_packages directory not found!
    pause
    exit /b 1
)

echo ========================================
echo    Preparation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Copy the entire folder to USB drive
echo 2. Transfer to intranet computer
echo 3. On intranet computer, run: install_offline.bat
echo 4. Install Oracle Instant Client (see 内网部署指南.txt)
echo 5. Run the program: run.bat
echo.
pause
