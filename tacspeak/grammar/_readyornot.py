#
# This file is part of Tacspeak.
# (c) Copyright 2023 by Joshua Webb
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

import dragonfly
from dragonfly import (BasicRule, CompoundRule, MappingRule, RuleRef, Repetition, RecognitionObserver,
                       Function, Choice, IntegerRef, Grammar, Alternative, Literal, Text,
                       AppContext)
from dragonfly.engines.backend_kaldi.dictation import UserDictation as Dictation
from dragonfly.actions import (Key, Mouse)

import kaldi_active_grammar

# ---------------------------------------------------------------------------
# Create this module's grammar and the context under which it'll be active.

grammar_context = AppContext(executable="notepad")
grammar = Grammar("ReadyOrNot", 
                  # context=grammar_context,
                  )
grammar_priority = Grammar("ReadyOrNot_priority", 
                  # context=grammar_context,
                  )

# ---------------------------------------------------------------------------
# Rules which will be added to our grammar

# Will map keybindings to print()
DEBUG_NOCMD_PRINT_ONLY = True

# the minimum time between keys state changes (e.g. pressed then released), 
# it's to make sure key presses are registered in-game
min_delay = 3.3  # 100/(30 fps) = 3.3 (/100 seconds between frames)

# map of action to in-game key bindings
# https://dragonfly.readthedocs.io/en/latest/actions.html#key-names
ingame_key_bindings_kb = {
    "gold": "f5",
    "blue": "f6",
    "red": "f7",
    "cmd_1": "1",
    "cmd_2": "2",
    "cmd_3": "3",
    "cmd_4": "4",
    "cmd_5": "5",
    "cmd_6": "6",
    "cmd_7": "7",
    "cmd_8": "8",
    "cmd_9": "9",
    "cmd_back": "tab",
    "hold_cmd": "shift",
    "default_cmd": "z",
}

ingame_key_bindings_mouse = {
    "cmd_menu": "middle",
}

def debug_print_key(device, key):
    print(f'({device}_{key})')

if DEBUG_NOCMD_PRINT_ONLY:
    map_ingame_key_bindings = {k: Function(debug_print_key, device='kb', key=v) for k, v in ingame_key_bindings_kb.items()}
    map_ingame_key_bindings.update({k: Function(debug_print_key, device='m', key=v) for k, v in ingame_key_bindings_mouse.items()})
else:
    map_ingame_key_bindings = {k: Key(f'{v}:down/{min_delay}, {v}:up') for k, v in ingame_key_bindings_kb.items()}
    map_ingame_key_bindings.update({k: Mouse(f'{v}:down/{min_delay}, {v}:up') for k, v in ingame_key_bindings_mouse.items()})

for (k,v) in map_ingame_key_bindings.items():
    print(f'{k}:{v}')


# spoken phrase to value mappings
map_colors = {
    "current": "current",
    "gold": "gold",
    "blue": "blue",
    "red": "red",
}
map_tools = {
    "open": "open",
    "c2": "c2",
    "shotgun": "shotgun",
    "shotty": "shotgun",
    "ram": "ram",
    "battering ram": "ram",
    "ram it": "ram",
    "kick": "kick",
    "kick down": "kick",
    "kick it": "kick",
    "kick it down": "kick",
}
map_grenades = {
    "none": "none",
    "bang": "flashbang",
    "flashbang": "flashbang",
    "cs": "gas",
    "gas": "gas",
    "stinger": "stinger",
}
map_launcher_grenades = map_grenades
map_hold = {
    "go": "go",
    "hold": "hold",
    "on my mark": "hold",
    "on my order": "hold",
    "on my command": "hold",
    "hold for my order": "hold",
    "hold for my mark": "hold",
    "hold for my command": "hold",
}

def cmd_select_team(color):
    map_ingame_key_bindings[color]

class SelectTeam(CompoundRule):
    spec = "[<color>] team"
    extras = [Choice("color", map_colors)]
    defaults = {"color": "current"}

    def _process_recognition(self, node, extras):
        color = extras["color"]
        map_ingame_key_bindings[color].execute()


class SelectColor(CompoundRule):
    spec = "<color>"
    extras = [Choice("color", ["blue", "red", "gold"])]

    def _process_recognition(self, node, extras):
        color = extras["color"]
        map_ingame_key_bindings[color].execute()


class BreachAndClear(CompoundRule):
    spec = "[<color>] [team] [<hold>] [<tool>] [the door] [([(throw | deploy | use)] <grenade> | [deploy] fourtymil <launcher>)] [and] (breach and clear | clear) [it]"
    extras = [
        Choice("color", map_colors),
        Choice("hold", map_hold),
        Choice("tool", map_tools),
        Choice("grenade", map_grenades),
        Choice("launcher", map_launcher_grenades),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "tool": "open",
        "grenade": "none",
        "launcher": "none",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        tool = extras["tool"]
        grenade = extras["grenade"]
        launcher = extras["launcher"]

        deployed_nade = ""
        if grenade != "none":
            deployed_nade = grenade
        if launcher != "none":
            deployed_nade = deployed_nade + "40mm " + launcher
        fmt_deployed_nade = ""
        if len(deployed_nade) > 0:
            fmt_deployed_nade = " deploy " + deployed_nade

        print(f"{color} team {hold} {tool} the door{fmt_deployed_nade} breach and clear")


class YellFreeze(BasicRule):
    element = Alternative((
        Literal("freeze"),
        Literal("hands"),
        Literal("drop"),
        Literal("police"),
    ))

    def _process_recognition(self, node, extras):
        print("{0}".format(self.value(node)))

#---------------------------------------------------------------------------
# Recognition Observer - for mid-utterance recognition

class FreezeRecob(RecognitionObserver):

    def __init__(self):
        RecognitionObserver.__init__(self)
        self.words = None
        self.frozen = False

    def on_begin(self):
        self.frozen = False

    def on_partial_recognition(self, words, rule):
        self.words = words
        if (not self.frozen) and isinstance(rule, kaldi_active_grammar.KaldiRule) and rule.name == "ReadyOrNot_priority::YellFreeze":
            print("Freeze dirtbag!")
            self.frozen = True

    def on_recognition(self, words, results):
        self.words = words
        # print("words={0}".format(words))
        # print("rule={0}".format(rule))
        # print("node={0}".format(node))
        # print("results={0}".format(results))

    def on_failure(self, results):
        self.words = False
    
    def on_end(self, results):
        self.words = False
        self.frozen = False


#---------------------------------------------------------------------------
# Add rules to grammar and create RecognitionObserver instances

grammar.add_rule(SelectTeam())
grammar.add_rule(SelectColor())
grammar.add_rule(BreachAndClear())
grammar_priority.add_rule(YellFreeze())

freeze_recob = FreezeRecob()

#---------------------------------------------------------------------------
# Load the grammar instance, register RecognitionObservers, and define how 
# to unload them.

grammar.load()
grammar_priority.load()
freeze_recob.register()

# Unload function which will be called at unload time.
def unload():
    global grammar
    global grammar_priority
    global freeze_recob
    if grammar: grammar.unload()
    grammar = None
    if grammar_priority: grammar_priority.unload()
    grammar_priority = None
    freeze_recob.unregister()
    freeze_recob = None