import re
# import pandas as pd
import os
import json
import csv
# from rdflib import Literal

main_dict = {}

# Open the CSV file
with open('/media/newbuntu/rdfal/NEW AGE/OpenTargets/csv_data/otDrug.csv', 'r') as f:
    # Create a CSV reader
    reader = csv.reader(f)

    # Iterate over each row in the CSV
    for row in reader:
        # Get the key (first item in row) and values (rest of the items)
        key = row[0]
        values = row[1:]

        # If the first column is not blank
        if key:
            # If the key doesn't exist in the dictionary, add it with a list containing the values
            if key not in main_dict:
                main_dict[key] = [values]

            # If the key already exists, append the values to the existing list
            else:
                main_dict[key].append(values)

# Define variables for URIs
base_uri_prefix = "otgs"
#class_uri = "otgs"

type_triple = "{} rdf:type {} .\n"
base_triple = "{} <http://mdata.com/{}> {} .\n"
base_uri = "<http://mdata.com/{}>"
class_uri = "<http://mdata.com/{}>"
empty_triple = "{} {} {} .\n"

# Initialize ontology in Turtle format
# Prefixes are required for the correct interpretation of the ontology
turtle = f"""
@prefix {base_uri_prefix}: <http://mdata.com/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix oboInOwl: <http://www.geneontology.org/formats/oboInOwl#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix BFO: <http://purl.obolibrary.org/obo/BFO_> .


{base_uri_prefix}:isPartOf owl:equivalentProperty BFO:0000050 .
"""

filepaths = {
             'molecule':'molecule/',
            'indications':'indication/',
             'mechanismofaction':'mechanismOfAction/',
             'drugwarnings':'fda/drugWarnings/',
             'significantreactions':'fda/significantAdverseDrugReactions/'
             }

def comillas(inputText):
    return '"' + str(inputText) + '"'

def remove_baseURI_prefix(input_text):
    if input_text.startswith('baseURI'):
        return input_text.replace('baseURI:','').strip()
    elif input_text.startswith('URI -'):
        return input_text.replace('URI -','').strip()
    else:
        return input_text

def replace_baseURI_prefix(input_text):
    if input_text.startswith('baseURI'):
        return base_uri.format(input_text.replace('baseURI:','').strip())
    elif input_text.startswith('classURI'):
        return class_uri.format(input_text.replace('classURI:','').strip())
    elif input_text.startswith('URI -'):
        return base_uri.format(input_text.replace('URI -','').strip())
    else:
        return input_text

def list_to_string(input_text):
    if isinstance(input_text, list):
        return ','.join(input_text)
    elif isinstance(input_text, dict):
        # Use a list comprehension to convert the dictionary keys and values to strings,
        # Capitalize the first letter of each key, and join them together with ": " and ". "
        return '. '.join([f'{k.capitalize()}: {list_to_string(v)}' for k, v in input_text.items()])

    else:
        return input_text

def rdf_encode(input_text):
    if isinstance(input_text, str):
        input_text = input_text.replace("\\",'\\\\')
        return input_text.replace('"', r'\"')
    else:
        return input_text

def read_text_file(file_path):
    global level_1_auto_generated_id

    file_ttl = ""

    with open(file_path, 'r') as f:
        lines = f.readlines()

        level_1_base_uri = base_uri.format(level_1_entity[0].replace('URI -','').strip()+'/{}')
        #print(level_1_base_uri)

        for level_1_row in lines:
            level_1_row = json.loads(level_1_row)

            #print(level_1_row)
