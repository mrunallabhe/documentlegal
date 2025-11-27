@echo off
echo ========================================
echo AI Crime Evidence Organizer Server
echo (with auto-reload for development)
echo ========================================
echo.
echo WARNING: On Windows, you may see KeyboardInterrupt errors
echo when stopping the server (CTRL+C). This is harmless and
echo does not affect server functionality.
echo.
echo Server will be available at: http://127.0.0.1:8000
echo API Documentation: http://127.0.0.1:8000/docs
echo Frontend: http://127.0.0.1:8000/static/index.html
echo.
echo Press CTRL+C to stop the server
echo.
echo ========================================
echo.

cd /d %~dp0
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

