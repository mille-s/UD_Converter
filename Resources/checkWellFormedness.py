#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: simon mille

# Import package of regular expressions
import re
import os, shutil
import sys
import codecs
from termcolor import colored

if len(sys.argv) < 5:
	sys.exit('!!! ARGUMENTS MISSING !!!\n1 = path to folder to save logfile\n2 = path to file to be checked\n3 = encoding of input file to be checked (e.g. "utf-16BE")\n4 = output format ("tree"/"graph")\n5 (optional) = create output directory with problematic files ("debug")')

mainOutputFolder = sys.argv[1]
filepathOUT = sys.argv[2]
# utf-8, utf-16BE, etc.
input_file_encoding = sys.argv[3]
# output type should be 'tree' or 'graph'
output_type = sys.argv[4]
inputFormat = sys.argv[6]
# set this value by default
create_output = ''
sentencesIN = []

pathX, filenameX = os.path.split(filepathOUT)
originalFilename = filenameX.split('_DEEP', 1)[0]+'.'+inputFormat
filepathIN = ''
outputFolder = os.path.join(mainOutputFolder, originalFilename)
if not os.path.exists(outputFolder):
	os.makedirs(outputFolder)

if len(sys.argv) > 5:
	filepathIN = os.path.join(sys.argv[5], originalFilename)

# Define template for output file names
filename_template1 = os.path.join(outputFolder, 'in-out_Disconnected', 'str_{0}.conllu')
filename_template2 =  os.path.join(outputFolder, 'in-out_MultipleIncoming', 'str_{0}.conllu')
#filename_template3 =  os.path.join(outputFolder, 'in_out-Disconnected_AND_Multiple_incoming_deprels', 'str_{0}.conllu')
filename_template4 =  os.path.join(outputFolder, 'in-out_DuplicatedArguments', 'str_{0}.conllu')

def build_debug_file(sentIN, sentOUT):
	""" Function that builds a file with all buggy inputs, and processes the lines to be written in the individual files """
	sentenceFinal = '//INPUT\n//------\n'+sentIN+'\n\n//OUTPUT\n//------\n'+sentOUT
	fo = codecs.open(os.path.join(outputFolder, 'in-allErrors.conllu'),'a','utf-8')
	fo.write(sentIN + '\n\n')
	fo.close()
	return(sentenceFinal)
	
def build_debug_file1(sent_num, sentIN, sentOUT):
	""" Function that builds individual files with buggy inputs/outputs """
	sentenceFinal = build_debug_file(sentIN, sentOUT)
	fo = codecs.open(filename_template1.format(sent_num),'a','utf-8')
	fo.write(sentenceFinal)
	fo.close()
	
def build_debug_file2(sent_num, sentIN, sentOUT):
	""" Function that builds individual files with buggy inputs/outputs """
	sentenceFinal = build_debug_file(sentIN, sentOUT)
	fo = codecs.open(filename_template2.format(sent_num),'a','utf-8')
	fo.write(sentenceFinal)
	fo.close()
	
def build_debug_file3(sent_num, sentIN, sentOUT):
	""" Function that builds individual files with buggy inputs/outputs """
	sentenceFinal = build_debug_file(sentIN, sentOUT)
	fo = codecs.open(filename_template3.format(sent_num),'a','utf-8')
	fo.write(sentenceFinal)
	fo.close()
	
def build_debug_file4(sent_num, sentIN, sentOUT):
	""" Function that builds individual files with buggy inputs/outputs """
	sentenceFinal = build_debug_file(sentIN, sentOUT)
	fo = codecs.open(filename_template4.format(sent_num),'a','utf-8')
	fo.write(sentenceFinal)
	fo.close()

# For creating (on request) debug files
if len(sys.argv) > 5:
	create_output = sys.argv[5]
# Create output folder if does not exist
	output_folder1 = os.path.join(outputFolder, 'in-out_Disconnected')
	if not os.path.exists(output_folder1):
		os.makedirs(output_folder1)
	output_folder2 = os.path.join(outputFolder, 'in-out_MultipleIncoming')
	if not os.path.exists(output_folder2):
		os.makedirs(output_folder2)
	#output_folder3 = os.path.join(outputFolder, 'in-out_Disconnected_AND_Multiple_incoming_deprels')
	#if not os.path.exists(output_folder3):
	#	os.makedirs(output_folder3)
	output_folder4 = os.path.join(outputFolder, 'in-out_DuplicatedArguments')
	if not os.path.exists(output_folder4):
		os.makedirs(output_folder4)
		
	fdIN = codecs.open(filepathIN, 'r', 'utf-8')
	fileIN = fdIN.read()
	sentencesIN = fileIN.split('\n\n')

