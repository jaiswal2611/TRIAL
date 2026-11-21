@echo off
setlocal DisableDelayedExpansion
title Nandi local test server - Jaiswal Dental Clinic
cd /d "%~dp0"
set "ROOT=%~dp0"
set "SITE=%ROOT%public_html"
set "PORT=8000"
echo.
echo  Nandi local test server
echo  -----------------------

if not exist "%SITE%\index.html" (
  echo  [X] Cannot find public_html\index.html.
  echo      Extract the WHOLE zip first, then run this file from inside the extracted folder.
  pause
  exit /b 1
)

rem ---- 1. find PHP (PATH, C:\php, or tools\php inside this folder) ----
set "PHPEXE="
for /f "delims=" %%P in ('where php 2^>nul') do if not defined PHPEXE set "PHPEXE=%%P"
if not defined PHPEXE if exist "C:\php\php.exe" set "PHPEXE=C:\php\php.exe"
if not defined PHPEXE if exist "%ROOT%tools\php\php.exe" set "PHPEXE=%ROOT%tools\php\php.exe"
if not defined PHPEXE goto nophp
for %%I in ("%PHPEXE%") do set "PHPDIR=%%~dpI"
echo  [OK] PHP found: %PHPEXE%

rem ---- 2. read your private settings from .env (the key is never printed) ----
if not exist "%ROOT%.env" goto nokeyfile
for /f "usebackq eol=# tokens=1,* delims==" %%A in ("%ROOT%.env") do (
  if /i "%%A"=="ELEVENLABS_API_KEY" set "ELEVENLABS_API_KEY=%%B"
  if /i "%%A"=="ELEVENLABS_MODEL" set "ELEVENLABS_MODEL=%%B"
  if /i "%%A"=="ELEVENLABS_API_HOST" set "ELEVENLABS_API_HOST=%%B"
  if /i "%%A"=="NANDI_ALLOWED_ORIGINS" set "NANDI_ALLOWED_ORIGINS=%%B"
)
:nokeyfile
if defined ELEVENLABS_API_KEY (
  echo  [OK] ElevenLabs key found. It is hidden and stays on this computer.
) else (
  echo  [!] No ElevenLabs key yet. Nandi will use the plain browser voice.
  echo      Run SETUP-KEY.bat to add your key, then start this again.
)

rem ---- 3. certificate file so PHP can talk to ElevenLabs securely ----
set "CA=%ROOT%php-config\cacert.pem"
if not exist "%CA%" (
  echo  [!] php-config\cacert.pem is missing. ElevenLabs will fail with an SSL error until you add it.
  echo      See WINDOWS-SETUP-GUIDE.md, step 3.
)
set "NANDI_CA_BUNDLE=%CA%"

rem ---- 4. write the PHP settings file for this session ----
set "INI=%ROOT%php-config\php-local.ini"
> "%INI%" echo extension_dir="%PHPDIR%ext"
>> "%INI%" echo extension=curl
>> "%INI%" echo extension=openssl
>> "%INI%" echo extension=mbstring
>> "%INI%" echo curl.cainfo="%CA%"
>> "%INI%" echo openssl.cafile="%CA%"
>> "%INI%" echo display_errors=Off
>> "%INI%" echo log_errors=On
>> "%INI%" echo error_log="%ROOT%php-config\php-errors.log"
>> "%INI%" echo variables_order=EGPCS
>> "%INI%" echo date.timezone=Asia/Kolkata

rem ---- 5. PHP checks its own syntax on YOUR computer ----
"%PHPEXE%" -c "%INI%" -l "%SITE%\api\nandi-voice.php"
if errorlevel 1 goto phpbad
"%PHPEXE%" -c "%INI%" -l "%SITE%\router.php"
if errorlevel 1 goto phpbad

rem ---- 6. pick a free port ----
:findport
netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul
if errorlevel 1 goto portok
set /a PORT+=1
if %PORT% LEQ 8010 goto findport
echo  [X] Ports 8000 to 8010 are all busy. Close other programs and try again.
pause
exit /b 1
:portok

rem ---- 7. open Chrome shortly after the server starts ----
set "CHROME="
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not defined CHROME if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not defined CHROME if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"
if defined CHROME (
  start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep 2; Start-Process '%CHROME%' 'http://localhost:%PORT%/'"
) else (
  start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep 2; Start-Process 'http://localhost:%PORT%/'"
)

echo.
echo  Website:      http://localhost:%PORT%/
echo  Voice test:   http://localhost:%PORT%/voice-test.html
echo  Close this window (or press Ctrl+C) to stop the server.
echo.
"%PHPEXE%" -c "%INI%" -S localhost:%PORT% -t "%SITE%" "%SITE%\router.php"
echo.
echo  The server has stopped.
pause
exit /b 0

:nophp
echo  [X] PHP was not found on this computer.
echo      1. Download the "Non Thread Safe" x64 zip from https://windows.php.net/download/
echo      2. Extract it to C:\php   (so that C:\php\php.exe exists)
echo      3. Run this file again.
echo      Full steps are in WINDOWS-SETUP-GUIDE.md.
pause
exit /b 1

:phpbad
echo.
echo  [X] PHP reported a problem with the website's PHP files (see above).
echo      Please send that message to the person who maintains the site.
pause
exit /b 1
