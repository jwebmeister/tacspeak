#
# This file is part of Tacspeak.
# (c) Copyright 2023 by Joshua Webb
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

import sys
import dragonfly
from dragonfly import (BasicRule, CompoundRule, MappingRule, RuleRef, Repetition, RecognitionObserver,
                       Function, Choice, IntegerRef, Grammar, Alternative, Literal, Text,
                       AppContext)
from dragonfly.engines.backend_kaldi.dictation import UserDictation as Dictation
from dragonfly.actions import (Key, Mouse)

from kaldi_active_grammar import KaldiRule

# ---------------------------------------------------------------------------
# Check DEBUG_MODE (from user_settings)

try:
    DEBUG_MODE = (sys.modules["user_settings"]).DEBUG_MODE
except NameError:
    DEBUG_MODE = False

# DEBUG_MODE = True # if you want to override

# ---------------------------------------------------------------------------
# Create this module's grammar and the context under which it'll be active.
if DEBUG_MODE:
    grammar_context = AppContext()
else:
    grammar_context = AppContext(executable="ReadyOrNot")
grammar = Grammar("ReadyOrNot",
                  context=grammar_context,
                  )
grammar_priority = Grammar("ReadyOrNot_priority",
                           context=grammar_context,
                           )

# ---------------------------------------------------------------------------
# Variables used by grammar, rules, recognition observers below
# Users should be able to look here first for customisation

# Will map keybindings to print()
DEBUG_NOCMD_PRINT_ONLY = DEBUG_MODE

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

# print key bindings
print("-- Ready or Not keybindings --")
for (k, v) in map_ingame_key_bindings.items():
    print(f'{k}:{v}')
print("-- Ready or Not keybindings --")

