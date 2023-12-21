$TmpDllFilePath = './tmp/libportaudio64bit.dll'
$VenvDllFilePath = './.venv/Lib/site-packages/_sounddevice_data/portaudio-binaries/libportaudio64bit.dll'
$PALicenseFilePath = './licenses/portaudio_license.txt'

If (-not (Test-Path $VenvDllFilePath)) {
    return "'$VenvDllFilePath not found!"
}

If (-not (Test-Path $PALicenseFilePath)) {
    Invoke-WebRequest 'https://github.com/jwebmeister/portaudio/releases/download/v19.7.0/LICENSE.txt' -OutFile $PALicenseFilePath
}

New-Item -Path './tmp' -ItemType Directory -Force
If (-not (Test-Path $TmpDllFilePath)) {
    Invoke-WebRequest 'https://github.com/jwebmeister/portaudio/releases/download/v19.7.0/portaudio_x64.dll' -OutFile $TmpDllFilePath
}

echo "copying $TmpDllFilePath to $VenvDllFilePath"
Copy-Item -Path $TmpDllFilePath -Destination $VenvDllFilePath -Force