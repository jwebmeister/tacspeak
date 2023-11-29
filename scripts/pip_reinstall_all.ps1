pip freeze > to-uninstall.txt
pip uninstall -y -r to-uninstall.txt
if (Test-Path "to-uninstall.txt") {
    Remove-Item "to-uninstall.txt"
}
pip install -r requirements.txt