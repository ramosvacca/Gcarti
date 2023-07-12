import os
from config import AA_config_data

base_uri = AA_config_data.BASE_URI

# class_uri = "<http://mdata.com/{}>"
def capital_first_char(word):
    return word[0].upper() + word[1:]

def comillas(inputText):
    return '"' + rdf_encode(str(inputText)) + '"'

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

def get_subfolder_paths(directory):
    """
    Function to get the paths of all subdirectories in a directory.

    Args:
    directory (str): The parent directory.

    Returns:
    dict/False: A dictionary mapping subdirectory names to their full paths. If there are no subdirectories, returns False.
    """

    # Initialize a dictionary to store the subdirectory names and paths
    subfolder_paths = {}

    # Iterate over all items in the directory
    for name in os.listdir(directory):
        full_path = os.path.join(directory, name)
        # If the item is a subdirectory, add it to the dictionary
        if os.path.isdir(full_path):
            subfolder_paths[name] = full_path

    # If there are no subdirectories, return False. Otherwise, return the dictionary
    return False if not subfolder_paths else subfolder_paths