############ LEVEL 1 ###################
            if level_1_entity[1] == "AUTO GENERATED":
                level_1_instance_uri = level_1_base_uri.format(str(level_1_auto_generated_id)+'{}')
                level_1_auto_generated_id += 1
            else:
                level_1_instance_uri = level_1_base_uri.format(str(level_1_row[level_1_entity[1]])+'{}')

            # IF exists a class for this level row, create it.
            if level_1_entity[2] is not None:
                level1_type_triple = type_triple.format(level_1_instance_uri.format(''), base_uri.format(level_1_entity[2].replace('classURI:','')))
                file_ttl += level1_type_triple

            # Se itera por cada campo que haya en una linea dada
            for level_2_key, level_2_value in level_1_row.items():
                #print(level_2_key, level_2_value)
                ########## LEVEL 2 ##########
                level_2_auto_generated_id = 0
                for dict_1_row in main_dict[main_entity]:
                    # If the field is in the config dict and the range is a level 2 entity, do next. We will configure level 2
                    if level_2_key == dict_1_row[3] and dict_1_row[5] == level_2_entity[0]:
                        level_2_base_uri = level_1_instance_uri.format('/' + level_2_entity[0].replace('URI -', '').strip() + '{}')

                        if main_entity == 'molecule':

                            for level_3_key, level_3_value in level_2_value.items():
                                level_2_instance_uri = level_2_base_uri.format('/' + str(level_2_auto_generated_id) + '{}')
                                level_2_type_triple = type_triple.format(level_2_instance_uri.format(''),replace_baseURI_prefix(level_2_entity[2]))

                                # Tripleta con la relación a la referencia, tripleta con rdf:type, triple con refSource y otra with refId
                                file_ttl += empty_triple.format(level_1_instance_uri.format(''),replace_baseURI_prefix(dict_1_row[4]), level_2_instance_uri.format(''))
                                file_ttl += level_2_type_triple
                                file_ttl += empty_triple.format(level_2_instance_uri.format(''), base_uri.format('refSource'), '"{}"'.format(level_3_key))
                                file_ttl += empty_triple.format(level_2_instance_uri.format(''), base_uri.format('refId'), '"{}"'.format(rdf_encode(list_to_string(level_3_value))))

                                level_2_auto_generated_id += 1
                        else:

                            for level_3_element in level_2_value:
                                level_2_instance_uri = level_2_base_uri.format('/' + str(level_2_auto_generated_id) + '{}')
                                level_2_type_triple = type_triple.format(level_2_instance_uri.format(''),replace_baseURI_prefix(level_2_entity[2]))
                                # Tripleta con la relación a la referencia, tripleta con rdf:type
                                # file_ttl += empty_triple.format(level_2_instance_uri.format(''),base_uri.format('refSource'),'"{}"'.format(level_3_key))
                                # file_ttl += empty_triple.format(level_2_instance_uri.format(''),base_uri.format('refId'),'"{}"'.format(','.join(level_3_value)))

                                file_ttl += empty_triple.format(level_1_instance_uri.format(''),replace_baseURI_prefix(dict_1_row[4]), level_2_instance_uri.format(''))
                                file_ttl += level_2_type_triple
                                level_2_auto_generated_id += 1

                                if main_entity == 'indications':
                                    ############# LEVEL 3 ########
                                    level_3_auto_generated_id = 0

                                    for level_3_key, level_3_value in level_3_element.items():
                                        for dict_2_row in main_dict[main_entity]:
                                            # If the field is in the config dict and the range is a level 3 entity, do next. We will configure level 2
                                            if level_3_key == dict_2_row[3] and dict_2_row[5] == level_3_entity[0]:
                                                level_3_base_uri = level_2_instance_uri.format('/' + level_3_entity[0].replace('URI -', '').strip()+'{}')


                                                for level_4_item in level_3_value:
                                                    #print(level_4_item)
                                                    for reference_id in level_4_item['ids']:
                                                        level_3_instance_uri = level_3_base_uri.format('/' + str(level_3_auto_generated_id))

                                                        level_3_type_triple = type_triple.format(level_3_instance_uri.format(''),replace_baseURI_prefix(level_3_entity[2]))
                                                        # Triple with relation to reference from indication, indication-reference type, source and id
                                                        file_ttl += empty_triple.format(level_2_instance_uri.format(''),replace_baseURI_prefix(dict_2_row[4]),level_3_instance_uri.format(''))
                                                        file_ttl += level_3_type_triple
                                                        file_ttl += empty_triple.format(level_3_instance_uri, base_uri.format('refSource'), comillas(level_4_item['source']))
                                                        file_ttl += empty_triple.format(level_3_instance_uri, base_uri.format('refId'), comillas(reference_id))

                                                        level_3_auto_generated_id += 1

                                            # If the field is just level 2 end the ttl
                                            elif level_3_key == dict_2_row[3] and dict_2_row[0] == "2":

                                                if dict_2_row[4] == "":
                                                    predicate = dict_2_row[3]
                                                else:
                                                    predicate = remove_baseURI_prefix(dict_2_row[4])

                                                file_ttl += base_triple.format(level_2_instance_uri.format(''), predicate, comillas(level_3_value))


                                else:
                                    #rint(level_3_element)
                                    for level_3_key, level_3_value in level_3_element.items():
                                        for dict_2_row in main_dict[main_entity]:
                                            if dict_2_row[0] == "2" and level_3_key == dict_2_row[3]:
                                                if dict_2_row[4] == "":
                                                    predicate = base_uri.format(dict_2_row[3])

                                                elif not dict_2_row[4].startswith('baseURI:'):
                                                    predicate = dict_2_row[4]
                                                else:
                                                    predicate = base_uri.format(remove_baseURI_prefix(dict_2_row[4]))

                                                file_ttl += empty_triple.format(level_2_instance_uri.format(''),predicate, comillas(rdf_encode(list_to_string(level_3_value))))
                    # Si es nivel 1 y el key actual está en el archivo de configuración
                    elif dict_1_row[0] == "1" and level_2_key == dict_1_row[3]:
                        # If the predicate already exists, we use it, otherwise we create depending on if it is already established with baseuri or not. For the latter we create it from the name.
                        if dict_1_row[4] == "":
                            predicate = base_uri.format(dict_1_row[3])

                        elif not dict_1_row[4].startswith('baseURI:'):
                            predicate = dict_1_row[4]
                        else:
                            predicate = base_uri.format(remove_baseURI_prefix(dict_1_row[4]))
                        # If the field refers to another entity.
                        if dict_1_row[5].startswith('URI -'):
                            base_object_uri = base_uri.format(remove_baseURI_prefix(dict_1_row[5])+'/{}')
                        else:
                            base_object_uri = '{}'
                            #print(base_object_uri)
                        if isinstance(level_2_value, list):
                            for each_object in level_2_value:
                                file_ttl += empty_triple.format(level_1_instance_uri.format(''), predicate, base_object_uri.format(comillas(rdf_encode(each_object))))
                        elif isinstance(level_2_value, dict):
                            #print(level_2_value)
                            if 'count' in level_2_value and level_2_value['count'] > 0:
                                for entity_id in level_2_value['rows']:
                                    file_ttl += empty_triple.format(level_1_instance_uri.format(''), predicate,base_object_uri.format(entity_id))
                            else:
                                file_ttl += empty_triple.format(level_1_instance_uri.format(''), predicate,comillas(rdf_encode(list_to_string(level_2_value))))
                        else:
                            file_ttl += empty_triple.format(level_1_instance_uri.format(''), predicate,base_object_uri.format(comillas(rdf_encode(level_2_value))))

                        # else:
                        #     file_ttl += empty_triple.format(level_1_instance_uri.format(''),predicate, comillas(rdf_encode(list_to_string(level_2_value))))


    return file_ttl



