import subprocess
from config.AA_config_data import *

def download_data (input_dicts_list):
    for entity_data in input_dicts_list:

        entity_name = entity_data['name_to_save']
        ftp_full_link = BASE_FTP_LINK + entity_name
        # data_write_folder = data_write_path + entity_name

        # Use wget with parameters to download the file
        subprocess.run(['wget', '--recursive', '--no-parent', '--no-host-directories', '--cut-dirs=8', '-P', DATA_BASE_PATH, ftp_full_link])
