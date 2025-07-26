@echo off
REM GitHub Repository Setup Script
REM Run this after creating your GitHub repository

echo =========================================
echo   GitHub Repository Setup
echo =========================================
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo Error: Please run this script from the project root directory
    pause
    exit /b 1
)

echo Current project directory: %CD%
echo.

REM Prompt for GitHub repository URL
set /p REPO_URL="Enter your GitHub repository URL (e.g., https://github.com/username/ai-study-assistant.git): "

if "%REPO_URL%"=="" (
    echo Error: Repository URL cannot be empty
    pause
    exit /b 1
)

echo.
echo Adding remote repository: %REPO_URL%
git remote add origin %REPO_URL%

echo.
echo Pushing to GitHub...
git branch -M main
git push -u origin main

echo.
echo =========================================
echo   Repository Setup Complete!
echo =========================================
echo.
echo Your AI Study Assistant is now on GitHub at:
echo %REPO_URL%
echo.
echo Next steps:
echo 1. Update the README.md with your actual repository URL
echo 2. Consider adding a LICENSE file
echo 3. Add repository topics/tags on GitHub for discoverability
echo.
pause
