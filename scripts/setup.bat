@echo off
rem One-time setup. Prerequisites: git + python 3.10+ on PATH.
rem Everything lands inside the repository folder (engine\).
setlocal
set ROOT=%~dp0..
set ENGINE=%ROOT%\engine\rime-schema-compare

if exist "%ENGINE%\.git" (
    echo [1/3] engine already present, updating ...
    git -C "%ENGINE%" pull --ff-only
    if not %ERRORLEVEL%==0 echo [WARN] engine update failed, check network/proxy; continuing with current copy
    goto corpora
)

echo [1/3] cloning engine (patched fork, up to 3 attempts) ...
set ATTEMPT=0

:retry
set /a ATTEMPT+=1
git clone --depth 1 https://github.com/jidzhang/rime-schema-compare "%ENGINE%"
if %ERRORLEVEL%==0 goto corpora
if %ATTEMPT% GEQ 3 (
    echo clone failed after 3 attempts, check network/proxy
    pause
    exit /b 1
)
echo attempt %ATTEMPT% failed, retry in 5s ...
timeout /t 5 /nobreak >nul
rd /s /q "%ENGINE%" >nul 2>&1
goto retry

:corpora
echo [2/3] placing corpora ...
if not exist "%ENGINE%\data\corpus" mkdir "%ENGINE%\data\corpus"
copy /y "%ROOT%\corpus\zhihu120.txt"  "%ENGINE%\data\corpus\" >nul
copy /y "%ROOT%\corpus\words234.txt" "%ENGINE%\data\corpus\" >nul

echo [3/3] installing python deps (pypinyin, python-dotenv) ...
python -m pip install -q pypinyin python-dotenv

echo.
echo Setup done. Next: edit scripts\run.bat (IME list at top), then double-click it.
echo Repository folder: %ROOT%
pause
endlocal
