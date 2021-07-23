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

This example is made using the mappings `small-air-bnb-listings@public.rml.yml` and `small-annuaire-des-professionnels-de-sante@public.rml.yml`.

Here are examples of query formed with those mappings.
Each of those first features comments that indicates meta information on the queries:
- the type of join
- the mappings
- Which template of which mapping was used, and in which position
- The jaccard index number, which tells us how much the two template were similar. This index is calculated using the types link to a template, we consider both sets of types (one for each template) and then calculate the [Jaccard index](https://en.wikipedia.org/wiki/Jaccard_index)

 
```
### subject-subject
#M1: small-air-bnb-listings
#M2: small-annuaire-des-professionnels-de-sante
#M1_Subject :   Host
#M2_Subject :   Docteur
#Jaccard index: 0.3333333333333333
Select Count(?S2) Where {
        ?s2 rdf:type <http://schema.org/Person>.        #M1 M2
        ?s2 rdf:type <http://purl.org/goodrelations/v1#BusinessEntity>. #M1
        ?s2 rdf:type <http://linkedgeodata.org/ontology/Doctor>.        #M2
        ?s2 <https://schema.org/location> ?o1.  #M2
        ?s2 <http://dbpedia.org/ontology/speciality> ?o2.       #M2
}
 ```
 This is a "subject-subject" query, which means the two templates that were used to join the mappings were both subjects in their respective mappings.
 
 ```
### object-object
#M1: small-air-bnb-listings
#M2: small-annuaire-des-professionnels-de-sante
#M1_Object :    Neighbourhood
#M2_Object :    Address
#Jaccard index: 0.3333333333333333
Select Count(?O2) Where {
        ?s1 <https://schema.org/containedInPlace> ?o2.  #M1
        ?s2 <https://schema.org/location> ?o2.  #M2
}
 ```
 This is a "object-object" query, which means the two templates that were used to join the mappings were both objects in their respective mappings.
 
 ```
### subject-object
#M1: small-air-bnb-listings
#M2: small-annuaire-des-professionnels-de-sante
#M1_Object :    Host
#M2_Subject :   Docteur
#Jaccard index: 0.3333333333333333
Select Count(?T1) Where {
        ?t1 rdf:type <http://schema.org/Person>.        #M2
        ?t1 rdf:type <http://linkedgeodata.org/ontology/Doctor>.        #M2
        ?t1 <https://schema.org/location> ?f1.  #M2
        ?t1 <http://dbpedia.org/ontology/speciality> ?f2.       #M2
        ?f3 <http://dbpedia.org/ontology/owner> ?t1.    #M1
}
 ```
 This is a "subject-object" query, which means the one of the templates that were used to join the mappings was a subject in its mapping and the other template was a object in hin the other a object
 
 ```
### subject-object
#M1: small-air-bnb-listings
#M2: small-annuaire-des-professionnels-de-sante
#M1_Subject :   Neighbourhood
#M2_Object :    Address
#Jaccard index: 0.3333333333333333
Select Count(?T1) Where {
        ?t1 rdf:type <http://schema.org/Place>. #M1
        ?t1 rdf:type <http://dbpedia.org/ontology/PopulatedPlace>.      #M1
        ?f1 <https://schema.org/location> ?t1.  #M2
}
 ```
 This is a "subject-object" query.

