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

IGNORED_PROPERTIES = ['http://www.w3.org/2000/01/rdf-schema#label', ' https://schema.org/name', 'http://www.w3.org/2004/02/skos/core#prefLabel']
IGNORED_CLASSES = ['https://schema.org/Thing']

REF_REGEX = re.compile(r'(\$\(.+?\))')


def get_keys(d, key):
    # Get the value of the first key in corresponding YARRRML_KEYS that match a key in d
    if key in YARRRML_KEYS:
        for yarrrml_key in YARRRML_KEYS[key]:
            if yarrrml_key in d:
                return d[key]
    return {}


def get_generic_template(template):
    generic_template = template
    references = {}
    for index, reference in enumerate(REF_REGEX.findall(template), start=1):
        generic_reference = f'$(field{index})'
        generic_template = generic_template.replace(reference, generic_reference)
        references[generic_reference] = reference
    return references, generic_template


def get_classes_properties_references(mapping):
    classes = []
    properties = []
    references = []

    predicate_objects = get_keys(mapping, 'predicateobjects')

    for predicate_object in predicate_objects:
        # for each predicate object (list) in mapping
        if predicate_object[0] == 'a' \
                or predicate_object[0] == 'rdf:type' \
                or predicate_object[0] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
            classes.append(predicate_object[1])
        else:
            properties.append(predicate_object[0])
            references.append(predicate_object[1])

    return classes, properties, references


def get_templates(yarrrml):
    template_list = {'templates': {}}
    # get  yarrrml key of the yarrrml file
    mappings = get_keys(yarrrml, 'mappings')
    for mapping_name, mapping in mappings.items():
        # for each mapping
        classes, properties, references = get_classes_properties_references(mapping)
        references, generic_template = get_generic_template(mapping['subject'])
        template_list['templates'][generic_template] = {
            'classes': classes,  # classes associated to this template (if subject)
            'properties': properties,  # properties associated to this template
            'references': references}

    return template_list


def get_objects(yarrrml):
    # get  yarrrml key of the yarrrml file
    mappings = get_keys(yarrrml, 'mappings')

    is_url = re.compile(r'\Ahttp')

    object_list = []
    properties_list = []
    for mapping_name, mapping in mappings.items():
        for predicate_object in get_keys(mapping, 'predicateobjects'):
            # add a new object only if it wasn't already listed

            found = False
            ite = 0
            reference, generic_template = get_generic_template(predicate_object[1])

            while ite < len(object_list) and not found:
                if object_list[ite] == generic_template:
                    found = True
                else:
                    ite = ite + 1

            if ite == len(object_list):
                if is_url.match(predicate_object[1]) is not None:
                    # if the object is an url, change it to match a generic template
                    object_list.append(generic_template)
                else:
                    # if the object is a constant
                    object_list.append(predicate_object[1])
                properties_list.append(set())

            properties_list[ite].add(predicate_object[0])

    return object_list, properties_list


def get_properties(yarrrml):
    properties_list = {'properties': {}}
    # get  yarrrml key of the yarrrml file
    mappings = get_keys(yarrrml, 'mappings')
    for mapping_name, mapping in mappings.items():
        classes, properties, references = get_classes_properties_references(mapping)
        references1, generic_template = get_generic_template(mapping['subject'])
        for i in range(len(properties)):
            properties_list['properties'][properties[i]] = {
                'classes': classes,     # classes associated to this template (if subject)
                'templates': generic_template,
                'references_templates': references1,
                'references': references[i],
                'mapping_name': mapping_name
            }

    return properties_list


