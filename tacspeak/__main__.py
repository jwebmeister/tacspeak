#
# This file is part of Tacspeak.
# (c) Copyright 2023 by Joshua Webb
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Command-module loader for Tacspeak.

It scans the ``./tacspeak/grammar`` folder and loads any ``_*.py``.
"""

from __future__ import print_function

import logging
import os.path
import sys

from dragonfly import get_engine
from dragonfly import Grammar, MappingRule, Function, FuncContext
from dragonfly.engines.backend_kaldi.dictation import UserDictation as Dictation
from dragonfly.loader import CommandModuleDirectory
from dragonfly.log import setup_log

# --------------------------------------------------------------------------
# Set up basic logging.

if False:
    # Debugging logging for reporting trouble
    logging.basicConfig(level=10)
    logging.getLogger('grammar.decode').setLevel(20)
    logging.getLogger('grammar.begin').setLevel(20)
    logging.getLogger('compound').setLevel(20)
    logging.getLogger('kaldi.compiler').setLevel(10)
else:
    setup_log()


# --------------------------------------------------------------------------
# User notification / rudimentary UI. MODIFY AS DESIRED

# For message in ('sleep', 'wake')
def notify(message):
    if message == 'sleep':
        print("Sleeping...")
        # get_engine().speak("Sleeping")
    elif message == 'wake':
        print("Awake...")
        # get_engine().speak("Awake")


# --------------------------------------------------------------------------
# Sleep/wake grammar. (This can be unused or removed if you don't want it.)

sleeping = False

def load_sleep_wake_grammar(initial_awake):
    sleep_grammar = Grammar("sleep_priority")

    def sleep(force=False):
        global sleeping
        if not sleeping or force:
            sleeping = True
            sleep_grammar.set_exclusiveness(True)
        notify('sleep')

    def wake(force=False):
        global sleeping
        if sleeping or force:
            sleeping = False
            sleep_grammar.set_exclusiveness(False)
        notify('wake')

    class SleepRule(MappingRule):
        mapping = {
            "start listening":  Function(wake) + Function(lambda: get_engine().start_saving_adaptation_state()),
            "stop listening":   Function(lambda: get_engine().stop_saving_adaptation_state()) + Function(sleep),
            "halt listening":   Function(lambda: get_engine().stop_saving_adaptation_state()) + Function(sleep),
        }
    sleep_grammar.add_rule(SleepRule())

    sleep_noise_rule = MappingRule(
        name = "sleep_noise_rule",
        mapping = { "<text>": Function(lambda text: False and print(text)) },
        extras = [ Dictation("text") ],
        context = FuncContext(lambda: sleeping),
    )
    sleep_grammar.add_rule(sleep_noise_rule)

    sleep_grammar.load()

    if initial_awake:
        wake(force=True)
    else:
        sleep(force=True)


# --------------------------------------------------------------------------
# Main event driving loop.

def main():
    logging.basicConfig(level=logging.INFO)

    path = os.path.join(os.getcwd(), os.path.relpath("tacspeak/grammar/"))

    # Set any configuration options here as keyword arguments.
    # See Kaldi engine documentation for all available options and more info.
    engine = get_engine('kaldi',
        # model_dir='kaldi_model',  # default model directory
        # vad_aggressiveness=3,  # default aggressiveness of VAD
        # vad_padding_start_ms=150,  # default ms of required silence before VAD
        vad_padding_end_ms=250,  # default ms of required silence after VAD
        # vad_complex_padding_end_ms=500,  # default ms of required silence after VAD for complex utterances
        # input_device_index=None,  # set to an int to choose a non-default microphone
        # lazy_compilation=True,  # set to True to parallelize & speed up loading
        # retain_dir=None,  # set to a writable directory path to retain recognition metadata and/or audio data
        # retain_audio=None,  # set to True to retain speech data wave files in the retain_dir (if set)
        listen_key=0x10, # 0x10=SHIFT key, 0x05=X1 mouse button, 0x06=X2 mouse button, see https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
        listen_key_toggle=0, # 0 for toggle mode off; 1 for toggle mode on; 2 for global toggle on (use VAD); -1 for toggle mode off but allow priority grammar even when key not pressed
        auto_add_to_user_lexicon=False,
    )

    # Call connect() now that the engine configuration is set.
    engine.connect()

    # Load grammars.
    # load_sleep_wake_grammar(True)
    directory = CommandModuleDirectory(path)
    directory.load()

    # Define recognition callback functions.
    def on_begin():
        """"""
        # print("Speech start detected.")

    def on_recognition(words):
        """"""
        message = u"Recognized: %s" % u" ".join(words)

    def on_failure():
        """"""
        # print("Sorry, what was that?")

    # Start the engine's main recognition loop
    engine.prepare_for_recognition()
    try:
        print("Listening...")
        engine.do_recognition(on_begin, on_recognition, on_failure)
    except KeyboardInterrupt:
        pass

    # Disconnect from the engine, freeing its resources.
    engine.disconnect()


if __name__ == "__main__":
    main()