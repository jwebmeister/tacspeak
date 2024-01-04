$ErrorActionPreference = "Stop"

$VenvPath = '.venv'
$VenvAbsPath = Join-Path -Path $pwd.Path -ChildPath $VenvPath

# check .venv is created
If (-not (Test-Path $VenvAbsPath)) {
    return "'$VenvAbsPath not found! Please create python virtual environment at $VenvPath "
}

# check .venv is activated
$PythonVenvPath = python -c "import sys; print(sys.prefix)"

If (-not ($VenvAbsPath -eq $PythonVenvPath)) {
    return "'$PythonVenvPath not activated or not same path as $VenvAbsPath! Please activate python virtual environment at $VenvPath "
}


scripts\pip_reinstall_all.ps1
scripts\download_replace_portaudio_x64_dll.ps1
scripts\download_extract_model.ps1
scripts\move_extracted_model.ps1
scripts\generate_all_licenses.ps1

pip freeze > freeze.txt