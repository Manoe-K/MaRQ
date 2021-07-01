import sys
import os
import re

import MaRQ
#import common_ontology as CO
#import create_queries as cq


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
        l_mapping.append(sys.argv[1] + '/' + mapping)


# execute MaRQ on every pair of mappings
MaRQ_results = []
for i in range(len(l_mapping)):
    for j in range(i+1, len(l_mapping)):
        MaRQ_results.append({
            'name1': l_names[i],
            'name2': l_names[j],
            'result': MaRQ.compare(l_mapping[i], l_mapping[j])})    # Create queries out of possible joins


# Print the results
for pair in range(len(MaRQ_results)):
    print()
    print('subject-subject:')
    for k in range(len(MaRQ_results[pair]['result']['subject-subject']['templates'])):
        print()
        print('M1:', MaRQ_results[pair]['name1'])
        print('M2:', MaRQ_results[pair]['name2'])
        print('Template :\t' + MaRQ_results[pair]['result']['subject-subject']['templates'][k])
        print('Jaccard index:\t' + str(MaRQ_results[pair]['result']['subject-subject']['Jaccard_index'][k]))
        for pattern in MaRQ_results[pair]['result']['subject-subject']['triple_patterns'][k]:
            print(MaRQ.triple_pattern_to_sparql(pattern))

    print()
    print()
    print('object-object:')
    for k in range(len(MaRQ_results[pair]['result']['object-object']['templates'])):
        print()
        print('M1:', MaRQ_results[pair]['name1'])
        print('M2:', MaRQ_results[pair]['name2'])
        print('Template :\t' + MaRQ_results[pair]['result']['object-object']['templates'][k])
        print('Jaccard index:\t' + str(MaRQ_results[pair]['result']['object-object']['Jaccard_index'][k]))
        for pattern in MaRQ_results[pair]['result']['object-object']['triple_patterns'][k]:
            print(MaRQ.triple_pattern_to_sparql(pattern))

    print()
    print()
    print('subject-object:')
    for k in range(len(MaRQ_results[pair]['result']['subject-object']['templates'])):
        print()
        print('M1:', MaRQ_results[pair]['name1'])
        print('M2:', MaRQ_results[pair]['name2'])
        print('Template :\t' + MaRQ_results[pair]['result']['subject-object']['templates'][k])
        print('Jaccard index:\t' + str(MaRQ_results[pair]['result']['subject-object']['Jaccard_index'][k]))
        for pattern in MaRQ_results[pair]['result']['subject-object']['triple_patterns'][k]:
            print(MaRQ.triple_pattern_to_sparql(pattern))

    print()
    print()
    print('object-subject:')
    for k in range(len(MaRQ_results[pair]['result']['object-subject']['templates'])):
        print('M1:', MaRQ_results[pair]['name1'])
        print('M2:', MaRQ_results[pair]['name2'])
        print('Template :\t' + MaRQ_results[pair]['result']['object-subject']['templates'][k])
        print('Jaccard index:\t' + str(MaRQ_results[pair]['result']['object-subject']['Jaccard_index'][k]))
        for pattern in MaRQ_results[pair]['result']['object-subject']['triple_patterns'][k]:
            print(MaRQ.triple_pattern_to_sparql(pattern))



