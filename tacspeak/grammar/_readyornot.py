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
# https://dragonfly.readthedocs.io/en/latest/actions.html#mouse-specification-format
ingame_key_bindings = {
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
    "cmd_hold": "shift",
    "cmd_default": "z",
    "cmd_menu": "mouse_middle",
}

def debug_print_key(device, key):
    print(f'({device}_{key})')

if DEBUG_NOCMD_PRINT_ONLY:
    map_ingame_key_bindings = {k: Function(debug_print_key, device='m', key=v) if "mouse_" in v 
                               else Function(debug_print_key, device='kb', key=v) 
                               for k, v in ingame_key_bindings.items()}
else:
    map_ingame_key_bindings = {k: Mouse(f'{v}:down/{min_delay}, {v}:up') if "mouse_" in v 
                               else Key(f'{v}:down/{min_delay}, {v}:up') 
                               for k, v in ingame_key_bindings.items()}

# key bindings
print("-- Ready or Not keybindings --")
for (k,v) in map_ingame_key_bindings.items():
    print(f'{k}:{v}')
print("-- Ready or Not keybindings --")

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
    "stinger": "stinger",
    "cs": "gas",
    "gas": "gas",
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
map_stack_tool = {
    "stack up": "stack",
    "mirror": "mirror",
    "mirror under": "mirror",
    "disarm": "disarm",
    "disarm trap": "disarm",
    "wedge": "wedge",
}

NULL_ACTION = Function(lambda: print("NULL_ACTION") if DEBUG_NOCMD_PRINT_ONLY else None)

# press down or up on hold command key, direction="up"|"down"
def action_hold(direction):
    if DEBUG_NOCMD_PRINT_ONLY:
        device = 'm' if 'mouse_' in ingame_key_bindings["cmd_hold"] else 'kb'
        return Function(debug_print_key, device=device, key=f'{ingame_key_bindings["cmd_hold"]}:{direction}') 
    else:
        return Key(f'{ingame_key_bindings["cmd_hold"]}:{direction}')

def cmd_select_team(color):
    if color != "current":
        return map_ingame_key_bindings[color]
    else:
        return NULL_ACTION

def cmd_breach_and_clear(color, hold, tool, grenade, launcher):
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    if tool == "open":
        actions += map_ingame_key_bindings["cmd_2"]
    else:
        actions += map_ingame_key_bindings["cmd_3"]
        match tool:
            case "kick":
                actions += map_ingame_key_bindings["cmd_1"]
            case "shotgun":
                actions += map_ingame_key_bindings["cmd_2"]
            case "c2":
                actions += map_ingame_key_bindings["cmd_3"]
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    match grenade:
        case "none":
            actions += map_ingame_key_bindings["cmd_1"]
        case "flashbang":
            actions += map_ingame_key_bindings["cmd_2"]
        case "stinger":
            actions += map_ingame_key_bindings["cmd_3"]
        case "gas":
            actions += map_ingame_key_bindings["cmd_4"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    actions.execute()
    

class SelectTeam(CompoundRule):
    spec = "[<color>] team"
    extras = [Choice("color", map_colors)]
    defaults = {"color": "current"}

    def _process_recognition(self, node, extras):
        color = extras["color"]
        cmd_select_team(color).execute()


class SelectColor(CompoundRule):
    spec = "<color>"
    extras = [Choice("color", ["blue", "red", "gold"])]

    def _process_recognition(self, node, extras):
        color = extras["color"]
        cmd_select_team(color).execute()

class BreachAndClear(CompoundRule):
    spec1 = "[<color>] [team] [<hold>] [<tool>] [the door] [([(throw | deploy | use)] <grenade> | [deploy] fourtymil <launcher>)] [and] (breach and clear | clear) [it]"
    spec2 = "[<color>] [team] [<hold>] [<tool>] [the door] [and] (breach and clear | clear) [it] [with] (<grenade> | fourtymil <launcher>) [grenade]"
    spec = f"(({spec1}) | ({spec2}))"
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
        cmd_breach_and_clear(color, hold, tool, grenade, launcher)


class OpenDoor(CompoundRule):
    spec = "[<color>] [team] [<hold>] open [the] door"
    extras = [
        Choice("color", map_colors),
        Choice("hold", map_hold),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]

        print(f"{color} team {hold} open the door")


class StackUp(CompoundRule):
    spec1 = "[<color>] [team] [<hold>] stack up [on] [the] [door] [use] [<stack_tool>] [(the door | it)]"
    spec2 = "[<color>] [team] [<hold>] [use] <stack_tool> [((on | the) door | it)]"
    spec = f"(({spec1}) | ({spec2}))"
    extras = [
        Choice("color", map_colors),
        Choice("hold", map_hold),
        Choice("stack_tool", map_stack_tool),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "stack_tool": "stack",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        stack_tool = extras["stack_tool"]

        print(f"{color} team {hold} stack up {stack_tool}")


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
grammar.add_rule(OpenDoor())
grammar.add_rule(StackUp())
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