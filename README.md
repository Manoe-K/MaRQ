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

## Run script

Run the following command:
`python Marq.py mapping1.yml mapping2.yml`

TEMPORARY:   For now, to change the query type change `join_subject_subject()` to `join_object_object()` or `join_subject_object()` on line 197 of `Marq.py`.

Where `mapping1.yml`and `mapping2.yml` are our YARRRML mapping.

To run the old program:
`python program.py mapping1.yml mapping2.yml`
