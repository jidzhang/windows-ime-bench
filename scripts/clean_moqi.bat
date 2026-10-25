@echo off
rem Moqi IME full cleanup (2026-10-25): uninstall + wipe all user data dirs.
rem For absolutely-clean black-box benchmark runs.
rem IMPORTANT: keep this file ASCII-only. cmd.exe reads .bat as ANSI/GBK;
rem UTF-8 Chinese text becomes mojibake and breaks line parsing (2026-10-25
rem incident: fragments of comments got executed as commands).
rem Run as Administrator.

net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ABORT] Administrator rights required. Right-click and "Run as administrator".
    pause
    exit /b 1
)

echo ==== 1/4 kill processes (launcher FIRST, it respawns the backend) ====
taskkill /IM MoqiLauncher.exe /F >nul 2>&1
taskkill /IM MoqiLaunch.exe  /F >nul 2>&1
taskkill /IM MoqiIME.exe     /F >nul 2>&1
timeout /t 2 /nobreak >nul

echo ==== 2/4 silent uninstall ====
set "UNINST=C:\Program Files (x86)\MoqiIM\unins000.exe"
if exist "%UNINST%" (
    "%UNINST%" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
    echo uninstaller exit code %ERRORLEVEL%
) else (
    echo [WARN] uninstaller not found, maybe already uninstalled, skip.
)

echo ==== 3/4 wipe leftover directories ====
if exist "C:\Program Files (x86)\MoqiIM" rd /s /q "C:\Program Files (x86)\MoqiIM" 2>nul
if exist "C:\Users\TEST\AppData\Roaming\Moqi" rd /s /q "C:\Users\TEST\AppData\Roaming\Moqi" 2>nul
if exist "C:\Users\TEST\AppData\Local\MoqiIM" rd /s /q "C:\Users\TEST\AppData\Local\MoqiIM" 2>nul

echo ==== 4/4 verify ====
set CLEAN=YES
if exist "C:\Program Files (x86)\MoqiIM" (
    echo   [DIR] Program Files\MoqiIM still present
    set CLEAN=NO
)
if exist "C:\Users\TEST\AppData\Roaming\Moqi" (
    echo   [DIR] Roaming\Moqi still present
    set CLEAN=NO
)
if exist "C:\Users\TEST\AppData\Local\MoqiIM" (
    echo   [DIR] Local\MoqiIM still present
    set CLEAN=NO
)
tasklist | findstr /i "MoqiIME MoqiLaunch MoqiLauncher" >nul 2>&1
if not ERRORLEVEL 1 (
    echo   [PROC] Moqi processes still running
    set CLEAN=NO
)

if "%CLEAN%"=="YES" (
    echo.
    echo ==== CLEAN: all dirs removed, all processes stopped. Ready to install. ====
) else (
    echo.
    echo ==== Items listed above are NOT cleaned ^(likely held by explorer/IME host^).
    echo ==== Log off, log back on, run this script again to finish. ====
)
pause
