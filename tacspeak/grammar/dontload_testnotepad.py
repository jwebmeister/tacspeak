#
# This file is part of Tacspeak.
# (c) Copyright 2023-2024 by Joshua Webb
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#


from dragonfly import (CompoundRule, AppContext, Grammar, Dictation, MappingRule, Function, Choice)
# from dragonfly.engines.backend_kaldi.dictation import UserDictation as Dictation
from dragonfly.actions import Text

test_grammar_context = AppContext(executable="notepad")
test_grammar = Grammar("testnotepad", context=test_grammar_context)

# ----------------------------------------------------------------

class TestNotepadDictationRule(CompoundRule):
    spec = "<text>"
    extras = [Dictation("text")]

    def _process_recognition(self, node, extras):
        # Retrieve the recognized text and format it.
        text = extras.get("text").format()
        print(f"text: {text}")
        Text(f"{text}\n").execute()

test_grammar.add_rule(TestNotepadDictationRule())

# ----------------------------------------------------------------

def print_type_cmd_text(cmd_text):
        print(f"text: {cmd_text}")
        Text(f"{cmd_text}\n").execute()

class TestNotepadCommandRule(MappingRule):
    mapping = {
        '<cmd_text>': Function(print_type_cmd_text),
        }
    extras = [
         Choice('cmd_text', ['turtle', 'bear', 'beaver', 'dove'])
    ]

test_grammar.add_rule(TestNotepadCommandRule())

# ----------------------------------------------------------------

# Load the grammar and set it as exclusive, meaning that the engine will
#  only recognize from this grammar (and any other exclusive grammar).
test_grammar.load()
test_grammar.set_exclusiveness(True)

# Unload function which will be called by natlink at unload time.
def unload():
    global test_grammar
    if test_grammar: test_grammar.unload()
    test_grammar = None