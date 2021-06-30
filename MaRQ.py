import sys
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
        for predicate_object in predicate_objects:
            if predicate_object[1] in names:     # If object is a reference, we use the subject it refers to
                objects.add(mappings[predicate_object[1]]['subject'])
            else:
                objects.add(predicate_object[1])

    return objects


# Return all of the predicate of a mapping in relation to a given subject
def get_triplets_of_subject(yarrrml, subject_to_search_with):
    mappings = get_keys(yarrrml, 'mappings')

    predicates = []
    objects = []
    for mapping_name, mapping in mappings.items():
        if subject_to_search_with == mappings[mapping_name]['subject']:
            predicate_objects = get_keys(mapping, 'predicateobjects')
            for predicate_object in predicate_objects:
                predicates.append(predicate_object[0])
                objects.append(predicate_object[1])
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
        for predicate_object in predicate_objects:
            if predicate_object[1] in names:     # If object is a reference to a subject, we use the subject it refers to
                if object_to_search_with == mappings[predicate_object[1]]['subject']:
                    predicates.append(predicate_object[0])
                    subjects.append(mapping['subject'])
            else:
                if object_to_search_with == predicate_object[1]:
                    predicates.append(predicate_object[0])
                    subjects.append(mapping['subject'])
    return predicates, subjects


# attention la saturation cree trop de faux positif (car thing == thing)
def joinable(predicates1, predicates2, objects1, objects2):

    set1 = set()
    set2 = set()

    print()

    for i in range(len(objects1)):
        if predicates1[i] == 'a' or predicates1[i] == 'rdf:type':
            set1.add(objects1[i])
    for i in range(len(objects2)):
        if predicates2[i] == 'a' or predicates2[i] == 'rdf:type':
            set2.add(objects2[i])

    print('set1')
    print(set1)
    print('set2')
    print(set2)
    print('set1 n set2')
    print(set1.intersection(set2))

    Jaccard = len(set1.intersection(set2))/len(set1.union(set2))

    print('Jaccard')
    print(Jaccard)

    return Jaccard > 0


# return the triple patterns created with Subject-Subject joins
def S2S_joinDetection(yarrrml1, yarrrml2):

    #print('S2S')
    #test_bgp = 0

    bgp = []
    list_tp_per_template_count = []
    tp_M1_count = 0
    tp_M2_count = 0

    id_subject = 0

    for subject1 in get_subjects(yarrrml1):
        for subject2 in get_subjects(yarrrml2):

            predicates1, objects1 = get_triplets_of_subject(yarrrml1, subject1)
            predicates2, objects2 = get_triplets_of_subject(yarrrml2, subject2)

            if subject1 == subject2 or joinable(predicates1, predicates2, objects1, objects2):
                id_subject = id_subject + 1
                id_object = 0
                triple_patterns = []
                tp_per_template_count = 0

                for i in range(len(predicates1)):
                    if predicates1[i] in predicates2:
                        if predicates1[i] == 'a' or predicates1[i] == 'rdf:thing':
                            if objects1[i] in objects2:
                                source = 'M1 M2'
                            else:
                                source = 'M1'
                                tp_M1_count += 1
                        else:
                            source = 'M1 M2'
                    else:
                        source = 'M1'
                        tp_M1_count += 1

                    tp_per_template_count += 1

                    if predicates1[i] == 'rdf:type' or predicates1[i] == 'a':  # if the object is a type, we keep it for the pattern
                        triple_patterns.append(
                            {'subject':    '?S' + str(id_subject),
                             'predicate':   str(predicates1[i]),
                             'object':     objects1[i],
                             'source':     source})
                    else:
                        id_object = id_object+1
                        triple_patterns.append(
                            {'subject':    '?S' + str(id_subject),
                             'predicate':   str(predicates1[i]),
                             'object':     '?O' + str(id_object),
                             'source':     source})

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
                        tp_M2_count += 1

                        tp_per_template_count += 1

                        if predicates2[i] == 'rdf:type' or predicates2[i] == 'a':  # if the object is a type, we keep it for the pattern
                            triple_patterns.append(
                                {'subject':    '?S' + str(id_subject),
                                 'predicate':   str(predicates2[i]),
                                 'object':     objects2[i],
                                 'source':     source})
                        else:
                            id_object = id_object+1
                            triple_patterns.append(
                                {'subject':    '?S' + str(id_subject),
                                 'predicate':   str(predicates2[i]),
                                 'object':     '?O' + str(id_object),
                                 'source':     source})

                #test_bgp = test_bgp + 1
                #print(test_bgp, ': ', subject1, ' et ', subject2)
                list_tp_per_template_count.append(tp_per_template_count)
                bgp.append(triple_patterns)

    return {'triple_patterns': bgp,
            'Number_of_triple_patterns': list_tp_per_template_count,
            'Number_of_triple_patterns_from_M1': tp_M1_count,
            'Number_of_triple_patterns_from_M2': tp_M2_count}


