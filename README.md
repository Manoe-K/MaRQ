# MaRQ: Mapping RDF Queries

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

MaRQ use types to make queries, 
so a saturated mapping can create queries that would have been missed with a standard mapping.


'predicateobjects' should be of the form:

`- [{one and only one predicate}, {one and only one object}]`

Types or language aren't supported and might cause issues.

## Run script

Run the following command to execute MaRQ on each possible pair from n mappings:

`python script.py path/to/mapping/1 ... path/to/mapping/n`

You can also specify a directory containing only mappings to execute MaRQ on every pair of mappings contained in the directory:

`python script.py path/to/directory`

It's also possible to specify the threshold at which a query is made from two template. Only a pair of template that have a Jaccard index >= of this value will pass.

`python script.py float_value path/to/directory`

## Example

This exemple is made using the mappings `air-bnb-listings@public.rml.yml` and `annuaire-des-professionnels-de-sante@public.rml.yml`.

```
SELECT *  WHERE {
 ?s1 rdf:type schema:Person . 
 ?s1 rdf:type lgdo:Doctor .  
 ?s1 rdf:type gr:BusinessEntity .
 ?s1 schema:location ?o1 . 
 ?s1 dbo:speciality ?o2
 }
 ```
 
 ```
 SELECT *  WHERE {
 ?s1 schema:location ?o1 . 
 ?s2 schema:containedInPlace ?o1
 }
 ```
 
 ```
 SELECT *  WHERE {
 ?t1 rdf:type schema:Person . 
 ?t1 rdf:type lgdo:Doctor . 
 ?t1 schema:location ?f1 .
 ?t1 dbo:speciality ?f2 . 
 ?f3 dbo:owner ?t1
 }
 ```
 
 ```
 SELECT *  WHERE {
 ?t2 rdf:type schema:Place .
 ?t2 rdf:type dbo:PopulatedPlace .
 ?f1 schema:location ?t2
 }
 ```

