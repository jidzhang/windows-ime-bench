@echo off
rem Moqi sentence-ONLY benchmark (2026-10-25): zhihu120, no words phase.
rem Same usage/labels/output layout as run_moqi.bat, ~3 min per run.
rem Keep this file ASCII-only (cmd.exe reads .bat as ANSI).
setlocal
set ROOT=%~dp0..
set ENGINE=%ROOT%\engine\rime-schema-compare

set IMES=moqi_pinyin

set LABEL=%1
if "%LABEL%"=="" set /p LABEL=Enter a name for this run (one per installer package, e.g. pkg1):
if "%LABEL%"=="" exit /b 1

set OUTROOT=%ROOT%\results\run\%LABEL%
set LOG=%OUTROOT%\run_log.txt
if not exist "%OUTROOT%\sentences" mkdir "%OUTROOT%\sentences"

cd /d "%ENGINE%"
ping -n 1 -w 2000 223.5.5.5 >nul 2>&1
if %ERRORLEVEL%==0 (set NET0=True) else (set NET0=False)
echo ==== moqi sentence-only bench [%LABEL%] start %DATE% %TIME% online=%NET0% >> "%LOG%"

python scripts\preflight_imes.py --extra-imes="%ROOT%\imes.json" %IMES% > "%OUTROOT%\preflight.txt"
type "%OUTROOT%\preflight.txt"
set NEWIMES=
for /f "tokens=1* delims==" %%A in ('findstr /B "OK_IMES=" "%OUTROOT%\preflight.txt"') do set NEWIMES=%%B
if "%NEWIMES%"=="" (
    echo [ABORT] moqi_pinyin is not enabled in the Windows language list.
    echo ==== moqi bench [%LABEL%] aborted: moqi not enabled %DATE% %TIME% >> "%LOG%"
    pause
    exit /b 1
)
set IMES=%NEWIMES%

for %%I in (%IMES%) do call :bench %%I

echo ==== moqi sentence-only bench [%LABEL%] done %DATE% %TIME% >> "%LOG%"
echo.
echo ===================== RESULTS (this run) =====================
rem Show the LAST [RESULT] line in the log (= this run; earlier ones are
rem history from previous runs with the same label).
rem Print this run's score as a percentage and write the per-run summary
rem (helper does both; batch token-splitting is fragile, keep it out of cmd).
rem NOTE: cwd is the ENGINE dir here; the helper lives next to this .bat.
python "%~dp0print_last_score.py" "%LOG%" "%ROOT%\results\summary_%LABEL%_sent.md" %LABEL%
echo ==================================================
echo This run:    %ROOT%\results\summary_%LABEL%_sent.md
echo Full history: %LOG%
echo ==================================================
pause
endlocal
exit /b 0

:bench
set IME=%1
echo ---- %IME% sentences %TIME% >> "%LOG%"
python -c "import sys; sys.path.insert(0,'src'); from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher; WindowsImeSwitcher().activate_profile('%IME%')" >nul 2>&1
python scripts\benchmark_windows_pinyin.py --ime %IME% --corpus data\corpus\zhihu120.txt --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\sentences" 2>&1 | findstr /C:"not_confirmed" /C:"[RESULT]" /C:"[ABORT]" /C:"[SKIP]" >> "%LOG%"
goto :eof
