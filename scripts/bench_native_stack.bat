@echo off
rem Native-stack (product-level) benchmark: rime.dll + Go pipeline, no GUI.
rem Usage: scripts\bench_native_stack.bat <data_dir> [label]
rem   <data_dir> : product stage data dir (contains dicts + one .gram + rime_frost.custom.yaml)
rem   label      : optional name for the fresh user dir (default: auto)
rem Contract: see docs\protocol_native_stack.md (frozen corpus/keys/tool hashes).
setlocal
set ROOT=%~dp0..
set ENG=%ROOT%\engine\rime-schema-compare
set TOOL=%ROOT%\tools\native_stack\eval-sentences-v3.exe
set DATA=%~1
if "%DATA%"=="" (
    echo [ABORT] usage: bench_native_stack.bat ^<data_dir^> [label]
    exit /b 1
)
if not exist "%DATA%" (
    echo [ABORT] data dir not found: %DATA%
    exit /b 1
)
if not exist "%DATA%\zh-bigram.tsv" (
    echo [WARN] zh-bigram.tsv missing in data dir - Go rerank will be inert.
)
set LABEL=%~2
if "%LABEL%"=="" (
    for %%I in ("%DATA%") do set LABEL=%%~nxI
)
set USERDIR=%TEMP%\moqi-native-%LABEL%
if exist "%USERDIR%" rd /s /q "%USERDIR%"
mkdir "%USERDIR%"

echo ==== native stack: %LABEL% ====
"%TOOL%" ^
  -corpus "%ROOT%\corpus\zhihu120.txt" ^
  -pinyinCorpus "%ROOT%\corpus\zhihu120.keys.tsv" ^
  -input full -stack ime ^
  -data "%DATA%" -user "%USERDIR%" ^
  -pinyin "%ROOT%\tools\native_stack\pinyin.txt" ^
  -limit 0
if errorlevel 1 (
    echo [ABORT] evaluator failed
    exit /b 1
)
echo ==== rerun once to prove determinism (must match above exactly) ====
if exist "%USERDIR%" rd /s /q "%USERDIR%"
mkdir "%USERDIR%"
"%TOOL%" ^
  -corpus "%ROOT%\corpus\zhihu120.txt" ^
  -pinyinCorpus "%ROOT%\corpus\zhihu120.keys.tsv" ^
  -input full -stack ime ^
  -data "%DATA%" -user "%USERDIR%" ^
  -pinyin "%ROOT%\tools\native_stack\pinyin.txt" ^
  -limit 0 | findstr /C:"top-1"
endlocal
