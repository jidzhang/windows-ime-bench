@echo off
rem Light reset for MS Pinyin + Moqi only (no admin, user scope).
rem Kills IME hosts then wipes learning/user dict; verifies absence.
set CHS=%APPDATA%\Microsoft\InputMethod\Chs
set MQ=%APPDATA%\Moqi\Rime
taskkill /F /IM ChsIME.exe >nul 2>&1
taskkill /F /IM MoqiIME.exe >nul 2>&1
taskkill /F /IM MoqiLaunch.exe >nul 2>&1
taskkill /F /IM MoqiLauncher.exe >nul 2>&1
ping -n 2 127.0.0.1 >nul
del /f /q "%CHS%\ChsPinyin*UDL*.dat*" >nul 2>&1
del /f /q "%CHS%\ChsPinyinIH*.dat*" >nul 2>&1
del /f /q "%CHS%\ChsPinyin*Cands*.dat*" >nul 2>&1
del /f /q "%CHS%\UDP*.tmp" >nul 2>&1
rd /s /q "%MQ%\rime_frost.userdb" >nul 2>&1
del /f /q "%APPDATA%\Moqi\grammar_penalty_cache.json" >nul 2>&1
set FAIL=0
if exist "%CHS%\ChsPinyinUDL.dat" set FAIL=1
if exist "%CHS%\ChsPinyinIH.dat" set FAIL=1
if exist "%MQ%\rime_frost.userdb" set FAIL=1
if "%FAIL%"=="0" (echo LIGHT-RESET OK) else (echo LIGHT-RESET LEFT)
exit /b %FAIL%