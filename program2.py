import re
import sys

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

stream=open(sys.argv[1])

data = load(stream, Loader=Loader)
output = dump(data, Dumper=Dumper)

mot=output.split( '\n' )
#print(mot)


liste_properties = []
liste_classes = []
#les_autres = []
for m in mot:
    if "[a," in m:
        n = re.search(r"a, '(.+?)']", m)
        if n:
            liste_classes.append(n.group(1))
    elif "['" in m:
        n = re.search(r"'(.+?)',", m)
        if n:
            liste_properties .append(n.group(1))
            #..  else:
            # les_autres.append(m)
            # print(len(liste_properties))
