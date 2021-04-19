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
        subjects.add(get_keys(yarrrml, 'mappings')[mapping_name]['subject'])

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
def get_triplets_of_subject(yarrrml, subject_to_search_with):
    mappings = get_keys(yarrrml, 'mappings')

    predicates = []
    objects = []
    for mapping_name, mapping in mappings.items():
        if subject_to_search_with == mappings[mapping_name]['subject']:
            predicate_objects = get_keys(mapping, 'predicateobjects')
            for predicate, object in predicate_objects:
                predicates.append(predicate)
                objects.append(object)
    return predicates, objects


# Return all of the predicate of a mapping in relation to a given object
def get_triplets_of_object(yarrrml, object_to_search_with):
    mappings = get_keys(yarrrml, 'mappings')

    names = set()
    for mapping_name, mapping in mappings.items():
        names.add(mapping_name)

    predicates = []
    subjects = []
    for mapping_name, mapping in mappings.items():
        predicate_objects = get_keys(mapping, 'predicateobjects')
        for predicate, object in predicate_objects:
            if object in names:     # If object is a reference, we use the subject it refers to
                if object_to_search_with == mappings[object]['subject']:
                    predicates.append(predicate)
                    subjects.append(mapping['subject'])
            else:
                if object_to_search_with == object:
                    predicates.append(predicate)
                    subjects.append(mapping['subject'])
    return predicates, subjects


def equals(predicates1, predicates2, objects1, objects2):
    for i in range(len(predicates1)):
        if predicates1[i] == 'a' or predicates1[i] == 'rdf:type':
            for j in range(len(predicates2)):
                if predicates2[j] == 'a' or predicates2[j] == 'rdf:type':
                    if objects1[i] == objects2[j]:
                        return True
    return False


def get_join_subject_subject(yarrrml1, yarrrml2):

    bgp = []
    id_subject = 0
    id_object = 0

    for subject1 in get_subjects(yarrrml1):
        for subject2 in get_subjects(yarrrml2):

            predicates1, objects1 = get_triplets_of_subject(yarrrml1, subject1)
            predicates2, objects2 = get_triplets_of_subject(yarrrml2, subject2)

            if subject1 == subject2 or equals(predicates1, predicates2, objects1, objects2):
                id_subject = id_subject+1
                triple_patterns = []

                for i in range(len(predicates1)):
                    if predicates1[i] in predicates2:
                        source = 'M1 M2'
                    else:
                        source = 'M1'
                    id_object = id_object+1
                    triple_patterns.append(['?S'+str(id_subject)+' '+str(predicates1[i])+' ?O'+str(id_object), source])
                for i in range(len(predicates2)):
                    if predicates2[i] not in predicates1:
                        source = 'M2'
                        id_object = id_object+1
                        triple_patterns.append(['?S'+str(id_subject)+' '+str(predicates2[i])+' ?O'+str(id_object), source])
                bgp.append(triple_patterns)

    return bgp


def get_join_object_object(yarrrml1, yarrrml2):

    bgp = []
    id_subject = 0
    id_object = 0

    for object1 in get_objects(yarrrml1):
        for object2 in get_objects(yarrrml2):

            predicates1, objects1 = get_triplets_of_subject(yarrrml1, object1)
            predicates2, objects2 = get_triplets_of_subject(yarrrml2, object2)

            equal = False
            if predicates1 and predicates2:
                equal = equals(predicates1, predicates2, object1, object2)

            if object1 == object2 or equal:
                id_object = id_object+1
                triple_patterns = []

                for i in range(len(predicates1)):
                    if predicates1[i] in predicates2:
                        source = 'M1 M2'
                    else:
                        source = 'M1'
                    id_subject = id_subject+1
                    if predicates1[i] == 'rdf:type' or predicates1[i] == 'a': # if the object is a type, we keep it for the pattern
                        triple_patterns.append(['?S'+str(id_subject)+' '+str(predicates1[i])+' '+object1, source])
                    else:
                        triple_patterns.append(['?S'+str(id_subject)+' '+str(predicates1[i])+' ?O'+str(id_object), source])
                for i in range(len(predicates2)):
                    if predicates2[i] not in predicates1:
                        source = 'M2'
                        id_subject = id_subject+1
                        triple_patterns.append(['?S'+str(id_subject)+' '+str(predicates2[i])+' ?O'+str(id_object), source])
                bgp.append(triple_patterns)

    return bgp


def get_join_subject_object(yarrrml1, yarrrml2):
    bgp = []
    id_filler = 0
    id_template = 0

    for subject in get_subjects(yarrrml1):
        for object in get_objects(yarrrml2):

            predicates1, objects1 = get_triplets_of_subject(yarrrml1, subject)
            predicates2, objects2 = get_triplets_of_subject(yarrrml2, object)

            equal = False
            if predicates1 and predicates2:
                equal = equals(predicates1, predicates2, subject, object)

            if subject == object or equal:
                id_template = id_template + 1
                triple_patterns = []

                for i in range(len(predicates1)):
                    if predicates1[i] in predicates2:
                        source = 'M1 M2'
                    else:
                        source = 'M1'
                    id_filler = id_filler + 1
                    triple_patterns.append(['?T' + str(id_template) + ' ' + str(predicates1[i]) + ' ?F' + str(id_filler), source])
                for i in range(len(predicates2)):
                    if predicates2[i] in predicates1:
                        source = 'M1 M2'
                    else:
                        source = 'M2'
                    id_filler = id_filler + 1
                    triple_patterns.append(['?F' + str(id_filler) + ' ' + str(predicates2[i]) + ' ?T' + str(id_template), source])
                bgp.append(triple_patterns)

    return bgp


def compare(yarrrml1, yarrrml2):
    return {'subject-subject': get_join_subject_subject(yarrrml1, yarrrml2),
            'object-object': get_join_subject_subject(yarrrml1, yarrrml2),
            'subject-object': get_join_subject_subject(yarrrml1, yarrrml2),
            'object-subject': get_join_subject_subject(yarrrml2, yarrrml1)}


def print_result(results):
    i = 1
    print()
    print('S-S')
    for bgp in results['subject-subject']:
        print()
        print('bgp', i)
        i = i+1
        for queries in bgp:
            print(queries)
    print()
    print()
    print('O-O')
    for bgp in results['object-object']:
        print()
        print('bgp', i)
        i = i+1
        for queries in bgp:
            print(queries)
    print()
    print()
    print('S-O')
    for bgp in results['subject-object']:
        print()
        print('bgp', i)
        i = i+1
        for queries in bgp:
            print(queries)
    print()
    print()
    print('O-S')
    for bgp in results['object-subject']:
        print()
        print('bgp', i)
        i = i+1
        for queries in bgp:
            print(queries)


# Main
list_mappings = []
for yarrrml in sys.argv[1:]:
    list_mappings.append(load(open(yarrrml), Loader=Loader))

print_result(compare(list_mappings[0], list_mappings[1]))