# return the triple patterns created with Object-Object joins
def O2O_joinDetection(yarrrml1, yarrrml2):

    #print('O2O')
    #test_bgp = 0

    bgp = []
    list_tp_per_template_count = []
    tp_M1_count = 0
    tp_M2_count = 0

    id_object = 0

    for object1 in get_objects(yarrrml1):
        for object2 in get_objects(yarrrml2):

            predicates1, objects1 = get_triplets_of_subject(yarrrml1, object1)
            predicates2, objects2 = get_triplets_of_subject(yarrrml2, object2)

            join = False
            if predicates1 and predicates2:
                join = joinable(predicates1, predicates2, objects1, objects2)

            if object1 == object2 or join:
                id_object = id_object + 1
                id_subject = 0
                triple_patterns = []
                tp_per_template_count = 0

                predicates1, subjects1 = get_triplets_of_object(yarrrml1, object1)
                predicates2, subjects2 = get_triplets_of_object(yarrrml2, object2)

                for i in range(len(predicates1)):
                    if predicates1[i] in predicates2:
                        source = 'M1 M2'
                    else:
                        source = 'M1'
                        tp_M1_count += 1

                    # test if the triplet pattern isn't already in the list
                    already_in = False
                    k = 0
                    while k < len(triple_patterns) and not already_in:
                        if predicates1[i] == triple_patterns[k]['predicate']:
                            if predicates1[i] == 'rdf:type' or predicates1[i] == 'a':
                                if object1 == triple_patterns[k]['object']:
                                    already_in = True
                            else:
                                already_in = True
                        k += 1

                    if not already_in:
                        tp_per_template_count += 1
                        id_subject = id_subject + 1

                        if predicates1[i] == 'rdf:type' or predicates1[i] == 'a':  # if the object is a type, we keep it for the pattern
                            triple_patterns.append(
                                {'subject':    '?S' + str(id_subject),
                                 'predicate':   str(predicates1[i]),
                                 'object':     object1,
                                 'source':     source})
                        else:
                            triple_patterns.append(
                                {'subject':    '?S' + str(id_subject),
                                 'predicate':   str(predicates1[i]),
                                 'object':     '?O' + str(id_object),
                                 'source':     source})

                for i in range(len(predicates2)):
                    if predicates2[i] not in predicates1:
                        source = 'M2'
                        tp_M2_count += 1

                        tp_per_template_count += 1
                        id_subject = id_subject + 1

                        if predicates2[i] == 'rdf:type' or predicates2[i] == 'a':  # if the object is a type, we keep it for the pattern
                            pass
                            """triple_patterns.append(
                                {'subject':    '?S' + str(id_subject),
                                 'predicate':   str(predicates2[i]),
                                 'object':     object2,
                                 'source':     source})"""
                        else:
                            triple_patterns.append(
                                {'subject':    '?S' + str(id_subject),
                                 'predicate':   str(predicates2[i]),
                                 'object':     '?O' + str(id_object),
                                 'source':     source})

                #test_bgp = test_bgp + 1
                #print(test_bgp, ': ', object1, ' et ', object2)
                list_tp_per_template_count.append(tp_per_template_count)
                bgp.append(triple_patterns)

    return {'triple_patterns': bgp,
            'Number_of_triple_patterns': list_tp_per_template_count,
            'Number_of_triple_patterns_from_M1': tp_M1_count,
            'Number_of_triple_patterns_from_M2': tp_M2_count}


