#!/usr/bin/env python
# -*- coding: utf-8 -*-
# authors: bernd bohnet, simon mille

import codecs
import io
import os
import random
import sys
import shutil

filename = sys.argv[1]
outFolder = sys.argv[2]
track = sys.argv[3]
dType = sys.argv[4]
tmpIn = sys.argv[5]

def corpus(source, target):
	"""Reads a conll corpus and shuffle the tokens.

	Adjust the head and add the original id to to features.

	Args:
		 source: Filename for the source corpus.
		 target: Filename for the target corpus.
	"""
	sentence = []
	#with open(target, 'w') as f:
		#t_out = codecs.getwriter('utf-8')(f)
	t_out = codecs.open(target, 'w', 'utf-8')
	for line in codecs.open(source, 'r', 'utf-8'):
		line = line.rstrip()
		if line.startswith(u'#'):
			t_out.write(line+'\n')
			continue
		split = line.split('\t')
		if len(split) > 1:
			sentence.append(split)
		else:
			# create mapping
			random.shuffle(sentence)
			token_map = {}
			for i, t in enumerate(sentence, start=1):
				token_map[t[0]] = u''.join(str(i))
			token_map[u'0'] = u'0'
			for i, t in enumerate(sentence, start=1):
				if track == 't1':
					if t[6] in token_map:
						t[6] = token_map[t[6]]
				elif track == 't2':
					if t[8] in token_map:
						t[8] = token_map[t[8]]
				else:
					pass
				if dType == '1':
					if track == 't1':
						if t[5] != u'_':
							t[5] = t[5] + u'|original_id=' + t[0]
						else:
							t[5] = u'original_id=' + t[0]
					elif track == 't2':
						if t[6] != u'_':
							t[6] = t[6] + u'|original_id=' + t[0]
						else:
							t[6] = u'original_id=' + t[0]
				t[0] = u''.join(str(i))

			for tok in sentence:
				first = True
				for t in tok:
					if not first:
						t_out.write(u'\t')
					first = False
					t_out.write(t)
				t_out.write(u'\n')
			t_out.write(u'\n')
			sentence = []
	t_out.close()
			
source = os.path.join(tmpIn, 'conllu2conll', filename)

random.seed(1)

print(str(sys.argv[1]))

target = os.path.join(outFolder, filename)
corpus(source, target)
