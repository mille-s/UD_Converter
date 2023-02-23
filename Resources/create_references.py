#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is for producing a tokenized version of the UD sentences, using the structures (instead of using a tokenizer). The poblem are the "multilexemes" (e.g. 'del' in Spanish, which contains 'de+el' / 'of+the'), which are duplicated in the structure. However, this is done in a systematic way and easy to cope with. The detokenized version of the sentences is also created.

# In the following example, we want to write the 2-3 line, but not the lines 2 nor 3, that is, we want "Sin mencionarlo directamente":
#1	Sin	sin	ADP	ADP	AdpType=Prep	2	mark	_	_
#2-3	mencionarlo	_	_	_	_	_	_	_	_
#2	mencionar	mencionar	VERB	VERB	VerbForm=Inf	8	advcl	_	_
#3	lo	él	PRON	PRON	Case=Acc|Gender=Masc|Number=Sing|Person=3|PronType=Prs	2	obj	_	_
#4	directamente	directamente	ADV	ADV	_	2	advmod	_	SpaceAfter=No

import re
import os, shutil
import sys
import codecs
import glob
from sacremoses import MosesTokenizer, MosesDetokenizer

pathIN = sys.argv[1]
input_file_encoding = 'utf-8'
output_file_encoding = 'utf-8'

# Clear the output folder before starting
output_folder = os.path.join(pathIN, 'references')
try:
	shutil.rmtree(output_folder)
except Exception as e:
	pass
	
FileList = glob.glob(os.path.join(pathIN, '*.conllu'))
#print(FileList)
FileNameList = os.listdir(pathIN)
#print(FileNameList)

# create output repository	
output_tokenized = os.path.join(output_folder, 'tokenized')
output_detokenized = os.path.join(output_folder, 'detokenized')
os.makedirs(output_folder)
os.makedirs(output_tokenized)
os.makedirs(output_detokenized)

language = 'en'

