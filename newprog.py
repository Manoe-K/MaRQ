import sys
from yaml import load
import re
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


# Return all of the subject templates of a mapping
def get_subjects(yarrrml):
    mappings = get_keys(yarrrml, 'mappings')

    subjects = set()
    for mapping_name, mapping in mappings.items():
        subjects.add(yarrrml['mappings'][mapping_name]['subject'])

    return subjects


# Return all of the object templates of a mapping
def get_objects(yarrrml):
    mappings = get_keys(yarrrml, 'mappings')

    names = set()
    for mapping_name, mapping in mappings.items():
        names.add(mapping_name)

    objects = set()
    for mapping_name, mapping in mappings.items():
        predicate_objects = get_keys(mapping, 'predicateobjects')
        for predicate, object in predicate_objects:
            if object in names:     # If object is a reference, we use the subject it refers to
                objects.add(mappings[object]['subject'])
            else:
                objects.add(object)

    return objects


# Return all of the predicate of a mapping in relation to a given subject
def get_predicates_of_subject(yarrrml, subject):
    mappings = get_keys(yarrrml, 'mappings')

    predicates = set()
    for mapping_name, mapping in mappings.items():
        if subject == mappings[mapping_name]['subject']:
            predicate_objects = get_keys(mapping, 'predicateobjects')
            for predicate, object in predicate_objects:
                predicates.add(predicate)

    return predicates


# Return all of the predicate of a mapping in relation to a given object
def get_predicates_of_object(yarrrml, object_to_search):
    mappings = get_keys(yarrrml, 'mappings')

    names = set()
    for mapping_name, mapping in mappings.items():
        names.add(mapping_name)

    predicates = set()
    for mapping_name, mapping in mappings.items():
        predicate_objects = get_keys(mapping, 'predicateobjects')
        for predicate, object in predicate_objects:
            if object in names:     # If object is a reference, we use the subject it refers to
                if object_to_search == mappings[object]['subject']:
                    predicates.add(predicate)
            else:
                if object_to_search == object:
                    predicates.add(predicate)

    return predicates


def get_join_subject_subject(yarrrml1, yarrrml2):

    bgp = []
    id_subject = 0
    id_object = 0

    for subject1 in get_subjects(yarrrml1):
        for subject2 in get_subjects(yarrrml2):

            if subject1 == subject2:
                id_subject = id_subject+1
                triple_patterns = []
                predicates1 = get_predicates_of_subject(yarrrml1, subject1)
                predicates2 = get_predicates_of_subject(yarrrml2, subject1)

                for predicate in predicates1:
                    if predicate in predicates2:
                        source = 'M1 M2'
                    else:
                        source = 'M1'
                    id_object = id_object+1
                    triple_patterns.append(['?S'+str(id_subject)+' '+str(predicate)+' ?O'+str(id_object), source])
                for predicate in predicates2:
                    if predicate not in predicates1:
                        source = 'M2'
                        id_object = id_object+1
                        triple_patterns.append(['?S'+str(id_subject)+' '+str(predicate)+' ?O'+str(id_object), source])
                bgp.append(triple_patterns)

    return bgp


def get_join_object_object(yarrrml1, yarrrml2):

    bgp = []
    id_subject = 0
    id_object = 0

    for object1 in get_objects(yarrrml1):
        for object2 in get_objects(yarrrml2):

            if object1 == object2:
                id_object = id_object+1
                triple_patterns = []
                predicates1 = get_predicates_of_object(yarrrml1, object1)
                predicates2 = get_predicates_of_object(yarrrml2, object1)
                for predicate in predicates1:
                    if predicate in predicates2:
                        source = 'M1 M2'
                    else:
                        source = 'M1'
                    id_subject = id_subject+1
                    if predicate == 'rdf:type' or predicate == 'a': # if the object is a type, we keep it for the pattern
                        triple_patterns.append(['?S'+str(id_subject)+' '+str(predicate)+' '+object1, source])
                    else:
                        triple_patterns.append(['?S'+str(id_subject)+' '+str(predicate)+' ?O'+str(id_object), source])
                for predicate in predicates2:
                    if predicate not in predicates1:
                        source = 'M2'
                        id_subject = id_subject+1
                        triple_patterns.append(['?S'+str(id_subject)+' '+str(predicate)+' ?O'+str(id_object), source])
                bgp.append(triple_patterns)

    return bgp


def get_join_subject_object(yarrrml1, yarrrml2):
    bgp = []
    id_filler = 0
    id_template = 0

    for subject in get_subjects(yarrrml1):
        for object in get_objects(yarrrml2):

            if subject == object:
                id_template = id_template + 1
                triple_patterns = []
                predicates1 = get_predicates_of_subject(yarrrml1, subject)
                predicates2 = get_predicates_of_object(yarrrml2, subject)
                for predicate in predicates1:
                    if predicate in predicates2:
                        source = 'M1 M2'
                    else:
                        source = 'M1'
                    id_filler = id_filler + 1
                    triple_patterns.append(['?T' + str(id_template) + ' ' + str(predicate) + ' ?O' + str(id_filler), source])
                for predicate in predicates2:
                    if predicate in predicates1:
                        source = 'M1 M2'
                    else:
                        source = 'M2'
                    id_filler = id_filler + 1
                    triple_patterns.append(['?S' + str(id_filler) + ' ' + str(predicate) + ' ?T' + str(id_template), source])
                bgp.append(triple_patterns)

    return bgp


# Main
list_mappings = []
for yarrrml in sys.argv[1:]:
    list_mappings.append(load(open('Mappings/'+yarrrml), Loader=Loader))

for bgp in get_join_subject_object(list_mappings[0], list_mappings[1]):
    print('Bgp:')
    for tp in bgp:
        print(tp)
