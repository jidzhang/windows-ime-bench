@echo off
rem Offline-only run for Sogou (sentences + words).
rem Precondition: Sogou (re)installed and healthy (shared dicts under
rem ProgramData\SogouInput intact), airplane mode ON, network unreachable.
rem It refuses to run while the network is up, so the "offline" label
rem stays honest. Results: results\run\offline_sogou\ + summary_offline_sogou.md
setlocal
set ROOT=%~dp0..
set ENGINE=%ROOT%\engine\rime-schema-compare
set LABEL=offline_sogou
set OUTROOT=%ROOT%\results\run\%LABEL%
set LOG=%OUTROOT%\run_log.txt

if not exist "%OUTROOT%\sentences" mkdir "%OUTROOT%\sentences"
if not exist "%OUTROOT%\words"     mkdir "%OUTROOT%\words"

ping -n 1 -w 2000 223.5.5.5 >nul 2>&1
if not errorlevel 1 goto online

echo ==== sogou offline bench [%LABEL%] start %DATE% %TIME% online=False >> "%LOG%"
cd /d "%ENGINE%"

echo.
echo [1/2] Sentences: zhihu120, 120 items, about 5 minutes...
python scripts\benchmark_windows_pinyin.py --ime sogou_pinyin --corpus data\corpus\zhihu120.txt --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\sentences" 2>&1 | findstr /C:"[RESULT]" /C:"[ABORT]" /C:"not_confirmed" >> "%LOG%"
if errorlevel 1 echo [WARN] sentences run returned an error, check latest report in %OUTROOT%\sentences
echo ---- sentences done %TIME% >> "%LOG%"

echo.
echo [2/2] Words: words234, 450 items, about 5 minutes...
python scripts\benchmark_windows_pinyin.py --ime sogou_pinyin --corpus data\corpus\words234.txt --min-hanzi 2 --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\words" 2>&1 | findstr /C:"[RESULT]" /C:"[ABORT]" /C:"not_confirmed" >> "%LOG%"
if errorlevel 1 echo [WARN] words run returned an error, check latest report in %OUTROOT%\words
echo ---- words done %TIME% >> "%LOG%"

python "%ROOT%\scripts\collect_results.py" "%ROOT%" %LABEL%
echo ==== sogou offline bench [%LABEL%] done %DATE% %TIME% >> "%LOG%"

echo.
echo ===================== SUMMARY =====================
type "%ROOT%\results\summary_%LABEL%.md"
echo ==================================================
echo.
echo Offline run finished. You can turn the network back on now.
echo Tell the agent the run is done so the report gets updated.
pause
exit /b 0

:online
echo.
echo [ABORT] The network is still reachable.
echo Reinstall Sogou first if you have not, then turn on airplane mode
echo (or unplug Ethernet), then run this file again. No test was started.
pause
exit /b 1
