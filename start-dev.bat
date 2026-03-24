@echo off
echo ========================================
echo  Fake News Detection System
echo  Starting Development Environment
echo ========================================
echo.

echo Checking if MongoDB is running...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] MongoDB is running
) else (
    echo [WARNING] MongoDB is not running!
    echo Please start MongoDB first:
    echo   - Run: net start MongoDB
    echo   - Or use MongoDB Atlas cloud database
    echo.
    echo Press any key to continue anyway...
    pause >nul
)

echo.
echo Starting all services...
echo - Frontend: http://localhost:3000
echo - Backend: http://localhost:5000
echo - AI API: http://localhost:5001
echo.

npm run dev