def get_join_subject_subject(yarrrml1, yarrrml2):
    # keep track of the number of subject shared in order to name them differently
    id_subject = 0
    # keep track of the number of object in order to name them differently
    id_object = 0
    # keep track of the size of each bgp
    data = []

    join_subject_subject = []

    # for subject in both subject(mapping1) and subject(mapping2)
    for subject1, information1 in (get_templates(yarrrml1)['templates']).items():
        for subject2, information2 in (get_templates(yarrrml2)['templates']).items():
            if subject1 == subject2:

                triple_patterns = []
                count_pattern = 0
                id_subject = id_subject + 1

                for propertie1 in information1['properties']:
                    if propertie1 in information2['properties']:
                        provenance = 'M1 M2'
                    else:
                        provenance = 'M1'
                    id_object = id_object + 1
                    # the propertie a doesn't require < >
                    if propertie1 == 'a':
                        triple_patterns.append(['?S' + str(id_subject) + ' ' + propertie1 + ' ' + '?O' + str(id_object), provenance])
                    else:
                        triple_patterns.append(['?S' + str(id_subject) + ' <' + propertie1 + '> ' + '?O' + str(id_object), provenance])
                    count_pattern = count_pattern + 1

                for propertie2 in information2['properties']:
                    if propertie2 not in information1['properties']:
                        provenance = 'M2'
                        id_object = id_object + 1
                        # the propertie a doesn't require < >
                        if propertie2 == 'a':
                            triple_patterns.append(['?S' + str(id_subject) + ' ' + propertie2 + ' ' + '?O' + str(id_object), provenance])
                        else:
                            triple_patterns.append(['?S' + str(id_subject) + ' <' + propertie2 + '> ' + '?O' + str(id_object), provenance])
                        count_pattern = count_pattern + 1

                for class1 in information1['classes']:
                    if class1 in information2['classes']:
                        provenance = 'M1 M2'
                    else:
                        provenance = 'M1'
                    triple_patterns.append(['?S' + str(id_subject) + ' a <' + class1 + '>', provenance])
                    count_pattern = count_pattern + 1

                for class2 in information2['classes']:
                    if class2 not in information1['classes']:
                        provenance = 'M2'
                        triple_patterns.append(['?S' + str(id_subject) + ' a <' + class2 + '>', provenance])
                        count_pattern = count_pattern + 1

                if triple_patterns:

                    join_subject_subject.append(triple_patterns)
                    data.append(count_pattern)

    return [id_subject, data], {'subject-subject': join_subject_subject}


def get_join_object_object(yarrrml1, yarrrml2):
    # keep track of the number of object shared in order to name them differently
    id_object = 0
    # keep track of the number of subject in order to name them differently
    id_subject = 0
    # and count the total size of each bgp
    data = []

    join_object_object = []

    objects1, properties_list1 = get_objects(yarrrml1)
    objects2, properties_list2 = get_objects(yarrrml2)

    # for subject in both subject(mapping1) and subject(mapping2)
    for i in range(len(objects1)):
        for y in range(len(objects2)):
            if objects1[i] == objects2[y]:

                triple_patterns = []
                count_pattern = 0
                id_object = id_object + 1

                for propertie1 in properties_list1[i]:
                    if propertie1 in properties_list2[y]:
                        provenance = 'M1 M2'
                    else:
                        provenance = 'M1'
                    id_subject = id_subject + 1
                    # the propertie a doesn't require < >
                    if propertie1 == 'a':
                        triple_patterns.append(['?S' + str(id_subject) + ' ' + propertie1 + ' <' + objects1[i] + '>', provenance])
                    else:
                        if propertie1 == 'rdf:type':
                            triple_patterns.append(['?S' + str(id_subject) + ' <' + propertie1 + '> <' + objects1[i] + '>', provenance])
                        else:
                            triple_patterns.append(['?S' + str(id_subject) + ' <' + propertie1 + '> ?O' + str(id_object), provenance])
                    count_pattern = count_pattern + 1

                for propertie2 in properties_list2[y]:
                    if propertie2 not in properties_list1[i]:
                        provenance = 'M2'
                        id_subject = id_subject + 1
                        # the propertie a doesn't require < >
                        if propertie2 == 'a':
                            triple_patterns.append(['?S' + str(id_subject) + ' ' + propertie2 + ' <' + objects2[y] + '>', provenance])
                        else:
                            if propertie2 == 'rdf:type':
                                triple_patterns.append(['?S' + str(id_subject) + ' <' + propertie2 + '> <' + objects2[y] + '>', provenance])
                            else:
                                triple_patterns.append(['?S' + str(id_subject) + ' <' + propertie2 + '> ?O' + str(id_object), provenance])

                        count_pattern = count_pattern + 1

                if triple_patterns:

                    join_object_object.append(triple_patterns)
                    data.append(count_pattern)

    return [id_object, data], {'object-object': join_object_object}


