@echo off
echo ========================================================
echo  Jan-Sahayak AI (जन-सहायक) - Local Production Launcher
echo ========================================================
echo.
echo Starting FastAPI Web Server & Multi-Agent Swarm...
python -m uvicorn server:app --host 127.0.0.1 --port 8000
pause
