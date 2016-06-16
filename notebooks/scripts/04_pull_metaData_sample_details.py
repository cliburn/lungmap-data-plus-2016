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
PREFIX owl: <http://www.w3.org/2002/07/>
PREFIX owl2: <http://www.w3.org/2002/07/owl#>
PREFIX mont: <http://ontology.lungmap.net/ontologies/mouse_anatomy#>
PREFIX hont: <http://ontology.lungmap.net/ontologies/human_anatomy#>
SELECT ?experiment_id ?sample_id ?tax_id ?organism_label ?local_id ?age ?age_label ?age_group ?age_group_label ?weight ?sex ?race ?cause_of_death ?health_status ?strain ?genotype ?crown_rump_length ?harvest_date
WHERE {
    ?sample_id lm:part_of_experiment ?experiment_id .
    ?sample_id lm:in_organism ?tax_id .
    ?tax_id rdfs:label ?organism_label .
    ?sample_id lm:local_id ?local_id .
    ?sample_id lm:in_stage ?age .
    ?sample_id lm:in_stage ?age .
    OPTIONAL { ?age rdfs:label ?age_label }
    FILTER NOT EXISTS { ?age rdfs:subClassOf hont:LMHA0000000648 }
    OPTIONAL {
       ?sample_id lm:in_stage ?age_group .
       ?age_group rdfs:label ?age_group_label .
       ?age_group rdfs:subClassOf hont:LMHA0000000648
    }
    ?sample_id lm:weight ?weight .
    ?sample_id lm:gender ?sex .
    OPTIONAL {?sample_id lm:race ?race }
    OPTIONAL {?sample_id lm:cause_of_death ?cause_of_death }
    OPTIONAL {?sample_id lm:health_status ?health_status }
    OPTIONAL {?sample_id lm:in_strain ?strain }
    OPTIONAL {?sample_id lm:genotype ?genotype }
    OPTIONAL {?sample_id lm:crown_rump_length ?crown_rump_length }
    OPTIONAL {?sample_id lm:harvest_date ?harvest_date }
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
x = results['results']['bindings'][81]
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
age = []
age_group = []
age_group_label = []
age_label = []
cause_of_death = []
health_status = []
local_id = []
organism_label = []
race = []
sample_id = []
sex = []
experiment_id = []
tax_id = []
weight = []
crown_rump_length = []
genotype = []
harvest_date = []
strain = []
z=0

def append_if_not_miss(thing_label,thing,regex=False):
    if regex==False:
        if thing_label in x.keys():        
            thing.append(x.get(thing_label).get('value'))
        else:
            thing.append('')
    else:
        if thing_label in x.keys():        
            thing.append(regexp.search(os.path.normpath(x.get(thing_label).get('value'))).group(1))
        else:
            thing.append('')

for i,x in enumerate(results['results']['bindings']):
    #first, I'll create my s3key name
    try:
        append_if_not_miss('age',age)
        append_if_not_miss('age_group',age_group)
        append_if_not_miss('age_group_label',age_group_label)
        append_if_not_miss('age_label',age_label)
        append_if_not_miss('cause_of_death',cause_of_death)
        append_if_not_miss('health_status',health_status)
        append_if_not_miss('local_id',local_id)
        append_if_not_miss('organism_label',organism_label)
        append_if_not_miss('race',race)
        append_if_not_miss('sample_id',sample_id,True)
        append_if_not_miss('sex',sex)
        append_if_not_miss('experiment_id',experiment_id,True)
        append_if_not_miss('tax_id',tax_id)
        append_if_not_miss('weight',weight)
        append_if_not_miss('crown_rump_length',crown_rump_length)
        append_if_not_miss('genotype',genotype)
        append_if_not_miss('harvest_date',harvest_date)
        append_if_not_miss('strain',strain,True)
    except:
        z += 1
        print(i)
        pp.pprint(x)
    if z > 5:
        break
output = pd.DataFrame({  'age_group' : age_group,
                         'age_group_label' : age_group_label,
                         'age_label': age_label,
                         'cause_of_death': cause_of_death,
                         'experiment_id': experiment_id,
                         'health_status' : health_status,
                         'local_id' : local_id,
                         'organism_label': organism_label,
                         'race': race,
                         'sample_id': sample_id,
                         'sex' : sex,
                         'tax_id' : tax_id,
                         'weight': weight,
                         'crown_rump_length':crown_rump_length,
                         'genotype':genotype,
                         'harvest_date':harvest_date,
                         'strain':strain})
#check the file from the meeting                       
output.loc[output['experiment_id'].isin(['LMEX0000000004'])]
#did we get everything?:
output.shape[0]==len(results['results']['bindings'])
output.to_csv('/Users/nn31/Dropbox/40-githubRrepos/lungmap-data-plus-2016/metadata/04_metadata_sample_details.csv',index=False)    
                     
                     
                     
                     
                     
                     
                     
                     
    
