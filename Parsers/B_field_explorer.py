import os, json
from config.AA_config_data import *


def capital_first_char(word):
    return word[0].upper() + word[1:]


def read_text_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        file_set = dict()
        for line in lines:
            json_line = json.loads(line)
            # if json_line['chemblIds'] == ['CHEMBL786', 'CHEMBL83']:
            #     print(json_line)
            # print(json_line)
            for key, value in json_line.items():
                if key not in file_set:

                    file_set[key] = value

                elif key in file_set and type(value) == list and len(file_set[key]) < len(value) :

                    file_set[key] = value

        return file_set


def check_if_entity(key_to_verify, str_to_verify):
    for entity_type in TYPE_PREFIXES:
        # Check if the string representation of t_object starts with the current prefix
        if key_to_verify not in PREFIX_EXCLUDING_PREDICATES and str(str_to_verify).startswith(TYPE_PREFIXES[entity_type]):
            # Format t_object by appending entity type and original t_object to base URI
            # value = AA_config_data.base_uri.format(f'/{entity_type}/{value}')
            return 'URI - ' + entity_type


# Helper function to create and return a CSV output line
def append_csv_output(level, parent_level_name, key, value, range_val, has_next_level):
    """Creates a list with CSV data.

    Parameters:
    level (int): Current processing level.
    parent_level_name (str): Name of the parent level.
    key (str): Key from the input dictionary.
    value (varies): Value corresponding to the key in the input dictionary.
    range_val (str): Data type of the value.
    has_next_level (bool): Flag to indicate if there's a next level in the dictionary.

    Returns:
    list: A list containing the CSV data.
    """
    return [level, parent_level_name, "", key, "", range_val, value, has_next_level]


# Main function to convert a dictionary to a CSV format
def dict_to_csv(input=None, level=1, level_name=None, has_next_level=False):
    """Converts a nested dictionary to a CSV-like nested list structure.

    Parameters:
    input (dict, optional): Input dictionary to process.
    level (int, optional): Current processing level.
    level_name (str, optional): Name of the current level.
    has_next_level (bool, optional): Flag to indicate if there's a next level in the dictionary.

    Returns:
    list: A nested list representing the CSV format of the input dictionary.
    """
    parent_level_name = 'URI - ' + level_name
    csv_output = []

    for key, value in input.items():
        # If value is a dictionary and 'rows' key is present, replace value with the value of 'rows'
        if isinstance(value, dict) and 'rows' in value:
            value = value['rows']

        # If value is a dictionary, recursively process the nested dictionary
        if isinstance(value, dict):
            csv_output.append(append_csv_output(level, parent_level_name, key, value, 'URI - ' + capital_first_char(key), True))
            csv_output += dict_to_csv(input=value, level=level + 1, level_name=capital_first_char(key), has_next_level=False )

        # If value is a list and first element is a dictionary, recursively process the nested dictionary
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            csv_output.append(append_csv_output(level, parent_level_name, key, value, 'URI - ' + capital_first_char(key), True))
            csv_output += dict_to_csv(input=value[0], level=level + 1, level_name=capital_first_char(key), has_next_level=False)

        # If value is a normal field (list, integer, decimal or string), append it to the csv_output list
        else:
            if isinstance(value, list) and not value:
                continue
            range_val = 'list' if isinstance(value, list) else 'integer' if isinstance(value, int) else 'decimal' if isinstance(value, float) else 'string'
            check_range = check_if_entity(key, value[0] if isinstance(value, list) else value)
            if check_range is not None:
                range_val = check_range
            csv_output.append(append_csv_output(level, parent_level_name, key, value, range_val, False))

    return csv_output


def get_output(type_of_output='csv', eval_path=None, level_name=None, csv_save_folder=None, save_name=None):
    final_dict = dict()

    # Change the directory
    os.chdir(eval_path)

    for dirpath, dirs, files in os.walk(eval_path):
        for file_name in files:
            if file_name.endswith(".json"):
                file_path = os.path.join(dirpath, file_name)
                # Call the function to read json file
                final_dict.update(read_text_file(file_path))
    output = dict_to_csv(input=final_dict, level_name=level_name)
    # Print the result

    to_print = 'level|parent|property_type|name_in_dataset|predicate|range|example|has_next_level\n'
    for row in output:

        to_print += ('|'.join(str(x).replace('|', '-') for x in row)) + '\n'

    if csv_save_folder is not None:
        with open(f'{csv_save_folder}{save_name}.csv', 'w') as output_file:
            output_file.write(to_print)

    if type_of_output == 'csv':
        return to_print

    else:
        return output
# Use the function to convert dictionary to the required CSV-like list of lists



# get_output()
# print(get_output(level_name='Drug'))


