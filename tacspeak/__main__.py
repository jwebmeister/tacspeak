#
# This file is part of Tacspeak.
# (c) Copyright 2023 by Joshua Webb
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Command-module loader for Tacspeak.

It scans the ``./tacspeak/grammar/`` folder and loads any ``_*.py``.
It also loads ``./tacspeak/user_settings.py`` for engine settings.
"""

from __future__ import print_function

import logging
import os.path
import sys

from dragonfly import get_engine
from dragonfly import Grammar, MappingRule, Function, FuncContext
from dragonfly.engines.backend_kaldi.dictation import UserDictation as Dictation
from dragonfly.loader import CommandModuleDirectory, CommandModule
from dragonfly.log import setup_log

# --------------------------------------------------------------------------
# Main event driving loop.

def main():
    user_settings_path = os.path.join(os.getcwd(), os.path.relpath("tacspeak/user_settings.py"))
    user_settings = CommandModule(user_settings_path)
    user_settings.load()
    try:
        DEBUG_MODE = (sys.modules["user_settings"]).DEBUG_MODE
        KALDI_ENGINE_SETTINGS = (sys.modules["user_settings"]).KALDI_ENGINE_SETTINGS
    except NameError:
        print("Failed to load `tacspeak/user_settings.py`. Using default settings as fallback.")
        DEBUG_MODE = False
        KALDI_ENGINE_SETTINGS = {
            "listen_key":0x10, # 0x10=SHIFT key, 0x05=X1 mouse button, 0x06=X2 mouse button, see https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
            "listen_key_toggle":0, # 0 for toggle mode off; 1 for toggle mode on; 2 for global toggle on (use VAD); -1 for toggle mode off but allow priority grammar even when key not pressed
            "vad_padding_end_ms":250, # ms of required silence after VAD
            "auto_add_to_user_lexicon":False, # this requires g2p_en (which isn't installed by default)
            "allow_online_pronunciations":False,
            # "input_device_index":None, # set to an int to choose a non-default microphone
            # "vad_aggressiveness":3, # default aggressiveness of VAD
            # "vad_padding_start_ms":150, # default ms of required silence before VAD
            # "model_dir":'kaldi_model', # default model directory
            # "tmp_dir":None, 
            # "audio_input_device":None, 
            # "audio_self_threaded":True, 
            # "audio_auto_reconnect":True, 
            # "audio_reconnect_callback":None,
            # "retain_dir":None, # set to a writable directory path to retain recognition metadata and/or audio data
            # "retain_audio":None, # set to True to retain speech data wave files in the retain_dir (if set)
            # "retain_metadata":None, 
            # "retain_approval_func":None,
            # "vad_complex_padding_end_ms":600, # default ms of required silence after VAD for complex utterances
            # "lazy_compilation":True, # set to True to parallelize & speed up loading
            # "invalidate_cache":False,
            # "expected_error_rate_threshold":None,
            # "alternative_dictation":None,
            # "compiler_init_config":None, 
            # "decoder_init_config":None,
        }
    
    if DEBUG_MODE:
        def log_handlers():
            log_file_path = os.path.join(os.path.expanduser("~"), ".dragonfly.log")
            log_file_handler = logging.FileHandler(log_file_path)
            log_file_formatter = logging.Formatter("%(asctime)s %(name)s (%(levelname)s): %(message)s")
            log_file_handler.setFormatter(log_file_formatter)

            log_stream_handler = logging.StreamHandler()
            log_stream_formatter = logging.Formatter("%(name)s (%(levelname)s): %(message)s")
            log_stream_handler.setFormatter(log_stream_formatter)
            return [log_stream_handler, log_file_handler]

        logging.basicConfig(level=10, handlers=log_handlers())
        logging.getLogger('grammar.decode').setLevel(20)
        logging.getLogger('grammar.begin').setLevel(20)
        logging.getLogger('compound').setLevel(20)
        logging.getLogger('engine').setLevel(15)
        logging.getLogger('kaldi').setLevel(15)
        logging.getLogger('kaldi.compiler').setLevel(15)
    else:
        setup_log()

    # Set any configuration options here as keyword arguments.
    # See Kaldi engine documentation for all available options and more info.
    engine = get_engine('kaldi',**KALDI_ENGINE_SETTINGS)

    # Call connect() now that the engine configuration is set.
    engine.connect()

    # Load grammars.
    grammar_path = os.path.join(os.getcwd(), os.path.relpath("tacspeak/grammar/"))
    directory = CommandModuleDirectory(grammar_path)
    directory.load()

    # Start the engine's main recognition loop
    engine.prepare_for_recognition()
    try:
        print("Ready to listen...")
        engine.do_recognition()
    except KeyboardInterrupt:
        pass

    # Disconnect from the engine, freeing its resources.
    engine.disconnect()


if __name__ == "__main__":
    main()