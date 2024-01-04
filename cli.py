#
# This file is part of Tacspeak.
# (c) Copyright 2023-2024 by Joshua Webb
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

import argparse
import os
from kaldi_active_grammar import Compiler, disable_donation_message
import tacspeak
from tacspeak.__main__ import main as tacspeak_main
from tacspeak.test_model import test_model
from dragonfly import get_engine

def main():
    print(f"Tacspeak version {tacspeak.__version__}")
    print_notices()
    disable_donation_message()
    
    parser = argparse.ArgumentParser(description='Start speech recognition.')
    parser.add_argument('--recompile_model', dest='model_dir', action='store',
                        metavar='model_dir', nargs='?', const='kaldi_model/',
                        help='recompile the model in `model_dir` (default is kaldi_model/), for changes to user_lexicon.txt')
    parser.add_argument('--print_mic_list', action='store_true',
                        help=('see a list of available input devices and their corresponding indexes and names.' 
                                + ' useful for setting `audio_input_device` in ./tacspeak/user_settings.py'))
    parser.add_argument('--test_model', dest='test_model', action='store',
                        metavar=('tsv_file', 'model_dir', 'lexicon_file', 'num_threads'), nargs=4,
                        help=('test model + active grammar recognition using test audio specified in .tsv file.'
                                + " Example: --test_model './testaudio/recorder.tsv' './kaldi_model/' './kaldi_model/lexicon.txt' 2"))
    args = parser.parse_args()
    if args.model_dir is not None and os.path.isdir(args.model_dir):
        compiler = Compiler(args.model_dir)
        print("Compiling dictation graph (approx. 30 minutes)...")
        compiler.compile_agf_dictation_fst()
        return
    if args.print_mic_list:
        get_engine('kaldi').print_mic_list()
        input("Press enter key to exit.")
        return
    if args.test_model:
        if args.test_model[0] is not None and os.path.isfile(args.test_model[0]) and args.test_model[1] is not None and os.path.isdir(args.test_model[1]):
            tsv_file = args.test_model[0]
            model_dir = args.test_model[1]
            try:
                lexicon_file = args.test_model[2]
                if not os.path.isfile(lexicon_file):
                    lexicon_file = None
            except Exception as e:
                print(f"{e}")
                lexicon_file = None
            try:
                num_threads = int(args.test_model[3])
                if not isinstance(num_threads, int) or num_threads < 1:
                    num_threads = 1
            except Exception as e:
                print(f"{e}")
                num_threads = 1
            print(f"{tsv_file},{model_dir},{lexicon_file},{num_threads}")
            calculator = test_model(tsv_file, model_dir, lexicon_file, num_threads)
            with open('test_model_output_tokens.txt', 'w', encoding='utf-8') as outfile:
                outfile.write(f"\n{calculator.overall_string()}\n")
                for item in calculator.data.items():
                    outfile.write(f"\n{str(item)}")
                outfile.write("\n")
                for entry in calculator.ranked_worst_to_best_list():
                    outfile.write(f"\n{str(entry)}")
        return
    tacspeak_main()

def print_notices():
    text = """
    Tacspeak - speech recognition for gaming
    © Copyright 2023-2024 by Joshua Webb

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
        """
    print(text)

if __name__ == "__main__":
    main()