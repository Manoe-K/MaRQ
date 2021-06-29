import itertools

# Given MaRQ queries results, create smaller queries in order to find the longer queries with results.
# For that we create queries of the form:
"""
SELECT ?s WHERE {
    GRAPH <mapping_name1> {
        triple patterns originating from M1 or both mappings. }.
    GRAPH <mapping_name2> {
        triple patterns originating from M2 or both mappings. }
}
LIMIT 1
"""
# We start by making every queries of size 2 (1 pattern in each GRAPH) then increase it to size 3 and so on


# take the marq results of a pair of mapping and return a list/set(?) of string representing queries like shown above for each join
# use the "common_type" to prune the pattern containing types, keeping only the more precise common type
def create_queries(pair, common_type):

    # pruning "?s a type" queries using the results of common_ontology, we only keep the most precise common types
    for i in range(len(pair['result']['subject-subject']['triple_patterns'])):
        pruned_results = []

        for triple_pattern in pair['result']['subject-subject']['triple_patterns'][i]:
            if triple_pattern['predicate'] == 'a' or triple_pattern['predicate'] == 'rdf:type':
                if triple_pattern['object'] in common_type[i]:
                    pruned_results.append(triple_pattern)
            else:
                pruned_results.append(triple_pattern)

        pair['result']['subject-subject']['triple_patterns'][i] = pruned_results

    list_queries = []

    for bgp in pair['result']['subject-subject']['triple_patterns']:
        # for each joined template

        # Calculate the maximum sized query that we can do
        max_length = 0
        # Also separate pattern with both source in two different tripple pattern for each source
        bgp_M1 = []
        bgp_M2 = []
        for pattern in bgp:
            if pattern['source'] == 'M1':
                bgp_M1.append(
                    {'subject':     pattern['subject'],
                     'predicate':   pattern['predicate'],
                     'object':      pattern['object'],
                     'source':      'M1'})
                max_length += 1

            elif pattern['source'] == 'M2':
                bgp_M2.append(
                    {'subject': pattern['subject'],
                     'predicate': pattern['predicate'],
                     'object': pattern['object'],
                     'source': 'M2'})
                max_length += 1

            elif pattern['source'] == 'M1 M2':
                bgp_M1.append(
                    {'subject': pattern['subject'],
                     'predicate': pattern['predicate'],
                     'object': pattern['object'],
                     'source': 'M1 M2'})
                bgp_M2.append(
                    {'subject': pattern['subject'],
                     'predicate': pattern['predicate'],
                     'object': pattern['object'],
                     'source': 'M1 M2'})
                max_length += 2

        # For each size of query between 2 and the max_length
        for queries_length in range(2, max_length+1):

            for length_M1, length_M2 in [(x, y) for x in range(queries_length) for y in range(queries_length) if x+y == queries_length]:

                tuples_M1 = list(itertools.combinations(bgp_M1, length_M1))
                tuples_M2 = list(itertools.combinations(bgp_M2, length_M2))

                for tupl1 in tuples_M1:
                    for tupl2 in tuples_M2:

                        query = "SELECT count(?s) WHERE {\n"
                        query += "\tGRAPH " + pair['name1'] + " {\n"

                        for pattern in tupl1:
                            query += "\t\t" + triple_pattern_to_sparql(pattern) + "\n"

                        query += "\t}.\n"
                        query += "\tGRAPH " + pair['name2'] + " {\n"

                        for pattern in tupl2:
                            query += "\t\t" + triple_pattern_to_sparql(pattern) + "\n"

                        query += "\t}\n"
                        query += "}\n"

                        list_queries.append(query)

    return list_queries


def triple_pattern_to_sparql(pattern):
    if pattern['predicate'] == 'a' or pattern['predicate'] == 'rdf:type':
        return pattern['subject'] + ' ' + pattern['predicate'] + ' <' + pattern['object'] + '>' + '.\t#' + pattern['source']
    else:
        return pattern['subject'] + ' <' + pattern['predicate'] + '> ' + pattern['object'] + '.\t#' + pattern['source']

