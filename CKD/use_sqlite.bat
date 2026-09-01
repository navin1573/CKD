@echo off
echo Clearing MySQL environment variables to use SQLite...
set USE_MYSQL=
set DB_NAME=
set DB_USER=
set DB_PASSWORD=
set DB_HOST=
set DB_PORT=
echo Environment variables cleared. Using SQLite for local development.
echo.
echo Starting Django server...
cd ckd_backend
..\.venv\Scripts\python.exe manage.py runserver
pause
