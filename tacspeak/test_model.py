#
# This file is part of Tacspeak.
# (c) Copyright 2024 by Joshua Webb
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

from __future__ import print_function

import logging
import os.path
import sys
import time
import math
import multiprocessing
import wave

from dragonfly import get_engine
from dragonfly.loader import CommandModuleDirectory, CommandModule
from dragonfly.log import default_levels
from dragonfly.engines.backend_kaldi.audio import WavAudio

from dragonfly.grammar.rule_compound import CompoundRule

from kaldi_active_grammar import disable_donation_message, PlainDictationRecognizer


# --------------------------------------------------------------------------
# Functions

# Adapted from daanzu/kaldi_ag_training, licensed under the AGPL-3.0
# From wenet-e2e/wenet, licensed under the Apache License 2.0
class Calculator:
    def __init__(self) :
        self.data = {}
        self.space = []
        self.cost = {}
        self.cost['cor'] = 0
        self.cost['sub'] = 1
        self.cost['del'] = 1
        self.cost['ins'] = 1
    def calculate(self, lab, rec) :
        # Initialization
        lab.insert(0, '')
        rec.insert(0, '')
        while len(self.space) < len(lab) :
            self.space.append([])
        for row in self.space :
            for element in row :
                element['dist'] = 0
                element['error'] = 'non'
            while len(row) < len(rec) :
                row.append({'dist' : 0, 'error' : 'non'})
        for i in range(len(lab)) :
            self.space[i][0]['dist'] = i
            self.space[i][0]['error'] = 'del'
        for j in range(len(rec)) :
            self.space[0][j]['dist'] = j
            self.space[0][j]['error'] = 'ins'
        self.space[0][0]['error'] = 'non'
        for token in lab :
            if token not in self.data and len(token) > 0 :
                self.data[token] = {'all' : 0, 'cor' : 0, 'sub' : 0, 'ins' : 0, 'del' : 0}
        for token in rec :
            if token not in self.data and len(token) > 0 :
                self.data[token] = {'all' : 0, 'cor' : 0, 'sub' : 0, 'ins' : 0, 'del' : 0}
        # Computing edit distance
        for i, lab_token in enumerate(lab) :
            for j, rec_token in enumerate(rec) :
                if i == 0 or j == 0 :
                    continue
                min_dist = sys.maxsize
                min_error = 'none'
                dist = self.space[i-1][j]['dist'] + self.cost['del']
                error = 'del'
                if dist < min_dist :
                    min_dist = dist
                    min_error = error
                dist = self.space[i][j-1]['dist'] + self.cost['ins']
                error = 'ins'
                if dist < min_dist :
                    min_dist = dist
                    min_error = error
                if lab_token == rec_token :
                    dist = self.space[i-1][j-1]['dist'] + self.cost['cor']
                    error = 'cor'
                else :
                    dist = self.space[i-1][j-1]['dist'] + self.cost['sub']
                    error = 'sub'
                if dist < min_dist :
                    min_dist = dist
                    min_error = error
                self.space[i][j]['dist'] = min_dist
                self.space[i][j]['error'] = min_error
        # Tracing back
        result = {'lab':[], 'rec':[], 'all':0, 'cor':0, 'sub':0, 'ins':0, 'del':0}
        i = len(lab) - 1
        j = len(rec) - 1
        while True :
            if self.space[i][j]['error'] == 'cor' : # correct
                if len(lab[i]) > 0 :
                    self.data[lab[i]]['all'] = self.data[lab[i]]['all'] + 1
                    self.data[lab[i]]['cor'] = self.data[lab[i]]['cor'] + 1
                    result['all'] = result['all'] + 1
                    result['cor'] = result['cor'] + 1
                result['lab'].insert(0, lab[i])
                result['rec'].insert(0, rec[j])
                i = i - 1
                j = j - 1
            elif self.space[i][j]['error'] == 'sub' : # substitution
                if len(lab[i]) > 0 :
                    self.data[lab[i]]['all'] = self.data[lab[i]]['all'] + 1
                    self.data[lab[i]]['sub'] = self.data[lab[i]]['sub'] + 1
                    result['all'] = result['all'] + 1
                    result['sub'] = result['sub'] + 1
                result['lab'].insert(0, lab[i])
                result['rec'].insert(0, rec[j])
                i = i - 1
                j = j - 1
            elif self.space[i][j]['error'] == 'del' : # deletion
                if len(lab[i]) > 0 :
                    self.data[lab[i]]['all'] = self.data[lab[i]]['all'] + 1
                    self.data[lab[i]]['del'] = self.data[lab[i]]['del'] + 1
                    result['all'] = result['all'] + 1
                    result['del'] = result['del'] + 1
                result['lab'].insert(0, lab[i])
                result['rec'].insert(0, "")
                i = i - 1
            elif self.space[i][j]['error'] == 'ins' : # insertion
                if len(rec[j]) > 0 :
                    self.data[rec[j]]['ins'] = self.data[rec[j]]['ins'] + 1
                    result['ins'] = result['ins'] + 1
                result['lab'].insert(0, "")
                result['rec'].insert(0, rec[j])
                j = j - 1
            elif self.space[i][j]['error'] == 'non' : # starting point
                break
            else : # shouldn't reach here
                print('this should not happen , i = {i} , j = {j} , error = {error}'.format(i = i, j = j, error = self.space[i][j]['error']))
        return result
    def overall(self) :
        result = {'all':0, 'cor':0, 'sub':0, 'ins':0, 'del':0}
        for token in self.data :
            result['all'] = result['all'] + self.data[token]['all']
            result['cor'] = result['cor'] + self.data[token]['cor']
            result['sub'] = result['sub'] + self.data[token]['sub']
            result['ins'] = result['ins'] + self.data[token]['ins']
            result['del'] = result['del'] + self.data[token]['del']
        return result
    def overall_string(self):
        out_string = ''
        result = self.overall()
        if result['all'] != 0 :
            wer = float(result['ins'] + result['sub'] + result['del']) * 100.0 / result['all']
        else :
            wer = 0.0
        out_string += str('Overall -> %4.2f %%' % wer)
        out_string += str('+/- %4.2f %%' % er_margin_of_error(wer, n=result['all']))
        out_string += str('N=%d C=%d S=%d D=%d I=%d' % (result['all'], result['cor'], result['sub'], result['del'], result['ins']))
        return out_string

    def cluster(self, data) :
        result = {'all':0, 'cor':0, 'sub':0, 'ins':0, 'del':0}
        for token in data :
            if token in self.data :
                result['all'] = result['all'] + self.data[token]['all']
                result['cor'] = result['cor'] + self.data[token]['cor']
                result['sub'] = result['sub'] + self.data[token]['sub']
                result['ins'] = result['ins'] + self.data[token]['ins']
                result['del'] = result['del'] + self.data[token]['del']
        return result
    def keys(self) :
        return list(self.data.keys())
    def ranked_worst_to_best_list(self) :
        ranked_worst_tokens = []
        for key, value in self.data.items():
            token = key
            n_errors = value['sub'] + value['del'] + value['ins']
            n_correct = value['cor']
            n_all = value['all']
            rate_errors = float(n_errors) / float(max(1, n_all))
            entry = {'token':token, 'rate_errors':rate_errors, 'n_errors':n_errors, 
                     'n_correct':n_correct, 'n_all':n_all}
            ranked_worst_tokens.append(entry)
        ranked_worst_tokens.sort(key=lambda x: x['rate_errors'], reverse=True)
        return ranked_worst_tokens