# mappings of spoken phrases to values
map_colors = {
    "current": "current",
    "gold": "gold",
    "blue": "blue",
    "red": "red",
}
map_breach_tools = {
    "open": "open",
    "move [in]": "open",
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
map_deployables = {
    "(bang | flashbang | flash)": "flashbang",
    "stinger": "stinger",
    "(cs | gas | cs gas)": "gas",
    "chem light": "chemlight",
    "shield": "shield",
}
map_execute_or_cancels = {
    "execute": "execute", 
    "cancel": "cancel", 
    "go [go] [go]": "execute",
    "belay": "cancel", 
}
map_npc_team_interacts = {
    "restrain [(them | him | her | target)]": "restrain",
    "zip [(them | him | her | target) [up]]": "restrain",
    "cuff [(them | him | her | target)]": "restrain",
    "arrest [(them | him | her | target)]": "restrain",
    "tie [(them | him | her | target) [up]]": "restrain",
}

# WIP - 1.0 mappings
map_stack_splits = {
    "split": "split",
    "left": "left",
    "right": "right",
}
map_formations = {
    "single file": "single",
    "double file": "double",
    "diamond": "diamond",
    "wedge": "wedge",
}
map_npc_player_interacts = {
    "(move | come) (here | forward)": "move here",
    "(move | come) [to] my position": "move my position",
    "stop [there]": "move stop",
    "turn around [and stay still]": "turn around",
    "move to [the] exit": "move to exit",
}
map_npc_deployables = {
    "(bang | flashbang | flash)": "flashbang",
    "stinger": "stinger",
    "(cs | gas | cs gas)": "gas",
    "(fourtymil | launcher)": "launcher",
    "[pepper] spray": "spray",
    "taser": "taser",
}
# map_npc_team_interacts.update({f"(deploy | use) [the] {k}": v for k, v in map_deployables.items()}) # don't use this will conflict with cmd not looking at target
# map_npc_team_interacts.update({f"(deploy | use) [the] {k}": v for k, v in map_npc_deployables.items()}) # WIP - for 1.0

# ---------------------------------------------------------------------------
# Rules which will be added to our grammar

# used to chain actions together, e.g. (NULL_ACTION + Key(...) + Mouse(...)).execute()
NULL_ACTION = Function(lambda: print("NULL_ACTION")
                       if DEBUG_NOCMD_PRINT_ONLY else None)

def action_hold(direction):
    """
    press "down" or release "up" the hold command key (on execution)
    - direction="up"|"down"
    """
    if DEBUG_NOCMD_PRINT_ONLY:
        device = 'm' if 'mouse_' in ingame_key_bindings["cmd_hold"] else 'kb'
        return Function(debug_print_key, device=device, key=f'{ingame_key_bindings["cmd_hold"]}:{direction}')
    else:
        return Key(f'{ingame_key_bindings["cmd_hold"]}:{direction}')

# ------------------------------------------------------------------

def cmd_select_team(color):
    """
    Press & release select color team key (on execution), or return NULL_ACTION
    """
    if color != "current":
        return map_ingame_key_bindings[color]
    else:
        return NULL_ACTION

class SelectTeam(CompoundRule):
    """
    Speech recognise select color team
    """
    spec = "[<color>] team"
    extras = [Choice("color", map_colors)]
    defaults = {"color": "current"}

    def _process_recognition(self, node, extras):
        color = extras["color"]
        print(f"{color}")
        cmd_select_team(color).execute()

class SelectColor(CompoundRule):
    """
    Speech recognise select color team
    """
    spec = "<color>"
    extras = [Choice("color", ["blue", "red", "gold"])]

    def _process_recognition(self, node, extras):
        color = extras["color"]
        print(f"{color}")
        cmd_select_team(color).execute()

# ------------------------------------------------------------------

def cmd_team_move_there(color, hold):
    """
    Press & release command keys for the team to move to location
    - assumes player is not looking at person or door
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    # todo! check if hold command is possible?
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    actions += map_ingame_key_bindings["cmd_1"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class TeamMoveThere(CompoundRule):
    """
    Speech recognise team move there
    """
    spec = "[<color>] [team] [<hold>] move (there | to my front | forward)"
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
        print(f"{color} team {hold} move there")
        cmd_team_move_there(color, hold).execute()

# ------------------------------------------------------------------

def cmd_pick_lock(color, hold):
    """
    Press & release command keys for the team to move to location
    - assumes player is looking at door
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    # todo! check if hold command is possible?
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    actions += map_ingame_key_bindings["cmd_2"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class PickLock(CompoundRule):
    """
    Speech recognise team pick the lock
    """
    spec = "[<color>] [team] [<hold>] pick ([the] door | [the] lock | it)"
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
        print(f"{color} team {hold} pick the lock")
        cmd_pick_lock(color, hold).execute()

# ------------------------------------------------------------------

def cmd_use_deployable(color, hold, deployable):
    """
    Press & release command keys for the team to use deployable (on execution) 
    - assumes player is not looking at person or door
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    actions += map_ingame_key_bindings["cmd_4"]
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    match deployable:
        case "flashbang":
            actions += map_ingame_key_bindings["cmd_1"]
        case "stinger":
            actions += map_ingame_key_bindings["cmd_2"]
        case "gas":
            actions += map_ingame_key_bindings["cmd_3"]
        case "chemlight":
            actions += map_ingame_key_bindings["cmd_4"]
        case "shield":
            actions += map_ingame_key_bindings["cmd_5"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class UseDeployable(CompoundRule):
    """
    Speech recognise command team to interact with NPC target
    """
    spec = "[<color>] [team] [<hold>] (use | deploy) <deployable>"
    extras = [
        Choice("color", map_colors),
        Choice("hold", map_hold),
        Choice("deployable", map_deployables),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "deployable": "flashbang",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        deployable = extras["deployable"]
        print(f"{color} team {hold} deploy {deployable}")
        cmd_use_deployable(color, hold, deployable).execute()

# ------------------------------------------------------------------

# WIP - speculative for 1.0
def cmd_npc_player_interact(hold, interaction):
    """
    Press & release command keys for player to interact with target (on execution) 
    - assumes player is looking at person
    """
    actions = map_ingame_key_bindings["cmd_menu"]
    # todo! check if hold command is possible in 1.0?
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    match interaction:
        case "move here":
            actions += map_ingame_key_bindings["cmd_2"]
            actions += map_ingame_key_bindings["cmd_1"]
        case "move my position":
            actions += map_ingame_key_bindings["cmd_2"]
            actions += map_ingame_key_bindings["cmd_2"]
        case "move stop":
            actions += map_ingame_key_bindings["cmd_2"]
            actions += map_ingame_key_bindings["cmd_3"]
        case "turn around":
            actions += map_ingame_key_bindings["cmd_4"]
        case "move to exit":
            actions += map_ingame_key_bindings["cmd_5"]
    # todo! check if hold command is possible in 1.0?
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

# todo! class NpcPlayerInteract

# ------------------------------------------------------------------

def cmd_npc_team_interact(color, hold, interaction):
    """
    Press & release command keys for the team to interact with target (on execution) 
    - assumes player is looking at person
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    match interaction:
        case "restrain":
            actions += map_ingame_key_bindings["cmd_1"]
        # todo! update deployables for 1.0
        case "deploy flashbang":
            actions += map_ingame_key_bindings["cmd_5"]
            actions += map_ingame_key_bindings["cmd_1"]
        case "deploy stinger":
            actions += map_ingame_key_bindings["cmd_5"]
            actions += map_ingame_key_bindings["cmd_2"]
        case "deploy gas":
            actions += map_ingame_key_bindings["cmd_5"]
            actions += map_ingame_key_bindings["cmd_3"]
        case "deploy chemlight":
            actions += map_ingame_key_bindings["cmd_5"]
            actions += map_ingame_key_bindings["cmd_4"]
        case "deploy shield":
            actions += map_ingame_key_bindings["cmd_5"]
            actions += map_ingame_key_bindings["cmd_5"]
        case "deploy launcher":
            # todo! update for 1.0
            print(f"todo: {interaction}")
        case "deploy spray":
            # todo! update for 1.0
            print(f"todo: {interaction}")
        case "deploy taser":
            # todo! update for 1.0
            print(f"todo: {interaction}")
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class NpcTeamInteract(CompoundRule):
    """
    Speech recognise command team to interact with NPC target
    """
    spec = "[<color>] [team] [<hold>] <interaction>"
    extras = [
        Choice("color", map_colors),
        Choice("hold", map_hold),
        Choice("interaction", map_npc_team_interacts),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "interaction": "restrain",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        interaction = extras["interaction"]
        print(f"{color} team {hold} {interaction} target")
        cmd_npc_team_interact(color, hold, interaction).execute()

# ------------------------------------------------------------------

def cmd_execute_or_cancel_held_order(color, execute_or_cancel):
    """
    Press & release command keys for team to execute held order
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    match execute_or_cancel:
        case "execute":
            actions += map_ingame_key_bindings["cmd_1"]
        case "cancel":
            actions += map_ingame_key_bindings["cmd_2"]
    return actions

class ExecuteOrCancelHeldOrder(CompoundRule):
    """
    Speech recognise team execute or cancel a held order
    """
    spec = "[<color>] [team] <execute_or_cancel> [([that] [held] order | that [order])]"
    extras = [
        Choice("color", map_colors),
        Choice("execute_or_cancel", map_execute_or_cancels),
    ]
    defaults = {
        "color": "current",
        "execute_or_cancel": "execute",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        execute_or_cancel = extras["execute_or_cancel"]
        print(f"{color} team {execute_or_cancel} held order")
        cmd_execute_or_cancel_held_order(color, execute_or_cancel).execute()

# ------------------------------------------------------------------

def cmd_fall_in(color, hold, formation):
    """
    Press & release command keys for team to fall in (on execution) 
    - assumes player is not looking at person or door
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    actions += map_ingame_key_bindings["cmd_2"]

    # todo! add formations for 1.0

    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class FallIn(CompoundRule):
    """
    Speech recognise team fall in
    """
    spec = "[<color>] [team] [<hold>] (fall in | regroup | form [up] | on me) [<formation>]"
    extras = [
        Choice("color", map_colors),
        Choice("hold", map_hold),
        Choice("formation", map_formations),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "formation": "single",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        formation = extras["formation"]
        print(f"{color} team {hold} fall in {formation}")
        cmd_fall_in(color, hold, formation).execute()

# ------------------------------------------------------------------

def cmd_open_or_close_door(color, hold, open_or_close):
    """
    Press & release command keys for team to open or close door (on execution)
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    match open_or_close:
        case "open":
            actions += map_ingame_key_bindings["cmd_4"]
        case "close":
            actions += map_ingame_key_bindings["cmd_3"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class OpenOrCloseDoor(CompoundRule):
    """
    Speech recognise team open (or close) door
    """
    spec = "[<color>] [team] [<hold>] <open_or_close> [the] door"
    extras = [
        Choice("color", map_colors),
        Choice("hold", map_hold),
        Choice("open_or_close", ["open", "close"]),
    ]
    defaults = {
        "color": "current",
        "hold": "go",
        "open_or_close": "open",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
        hold = extras["hold"]
        open_or_close = extras["open_or_close"]
        print(f"{color} team {hold} {open_or_close} the door")
        cmd_open_or_close_door(color, hold, open_or_close).execute()

# ------------------------------------------------------------------

def cmd_stack_up(color, hold, tool):
    """
    Press & release command keys for team to stack up and/or use tool (on execution)
    """
    actions = cmd_select_team(color)
    actions += map_ingame_key_bindings["cmd_menu"]
    actions += map_ingame_key_bindings["cmd_1"]

    # todo! add split for 1.0

    # start hold for command
    if hold == "hold":
        actions += action_hold("down")
    match tool:
        case "stack":
            actions += map_ingame_key_bindings["cmd_1"]
        case "mirror":
            actions += map_ingame_key_bindings["cmd_2"]
        case "disarm":
            actions += map_ingame_key_bindings["cmd_3"]
        case "wedge":
            actions += map_ingame_key_bindings["cmd_4"]
    # end hold for command
    if hold == "hold":
        actions += action_hold("up")
    return actions

class StackUp(CompoundRule):
    """
    Speech recognise team stack up on door
    """
    # todo! update with split stack for 1.0
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
        cmd_stack_up(color, hold, tool).execute()

# ------------------------------------------------------------------

def cmd_breach_and_clear(color, hold, tool, grenade):
    """
    Press & release command keys for team to breach & clear (on execution)
    """
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
    return actions

class BreachAndClear(CompoundRule):
    """
    Speech recognise team breach and clear
    """
    spec1 = "[<color>] [team] [<hold>] [<tool>] [the door] [you] [[(throw | deploy | use)] <grenade>] [and] (breach (and clear | it) | clear) [it]"
    spec2 = "[<color>] [team] [<hold>] [<tool>] [the door] [you] [and] (breach (and clear | it) | clear) [it] [with] <grenade> [grenade]"
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
        cmd_breach_and_clear(color, hold, tool, grenade).execute()

# ------------------------------------------------------------------

def cmd_yell():
    """
    Press & release yell key (on execution)
    """
    return map_ingame_key_bindings["yell"]

class YellFreeze(BasicRule):
    """
    Speech recognise yell at NPC
    """
    element = Alternative((
        Literal("freeze"),
        Literal("hands"),
        Literal("drop"),
        Literal("police"),
    ))

    def _process_recognition(self, node, extras):
        print("Freeze!")
        cmd_yell().execute()

# ---------------------------------------------------------------------------
# Recognition Observer - for mid-utterance recognition

class FreezeRecob(RecognitionObserver):
    """
    Observer of partial recognition of yell commands
    """
    def __init__(self):
        RecognitionObserver.__init__(self)
        self.words = None
        self.frozen = False

    def on_begin(self):
        self.frozen = False

    def on_partial_recognition(self, words, rule):
        self.words = words
        if (not self.frozen) and isinstance(rule, KaldiRule) and rule.name == "ReadyOrNot_priority::YellFreeze":
            print("Freeze!")
            cmd_yell().execute()
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

# ---------------------------------------------------------------------------
# Add rules to grammar and create RecognitionObserver instances

grammar.add_rule(SelectTeam())
grammar.add_rule(SelectColor())
grammar.add_rule(BreachAndClear())
grammar.add_rule(OpenOrCloseDoor())
grammar.add_rule(StackUp())
grammar.add_rule(NpcTeamInteract())
grammar.add_rule(UseDeployable())
grammar.add_rule(FallIn())
grammar.add_rule(ExecuteOrCancelHeldOrder())
grammar.add_rule(TeamMoveThere())
grammar.add_rule(PickLock())
grammar_priority.add_rule(YellFreeze())

freeze_recob = FreezeRecob()

# ---------------------------------------------------------------------------
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
    if grammar:
        grammar.unload()
    grammar = None
    if grammar_priority:
        grammar_priority.unload()
    grammar_priority = None
    freeze_recob.unregister()
    freeze_recob = None