def get_join_subject_object(yarrrml1, yarrrml2):
    # keep track of the number of template (subject-object) shared in order to name them differently
    id_template = 0
    # keep track of the number of generic template used in order to name them differently
    id_filler = 0
    # and count the total size of each bgp
    data = []

    join_subject_object = []

    objects1, properties_list1 = get_objects(yarrrml1)
    objects2, properties_list2 = get_objects(yarrrml2)

    # pour les objets du mapping 1 communs aux sujets du mapping 2
    for i in range(len(objects1)):
        for subject2, information2 in (get_templates(yarrrml2)['templates']).items():
            if objects1[i] == subject2:

                triple_patterns = []
                count_pattern = 0
                id_template = id_template + 1

                for propertie1 in properties_list1[i]:
                    if propertie1 in information2['properties']:
                        provenance = 'M1 M2'
                    else:
                        provenance = 'M1'
                    id_filler = id_filler + 1
                    # the propertie a doesn't require < >
                    if propertie1 == 'a':
                        triple_patterns.append(
                            ['?S' + str(id_filler) + ' ' + propertie1 + ' ' + '?T' + str(id_template), provenance])
                    else:
                        triple_patterns.append(
                            ['?F' + str(id_filler) + ' <' + propertie1 + '> ' + '?T' + str(id_template), provenance])
                    count_pattern = count_pattern + 1

                for propertie2 in information2['properties']:
                    if propertie2 in properties_list1[i]:
                        provenance = 'M1 M2'
                    else:
                        provenance = 'M2'
                    id_filler = id_filler + 1
                    # the propertie a doesn't require < >
                    if propertie2 == 'a':
                        triple_patterns.append(['?T' + str(id_template) + ' ' + propertie2 + ' ' + '?F' + str(id_filler), provenance])
                    else:
                        triple_patterns.append(['?T' + str(id_template) + ' <' + propertie2 + '> ' + '?F' + str(id_filler), provenance])
                    count_pattern = count_pattern + 1

                if triple_patterns:

                    join_subject_object.append(triple_patterns)
                    data.append(count_pattern)

    # pour les sujets du mapping 1 communs aux objets du mapping 2
    for subject1, information1 in (get_templates(yarrrml1)['templates']).items():
        for ite in range(len(objects2)):
            if subject1 == objects2[ite]:

                triple_patterns = []
                count_pattern = 0
                id_template = id_template + 1

                for propertie1 in information1['properties']:
                    if propertie1 in properties_list2[ite]:
                        provenance = 'M1 M2'
                    else:
                        provenance = 'M1'
                    id_filler = id_filler + 1
                    # the propertie a doesn't require < >
                    if propertie1 == 'a':
                        triple_patterns.append(['?T' + str(id_template) + ' ' + propertie1 + ' ' + '?F' + str(id_filler), provenance])
                    else:
                        triple_patterns.append(['?T' + str(id_template) + ' <' + propertie1 + '> ' + '?F' + str(id_filler), provenance])
                    count_pattern = count_pattern + 1

                for propertie2 in properties_list2[ite]:
                    if propertie2 in information1['properties']:
                        provenance = 'M1 M2'
                    else:
                        provenance = 'M2'
                    id_filler = id_filler + 1
                    # the propertie a doesn't require < >
                    if propertie2 == 'a':
                        triple_patterns.append(['?F' + str(id_filler) + ' ' + propertie2 + ' ' + '?T' + str(id_template), provenance])
                    else:
                        triple_patterns.append(['?F' + str(id_filler) + ' <' + propertie2 + '> ' + '?T' + str(id_template), provenance])
                    count_pattern = count_pattern + 1

                if triple_patterns:

                    join_subject_object.append(triple_patterns)
                    data.append(count_pattern)

    return [id_template, data], {'subject-object': join_subject_object}


