if Test-Path "./tacspeak.exe" {
    ./tacspeak.exe --recompile_model kaldi_model
    return True
}
if Test-Path "./cli.py" {
    python ./cli.py --recompile_model kaldi_model
    return True
}

python -m kaldi_active_grammar compile_agf_dictation_graph -m kaldi_model