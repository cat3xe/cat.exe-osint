@echo off
chcp 65001 >nul
title CAT.EXE OSINT TOOL
cd /d "%~dp0"
set "PYEXE="
set "PYARGS="
call :findpy
if not defined PYEXE (
  echo [CAT.EXE] Python 3.14 minimum absent : installation automatique...
  winget install -e --id Python.Python.3.14 --scope user --accept-source-agreements --accept-package-agreements
  call :findpy
)
if not defined PYEXE (
  echo Installation automatique impossible : installe Python 3.14 depuis python.org puis relance.
  start https://www.python.org/downloads/
  pause
  exit /b 1
)
echo [CAT.EXE] Python : %PYEXE% %PYARGS%
echo [CAT.EXE] Verification des modules...
"%PYEXE%" %PYARGS% -m pip install -q --disable-pip-version-check -r requirements.txt
"%PYEXE%" %PYARGS% osint_tool.py
pause
exit /b 0

:findpy
set "PYEXE="
set "PYARGS="
py -3.14 -c "import sys" >nul 2>&1 && (set "PYEXE=py" & set "PYARGS=-3.14")
if not defined PYEXE if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if not defined PYEXE (
  python -c "import sys; sys.exit(0 if sys.version_info >= (3, 14) else 1)" >nul 2>&1
  if not errorlevel 1 set "PYEXE=python"
)
goto :eof
