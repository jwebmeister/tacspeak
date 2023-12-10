The Kaldi Active Grammar version 3.1.0 medium model, is required to use this software.

The file `<project folder>\kaldi_model\user_lexicon.txt` has been created by [JWebmeister][gh-jwebmeister], intended to be combined with [v3.1.0 medium model files][kag-medium-model].

Install instructions:
- recommended to create a new virtual environment, 
    - `python -m venv <project folder>\.venv`
- `pip install 'kaldi-active-grammar[g2p_en]'`
- Download the [medium model files][kag-medium-model] and extract to a temporary folder, 
    - e.g. `<temp folder>\kaldi_model`
- copy the file `<project folder>\kaldi_model\user_lexicon.txt` into the temporary folder, replacing the existing `<temp folder>\kaldi_model\user_lexicon.txt`
- move all files and folders from `<temp folder>\kaldi_model\*` into `<project folder>\kaldi_model\*`
- cd `<project folder>`
- Recompile graph (this will take on the order of 15 minutes), either via:
    - `cli.exe --recompile-graph kaldi_model`; or
    - `python ./cli.py --recompile-graph kaldi_model`; or
    - `python -m kaldi_active_grammar compile_agf_dictation_graph -m kaldi_model`

[gh-jwebmeister]: https://github.com/jwebmeister
[kag-medium-model]: https://github.com/jwebmeister/kaldi-active-grammar/releases/tag/v3.1.0

---

Details of the [originating projects][kag-original] source below:

- Name: kaldi-active-grammar
- Version: 3.1.0
- Summary: Kaldi speech recognition with grammars that can be set active/inactive dynamically at decode-time
- License: AGPL-3.0
- Home-page: https://github.com/daanzu/kaldi-active-grammar


[kag-original]: https://github.com/daanzu/kaldi-active-grammar