def er_margin_of_error(error, n, z=1.96):
    error = max(0, min(error, 100))
    if n == 0: return float('nan')
    error = float(error * 0.01)
    moe = z * math.sqrt(error * (1 - error) / n)
    return moe * 100

def initialize_kaldi(model_dir):
    disable_donation_message()
    user_settings_path = os.path.join(os.getcwd(), os.path.relpath("tacspeak/user_settings.py"))
    user_settings = CommandModule(user_settings_path)
    user_settings.load()
    try:
        (sys.modules["user_settings"]).DEBUG_MODE = True
        DEBUG_MODE = (sys.modules["user_settings"]).DEBUG_MODE
    except Exception:
        print("Failed to load `tacspeak/user_settings.py` DEBUG_MODE. Using default settings as fallback.")
        DEBUG_MODE = True
    try:
        (sys.modules["user_settings"]).DEBUG_HEAVY_DUMP_GRAMMAR = False
        DEBUG_HEAVY_DUMP_GRAMMAR = (sys.modules["user_settings"]).DEBUG_HEAVY_DUMP_GRAMMAR
    except Exception:
        print("Failed to load `tacspeak/user_settings.py` DEBUG_HEAVY_DUMP_GRAMMAR. Using default settings as fallback.")
        DEBUG_HEAVY_DUMP_GRAMMAR = False
    try:
        (sys.modules["user_settings"]).KALDI_ENGINE_SETTINGS["model_dir"] = model_dir
        (sys.modules["user_settings"]).KALDI_ENGINE_SETTINGS["listen_key"] = None
        (sys.modules["user_settings"]).KALDI_ENGINE_SETTINGS["listen_key_toggle"] = 0
        (sys.modules["user_settings"]).KALDI_ENGINE_SETTINGS["retain_dir"] = None
        (sys.modules["user_settings"]).KALDI_ENGINE_SETTINGS["retain_audio"] = False
        (sys.modules["user_settings"]).KALDI_ENGINE_SETTINGS["retain_metadata"] = False
        (sys.modules["user_settings"]).KALDI_ENGINE_SETTINGS["listen_key_padding_end_ms_min"] = 0
        (sys.modules["user_settings"]).KALDI_ENGINE_SETTINGS["listen_key_padding_end_ms_max"] = 0
        (sys.modules["user_settings"]).KALDI_ENGINE_SETTINGS["listen_key_padding_end_always_max"] = False
        KALDI_ENGINE_SETTINGS = (sys.modules["user_settings"]).KALDI_ENGINE_SETTINGS
    except Exception:
        print("Failed to load `tacspeak/user_settings.py` KALDI_ENGINE_SETTINGS. Using default settings as fallback.")
        KALDI_ENGINE_SETTINGS = {
            "listen_key":None, # 0x10=SHIFT key, 0x05=X1 mouse button, 0x06=X2 mouse button, see https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
            "listen_key_toggle":0, # 0 for toggle mode off; 1 for toggle mode on; 2 for global toggle on (use VAD); -1 for toggle mode off but allow priority grammar even when key not pressed
            "vad_padding_end_ms":250, # ms of required silence after VAD
            "auto_add_to_user_lexicon":False, # this requires g2p_en (which isn't installed by default)
            "allow_online_pronunciations":False,
        }
    

    def log_handlers():
        log_file_path = os.path.join(os.getcwd(), ".tacspeak.log")
        log_file_handler = logging.FileHandler(log_file_path)
        log_file_formatter = logging.Formatter("%(asctime)s %(name)s (%(levelname)s): %(message)s")
        log_file_handler.setFormatter(log_file_formatter)

        log_stream_handler = logging.StreamHandler()
        log_stream_formatter = logging.Formatter("%(name)s (%(levelname)s): %(message)s")
        log_stream_handler.setFormatter(log_stream_formatter)
        return [log_stream_handler, log_file_handler]
    
    def setup_loggers(use_default_levels=True):
        for name, levels in default_levels.items():
            stderr_level, file_level = levels
            handlers = log_handlers()
            if use_default_levels:
                handlers[0].setLevel(stderr_level)
                handlers[1].setLevel(file_level)
            logger = logging.getLogger(name)
            logger.addHandler(handlers[0])
            logger.addHandler(handlers[1])
            logger.setLevel(min(stderr_level, file_level))
            logger.propagate = False
            logger.setLevel(20)
    
    setup_loggers()

    # Set any configuration options here as keyword arguments.
    # See Kaldi engine documentation for all available options and more info.
    engine = get_engine('kaldi',**KALDI_ENGINE_SETTINGS)

    # Call connect() now that the engine configuration is set.
    engine.connect()

    # Load grammars.
    grammar_path = os.path.join(os.getcwd(), os.path.relpath("tacspeak/grammar/"))
    directory = CommandModuleDirectory(grammar_path)
    directory.load()

    handlers = log_handlers()
    log_recognition = logging.getLogger('on_recognition')
    log_recognition.addHandler(handlers[0])
    log_recognition.addHandler(handlers[1])
    log_recognition.setLevel(20)

    # Start the engine's main recognition loop
    engine.prepare_for_recognition()
    return engine

