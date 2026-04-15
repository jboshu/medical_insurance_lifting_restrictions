@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo    Build Executable (EXE) Tool
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller not detected!
    echo.
    echo Please run install_offline.bat first
    echo Or on a computer with internet: pip install pyinstaller
    pause
    exit /b 1
)

echo [Info] PyInstaller is installed
echo.

REM Clean old build files
if exist "build" (
    echo [Info] Cleaning old build files...
    rmdir /s /q build
)
if exist "dist" (
    rmdir /s /q dist
)
echo.

echo [Step 1] Starting to build executable...
echo This may take a few minutes, please wait...
echo.

pyinstaller --clean build.spec

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo.
    echo Common reasons:
    echo 1. Oracle Instant Client not properly installed
    echo 2. cx_Oracle module not properly installed
    echo 3. Python version mismatch with cx_Oracle
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Build successful!
echo ========================================
echo.
echo EXE file location: dist\医保限制解除工具.exe
echo.

REM Create release folder
if not exist "release" mkdir release

REM Copy EXE to release folder
copy "dist\医保限制解除工具.exe" "release\" >nul

REM Copy documentation
copy "README.md" "release\" >nul
copy "离线部署说明.txt" "release\" >nul 2>&1

echo [Info] EXE file copied to release folder
echo.
echo ========================================
echo    Important Notes
echo ========================================
echo.
echo 1. Oracle Instant Client is still required even with packaged EXE
echo 2. Make sure Oracle Instant Client is installed on target computer
echo 3. Copy files from release folder to target computer to use
echo.
echo Oracle Instant Client download:
echo https://www.oracle.com/database/technologies/instant-client/downloads.html
echo.
echo After download, extract to any directory and add to system PATH
echo.
pause
