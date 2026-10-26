@echo off
rem Offline-only run for WeType / WeChat Pinyin (sentences + words).
rem Precondition: network unreachable (airplane mode ON).
rem It refuses to run while the network is up, so the "offline" label
rem stays honest. Results: results\run\offline_wechat\ + summary_offline_wechat.md
rem Note: this run does NOT reset WeType data on purpose - run
rem scripts\reset_all_imes.bat BEFORE reconnecting/disconnecting if you
rem want the clean-initial-state comparison to match the 10-25 offline round.
setlocal
set ROOT=%~dp0..
set ENGINE=%ROOT%\engine\rime-schema-compare
set LABEL=offline_wechat
set OUTROOT=%ROOT%\results\run\%LABEL%
set LOG=%OUTROOT%\run_log.txt

if not exist "%OUTROOT%\sentences" mkdir "%OUTROOT%\sentences"
if not exist "%OUTROOT%\words"     mkdir "%OUTROOT%\words"

ping -n 1 -w 2000 223.5.5.5 >nul 2>&1
if not errorlevel 1 goto online

echo ==== wechat offline bench [%LABEL%] start %DATE% %TIME% online=False >> "%LOG%"
cd /d "%ENGINE%"

echo.
echo [1/2] Sentences: zhihu120, 120 items, about 6 minutes...
python scripts\benchmark_windows_pinyin.py --ime wechat_pinyin --corpus data\corpus\zhihu120.txt --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\sentences" 2>&1 | findstr /C:"[RESULT]" /C:"[ABORT]" /C:"not_confirmed" >> "%LOG%"
if errorlevel 1 echo [WARN] sentences run returned an error, check latest report in %OUTROOT%\sentences
echo ---- sentences done %TIME% >> "%LOG%"

echo.
echo [2/2] Words: words234, 450 items, about 6 minutes...
python scripts\benchmark_windows_pinyin.py --ime wechat_pinyin --corpus data\corpus\words234.txt --min-hanzi 2 --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\words" 2>&1 | findstr /C:"[RESULT]" /C:"[ABORT]" /C:"not_confirmed" >> "%LOG%"
if errorlevel 1 echo [WARN] words run returned an error, check latest report in %OUTROOT%\words
echo ---- words done %TIME% >> "%LOG%"

python "%ROOT%\scripts\collect_results.py" "%ROOT%" %LABEL%
echo ==== wechat offline bench [%LABEL%] done %DATE% %TIME% >> "%LOG%"

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
echo Turn on airplane mode (or unplug Ethernet) and run this file again.
echo No test was started.
pause
exit /b 1
