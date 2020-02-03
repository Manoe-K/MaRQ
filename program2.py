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


def mapping_list(yarrrml):
    classes = []
    properties = []
    datasource = None
    # get  yarrrml key of the yarrrml file
    mappings = get_keys(yarrrml, 'mappings')
    for mapping_name, mapping in mappings.items():
        # for each mapping
        predicate_objects = get_keys(mapping, 'predicateobjects')
        for predicate_object in predicate_objects:
            # for each predicate object (list) in mapping
            if predicate_object[0] == 'a' \
                    or predicate_object[0] == 'rdf:type' \
                    or predicate_object[0] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
                classes.append(predicate_object[1])
            else:
                properties.append(predicate_object[0])
    for source_name, source in yarrrml_mapping['sources'].items():
        # for each mapping
        datasource = source[0]
    return {'classes': classes,
            'properties': properties,
            'dataset': datasource}



def mapping_compare(yarrrml_map1, yarrrml_map2):

    classes = []
    properties = []

    mapping1 = mapping_list(yarrrml_map1)
    mapping2 = mapping_list(yarrrml_map2)

    for mapping_name, mapping in mapping1.items():
        # for each mapping
        classesM1 =mapping1['classes']
        propertiesM1 = mapping1['properties']

    for mapping_name, mapping in mapping2.items():
    # for each mapping
        classesM2 = mapping2['classes']
        propertiesM2 = mapping2['properties']

    for classes2 in classesM2:
            for classes1 in classesM1:
                if classes2==classes1:
                    classes.append(classes2)




    for properties2 in propertiesM2:
            for properties1 in propertiesM1:
                if properties2==properties1:
                    properties.append(properties2)


    return {'classes': classes,
            'properties:': properties}



parser = argparse.ArgumentParser(description='Find federated queries for a federation.')
parser.add_argument('mapping', type=str, help='yarrrml mapping filepath')
parser.add_argument('mapping2', type=str, help='yarrrml mapping filepath')

args = parser.parse_args()

# open yarrrml file
stream = open(args.mapping)
stream2 = open(args.mapping2)

# loading the text file
yarrrml_mapping = load(stream, Loader=Loader)
yarrrml_mapping2 = load(stream2, Loader=Loader)
# method test
print(mapping_compare(yarrrml_mapping, yarrrml_mapping2))

