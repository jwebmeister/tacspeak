#!/usr/bin/env python3

import argparse, math, multiprocessing, os, sys, wave

from kaldi_active_grammar import PlainDictationRecognizer

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

def er_margin_of_error(error, n, z=1.96):
    error = max(0, min(error, 100))
    if n == 0: return float('nan')
    error = float(error * 0.01)
    moe = z * math.sqrt(error * (1 - error) / n)
    return moe * 100

def initialize_kaldi(model_dir):
    global call_recognizer
    recognizer = PlainDictationRecognizer(model_dir=model_dir)
    def decode(data):
        output_str, info = recognizer.decode_utterance(data)
        return output_str
    call_recognizer = decode

def recognize(wav_path, text):
    global call_recognizer
    with wave.open(wav_path, 'rb') as wav_file:
        data = wav_file.readframes(wav_file.getnframes())
    output_str = call_recognizer(data)
    print(f"Ref: {text}")
    print(f"Hyp: {output_str}")
    return output_str, text

def main():
    parser = argparse.ArgumentParser(description='Run evaluation test of kaldi_active_grammar model.')
    parser.add_argument('filename', help='Dataset TSV file to test with.')
    parser.add_argument('model_dir', nargs='?', default='exported_model', help='Model directory.')
    parser.add_argument('-l', '--lexicon_file', help='Filename of the lexicon file, for filtering out out-of-vocabulary utterances.')
    parser.add_argument('-p', '--parallel', help='Number of parallel processes to use.', type=int, default=None)
    args = parser.parse_args()

    initialize = initialize_kaldi

    lexicon = set()
    if args.lexicon_file:
        with open(args.lexicon_file, 'r') as f:
            for line in f:
                word = line.strip().split(None, 1)[0]
                lexicon.add(word)

    calculator = Calculator()

    # Initialize first before going parallel, in case any model rebuilding is needed, which must be performed serially.
    initialize(args.model_dir)

    with open(args.filename, 'r') as f, multiprocessing.Pool(args.parallel, initializer=initialize, initargs=(args.model_dir,)) as pool:
        submissions = []
        for line in f:
            fields = line.rstrip('\n').split('\t')
            text = fields[4]
            wav_path = fields[0]
            if not os.path.exists(wav_path):
                print(f"{wav_path} does not exist")
                continue
            if args.lexicon_file and any(word not in lexicon for word in text.split()):
                print(f"{wav_path} is out of vocabulary: {text}")
                continue
            submissions.append((wav_path, text,))
        for output_str, text in pool.starmap(recognize, submissions, chunksize=1):
            calculator.calculate(text.strip().split(), output_str.strip().split())

    result = calculator.overall()
    if result['all'] != 0 :
        wer = float(result['ins'] + result['sub'] + result['del']) * 100.0 / result['all']
    else :
        wer = 0.0
    print('Overall -> %4.2f %%' % wer, end = ' ')
    print('+/- %4.2f %%' % er_margin_of_error(wer, n=result['all']), end = ' ')
    print('N=%d C=%d S=%d D=%d I=%d' % (result['all'], result['cor'], result['sub'], result['del'], result['ins']))

if __name__ == '__main__':
    main()
