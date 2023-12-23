# Always check first before you delete!
# run `.\scripts\list_wav_missing_from_retain_tsv.ps1` first!
.\scripts\list_wav_missing_from_retain_tsv.ps1 | ForEach-Object -Process {$_.Delete()}