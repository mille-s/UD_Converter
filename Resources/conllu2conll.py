#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: simon mille (I'm not good at python)

import re
import os
import sys
import codecs
import glob


#if len(sys.argv) < 3:
#	sys.exit('!!! ARGUMENTS MISSING !!!\n1 = which track (t1 or t2)\n2 = input file type (conllu or conll)')
	
# t1 or t2 preprocessing
#preprocessingType = sys.argv[1]
fileType = sys.argv[1]
pathIN = sys.argv[2]
originalID = sys.argv[3]
originalForm = sys.argv[4]
originalXpos = sys.argv[5]
parentheses = sys.argv[6] 
quotationMarks = sys.argv[7]
orderPunc = sys.argv[8]
orderConj = sys.argv[9]
orderMWE = sys.argv[10]
preprocessingType = sys.argv[11]
dType = sys.argv[12]
sentOutTmpFolder =  sys.argv[13]
reduce_tree =  sys.argv[14]
adposition =  sys.argv[15]
copula =  sys.argv[16]

#print('Processing', str(pathIN))
# utf-8, utf-16BE, etc.
#input_file_encoding = sys.argv[4]
input_file_encoding = 'utf-8'
# output type should be "tree" or "graph"
#output_file_encoding = sys.argv[5]
output_file_encoding = 'utf-8'


FileList = ''
if fileType == 'conllu':
	FileList = glob.glob(os.path.join(pathIN, '*.conllu'))
elif fileType == 'conll':
	FileList = glob.glob(os.path.join(pathIN, '*.conll'))

FileNameList = os.listdir(pathIN)

def writeLineOrder (line, number):
	""" Function to write the lines of the output file including relative word order information """
	line = re.subn('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t\r\n]+)$', '\g<1>lin="'+number+'"|\g<2>', line)[0]
	return(line)
	
def addRelativeOrder(line, dico_order_neg, dico_order_pos, deprel):
	""" Function for adding the relative order of selected dependents with respect to their governor, under the form lin=-3, lin=-2, lin=1, lin=2, etc.  """
	list_columns = line.split('\t')
	relative_order = int(list_columns[0]) - int(list_columns[6])
	length_negatives = 0
	length_positives = 0
	# Count numbers of dependents on the left of their governor
	if int(list_columns[6]) in dico_order_neg.keys():
		length_negatives = len(dico_order_neg[int(list_columns[6])])
	# Count numbers of dependents on the right of their governor
	if int(list_columns[6]) in dico_order_pos.keys():
		length_positives = len(dico_order_pos[int(list_columns[6])])
		
	number = ''
	# For negative numbers, use the number of remaining elements in the list 
	if relative_order < 0:
		number = '-'+str(length_negatives)
		dico_order_neg[int(list_columns[6])].remove(relative_order)
	# For positive numbers, use the position of element in the list
	elif relative_order > 0:
		for i in [i for i,x in enumerate(dico_order_pos[int(list_columns[6])]) if x == relative_order]:
			number = '+'+str(i+1)
		
	# For conjunctions, we only add order info if there are at least two conjuncts below a governor 
	if deprel == 'conj':
		if length_negatives + length_positives > 1:
			line = writeLineOrder(line, number)
	# For other puncts and mwes, we add order info in all cases
	else:
		line = writeLineOrder(line, number)
	return(line)

def fillDicoOrder (line, dico_order_neg, dico_order_pos):
	""" Function for filling two dictionaries per structures, with governors as keys and dependents in list of values. One dico for dependents linearized after the governor, and one for dependents linearized before. """
	list_columns = line.split('\t')
	relative_order = int(list_columns[0]) - int(list_columns[6])
	if relative_order < 0:
		# Create an entry in the dictionary for each governor that has a targeted dependent realized before its governor, or append dependent in list of dependents for each governor
		if int(list_columns[6]) in dico_order_neg.keys():
			dico_order_neg[int(list_columns[6])].append(relative_order)
		else:
			dico_order_neg[int(list_columns[6])] = []
			dico_order_neg[int(list_columns[6])].append(relative_order)
	elif relative_order > 0:
		# Create an entry in the dictionary for each governor that has a targeted dependent realized after its governor, or append dependent in list of dependents for each governor
		if int(list_columns[6]) in dico_order_pos.keys():
			dico_order_pos[int(list_columns[6])].append(relative_order)
		else:
			dico_order_pos[int(list_columns[6])] = []
			dico_order_pos[int(list_columns[6])].append(relative_order)