for key, value in filepaths.items():
    path = f'/media/newbuntu/rdfal/NEW AGE/OpenTargets/Data/Drug/{value}'
    # Change the directory
    os.chdir(path)

    # Define current main_entity
    main_entity = key

    # Define level-1, level-2 and leve-3 classes
    level_1_entity = [None, None, None]
    level_2_entity = [None, None, None]
    level_3_entity = [None, None, None]
    for row in main_dict[key]:
        # Extract level name and construct type
        if row[0] == '1' and row[2] == 'URI':
            level_1_entity[0] = row[1] # URI level name
            level_1_entity[1] = row[3] # URI construct type
        elif row[0] == '2' and row[2] == 'URI':
            level_2_entity[0] = row[1] # URI level name
            level_2_entity[1] = row[3] # URI construct type
        elif row[0] == '3' and row[2] == 'URI':
            level_3_entity[0] = row[1] # URI level name
            level_3_entity[1] = row[3] # URI construct type
        # Extract class
        if row[0] == '1' and row[3] == 'a':
            level_1_entity[2] = row[5]
        elif row[0] == '2' and row[3] == 'a':
            level_2_entity[2] = row[5]
        elif row[0] == '3' and row[3] == 'a':
            level_3_entity[2] = row[5]

    level_1_auto_generated_id = 0
    # Loop over files
    for file in os.listdir():
        # Check whether file is in json format or not


        if file.endswith(".json"):
            file_path = f"{path}{file}"

            # call read text file function
            toprint = (read_text_file(file_path))
            turtle += toprint

with open('/home/dinforma/Downloads/output.ttl', 'w') as f:
    f.write(turtle)

