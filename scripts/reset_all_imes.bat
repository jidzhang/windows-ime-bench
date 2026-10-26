@echo off
rem Reset ALL installed IMEs to clean initial state (2026-10-25).
rem Wipes user dictionaries, learning/frequency data and cloud-synced dict
rem caches for every IME on this machine. Keeps configs, skins, programs.
rem For between-round benchmark resets ("initial state" runs).
rem Sogou = official 16.9 in "Program Files (x86)\SogouInput" (portable
rem Toolbox install + its LocalLow junction removed 2026-10-25).
rem ASCII only - cmd.exe parses .bat as ANSI/GBK, UTF-8 Chinese breaks it.
rem Run as Administrator.

net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ABORT] Administrator rights required. Right-click and "Run as administrator".
    pause
    exit /b 1
)

echo ==== 1/4 stop IME background processes (watchdogs/services first) ====
for %%P in (
    MetasequoiaImeWatchdog.exe MetasequoiaImeServer.exe
    PalmInputGuard.exe PalmInputService.exe
    QianwenIMEMaintenanceService.exe QianwenIMEServer.exe QianwenIMEUiClient.exe qianwenime_crashpad_handler.exe
    wetype_server.exe wetype_renderer.exe wetype_update.exe wetype_service.exe
    SGTool.exe SogouCloud.exe SogouImeBroker.exe SogouExe.exe
    QQPYUserCenter.exe QQPYBroker.exe QQPYTask.exe QQPYToolbox.exe QQPYConfig.exe QQPYSnapshot.exe QQPYCloud.exe
    baidupinyin.exe
    iFlyInput.exe iFlyPlatform.exe
    GooglePinyinDaemon.exe
    DoubaoIme.exe DoubaoImeServer.exe DoubaoImeService.exe
    SuYanServer.exe
    wind_input.exe
    qingjian-server.exe
    winxime-server.exe
    MoqiLauncher.exe MoqiLaunch.exe MoqiIME.exe
) do taskkill /IM %%P /F >nul 2>&1
timeout /t 2 /nobreak >nul

set "LL=%USERPROFILE%\AppData\LocalLow"
set FAIL=

echo ==== 2/4 wipe user dictionaries + learning data ====

echo   [01] Microsoft Pinyin (user dict pages + self-learning) ...
del /f /q "%APPDATA%\Microsoft\InputMethod\Chs\UDP*.tmp" >nul 2>&1
del /f /q "%APPDATA%\Microsoft\InputMethod\Chs\ChsPinyinUDL*.dat" >nul 2>&1
del /f /q "%APPDATA%\Microsoft\InputMethod\Chs\ChsPinyinIH*.dat" >nul 2>&1
del /f /q "%APPDATA%\Microsoft\InputMethod\Chs\ChsPinyinDeletedCands*.dat" >nul 2>&1
del /f /q "%APPDATA%\Microsoft\InputMethod\Chs\ChsPinyinPinnedCands*.dat" >nul 2>&1
rd /s /q "%APPDATA%\Microsoft\InputMethod\Chs\OnlineRoaming" >nul 2>&1

echo   [02] Sogou Pinyin 16.9 official ...
rem user dict + learning files in LocalLow\SogouPY (real dir since junction
rem removal; if a junction ever reappears, del through it cleans the target
rem but do NOT rd the SogouPY dir itself)
set "SG=%LL%\SogouPY"
if exist "%SG%\" (
    del /f /q "%SG%\sgim_gd_usr.bin" >nul 2>&1
    del /f /q "%SG%\sgim_gd_usr_a_bigram.bin" >nul 2>&1
    del /f /q "%SG%\sgim_gd_usr_dca_bigram.bin" >nul 2>&1
    del /f /q "%SG%\sgim_gd_usrbg.bin" >nul 2>&1
    del /f /q "%SG%\sgim_gd_panel_usr.bin" >nul 2>&1
    del /f /q "%SG%\sgim_gd_bhusr.bin" >nul 2>&1
    del /f /q "%SG%\sgim_eng_usr.bin" >nul 2>&1
    del /f /q "%SG%\sgim_eng_usr_emod.bin" >nul 2>&1
    del /f /q "%SG%\sgim_url_usr.bin" >nul 2>&1
    del /f /q "%SG%\sgim_usr_fuzzy.bin" >nul 2>&1
    del /f /q "%SG%\sgim_del_word.bin" >nul 2>&1
    del /f /q "%SG%\sgim_fix_first.bin" >nul 2>&1
    del /f /q "%SG%\usrZone.dat" >nul 2>&1
    del /f /q "%SG%\usrzoneext.dat" >nul 2>&1
    del /f /q "%SG%\InputStaticstics.dat" >nul 2>&1
    del /f /q "%SG%\sgim_gd_cell.bin" >nul 2>&1
    del /f /q "%SG%\BrandScdConfig.download" >nul 2>&1
    rd /s /q "%SG%\scd" >nul 2>&1
)
rem per-user input history inside version dir (restored fresh by installer)
for /d %%V in ("C:\Program Files (x86)\SogouInput\1*") do (
    del /f /q "%%V\sgim_InputStr.bin" >nul 2>&1
    del /f /q "%%V\sgim_bigram_serdata.bin.*" >nul 2>&1
)
rd /s /q "%LL%\SogouPY.users" >nul 2>&1
rem 2026-10-26: KEEP ProgramData\SogouInput. It holds the shared engine base
rem dicts that even a fresh reinstall keeps (uninstaller never cleans it).
rem After wiping, Sogou does NOT rebuild it (only a ~400KB skeleton comes
rem back) and sentence accuracy drops ~20 pts (fake-low 35% vs true 55%).
rem rem rd /s /q "%ProgramData%\SogouInput" >nul 2>&1

