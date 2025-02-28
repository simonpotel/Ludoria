$IsWindows = $PSVersionTable.PSVersion.Major -ge 6 -and $IsWindows
$IsLinux = $PSVersionTable.PSVersion.Major -ge 6 -and $IsLinux

Write-Host "Creating builds directory..."
if (!(Test-Path "builds")) {
    New-Item -ItemType Directory -Path "builds" | Out-Null
}
if (!(Test-Path "builds/configs")) {
    New-Item -ItemType Directory -Path "builds/configs" | Out-Null
}

Write-Host "Checking PyInstaller..."
python -m pip install pyinstaller

Write-Host "Building client..."
python -m PyInstaller --onefile --name client `
    --distpath builds `
    --workpath "builds/temp" `
    --specpath "builds/temp" `
    client.py

Write-Host "Building server..."
python -m PyInstaller --onefile --name server `
    --distpath builds `
    --workpath "builds/temp" `
    --specpath "builds/temp" `
    start_server.py

Write-Host "Copying configuration files..."
Copy-Item "configs/quadrants.json" -Destination "builds/configs/"
Copy-Item "configs/server.json" -Destination "builds/configs/"

Write-Host "Cleaning up..."
if (Test-Path "builds/temp") {
    Remove-Item -Recurse -Force "builds/temp"
}
Get-ChildItem -Filter "*.spec" | Remove-Item

Write-Host "`nBuild completed successfully!"
Write-Host "Executables and configs are available in the builds directory:"
Write-Host "- builds/client.exe (or client on Linux)"
Write-Host "- builds/server.exe (or server on Linux)"
Write-Host "- builds/configs/quadrants.json"
Write-Host "- builds/configs/server.json" 