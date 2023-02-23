#!/usr/bin/env python
# -*- coding: utf-8 -*-
# authors: simon mille

import glob
import sys
import os
import codecs
import shutil
import re
from shutil import copyfile

def Fouteen2Ten (line):
	""" converts a CoNLL'09 line to CoNLL-U """
	line = re.subn('^([0-9]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t)([^\t]+\t[^\t\n]+)$', '\g<1>\g<2>\g<3>\g<5>\g<6>\g<7>\g<9>\g<11>\g<13>', line)[0]
	return(line)

def replaceUnderscores (line):
	""" replaces underscores by colons in the deprel column """
	while re.search('^[0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+_', line):
		line = re.subn('^([0-9]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+)_', '\g<1>:', line)[0]
	return(line)
	
def replaceQuotes (line):
	""" reinserts double quotes (replaced for MATE conversion) """
	line = re.subn('^([0-9]+\t)DoubleQuote', '\g<1>"', line)[0]
	return(line)
	
def replaceQuotesLem (line):
	""" reinserts double quotes (replaced for MATE conversion) """
	line = re.subn('^([0-9]+\t[^\t]+\t)DoubleQuote', '\g<1>"', line)[0]
	return(line)

def cleanFeats (line):
	""" removes ppos and other feats from feats column when followed by '|' """
	line = re.subn('(ppos|kI|kF|kX|kP|kQ|kC)="[^"\|\t]+"\|', '', line)[0]
	return(line)

def cleanFeatsAlone (line):
	""" replace ppos and other feats by underscore when alone """
	line = re.subn('\t(ppos|kI|kF|kX|kP|kQ|kC)="[^"\|\t]+"\t', '\t_\t', line)[0]
	return(line)

def cleanOrder (line):
	""" removes quotes around relative order info """
	line = re.subn('lin="([-\+][^"\|\t]+)"', 'lin=\g<1>', line)[0]
	return(line)

if len(sys.argv) == 1:
	print ('Arguments: temporaryInputFolder outputFolder encodingInputFile encodingOuputFile file_extension[no_dot]')
