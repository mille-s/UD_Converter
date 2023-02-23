#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: simon mille (I'm not good at python)
# Checks if folders, files, sentences and words are correctly aligned between an original file and a converted file

import re
import os
import sys
import codecs
import glob
from termcolor import colored


#if len(sys.argv) < 3:
#	sys.exit('!!! ARGUMENTS MISSING !!!\n1 = which track (t1 or t2)\n2 = input file type (conllu or conll)')
	
pathINOriginal = sys.argv[1]
pathINConverted = sys.argv[2]
pathDebug = sys.argv[3]
encoding = sys.argv[4]
converted = sys.argv[5]
dType = sys.argv[6]
scramble = sys.argv[7]

origFileList = glob.glob(os.path.join(pathINOriginal, '*.conllu'))
convertFileList = glob.glob(os.path.join(pathINConverted, '*.conllu'))

problems = 0

fo = codecs.open(os.path.join(pathDebug, 'log_alignments.txt'), 'a', 'utf-8')

line = ''
intro = ''

s1 = str(pathINOriginal)+' - '+str(pathINConverted)
print(s1)
intro += s1+'\n==================='
if len(origFileList) != len(convertFileList):
	problems += 1
	s2 = ' -ERROR: original or converted file missing!'
	print(colored(s2, 'red'))
	intro += '\n'+s2
else:
	s3 = ' -Same number of files in original and converted folders: '+str(len(origFileList))
	print(colored(s3, 'green'))
	intro += '\n'+s3

