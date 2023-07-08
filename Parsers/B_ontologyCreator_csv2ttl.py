import re
import pandas as pd
import AA_config_data

# Function to split CamelCase words into separate words with spaces in between
def split_camel_case(s):
    return re.sub('([a-z])([A-Z])', r'\1 \2', s)

# Define variables for URIs
base_uri_prefix = "otgs"
class_uri_prefix = "otgs"

# Read the CSV file
df = pd.read_csv('/home/dinforma/Downloads/otDrugs.csv', keep_default_na=False, header=None)

# Initialize ontology in Turtle format
# Prefixes are required for the correct interpretation of the ontology
turtle = AA_config_data.TTL_INIT

# Dictionary to store found properties and their domain and range
properties_dict = {}

# Dictionary to store found classes
classes_dict = {}

# Loop over rows in dataframe
for index, row in df.iterrows():
    depth = row[1]
    domain = row[2]
    ptype = row[3]
    name = row[4]

    # Replace "baseURI:" with the base_uri defined above in predicate
    predicate = row[5].replace("baseURI:", base_uri_prefix + ":")

    range_ = row[6]

    # If it's a class
    if "URI" in ptype:
        # Extract the class name from domain
        class_name = domain.split("-")[1].strip()  # .strip() is used to remove leading and trailing spaces

        # Check if the class has already been added to the ontology
        if class_name not in classes_dict.keys():
            # Add the class to the turtle string
            turtle += f"\n\n{class_uri_prefix}:{class_name} a owl:Class ; \n\trdfs:label \"{split_camel_case(class_name).title()}\" ."
            classes_dict[class_name] = True

    # If it's a property
    elif depth != "0" and ptype != "Property" and depth != "":
        domain_class_name = domain.split("-")[1].strip()
        property_name = name.replace(" ", "")

        # If the predicate already exists and its prefix is not "otgs", then continue to the next iteration
        if predicate != "" and not predicate.startswith(base_uri_prefix):
            continue
        # If the predicate exists and its prefix is "otgs", replace the prefix with an empty string to get the property name
        elif predicate != "" and predicate.startswith(base_uri_prefix):
            property_name = predicate.replace(base_uri_prefix + ":", "")

        # Check if the property has already been added to the ontology
        if property_name not in properties_dict.keys():
            # Add the property to the properties dictionary with its domain, range, and type
            properties_dict[property_name] = {"domain": domain_class_name, "range": range_, "type": ptype}
        else:
            # If the property has already been seen and the range is different, remove the range
            if properties_dict[property_name]["range"] != range_:
                properties_dict[property_name]["range"] = None
            # Remove the domain as the property belongs to more than one class
            properties_dict[property_name]["domain"] = None

# Add properties to the ontology
for property_name, property_info in properties_dict.items():
    ptype = property_info['type']

    # Check the type of the property and add the property to the ontology as that type
    if ptype == "datatype property":
        turtle += f"\n\n{base_uri_prefix}:{property_name} a owl:DatatypeProperty ;"
    elif ptype == "object property":
        turtle += f"\n\n{base_uri_prefix}:{property_name} a owl:ObjectProperty ;"
    elif ptype == "annotation property":
        turtle += f"\n\n{base_uri_prefix}:{property_name} a owl:AnnotationProperty ;"

    # If the property is not an annotation property, add domain and range if they exist
    if ptype != "annotation property":
        if property_info["domain"] is not None:
            turtle += f"\n\trdfs:domain {class_uri_prefix}:{property_info['domain']} ;"
        if property_info["range"] is not None:
            # If the range is a class, add it with the correct prefix
            if "URI -" in property_info["range"]:
                turtle += f"\n\trdfs:range {class_uri_prefix}:{property_info['range'].split('-')[1].strip()} ;"
            # If the range is a data type, add it as it is
            else:
                turtle += f"\n\trdfs:range {property_info['range']} ;"

    # Add a label to the ontology with the property name in title format
    turtle += f"\n\trdfs:label \"{split_camel_case(property_name).title()}\" ."

print(turtle)

# Optionally, you can save the ontology to a file
# with open('ontology.ttl', 'w') as f:
#     f.write(turtle)