else:
	tempOutPath = sys.argv[1]
	temp_output_folder_allFiles = os.path.join(tempOutPath,'allFiles')
	output_folder = sys.argv[2]
	input_encoding = sys.argv[3]
	output_encoding = sys.argv[4]
	output_format = sys.argv[5]
	structure_type = sys.argv[6]
	track = sys.argv[7]
	dType = sys.argv[8]
	reference_format = output_format
	#Create temporary and final output folders
	os.makedirs(temp_output_folder_allFiles)
	
	listFoldersToGroup = []
	
	#MATE puts the output files in folders; get the all files
	list_filepaths = ''
	if structure_type == 'deep':
		list_filepaths = glob.glob(os.path.join(tempOutPath, '**', '*out.conll'))
		reference_format = 'conll'
	elif structure_type == 'surf':
		list_filepaths = glob.glob(os.path.join(tempOutPath, '*.conll'))
		reference_format = 'conll'
	elif structure_type == 'sent':
		list_filepaths = glob.glob(os.path.join(tempOutPath, '*sentences.txt'))
	list_filepaths.sort()
	for filepath in list_filepaths:
		#Separate the path and the filename
		path, filename = os.path.split(filepath)
		#Remove the extension created by the conversion
		newFileName = filename
		if structure_type == 'deep':
			newFileName = re.subn('_out.conll', '', filename)[0]
		elif structure_type == 'sent':
			newFileName = re.subn('_sentences', '', filename)[0]
		
		if re.search('[0-9]+-[0-9]+\.'+reference_format, newFileName):
			#Separate the original filename and the number extensions added when files are cut (split_conllu.py)
			prefix = newFileName.rsplit('_', 1)[0]
			#Create a folder for each original filename
			if os.path.exists(os.path.join(temp_output_folder_allFiles, prefix)):
				pass
			else:
				os.makedirs(os.path.join(temp_output_folder_allFiles, prefix))
				listFoldersToGroup.append(prefix)
			#Group the files that belonged to the same original file within the same folder; these files will be grouped later on.
			copyfile(filepath, os.path.join(temp_output_folder_allFiles, prefix, newFileName))
			
		#Files that haven't been cut can be copied directly to the final output folder
		else:
			#finalFilename = ''
			if structure_type == 'deep':
				finalFilename = newFileName.rsplit('.', 1)[0]+'_DEEP.'+output_format
				copyfile(filepath, os.path.join(output_folder, finalFilename))
			elif structure_type == 'surf':
				finalFilename = newFileName.rsplit('.', 1)[0]+'.'+output_format
				fo = codecs.open(os.path.join(output_folder, finalFilename), 'w', str(output_encoding))
				file = codecs.open(os.path.join(tempOutPath, newFileName), 'r', str(input_encoding))
				#read lines of file
				list_lines = file.readlines()
				#write line in output file				
				for line in list_lines:
					if track == 't2':
						# reformat in CoNLLU (dirty copy from downstairs)
						 line = Fouteen2Ten(line)
					# This IF has to be synced with the one in conll2conllu.py
					if dType == '2':
						line = re.subn('^([0-9]+\t[^\t]+\t)[^\t]+(\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t\n]+)$', '\g<1>_\g<2>', line)[0]
					# remove ppos from feats (when followed by | )
					line = cleanFeats(line)
					# remove ppos from feats (when alone )
					line = cleanFeatsAlone(line)
					# clean quotes around order information
					line = cleanOrder(line)
					# reintroduce colons in deprel names
					line = replaceUnderscores(line)
					# reinsert double quotes
					line = replaceQuotes(line)
					line = replaceQuotesLem(line)
					fo.write(line)
				fo.close()
			elif structure_type == 'sent':
				finalFilename = newFileName.rsplit('.', 1)[0]+'.'+output_format
				copyfile(filepath, os.path.join(output_folder, finalFilename))
	
	#now go to each folder that contains the files to be grouped
	if len(listFoldersToGroup) == 0:
		print('No files to concatenate.')
	else:
		for folderToGroup in listFoldersToGroup:
			print(folderToGroup)
			folderPath = os.path.join(temp_output_folder_allFiles, folderToGroup)
			finalFilename = ''
			listFinalFilepaths = ''
			if structure_type == 'deep':
				finalFilename = os.path.join(output_folder, folderToGroup+'_DEEP.'+output_format)
				listFinalFilepaths = glob.glob(os.path.join(folderPath, '*.conll'))
			elif structure_type == 'surf':
				finalFilename = os.path.join(output_folder, folderToGroup+'.'+output_format)
				listFinalFilepaths = glob.glob(os.path.join(folderPath, '*.conll'))
			elif structure_type == 'sent':
				finalFilename = os.path.join(output_folder, folderToGroup+'.'+output_format)
				listFinalFilepaths = glob.glob(os.path.join(folderPath, '*.txt'))
			listFinalFilepaths.sort()
			#create output file
			fo = codecs.open(finalFilename, 'w', str(output_encoding))
			for finalFilepath in listFinalFilepaths:
				#open filepaths with argline encoding
				file = codecs.open(finalFilepath, 'r', str(input_encoding))
				#read lines of file
				list_lines = file.readlines()
				#write line in output file				
				for line in list_lines:
					if structure_type == 'surf' and track == 't2':
						# reformat in CoNLLU
						line = Fouteen2Ten(line)	
					# This IF has to be synced with the one in conll2conllu.py
					if dType == '2':
						line = re.subn('^([0-9]+\t[^\t]+\t)[^\t]+(\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t]+\t[^\t\n]+)$', '\g<1>_\g<2>', line)[0]
					# remove ppos from feats (when followed by | )
					line = cleanFeats(line)
					# remove ppos from feats (when alone )
					line = cleanFeatsAlone(line)
					# clean quotes around order information
					line = cleanOrder(line)
					# reintroduce colons in deprel names
					line = replaceUnderscores(line)
					# reinsert double quotes
					line = replaceQuotes(line)
					line = replaceQuotesLem(line)
					fo.write(line)
			fo.close()
		