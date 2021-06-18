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


#take a set of triple patterns with their origin and return a list/set(?) of string representing queries like shown above
def make_queries(bgp):
    return set()