@echo off
chcp 65001 >nul
title CAT.EXE - creation du .exe
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
echo [CAT.EXE] Preparation (2 a 5 minutes)...
"%PYEXE%" %PYARGS% -m pip install -q --disable-pip-version-check -r requirements.txt pyinstaller
"%PYEXE%" %PYARGS% -m PyInstaller --noconfirm --onefile --console --name CatExe-OSINT --collect-all phonenumbers --collect-all pillow_heif --collect-all rich --collect-all fpdf --exclude-module torch --exclude-module torchvision --exclude-module transformers --exclude-module geoclip osint_tool.py
if not exist dist\CatExe-OSINT.exe (
  echo Echec de la creation du .exe
  pause
  exit /b 1
)
if not exist CatExe-OSINT mkdir CatExe-OSINT
copy /y dist\CatExe-OSINT.exe CatExe-OSINT\ >nul
xcopy /e /i /y challenges CatExe-OSINT\challenges >nul
xcopy /e /i /y lang CatExe-OSINT\lang >nul
copy /y LISEZMOI.txt CatExe-OSINT\ >nul
rmdir /s /q build dist >nul 2>&1
del /q CatExe-OSINT.spec >nul 2>&1
echo.
echo Termine : le dossier CatExe-OSINT contient CatExe-OSINT.exe (a double-cliquer).
echo Tu peux copier ce dossier sur n'importe quel PC Windows, sans Python.
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
