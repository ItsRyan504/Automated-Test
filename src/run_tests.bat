@echo off
echo ============================================
echo  JazSam / SalesPresso - Automated Test Suite
echo ============================================
echo.

cd /d "%~dp0"

echo [1/2] Installing dependencies...
pip install -r requirements.txt -q

echo.
echo [2/2] Running all tests...
echo.

python -m pytest -v -s --tb=short 2>&1

echo.
echo Done! See results above.
pause
