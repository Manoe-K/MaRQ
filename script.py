import sys
import os
import re

import MaRQ
import common_ontology as CO
import create_queries as cq


if len(sys.argv[1:]) > 1:               # read the script's arguments, each one being a mapping path
    l_names   = []
    l_mapping = []

    for mapping in sys.argv[1:]:
        l_names.append(re.search(r'(\\[^\\]+?|/[^/]+?)$', mapping).group()[1:])
        l_mapping.append(mapping)

elif len(sys.argv[1:]) == 1:            # read the script's argument, being the directory where all mappings are found
    l_names   = []
    l_mapping = []

    mappings_directory = os.listdir(sys.argv[1])
    for mapping in mappings_directory:
        l_names.append(mapping)
        print(mapping)
        l_mapping.append(sys.argv[1] + '/' + mapping)


# execute MaRQ on every pair of mappings
MaRQ_results = []
for i in range(len(l_mapping)):
    for j in range(i+1, len(l_mapping)):
        MaRQ_results.append({
            'name1': l_names[i],
            'name2': l_names[j],
            'result': MaRQ.compare(l_mapping[i], l_mapping[j])})    # Create queries out of possible joins


# Calculate the minimal common subject of each pair of mappings, for each of there s2s joins
common_types = []
for pair in MaRQ_results:
    common_types.append(CO.get_common_ontologies(pair['result']))

for i in range(len(MaRQ_results)):
    print(cq.create_queries(MaRQ_results[i], common_types[i]))


"""
# Print the results
for k in range(len(MaRQ_results)):
    print()
    print('M1:', MaRQ_results[k]['name1'])
    print('M2:', MaRQ_results[k]['name2'])

    print()
    for list in co:
        for set in list:
            print(set)
    print()
"""