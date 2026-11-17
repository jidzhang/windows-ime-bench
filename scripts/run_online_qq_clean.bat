@echo off
rem Online clean-state bench: QQ Pinyin ONLY (user re-tests offline tomorrow).
rem Double-click to run. ONLINE run (network stays up; cloud candidates allowed).
rem
rem QQ cleanup note (2026-11-17): QQ restores sgim_usr_v3new.bin from a process-held
rem copy seconds after deletion. We stop QQPYService + kill QQ helpers, wipe the
rem data, and START THE BENCH IMMEDIATELY (no explorer restart, no IME switch) to
rem minimise the window for QQ to write back. If the dict reappears mid-run the
rem result carries residual learning - flagged in the summary.
rem inputstat.dat could not be deleted (loaded into 8 processes incl. the shell);
rem it was renamed to inputstat.dat.old so QQ cannot read it on next start.
rem
rem Results: results\run\online_qq_clean\ + results\summary_online_qq_clean.md
rem ASCII only - cmd.exe parses .bat as ANSI/GBK; UTF-8 Chinese breaks parsing.
setlocal
set ROOT=%~dp0..
set ENGINE=%ROOT%\engine\rime-schema-compare
set IMES=qq_pinyin
set LABEL=online_qq_clean
set OUTROOT=%ROOT%\results\run\%LABEL%
set LOG=%OUTROOT%\run_log.txt
if not exist "%OUTROOT%\sentences" mkdir "%OUTROOT%\sentences"
if not exist "%OUTROOT%\words" mkdir "%OUTROOT%\words"

echo ==== online bench [%LABEL%] start %DATE% %TIME% delay=12ms >> "%LOG%"

rem ---- 1/2 stop QQ service + helpers, then wipe ----
net stop QQPYService /y >nul 2>&1
sc stop QQPYService >nul 2>&1
for %%P in (QQPYUserCenter.exe QQPYBroker.exe QQPYTask.exe QQPYToolbox.exe QQPYConfig.exe QQPYSnapshot.exe QQPYCloud.exe) do taskkill /IM %%P /F >nul 2>&1
timeout /t 1 /nobreak >nul

set "P=C:\ProgramData\Tencent\QQPinyin\users\public"
echo ==== 2/2 wipe QQ learned data ====
del /f /q "%P%\dict\sgim_usr_v3new.bin" >nul 2>&1
del /f /q "%P%\dict\sgim_eng_usr.bin" >nul 2>&1
del /f /q "%P%\dict\sgim_ext.bin" >nul 2>&1
del /f /q "%P%\dict\sgim_jianabbr.bin" >nul 2>&1
del /f /q "%P%\dict\sgim_punc.bin" >nul 2>&1
del /f /q "%P%\dict\sgim_keymap.bin" >nul 2>&1
del /f /q "%P%\dict\Correction.ini" >nul 2>&1
del /f /q "%P%\dict\Fuzzy.dat" >nul 2>&1
del /f /q "%P%\cdictlist.ini" >nul 2>&1
rd /s /q "%P%\dict\Backup" >nul 2>&1
rd /s /q "%P%\dict\Temp" >nul 2>&1
rd /s /q "C:\ProgramData\Tencent\QQPinyin\cdict\Temp" >nul 2>&1
rd /s /q "C:\ProgramData\Tencent\QQPinyin\cdict\tmp" >nul 2>&1
del /f /q "C:\ProgramData\Tencent\QQPinyin\cdict\*.qcel" >nul 2>&1
rem inputstat.dat: cannot be deleted (loaded into 8 live processes). Rename it so
rem QQ cannot read it; .old stays on disk for post-mortem.
if exist "%P%\inputstat.dat" ren "%P%\inputstat.dat" inputstat.dat.old >nul 2>&1

echo ==== clean status ====
if exist "%P%\dict\sgim_usr_v3new.bin" (echo   [LEFT] QQ user dict) else (echo   [ OK ] QQ user dict)
if exist "%P%\dict\Backup" (echo   [LEFT] QQ backup) else (echo   [ OK ] QQ backup)
if exist "%P%\inputstat.dat" (echo   [LEFT] QQ inputstat) else (echo   [ OK ] QQ inputstat)

rem ---- bench immediately (minimise QQ write-back window) ----
cd /d "%ENGINE%"
if not exist "%ENGINE%\scripts\preflight_imes.py" (
    echo [ABORT] test engine outdated ^(preflight_imes.py missing^). Run scripts\setup.bat.
    pause
    exit /b 1
)
python scripts\preflight_imes.py --extra-imes="%ROOT%\imes.json" %IMES% > "%OUTROOT%\preflight.txt"
type "%OUTROOT%\preflight.txt"
set NEWIMES=
for /f "tokens=1* delims==" %%A in ('findstr /B "OK_IMES=" "%OUTROOT%\preflight.txt"') do set NEWIMES=%%B
if "%NEWIMES%"=="" (
    echo [ABORT] neither IME is enabled in the Windows language list.
    pause
    exit /b 1
)
set IMES=%NEWIMES%
for %%I in (%IMES%) do call :bench %%I

rem ---- post-run: did QQ restore its dict? ----
echo ==== post-run QQ data check ====
if exist "%P%\dict\sgim_usr_v3new.bin" (
    echo   [WARN] QQ user dict reappeared during the run - result carries residual learning
    echo [WARN] QQ dict reappeared during run>> "%LOG%"
) else (
    echo   [ OK ] QQ user dict still absent
)
python "%ROOT%\scripts\collect_results.py" "%ROOT%" %LABEL%
echo ==== online bench [%LABEL%] done %DATE% %TIME% >> "%LOG%"
echo.
echo ===================== RESULTS =====================
type "%ROOT%\results\summary_%LABEL%.md"
echo ===================================================
pause
endlocal
exit /b 0

:bench
set IME=%1
echo ---- %IME% sentences %TIME% >> "%LOG%"
python -c "import sys; sys.path.insert(0,'src'); from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher; WindowsImeSwitcher().activate_profile('%IME%')" >nul 2>&1
python scripts\benchmark_windows_pinyin.py --ime %IME% --corpus data\corpus\zhihu120.txt --inter-key-delay-ms 12 --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\sentences" 2>&1 | findstr /C:"not_confirmed" /C:"[RESULT]" /C:"[ABORT]" /C:"[SKIP]" >> "%LOG%"
echo ---- %IME% words %TIME% >> "%LOG%"
python -c "import sys; sys.path.insert(0,'src'); from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher; WindowsImeSwitcher().activate_profile('%IME%')" >nul 2>&1
python scripts\benchmark_windows_pinyin.py --ime %IME% --corpus data\corpus\words234.txt --min-hanzi 2 --inter-key-delay-ms 12 --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\words" 2>&1 | findstr /C:"not_confirmed" /C:"[RESULT]" /C:"[ABORT]" /C:"[SKIP]" >> "%LOG%"
goto :eof
