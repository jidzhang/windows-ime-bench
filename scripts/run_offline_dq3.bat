@echo off
rem Offline clean-state bench: Doubao + Qianwen + QQ Pinyin (3 IMEs).
rem Double-click to run. User enables airplane mode themselves (no network guard).
rem Full wipe of ALL learning data for the 3 IMEs:
rem   Doubao : dict\usr*.dat + dict\engine_storage.leveldb + Account\dictionary-state.v1.json
rem   Qianwen: Rime\qw.userdb (fresh reinstall after 2026-11-17 uninstall)
rem   QQ     : users\public\dict\sgim_*usr*.bin + Backup\ + inputstat.dat
rem            (Backup dir restores the user dict - it MUST be wiped too)
rem Runs zhihu120 + words234 at 12ms key interval.
rem Results: results\run\offline_dq3\ + results\summary_offline_dq3.md
rem ASCII only - cmd.exe parses .bat as ANSI/GBK; UTF-8 Chinese breaks parsing.
setlocal
set ROOT=%~dp0..
set ENGINE=%ROOT%\engine\rime-schema-compare
set IMES=doubao_pinyin qianwen_pinyin qq_pinyin
set LABEL=offline_dq3
set OUTROOT=%ROOT%\results\run\%LABEL%
set LOG=%OUTROOT%\run_log.txt
if not exist "%OUTROOT%\sentences" mkdir "%OUTROOT%\sentences"
if not exist "%OUTROOT%\words" mkdir "%OUTROOT%\words"

rem Network is the user's responsibility (they enable airplane mode themselves).
rem No ping guard: ping hangs when the network stack is disabled.
echo ==== offline bench [%LABEL%] start %DATE% %TIME% delay=12ms >> "%LOG%"

rem ---- 1/2 stop background processes (best effort) ----
for %%P in (
    DoubaoIme.exe DoubaoImeServer.exe DoubaoImeService.exe
    QianwenIMEMaintenanceService.exe QianwenIMEServer.exe QianwenIMEUiClient.exe qianwenime_crashpad_handler.exe
    QQPYUserCenter.exe QQPYBroker.exe QQPYTask.exe QQPYToolbox.exe QQPYConfig.exe QQPYSnapshot.exe QQPYCloud.exe
    QQPYConfig.exe QQPYCloud.exe
) do taskkill /IM %%P /F >nul 2>&1
timeout /t 2 /nobreak >nul

set "LL=%USERPROFILE%\AppData\LocalLow"
set "QQD=C:\ProgramData\Tencent\QQPinyin\users\public"
echo ==== 2/2 wipe user dictionaries (locked files are skipped) ====

echo   [Doubao] ...
del /f /q "%APPDATA%\DoubaoIme\dict\usr*.dat" >nul 2>&1
del /f /q "%APPDATA%\DoubaoIme\dict\common_phrase_dict.dat" >nul 2>&1
del /f /q "%APPDATA%\DoubaoIme\dict\asr_user_ner_dict.dat" >nul 2>&1
rem usr*.dat alone is not enough: learning also lives in engine_storage.leveldb
rem (old 10-31/11-05 files survived the 11-17 wipe) and dictionary-state.
rd /s /q "%APPDATA%\DoubaoIme\dict\engine_storage.leveldb" >nul 2>&1
del /f /q "%APPDATA%\DoubaoIme\Account\dictionary-state.v1.json" >nul 2>&1

echo   [Qianwen] ...
rd /s /q "%APPDATA%\QianwenIME\Rime\qw.userdb" >nul 2>&1

echo   [QQ Pinyin] ...
del /f /q "%QQD%\dict\sgim_usr_v3new.bin" >nul 2>&1
del /f /q "%QQD%\dict\sgim_eng_usr.bin" >nul 2>&1
del /f /q "%QQD%\dict\sgim_ext.bin" >nul 2>&1
del /f /q "%QQD%\dict\sgim_jianabbr.bin" >nul 2>&1
del /f /q "%QQD%\dict\sgim_punc.bin" >nul 2>&1
del /f /q "%QQD%\dict\sgim_keymap.bin" >nul 2>&1
del /f /q "%QQD%\dict\Correction.ini" >nul 2>&1
del /f /q "%QQD%\dict\Fuzzy.dat" >nul 2>&1
rem Backup\ holds a copy of the user dict that QQ restores on next start.
rd /s /q "%QQD%\dict\Backup" >nul 2>&1
rem inputstat.dat = per-user input statistics (also learned, also must go).
del /f /q "%QQD%\inputstat.dat" >nul 2>&1
del /f /q "%QQD%\cdictlist.ini" >nul 2>&1
rd /s /q "C:\ProgramData\Tencent\QQPinyin\cdict\Temp" >nul 2>&1
rd /s /q "C:\ProgramData\Tencent\QQPinyin\cdict\tmp" >nul 2>&1
del /f /q "C:\ProgramData\Tencent\QQPinyin\cdict\*.qcel" >nul 2>&1

echo ==== clean status (LEFT = skipped, bench continues) ====
call :CHECK "%APPDATA%\DoubaoIme\dict\usr.dat" "Doubao usr.dat"
call :CHECK "%APPDATA%\DoubaoIme\dict\engine_storage.leveldb" "Doubao leveldb"
call :CHECK "%APPDATA%\QianwenIME\Rime\qw.userdb" "Qianwen userdb"
call :CHECK "%QQD%\dict\sgim_usr_v3new.bin" "QQ user dict"
call :CHECK "%QQD%\dict\Backup" "QQ backup dict"
call :CHECK "%QQD%\inputstat.dat" "QQ inputstat"

rem ---- bench at 12ms ----
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
    echo [ABORT] none of the 3 IMEs is enabled in the Windows language list.
    pause
    exit /b 1
)
set IMES=%NEWIMES%
for %%I in (%IMES%) do call :bench %%I

python "%ROOT%\scripts\collect_results.py" "%ROOT%" %LABEL%
echo ==== offline bench [%LABEL%] done %DATE% %TIME% >> "%LOG%"
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

:CHECK
if exist %1 (
    echo   [LEFT-skipped] %~2
) else (
    echo   [ OK ] %~2
)
goto :eof
