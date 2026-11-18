@echo off
rem Six-IME bench: WeChat + Doubao + Qianwen + QQ + Zhongwen(Bing) + Moqi.
rem Corpora: zhihu120 (sentences) + words23456 (2-6 char, full pinyin) +
rem          words_mixed (front full pinyin + rear initials) - the new word sets
rem          where words234 had no discrimination (everyone 99%).
rem Ranking afterwards: scripts\weighted_rank.py (long sentence 30% / words 70%).
rem
rem Double-click to run. User controls the network themselves.
rem QQ: its user dict is restored from a process-held copy seconds after deletion,
rem     so the wipe below is best-effort (reported, never fatal).
rem Results: results\run\six_23456\ + results\summary_six_23456.md
rem ASCII only - cmd.exe parses .bat as ANSI/GBK; UTF-8 Chinese breaks parsing.
setlocal
set ROOT=%~dp0..
set ENGINE=%ROOT%\engine\rime-schema-compare
set IMES=wechat_pinyin doubao_pinyin qianwen_pinyin qq_pinyin zhongwen_pinyin moqi_pinyin
set LABEL=six_23456
set OUTROOT=%ROOT%\results\run\%LABEL%
set LOG=%OUTROOT%\run_log.txt
if not exist "%OUTROOT%\sentences" mkdir "%OUTROOT%\sentences"
if not exist "%OUTROOT%\words" mkdir "%OUTROOT%\words"

echo ==== six-IME bench [%LABEL%] start %DATE% %TIME% delay=12ms >> "%LOG%"

rem ---- 1/2 stop IME helper processes, then wipe learning data ----
net stop QQPYService /y >nul 2>&1
sc stop QianwenIMEMaintenanceService >nul 2>&1
for %%P in (
    wetype_server.exe wetype_renderer.exe wetype_update.exe wetype_service.exe
    DoubaoIme.exe DoubaoImeServer.exe DoubaoImeService.exe
    QianwenIMEMaintenanceService.exe QianwenIMEServer.exe QianwenIMEUiClient.exe qianwenime_crashpad_handler.exe
    QQPYUserCenter.exe QQPYBroker.exe QQPYTask.exe QQPYToolbox.exe QQPYConfig.exe QQPYSnapshot.exe QQPYCloud.exe
    BingKeyboardService.exe BingIMEMtfServerHost.exe BingKeyboardUpdater.exe
    MoqiLauncher.exe MoqiLaunch.exe MoqiIME.exe
) do taskkill /IM %%P /F >nul 2>&1
timeout /t 2 /nobreak >nul

set "LL=%USERPROFILE%\AppData\LocalLow"
set "PQQ=C:\ProgramData\Tencent\QQPinyin\users\public"
echo ==== 2/2 wipe learning data (best effort; locked files skipped) ====
echo   [WeChat] ...
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
rd /s /q "%APPDATA%\DoubaoIme\dict\engine_storage.leveldb" >nul 2>&1
del /f /q "%APPDATA%\DoubaoIme\Account\dictionary-state.v1.json" >nul 2>&1
echo   [Qianwen] ...
rd /s /q "%APPDATA%\QianwenIME\Rime\qw.userdb" >nul 2>&1
echo   [QQ] ...
del /f /q "%PQQ%\dict\sgim_usr_v3new.bin" >nul 2>&1
del /f /q "%PQQ%\dict\sgim_eng_usr.bin" >nul 2>&1
del /f /q "%PQQ%\dict\sgim_ext.bin" >nul 2>&1
del /f /q "%PQQ%\dict\sgim_jianabbr.bin" >nul 2>&1
del /f /q "%PQQ%\dict\Correction.ini" >nul 2>&1
del /f /q "%PQQ%\dict\Fuzzy.dat" >nul 2>&1
del /f /q "%PQQ%\cdictlist.ini" >nul 2>&1
rd /s /q "%PQQ%\dict\Backup" >nul 2>&1
if exist "%PQQ%\inputstat.dat" ren "%PQQ%\inputstat.dat" inputstat.dat.old >nul 2>&1
echo   [Zhongwen/Bing] ...
del /f /q "%APPDATA%\Microsoft\BingKeyboard\CHS\UDP*.tmp" >nul 2>&1
del /f /q "%APPDATA%\Microsoft\BingKeyboard\CHS\ChsPinyin*UDL*.dat*" >nul 2>&1
del /f /q "%APPDATA%\Microsoft\BingKeyboard\CHS\ChsPinyinIH*.dat*" >nul 2>&1
del /f /q "%APPDATA%\Microsoft\BingKeyboard\CHS\ChsPinyin*Cands*.dat*" >nul 2>&1
rd /s /q "%APPDATA%\Microsoft\BingKeyboard\CHS\OnlineRoaming" >nul 2>&1
echo   [Moqi] ...
rd /s /q "%APPDATA%\Moqi\Rime\rime_frost.userdb" >nul 2>&1
del /f /q "%APPDATA%\Moqi\grammar_penalty_cache.json" >nul 2>&1
del /f /q "%APPDATA%\Moqi\typo_memory.tsv" >nul 2>&1