for origFilepath in origFileList:
	# store the original and converted sentences in two lists
	sentencesOrig = ''
	sentencesConvert = ''
	
	# build converted filepath to go get the file that corresponds to the original file
	path, filename = os.path.split(origFilepath)
	print(filename)
	line += '\n\n'+filename
	filenameNoExt = filename.rsplit('.', 1)[0]
	convertFilepath = ''
	if converted == 'UD2surf':
		convertFilepath = os.path.join(pathINConverted, filenameNoExt+'.conllu')
	else:
		convertFilepath = os.path.join(pathINConverted, filenameNoExt+'_DEEP.conllu')

	# open file
	fdOrigIN = codecs.open(origFilepath, 'r', str(encoding))
	fdConvertIN = ''
	
	# Process original file
	fileOrig = fdOrigIN.read()
	# normalise line breaks in original file
	if re.search('\r\n', fileOrig):
		fileOrig = re.subn('\r\n', '\n', fileOrig)[0]
	elif re.search('\r', fileOrig):
		fileOrig = re.subn('\r', '\n', fileOrig)[0]
	# Split file into sentences
	sentencesOrig = fileOrig.split('\n\n')
	# remove empty sentences at the end of the file
	if sentencesOrig[-1] == '' or sentencesOrig[-1] == u'':
		sentencesOrig = sentencesOrig[:-1]
	
	# Process converted file
	if os.path.isfile(convertFilepath):
		# open file
		fdConvertIN = codecs.open(convertFilepath, 'r', str(encoding))
		fileConvert = fdConvertIN.read()
		# Split file into sentences
		sentencesConvert = fileConvert.split('\n\n')
		# remove empty sentences at the end of the file
		if  sentencesConvert[-1] == '' or sentencesConvert[-1] == u'':
			sentencesConvert = sentencesConvert[:-1]
		x = ''
		# compare original and converted files
		if len(sentencesOrig) == len(sentencesConvert):
			s4 = ' -Same number of sentences in original and converted files: '+str(len(sentencesOrig))
			print(colored(s4, 'green'))
			line += '\n'+s4
			#if dType == '1':
			x = 0
			allProblemsWordAlign = 0
			# compare the original and converted files node to 
			while x < len(sentencesOrig):
				problemsWordAlign = 0
				# create two lists to store the ids of the original file and the original_ids of the converted file
				origId = []
				origLemma = []
				origIdLemDico = {}
				convertId = []
				convertLemma = []
				convertIdLemDico = {}
				# get ids and lemmas of original file (first column in conll)
				sentenceOrig = sentencesOrig[x]
				linesOrig = sentenceOrig.split('\n')
				counter_lines_metadata = 0
				counter_lines_bad_format = 0
				counter_lines_sentence = 1
				for lineOrig in linesOrig:
					# skip metadata
					# also ignore the non-conventional lines when comparing sentence lengths (e.g. 9.1, 2-3) 
					if re.search('^#', lineOrig) or re.search('^[0-9]+[^0-9\t]', lineOrig):
						counter_lines_metadata += 1
					elif re.search('\t', lineOrig):
						columnsOrig = lineOrig.split('\t')
						origId.append(columnsOrig[0])
						origIdLemDico[columnsOrig[0]] = ''
						# get the lemma in the original file
						if converted == 'surf2deep':
							origLemma.append(columnsOrig[1])
							origIdLemDico[columnsOrig[0]] = columnsOrig[1]
						else:
							origLemma.append(columnsOrig[2])
							origIdLemDico[columnsOrig[0]] = columnsOrig[2]
					else:
						counter_lines_bad_format += 1
						# print('"'+lineOrig+'"')
						print(' -sentence '+str(x)+', line '+str(counter_lines_sentence)+': line with a possible hidden character that breaks format.')
					counter_lines_sentence += 1
							
				# get ids and lemmas of converted file (in the feats column, under the original_id feature)
				sentenceConvert = sentencesConvert[x]
				linesConvert = sentenceConvert.split('\n')
				# first check that there are the same number of nodes in surface and original UD structures
				if converted == 'UD2surf':
					actual_len_linesOrig = len(linesOrig) - counter_lines_metadata
					if actual_len_linesOrig == len(linesConvert):
						pass
					else:
						problems += 1
						problemsWordAlign += 1
						allProblemsWordAlign += 1
						s14 = ' -ERROR: Sentence '+str(x)+' : different number of words'
						print(colored(s14, 'red'))
						line += '\n'+s14+' >>>>> '+str(actual_len_linesOrig)+'-'+str(len(linesConvert))
				for lineConvert in linesConvert:
					if re.search('\t', lineConvert):
						columnsConvert = lineConvert.split('\t')
						if re.search('original_id=[0-9]+', columnsConvert[5]):
							# if there are more than one features, split the feats
							if re.search('|',  columnsConvert[5]):
								featsConvert = columnsConvert[5].split('|')
								for featConvert in featsConvert:
									nameFeat = featConvert.split('=')
									if converted == 'surf2deep':
										if re.search('id1=[0-9]+', columnsConvert[5]):
											if nameFeat[0] == 'id1':
												convertId.append(nameFeat[1])
												if re.search('^[0-9]+\t_\t\_\tPRON', lineConvert):
													pass
												else:
													convertIdLemDico[nameFeat[1]] = columnsConvert[1]
										else:
											if dType == '1':
												problems += 1
												problemsWordAlign += 1
												allProblemsWordAlign += 1
												s16 = ' -ERROR: Sentence '+str(x)+' : missing ID (id1) in converted file'
												print(colored(s16, 'red'))
												line += '\n'+s16+' >>>>> Converted line: "'+str(lineConvert)+'"'
									else:
										if nameFeat[0] == 'original_id':
											convertId.append(nameFeat[1])
											if re.search('^[0-9]+\t_\t\_\tPRON', lineConvert):
												pass
											else:
												convertIdLemDico[nameFeat[1]] = columnsConvert[1]
							# if there is only one feature
							else:
								nameFeat = columnsConvert[5].split('=')
								convertId.append(nameFeat[1])
								if re.search('^[0-9]+\t_\t\_\tPRON', lineConvert):
									pass
								else:
									convertIdLemDico[nameFeat[1]] = columnsConvert[1]
						else:
							# if a feats columns doesn't contain the original_id feat
							# empty pronouns added during the conversion have no correspondence
							if scramble == 'no':
								pass
							elif re.search('^[0-9]+\t_\t\_\tPRON', lineConvert):
								pass
							else:
								if dType == '1':
									problems += 1
									problemsWordAlign += 1
									allProblemsWordAlign += 1
									s5 = ' -ERROR: Sentence '+str(x)+' : missing ID (original_id) in converted file'
									print(colored(s5, 'red'))
									try:
										line += '\n'+s5+' >>>>> Converted line: "'+str(lineConvert)+'"'
									except Exception as e:
										line += '\n  -ERROR: '+str(e)
						# get the lemma in the converted filefeat
						# empty pronouns added during the conversion have no correspondence
						if re.search('^[0-9]+\t_\t\_\tPRON', lineConvert):
							pass
						else:
							convertLemma.append(columnsConvert[1])
				id_duplicate_check_list = []
				# once the lists with the original ids and the corresponent id in the converted file are filled, chech that every ID of the converted file is in the original file
				if dType == '1':
					for id in convertId:
						if id not in origId:
							problems += 1
							problemsWordAlign += 1
							allProblemsWordAlign += 1
							s6 = ' -ERROR: Sentence '+str(x)+' : mismatch ID between converted and original'
							print(colored(s6, 'red'))
							line += '\n'+s6+' >>>>> Converted id = '+id
						else:
							pass
						# check that every converted ID is unique
						if id not in id_duplicate_check_list:
							id_duplicate_check_list.append(id)
						else:
							problems += 1
							problemsWordAlign += 1
							allProblemsWordAlign += 1
							s13 = ' -ERROR: Sentence '+str(x)+' : n to 1 alignment with original node'
							print(colored(s13, 'red'))
							line += '\n'+s13+' >>>>> Converted id = '+id
				# now check the lemmas in both files		
				for lemma in convertLemma:
					if lemma not in origLemma:
						# in the following cases there will be a mismatch, no need to report it; if a real error happens in a sentence with these lemmas it won't appear in the log. OK for now.
						#if u'_' in origLemma or u'@card@' in origLemma or u'@ord@' in origLemma:
							#pass
						#else:						
						problems += 1
						problemsWordAlign += 1
						allProblemsWordAlign += 1
						s7 = ' -ERROR: Sentence '+str(x)+' : mismatch LEMMAS between converted and original'
						print(colored(s7, 'red'))
						line += '\n'+s7+' >>>>> Converted lemma = "'+lemma+'"'
					else:
						pass
				# in case there is no error with lemmas and IDs individually, for each sentence, compare ID-lemma pairs
				if dType == '1':
					if problemsWordAlign == 0:
						#if lemmas and ids correspond on their own, check that the pairs of lemma-id correspond too
						for k in convertIdLemDico:
							if convertIdLemDico[k] == origIdLemDico[k]:
							#if convertIdLemDico.items() <= origIdLemDico.items():
								pass
							else:
								problems += 1
								allProblemsWordAlign += 1
								s15 = ' -ERROR: Sentence '+str(x)+' : mismatch ID-LEMMA between converted and original'
								print(colored(s15, 'red'))
								line += '\n'+s15+' >>>>> Original: "'+str(origIdLemDico[k])+'", Converted: "'+str(convertIdLemDico[k])+'"'
				x += 1

			if allProblemsWordAlign == 0:
				s8 = ' -All converted nodes are aligned with the original file'
				print(colored(s8, 'green'))
				line += '\n'+s8
		else:
			# if the number of sentences is not the same in both files...
			problems += 1
			s9 = ' -ERROR: different number of sentences:'+' Original='+str(len(sentencesOrig))+', Converted='+str(len(sentencesConvert))
			print(colored(s9, 'red'))
			line += '\n'+s9
	else:
		# if a original file has no correspondence in the converted folder
		problems += 1
		s10 = ' -ERROR: converted file missing: '+str(convertFilepath)
		print(colored(s10, 'red'))
		line += '\n'+s10

if problems == 0:
	s11 = '------------------\nAll alignments OK!\n------------------'
	print(colored(s11, 'green'))
	intro += '\n\n'+s11
else:
	s12 = '------------------\nProblems detected!\n------------------'
	print(colored(s12, 'red'))
	intro += '\n\n'+s12

fo.write(intro)
fo.write(line)
fo.write('\n\n\n\n')
fo.close()
	

