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
SELECT DISTINCT ?experiment ?experiment_type_label ?release_date ?description ?platform
FROM  <http://data.lungmap.net/lungmap_data>
FROM  <http://data.lungmap.net/lungmap_ontology>
WHERE {
    ?experiment lm:is_experiment_type/rdfs:label ?experiment_type_label .
    OPTIONAL { ?experiment lm:creation_date|(^lm:part_of_experiment/lm:creation_date) ?release_date }
    OPTIONAL { ?experiment rdfs:comment ?description }
    OPTIONAL { ?experiment lm:platform|(^lm:part_of_experiment/lm:platform) ?platform }
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

len(results['results']['bindings'])
x = results['results']['bindings'][842]
x
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
platform = []
description = []
release_date = []
experiment = []
experiment_type = []
for i,x in enumerate(results['results']['bindings']):
    #first, I'll create my s3key name
    try:
        if 'platform' in x.keys():
            platform.append(x.get('platform').get('value'))
        else:
            platform.append('')
        if 'description' in x.keys():
            description.append(x.get('description').get('value'))
        else:
            description.append('')
        if 'release_date' in x.keys():
            release_date.append(x.get('release_date').get('value'))
        else:
            release_date.append('')
        experiment.append(regexp.search(os.path.normpath(x.get('experiment').get('value'))).group(1))
        experiment_type.append(x.get('experiment_type_label').get('value'))
    except:
        print(i)
        print(x)
output = pd.DataFrame({  'platform' : platform,
                         'release_date' : release_date,
                         'experiment_type': experiment_type,
                         'experiment' : experiment})
#did we get everything?:
output.shape[0]==len(results['results']['bindings'])
output.to_csv('/Users/nn31/Dropbox/40-githubRrepos/lungmap-data-plus-2016/metadata/02_metadata_experiment_type.csv',index=False)    
                     
                     
                     
                     
                     
                     
                     
                     
    
