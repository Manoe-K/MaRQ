import argparse
import re
from builtins import property

from sympy import subfactorial, primenu
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
IGNORED_PROPERTIES = ['http://www.w3.org/2000/01/rdf-schema#label',' https://schema.org/name', 'http://www.w3.org/2004/02/skos/core#prefLabel']
IGNORED_CLASSES = ['https://schema.org/Thing']

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
    return {'classes': get_classes(yarrrml),
            'properties':get_properties(yarrrml),
            'dataset': datasource,
            'template':get_templates(yarrrml)}

def get_templates(yarrrml):
    template_list = {'templates':{}}


    # get  yarrrml key of the yarrrml file
    mappings = get_keys(yarrrml, 'mappings')
    for mapping_name, mapping in mappings.items():
        # for each mapping

                predicate_objects= get_keys(mapping, 'predicateobjects')
                classes = []
                properties = []
                for predicate_object in predicate_objects:

                    # for each predicate object (list) in mapping
                    if predicate_object[0] == 'a' \
                            or predicate_object[0] == 'rdf:type' \
                            or predicate_object[0] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
                        classes.append(predicate_object[1])
                    else:
                        properties.append(predicate_object[0])


                tmp = re.search(r'(\(.+?)\)',mapping['subject'])
                reference = tmp.group(1)

                reference_replace =mapping['subject'].replace(reference,'(field1')
                template_list['templates'][reference_replace] = {
                    'classes': classes,  # classes associated to this template (if subject)
                    'properties': properties,  # properties associated to this template
                    'position': 'S',  # S or O
                   'references': {
                   'field1': '$'+reference+')'
                                }}

    return template_list


def get_classes(yarrrml):
    classes_list = {'classes': {}}


    # get  yarrrml key of the yarrrml file
    mappings = get_keys(yarrrml, 'mappings')
    for mapping_name, mapping in mappings.items():
        # for each mapping

        predicate_objects = get_keys(mapping, 'predicateobjects')
        classes = []
        properties = []
        for predicate_object in predicate_objects:

            # for each predicate object (list) in mapping
            if predicate_object[0] == 'a' \
                    or predicate_object[0] == 'rdf:type' \
                    or predicate_object[0] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
                classes.append(predicate_object[1])
            else:
                properties.append(predicate_object[0])
            tmp = re.search(r'(\(.+?)\)', mapping['subject'])
            reference = tmp.group(1)

            reference_replace = mapping['subject'].replace(reference, '(field1')
        for i in range(len(classes)):
            classes_list['classes'][classes[i]] = {
                  # classes associated to this template (if subject)
                'properties': properties,  # properties associated to this template
                'template': reference_replace
                }

    return classes_list


def get_properties(yarrrml):
    properties_list = {'properties': {}}

    # get  yarrrml key of the yarrrml file
    mappings = get_keys(yarrrml, 'mappings')
    for mapping_name, mapping in mappings.items():
        # for each mapping

        predicate_objects = get_keys(mapping, 'predicateobjects')
        classes = []
        properties = []
        references = []
        for predicate_object in predicate_objects:

            # for each predicate object (list) in mapping
            if predicate_object[0] == 'a' \
                    or predicate_object[0] == 'rdf:type' \
                    or predicate_object[0] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
                classes.append(predicate_object[1])
            else:
                properties.append(predicate_object[0])
                references.append(predicate_object[1])

            tmp = re.search(r'(\(.+?)\)', mapping['subject'])
            reference = tmp.group(1)

            reference_replace = mapping['subject'].replace(reference, '(field1')
        for i in range(len(properties)):
            properties_list['properties'][properties[i]] = {
                # classes associated to this template (if subject)
                'classes': classes,  # properties associated to this template
                'template': reference_replace,
                'references': references
            }

    return properties_list

def mapping_compare(yarrrml_map1, yarrrml_map2):
    common_classes = []
    common_properties = []
    datasource= []


    mapping_desc1 = mapping_list(yarrrml_map1)
    mapping_desc2 = mapping_list(yarrrml_map2)


    datasource.append(mapping_desc1['dataset'])
    datasource.append(mapping_desc2['dataset'])


    for classes2 in mapping_desc2['classes']:
        if classes2 in mapping_desc1['classes'] and classes2 not in IGNORED_CLASSES:
            common_classes.append(classes2)
    for properties2 in mapping_desc2['properties']:
        if properties2 in mapping_desc1['properties'] and properties2 not in IGNORED_PROPERTIES:
            common_properties.append(properties2)
    return {'classes': common_classes,
            'properties:': common_properties,
            'dataset': datasource

            }



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
#print(mapping_compare(yarrrml_mapping, yarrrml_mapping2))



print(get_properties(yarrrml_mapping))

        # get  yarrrml key of the yarrrml file

