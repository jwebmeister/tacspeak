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
from tacspeak.test_model import test_model, test_model_dictation, transcribe_wav, transcribe_wav_dictation
from dragonfly import get_engine
import logging

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
                                + " Example: --test_model './testaudio/recorder.tsv' './kaldi_model/' './kaldi_model/lexicon.txt' 4"))
    parser.add_argument('--test_dictation', action='store_true',
                        help=('only used together with --test_model. tests model using raw dictation graph, irrespective of grammar modules.'
                              + " Example: --test_model './testaudio/recorder.tsv' './kaldi_model/' './kaldi_model/lexicon.txt' 4 --test_dictation"))
    parser.add_argument('--transcribe_wav', dest='transcribe_wav', action='store',
                        metavar=('wav_path', 'out_txt_path', 'model_dir'), nargs=3,
                        help=('transcribe a wav file using active grammar modules, output to txt file.'
                                + " Example: --transcribe_wav 'audio.wav' 'audio.txt' './kaldi_model/'"))
    parser.add_argument('--transcribe_dictation', action='store_true',
                        help=('only used together with --transcribe_wav. transcribes using raw dictation graph, irrespective of grammar modules.'
                              + " Example: --transcribe_wav 'audio.wav' 'audio.txt' './kaldi_model/' --transcribe_dictation"))
    args = parser.parse_args()
    if args.model_dir is not None and os.path.isdir(args.model_dir):
        _log = logging.getLogger('kaldi')
        logging.basicConfig(level=5)
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
            if args.test_dictation:
                calculator, cmd_overall_stats = test_model_dictation(tsv_file, model_dir, lexicon_file, num_threads)
                outfile_path = 'test_model_output_dictation_tokens.txt'
            else:
                calculator, cmd_overall_stats = test_model(tsv_file, model_dir, lexicon_file, num_threads)
                outfile_path = 'test_model_output_tokens.txt'

            with open(outfile_path, 'w', encoding='utf-8') as outfile:
                outfile.write(f"\n{calculator.overall_string()}\n")
                for item in calculator.data.items():
                    outfile.write(f"\n{str(item)}")
                outfile.write("\n")
                for entry in calculator.ranked_worst_to_best_list():
                    outfile.write(f"\n{str(entry)}")
            
            overall_entry_1 = (model_dir, tsv_file, "Dictation" if args.test_dictation else "Command", "WER", calculator.overall_string())
            overall_entry_2 = (model_dir, tsv_file, "Dictation" if args.test_dictation else "Command", "CMDERR", cmd_overall_stats)
            with open('test_model_output_overall.txt', 'a', encoding='utf-8') as outfile:
                outfile.write(f"{overall_entry_1}\n")
                if not args.test_dictation:
                    outfile.write(f"{overall_entry_2}\n")

            return calculator.overall_string(), cmd_overall_stats
        return
    if args.transcribe_wav:
        if args.transcribe_wav[0] is not None and os.path.isfile(args.transcribe_wav[0]):
            wav_path = args.transcribe_wav[0]
            try:
                out_txt_path = args.transcribe_wav[1]
            except Exception:
                out_txt_path = None
            try:
                model_dir = args.transcribe_wav[2]
            except Exception:
                model_dir = "./kaldi_model/"
            if args.transcribe_dictation:
                entry = transcribe_wav_dictation(wav_path, out_txt_path, model_dir)
            else:
                entry = transcribe_wav(wav_path, out_txt_path, model_dir)
            print(f"{entry}")
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