"""
Programmer: Ben Neely
Name: 00_pull_data.py
Date: 6/9/2016
"""
#My first goal is to get all of the metadata (not in S3), for all of the files
#that I'm interested in grinding through
#Here is a SPARQL query to get (some of) the metadata
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
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
#Here are all the results form the sparql query above
results = sparql.query().convert()

index = []
#only want to do .tif files (check with Cliburn), so get index of those files
for i,x in enumerate(results['results']['bindings']):
    filename = x.get('raw_file').get('value')
    name, ext = os.path.splitext(filename)
    if (ext=='.tif' or ext=='.tiff'):
        #print(ext)
        index.append(i)
##############################################################################
############################################################################## 
############################################################################## 
#Example of downloading only 1 file    
##############################################################################
############################################################################## 
##############################################################################       
#here are the files I'm interested in:
tif_files = [results['results']['bindings'][i] for i in index]
#Define a client connection to our bucket for download
s3 = boto3.resource('s3')
bucket = s3.Bucket('lungmap-breath-data')
#Here is how to get 1 file, and output it and it's JSON metadata to a local directory
first_result = tif_files[0]
pp.pprint(first_result)
#now, we need to create an s3.ObjectSummary key from this metadata
filename = first_result.get('raw_file').get('value')
name, ext = os.path.splitext(filename)
root = os.path.basename(os.path.normpath(first_result.get('path').get('value')))
s3objkey =  os.path.join(root,name,filename) 
basepath = '/Users/nn31/Dropbox/40-githubRrepos/lungmap-data-plus-2016/data'
filepath = os.path.join(basepath,root,name)
if not os.path.exists(filepath):
    os.makedirs(filepath)
    bucket.download_file(s3objkey, os.path.join(filepath, filename))
    with open(os.path.join(filepath,'meta.json'),'w') as outfile:
        json.dump(first_result,outfile)
##############################################################################
############################################################################## 
############################################################################## 
#Example of downloading multiple files   
##############################################################################
############################################################################## 
##############################################################################       
def download_n_files(results_list=[],n=None,basepath=None):
    if n is None:
        nr = range(0,len(results_list))
    else:
        nr = range(0,n)
    first_result =  [results_list[i] for i in nr]
    for i,x in enumerate(first_result):
        #now, we need to create an s3.ObjectSummary key from this metadata
        filename = x.get('raw_file').get('value')
        name, ext = os.path.splitext(filename)
        root = os.path.basename(os.path.normpath(x.get('path').get('value')))
        s3objkey =  os.path.join(root,name,filename)
        if basepath is None:
            basepath = '/Users/nn/Dropbox/40-githubRrepos/lungmap-data-plus-2016/data'
        filepath = os.path.join(basepath,root,name)
        if not os.path.exists(filepath):
            print('downloading ' + filename)
            os.makedirs(filepath)
            bucket.download_file(s3objkey, os.path.join(filepath, filename))
            with open(os.path.join(filepath,'meta.json'),'w') as outfile:
                json.dump(x,outfile)
    print('download of files complete')
                         
                
#download the first 10 tif files and their associated metadata objects (as defined in query above)
#download_n_files(tif_files,n=4)  
#alternatively download 6 files:
download_n_files(tif_files,n=6)
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
def bens_dict_2_flatfile(metadata_from_sparql):
    #Here are the "variables that I want in my flat file:
    s3downloadkey = [] #I can parse this to get file name if needed and this should be unique by metadata object (primary key)
    age_label = []
    date = []
    gender = []
    image_id = []
    experiment_id = []
    label = []
    magnification = []
    organism_label = []
    platform = []
    strain = []
    for i,x in enumerate(metadata_from_sparql):
        #first, I'll create my s3key name
        filename = x.get('raw_file').get('value')
        name, ext = os.path.splitext(filename)
        root = os.path.basename(os.path.normpath(x.get('path').get('value')))
        s3objkey =  os.path.join(root,name,filename)
        #now let's start appending to our lists
        s3downloadkey.append(s3objkey)
        age_label.append(x.get('age_label').get('value'))
        date.append(x.get('date').get('value'))
        gender.append(x.get('gender').get('value'))
        im_id = regexp.search(os.path.normpath(x.get('image_id').get('value'))).group(1)
        image_id.append(im_id)
        exp_id = regexp.search(os.path.basename(os.path.normpath(x.get('experiment_type_id').get('value')))).group(1)
        experiment_id.append(exp_id)
        label.append(x.get('label').get('value'))
        magnification.append(x.get('magnification').get('value'))
        organism_label.append(x.get('organism_label').get('value'))
        platform.append(x.get('platform').get('value'))
        strain.append(x.get('strain').get('value'))
    output = pd.DataFrame({  's3downloadkey' : s3downloadkey,
                             'age_label' : age_label,
                             'date' : date,
                             'gender': gender,
                             'image_id': image_id,
                             'experiment_id': experiment_id,
                             'label': label,
                             'magnification': magnification,
                             'organism_label': organism_label,
                             'platform': platform,
                             'strain': strain
                              },index=s3downloadkey)
    return(output)
        
flat_file = bens_dict_2_flatfile(tif_files) 
#note that we now have the key to download from boto3
#i.e. bucket.download_file(s3objkey, os.path.join(filepath, filename)) 
os.chdir('/Users/nn/Dropbox/40-githubRrepos/lungmap-data-plus-2016/metadata') 
flat_file.to_csv('00_metadata_dictionary.csv',index=False)    #this file ends up in os.getcwd()               
#once you get to this point, go to http://www.lungmap.net/breath-experiment-browser/?visibletabs=LMXT0000000003
#do we have all of the metadata that the website displays? combining everybody's contribution...                 
                     
                     
                     
                     
                     
                     
                     
                     
                     
    
