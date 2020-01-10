#!/usr/bin/env python3
# Script to extract persons and their associates from XML file
# and create CSV nodes and edges file.

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
infile = open(input_file, 'r')
teitree = ET.parse(infile)
teiroot = teitree.getroot()
number_persons = 0
number_rows = 0
row_list = []
columnames = ['node1', 'node2', 'relationship']
count = 0
for child in teiroot.iter():
	if 'person' in child.tag and '{http://www.w3.org/XML/1998/namespace}id' in child.attrib:
		number_persons += 1
		nextrow = {ckey:' ' for ckey in columnames}
		nextrow['node1'] = child.attrib.get('{http://www.w3.org/XML/1998/namespace}id')
		for sub1 in child.iter():
			if 'note' in sub1.tag and 'type' in sub1.attrib:
				if sub1.attrib['type'] == 'associates':
					nextrow['relationship'] = 'associate'
					for sub2 in sub1.iter():
						if not sub2.attrib.get('key') is None:
							number_rows += 1
							nextrow['node2'] = sub2.attrib.get('key')
							row_list.append(nextrow)
		print(f'\rProgress: {number_persons} Persons', end='')
infile.close()
outfile = path.join(working_dir, path.splitext(path.basename(input_file))[0] + '_list.csv')
itemrows = 0
with open(outfile, 'w') as outcsv:
	mwriter = csv.DictWriter(outcsv, fieldnames=columnames)
	mwriter.writeheader()
	for newrow in row_list:
		itemrows += 1
		mwriter.writerow(newrow)
print(f'\n {itemrows} rows')
