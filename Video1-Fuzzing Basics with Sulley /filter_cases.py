# This script will take the relevant cases and extract these from all conducted use cases.

datafile = 'pcman_all_cases.txt'
inputfile = 'pcman_relevant_cases.txt'
result = open('pcman_relevant.txt','a+')

relevant = open(inputfile)
all = open(datafile)
"""
for line in all:
	relevant = open(inputfile)
	for rel in relevant:
		search_case = "=%s:" % rel.strip()
		if search_case in line:
			result.write(line)
	relevant.close()
result.close()"""

for line in all:
	with open(inputfile) as relevant:
		for rel in relevant:
			search_case = "=%s:" % rel.strip()
			if search_case in line:
				result.write(line)
result.close()