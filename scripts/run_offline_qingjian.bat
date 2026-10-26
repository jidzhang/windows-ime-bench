@echo off
rem Offline-only run for Qingjian (sentences + words).
rem Usage: turn on airplane mode / disconnect network, then double-click this file.
rem It refuses to run if the network is still reachable, so the "offline" label stays honest.
setlocal
set ROOT=%~dp0..
set ENGINE=%ROOT%\engine\rime-schema-compare
set LABEL=offline_qingjian
set OUTROOT=%ROOT%\results\run\%LABEL%
set LOG=%OUTROOT%\run_log.txt

if not exist "%OUTROOT%\sentences" mkdir "%OUTROOT%\sentences"
if not exist "%OUTROOT%\words"     mkdir "%OUTROOT%\words"

ping -n 1 -w 2000 223.5.5.5 >nul 2>&1
if not errorlevel 1 goto online

echo ==== qingjian offline bench start %DATE% %TIME% online=False >> "%LOG%"
cd /d "%ENGINE%"

echo.
echo [1/2] Sentences (zhihu120, 120 items, about 3 minutes)...
python scripts\benchmark_windows_pinyin.py --ime qingjian_pinyin --corpus data\corpus\zhihu120.txt --out-dir "%OUTROOT%\sentences" 2> "%OUTROOT%\sentences\stderr.log"
if errorlevel 1 echo [WARN] sentences run returned an error, see stderr.log
echo ---- sentences done %TIME% >> "%LOG%"

echo.
echo [2/2] Words (words234, 450 items, about 7 minutes)...
python scripts\benchmark_windows_pinyin.py --ime qingjian_pinyin --corpus data\corpus\words234.txt --min-hanzi 2 --out-dir "%OUTROOT%\words" 2> "%OUTROOT%\words\stderr.log"
if errorlevel 1 echo [WARN] words run returned an error, see stderr.log
echo ---- words done %TIME% >> "%LOG%"

python "%ROOT%\scripts\collect_results.py" "%ROOT%" %LABEL%
echo ==== qingjian offline bench done %DATE% %TIME% >> "%LOG%"

echo.
echo ===================== SUMMARY =====================
type "%ROOT%\results\summary_%LABEL%.md"
echo ===================================================
echo.
echo Offline run finished. You can turn airplane mode off now.
pause
exit /b 0

:online
echo.
echo [ABORT] The network is still reachable.
echo Turn on airplane mode (or unplug Ethernet) and run this file again.
echo No test was started.
pause
exit /b 1
