from AA_config_data import *
import subprocess

for entity_data in ENTITIES_DATA_DICTS_LIST:

    entity_name = entity_data['name_to_save']
    ftp_full_link = BASE_FTP_LINK + entity_name
    # data_write_folder = data_write_path + entity_name

    # Use wget with parameters to download the file
    subprocess.run(['wget', '--recursive', '--no-parent', '--no-host-directories', '--cut-dirs=8', '-P', DATA_BASE_PATH, ftp_full_link])
