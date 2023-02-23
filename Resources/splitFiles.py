#!/usr/bin/env python
# -*- coding: utf-8 -*-
# authors: simon mille, alex shvets


import os
import sys
import codecs
import re
import shutil
from shutil import copyfile

import ntpath
ntpath.basename('a/b/c')

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

if len(sys.argv) < 5:
	sys.exit('!!! ARGUMENTS MISSING !!!\n1 = path to file to be checked\n2 = encoding of file to be checked (e.g. "utf-16BE")\n3 = number of structures per output file\n4 = cut input file once or every time the number defined for the previous parameter is reached ("first"/"all"\n(optional)')

# Applying this program to TIGER will trigger a problem with encoding due to "BOGOTÁ" ("Á" is apparently not UTF-8)


# Create output folder if does not exist
output_folder = sys.argv[5]
if os.path.exists(output_folder):
	try:
		shutil.rmtree(os.path.join(output_folder))
	except Exception as e:
		print(e)
os.makedirs(output_folder)

def zeroprefix(x, num_dig):
	return ''.join(['0' for zeroi in range(num_dig-len(str(x)))])

folderpath = sys.argv[1] #inputs
for filename in [f for f in os.listdir(folderpath) if '.conll' in f]:
	print(filename)
	filepath = os.path.join(folderpath, filename)
	# gather folder of input file; right split at the first separator
	#filename = path_leaf(filepath)

	fd = codecs.open(filepath, 'r', sys.argv[2])
	fileIn = fd.read()
	# Split file into sentences
	# normalise line breaks in original file
	if re.search('\r\n', fileIn):
		fileIn = re.subn('\r\n', '\n', fileIn)[0]
	elif re.search('\r', fileIn):
		fileIn = re.subn('\r', '\n', fileIn)[0]
	sentences = fileIn.split('\n\n')
	# remove last element of the list, which is a empty item that corresponds to the nothingness after the last two linebreaks
	if sentences[-1] == '':
		del sentences[-1]

	# Define template for output file names
	filename_split = filename.split('.')
	filename_template = os.path.join(output_folder,'%s_{0}.%s' % ('.'.join(filename_split[:-1]), filename_split[-1]))

	# get number of structures per file from command line
	out_num = sys.argv[3]
	sent_num = len(sentences)
	num_dig = len(str(sent_num))

	if sent_num > int(out_num):
		console2 = '-> Splitting '+ filename + '...'
		print(console2)
		# Write output files 
		# y is used to keep track of how many structures we put in each file
		y = 1
		# x is used to track the total number of structures, and to number the output files
		x = 0

		# if there is one file per structure, keep number the first file using "0"
		#zeroprefix = ''.join(['0' for zeroi in range(num_dig-len(str(x)))])
		#zeroprefix_end = ''.join(['0' for zeroi in range(num_dig-len(str(int(out_num) - 1)))])
		if out_num == '1':
			fo = codecs.open(filename_template.format(zeroprefix(x, num_dig)+x),'w', 'utf-8')
		# if there is more than one structure per file, name the first file with the range of structures it contains (0 to the number of structures per file)
		else:
			file_extension = zeroprefix(x, num_dig) + str(x)+'-'+ zeroprefix(int(out_num) - 1, num_dig) + str(int(out_num) - 1)
			fo = codecs.open(filename_template.format(file_extension),'w', 'utf-8')
			
		for sentence in sentences:
			sentenceFinal = sentence+'\n\n'
			# every time "y" reaches the number of desired structures, we build a new file
			if y == int(out_num):
				fo.write(sentenceFinal)
				x = x + int(out_num)
				x_end = min(x + int(out_num) - 1, sent_num-1)
				# if there is one file per structure, keep numbering the files using x
				# do not create another file if x reached the total number of structures
				
				if out_num == '1' and x != len(sentences):
					fo = codecs.open(filename_template.format(zeroprefix(x, num_dig)+x),'w', 'utf-8')
				# if there is more than one structure per file, name the file with the number of the first and last structure it contains
				elif not out_num == '1':
					# if we split the original file in more than 2, name the output file accordingly (for out_num = 100: 100-199, 200-299, etc.)
					if sys.argv[4] == 'all':
						file_extension = zeroprefix(x, num_dig)+str(x)+'-'+zeroprefix(x_end, num_dig)+str(x_end)
						fo = codecs.open(filename_template.format(file_extension),'w', 'utf-8')
					# if the original file is split into 2, number the second file with the maximum number of structures (for out_num = 100 and 739 structures, the last file is named 700-739)
					elif sys.argv[4] == 'first':
						file_extension = zeroprefix(x, num_dig)+str(x)+'-'+zeroprefix(len(sentences) - 1, num_dig)+str(len(sentences) - 1)
						fo = codecs.open(filename_template.format(file_extension),'w', 'utf-8')
				# reinitialize y for counting structures in the next file if we want more than two files
				if sys.argv[4] == 'all':
					y = 1
				# we don't reinitialize y if the user just wants 2 files as output, so this if loop is not used anymore, and no more new file is created.
				elif sys.argv[4] == 'first':
					y = y + 1
			# otherwise, we keep filling the already existing file (y can be smaller than int(out_num), or bigger when we don't reinitialize it
			else:
				fo.write(sentenceFinal)
				y = y + 1
		fo.close()
	else:
		copyfile(filepath, os.path.join(sys.argv[5], filename))