def recognize(wav_path, text):
    engine = get_engine('kaldi')

    testmodel_recog_buffer = None
    testmodel_busy = False

    # Define recognition callback functions.
    def on_begin():
        nonlocal testmodel_recog_buffer
        nonlocal testmodel_busy
        testmodel_recog_buffer = None
        testmodel_busy = True

    def on_recognition(words, results, rule, node):
        nonlocal testmodel_recog_buffer
        # message = f"{results.kaldi_rule} | {' '.join(words)}"
        # log_recognition = logging.getLogger('on_recognition')
        # log_recognition.log(20, message)
        testmodel_recog_buffer = (' '.join(words), results, rule, node)

    def on_failure():
        pass

    def on_end():
        nonlocal testmodel_busy
        testmodel_busy = False

    engine.do_recognition(on_begin, on_recognition, on_failure, on_end, audio_iter=WavAudio.read_file(wav_path, realtime=False))
    
    n_sleeps = 0
    while testmodel_recog_buffer is None and n_sleeps < 30:
        n_sleeps += 1
        time.sleep(0.1)
    output_str = ""
    output_extras = None
    output_options = None
    output_rule = None
    if testmodel_recog_buffer:
        output_str = testmodel_recog_buffer[0]
        rule = testmodel_recog_buffer[2]
        output_rule = rule
        node = testmodel_recog_buffer[3]
        if isinstance(rule, CompoundRule):
            extras = {
                "_grammar":  rule.grammar,
                "_rule":     rule,
                "_node":     node,
            }
            extras.update(rule._defaults)
            for name, element in rule._extras.items():
                extra_node = node.get_child_by_name(name, shallow=True)
                if extra_node:
                    extras[name] = extra_node.value()
                elif element.has_default():
                    extras[name] = element.default
            output_extras = extras
            output_options = {k:v for k,v in output_extras.items() if k not in ['_grammar','_rule','_node']}
    else:
        output_str = ""

    testmodel_recog_buffer = None
    testmodel_busy = False

    # becaused we called do_recognition with on_recognition callbacks, 
    # it should still be registered in engine and we don't have to do anything for mimic
    try:
        engine.mimic(text)
    except Exception:
        pass
    
    n_sleeps = 0
    while testmodel_recog_buffer is None and n_sleeps < 30:
        n_sleeps += 1
        time.sleep(0.1)
    input_str = ""
    input_extras = None
    input_options = None
    input_rule = None
    if testmodel_recog_buffer:
        input_str = testmodel_recog_buffer[0]
        rule = testmodel_recog_buffer[2]
        input_rule = rule
        node = testmodel_recog_buffer[3]
        if isinstance(rule, CompoundRule):
            extras = {
                "_grammar":  rule.grammar,
                "_rule":     rule,
                "_node":     node,
            }
            extras.update(rule._defaults)
            for name, element in rule._extras.items():
                extra_node = node.get_child_by_name(name, shallow=True)
                if extra_node:
                    extras[name] = extra_node.value()
                elif element.has_default():
                    extras[name] = element.default
            input_extras = extras
            input_options = {k:v for k,v in input_extras.items() if k not in ['_grammar','_rule','_node']}
    else:
        input_str = ""

    correct_rule = 0
    if output_rule is not None and output_rule == input_rule:
        correct_rule = 1
    elif output_rule is not None and input_rule is not None and output_rule != input_rule:
        correct_rule = -1

    print(f"Ref: {text}")
    print(f"Hyp: {output_str}")
    print(f"input_extras: {input_extras}")
    print(f"output_extras: {output_extras}")

    return output_str, text, output_options, input_options, correct_rule, wav_path

