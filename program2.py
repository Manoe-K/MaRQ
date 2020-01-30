import re
import sys

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

stream = open(sys.argv[1])


yarrrml_mapping = load(stream, Loader=Loader)
# output = dump(data, Dumper=Dumper)

# mot=output.split( '\n' )


liste_properties = []
liste_classes = []
# les_autres = []
'''
for m in mot:
    if "[a," in m:
        n = re.search(r"a, '(.+?)']", m)
        if n:
            liste_classes.append(n.group(1))
    elif "['" in m:
        n = re.search(r"'(.+?)',", m)
        if n:
            liste_properties .append(n.group(1))
            #..  else:
            # les_autres.append(m)
            # print(len(liste_properties))
'''

for mapping_name, mapping in yarrrml_mapping['mappings'].items():
    # for each mapping
    print(mapping_name)
    predicate_objects = mapping['predicateobjects']
    for predicate_object in predicate_objects:
        # for each predicate object (list) in mapping
        print(predicate_object)

print(liste_classes)
print(liste_properties)
