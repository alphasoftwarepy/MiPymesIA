@echo off
REM ============================================
REM MiPymesIA - Quick Deployment Script
REM ============================================

echo.
echo ============================================
echo   MiPymesIA - Deployment to GitHub
echo ============================================
echo.

REM Step 1: Run pre-deployment checks
echo [1/5] Running pre-deployment checks...
python pre_deploy_check.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Pre-deployment checks failed!
    echo Please fix the issues before deploying.
    pause
    exit /b 1
)

echo.
echo ============================================
echo.

REM Step 2: Export database schema (for documentation)
echo [2/5] Exporting database schema...
python export_db_schema.py
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Schema export failed, but continuing...
)

echo.
echo ============================================
echo.

REM Step 3: Show git status
echo [3/5] Current Git status:
git status

echo.
echo ============================================
echo.

REM Step 4: Confirm before proceeding
echo [4/5] Ready to commit and push changes?
echo.
echo This will:
echo   - Add all changes to git
echo   - Create a commit
echo   - Push to GitHub (origin/main)
echo.
set /p CONFIRM="Continue? (yes/no): "

if /i NOT "%CONFIRM%"=="yes" (
    echo.
    echo Deployment cancelled by user.
    pause
    exit /b 0
)

echo.
echo ============================================
echo.

REM Step 5: Git operations
echo [5/5] Committing and pushing to GitHub...

echo.
echo Adding files to git...
git add .

echo.
echo Creating commit...
set /p COMMIT_MSG="Enter commit message (or press Enter for default): "

if "%COMMIT_MSG%"=="" (
    set COMMIT_MSG=feat: Actualización completa del sistema - Mejoras en suscripciones, tareas, y generación de estrategias
)

git commit -m "%COMMIT_MSG%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Git commit failed!
    echo Check the error message above.
    pause
    exit /b 1
)

echo.
echo Pushing to GitHub...
git push origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Git push failed!
    echo You may need to pull changes first or resolve conflicts.
    echo.
    echo Try running: git pull origin main --rebase
    pause
    exit /b 1
)

echo.
echo ============================================
echo   SUCCESS! Code pushed to GitHub
echo ============================================
echo.
echo Next steps:
echo   1. Connect to your VPS
echo   2. Navigate to project directory
echo   3. Run: git pull origin main
echo   4. Run: python db_migrations.py
echo   5. Restart the application
echo.
echo See DEPLOY.md for detailed VPS deployment instructions.
echo.

pause
