@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo    Python Environment Check
echo ========================================
echo.

echo [Check 1] Testing python command...
python --version 2>&1
if errorlevel 1 (
    echo [FAIL] python command not found
    echo.
    echo Python is NOT installed or NOT in PATH
    echo.
    goto :install_python
) else (
    echo [OK] python command works
)
echo.

echo [Check 2] Testing pip command...
pip --version 2>&1
if errorlevel 1 (
    echo [FAIL] pip command not found
    echo.
    echo Trying alternative method...
    python -m pip --version 2>&1
    if errorlevel 1 (
        echo [FAIL] python -m pip also not working
        echo.
        echo pip is NOT available
        echo.
        goto :fix_pip
    ) else (
        echo [OK] python -m pip works (use this instead of pip)
    )
) else (
    echo [OK] pip command works
)
echo.

echo [Check 3] Python installation path...
where python 2>nul
echo.

echo [Check 4] pip installation path...
where pip 2>nul
if errorlevel 1 (
    echo pip not found in PATH
)
echo.

echo ========================================
echo    Environment Check Complete
echo ========================================
echo.
echo If all checks passed, you can run:
echo     install_offline.bat
echo.
pause
exit /b 0

:install_python
echo ========================================
echo    Python Installation Required
echo ========================================
echo.
echo Steps to install Python:
echo.
echo 1. Download Python from:
echo    https://www.python.org/downloads/
echo.
echo 2. Choose Python 3.8 or higher (recommended: 3.11 or 3.12)
echo.
echo 3. Run the installer
echo    IMPORTANT: Check the box "Add Python to PATH"
echo.
echo 4. Click "Install Now"
echo.
echo 5. After installation, restart this script
echo.
pause
exit /b 1

:fix_pip
echo ========================================
echo    Fixing pip Installation
echo ========================================
echo.
echo Try these solutions:
echo.
echo Solution 1: Reinstall pip
echo     python -m ensurepip --upgrade
echo.
echo Solution 2: Use python -m pip instead of pip
echo     python -m pip install --no-index --find-links=offline_packages -r requirements.txt
echo.
echo Solution 3: Get pip from official site
echo     curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
echo     python get-pip.py
echo.
pause
exit /b 1
