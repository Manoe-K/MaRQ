import sys
import re
import MaRQ
import common_ontology as CO

# read the script's arguments, each one being a mapping path
l_names   = []
l_mapping = []
for mapping in sys.argv[1:]:
    l_names.append(re.search(r'(\\[^\\]+?|/[^/]+?)$', mapping).group()[1:])
    l_mapping.append(mapping)

# Create queries out of possible joins
MaRQ_results = MaRQ.compare(l_mapping[0], l_mapping[1], l_names[0], l_names[1])

# Calculate the minimal common subject of each s2s joins
co = CO.get_common_ontologies(MaRQ_results)

# Print the results
print()
for k in range(len(l_names)):
    print('M'+str(k+1)+':', l_names[k])
print()
for line in MaRQ_results.splitlines():
    print(line)
print()
for dic in co:
    print(dic)
