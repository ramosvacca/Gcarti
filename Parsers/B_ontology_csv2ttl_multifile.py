import os
import re
import pandas as pd
from config.AA_config_data import *
from .helper_functions import *


def split_camel_case(s):
    """
    Split camel case words into separate words with spaces in between.
    :param s: string in camel case.
    :return: string with camel case split into words with space.
    """
    return re.sub('([a-z])([A-Z])', r'\1 \2', s)


def add_class_to_ontology(class_name, classes_dict):
    """
    Add a class to ontology if it's not already present.
    :param class_name: the name of the class to be added.
    :param classes_dict: dictionary to track added classes.
    :return: Turtle format string to add class to ontology.
    """
    if class_name not in classes_dict:
        classes_dict[class_name] = True
        return f"\n\n{class_uri_prefix}:{class_name} a owl:Class ; \n\trdfs:label \"{split_camel_case(class_name).title()}\" ."
    return ''


def add_property_to_ontology(property_name, property_info):
    """
    Add a property to ontology based on its type.
    :param property_name: the name of the property to be added.
    :param property_info: the property information including domain, range, and type.
    :return: Turtle format string to add property to ontology.
    """
    ptype = property_info['type']
    if property_info["range"] is not None and "URI -" in property_info["range"]:
        ptype = 'object property'
    property_string = f"\n\n{base_uri_prefix}:{property_name} a "
    property_string += {
                           "datatype property": "owl:DatatypeProperty",
                           "object property": "owl:ObjectProperty",
                           "annotation property": "owl:AnnotationProperty"
                       }.get(ptype, "rdf:Property") + " ;"

    # If the property is not an annotation property, add domain and range if they exist

    if ptype != "annotation property":
        if property_info["domain"] is not None:
            property_string += f"\n\trdfs:domain {class_uri_prefix}:{property_info['domain']} ;"
        if property_info["range"] is not None:
            # If the range is a class, add it with the correct prefix
            if "URI -" in property_info["range"]:
                property_string += f"\n\trdfs:range {class_uri_prefix}:{property_info['range'].split('-')[1].strip()} ;"
            # If the range is a data type, add it as it is
            else:
                property_string += f"\n\trdfs:range xsd:{property_info['range']} ;"

    property_string += f"\n\trdfs:label \"{split_camel_case(property_name).title()}\" ."
    return property_string


# Define variables for URIs
base_uri_prefix = "otgs"
class_uri_prefix = "otgs"

def get_onto_from_csv():
    # Fetch all csv files in the directory excluding 'otDrug.csv'
    all_filenames = [f for f in os.listdir(CSV_WRITE_PATH) if f.endswith('.csv') and f != 'otDrug.csv']

    # Combine all csv files into a pandas DataFrame
    combined_csv_data = pd.DataFrame()  # start with an empty DataFrame
    for f in all_filenames:
        print(f)
        data = pd.read_csv(os.path.join(CSV_WRITE_PATH, f), sep='|', keep_default_na=False)
        print(f"Data from {f}:\n", data)  # print data from the current file
        combined_csv_data = pd.concat([combined_csv_data, data])  # concatenate the data

    # Initialize ontology in Turtle format
    turtle = TTL_INIT

    # Dictionaries to store found properties and classes
    properties_dict = {}
    classes_dict = {}

    # Loop over rows in DataFrame
    for _, row in combined_csv_data.iloc[1:].iterrows():
        # Extract the class name from domain
        class_name = row[1].split("-")[1].strip()

        # Add the class to ontology
        turtle += add_class_to_ontology(class_name, classes_dict)

        # Extract the property name and domain class name
        domain_class_name = row[1].split("-")[1].strip()
        property_name = row[3].replace(" ", "")

        # Replace base URI prefix from predicate to get the property name
        if row[4].startswith("baseURI:" + base_uri_prefix):
            property_name = row[4].replace(base_uri_prefix + ":", "")

        # Check and update the properties dictionary with new property details
        if property_name not in properties_dict:
            properties_dict[property_name] = {"domain": domain_class_name, "range": row[5], "type": row[2]}
        else:
            # Update domain and range to None if they differ across multiple properties with the same name
            if properties_dict[property_name]["range"] != row[5]:
                properties_dict[property_name]["range"] = None
            properties_dict[property_name]["domain"] = None

    # Add all the properties to ontology
    turtle += ''.join(add_property_to_ontology(name, info) for name, info in properties_dict.items())

    print(turtle)  # Optionally, you can save the ontology to a file
    with open(ONTOLOGY_WRITE_PATH + 'ontology.ttl', 'w') as f:
         f.write(turtle)

