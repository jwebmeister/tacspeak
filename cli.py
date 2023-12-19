#
# This file is part of Tacspeak.
# (c) Copyright 2023 by Joshua Webb
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

import argparse
import os
from kaldi_active_grammar import Compiler, disable_donation_message
import tacspeak
from tacspeak.__main__ import main as tacspeak_main
from dragonfly import get_engine

import kaldifst
import graphviz

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
                                + ' useful for setting `input_device_index` in ./tacspeak/user_settings.py'))
    parser.add_argument('--visualise_fst', dest='fst_filepath', action='store',
                        metavar=('fst_filepath', 'model_words_txt_filepath'), nargs=2,
                        help='generate .gv (dot) and .svg for visualisation of a FST file. Only use with small (~200 kB) files!')
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
    if args.fst_filepath[0] is not None and os.path.isfile(args.fst_filepath[0]) and args.fst_filepath[1] is not None and os.path.isfile(args.fst_filepath[1]):
        fst_filepath = args.fst_filepath[0]
        fst_filename_noext = os.path.splitext(fst_filepath)[0]
        model_words_txt_filepath = args.fst_filepath[1]
        print(fst_filename_noext)
        fst = kaldifst.StdFst.read(fst_filepath)
        sym = kaldifst.SymbolTable()
        with open(model_words_txt_filepath, 'r', encoding='utf-8') as sym_file:
            for line in sym_file:
                line_split = line.strip().split(' ')
                sym.add_symbol(symbol=line_split[0], key=int(line_split[1]))
        fst_dot = kaldifst.draw(fst, osymbols=sym, acceptor=False, portrait=True)
        source = graphviz.Source(fst_dot)
        source.render(outfile=f"{fst_filename_noext}.svg")
        return
    tacspeak_main()

def print_notices():
    text = """
    Tacspeak - speech recognition for gaming
    © Copyright 2023 by Joshua Webb

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