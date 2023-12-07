#
# This file is part of Tacspeak.
# (c) Copyright 2023 by Joshua Webb
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

import argparse
import os
import kaldi_active_grammar
from tacspeak.__main__ import main as tacspeak_main


def main():
    parser = argparse.ArgumentParser(description='Start speech recognition.')
    parser.add_argument('--recompile_model', dest='model_dir', action='store',
                        metavar='model_dir', nargs='?', const='kaldi_model/',
                        help='recompile the model in `model_dir` (default is kaldi_model/), for changes to user_lexicon.txt')
    args = parser.parse_args()
    if args.model_dir is not None and os.path.isdir(args.model_dir):
        compiler = kaldi_active_grammar.Compiler(args.model_dir)
        print("Compiling dictation graph (approx. 15 minutes)...")
        compiler.compile_agf_dictation_fst()
    else:
        tacspeak_main()

if __name__ == "__main__":
    main()