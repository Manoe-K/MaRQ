import sparql
import sys
import re


# read the common_ontology.py output to create queries with the common classes
ontology_results = open(sys.argv[1], "r")
l_type = []
for line in ontology_results.readlines():

    if line[:2] == 'M1':                # mapping 1 name
        M1 = re.search(' .*?@', line).group()[1:-1]
        print(line[:-1])
    elif line[:2] == 'M2':              # mapping 2 name
        M2 = re.search(' .*?@', line).group()[1:-1]
        print(line[:-1])

    else:                               # types
        tempo = []
        for v in re.findall("'.*?'", line):
            tempo.append(v[1:-1])
        l_type.append(tempo)

for join in l_type:
    for type in join:
        q = ('SELECT ?s WHERE {' 
             'GRAPH ' + M1 + ' { ?s a ' + type + ' . }'
             'GRAPH ' + M2 + ' { ?s a ' + type + ' . }'
             '}'
             'LIMIT 1')
        print(q)
        #answer = sparql.query('localhost', q)