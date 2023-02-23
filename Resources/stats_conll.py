#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import codecs
import re
import operator
import glob
import os

def addEntry(dico, key, value):
	if key not in dico:
		dico[key] = []
	dico[key].append(value)
	#rober
	#dico[key] = dico.get(key, []).append(value)

#addEntry function using a class, by rober
def newAddEntry(dico, key, value):
	if key not in dico:
		dico[key] = ConllData()
	dico[key].addOccurrence(value)

class ConllData:
	def __init__(self):
		self.occurs = []
	def addOccurrence(self, lineno):
		self.occurs.append(lineno)
	def count(self):
		return len(self.occurs)

		
def formatOutput (dico, wordcount):
	#build new dico with number of occurrences instead of list of lines they appear in
	dico_numOcc = {}
	#for entry in dico_lemma.keys():
	for entry in dico:
		dico_numOcc[entry] = len(dico[entry])

	#produce a list of tuples with dico entries sorted by numeric value of value
	#tuples have the form (key, value)
	sorted_list_numOcc = sorted(dico_numOcc.items(), key=operator.itemgetter(1), reverse = True)

	whole_list = ''
	for tuple in sorted_list_numOcc:
		key = tuple[0]
		value = tuple[1]
		relative_frequency = value/wordcount
		line = str(key)+'\t'+str(value)+'\t'+str(relative_frequency)+'\n'
		whole_list = whole_list+line
	return(whole_list)

if len(sys.argv) == 1:
	print('2 Arguments needed: pathInputFolder gold|pred|conllu')
else:
	folderPath = sys.argv[1]
	list_filepaths = glob.glob(os.path.join(folderPath, '*.*'))
	for filepath in list_filepaths:
		dico_lemma = {}
		dico_pos = {}
		dico_dep = {}
		dico_pos_dep = {}
		#to count number of lines in input file
		lineno = 0
		wordno = 0
		sentenceno = 0
		
		fd = codecs.open(filepath, 'r', 'utf-8')
		path, filename = os.path.split(filepath)
		lines = fd.readlines()
		for line in lines:
			lineno = lineno + 1
			# exclude lines with metadata
			if re.search('^#', line):
				pass
			elif re.search('^[0-9]+', line):
				wordno = wordno + 1
				line = re.subn('\n', '', line)[0]
				# split conll columns
				list_columns = line.split('\t')
				
				lemma = ''
				pos = ''
				dep = ''
				# the info is in different columns if looking at a gold annotation or a predicted one.
				if sys.argv[2] == 'gold':
					lemma = list_columns[2]
					pos = list_columns[4]
					dep = list_columns[10]
				elif sys.argv[2] == 'pred':
					lemma = list_columns[3]
					pos = list_columns[5]
					dep = list_columns[11]
				elif sys.argv[2] == 'conllu':
					lemma = list_columns[2]
					pos = list_columns[3]
					dep = list_columns[7]
					
				pos_and_dep = pos + '_' + dep
				
				addEntry(dico_lemma, lemma, lineno)
				addEntry(dico_pos, pos, lineno)
				addEntry(dico_dep, dep, lineno)
				addEntry(dico_pos_dep, pos_and_dep, lineno)
			# if a line doesn't start with a number, it's a linebreak between two consecutive structures
			else:
				# we actualize the sentence counter
				sentenceno = sentenceno + 1
				
				
				#newAddEntry(dico_lemma, lemma, lineno)
				#newAddEntry(dico_pos, pos, lineno)
				#newAddEntry(dico_dep, dep, lineno)
				
		#print(dico_lemma)


		pos_list = formatOutput(dico_pos, wordno)
		dep_list = formatOutput(dico_dep, wordno)
		lemma_list = formatOutput(dico_lemma, wordno)
		pos_and_dep_list = formatOutput(dico_pos_dep, wordno)
		words_by_sentence = str(round(wordno/sentenceno, 2))
		
		outputFolder = os.path.join(folderPath, 'stats')
		if not os.path.exists(outputFolder):
			os.makedirs(outputFolder)

		fo = codecs.open(os.path.join(outputFolder, filename+'.txt'), 'w', 'utf-8')

		fo.write('Number of sentence: '+str(sentenceno)+'\n'+'Number of words: '+str(wordno)+'\n'+'Average words by sentence: '+words_by_sentence+'\n\n===========\n    POS    \n===========\n'+pos_list+'\n==============\n DEPENDENCIES \n==============\n'+dep_list+'\n=============\n  POS & DEP  \n=============\n'+pos_and_dep_list+'\n============\n   LEMMAS   \n============\n'+lemma_list)

		fo.close()