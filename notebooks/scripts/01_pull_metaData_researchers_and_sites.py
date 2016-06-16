"""
Programmer: Ben Neely
Name: 00_pull_data.py
Date: 6/9/2016
"""
#My first goal is to get all of the metadata (not in S3), for all of the files
#that I'm interested in grinding through
#Here is a SPARQL query to get (some of) the metadata
query = """
PREFIX lm: <http://ontology.lungmap.net/ontologies/expression_ontology#>
PREFIX mont: <http://ontology.lungmap.net/ontologies/mouse_anatomy#>
PREFIX owl: <http://www.w3.org/2002/07/>
PREFIX owl2: <http://www.w3.org/2002/07/owl#>
SELECT DISTINCT ?experiment ?researcher_label ?site_label
FROM  <http://data.lungmap.net/lungmap_data>
FROM  <http://data.lungmap.net/lungmap_ontology>
WHERE {
    ?researcher a lm:researcher .
    ?experiment lm:part_of ?researcher .
    ?site a lm:site .
    ?researcher lm:part_of ?site .
    ?researcher rdfs:label ?researcher_label .
    ?site rdfs:label ?site_label .
}
"""
import pprint
import os
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import re
#instantiate our pretty printer
pp = pprint.PrettyPrinter(indent=2)

sparql = SPARQLWrapper("http://testdata.lungmap.net/sparql")
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
#Here are all the results form the sparql query above
results = sparql.query().convert()

##############################################################################
############################################################################## 
############################################################################## 
#Here is what we're really after for our collaborators     
##############################################################################
############################################################################## 
############################################################################## 
#They asked us to turn our metadata object into a flat file, to do this,
#you'll need to thoroughly examine the "data model" of your new dictionary. By
#data model, i just mean the way in which that data is stored. For instance,
#notice below that i usually only pull the 'label' key of my dictionary and not
#the type key.
regexp = re.compile("#(.*)$")
#Here are the "variables that I want in my flat file:
researcher = []
site = []
experiment = []
for i,x in enumerate(results['results']['bindings']):
    #first, I'll create my s3key name
    researcher.append(x.get('researcher_label').get('value'))
    site.append((x.get('site_label').get('value')))
    experiment.append(regexp.search(os.path.normpath(x.get('experiment').get('value'))).group(1))
output = pd.DataFrame({  'researcher' : researcher,
                         'site' : site,
                         'experiment' : experiment})
output.to_csv('/Users/nn31/Dropbox/40-githubRrepos/lungmap-data-plus-2016/metadata/01_metadata_researcher.csv',index=False)    
                     
                     
                     
                     
                     
                     
                     
                     
    