# return the triple patterns created with Subject-Object joins
# reversed act as the mappings are inverted, changing the 'source' variable, thus allowing to do Object-Subject joins
def S2O_joinDetection(yarrrml1, yarrrml2, reversed=False):

    #print('S2O')
    #test_bgp = 0

    bgp = []
    list_tp_per_template_count = []
    tp_M1_count = 0
    tp_M2_count = 0

    id_template = 0

    for subject in get_subjects(yarrrml1):
        for object in get_objects(yarrrml2):

            predicates1, objects1 = get_triplets_of_subject(yarrrml1, subject)
            predicates2, objects2 = get_triplets_of_subject(yarrrml2, object)

            join = False
            if predicates1 and predicates2:
                join = joinable(predicates1, predicates2, objects1, objects2)

            if subject == object or join:
                id_template = id_template + 1
                id_filler = 0
                triple_patterns = []
                tp_per_template_count = 0

                predicates2, objects2 = get_triplets_of_object(yarrrml2, object)

                for i in range(len(predicates1)):
                    if predicates1[i] in predicates2:
                        if predicates1[i] == 'a' or predicates1[i] == 'rdf:thing':
                            if objects1[i] in objects2:
                                source = 'M1 M2'
                            else:
                                if not reversed:
                                    source = 'M1'
                                    tp_M1_count += 1
                                else:
                                    source = 'M2'
                                    tp_M2_count += 1
                        else:
                            source = 'M1 M2'
                    else:
                        if not reversed:
                            source = 'M1'
                            tp_M1_count += 1
                        else:
                            source = 'M2'
                            tp_M2_count += 1

                    tp_per_template_count += 1

                    if predicates1[i] == 'rdf:type' or predicates1[i] == 'a':  # if the object is a type, we keep it for the pattern
                        triple_patterns.append(
                            {'subject':    '?T' + str(id_template),
                             'predicate':   str(predicates1[i]),
                             'object':     objects1[i],
                             'source':     source})
                    else:
                        id_filler = id_filler + 1
                        triple_patterns.append(
                            {'subject':    '?T' + str(id_template),
                             'predicate':   str(predicates1[i]),
                             'object':     '?F' + str(id_filler),
                             'source':     source})

                for i in range(len(predicates2)):
                    if predicates2[i] in predicates1:
                        source = 'M1 M2'
                    else:
                        if not reversed:
                            source = 'M2'
                            tp_M2_count += 1
                        else:
                            source = 'M1'
                            tp_M1_count += 1

                    tp_per_template_count += 1
                    id_filler = id_filler + 1

                    triple_patterns.append(
                        {'subject':    '?F' + str(id_filler),
                         'predicate':   str(predicates2[i]),
                         'object':     '?T' + str(id_template),
                         'source':     source})

                #test_bgp = test_bgp + 1
                #print(test_bgp, ': ', subject, ' et ', object)
                list_tp_per_template_count.append(tp_per_template_count)
                bgp.append(triple_patterns)

    return {'triple_patterns': bgp,
            'Number_of_triple_patterns': list_tp_per_template_count,
            'Number_of_triple_patterns_from_M1': tp_M1_count,
            'Number_of_triple_patterns_from_M2': tp_M2_count}


def compare_mappings(yarrrml1, yarrrml2):
    return {'subject-subject': S2S_joinDetection(yarrrml1, yarrrml2),
            'object-object':   O2O_joinDetection(yarrrml1, yarrrml2),
            'subject-object':  S2O_joinDetection(yarrrml1, yarrrml2),
            'object-subject':  S2O_joinDetection(yarrrml2, yarrrml1, reversed=True)}


