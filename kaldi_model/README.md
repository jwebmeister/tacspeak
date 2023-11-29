The Kaldi Active Grammar version 3.1.0 medium model, is required to use this software.

The file `<project folder>\kaldi_model\user_lexicon.txt` has been created by JWebmeister <[github.com/jwebmeister][gh-jwebmeister]>, intended to be combined with [v3.1.0 medium model files][kag-medium-model] downloaded from [github.com/daanzu/kaldi-active-grammar][kag]

Install instructions:
- recommended to create a new virtual environment, `python -m venv <project folder>\.venv`
- `pip install 'kaldi-active-grammar[g2p_en]'`
- Download the [medium model files][kag-medium-model] and extract to a temporary folder, e.g. `<temp folder>\kaldi_model`
- copy the file `<project folder>\kaldi_model\user_lexicon.txt` into the temporary folder, replacing the existing `<temp folder>\kaldi_model\user_lexicon.txt`
- move all files and folders from `<temp folder>\kaldi_model\*` into `<project folder>\kaldi_model\*`
- cd `<project folder>`
- `python -m kaldi_active_grammar compile_agf_dictation_graph -m kaldi_model` (this will take on the order of 15 minutes)


Details of the unmodified source version below:

- Name: kaldi-active-grammar
- Version: 3.1.0
- Summary: Kaldi speech recognition with grammars that can be set active/inactive dynamically at decode-time
- License: AGPL-3.0
- Home-page: https://github.com/daanzu/kaldi-active-grammar
- pypi: https://pypi.org/project/kaldi-active-grammar/
- Author: David Zurow
- Author-email: daanzu@gmail.com
- Authors: AUTHORS.txt
- License-File: LICENSE.txt


[gh-jwebmeister]: https://github.com/jwebmeister

[kag]: https://github.com/daanzu/kaldi-active-grammar
[kag-medium-model]: https://github.com/daanzu/kaldi-active-grammar/releases/download/v3.1.0/kaldi_model_daanzu_20211030-mediumlm.zip