# --------------------------------------------------------------------------
# Main event driving loop.

def test_model(tsv_file, model_dir, lexicon_file=None, num_threads=1):
    # from tacspeak.test_model import test_model
    # test_model("./testaudio/recorder.tsv", "./kaldi_model/")
    # python -c 'from tacspeak.test_model import test_model; test_model("./testaudio/recorder.tsv", "./kaldi_model/")'

    print("Start test_model")

    calculator = Calculator()

    lexicon = set()
    if lexicon_file:
        with open(lexicon_file, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().split(None, 1)[0]
                lexicon.add(word)

    print(f"opening {tsv_file}")
    with open(tsv_file, 'r', encoding='utf-8') as f:
        submissions = []
        for line in f:
            fields = line.rstrip('\n').split('\t')
            text = fields[4]
            wav_path = fields[0]
            if not os.path.exists(wav_path):
                print(f"{wav_path} does not exist")
                continue
            if lexicon_file and any(word not in lexicon for word in text.split()):
                print(f"{wav_path} is out of vocabulary: {text}")
                continue
            submissions.append((wav_path, text,))
        print(f"read lines: {len(submissions)}")

    
    # initialize first in-case model needs to be recompiled
    engine = initialize_kaldi(model_dir)
    engine.disconnect()

    utterances_list = []
    cmd_all_threads_overall_stats = []
    
    with multiprocessing.Pool(processes=num_threads, initializer=initialize_kaldi, initargs=(model_dir,)) as pool:
        try:
            cmd_thread_overall_stats = {'cmd_not_correct_output':0, 
                                        'cmd_not_correct_rule':0,
                                        'cmd_not_correct_options':0,
                                        'cmd_not_recog_output':0,
                                        'cmd_not_recog_input':0,
                                        'cmds':0,
                                        }
            for output_str, text, output_options, input_options, correct_rule, wav_path in pool.starmap(recognize, submissions, chunksize=1):
                result = calculator.calculate(text.strip().split(), output_str.strip().split())
                n_errors = result['sub'] + result['del'] + result['ins']
                n_correct = result['cor']
                n_all = result['all']
                rate_errors = float(n_errors) / float(max(1, n_all))

                cmd_recog_input = 1 if input_options is not None else -1
                cmd_recog_output = 1 if output_options is not None else -1

                cmd_correct_rule = correct_rule
                cmd_correct_options = 0
                cmd_correct_output = 0

                if cmd_recog_input == 1 and cmd_recog_output == 1:
                    if cmd_correct_rule == 1:
                        cmd_correct_options = 1
                        for key, value in input_options.items():
                            if output_options[key] != value:
                                cmd_correct_options = -1
                
                if correct_rule == 1:
                    cmd_recog_input = 1
                    cmd_recog_output = 1

                if cmd_correct_rule == -1 or cmd_correct_options == -1:
                    cmd_correct_output = -1
                elif cmd_correct_rule == 1 and cmd_correct_options == 1:
                    cmd_correct_output = 1

                cmd_thread_overall_stats['cmd_not_correct_output'] += 1 if cmd_correct_output == -1 else 0
                cmd_thread_overall_stats['cmd_not_correct_rule'] += 1 if cmd_correct_rule == -1 else 0
                cmd_thread_overall_stats['cmd_not_correct_options'] += 1 if cmd_correct_options == -1 else 0
                cmd_thread_overall_stats['cmd_not_recog_output'] += 1 if cmd_recog_output == -1 else 0
                cmd_thread_overall_stats['cmd_not_recog_input'] += 1 if cmd_recog_input == -1 else 0
                cmd_thread_overall_stats['cmds'] += 1

                entry = {'ref':text, 'hyp':output_str, 'wav_path':wav_path,
                         'cmd_correct_output':cmd_correct_output, 
                         'cmd_correct_rule':cmd_correct_rule,
                         'cmd_correct_options':cmd_correct_options,
                         'cmd_recog_output':cmd_recog_output,
                         'cmd_recog_input':cmd_recog_input,
                         'output_options':output_options,
                         'input_options':input_options,
                         'n_errors':n_errors, 'n_correct':n_correct, 'n_all':n_all, 'rate_errors':rate_errors
                         }
                utterances_list.append(entry)

            cmd_all_threads_overall_stats.append(cmd_thread_overall_stats)
        except KeyboardInterrupt as e:
            print(f"Closing pool: {e}")
            pool.close()
            return None

    utterances_list.sort(key=lambda x: (x['cmd_correct_output'] * 100.0) + (x['cmd_correct_rule'] * 3.0) + (x['cmd_correct_options'] * 3.0) + (x['cmd_recog_output'] * 2.0) + x['cmd_recog_input'] - x['rate_errors'], reverse=False)
    
    cmd_overall_stats = {}
    cmd_overall_stats['cmd_not_correct_output'] = 0
    cmd_overall_stats['cmd_not_correct_rule'] = 0
    cmd_overall_stats['cmd_not_correct_options'] = 0
    cmd_overall_stats['cmd_not_recog_output'] = 0
    cmd_overall_stats['cmd_not_recog_input'] = 0
    cmd_overall_stats['cmds'] = 0

    for thread_item in cmd_all_threads_overall_stats:
        cmd_overall_stats['cmd_not_correct_output'] += thread_item['cmd_not_correct_output']
        cmd_overall_stats['cmd_not_correct_rule'] += thread_item['cmd_not_correct_rule']
        cmd_overall_stats['cmd_not_correct_options'] += thread_item['cmd_not_correct_options']
        cmd_overall_stats['cmd_not_recog_output'] += thread_item['cmd_not_recog_output']
        cmd_overall_stats['cmd_not_recog_input'] += thread_item['cmd_not_recog_input']
        cmd_overall_stats['cmds'] += thread_item['cmds']
    
    with open('./test_model_output_utterances.txt', 'w', encoding='utf-8') as outfile:
        outfile.write(f"{cmd_overall_stats}\n\n")
        for item in utterances_list:
            outfile.write(  f"\n cmd_correct_output={item['cmd_correct_output']}, "
                            + f"cmd_correct_rule={item['cmd_correct_rule']}, "
                            + f"cmd_correct_options={item['cmd_correct_options']}, "
                            + f"cmd_recog_output={item['cmd_recog_output']}, "
                            + f"cmd_recog_input={item['cmd_recog_input']}"
                            + f"\n errors={item['n_errors']}, n_correct={item['n_correct']}"
                            + f", n_all={item['n_all']}, rate_errors={item['rate_errors']}"
                            + f"\n ref: {item['ref']}"
                            + f"\n hyp: {item['hyp']}"
                            + f"\n wav_path: {item['wav_path']}"
                            + f"\n input_options: {item['input_options']}"
                            + f"\n output_options: {item['output_options']}"
                            + "\n"
                            )
    
    print(f"{calculator.overall_string()}")
    print(f"Command stats -> {cmd_overall_stats}")
    
    return calculator


# ---------------------------------------------------------------------------------------------
# Dictation test_model

def initialize_kaldi_dictation(model_dir):
    global call_recognizer
    disable_donation_message()
    recognizer = PlainDictationRecognizer(model_dir=model_dir)
    def decode(data):
        output_str, info = recognizer.decode_utterance(data)
        return output_str
    call_recognizer = decode

def recognize_dictation(wav_path, text):
    global call_recognizer
    with wave.open(wav_path, 'rb') as wav_file:
        data = wav_file.readframes(wav_file.getnframes())
    output_str = call_recognizer(data)
    print(f"Ref: {text}")
    print(f"Hyp: {output_str}")
    return output_str, text, wav_path

def test_model_dictation(tsv_file, model_dir, lexicon_file=None, num_threads=1):

    print("Start test_model_dictation")

    call_recognizer = None

    calculator = Calculator()

    lexicon = set()
    if lexicon_file:
        with open(lexicon_file, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().split(None, 1)[0]
                lexicon.add(word)

    print(f"opening {tsv_file}")
    with open(tsv_file, 'r', encoding='utf-8') as f:
        submissions = []
        for line in f:
            fields = line.rstrip('\n').split('\t')
            text = fields[4]
            wav_path = fields[0]
            if not os.path.exists(wav_path):
                print(f"{wav_path} does not exist")
                continue
            if lexicon_file and any(word not in lexicon for word in text.split()):
                print(f"{wav_path} is out of vocabulary: {text}")
                continue
            submissions.append((wav_path, text,))
        print(f"read lines: {len(submissions)}")

    
    # initialize first in-case model needs to be recompiled
    initialize_kaldi_dictation(model_dir)

    utterances_list = []
    
    with multiprocessing.Pool(processes=num_threads, initializer=initialize_kaldi_dictation, initargs=(model_dir,)) as pool:
        try:
            for output_str, text, wav_path in pool.starmap(recognize_dictation, submissions, chunksize=1):
                result = calculator.calculate(text.strip().split(), output_str.strip().split())
                n_errors = result['sub'] + result['del'] + result['ins']
                n_correct = result['cor']
                n_all = result['all']
                rate_errors = float(n_errors) / float(max(1, n_all))

                entry = {'ref':text, 'hyp':output_str, 'wav_path':wav_path,
                         'n_errors':n_errors, 'n_correct':n_correct, 'n_all':n_all, 'rate_errors':rate_errors
                         }
                utterances_list.append(entry)

        except KeyboardInterrupt as e:
            print(f"Closing pool: {e}")
            pool.close()
            return None

    utterances_list.sort(key=lambda x: x['n_errors'], reverse=True)
    with open('./test_model_output_dictation.txt', 'w', encoding='utf-8') as outfile:
        for item in utterances_list:
            outfile.write(  f"\n errors={item['n_errors']}, n_correct={item['n_correct']}"
                            + f", n_all={item['n_all']}, rate_errors={item['rate_errors']}"
                            + f"\n ref: {item['ref']}"
                            + f"\n hyp: {item['hyp']}"
                            + f"\n wav_path: {item['wav_path']}"
                            + "\n"
                            )
    
    print(f"{calculator.overall_string()}")
    
    return calculator