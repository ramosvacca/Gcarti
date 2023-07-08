# OpenTargets to RDF conversion tool

The OpenTarget2RDF tool offers convenient and efficient way to migrate the OpenTargets datasets to serialized TTL files constructing an ontology data model inferred from the data fields and its links, identifying entities to achieve a model. This tool provides methods for creating and maintaining RDF data.

## Requirements

Python 3.10+ is supported. 

Necessary libraries are in requirements.txt

## Installation

### notes
It is highly recommended to perform the install in a virtualenv environment.

Use the pip install -r requirements.txt command to install all of the Python modules and packages listed in your requirements.txt file.

You will need ~200 GB to download dataset and resulting files.

The entire process takes ~8 hours. 

### Procedure

Clone the repository to your local machine and specify the main folder to work on with required data (inputs and outputs). Separate folders for downloaded datasets, output TTL, CSV and ontologies TTL will be created.
The main folder can be specified in the config_data.py file under the variable name BASE_PATH.

Create virtual environment and run pip to install required libraries in requirements.txt

## Usage

Execute the project with the configured python interpreter.
Alternatively, run the __main__.py file.