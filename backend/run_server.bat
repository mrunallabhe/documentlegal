@echo off
echo ========================================
echo AI Crime Evidence Organizer Server
echo (Recommended for Windows - no reload)
echo ========================================
echo.
echo Server will be available at: http://127.0.0.1:8000
echo API Documentation: http://127.0.0.1:8000/docs
echo Frontend: http://127.0.0.1:8000/static/index.html
echo.
echo Note: This version does NOT auto-reload on code changes.
echo Use run_server_reload.bat if you need auto-reload.
echo.
echo Press CTRL+C to stop the server
echo.
echo ========================================
echo.

cd /d %~dp0
uvicorn app.main:app --host 127.0.0.1 --port 8000

