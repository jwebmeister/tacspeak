from __future__ import print_function
import logging
import os

import dragonfly
from dragonfly import (CompoundRule, MappingRule, RuleRef, Repetition, RecognitionObserver,
                       Function, Choice, IntegerRef, Grammar, Alternative, Literal, Text)
from dragonfly.engines.backend_kaldi.dictation import UserDictation as Dictation
from dragonfly.log import setup_log

import kaldi_active_grammar

def main():

    kaldi_active_grammar.disable_donation_message()

    if False:
        logging.basicConfig(level=10)
        logging.getLogger('grammar.decode').setLevel(20)
        logging.getLogger('compound').setLevel(20)
        # logging.getLogger('kaldi').setLevel(30)
        logging.getLogger('engine').setLevel(10)
        logging.getLogger('kaldi').setLevel(10)
    else:
        # logging.basicConfig(level=20)
        setup_log()

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


    class SelectTeam(dragonfly.CompoundRule):
        spec = "[<color>] team"
        extras = [dragonfly.Choice("color", ["current", "blue", "red", "gold"])]
        defaults = {"color": "current"}

        def _process_recognition(self, node, extras):
            color = extras["color"]
            print("%s team" % color)


    class SelectColor(dragonfly.CompoundRule):
        spec = "<color>"
        extras = [dragonfly.Choice("color", ["blue", "red", "gold"])]

        def _process_recognition(self, node, extras):
            color = extras["color"]
            print("%s team" % color)


    class BreachAndClear(dragonfly.CompoundRule):
        spec = "[<color>] [team] [<tool>] [the door] [(throw | deploy)] [(<grenade> | fourtymil <launcher> | launch <launcher> | launcher <launcher>)] [and] (breach and clear | clear) [it]"
        extras = [
            dragonfly.Choice("color", colors),
            dragonfly.Choice("tool", tools),
            dragonfly.Choice("grenade", grenades),
            dragonfly.Choice("launcher", launcher_grenades),
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

    class YellFreeze(dragonfly.BasicRule):
        element = Alternative((
            Literal("freeze"),
            Literal("hands"),
            Literal("drop"),
        ))

        def _process_recognition(self, node, extras):
            print("{0}".format(self.value(node)))


    # Load engine before instantiating rules/grammars!
    # Set any configuration options here as keyword arguments.
    engine = dragonfly.get_engine("kaldi",
                                model_dir='kaldi_model',
                                # tmp_dir='kaldi_tmp',  # default for temporary directory
                                # vad_aggressiveness=3,  # default aggressiveness of VAD
                                # vad_padding_ms=300,  # default ms of required silence surrounding VAD
                                # input_device_index=None,  # set to an int to choose a non-default microphone
                                # cloud_dictation=None,  # set to 'gcloud' to use cloud dictation
                                listen_key=0x10,
                                listen_key_toggle=True,
                                auto_add_to_user_lexicon=False,
                                )
    # Call connect() now that the engine configuration is set.
    engine.connect()

    grammar = Grammar(name="mygrammar")
    grammar.add_rule(SelectTeam())
    grammar.add_rule(SelectColor())
    grammar.add_rule(BreachAndClear())
    grammar.add_rule(YellFreeze())
    grammar.load()

    # quickgrammar = QuickGrammar(name="quickgrammar")
    # quickgrammar.add_rule(SelectTeam())
    # quickgrammar.add_rule(SelectColor())
    # quickgrammar.add_rule(BreachAndClear())
    # quickgrammar.add_rule(YellFreeze())
    # quickgrammar.load()

     
    class RecognitionObserverTester(RecognitionObserver):

        def __init__(self):
            RecognitionObserver.__init__(self)
            self.waiting = False
            self.words = None
            self.frozen = False

        def on_begin(self):
            self.waiting = True

        def on_partial_recognition(self, words, rule):
            self.words = words
            if (not self.frozen) and isinstance(rule, kaldi_active_grammar.KaldiRule) and rule.name == "mygrammar::YellFreeze":
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

    test_recobs = RecognitionObserverTester()
    test_recobs.register()
    
    print("Listening...")
    engine.do_recognition()


if __name__ == "__main__":
    main()