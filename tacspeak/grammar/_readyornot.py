#
# This file is part of tacspeak.
# (c) Copyright 2023 by Joshua Webb
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

import dragonfly
from dragonfly import (BasicRule, CompoundRule, MappingRule, RuleRef, Repetition, RecognitionObserver,
                       Function, Choice, IntegerRef, Grammar, Alternative, Literal, Text,
                       AppContext)
from dragonfly.engines.backend_kaldi.dictation import UserDictation as Dictation

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

colors = {
    "current": "current",
    "gold": "gold",
    "blue": "blue",
    "red": "red",
}
tools = {
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
    "open": "open",
}
grenades = {
    "bang": "flashbang",
    "flashbang": "flashbang",
    "cs": "gas",
    "gas": "gas",
    "stinger": "stinger",
    "none": "none"
}
launcher_grenades = grenades


class SelectTeam(CompoundRule):
    spec = "[<color>] team"
    extras = [Choice("color", ["current", "blue", "red", "gold"])]
    defaults = {"color": "current"}

    def _process_recognition(self, node, extras):
        color = extras["color"]
        print("%s team" % color)


class SelectColor(CompoundRule):
    spec = "<color>"
    extras = [Choice("color", ["blue", "red", "gold"])]

    def _process_recognition(self, node, extras):
        color = extras["color"]
        print("%s team" % color)


class BreachAndClear(CompoundRule):
    spec = "[<color>] [team] [<tool>] [the door] [(throw | deploy)] [(<grenade> | fourtymil <launcher> | launch <launcher> | launcher <launcher>)] [and] (breach and clear | clear) [it]"
    extras = [
        Choice("color", colors),
        Choice("tool", tools),
        Choice("grenade", grenades),
        Choice("launcher", launcher_grenades),
    ]
    defaults = {
        "color": "current",
        "tool": "open",
        "grenade": "none",
        "launcher": "none",
    }

    def _process_recognition(self, node, extras):
        color = extras["color"]
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
        print("{0} team {1} the door{2} breach and clear".format(
            color, tool, fmt_deployed_nade))


class YellFreeze(BasicRule):
    element = Alternative((
        Literal("freeze"),
        Literal("hands"),
        Literal("drop"),
    ))

    def _process_recognition(self, node, extras):
        print("{0}".format(self.value(node)))

#---------------------------------------------------------------------------
# Recognition Observer - for mid-utterance recognition

class FreezeRecob(RecognitionObserver):

    def __init__(self):
        RecognitionObserver.__init__(self)
        self.waiting = False
        self.words = None
        self.frozen = False

    def on_begin(self):
        self.waiting = True

    def on_partial_recognition(self, words, rule):
        self.words = words
        if (not self.frozen) and isinstance(rule, kaldi_active_grammar.KaldiRule) and rule.name == "ReadyOrNot_priority::YellFreeze":
            print("Freeze dirtbag!")
            self.frozen = True
        # print("rule_type={0}".format(type(rule)))
        # print("rule={0}".format(rule))

    def on_recognition(self, words, results):
        self.waiting = False
        self.words = words
        # print("words={0}".format(words))
        # print("rule={0}".format(rule))
        # print("node={0}".format(node))
        # print("results={0}".format(results))

    def on_failure(self, results):
        self.waiting = False
        self.words = False
    
    def on_end(self, results):
        self.waiting = False
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