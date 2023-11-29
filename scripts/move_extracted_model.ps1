$TmpPath = '.\tmp\kaldi_model'
$TmpPathAll = '.\tmp\kaldi_model\*'
$TmpDictationFst = '.\tmp\kaldi_model\Dictation.fst'
$TmpUserLexicon = '.\tmp\kaldi_model\user_lexicon.txt'
$TmpREADME = '.\tmp\kaldi_model\README.md'

$NewPath = '.\kaldi_model'

If (-not (Test-Path $TmpPath)) {
    return "'$TmpPath not found!"
}

If (-not (Test-Path $TmpDictationFst)) {
    return "'$TmpDictationFst not found!"
}

If (-not (Test-Path $TmpUserLexicon)) {
    return "'$TmpUserLexicon not found!"
}

If (-not (Test-Path $TmpREADME)) {
    return "'$TmpREADME not found!"
}

# Empty '.\kaldi_model' 
Get-ChildItem $NewPath | Remove-Item -Recurse -Force
# Move files
Move-Item -Path $TmpPathAll -Destination $NewPath