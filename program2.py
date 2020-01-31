import argparse

from yaml import load

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

YARRRML_KEYS = {
    'mappings': ['mappings', 'mapping'],
    'predicateobjects': ['predicateobjects', 'predicateobject', 'po'],
    'predicates': ['predicates', 'predicate', 'p'],
    'objects': ['objects', 'object', 'o'],
    'value': ['value', 'v']
}


def get_keys(d, key):
    # Get the value of the first key in corresponding YARRRML_KEYS that match a key in d
    if key in YARRRML_KEYS:
        for yarrrml_key in YARRRML_KEYS[key]:
            if yarrrml_key in d:
                return d[key]
    return {}


liste_properties = []
liste_classes = []


#
def mapping_list(yarrrml):
    # get  yarrrml key of the yarrrml file
    key = list(yarrrml_mapping.keys())[0]

    liste = get_keys(yarrrml_mapping, key)
    for mapping_name, mapping in liste.items():
        # for each mapping
        # print(mapping_name)
        predicate_objects = mapping[list(mapping.keys())[0]]

        for predicate_object in predicate_objects:
            # for each predicate object (list) in mapping
            # print(predicate_object)

            if predicate_object[0] == 'a' or predicate_object[0] == 'rdf:type':
                liste_classes.append(predicate_object[1])
            elif len(predicate_object) == 3:
                liste_properties.append(predicate_object[0])
                liste_properties.append(predicate_object[2])
            else:
                liste_properties.append(predicate_object[0])

    return {'classes': liste_classes, 'properties:': liste_properties}


parser = argparse.ArgumentParser(description='Find federated queries for a federation.')
parser.add_argument('mapping', type=str, help='yarrrml mapping filepath')
args = parser.parse_args()

# open yarrrml file
stream = open(args.mapping)




# loading the text file
yarrrml_mapping = load(stream, Loader=Loader)

#method test
print(mapping_list(yarrrml_mapping))


# test = {'classes': liste_classes,
#  'properties:': liste_properties}