fdOUT = codecs.open(filepathOUT, 'r', str(input_file_encoding))
fileOUT = fdOUT.read()

# Split files into sentences
sentencesOUT = fileOUT.split('\n\n')

# Write output files 
fo_log = codecs.open(os.path.join(mainOutputFolder, 'log_deep_treeness.txt'), 'a', 'utf-8')

x = 0
structures_with_one_root = 0
structures_with_at_most_one_gov_per_node = 0
structures_with_no_double_dependencies = 0
structures_with_no_duplicated_args = 0
well_formed_trees = 0
well_formed_graphs = 0
no_root = 0
combo1 = 0
combo2 = 0
combo3 = 0
supercombo = 0
graphs_all_connected = 0

# -1 because last sentence of a conll file is empty (conll file ends with 2 linebreaks)
while x < len(sentencesOUT) - 1:
	sentenceOUT = sentencesOUT[x]
	sentenceIN = ''
	if create_output != '':
		sentenceIN = sentencesIN[x]
	lines = sentenceOUT.split('\n')
	
	root = 0
	double_gov = 0
	disconnected = 0
	duplicate_arg = 0
	for line in lines:
		if output_type == 'tree':
			# add up one for every line that contains a ROOT
			if (re.search('\t0\t_\tROOT\t', line) or re.search('\t0\tROOT\t', line)):
				root = root + 1
			# add up one for every line that contains info about duplicated DepRel
			if re.search('hasDuplicate=', line):
				duplicate_arg = duplicate_arg + 1
			# add up one for every line that contains a double dependency
			if '\t' in line:
				# Split lines into columns
				column_heads = line.split('\t')[6]
				if ',' in column_heads:
					double_gov = double_gov + 1
		elif output_type == 'graph':
			# add up one for every line that does not contain the connected attribute
			if not re.search('connect_check=OK', line):
				disconnected = disconnected + 1
			#check if some nodes receive several relations from the same node
			if '\t' in line:
				# Split lines into columns
				column_govs = line.split('\t')[6]
				if re.search(',', column_govs):
					govs = column_govs.split(',')
					unique_govs = []
					duplicated_govs = []
					for gov in govs:
						if gov not in unique_govs:
							unique_govs.append(gov)
						else:
							duplicated_govs.append(gov)
					if len(duplicated_govs) > 0:
						double_gov = double_gov + 1

	# CHECK TREES			
	if output_type == 'tree':
		# CHECK ROOTS
		# if there is only one root in the sentence, add up one to the tree counter
		if root == 1:
			structures_with_one_root = structures_with_one_root + 1
		elif root > 1:
			fo_log.write('Sentence ' + str(x) + ' has at least 2 roots\n')
			# if there is more than one root, retrieve original conll file in order to debug it in Buddy manually
			if create_output != '':
				build_debug_file1(x, sentenceIN, sentenceOUT)

		else:
			no_root = no_root + 1
			fo_log.write('Found no root in Sentence ' + str(x) + '\n')	
			if create_output != '':
				build_debug_file2(x, sentenceIN, sentenceOUT)
		
		if duplicate_arg == 0:
			structures_with_no_duplicated_args = structures_with_no_duplicated_args + 1
		elif duplicate_arg > 0:
			fo_log.write('Sentence ' + str(x) + ' has at least one duplicated argument number\n')
			if create_output != '':
				build_debug_file4(x, sentenceIN, sentenceOUT)
		
						
		# CHECK INCOMING RELATIONS
		if double_gov == 0:
			structures_with_at_most_one_gov_per_node = structures_with_at_most_one_gov_per_node + 1
		else:
			fo_log.write('Sentence ' + str(x) + ' has double dependencies between some nodes\n')
			if create_output != '':
				build_debug_file2(x, sentenceIN, sentenceOUT)
			
		# CHECK ALL
		if root > 1:
			if double_gov > 0:
				if duplicate_arg > 0:
					# every error happens in the structure
					supercombo = supercombo + 1
				else:
					# two roots and double governor only
					combo1 = combo1 + 1
				# if more than one root and at least one node has two incoming dependencies, all wrong!
				if create_output != '':
					build_debug_file3(x, sentenceIN, sentenceOUT)
			else:
				if duplicate_arg > 0:
					# two roots and duplicate argument only
					combo2 = combo2 + 1
		else:
			if double_gov > 0:
				if duplicate_arg > 0:
					# double governor and duplicate argument 
					combo3 = combo3 + 1
			else:
				if duplicate_arg == 0:
					well_formed_trees = well_formed_trees + 1

	# CHECK GRAPHS		
	elif output_type == 'graph':
		# CHECK DISCONNECTIONS
		if disconnected == 0:
			graphs_all_connected = graphs_all_connected + 1
		elif disconnected > 0:
			fo_log.write('Sentence ' + str(x) + ' has at least one disconnection\n')
			# if there is more than one root, retrieve original conll file in order to debug it in Buddy manually
			if create_output != '':
				build_debug_file1(x, sentenceIN, sentenceOUT)
		
		# CHECK DOUBLE EDGES BETWEEN NODES
		if double_gov == 0:
			structures_with_no_double_dependencies = structures_with_no_double_dependencies + 1
		else:
			fo_log.write('Sentence ' + str(x) + ' has node(s) with multiple incoming dependency\n')
			if create_output != '':
				build_debug_file2(x, sentenceIN, sentenceOUT)

		# CHECK BOTH
		if disconnected == 0 and double_gov == 0:
			# if there is only one root and one governor per node, it's all OK!
			well_formed_graphs = well_formed_graphs + 1
		elif disconnected > 0 and double_gov > 0:
			combo1 = combo1 + 1
			# if more than one root and at least one node has two incoming dependencies, all wrong!
			#if create_output != '':
			#	build_debug_file3(x, sentenceIN, sentenceOUT)
			
	x = x + 1	