echo ==== clean status (LEFT = skipped, bench continues) ====
if exist "%LL%\Tencent\WeType\DictDir2\v5" (echo   [LEFT] WeChat dict) else (echo   [ OK ] WeChat dict)
if exist "%APPDATA%\DoubaoIme\dict\usr.dat" (echo   [LEFT] Doubao dict) else (echo   [ OK ] Doubao dict)
if exist "%APPDATA%\QianwenIME\Rime\qw.userdb" (echo   [LEFT] Qianwen userdb) else (echo   [ OK ] Qianwen userdb)
if exist "%PQQ%\dict\sgim_usr_v3new.bin" (echo   [LEFT] QQ dict) else (echo   [ OK ] QQ dict)
if exist "%APPDATA%\Microsoft\BingKeyboard\CHS\ChsPinyinUDL.dat" (echo   [LEFT] Bing UDL) else (echo   [ OK ] Bing UDL)
if exist "%APPDATA%\Moqi\Rime\rime_frost.userdb" (echo   [LEFT] Moqi userdb) else (echo   [ OK ] Moqi userdb)

rem ---- bench: 3 corpora per IME ----
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
    echo [ABORT] none of the 6 IMEs is enabled in the Windows language list.
    pause
    exit /b 1
)
set IMES=%NEWIMES%
for %%I in (%IMES%) do call :bench %%I

rem ---- post-run QQ check ----
if exist "%PQQ%\dict\sgim_usr_v3new.bin" (
    echo   [WARN] QQ user dict reappeared during run - carries residual learning
    echo [WARN] QQ dict reappeared>> "%LOG%"
)

python "%ROOT%\scripts\collect_results.py" "%ROOT%" %LABEL%
echo ==== six-IME bench [%LABEL%] done %DATE% %TIME% >> "%LOG%"
echo.
echo ===================== WEIGHTED RANKING =====================
python "%ROOT%\scripts\weighted_rank.py" "%ROOT%" %LABEL%
echo ==========================================================
echo Raw per-corpus summary: %ROOT%\results\summary_%LABEL%.md
pause
endlocal
exit /b 0

:bench
set IME=%1
echo ---- %IME% zhihu120 %TIME% >> "%LOG%"
python -c "import sys; sys.path.insert(0,'src'); from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher; WindowsImeSwitcher().activate_profile('%IME%')" >nul 2>&1
python scripts\benchmark_windows_pinyin.py --ime %IME% --corpus data\corpus\zhihu120.txt --inter-key-delay-ms 12 --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\sentences" 2>&1 | findstr /C:"not_confirmed" /C:"[RESULT]" /C:"[ABORT]" /C:"[SKIP]" >> "%LOG%"

echo ---- %IME% words23456 %TIME% >> "%LOG%"
python -c "import sys; sys.path.insert(0,'src'); from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher; WindowsImeSwitcher().activate_profile('%IME%')" >nul 2>&1
python scripts\benchmark_windows_pinyin.py --ime %IME% --corpus data\corpus\words23456.txt --min-hanzi 2 --inter-key-delay-ms 12 --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\words" 2>&1 | findstr /C:"not_confirmed" /C:"[RESULT]" /C:"[ABORT]" /C:"[SKIP]" >> "%LOG%"

echo ---- %IME% words_mixed %TIME% >> "%LOG%"
python -c "import sys; sys.path.insert(0,'src'); from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher; WindowsImeSwitcher().activate_profile('%IME%')" >nul 2>&1
python scripts\benchmark_windows_pinyin.py --ime %IME% --corpus data\corpus\words_mixed.txt --min-hanzi 2 --inter-key-delay-ms 12 --extra-imes "%ROOT%\imes.json" --out-dir "%OUTROOT%\words" 2>&1 | findstr /C:"not_confirmed" /C:"[RESULT]" /C:"[ABORT]" /C:"[SKIP]" >> "%LOG%"
goto :eof
