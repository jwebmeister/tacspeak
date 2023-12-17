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

from __future__ import print_function, annotations
from typing import TYPE_CHECKING

import logging
from pathlib import Path
import sys

from dragonfly import get_engine
from dragonfly.loader import CommandModuleDirectory, CommandModule
from dragonfly.log import default_levels

if TYPE_CHECKING:
    from logging import FileHandler, StreamHandler

# --------------------------------------------------------------------------
# Main event driving loop.


# noinspection PyPep8Naming
def main():
    user_settings_path: Path = Path("./tacspeak/user_settings.py")
    user_settings: CommandModule = CommandModule(user_settings_path)
    user_settings.load()
    try:
        DEBUG_MODE = (sys.modules["user_settings"]).DEBUG_MODE
        DEBUG_HEAVY_DUMP_GRAMMAR = (sys.modules["user_settings"]).DEBUG_HEAVY_DUMP_GRAMMAR
        KALDI_ENGINE_SETTINGS = (sys.modules["user_settings"]).KALDI_ENGINE_SETTINGS
    except NameError:
        print("Failed to load `tacspeak/user_settings.py`. Using default settings as fallback.")
        DEBUG_MODE = False
        DEBUG_HEAVY_DUMP_GRAMMAR = False
        KALDI_ENGINE_SETTINGS = {
            "listen_key": 0x10,  # 0x10=SHIFT key, 0x05=X1 mouse button, 0x06=X2 mouse button, see https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
            "listen_key_toggle": 0,  # 0 for toggle mode off; 1 for toggle mode on; 2 for global toggle on (use VAD); -1 for toggle mode off but allow priority grammar even when key not pressed
            "vad_padding_end_ms": 250,  # ms of required silence after VAD
            "auto_add_to_user_lexicon": False,  # this requires g2p_en (which isn't installed by default)
            "allow_online_pronunciations": False,
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

    def log_handlers() -> tuple[StreamHandler, FileHandler]:
        log_stream_handler: StreamHandler = logging.StreamHandler()
        log_stream_handler.setFormatter(
            fmt=logging.Formatter(
                fmt="%(name)s (%(levelname)s): %(message)s"
            )
        )
        log_file_handler: FileHandler = logging.FileHandler(filename=Path("./.tacspeak.log"))
        log_file_handler.setFormatter(
            fmt=logging.Formatter(
                fmt="%(asctime)s %(name)s (%(levelname)s): %(message)s"
            )
        )
        return log_stream_handler, log_file_handler

    def setup_loggers(use_default_levels: bool = True) -> None:
        for _name, _levels in default_levels.items():
            stderr_level, file_level = _levels
            log_stream_handler, log_file_handler = log_handlers()

            if use_default_levels:
                log_stream_handler.setLevel(stderr_level)
                log_file_handler.setLevel(file_level)

            logger = logging.getLogger(_name)
            logger.setLevel(min(stderr_level, file_level))
            logger.propagate = False

            for _handler in (log_stream_handler, log_file_handler):
                logger.addHandler(_handler)

    if not DEBUG_MODE:
        setup_loggers()
    else:
        logger_levels: dict[str, int] = {
            "grammar.decode": 20,
            "grammar.begin": 20,
            "compound": 20,
            "engine": 15,
            "kaldi": 15,
            "kaldi.compiler": 15,
            "kaldi.wrapper": 15,
            "action.exec": 10,
        }
        setup_loggers(use_default_levels=False)
        for name, level in logger_levels.items():
            logging.getLogger(name).setLevel(level)

    # Set any configuration options here as keyword arguments.
    # See Kaldi engine documentation for all available options and more info.
    engine = get_engine(
        name='kaldi',
        **KALDI_ENGINE_SETTINGS
    )

    # Call connect() now that the engine configuration is set.
    engine.connect()

    # Load grammars.
    grammar_path: Path = Path("./tacspeak/grammar")
    directory = CommandModuleDirectory(path=grammar_path)
    directory.load()

    log_recognition = logging.getLogger('on_recognition')
    for handler in log_handlers():
        log_recognition.addHandler(handler)
    log_recognition.setLevel(20)

    # Define recognition callback functions.
    def on_begin():
        pass

    def on_recognition(words, results):
        message = f"{results.kaldi_rule} | {' '.join(words)}"
        log_recognition.log(
            level=20,
            msg=message
        )

    def on_failure():
        pass

    def on_end():
        pass

    # Start the engine's main recognition loop
    engine.prepare_for_recognition()
    try:
        print("Ready to listen...")
        engine.do_recognition(
            begin_callback=on_begin,
            recognition_callback=on_recognition,
            failure_callback=on_failure,
            end_callback=on_end
        )
    except KeyboardInterrupt:
        pass

    # Disconnect from the engine, freeing its resources.
    engine.disconnect()


if __name__ == "__main__":
    main()
