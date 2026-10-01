@echo off
echo ========================================================
echo  Jan-Sahayak AI - Pushing Code to GitHub Repository
echo  Target: https://github.com/pyharshcodes/Bharat_Agentic_2026_Hackathon
echo  Team: Bits and Bytes (Harsh Deep Chak & Pallak Devi)
echo ========================================================
echo.
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo ========================================================
    echo  SUCCESS! Repository successfully pushed to GitHub!
    echo ========================================================
) else (
    echo ========================================================
    echo  If browser login appeared, please authorize and re-run.
    echo ========================================================
)
pause
