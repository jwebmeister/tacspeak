$TmpModelZipFilepath = '.\tmp\kaldi_model_daanzu_20211030-mediumlm.zip'

$ModelUserLexiconFilepath = '.\kaldi_model\user_lexicon.txt'
$TmpModelUserLexiconFilepath = '.\tmp\kaldi_model\user_lexicon.txt'

$ModelReadmeFilepath = '.\kaldi_model\README.md'
$TmpModelReadmeFilepath = '.\tmp\kaldi_model\README.md'

New-Item -Path '.\tmp' -ItemType Directory -Force
If (-not (Test-Path $TmpModelZipFilepath)) {
    Invoke-WebRequest 'https://github.com/jwebmeister/kaldi-active-grammar/releases/download/v3.1.0/kaldi_model_daanzu_20211030-mediumlm.zip' -OutFile $TmpModelZipFilepath
}
Expand-Archive -LiteralPath $TmpModelZipFilepath -DestinationPath '.\tmp\'

echo "copying $ModelUserLexiconFilepath to $TmpModelUserLexiconFilepath"
Copy-Item -Path $ModelUserLexiconFilepath -Destination $TmpModelUserLexiconFilepath -Force

echo "copying $ModelReadmeFilepath to $TmpModelReadmeFilepath"
Copy-Item -Path $ModelReadmeFilepath -Destination $TmpModelReadmeFilepath -Force