if output_type == 'tree':
	BAD_all = x - well_formed_trees + no_root
	BAD_ROOT = x - (structures_with_one_root + no_root)
	BAD_UG = x - structures_with_at_most_one_gov_per_node
	BAD_DUPL = x - structures_with_no_duplicated_args

	fo_log.write('If not too frequent, duplicated argument numbers can just be ignored.\n')
	fo_log.write('-------INPUT--------\n')
	fo_log.write(str(filepathOUT) + '\n\n')
	#fo_log.write('------ DONE ! ------\n')
	fo_log.write('Found ' + str(x) + ' structures in input file\n')
	fo_log.write('  ' + str(well_formed_trees - no_root) + ' structures are well formed trees\n')
	fo_log.write('  ' + str(BAD_all) + ' structures are not\n')
	fo_log.write('  ------------------\n')
	fo_log.write('  ' + str(BAD_ROOT) + ' structures have at least 2 roots\n')
	fo_log.write('  ' + str(BAD_UG) + ' structures have at least one node with multiple incoming edges\n')
	fo_log.write('  ' + str(BAD_DUPL) + ' structures have at least one argument slot duplicated\n')
	#fo_log.write('  ' + str(int(combo1) + int(combo2) + int(combo3)) + ' structures have two problems\n')
	#fo_log.write('  ' + str(supercombo) + ' structures have all problems\n')
	fo_log.write('  ' + str(no_root) + ' structures have no root\n')
	fo_log.write('\n\n////////////////////////////////////////////////////////////////////\n\n')
	if x == well_formed_trees and not x == 0:
		print (colored(' -OK-', 'green'))
	else:
		print (colored(' -!!- Some ill-formed trees have been detected', 'red'))
	
elif output_type == 'graph':
	BAD_all = x - well_formed_graphs
	BAD_graph = x - graphs_all_connected
	BAD_UG = x - structures_with_no_double_dependencies
	fo_log.write('\n-------INPUT--------\n')
	fo_log.write(str(filepathOUT) +'\n\n' )
	#fo_log.write('------ DONE ! ------\n')
	fo_log.write('Found ' + str(x) + ' structures in input file\n')
	fo_log.write('  ' + str(well_formed_graphs) + ' structures are well formed graphs\n')
	fo_log.write('  ' + str(BAD_all) + ' structures are not\n')
	fo_log.write('  ------------------\n')
	fo_log.write('  ' + str(BAD_graph) + ' structures are disconnected\n')
	fo_log.write('  ' + str(BAD_UG) + ' structures have nodes with with double dependencies between them\n')
	#fo_log.write('  ' + str(combo1) + ' structures have both problems\n')
	fo_log.write('\n\n////////////////////////////////////////////////////////////////////\n\n')
	if x == well_formed_graphs and not x == 0:
		print (colored(' -OK-', 'green'))
	else:
		print (colored(' -!!- Some ill-formed graphs have been detected', 'red'))
	
fo_log.close()

def removeFolder(foldersToRemove):
	folders = list(os.walk(foldersToRemove))[1:]
	removed = 0
	for folder in folders:
		if not folder[2]:
			#os.rmdir(folder[0])
			try:
				shutil.rmtree(folder[0])
			except Exception as e:
				pass
			removed+=1
	if removed == len(folders):
		#os.rmdir(foldersToRemove)
		try:
			shutil.rmtree(foldersToRemove)
		except Exception as e:
			pass
		
removeFolder(outputFolder)