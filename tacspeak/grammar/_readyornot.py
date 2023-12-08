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
    "interact": "f",
    "yell": "f",
}

def debug_print_key(device, key):
    print(f'({device}_{key})')

if DEBUG_NOCMD_PRINT_ONLY:
    map_ingame_key_bindings = {k: Function(debug_print_key, device='m', key=v.replace("mouse_", "")) if "mouse_" in v 
                               else Function(debug_print_key, device='kb', key=v) 
                               for k, v in ingame_key_bindings.items()}
else:
    map_ingame_key_bindings = {k: Mouse(f'{v.replace("mouse_", "")}:down/{min_delay}, {v.replace("mouse_", "")}:up') if "mouse_" in v 
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
map_breach_tools = {
    "open": "open",
    "kick [it] [down]": "kick",
    "(shotgun | shotty)": "shotgun",
    "c2": "c2",
    "[battering] ram [it]": "ram",
    "((leader | lead | i) will | wait for my) (open | breach | prep | kick | shotgun | shotty | [prep] c2 | [battering] ram )": "leader",
}
map_grenades = {
    "none": "none",
    "(bang | flashbang | flash)": "flashbang",
    "stinger": "stinger",
    "(cs | gas | cs gas)": "gas",
    "(fourtymil | launcher)": "launcher",
    "((leader | lead | i) will [(throw | use | deploy)] | wait for my) (grenade | flashbang | bang | flash | stinger | cs | gas) [grenade]": "leader",
}
map_hold = {
    "go": "go",
    "hold": "hold",
    "(on | hold for) my (mark | order | command)": "hold",
}
map_stack_tools = {
    "stack up": "stack",
    "mirror [under]": "mirror",
    "disarm [trap]": "disarm",
    "wedge": "wedge",
}

# 1.0 speculative
map_stack_split = {
    "split": "split",
    "left": "left",
    "right": "right",
}
map_formation = {
    "single file": "single",
    "double file": "double",
    "diamond": "diamond",
    "wedge": "wedge",
}
map_npc_interact = {
    "restrain [(them | him | her)]": "restrain",
    "(move | come) (here | forward)": "move here",
    "(move | come) [to] my position": "move my position",
    "stop [there]": "move stop",
    "deploy": "deploy",
    "turn around [and stay still]": "turn around",
    "move to [the] exit": "move to exit",
}

NULL_ACTION = Function(lambda: print("NULL_ACTION") if DEBUG_NOCMD_PRINT_ONLY else None)

# press down or up on hold command key, direction="up"|"down"
def action_hold(direction):
    if DEBUG_NOCMD_PRINT_ONLY:
        device = 'm' if 'mouse_' in ingame_key_bindings["cmd_hold"] else 'kb'
        return Function(debug_print_key, device=device, key=f'{ingame_key_bindings["cmd_hold"]}:{direction}') 
    else:
        return Key(f'{ingame_key_bindings["cmd_hold"]}:{direction}')
    
def cmd_yell():
    return map_ingame_key_bindings["yell"]

def cmd_select_team(color):
    if color != "current":
        return map_ingame_key_bindings[color]
    else:
        return NULL_ACTION
    
def cmd_open_door(color, hold):
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    actions += map_ingame_key_bindings["cmd_4"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    actions.execute()


def cmd_breach_and_clear(color, hold, tool, grenade):
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
            case "ram":
                actions += map_ingame_key_bindings["cmd_4"]
            case "leader":
                actions += map_ingame_key_bindings["cmd_5"]
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
        case "launcher":
            actions += map_ingame_key_bindings["cmd_5"]
        case "leader":
            actions += map_ingame_key_bindings["cmd_6"]
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
    spec1 = "[<color>] [team] [<hold>] [<tool>] [the door] [you] [[(throw | deploy | use)] <grenade>] [and] (breach and clear | clear) [it]"
    spec2 = "[<color>] [team] [<hold>] [<tool>] [the door] [you] [and] (breach and clear | clear) [it] [with] <grenade> [grenade]"
    spec = f"(({spec1}) | ({spec2}))"
    extras = [
        Choice("color", map_colors),
        Choice("hold", map_hold),
        Choice("tool", map_breach_tools),
        Choice("grenade", map_grenades),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "tool": "open",
        "grenade": "none",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        tool = extras["tool"]
        grenade = extras["grenade"]

        print(f"{color} team {hold} {tool} the door {grenade} breach and clear")
        cmd_breach_and_clear(color, hold, tool, grenade)


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
    spec1 = "[<color>] [team] [<hold>] stack up [on] [the] [door] [use] [the] [<tool>] [(the door | it)]"
    spec2 = "[<color>] [team] [<hold>] [use] <tool> [((on | the) door | it)]"
    spec = f"(({spec1}) | ({spec2}))"
    extras = [
        Choice("color", map_colors),
        Choice("hold", map_hold),
        Choice("tool", map_stack_tools),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "tool": "stack",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        tool = extras["tool"]

        print(f"{color} team {hold} stack up {tool}")


class YellFreeze(BasicRule):
    element = Alternative((
        Literal("freeze"),
        Literal("hands"),
        Literal("drop"),
        Literal("police"),
    ))

    def _process_recognition(self, node, extras):
        cmd_yell().execute()

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