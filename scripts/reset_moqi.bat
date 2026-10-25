@echo off
rem Reset Moqi IME to clean state WITHOUT uninstalling (2026-10-25):
rem   - kill backend (launcher first, it respawns the backend)
rem   - wipe user dictionary (rime_frost.userdb)
rem   - wipe grammar penalty cache
rem   - wipe logs
rem Keeps: install dir, IME registration, gram files in Roaming, other configs.
rem For between-round benchmark resets. ASCII only. Run as Administrator.

net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ABORT] Administrator rights required. Right-click and "Run as administrator".
    pause
    exit /b 1
)

echo ==== 1/3 kill processes ====
taskkill /IM MoqiLauncher.exe /F >nul 2>&1
taskkill /IM MoqiLaunch.exe  /F >nul 2>&1
taskkill /IM MoqiIME.exe     /F >nul 2>&1
timeout /t 2 /nobreak >nul

echo ==== 2/3 wipe user dict + penalty cache + logs ====
if exist "%APPDATA%\Moqi\Rime\rime_frost.userdb" rd /s /q "%APPDATA%\Moqi\Rime\rime_frost.userdb" 2>nul
if exist "%APPDATA%\Moqi\grammar_penalty_cache.json" del /f /q "%APPDATA%\Moqi\grammar_penalty_cache.json" 2>nul
if exist "%LOCALAPPDATA%\MoqiIM\Log" del /f /q "%LOCALAPPDATA%\MoqiIM\Log\*.log" >nul 2>&1

echo ==== 3/3 verify + restart backend ====
set OK=YES
if exist "%APPDATA%\Moqi\Rime\rime_frost.userdb" (
    echo   [DIR] userdb still present ^(held by backend?^)
    set OK=NO
)
if exist "%APPDATA%\Moqi\grammar_penalty_cache.json" (
    echo   [FILE] penalty cache still present
    set OK=NO
)
if "%OK%"=="YES" (
    start "" "C:\Program Files (x86)\MoqiIM\MoqiLaunch.exe"
    echo.
    echo ==== CLEAN. Backend restarting; wait ~30s before benchmark. ====
    echo ==== Gram files in Roaming are KEPT ^(wanxiang stays active^). ====
) else (
    echo.
    echo ==== Items above not cleaned. Run again, or log off / log on. ====
)
pause