def compare(mapping1, mapping2):

    yarrrml1 = load(open(mapping1), Loader=Loader)
    yarrrml2 = load(open(mapping2), Loader=Loader)

    return compare_mappings(yarrrml1, yarrrml2)


#sortie adaptée à l'appli web
def get_results(yarrrml_mappings, mapping_names):

    results = {
        'data': [],
        'queries': []
    }

    for it1 in range(0, len(yarrrml_mappings)):
        for it2 in range(0, len(yarrrml_mappings)):
            if it1 != it2:

                compared = compare_mappings(yarrrml_mappings[it1], yarrrml_mappings[it2])

                results['data'].append({
                    'Source': mapping_names[it1],
                    'Destination': mapping_names[it2],
                    'Score': 0,
                    'Join_subject_subject': {
                        'Number_of_triple_pattern': compared['subject-subject']['Number_of_triple_patterns'],
                        'Number_of_triple_pattern_from_M1': compared['subject-subject']['Number_of_triple_patterns_from_M1'],
                        'Number_of_triple_pattern_from_M2': compared['subject-subject']['Number_of_triple_patterns_from_M2']
                    },
                    'Join_object_object': {
                        'Number_of_triple_pattern': compared['object-object']['Number_of_triple_patterns'],
                        'Number_of_triple_pattern_from_M1': compared['object-object']['Number_of_triple_patterns_from_M1'],
                        'Number_of_triple_pattern_from_M2': compared['object-object']['Number_of_triple_patterns_from_M2']
                    },
                    'Join_subject_object': {
                        'Number_of_triple_pattern': compared['subject-object']['Number_of_triple_patterns'],
                        'Number_of_triple_pattern_from_M1': compared['subject-object']['Number_of_triple_patterns_from_M1'],
                        'Number_of_triple_pattern_from_M2': compared['subject-object']['Number_of_triple_patterns_from_M2']
                    }
                })

                for i in range(len(compared['subject-subject']['triple_patterns'])):
                    query = '#subject-subject\n'
                    query += f'#M1: {mapping_names[it1]}\n'
                    query += f'#M2: {mapping_names[it2]}\n'
                    query += 'SELECT *\nWHERE {\n'

                    for pattern in compared['subject-subject']['triple_patterns'][i]:
                        query += triple_pattern_to_sparql(pattern) + '\n'

                    query += '}'
                    results['queries'].append(query)

                for i in range(len(compared['object-object']['triple_patterns'])):
                    query = '#object-object\n'
                    query += f'#M1: {mapping_names[it1]}\n'
                    query += f'#M2: {mapping_names[it2]}\n'
                    query += 'SELECT *\nWHERE {\n'

                    for pattern in compared['object-object']['triple_patterns'][i]:
                        query += triple_pattern_to_sparql(pattern) + '\n'

                    query += '}'
                    results['queries'].append(query)

                for i in range(len(compared['subject-object']['triple_patterns'])):
                    query = '#subject-object\n'
                    query += f'#M1: {mapping_names[it1]}\n'
                    query += f'#M2: {mapping_names[it2]}\n'
                    query += 'SELECT *\nWHERE {\n'

                    for pattern in compared['subject-object']['triple_patterns'][i]:
                        query += triple_pattern_to_sparql(pattern) + '\n'

                    query += '}'
                    results['queries'].append(query)

    return results


def triple_pattern_to_sparql(pattern):
    if pattern['predicate'] == 'a':
        return pattern['subject'] + ' ' + pattern['predicate'] + ' <' + pattern['object'] + '>' + '.\t#' + pattern['source']
    elif pattern['predicate'] == 'rdf:type':
        return pattern['subject'] + ' ' + pattern['predicate'] + ' <' + pattern['object'] + '>' + '.\t#' + pattern['source']
    else:
        return pattern['subject'] + ' <' + pattern['predicate'] + '> ' + pattern['object'] + '.\t#' + pattern['source']