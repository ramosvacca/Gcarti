import json
from AA_helper_functions import *
import B_field_explorer as field_explorer
from AA_config_data import *

"""
rdf_write_path:             Where RDF files are to be saved
main_dict:                  Main dictionary when executing the script
data_dictionaries:          List containing the data dictionaries. One for each folder to process, explained in config data
base_path:                  Base path where data was downloaded from OT
prefixes                    Prefixes to recognize entity by type
exclude_convert_to_entity:  Predicates that exclude predicate conversion to entity URI
csv_write_folder_path:      Path to save CSV files
"""

main_dict = {}

type_triple = "{} rdf:type {} ."
base_triple = "{} <http://mdata.com/{}> {} ."
# class_uri = "<http://mdata.com/{}>"
empty_triple = "{} {} {} ."


def triple_to_ttl(t_subject, t_predicate, t_object, print_file):
    """
    The purpose of this function is to format the object of a RDF triple, `t_object`, according to a set of predefined prefixes.
    The function tries to match the beginning of `t_object` with one of the predefined prefixes. If a match is found, it appends the
    entity type and the original `t_object` to a base URI. If no match is found, it simply prints a message. The final step is to print
    the RDF triple into a predefined format and write it to `print_file`.

    Args:
    t_subject (str): The subject of the RDF triple.
    t_predicate (str): The predicate of the RDF triple.
    t_object (str): The object of the RDF triple to be formatted.
    print_file (file object): The file object where the output will be written.
    """

    # Initialize a flag to track if a matching prefix has been found
    matched = False

    # Iterate over each entity type in the prefixes dictionary
    for entity_type in TYPE_PREFIXES:
        # Check if the string representation of t_object starts with the current prefix
        if t_predicate not in PREFIX_EXCLUDING_PREDICATES and str(t_object).startswith(TYPE_PREFIXES[entity_type]):
            # Format t_object by appending entity type and original t_object to base URI
            t_object = BASE_URI.format(f'/{entity_type}/{t_object}')
            # Set flag to True indicating a match has been found
            matched = True
            # Exit loop as a matching prefix has been found
            break

    # If no matching prefix found, print a message
    if not matched:
        t_object = comillas(t_object)

    # Format and print the RDF triple, writing it to print_file
    print(empty_triple.format(t_subject, BASE_URI.format('/' + t_predicate), t_object), file=print_file)


def process_row(current_row, properties_array, is_auto_id, auto_id_counter, row_base_uri, current_entity_full_name,
                ttl_file, parent_entity=None):
    """
    Function to process each row in the JSON file, where each row corresponds to an entity or associated info.
    The function constructs an RDF triple for each field in the entity, and writes it to a ttl file.

    Args:
    current_row (dict): Dictionary representing a row of data to be processed.
    properties_array (list): List of all the properties in the data.
    is_auto_id (bool): Flag indicating whether automatic id generation is enabled.
    auto_id_counter (int): Counter for generating automatic ids.
    row_base_uri (str): The base URI for the current row.
    current_entity_full_name (str): The full name of the current entity.
    ttl_file (file object): The ttl file to write output to.
    parent_entity (str, optional): The parent entity of the current row. Defaults to None.
    """

    # Remove the base URI prefix from the current entity's full name to create the base entity name
    base_entity_name = remove_baseURI_prefix(current_entity_full_name)

    # Format the URI for the current entity using the row's base URI and the base entity name
    base_entity_uri = row_base_uri.format('/' + capital_first_char(base_entity_name) + '{}')

    # If automatic id generation is enabled, use the auto id counter as the row id;
    # otherwise, use the 'id' field from the current row
    row_id = str(auto_id_counter) if is_auto_id else str(current_row['id'])

    # Format the URI for this instance of the entity and construct the type triple
    instance_uri = base_entity_uri.format('/' + row_id + '{}')
    row_type_triple = type_triple.format(instance_uri.format(''),
                                         BASE_URI.format('/' + capital_first_char(base_entity_name)))

    # Write the type triple to the ttl file
    print(row_type_triple, file=ttl_file)

    # If there is a parent entity
    if parent_entity is not None:
        # Check if the current row is a dictionary and contains 'rows'
        if isinstance(current_row, dict) and 'rows' in current_row:
            # Process each value in 'rows' and write the triple to the ttl file
            for value in current_row['rows']:
                triple_to_ttl(BASE_URI.format('' + parent_entity), base_entity_name, value, print_file=ttl_file)
            return
        else:
            # Write the relation triple between the parent entity and this entity to the ttl file
            print(empty_triple.format(BASE_URI.format('' + parent_entity), BASE_URI.format('/' + base_entity_name),
                                      instance_uri.format('')), file=ttl_file)

    # Iterate over each field in the current row
    for key, value in current_row.items():
        # If the value is a nested dictionary, recursively process it
        if isinstance(value, dict):
            # Determine whether the sub-entity needs an automatic id
            sub_is_auto_id = not any(prop_row[1] == key and prop_row[3] == 'id' for prop_row in properties_array)
            # Construct the URI suffix for this sub-entity
            current_entity_suffix = str(parent_entity) + '/' + capital_first_char(base_entity_name) + '/' + row_id
            # Recursively process this sub-entity
            process_row(value, properties_array, sub_is_auto_id, 0, instance_uri, 'URI - ' + key, ttl_file,
                        parent_entity=current_entity_suffix)

        # If the value is a list```python
        # of dictionaries, process each dictionary in the list
        elif isinstance(value, list):
            # Determine whether the sub-entity needs an automatic id
            sub_is_auto_id = not any(prop_row[1] == key and prop_row[3] == 'id' for prop_row in properties_array)
            # Initiate a counter for the sub-entities
            sub_auto_id_counter = 0
            # Construct the URI suffix for this sub-entity
            parent_entity = str(parent_entity) if parent_entity is not None else ''
            current_entity_suffix = str(parent_entity) + '/' + capital_first_char(base_entity_name) + '/' + row_id

            # Process each dictionary in the list
            for sub_row in value:
                if isinstance(sub_row, dict):
                    process_row(sub_row, properties_array, sub_is_auto_id, sub_auto_id_counter, instance_uri,
                                'URI - ' + key,
                                ttl_file, parent_entity=current_entity_suffix)
                else:
                    # If the value is a list of strings, format the predicate and object, then print the triple
                    item_object = sub_row
                    triple_to_ttl(instance_uri.format(''), key, item_object, ttl_file)
                sub_auto_id_counter += 1

        else:
            # If the value is a simple field, format the predicate and object, then print the triple
            item_object = value
            triple_to_ttl(instance_uri.format(''), key, item_object, ttl_file)


