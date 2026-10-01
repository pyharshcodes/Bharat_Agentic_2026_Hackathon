@echo off
echo ========================================================
echo  Jan-Sahayak AI - Docker Build & Run Helper
echo ========================================================
echo.
echo Building Docker image 'docker.io/bharatagentic/jan-sahayak:1.0.0'...
docker build -t docker.io/bharatagentic/jan-sahayak:1.0.0 .
echo.
echo Testing Container Sandbox Execution...
docker run --rm docker.io/bharatagentic/jan-sahayak:1.0.0
echo.
pause
