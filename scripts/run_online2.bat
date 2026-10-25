@echo off
rem Corrected-corpus retest (2026-10-24 evening): 16 competitor IMEs, moqi
rem excluded (tested separately per variant). Two passes: every IME sentences
rem first, then every IME words, so an interrupted run still leaves a complete
rem sentence column. Results: results\run\<label>\ + results\summary_<label>.md
setlocal
set ROOT=%~dp0..
set ENGINE=%ROOT%\engine\rime-schema-compare

set IMES=microsoft_pinyin sogou_pinyin wechat_pinyin baidu_pinyin iflytek_pinyin qq_pinyin google_pinyin doubao_pinyin qianwen_pinyin suyan_pinyin shuishan_pinyin shouxin_pinyin windinput_pinyin ximeyao_pinyin qingjian_pinyin huayu_pinyin

set LABEL=%1
if "%LABEL%"=="" set LABEL=online2
set OUTROOT=%ROOT%\results\run\%LABEL%
set LOG=%OUTROOT%\run_log.txt
if not exist "%OUTROOT%\sentences" mkdir "%OUTROOT%\sentences"
if not exist "%OUTROOT%\words"     mkdir "%OUTROOT%\words"

cd /d "%ENGINE%"
ping -n 1 -w 2000 223.5.5.5 >nul 2>&1
if %ERRORLEVEL%==0 (set NET0=True) else (set NET0=False)
echo ==== full bench [%LABEL%] start %DATE% %TIME% online=%NET0% >> "%LOG%"

python scripts\preflight_imes.py --extra-imes="%ROOT%\imes.json" %IMES% > "%OUTROOT%\preflight.txt"
type "%OUTROOT%\preflight.txt"
set NEWIMES=
for /f "tokens=1* delims==" %%A in ('findstr /B "OK_IMES=" "%OUTROOT%\preflight.txt"') do set NEWIMES=%%B
if "%NEWIMES%"=="" (
    echo [ABORT] none of the requested IMEs is enabled in the Windows language list.
    echo ==== full bench [%LABEL%] aborted: no IME enabled %DATE% %TIME% >> "%LOG%"
    exit /b 1
)
set IMES=%NEWIMES%

for %%I in (%IMES%) do call :sent %%I
for %%I in (%IMES%) do call :words %%I

python "%ROOT%\scripts\collect_results.py" "%ROOT%" %LABEL%
echo ==== full bench [%LABEL%] done %DATE% %TIME% >> "%LOG%"
type "%ROOT%\results\summary_%LABEL%.md"
endlocal
exit /b 0

:sent
set IME=%1
echo ---- %IME% sentences %TIME% >> "%LOG%"
python -c "import sys; sys.path.insert(0,'src'); from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher; WindowsImeSwitcher().activate_profile('%IME%')" >nul 2>&1
python scripts\benchmark_windows_pinyin.py --ime %IME% --corpus data\corpus\zhihu120.txt --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\sentences" 2>&1 | findstr /C:"not_confirmed" /C:"[RESULT]" /C:"[ABORT]" /C:"[SKIP]" >> "%LOG%"
goto :eof

:words
set IME=%1
echo ---- %IME% words %TIME% >> "%LOG%"
python -c "import sys; sys.path.insert(0,'src'); from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher; WindowsImeSwitcher().activate_profile('%IME%')" >nul 2>&1
python scripts\benchmark_windows_pinyin.py --ime %IME% --corpus data\corpus\words234.txt --min-hanzi 2 --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\words" 2>&1 | findstr /C:"not_confirmed" /C:"[RESULT]" /C:"[ABORT]" /C:"[SKIP]" >> "%LOG%"
goto :eof
