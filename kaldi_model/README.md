## Simple version

The model files required to use Tacspeak are included in, and can be downloaded from, [Tacspeak releases](https://github.com/jwebmeister/tacspeak/releases).  

Models in Tacspeak releases have already been re-compiled using an appropriate `user_lexicon.txt`.  

Just download the .zip of the model, extract the `kaldi_model` folder (and files) into the folder containing `Tacspeak.exe` (or cli.py).


We might change this option in the future, specifically we might not offer this simple version and only offer the complex version; anticipating issues with storage.

## Complex version

Kaldi Active Grammar version 3.1.0 [medium model][kag-medium-model], is required to use this software, and it must(!) be re-compiled with the `user_lexicon.txt` included with Tacspeak.

The file `<project folder>/kaldi_model/user_lexicon.txt` has been created by [JWebmeister][gh-jwebmeister], intended to be combined with the [v3.1.0 medium model files][kag-medium-model] and re-compiled using Kaldi Active Grammar (or via the Tacspeak.exe --recompile-model).

### Complex install instructions:

#### Option 1
1. In PowerShell: cd to Tacspeak folder (containing Tacspeak.exe or cli.py)
2. from the project folder, run: `./scripts/download_extract_model.ps1`
    - this will download the medium model .zip (>600MB) and extract into `./tmp/`
    - this will also copy `user_lexicon.txt` and `README.md` from `./kaldi_model` and paste into `./tmp/kaldi_model/`
3. from the project folder, run: `./scripts/move_extracted_model.ps1`
    - this will move all from `./tmp/kaldi_model/` into `./kaldi_model/`
4. from the project folder, run: `./scripts/compile_dictation_graph.ps1`
    - note: it will take on the order of 30 minutes.
    - this will re-compile the model located in `./kaldi_model/`
    - it should use either of tacspeak.exe, cli.py, or the kaldi_active_grammar package.
    

#### Option 2
1. recommended to create a new virtual environment, 
    - `python -m venv <project folder>/.venv`
2. `pip install 'kaldi-active-grammar[g2p_en]'`
3. Download the [medium model files][kag-medium-model] and extract to a temporary folder, 
    - e.g. `<temp folder>/kaldi_model`
4. copy the file `<project folder>/kaldi_model/user_lexicon.txt` into the temporary folder, replacing the existing `<temp folder>/kaldi_model/user_lexicon.txt`
5. move all files and folders from `<temp folder>/kaldi_model/*` into `<project folder>/kaldi_model/*`
6. cd `<project folder>`
7. Recompile graph (this will take on the order of 30 minutes), either via:
    - `tacspeak.exe --recompile_model kaldi_model`; or
    - `python ./cli.py --recompile_model kaldi_model`; or
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