file_num = 0
for InputFile in FileList:
	console = FileNameList[file_num] + '...'
	print(console)
	
	# open file
	fdIN = codecs.open(InputFile, 'r', str(input_file_encoding))
	
	# create new file name and open output file	
	NewFileNameStructure = FileNameList[file_num].replace('conllu', 'txt')
	fo_tok = codecs.open(os.path.join(output_tokenized, NewFileNameStructure), 'w', str(output_file_encoding))
	fo_detok = codecs.open(os.path.join(output_detokenized, NewFileNameStructure), 'w', str(output_file_encoding))
	
	# update language parameter
	language = NewFileNameStructure.split('_')[0]
	
	# read file
	file = fdIN.read()
	# Split file into sentences
	sentences = file.split('\n\n')
	if sentences[-1] == '':
		sentences = sentences[:-1]
	id = 1
	for sentence in sentences:
		last_id = 0
		# split sentence into lines
		sentence_detok = []
		add_sentence_detok = 'yes'
		# If a sentence has metadata, we will take the detokenized reference sentence from it
		if re.search('^#', sentence):
			add_sentence_detok = 'no'
		# If there is no metadata (e.g. predicted parser outputs), we have to create the metadata fields
		else:
			fo_tok.write('# sent_id = '+str(id)+'\n#text = ')
			fo_detok.write('# sent_id = '+str(id)+'\n#text = ')
		lines = sentence.split('\n')
		for line in lines:
			# only write lines with original (detokenized) sentences for detokenized output
			if re.search('^\#\s*text = [^\n]+$', line):
				fo_tok.write('#text = ')
				fo_detok.write(line)
			elif re.search('^\#[^\n]+$', line):
				if re.search('^# orig_file_sentence', line):
					pass
				elif re.search('^# source', line):
					pass
				elif re.search('^# id', line):
					pass
				elif re.search('^# sent_id', line):
					pass
				elif re.search('^# text_en', line):
					pass
				elif re.search('^# english_text', line):
					pass
				elif re.search('^# s_type', line):
					pass
				elif re.search('^# speaker', line):
					pass
				else:
					fo_tok.write(line+'\n')
					fo_detok.write(line+'\n')
			# ignore lines which represent elided nodes
			elif re.search('^[0-9]+\.[0-9]+', line):
				pass
			else:
				# split lines into columns; we are interested in column 0 (id) and column 1 (surface form)	
				columns = line.split('\t')
				# if line is a word with multilexeme, write it
				if re.search('^[0-9]+-[0-9]+', line):
					# get the id of the last component of the multilexeme and update the variable
					last_id = int(columns[0].rsplit('-')[1])
					# write word in output file
					word = columns[1]
					fo_tok.write(word+' ')
					# store word in list for further detokenization
					sentence_detok.append(word)
				else:
					# if an ID is lower or equal to the last_id of a multilexeme, we don't write it.
					if int(columns[0]) <= last_id:
						pass
					else:
						# otherwise, the word is written
						word = columns[1]
						fo_tok.write(word+' ')
						# store word in list for further detokenization
						# the detokenizer doesn't handle simple hyphens, so we mark the configurations that need to be detokenized
						if word == '-':
							if columns[3] == 'PUNCT':
								if columns[4] == 'HYPH' or columns[4] == ':':
									word = 'NOSPACE_'+word+'_NOSPACE'
							elif columns[3] == 'SYM':
								if columns[4] == 'SYM':
									word = 'NOSPACE_'+word+'_NOSPACE'
						elif word == "'":
							if columns[3] == 'PUNCT':
								if columns[4] == '``':
									word = 'SPACE_'+word+'_NOSPACE'
								elif columns[4] == "''":
									word = 'NOSPACE_'+word+'_SPACE'
							elif columns[3] == 'PART':
								if columns[4] == 'POS':
									word = 'NOSPACE_'+word+'_SPACE'
						elif word == "/":
							if columns[3] == 'SYM':
								word = 'NOSPACE_'+word+'_NOSPACE'
							elif columns[7] == 'cc':
								word = 'NOSPACE_'+word+'_NOSPACE'
						sentence_detok.append(word)
		# write the detonekized version of the reference sentence
		if add_sentence_detok == 'yes':
			# For now we're mostly interested in the English tokenizer; it seems to perform OK on other languages.
			# Make the parameter a variable
			mt, md = MosesTokenizer(lang=language), MosesDetokenizer(lang=language)
			final_detok_sentence = (md.detokenize(sentence_detok))
			# custom detokenization cases not covered by the detokenizer
			if language == 'en':
				final_detok_sentence = re.subn(" n't ", "n't ", final_detok_sentence)[0]
				final_detok_sentence = re.subn(" nt ", "nt ", final_detok_sentence)[0]
				final_detok_sentence = re.subn(" d ", "d ", final_detok_sentence)[0]
				final_detok_sentence = re.subn(" s ", "s ", final_detok_sentence)[0]
			final_detok_sentence = re.subn(' NOSPACE_', '', final_detok_sentence)[0]
			final_detok_sentence = re.subn('_NOSPACE ', '', final_detok_sentence)[0]
			final_detok_sentence = re.subn('([^\s])SPACE_', '\g<1> ', final_detok_sentence)[0]
			final_detok_sentence = re.subn('^SPACE_', '', final_detok_sentence)[0]
			final_detok_sentence = re.subn('(\s)SPACE_', '\g<1>', final_detok_sentence)[0]
			final_detok_sentence = re.subn('_SPACE([^\s])', ' \g<1>', final_detok_sentence)[0]
			final_detok_sentence = re.subn('_SPACE(\s)', '\g<1>', final_detok_sentence)[0]
			final_detok_sentence = re.subn('_SPACE$', '', final_detok_sentence)[0]
			fo_detok.write(final_detok_sentence)
		id = id + 1	
		fo_tok.write('\n\n')
		fo_detok.write('\n\n')
	file_num = file_num + 1
	#print(language)
	fo_tok.close()
	fo_detok.close()