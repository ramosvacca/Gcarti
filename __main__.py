import multiprocessing
import concurrent.futures
from Parsers import B_ontology_csv2ttl_multifile
from Parsers.B_parser import process_folder_data
from Parsers.A_wget_data import download_data
from config.AA_config_data import *
import math
import logging
import time

"""
This main script divides the main list len in equal chunks (cores) to process them 
as threads to download the data for each entity (/Data folder) and then to process 
each entity making the data ttl (/RDF_data) and the csv files (/csv_data)
which later will be the input to generate the ontology.
"""

# Set up logging with timestamps
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.info('Starting script...')

num_cores = multiprocessing.cpu_count()

logging.info(f'Number of cores: {num_cores}')

def worker_function(chunk):
    for item in chunk:
        logging.info(f'Starting download for item: {item["name_to_save"]}')
        download_data([item])
        logging.info(f'Starting data processing for item: {item["name_to_save"]}')
        process_folder_data([item])
        logging.info(f'Finished processing for item: {item["name_to_save"]}')

# worker_function([{'name_to_save':'evidence/sourceId=europepmc', 'main_entity': 'Evidence',}])

chunk_size = math.ceil(len(ENTITIES_DATA_DICTS_LIST) / num_cores)

chunks = [ENTITIES_DATA_DICTS_LIST[i:i + chunk_size] for i in range(0, len(ENTITIES_DATA_DICTS_LIST), chunk_size)]
logging.debug(f'Chunks: {chunks}')

processes = []

logging.info('Starting multiprocessing...')

# Create and start one process at a time with a delay
for chunk in chunks:

    p = multiprocessing.Process(target=worker_function, args=(chunk,))
    processes.append(p)
    p.start()
    time.sleep(6)  # delay for 1 second

# Wait for all processes to finish
for p in processes:
    p.join()

logging.info('Finished multiprocessing')

B_ontology_csv2ttl_multifile.get_onto_from_csv()

logging.info('Script finished.')