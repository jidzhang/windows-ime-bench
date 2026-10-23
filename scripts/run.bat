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
set IMES=microsoft_pinyin sogou_pinyin wechat_pinyin baidu_pinyin iflytek_pinyin qq_pinyin google_pinyin doubao_pinyin qianwen_pinyin suyan_pinyin shuishan_pinyin moqi_pinyin shouxin_pinyin windinput_pinyin
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

for %%I in (%IMES%) do call :bench %%I

python "%ROOT%\scripts\collect_results.py" "%ROOT%" %LABEL%
echo ==== full bench [%LABEL%] done %DATE% %TIME% >> "%LOG%"
echo.
echo Done. Results: results\run\%LABEL%\ and results\summary_%LABEL%.md
endlocal
exit /b 0

:bench
set IME=%1
rem --- sentences ---
echo ---- %IME% sentences %TIME% >> "%LOG%"
python -c "import sys; sys.path.insert(0,'src'); from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher; WindowsImeSwitcher().activate_profile('%IME%')" >nul 2>&1
python scripts\benchmark_windows_pinyin.py --ime %IME% --corpus data\corpus\zhihu120.txt --out-dir "%OUTROOT%\sentences" 2>&1 | findstr /C:"not_confirmed" >> "%LOG%"
rem --- words ---
echo ---- %IME% words %TIME% >> "%LOG%"
python -c "import sys; sys.path.insert(0,'src'); from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher; WindowsImeSwitcher().activate_profile('%IME%')" >nul 2>&1
python scripts\benchmark_windows_pinyin.py --ime %IME% --corpus data\corpus\words234.txt --min-hanzi 2 --out-dir "%OUTROOT%\words" 2>&1 | findstr /C:"not_confirmed" >> "%LOG%"
goto :eof
