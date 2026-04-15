@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo    Medical Insurance Tool - Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not detected. Please install Python 3.6 or higher.
    pause
    exit /b 1
)

echo [Info] Python is installed
echo.

REM Check if oracledb is installed
python -c "import oracledb" >nul 2>&1
if errorlevel 1 (
    echo [Warning] oracledb module not detected.
    echo.
    set /p install="Install oracledb now? (y/n): "
    if /i "%install%"=="y" (
        echo Installing oracledb...
        pip install oracledb
        if errorlevel 1 (
            echo [ERROR] Installation failed. Please run manually: pip install oracledb
            pause
            exit /b 1
        )
        echo oracledb installed successfully!
    ) else (
        echo [Info] Please install oracledb manually before running this program.
        pause
        exit /b 1
    )
) else (
    echo [Info] oracledb module is installed
)

echo.
echo ========================================
echo    Starting program...
echo ========================================
echo.

REM Run Python program
python "%~dp0oracle_db_tool.py"

if errorlevel 1 (
    echo.
    echo [ERROR] Program execution failed.
    pause
)