def evaluate_folder(eval_path=None, level_name=None, save_name=None, auto_id_n=0, folder_data=None):
    """
    Function to evaluate the content of a folder, process each JSON file, and save the result in a .ttl file.

    Args:
    eval_path (str, optional): Path of the folder to evaluate. If not specified, the current working directory is used.
    level_name (str, optional): Name of the level. Defaults to None.
    save_name (str, optional): Name of the output .ttl file. Defaults to None.
    auto_id_n (int, optional): Starting number for auto generated ids. Defaults to 0.

    Returns:
    auto_id_n (int): The last auto generated id used.
    """

    # Obtain the properties array using field_explorer
    properties_array = field_explorer.get_output(type_of_output='list', eval_path=eval_path, level_name=level_name, csv_save_folder=CSV_WRITE_PATH, save_name=save_name)
    print('Properties array -> OK')

    # Determine the base entity full name from the properties array
    base_entity_full_name = next(row[1] for row in properties_array if row[0] == 1)

    # Determine if automatic id is enabled for the base entity
    base_auto_id = not any(prop_row[1] == base_entity_full_name and prop_row[3] == 'id' for prop_row in properties_array)

    # Get all JSON file paths in the evaluation path
    file_paths = [os.path.join(dirpath, file_name) for dirpath, _, files in os.walk(eval_path) for file_name in files if file_name.endswith(".json")]

    # Open the output ttl file
    with open(f'{RDF_WRITE_PATH}{folder_data["main_entity"]}_{save_name}.ttl', 'w') as output_file:
        # Process each JSON file
        for file_path in file_paths:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                for row in lines:
                    row = json.loads(row)
                    # Process each row and write the result to the output file
                    process_row(row, properties_array, base_auto_id, auto_id_n, BASE_URI, base_entity_full_name, output_file)
                    auto_id_n += 1

    # Return the last auto generated id used
    return auto_id_n


def process_folder_data(list_of_dict):
    """
    Function to process data in the specified folders.

    Parameters:
    main_data (list): A list of dictionaries, where each dictionary represents a folder and contains:
        - 'data_path': Relative path to the data folder
        - 'main_entity': The main entity in the data
        - 'name_to_save': The name used for saving the processed data

    base_path (str): The base path to the data folders

    Returns:
    None
    """
    # Iterate over all folder data in the provided list
    for folder_data in list_of_dict:

        # Initialize auto id counter
        auto_id_n = 0

        # Generate the path to the folder to be evaluated
        folder_path_to_evaluate = DATA_BASE_PATH + folder_data['name_to_save']

        # Get subfolder paths
        subfolder_paths = get_subfolder_paths(folder_path_to_evaluate)

        # If subfolder paths exist
        if subfolder_paths:

            # Iterate over each subfolder name and path
            for name, path in subfolder_paths.items():
                print(name, path)  # Printing the subfolder name and path

                # Evaluate the subfolder and update the auto_id_n
                auto_id_n = evaluate_folder(eval_path=path, level_name=folder_data['main_entity'],
                                            save_name=name, auto_id_n=auto_id_n, folder_data=folder_data)

        else:
            # Append the name to save to the folder path to evaluate
            folder_path_to_evaluate = folder_path_to_evaluate# + folder_data['name_to_save']
            print(folder_path_to_evaluate)

            file_name_to_save = folder_data['name_to_save'].replace('/','_')

            # Evaluate the folder
            evaluate_folder(eval_path=folder_path_to_evaluate, level_name=folder_data['main_entity'],
                            save_name=file_name_to_save, folder_data=folder_data)


process_folder_data(ENTITIES_DATA_DICTS_LIST)
