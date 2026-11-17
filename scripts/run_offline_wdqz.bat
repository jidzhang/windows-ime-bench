@echo off
rem Offline clean-state bench: WeChat + Doubao + Qianwen + Zhongwen(Bing keyboard).
rem Double-click to run. User enables airplane mode themselves (no network guard).
rem Best-effort wipe of the 4 IMEs' user dicts; a locked file is SKIPPED with a
rem warning and the bench still runs (never aborts on a locked dict).
rem Runs zhihu120 + words234 at 12ms key interval (avoids Doubao passthrough).
rem Results: results\run\offline_wdqz\ + results\summary_offline_wdqz.md
rem ASCII only - cmd.exe parses .bat as ANSI/GBK; UTF-8 Chinese breaks parsing.
setlocal
set ROOT=%~dp0..
set ENGINE=%ROOT%\engine\rime-schema-compare
set IMES=wechat_pinyin doubao_pinyin qianwen_pinyin zhongwen_pinyin
set LABEL=offline_wdqz
set OUTROOT=%ROOT%\results\run\%LABEL%
set LOG=%OUTROOT%\run_log.txt
if not exist "%OUTROOT%\sentences" mkdir "%OUTROOT%\sentences"
if not exist "%OUTROOT%\words" mkdir "%OUTROOT%\words"

rem Network is the user's responsibility (they enable airplane mode themselves).
rem No ping guard: ping hangs when the network stack is disabled.
echo ==== offline bench [%LABEL%] start %DATE% %TIME% delay=12ms >> "%LOG%"

rem ---- 1/2 stop background processes (best effort) ----
for %%P in (
    wetype_server.exe wetype_renderer.exe wetype_update.exe wetype_service.exe
    DoubaoIme.exe DoubaoImeServer.exe DoubaoImeService.exe
    QianwenIMEMaintenanceService.exe QianwenIMEServer.exe QianwenIMEUiClient.exe qianwenime_crashpad_handler.exe
    BingKeyboardService.exe BingIMEMtfServerHost.exe BingKeyboardUpdater.exe
) do taskkill /IM %%P /F >nul 2>&1
timeout /t 2 /nobreak >nul

set "LL=%USERPROFILE%\AppData\LocalLow"
echo ==== 2/2 wipe user dictionaries (locked files are skipped) ====
echo   [WeChat / WeType] ...
rd /s /q "%LL%\Tencent\WeType\DictDir2\v5" >nul 2>&1
rd /s /q "%LL%\Tencent\WeType\DictDir2\user_hot_word" >nul 2>&1
rd /s /q "%LL%\Tencent\WeType\ImeDir\user_dict" >nul 2>&1
rd /s /q "%LL%\Tencent\WeType\ImeDir\network" >nul 2>&1
del /f /q "%LL%\Tencent\WeType\Dict\cell_dict.*" >nul 2>&1
del /f /q "%LL%\Tencent\WeType\Dict\*DictIndexV2.json" >nul 2>&1
echo   [Doubao] ...
del /f /q "%APPDATA%\DoubaoIme\dict\usr*.dat" >nul 2>&1
del /f /q "%APPDATA%\DoubaoIme\dict\common_phrase_dict.dat" >nul 2>&1
del /f /q "%APPDATA%\DoubaoIme\dict\asr_user_ner_dict.dat" >nul 2>&1
rem 2026-11-17: usr*.dat is NOT the whole story. Learning also lives in
rem dict\engine_storage.leveldb (old 10-31/11-05 files survived our wipe) and
rem Account\dictionary-state.v1.json. Without these the 65% figure is not clean.
rd /s /q "%APPDATA%\DoubaoIme\dict\engine_storage.leveldb" >nul 2>&1
del /f /q "%APPDATA%\DoubaoIme\Account\dictionary-state.v1.json" >nul 2>&1
echo   [Qianwen] ...
rd /s /q "%APPDATA%\QianwenIME\Rime\qw.userdb" >nul 2>&1
echo   [Zhongwen / Bing keyboard] ...
del /f /q "%APPDATA%\Microsoft\BingKeyboard\CHS\UDP*.tmp" >nul 2>&1
del /f /q "%APPDATA%\Microsoft\BingKeyboard\CHS\ChsPinyin*UDL*.dat*" >nul 2>&1
del /f /q "%APPDATA%\Microsoft\BingKeyboard\CHS\ChsPinyinIH*.dat*" >nul 2>&1
del /f /q "%APPDATA%\Microsoft\BingKeyboard\CHS\ChsPinyin*Cands*.dat*" >nul 2>&1
rd /s /q "%APPDATA%\Microsoft\BingKeyboard\CHS\OnlineRoaming" >nul 2>&1

echo ==== clean status (LEFT = skipped, bench continues) ====
call :CHECK "%LL%\Tencent\WeType\DictDir2\v5" "WeType user dict"
call :CHECK "%APPDATA%\DoubaoIme\dict\usr.dat" "Doubao usr.dat"
call :CHECK "%APPDATA%\QianwenIME\Rime\qw.userdb" "Qianwen userdb"
call :CHECK "%APPDATA%\Microsoft\BingKeyboard\CHS\ChsPinyinUDL.dat" "Bing UDL"

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
    echo [ABORT] none of the 4 IMEs is enabled in the Windows language list.
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
