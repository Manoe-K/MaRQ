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
            if object in names:     # If object is a reference to a subject, we use the subject it refers to
                if object_to_search_with == mappings[object]['subject']:
                    predicates.append(predicate)
                    subjects.append(mapping['subject'])
            else:
                if object_to_search_with == object:
                    predicates.append(predicate)
                    subjects.append(mapping['subject'])
    return predicates, subjects


# attention la saturation crée trop de faux positif (car thing == thing)
# TODO: à changer: Ne test que le premier objet car les mappings sont saturés (temporaire)
def joinable(predicates1, predicates2, objects1, objects2):
    if predicates1[0] == 'a' or predicates1[0] == 'rdf:type':
        if predicates2[0] == 'a' or predicates2[0] == 'rdf:type':
            if objects1[0] == objects2[0]:
                return True
    return False
    #for i in range(len(predicates1)):
    #   if predicates1[i] == 'a' or predicates1[i] == 'rdf:type':
    #       for j in range(len(predicates2)):
    #           if predicates2[j] == 'a' or predicates1[j] == 'rdf:type':
    #               if objects1[i] == objects2[j]:
    #                    return True
    #return False

# function described in the paper:
# return the triple patterns created with Subject-Subject joins
def S2S_joinDetection(yarrrml1, yarrrml2):

    print('S2S')
    test_bgp = 0

    bgp = []
    id_subject = 0

    for subject1 in get_subjects(yarrrml1):
        for subject2 in get_subjects(yarrrml2):

            predicates1, objects1 = get_triplets_of_subject(yarrrml1, subject1)
            predicates2, objects2 = get_triplets_of_subject(yarrrml2, subject2)

            if subject1 == subject2 or joinable(predicates1, predicates2, objects1, objects2):
                id_subject = id_subject + 1
                id_object = 0
                triple_patterns = []

                for i in range(len(predicates1)):
                    if predicates1[i] in predicates2:
                        source = 'M1 M2'
                    else:
                        source = 'M1'
                    id_object = id_object+1

                    if predicates1[i] == 'rdf:type' or predicates1[i] == 'a':  # if the object is a type, we keep it for the pattern
                        triple_patterns.append(
                            ['?S' + str(id_subject) + ' ' + str(predicates1[i]) + ' ' + objects1[i], source])
                    else:
                        triple_patterns.append(
                            ['?S' + str(id_subject) + ' ' + str(predicates1[i]) + ' ?O' + str(id_object), source])

                for i in range(len(predicates2)):

                    #test if the (predicate, object) pair wasn't already used from the other mapping
                    used_pair = False
                    for j in range(len(predicates1)):
                        #if we have a common predicate that don't refer to a type object
                        if predicates2[i] == predicates1[j] and not (predicates2[i] == 'a' or predicates2[i] == 'rdf:type'):
                            used_pair = True
                        #if we have a common predicate and a common subject
                        elif predicates2[i] == predicates1[j] and objects2[i] == objects1[j]:
                            used_pair = True

                    if not used_pair:
                        source = 'M2'
                        id_object = id_object+1

                        if predicates2[i] == 'rdf:type' or predicates2[i] == 'a':  # if the object is a type, we keep it for the pattern
                            triple_patterns.append(
                                ['?S' + str(id_subject) + ' ' + str(predicates2[i]) + ' ' + objects2[i], source])
                        else:
                            triple_patterns.append(
                                ['?S' + str(id_subject) + ' ' + str(predicates2[i]) + ' ?O' + str(id_object), source])

                test_bgp = test_bgp + 1
                print(test_bgp, ': ', subject1, ' et ', subject2)
                bgp.append(triple_patterns)

    return bgp


