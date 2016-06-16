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
SELECT DISTINCT ?experiment_id ?probe_id ?probe_label ?color (GROUP_CONCAT(DISTINCT CONCAT(?gene_id, ';', ?symbol),'|') as ?target_molecules) (GROUP_CONCAT(DISTINCT CONCAT(?anatomy,';',?anatomy_label),'|') AS ?target_conditions)
WHERE {
    ?experiment_id lm:in_organism ?tax_id .
    ?image lm:part_of_experiment ?experiment_id .
    ?image lm:has_probe ?probe_id .
    ?probe_color lm:maps_to ?probe_id .
    ?probe_color lm:maps_to ?image .
    ?probe_color lm:color ?color .
    OPTIONAL { 
        ?probe_id lm:maps_to ?resource .
        ?resource lm:maps_to{0,1} ?gene_id .
        ?gene_id lm:id_type owl:Gene_ID .
        ?gene_id rdfs:label ?symbol .
        ?gene_id lm:in_organism ?tax_id .
    }
    OPTIONAL { ?probe_id rdfs:label ?probe_label }
    OPTIONAL { 
        ?probe_id lm:probe_target_condition ?anatomy .
        ?anatomy rdfs:label ?anatomy_label
    }
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
x = results['results']['bindings'][0]
pp.pprint(x)
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
probe_label = []
probe_id = []
experiment_id = []
color = []
target_conditions = [] 
target_molecules = []
z=0
for i,x in enumerate(results['results']['bindings']):
    #first, I'll create my s3key name
    try:        
        experiment_id.append(regexp.search(os.path.normpath(x.get('experiment_id').get('value'))).group(1))
        probe_label.append(x.get('probe_label').get('value'))
        probe_id.append(regexp.search(os.path.normpath(x.get('probe_id').get('value'))).group(1))
        color.append(x.get('color').get('value'))
        target_conditions.append(x.get('target_conditions').get('value'))
        target_molecules.append(x.get('target_molecules').get('value'))
    except:
        z += 1
        print(i)
        pp.pprint(x)
    if z > 5:
        break
output = pd.DataFrame({  'probe_label' : probe_label,
                         'probe_id' : probe_id,
                         'color': color,
                         'target_conditions': target_conditions,
                         'target_molecules': target_molecules,
                         'experiment' : experiment_id})
#check the file from the meeting                       
output.loc[output['experiment'].isin(['LMEX0000000004'])]
#did we get everything?:
output.shape[0]==len(results['results']['bindings'])
output.to_csv('/Users/nn31/Dropbox/40-githubRrepos/lungmap-data-plus-2016/metadata/03_metadata_probe_antibody.csv',index=False)    
                     
                     
                     
                     
                     
                     
                     
                     
    