file_num = 0
for InputFile in FileList:
	console = FileNameList[file_num] + '...'
	print(console)
	notify_lemma = ''
	fdIN = codecs.open(InputFile, 'r', str(input_file_encoding))
	#containing_path = pathIN.rsplit('/', 1)[0]
	output_folder = os.path.join(pathIN, 'conllu2conll')
	#if preprocessingType == 't1':
		#output_folder = os.path.join(pathIN, 'conllu2conll')
	#elif preprocessingType == 't2':
		#output_folder = os.path.join(pathIN, 'conllu2mate')
		
	# create output repository	
	if not os.path.exists(output_folder):
		os.makedirs(output_folder)
	# create names of output files
	NewFileNameStructure = FileNameList[file_num].replace('conllu', 'conll')
	NewFileNameSentence = FileNameList[file_num].replace('.conllu', '_sentences.txt')
	# create and open output files
	#fo = codecs.open(output_folder + '/' + NewFileNameStructure,'w',str(output_file_encoding))
	fo = codecs.open(os.path.join(output_folder, NewFileNameStructure),'w',str(output_file_encoding))
	if fileType == 'conllu':
		#foSent = codecs.open(output_folder + '/' + NewFileNameSentence,'w',str(output_file_encoding))
		foSent = codecs.open(os.path.join(sentOutTmpFolder, NewFileNameSentence),'w',str(output_file_encoding))

	file_in = fdIN.read()
  # Line break can be \n, \r or \r\n according to the OS. Normalise to \n
	if re.search('\n\n', file_in):
		pass
	elif re.search('\r\n', file_in):
		file_in = re.subn('\r\n', '\n', file_in)[0]
	elif re.search('\r', file_in):
		file_in = re.subn('\r', '\n', file_in)[0]
	sentences = file_in.split('\n\n')
	if sentences[-1] == '':
		sentences = sentences[:-1]
	for sentence in sentences:
		dico_order_neg = {}
		dico_order_pos = {}
		# print('##### Snt: '+sentence)
		# print('End Snt #####')
		# Do not write sentences that contain dependencies that don't make sense in a generation setup
		#if re.search('[0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\treparandum\t[^\t]+\t[^\t]+\n', sentence):
			#pass
		#elif re.search('[0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\treparandum\t[^\t]+\t[^\t]+$', sentence):
			#pass
		#elif re.search('[0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\torphan\t[^\t]+\t[^\t]+\n', sentence):
			#pass
		#elif re.search('[0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\torphan\t[^\t]+\t[^\t]+$', sentence):
			#pass
		#elif re.search('[0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\tgoeswith\t[^\t]+\t[^\t]+\n', sentence):
			#pass
		#elif re.search('[0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\tgoeswith\t[^\t]+\t[^\t]+$', sentence):
			#pass
		#else:		
		#START INDENT (if previous block activated)
		lines = sentence.split('\n')
		line_copy = ''
		# One loop to fill the dictionnary where the number of dependents for which the order information needs to be stored
		for line in lines:
			#print('Line: '+line)
			# remove weird characters
			# line = re.subn(' ', ' ', line)[0]
			if orderPunc == 'yes':
				if re.search('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\tpunct\t[^\t]+\t[^\t\r\n]+)$', line):
					fillDicoOrder(line, dico_order_neg, dico_order_pos)
			if orderConj == 'yes':
				if re.search('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\tconj\t[^\t]+\t[^\t\r\n]+)$', line):
					fillDicoOrder(line, dico_order_neg, dico_order_pos)
			if orderMWE == 'yes':
				if re.search('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\t(compound|compound:prt|compound:svc|flat|flat:foreign|flat:name|fixed)\t[^\t]+\t[^\t\r\n]+)$', line):
					fillDicoOrder(line, dico_order_neg, dico_order_pos)
		for line in lines:
			# Store the sentences separately
			if re.search('^\#[^\r\n]+$', line):
				foSent.write(line+'\n')
			else:
				# Ignore empty nodes
				if re.search('^[0-9]+\.[^\r\n]+$', line):
					pass
				# Ignore combined LUs (e.g, Italian train, sentence 1)
				elif re.search('^[0-9]+-[0-9]+[^\r\n]+$', line):
					pass
				else:
					# add order information
					if orderPunc == 'yes':
						if re.search('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\tpunct\t[^\t]+\t[^\t\r\n]+)$', line):
							line = addRelativeOrder(line, dico_order_neg, dico_order_pos, 'punct')
					if orderConj == 'yes':
						if re.search('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\tconj\t[^\t]+\t[^\t\r\n]+)$', line):
							line = addRelativeOrder(line, dico_order_neg, dico_order_pos, 'conj')
					if orderMWE == 'yes':
						if re.search('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\t(compound|compound:prt|compound:svc|flat|flat:foreign|flat:name|fixed)\t[^\t]+\t[^\t\r\n]+)$', line):
							line = addRelativeOrder(line, dico_order_neg, dico_order_pos, 'mwe')				
					# copy value of surface form to lemma if no lemma is available 
					if re.search('^([0-9]+\t)([^\t]+\t)(_\t)', line) or re.search('^([0-9]+\t)([^\t]+\t)(@card@\t)', line) or re.search('^([0-9]+\t)([^\t]+\t)(@ord@\t)', line):
						line = re.subn('^([0-9]+\t)([^\t]+\t)([^\t]+\t)', '\g<1>\g<2>\g<2>', line)[0]
						if notify_lemma == '':
							notify_lemma = 'yes'				
					# otherwise, if the lemma is not empty, invert slex and lemma so the lemma shows as new node name
					else:
						line = re.subn('^([0-9]+\t)([^\t]+\t)([^\t]+\t)', '\g<1>\g<3>\g<2>', line)[0]
					# remove the contents of the last two columns
					line =  re.subn('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)[^\t]+\t[^\t\r\n]+$', '\g<1>_\t_', line)[0]
					if preprocessingType == 't2':
						# Replace double quotes for MATE processing
						line = re.subn('\t"\t', '\tDoubleQuote\t', line)[0]
						# Replace double quotes for MATE processing
						line = re.subn('\t“\t', '\tDoubleQuote\t', line)[0]
						# Replace double quotes for MATE processing
						line = re.subn('\t”\t', '\tDoubleQuote\t', line)[0]
						# Reformat ppos column
						while re.search('^([0-9]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+)\|([^\t]+)\t([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t\r\n]+)$', line):
							line = re.subn('^([0-9]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+)\|([^\t]+)\t([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t\r\n]+)$', '\g<1>\g<2>\g<3>\g<4>\g<5>_\g<6>\t\g<7>\g<8>\g<9>\g<10>\g<11>', line)[0]
						# Move ppos to FEATS column
						line = re.subn('^([0-9]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+)\t([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t\r\n]+)$', '\g<1>\g<2>\g<3>\g<4>\g<5>\tppos="\g<5>"|\g<6>\g<7>\g<8>\g<9>\g<10>', line)[0]
						# Add features to keep information in the deep structure
						if originalID == 'yes':
							line = re.subn('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t\r\n]+)$', '\g<1>kI="y"|\g<2>', line)[0]
						if originalForm == 'yes':
							line = re.subn('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t\r\n]+)$', '\g<1>kF="y"|\g<2>', line)[0]
						if originalXpos == 'yes':
							line = re.subn('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t\r\n]+)$', '\g<1>kX="y"|\g<2>', line)[0]
						if parentheses == 'yes':
							line = re.subn('^([0-9]+\t[\(\)]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t\r\n]+)$', '\g<1>kP="y"|\g<2>', line)[0]
						if quotationMarks == 'yes':
							line = re.subn('^([0-9]+\t[‘’\']\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t\r\n]+)$', '\g<1>kQ="y"|\g<2>', line)[0]
							line = re.subn('^([0-9]+\tDoubleQuote\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t\r\n]+)$', '\g<1>kQ="y"|\g<2>', line)[0]
						if reduce_tree == 'yes':
							line = re.subn('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\troot\t[^\t]+\t[^\t\r\n]+)$', '\g<1>rT="y"|\g<2>', line)[0]
						if adposition == 'yes':
							line = re.subn('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t\r\n]+)$', '\g<1>kA="y"|\g<2>', line)[0]
						if copula == 'yes':
							line = re.subn('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t\r\n]+)$', '\g<1>kB="y"|\g<2>', line)[0]
						if dType == '2':
							line = re.subn('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t)([^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t\r\n]+)$', '\g<1>kC="n"|\g<2>', line)[0]
						# Map to CoNLL'09 (Shortcut: CoNLL06-matches)
						line = re.subn('^([0-9]+\t[^\t]+\t)([^\t]+\t)([^\t]+\t[^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t[^\t\r\n]+)$', '\g<1>\g<2>_\t\g<3>\g<4>_\t\g<5>\g<5>\g<6>\g<6>\g<7>', line)[0]
						# Clean
						line = re.subn('\|_', '', line)[0]
						# Replace colons by underscores in the DEPREL colum
						line = re.subn('^([0-9]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+):([^\t]+\t)([^\t]+):([^\t]+\t)([^\t]+\t[^\t\r\n]+)$', '\g<1>\g<2>\g<3>\g<4>\g<5>\g<6>\g<7>\g<8>\g<9>\g<10>\g<11>_\g<12>\g<13>_\g<14>\g<15>', line)[0]
					elif preprocessingType == 't1':
						# This IF has to be synced with the one in concatenateFiles.py
						if dType == '2':
							line = re.subn('^([0-9]+\t[^\t]+\t)[^\t]+(\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t\r\n]+)$', '\g<1>_\g<2>', line)[0]
						else:
							pass
							
						# Clean
						line = re.subn('lin="([-\+][^"\|\t]+)"', 'lin=\g<1>', line)[0]
						line = re.subn('\|_', '', line)[0]
					line = line + '\n'
					fo.write(line)
			line_copy = line
		if not line_copy == '\n':
			fo.write('\n')
			if fileType == 'conllu':
				foSent.write('\n')
		#STOP INDENT
	file_num = file_num + 1
	fo.close()
	if notify_lemma == 'yes':
		print('  !!! One or more LEMMA was changed, expect alignment error during output check.')
	if fileType == 'conllu':
		foSent.close()