def O2O_joinDetection(yarrrml1, yarrrml2):

    print('O2O')
    test_bgp = 0

    bgp = []
    id_object = 0

    for object1 in get_objects(yarrrml1):
        for object2 in get_objects(yarrrml2):

            predicates1, objects1 = get_triplets_of_subject(yarrrml1, object1)
            predicates2, objects2 = get_triplets_of_subject(yarrrml2, object2)

            join = False
            if predicates1 and predicates2:
                join = joinable(predicates1, predicates2, object1, object2)

            if object1 == object2 or join:
                id_object = id_object + 1
                id_subject = 0
                triple_patterns = []

                predicates1, subjects1 = get_triplets_of_object(yarrrml1, object1)
                predicates2, subjects2 = get_triplets_of_object(yarrrml2, object2)

                for i in range(len(predicates1)):
                    if predicates1[i] in predicates2:
                        source = 'M1 M2'
                    else:
                        source = 'M1'
                    id_subject = id_subject + 1

                    if predicates1[i] == 'rdf:type' or predicates1[i] == 'a':  # if the object is a type, we keep it for the pattern
                        triple_patterns.append(['?S' + str(id_subject) + ' ' + str(predicates1[i]) +' '+ object1, source])
                    else:
                        triple_patterns.append(['?S' + str(id_subject) + ' ' + str(predicates1[i]) + ' ?O'+ str(id_object), source])

                for i in range(len(predicates2)):
                    if predicates2[i] not in predicates1:
                        source = 'M2'
                        id_subject = id_subject + 1
                        if predicates2[i] == 'rdf:type' or predicates2[i] == 'a':  # if the object is a type, we keep it for the pattern
                            triple_patterns.append(
                                ['?S' + str(id_subject) + ' ' + str(predicates2[i]) +' '+ object2, source])
                        else:
                            triple_patterns.append(
                                ['?S' + str(id_subject) + ' ' + str(predicates2[i]) + ' ?O' + str(id_object), source])

                test_bgp = test_bgp + 1
                print(test_bgp, ': ', object1, ' et ', object2)
                bgp.append(triple_patterns)

    return bgp


def S2O_joinDetection(yarrrml1, yarrrml2):

    print('S2O')
    test_bgp = 0

    bgp = []
    id_template = 0

    for subject in get_subjects(yarrrml1):
        for object in get_objects(yarrrml2):

            predicates1, objects1 = get_triplets_of_subject(yarrrml1, subject)
            predicates2, objects2 = get_triplets_of_subject(yarrrml2, object)

            join = False
            if predicates1 and predicates2:
                join = joinable(predicates1, predicates2, subject, object)

            if subject == object or join:
                id_template = id_template + 1
                id_filler = 0
                triple_patterns = []

                predicates2, objects2 = get_triplets_of_object(yarrrml2, object)

                for i in range(len(predicates1)):
                    if predicates1[i] in predicates2:
                        source = 'M1 M2'
                    else:
                        source = 'M1'
                    id_filler = id_filler + 1
                    if predicates1[i] == 'rdf:type' or predicates1[i] == 'a':  # if the object is a type, we keep it for the pattern
                        triple_patterns.append(
                            ['?T' + str(id_template) + ' ' + str(predicates1[i]) + ' ' + objects1[i], source])
                    else:
                        triple_patterns.append(
                            ['?T' + str(id_template) + ' ' + str(predicates1[i]) + ' ?F' + str(id_filler), source])
                for i in range(len(predicates2)):
                    if predicates2[i] in predicates1:
                        source = 'M1 M2'
                    else:
                        source = 'M2'
                    id_filler = id_filler + 1
                    triple_patterns.append(['?F' + str(id_filler) + ' ' + str(predicates2[i]) + ' ?T' + str(id_template), source])

                test_bgp = test_bgp + 1
                print(test_bgp, ': ', subject, ' et ', object)
                bgp.append(triple_patterns)

    return bgp


def compare(yarrrml1, yarrrml2):
    return {'subject-subject': S2S_joinDetection(yarrrml1, yarrrml2),
            'object-object':   O2O_joinDetection(yarrrml1, yarrrml2),
            'subject-object':  S2O_joinDetection(yarrrml1, yarrrml2),
            'object-subject':  S2O_joinDetection(yarrrml2, yarrrml1)}


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
