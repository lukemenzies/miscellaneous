#!/usr/bin/env python3
# Script to extract persons and their associated educational institutions from a
# XML file, and create a CSV node attributes file.

import csv
import defusedxml.ElementTree as ET
from os import getcwd, listdir, path, remove

working_dir = getcwd()
for files in listdir(working_dir):
	print(f'  -  {files}')
tries = 0
while tries < 5:
	input_file = path.join(working_dir, input('What source file? '))
	if not path.exists(input_file):
		print('filename incorrect')
		tries += 1
	elif path.exists(input_file):
		tries = 5
columnames = ['id', 'school']
outfile = path.join(working_dir, 'Schools.csv')
with open(outfile, 'w') as outcsv:
	mwriter = csv.DictWriter(outcsv, fieldnames=columnames)
	mwriter.writeheader()
	with open(input_file, 'r') as infile:
		teitree = ET.parse(infile)
		teiroot = teitree.getroot()
		number_persons = 0
		number_rows = 0
		count = 0
		for child in teiroot.iter():
			if 'person' in child.tag and '{http://www.w3.org/XML/1998/namespace}id' in child.attrib:
				number_persons += 1
				nextrow = {ckey:' ' for ckey in columnames}
				nextrow['id'] = child.attrib.get('{http://www.w3.org/XML/1998/namespace}id')
				for sub1 in child.iter():
					if 'education' in sub1.tag:
						print(sub1.attrib)
						number_rows += 1
						# mwriter.writerow(nextrow)
				print(f'\rProgress: {number_persons} Persons', end='')
print(f'\nwrote {number_rows} rows')
