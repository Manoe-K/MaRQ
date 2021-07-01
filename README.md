# MappingQueryFinder

This project is an approach to generate federated queries from RDF mappings.

## Installation

We assume that `Python3` and `pip` is installed

Download IDE for python

this project was created with 
`Pycharm`

Installation in a virtualenv is strongly recommended

install venv

`python3 -m venv env`

Install dependencies with pip:

`pip install -r requirements.txt`

## Mappings

Mappings need to be Yarrrml mappings.

They are expected to be saturated (if not MaRQ might miss plausible queries).

'predicateobjects' should be of the form:

`- [{one and only one predicate}, {one and only one object}]`

Types or language aren't supported and might cause issues.

## Run script

Run the following command to execute MaRQ on each possible pair from n mappings:

`python script.py {path to mapping 1} ... {path to mapping n}`

You can also specify a directory containing only mappings to execute MaRQ on every pair of mappings contained in the directory:

`python script.py {path to directory}`

It's also possible to specify the threshold at which a query is made from two template. Only a pair of template that have a Jaccard index >= of this value will pass.

`python script.py {Jaccard_threshold} {path to directory}`

