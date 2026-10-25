@echo off
rem Moqi-only benchmark: moqi_pinyin x (120 sentences + 450 words).
rem For installer-package testing: install ONE package, then run this with a
rem per-package label so the 3 packages' results never overwrite each other.
rem   e.g.  run_moqi.bat pkg1     run_moqi.bat pkg2     run_moqi.bat pkg3
rem Results land in results\run\<label>\ and results\summary_<label>.md
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
if not exist "%OUTROOT%\words"     mkdir "%OUTROOT%\words"

cd /d "%ENGINE%"
ping -n 1 -w 2000 223.5.5.5 >nul 2>&1
if %ERRORLEVEL%==0 (set NET0=True) else (set NET0=False)
echo ==== moqi bench [%LABEL%] start %DATE% %TIME% online=%NET0% >> "%LOG%"

rem Preflight: abort with a clear message if the package under test did not
rem leave moqi installed AND ticked in the Windows language list.
if not exist "%ENGINE%\scripts\preflight_imes.py" (
    echo [ABORT] test engine is outdated ^(preflight_imes.py missing^).
    echo Fix: run scripts\setup.bat again ^(it updates the engine^), or manually:
    echo     git -C engine\rime-schema-compare pull
    pause
    exit /b 1
)
python scripts\preflight_imes.py --extra-imes="%ROOT%\imes.json" %IMES% > "%OUTROOT%\preflight.txt"
type "%OUTROOT%\preflight.txt"
set NEWIMES=
for /f "tokens=1* delims==" %%A in ('findstr /B "OK_IMES=" "%OUTROOT%\preflight.txt"') do set NEWIMES=%%B
if "%NEWIMES%"=="" (
    echo [ABORT] moqi_pinyin is not enabled in the Windows language list.
    echo If the installer was supposed to enable it, this run is the evidence: check the package.
    echo ==== moqi bench [%LABEL%] aborted: moqi not enabled %DATE% %TIME% >> "%LOG%"
    pause
    exit /b 1
)
set IMES=%NEWIMES%

for %%I in (%IMES%) do call :bench %%I

python "%ROOT%\scripts\collect_results.py" "%ROOT%" %LABEL%
echo ==== moqi bench [%LABEL%] done %DATE% %TIME% >> "%LOG%"
echo.
echo ===================== RESULTS =====================
type "%ROOT%\results\summary_%LABEL%.md"
echo.
echo ===================================================
echo Score summary ^(open this file^):  %ROOT%\results\summary_%LABEL%.md
echo Per-IME raw results:               %OUTROOT%\sentences   %OUTROOT%\words
echo Run log:                           %OUTROOT%\run_log.txt
echo ===================================================
pause
endlocal
exit /b 0

:bench
set IME=%1
rem --- sentences ---
echo ---- %IME% sentences %TIME% >> "%LOG%"
python -c "import sys; sys.path.insert(0,'src'); from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher; WindowsImeSwitcher().activate_profile('%IME%')" >nul 2>&1
python scripts\benchmark_windows_pinyin.py --ime %IME% --corpus data\corpus\zhihu120.txt --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\sentences" 2>&1 | findstr /C:"not_confirmed" /C:"[RESULT]" /C:"[ABORT]" /C:"[SKIP]" >> "%LOG%"
rem --- words (skipped 2026-10-25: sentence-only mode for faster per-package
rem     runs; word level has been 100% on every package, no information left) ---
rem echo ---- %IME% words %TIME% >> "%LOG%"
rem python -c "import sys; sys.path.insert(0,'src'); from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher; WindowsImeSwitcher().activate_profile('%IME%')" >nul 2>&1
rem python scripts\benchmark_windows_pinyin.py --ime %IME% --corpus data\corpus\words234.txt --min-hanzi 2 --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\words" 2>&1 | findstr /C:"not_confirmed" /C:"[RESULT]" /C:"[ABORT]" /C:"[SKIP]" >> "%LOG%"
goto :eof
