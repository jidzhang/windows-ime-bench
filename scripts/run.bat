@echo off
rem Full benchmark: every IME below x (120 sentences + 450 words).
rem All paths relative to this repository. Usage: run.bat <name>
rem   online test : run while connected          e.g.  run.bat online
rem   offline test: disconnect network / airplane mode first, then run
rem   (network is probed ONCE at start and logged; you control it yourself)
rem Results land in results\run\<name>\ and results\summary_<name>.md
setlocal
set ROOT=%~dp0..
set ENGINE=%ROOT%\engine\rime-schema-compare

rem ===== EDIT ME: IME list to test (keys must match installed TIPs) =====
set IMES=microsoft_pinyin sogou_pinyin wechat_pinyin baidu_pinyin iflytek_pinyin qq_pinyin google_pinyin doubao_pinyin qianwen_pinyin suyan_pinyin shuishan_pinyin moqi_pinyin shouxin_pinyin windinput_pinyin ximeyao_pinyin qingjian_pinyin huayu_pinyin
rem =======================================================================

set LABEL=%1
if "%LABEL%"=="" set /p LABEL=Enter a name for this run (e.g. online / offline):
if "%LABEL%"=="" exit /b 1

set OUTROOT=%ROOT%\results\run\%LABEL%
set LOG=%OUTROOT%\run_log.txt
if not exist "%OUTROOT%\sentences" mkdir "%OUTROOT%\sentences"
if not exist "%OUTROOT%\words"     mkdir "%OUTROOT%\words"

cd /d "%ENGINE%"
ping -n 1 -w 2000 223.5.5.5 >nul 2>&1
if %ERRORLEVEL%==0 (set NET0=True) else (set NET0=False)
echo ==== full bench [%LABEL%] start %DATE% %TIME% online=%NET0% >> "%LOG%"

rem Preflight: drop IMEs not installed/enabled so one missing IME cannot
rem abort the whole run. Full list kept in %OUTROOT%\preflight.txt.
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
    echo [ABORT] none of the requested IMEs is enabled in the Windows language list. Nothing to test.
    echo ==== full bench [%LABEL%] aborted: no IME enabled %DATE% %TIME% >> "%LOG%"
    pause
    exit /b 1
)
set IMES=%NEWIMES%

for %%I in (%IMES%) do call :bench %%I

python "%ROOT%\scripts\collect_results.py" "%ROOT%" %LABEL%
echo ==== full bench [%LABEL%] done %DATE% %TIME% >> "%LOG%"
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
rem --- words ---
echo ---- %IME% words %TIME% >> "%LOG%"
python -c "import sys; sys.path.insert(0,'src'); from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher; WindowsImeSwitcher().activate_profile('%IME%')" >nul 2>&1
python scripts\benchmark_windows_pinyin.py --ime %IME% --corpus data\corpus\words234.txt --min-hanzi 2 --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\words" 2>&1 | findstr /C:"not_confirmed" /C:"[RESULT]" /C:"[ABORT]" /C:"[SKIP]" >> "%LOG%"
goto :eof
