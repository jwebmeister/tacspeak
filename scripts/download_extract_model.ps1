New-Item -Path '.\tmp' -ItemType Directory -Force
Invoke-WebRequest 'https://github.com/jwebmeister/kaldi-active-grammar/releases/download/v3.1.0/kaldi_model_daanzu_20211030-mediumlm.zip' -OutFile '.\tmp\kaldi_model_daanzu_20211030-mediumlm.zip'
Expand-Archive -LiteralPath '.\tmp\kaldi_model_daanzu_20211030-mediumlm.zip' -DestinationPath '.\tmp\'
Copy-Item -Path '.\kaldi_model\user_lexicon.txt' -Destination '.\tmp\kaldi_model\user_lexicon.txt' -Force
Copy-Item -Path '.\kaldi_model\README.md' -Destination '.\tmp\kaldi_model\README.md' -Force