# calculate the score from data colected before hand
# the data is of this form:
#
#    [ [ [int,int,int], ...],[ [int,int,int], ...],[ [int,int,int], ...] ]
#    for each type of join (s-s, o-o, s-o in that order)
#       for each bgp (each triplet is a bgp
#           first is the number of triple pattern coming from mapping1
#           second is the number of triple pattern coming from mapping2
#           third is the number of triple pattern coming from mapping1 and mapping2
def calcul_score(data):
    score = 0

    for join in data:
        for triple_pattern in join:
            score = score -1 + 2 ** triple_pattern[1]

    return score


def get_results(yarrrml_mappings, mapping_names):
    result = {'data': [], 'queries': []}

    # compare every mapping with every other mappings and print data and results
    for it1 in range(0, len(yarrrml_mappings)):
        for it2 in range(it1+1, len(yarrrml_mappings)):

            data_1, results_1 = get_join_subject_subject(yarrrml_mappings[it1], yarrrml_mappings[it2])
            data_2, results_2 = get_join_object_object(yarrrml_mappings[it1], yarrrml_mappings[it2])
            data_3, results_3 = get_join_subject_object(yarrrml_mappings[it1], yarrrml_mappings[it2])

            # calculate the score in order to rank later
            # we calculate how much M2 adds to M1
            score_data = []

            # calculate the number of triplet coming from M1 and the number of triplet coming from M2
            provenance1_m1 = 0
            provenance1_m2 = 0
            score_data.append([])
            for provs in results_1['subject-subject']:
                for prov in provs:
                    count1 = 0
                    count2 = 0
                    count3 = 0
                    if len(prov[1]) > 2:
                        provenance1_m1 = provenance1_m1 + 1
                        provenance1_m2 = provenance1_m2 + 1
                        count3 = count3 + 1
                    else:
                        if prov[1][1] == '1':
                            provenance1_m1 = provenance1_m1 + 1
                            count1 = count1 + 1
                        else:
                            provenance1_m2 = provenance1_m2 + 1
                            count2 = count2 + 1
                    score_data[0].append([count1, count2, count3])

            provenance2_m1 = 0
            provenance2_m2 = 0
            score_data.append([])

            for provs in results_2['object-object']:
                for prov in provs:
                    count1 = 0
                    count2 = 0
                    count3 = 0
                    if len(prov[1]) > 2:
                        provenance2_m1 = provenance2_m1 + 1
                        provenance2_m2 = provenance2_m2 + 1
                    else:
                        if prov[1][1] == '1':
                            provenance2_m1 = provenance2_m1 + 1
                        else:
                            provenance2_m2 = provenance2_m2 + 1
                            count2 = count2 + 1
                    score_data[1].append([count1, count2, count3])

            provenance3_m1 = 0
            provenance3_m2 = 0
            score_data.append([])
            for provs in results_3['subject-object']:
                for prov in provs:
                    count1 = 0
                    count2 = 0
                    count3 = 0
                    if len(prov[1]) > 2:
                        provenance3_m1 = provenance3_m1 + 1
                        provenance3_m2 = provenance3_m2 + 1
                        count3 = count3 + 1
                    else:
                        if prov[1][1] == '1':
                            provenance3_m1 = provenance3_m1 + 1
                            count1 = count1 + 1
                        else:
                            provenance3_m2 = provenance3_m2 + 1
                            count2 = count2 + 1
                    score_data[2].append([count1, count2, count3])

            score = calcul_score(score_data)

            # only for the first loop of each pair of mappings
            comparison = {"Source": mapping_names[it1],
                          "Destination": mapping_names[it2],
                          "Score": score,
                          "Join_subject_subject": {
                                  "Number_of_triple_pattern": [],
                                  "Number_of_triple_pattern_from_M1": None,
                                  "Number_of_triple_pattern_from_M2": None},
                          "Join_object_object": {
                                  "Number_of_triple_pattern": [],
                                  "Number_of_triple_pattern_from_M1": None,
                                  "Number_of_triple_pattern_from_M2": None},
                          "Join_subject_object": {
                                  "Number_of_triple_pattern": [],
                                  "Number_of_triple_pattern_from_M1": None,
                                  "Number_of_triple_pattern_from_M2": None}
                          }

            if data_1[0] > 0:
                for j in range(len(data_1[1])):
                    comparison["Join_subject_subject"]["Number_of_triple_pattern"].append(data_1[1][j])
            comparison["Join_subject_subject"]["Number_of_triple_pattern_from_M1"] = provenance1_m1
            comparison["Join_subject_subject"]["Number_of_triple_pattern_from_M2"] = provenance1_m2

            # result from object_object
            if data_2[0] > 0:
                for j in range(len(data_2[1])):
                    comparison["Join_object_object"]["Number_of_triple_pattern"].append(data_2[1][j])
            comparison["Join_object_object"]["Number_of_triple_pattern_from_M1"] = provenance2_m1
            comparison["Join_object_object"]["Number_of_triple_pattern_from_M2"] = provenance2_m2

            # result from subject_object
            if data_3[0] > 0:
                for j in range(len(data_3[1])):
                    comparison["Join_subject_object"]["Number_of_triple_pattern"].append(data_3[1][j])
            comparison["Join_subject_object"]["Number_of_triple_pattern_from_M1"] = provenance3_m1
            comparison["Join_subject_object"]["Number_of_triple_pattern_from_M2"] = provenance3_m2

            result['data'].append(comparison)

            for j in range(len(results_1['subject-subject'])):
                query = 'SELECT *\nWHERE {\n'
                for y in results_1['subject-subject'][j]:
                    if y[1] == "M1 M2":
                        query += f' {y[0]}   #{mapping_names[it1]} and {mapping_names[it2]},\n'
                    if y[1] == "M1":
                        query += f' {y[0]}   #{mapping_names[it1]},\n'
                    if y[1] == "M2":
                        query += f' {y[0]}   #{mapping_names[it2]},\n'
                query += '\n}'
                result['queries'].append(query)

            for j in range(len(results_2['object-object'])):
                query = 'SELECT *\nWHERE {\n'
                for y in results_2['object-object'][j]:
                    if y[1] == "M1 M2":
                        query += f' {y[0]}   #{mapping_names[it1]} and {mapping_names[it2]},\n'
                    if y[1] == "M1":
                        query += f' {y[0]}   #{mapping_names[it1]},\n'
                    if y[1] == "M2":
                        query += f' {y[0]}   #{mapping_names[it2]},\n'
                query += '\n}'
                result['queries'].append(query)

            for j in range(len(results_3['subject-object'])):
                query = 'SELECT *\nWHERE {\n'
                for y in results_3['subject-object'][j]:
                    if y[1] == "M1 M2":
                        query += f' {y[0]}   #{mapping_names[it1]} and {mapping_names[it2]}.\n'
                    if y[1] == "M1":
                        query += f' {y[0]}   #{mapping_names[it1]}.\n'
                    if y[1] == "M2":
                        query += f' {y[0]}   #{mapping_names[it2]}.\n'
                query += '\n}'
                result['queries'].append(query)

    return result


# open and load yarrrml file
list_mappings = []
for yarrrml in sys.argv[1:]:
    list_mappings.append(load(open(yarrrml), Loader=Loader))

mappings_names =[]
for it in range(1, len(sys.argv[1:])+1):
    mappings_names.append("mapping" + str(it))

# test print
results = get_results(list_mappings, mappings_names)
print(results['data'])
print()
print(results['queries'])

