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
SELECT DISTINCT ?experiment ?image ?path ?img_file ?magnification ?x_scaling ?y_scaling
FROM  <http://data.lungmap.net/lungmap_data>
FROM  <http://data.lungmap.net/sequence_mappings>
FROM  <http://data.lungmap.net/lungmap_ontology>
WHERE {
    ?image lm:part_of_experiment ?experiment .
    ?image lm:display_url ?img_file .
    ?image lm:magnification ?magnification .
    ?image lm:x_scaling ?x_scaling .
    ?image lm:y_scaling ?y_scaling .
    ?experiment lm:file_name ?path .
} ORDER BY ASC(xsd:integer(REPLACE(str(?magnification), 'X', '')))

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
experiment = []
image = []
img_file = []
magnification = []
path = []
x_scaling = []
y_scaling = []
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
        append_if_not_miss('experiment',experiment,True)
        append_if_not_miss('image',image,True)
        append_if_not_miss('img_file',img_file)
        append_if_not_miss('magnification',magnification)
        append_if_not_miss('path',path)
        append_if_not_miss('x_scaling',x_scaling)
        append_if_not_miss('y_scaling',y_scaling)
    except:
        z += 1
        print(i)
        pp.pprint(x)
    if z > 5:
        break
output = pd.DataFrame({  'experiment' : experiment,
                         'image' : image,
                         'img_file' : img_file,
                         'magnification' : magnification,
                         'path' : path,
                         'x_scaling' : x_scaling,
                         'y_scaling': y_scaling})
#check the file from the meeting                       
output.loc[output['experiment'].str.contains('LMEX0000000622')]
#did we get everything?:
output.shape[0]==len(results['results']['bindings'])
#output.to_csv('/Users/nn31/Dropbox/40-githubRrepos/lungmap-data-plus-2016/metadata/05_metadata_experiment_annotation.csv',index=False)  
#Note, the file above would be 101.4 MB if output, so we'll only keep information for the tif files defined in the 00 script
our_images = pd.read_csv('/Users/nn31/Dropbox/40-githubRrepos/lungmap-data-plus-2016/metadata/00_metadata_dictionary.csv')  

new_output = output.loc[output['image'].isin(our_images.image_id.tolist())]
new_output.shape[0]==our_images.shape[0]                   
#we'll need to push this back to Nathan
new_output.to_csv('/Users/nn31/Dropbox/40-githubRrepos/lungmap-data-plus-2016/metadata/06_metadata_experiment_images.csv',index=False)                
                     
                     
                     
                     
                     
                     
    
