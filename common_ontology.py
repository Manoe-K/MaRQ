import sparql
import re
import sys


# read the MaRQ output and select the common classes used in the subject to subject BGPs
def get_common_ontologies(MaRQ_results):

    current_bgp = set()
    l_bgp = []
    S2S = False

    for line in MaRQ_results.splitlines():
        if line == 'S-S':     # select the part that we wanna test
            S2S = True
        if line == 'O-O':
            S2S = False

        if S2S:                 # select the lines that originate from both mappings and are type queries, remember the types
            if line[0:3] == 'bgp':
                l_bgp.append(current_bgp)
                current_bgp = set()
            if re.search(" a .*'M1 M2'.*", line):
                url = re.search("http.*',", line)
                current_bgp.add(url.group()[:-2])

    l_bgp.append(current_bgp)
    l_bgp.pop(0)


    # remove some ontologies that wont be of use
    # todo: candidat à supprimer:
    #  'http://purl.org/goodrelations/v1#Location'
    classes_to_suppress = {'http://www.w3.org/2000/01/rdf-schema#Resource'}

    for classes in l_bgp:
        for ontology in classes_to_suppress:
            if ontology in classes:
                classes.remove(ontology)


    # initiate superclasses from the superclasses.txt file that store results
    superclasses = {}
    try:
        superclasses_file = open('superclasses.txt', 'r')
        for line in superclasses_file.readlines():
            stock = line.split(',')
            superclasses[stock[0]] = []
            for value in stock[1:-1]:
                superclasses[stock[0]].append(value)
        superclasses_file.close()
    except FileNotFoundError:
        pass
        #the file will be created for the next usage


    results = []

    # ask the sparql endpoint for the superclasses of each bgps
    # also stores all queries answers in the superclasses.txt file to not ask twice the same query
    superclasses_file = open('superclasses.txt', 'a')
    for classes in l_bgp:

        for element in classes:
            if element not in superclasses:
                #ask the endpoint the superclasses of our element if it hasn't been done before

                superclasses[element] = []
                superclasses_file.write(element)

                q = ('PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>'
                     'SELECT ?superClass WHERE { '
                     '<' + element + '> rdfs:subClassOf ?superClass . }')

                answer = sparql.query('https://lov.linkeddata.es/dataset/lov/sparql', q)

                for row in answer:
                    values = sparql.unpack_row(row)

                    # verify if we are not adding a cycle, those make both ontology disappear which we do not want
                    cycle = False
                    if values[0] in superclasses:
                        if element in superclasses[values[0]]:
                            cycle = True
                    if not cycle:
                        superclasses[element].append(values[0])
                        superclasses_file.write(','+values[0])
                superclasses_file.write(',\n')

        # substract in classes all the superclasses of it's element, this finding the most precise common classes
        results.append(classes - ({v for k in classes for v in superclasses[k]}))

    return results