echo   [03] WeType / WeChat Pinyin ...
rd /s /q "%LL%\Tencent\WeType\DictDir2\v5" >nul 2>&1
rd /s /q "%LL%\Tencent\WeType\DictDir2\user_hot_word" >nul 2>&1
rd /s /q "%LL%\Tencent\WeType\ImeDir\user_dict" >nul 2>&1
rd /s /q "%LL%\Tencent\WeType\ImeDir\network" >nul 2>&1
del /f /q "%LL%\Tencent\WeType\Dict\cell_dict.*" >nul 2>&1
del /f /q "%LL%\Tencent\WeType\Dict\*DictIndexV2.json" >nul 2>&1

echo   [04] Baidu Pinyin ...
del /f /q "%LL%\Baidu\BaiduPinyin\Account\.common\dict\iptdict\*.*" >nul 2>&1
del /f /q "%LL%\Baidu\BaiduPinyin\inputrecord.dat" >nul 2>&1
del /f /q "%LL%\Baidu\BaiduPinyin\CacheData\pinyin_rpt.dat" >nul 2>&1
del /f /q "%LL%\Baidu\BaiduPinyin\Temp\recommend_personal_dicts_list.dat" >nul 2>&1
del /f /q "%LL%\Baidu\BaiduPinyin\dict\emotioncenter.dat" >nul 2>&1
del /f /q "%LL%\Baidu\BaiduPinyin\dict\emotionword.dat" >nul 2>&1

echo   [05] iFlytek Input ...
del /f /q "%LL%\iFly Info Tek\iFlyIME\dict\xf_userword.lit*" >nul 2>&1
del /f /q "%LL%\iFly Info Tek\iFlyIME\dict\xf_hotword.lit" >nul 2>&1
del /f /q "%LL%\iFly Info Tek\iFlyIME\dict\*.bin" >nul 2>&1
del /f /q "%LL%\iFly Info Tek\iFlyIME\dict\cphrase_default.jet" >nul 2>&1
del /f /q "%LL%\iFly Info Tek\iFlyIME\account\userword_del.kv*" >nul 2>&1
del /f /q "%LL%\iFly Info Tek\iFlyIME\ossp\log.db" >nul 2>&1

echo   [06] QQ Pinyin 6.7 (user dict in ProgramData) ...
del /f /q "%ProgramData%\Tencent\QQPinyin\users\public\dict\sgim_usr_v3new.bin" >nul 2>&1
del /f /q "%ProgramData%\Tencent\QQPinyin\users\public\dict\sgim_eng_usr.bin" >nul 2>&1
del /f /q "%ProgramData%\Tencent\QQPinyin\users\public\dict\sgim_ext.bin" >nul 2>&1
del /f /q "%ProgramData%\Tencent\QQPinyin\users\public\dict\sgim_jianabbr.bin" >nul 2>&1
del /f /q "%ProgramData%\Tencent\QQPinyin\users\public\dict\sgim_punc.bin" >nul 2>&1
del /f /q "%ProgramData%\Tencent\QQPinyin\users\public\dict\sgim_keymap.bin" >nul 2>&1
del /f /q "%ProgramData%\Tencent\QQPinyin\users\public\dict\Correction.ini" >nul 2>&1
del /f /q "%ProgramData%\Tencent\QQPinyin\users\public\dict\Fuzzy.dat" >nul 2>&1
rd /s /q "%ProgramData%\Tencent\QQPinyin\users\public\dict\Backup" >nul 2>&1
del /f /q "%ProgramData%\Tencent\QQPinyin\users\public\inputstat.dat" >nul 2>&1
del /f /q "%ProgramData%\Tencent\QQPinyin\users\public\cdictlist.ini" >nul 2>&1
rd /s /q "%ProgramData%\Tencent\QQPinyin\cdict\Temp" >nul 2>&1
rd /s /q "%ProgramData%\Tencent\QQPinyin\cdict\tmp" >nul 2>&1
del /f /q "%ProgramData%\Tencent\QQPinyin\cdict\*.qcel" >nul 2>&1

