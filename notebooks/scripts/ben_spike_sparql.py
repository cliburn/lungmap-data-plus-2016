# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 08:17:39 2016

@author: nn31
"""

#Using this interesting tutorial: http://semanticweb.org/wiki/Getting_data_from_the_Semantic_Web.html
#Learn more about the sematic web - note this is a version of wikipedia
# http://blog.markwatson.com/2014/07/python-sparql-client-example.html
#http://www.linkeddatatools.com/introducing-rdf

query = """PREFIX lm: <http://ontology.lungmap.net/ontologies/expression_ontology#>
PREFIX mont: <http://ontology.lungmap.net/ontologies/mouse_anatomy#>
PREFIX owl: <http://www.w3.org/2002/07/>
PREFIX owl2: <http://www.w3.org/2002/07/owl#>
SELECT DISTINCT ?experiment_id ?experiment_type_id ?image_id ?path ?raw_file ?label ?description ?age ?age_label ?organism ?organism_label ?magnification ?platform ?strain ?date ?gender
FROM  <http://data.lungmap.net/lungmap_data>
FROM  <http://data.lungmap.net/lungmap_ontology>
WHERE {
   ?image_id lm:part_of_experiment ?experiment_id .
   ?experiment_id lm:file_name ?path .
   ?image_id lm:display_url ?raw_file .
   ?image_id lm:part_of_experiment ?experiment_id .
   OPTIONAL { ?experiment_id rdfs:comment ?description } .
   OPTIONAL { ?image_id lm:magnification ?magnification } .
   OPTIONAL { ?image_id lm:platform ?platform } .
   OPTIONAL { ?image_id lm:creation_date ?date } .
   OPTIONAL { ?experiment_id lm:gender ?gender } .
   OPTIONAL { 
      ?experiment_id lm:in_strain ?strain_id .
      BIND(REPLACE(str(?strain_id), '^.+#', '') AS ?strain) .
   } .
   ?experiment_id rdfs:label ?label .
    ?experiment_id lm:is_experiment_type ?experiment_type_id .
   ?image_id lm:in_stage ?age .
   ?age rdfs:subClassOf ?organism .
   ?organism rdfs:subClassOf lm:organism .
   ?organism rdfs:label ?organism_label .
   ?age rdfs:label ?age_label .
}
"""
import pprint
import os
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import boto3
import pandas as pd
import re
#instantiate our pretty printer
pp = pprint.PrettyPrinter(indent=2)

sparql = SPARQLWrapper("http://testdata.lungmap.net/sparql")
# JSON example
print('\n\n*** JSON Example')
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
for result in results["results"]["bindings"]:
    print(result["label"]["value"])

# XML example
print('\n\n*** XML Example')
sparql.setReturnFormat(XML)
results = sparql.query().convert()
print(results.toxml())