echo   [07] Google Pinyin 2.7 (user dict inside install dir) ...
for %%U in (TEST SYSTEM) do (
    del /f /q "C:\Program Files (x86)\Google\Google Pinyin 2\user\%%U\Google\Google Pinyin 2\userdict.00000" >nul 2>&1
    del /f /q "C:\Program Files (x86)\Google\Google Pinyin 2\user\%%U\Google\Google Pinyin 2\cache.00000" >nul 2>&1
    del /f /q "C:\Program Files (x86)\Google\Google Pinyin 2\user\%%U\Google\Google Pinyin 2\customtoken.00000" >nul 2>&1
    del /f /q "C:\Program Files (x86)\Google\Google Pinyin 2\user\%%U\Google\Google Pinyin 2\url.data.00000" >nul 2>&1
    del /f /q "C:\Program Files (x86)\Google\Google Pinyin 2\user\%%U\Google\Google Pinyin 2\url.index.00000" >nul 2>&1
    rd /s /q "C:\Program Files (x86)\Google\Google Pinyin 2\user\%%U\Google\Google Pinyin 2\delta" >nul 2>&1
    rd /s /q "C:\Program Files (x86)\Google\Google Pinyin 2\user\%%U\Google\Google Pinyin 2\Dictionaries" >nul 2>&1
    rd /s /q "C:\Program Files (x86)\Google\Google Pinyin 2\user\%%U\Google\Google Pinyin 2\Crash" >nul 2>&1
)

echo   [08] Doubao IME ...
del /f /q "%APPDATA%\DoubaoIme\dict\usr*.dat" >nul 2>&1
del /f /q "%APPDATA%\DoubaoIme\dict\common_phrase_dict.dat" >nul 2>&1
del /f /q "%APPDATA%\DoubaoIme\dict\asr_user_ner_dict.dat" >nul 2>&1

echo   [09] Qianwen IME (rime userdb) ...
rd /s /q "%APPDATA%\QianwenIME\Rime\qw.userdb" >nul 2>&1

echo   [10] SuYan IME (rime userdb) ...
rd /s /q "%APPDATA%\SuYan\SuYan\rime\rime_ice.userdb" >nul 2>&1
del /f /q "%APPDATA%\SuYan\SuYan\rime\user_data.db*" >nul 2>&1

echo   [11] Metasequoia IME ...
del /f /q "%LOCALAPPDATA%\metasequoiaime\msime_user.db*" >nul 2>&1
del /f /q "%LOCALAPPDATA%\metasequoiaime\user_dict.dat" >nul 2>&1

echo   [12] WindInput ...
del /f /q "%APPDATA%\WindInput\data\pinyin\temp.dict.yaml" >nul 2>&1
del /f /q "%APPDATA%\WindInput\data\pinyin\freq.table.yaml" >nul 2>&1
rd /s /q "%APPDATA%\WindInput\data\stats" >nul 2>&1
rd /s /q "%APPDATA%\WindInput\data\.backup" >nul 2>&1

echo   [13] Qingjian IME ...
del /f /q "%APPDATA%\Qingjian\user*.tsv" >nul 2>&1
del /f /q "%APPDATA%\Qingjian\input-log.jsonl" >nul 2>&1
del /f /q "%APPDATA%\Qingjian\usage-hourly.tsv" >nul 2>&1

echo   [14] XiMe Yao (winxime, rime userdb) ...
rd /s /q "%APPDATA%\xime\rime\pinyin_simp.userdb" >nul 2>&1
rd /s /q "%APPDATA%\xime\rime\wubi86.userdb" >nul 2>&1
del /f /q "%APPDATA%\xime\rime\wubi86_user.dict.yaml" >nul 2>&1

echo   [15] Moqi IME ...
rd /s /q "%APPDATA%\Moqi\Rime\rime_frost.userdb" >nul 2>&1
del /f /q "%APPDATA%\Moqi\grammar_penalty_cache.json" >nul 2>&1
del /f /q "%APPDATA%\Moqi\moqi_custom_phrase.txt" >nul 2>&1
del /f /q "%LOCALAPPDATA%\MoqiIM\Log\*.log" >nul 2>&1

echo   [16] Huayu Pinyin V6.9 (unispim6) ...
del /f /q "%LL%\unispim6\wordlib\user.uwl*" >nul 2>&1
del /f /q "%LL%\unispim6\wordlib\ci_cache.dat" >nul 2>&1
del /f /q "%LL%\unispim6\zi\hz_cache.dat" >nul 2>&1

echo   [17] PalmInput (Shouxin) ...
del /f /q "%LL%\PalmInput\Dict\Palminput-pyuser-*.pidic" >nul 2>&1
del /f /q "%LL%\PalmInput\DB\Palminput.db" >nul 2>&1
del /f /q "%LL%\PalmInput\Dict\Cate\Cate-*.pidic" >nul 2>&1

echo ==== 3/4 verify key artifacts ====
call :CHECK "%APPDATA%\Microsoft\InputMethod\Chs\ChsPinyinUDL.dat" "MS Pinyin UDL"
call :CHECK "%LL%\SogouPY\sgim_gd_usr.bin" "Sogou user dict"
rem (x86) paths must NOT go through call :CHECK - CALL re-parses args and
rem the ")" in (x86) breaks the parser ("was unexpected at this time")
if exist "C:\Program Files (x86)\SogouInput\16.9.0.5535\sgim_InputStr.bin" (
    echo   [LEFT] Sogou InputStr
    set FAIL=1
) else (
    echo   [ OK ] Sogou InputStr
)
call :CHECK "%LL%\Tencent\WeType\DictDir2\v5" "WeType user dict"
call :CHECK "%LL%\Baidu\BaiduPinyin\Account\.common\dict\iptdict" "Baidu iptdict"
call :CHECK "%LL%\iFly Info Tek\iFlyIME\dict\xf_userword.lit" "iFlytek userword"
call :CHECK "%ProgramData%\Tencent\QQPinyin\users\public\dict\sgim_usr_v3new.bin" "QQPinyin user dict"
if exist "C:\Program Files (x86)\Google\Google Pinyin 2\user\TEST\Google\Google Pinyin 2\userdict.00000" (
    echo   [LEFT] Google userdict
    set FAIL=1
) else (
    echo   [ OK ] Google userdict
)
call :CHECK "%APPDATA%\DoubaoIme\dict\usr.dat" "Doubao usr.dat"
call :CHECK "%APPDATA%\QianwenIME\Rime\qw.userdb" "Qianwen userdb"
call :CHECK "%APPDATA%\SuYan\SuYan\rime\rime_ice.userdb" "SuYan userdb"
call :CHECK "%LOCALAPPDATA%\metasequoiaime\msime_user.db" "Metasequoia user db"
call :CHECK "%APPDATA%\WindInput\data\pinyin\temp.dict.yaml" "WindInput temp dict"
call :CHECK "%APPDATA%\Qingjian\user-words.tsv" "Qingjian user tsv"
call :CHECK "%APPDATA%\xime\rime\pinyin_simp.userdb" "Xime userdb"
call :CHECK "%APPDATA%\Moqi\Rime\rime_frost.userdb" "Moqi userdb"
call :CHECK "%LL%\unispim6\wordlib\user.uwl" "Huayu user.uwl"
call :CHECK "%LL%\PalmInput\DB\Palminput.db" "PalmInput db"

echo ==== 4/4 done ====
if defined FAIL (
    echo.
    echo ==== Some files ABOVE are locked by running IME hosts. ====
    echo ==== Switch input method to ENG, log off/on, run again to finish. ====
) else (
    echo.
    echo ==== ALL CLEAN: user dicts and cloud caches wiped for 17 IMEs. ====
    echo ==== IME servers respawn automatically on next activation. ====
)
pause
exit /b 0

:CHECK
if exist %1 (
    echo   [LEFT] %~2 still present: %~1
    set FAIL=1
) else (
    echo   [ OK ] %~2
)
goto :eof
