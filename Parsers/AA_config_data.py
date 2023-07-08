base_uri_prefix = "otgs"
BASE_URI = "<http://mdata.com{}>"

# Initialize ontology in Turtle format
# Prefixes are required for the correct interpretation of the ontology
TTL_INIT = f"""
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

BASE_PATH = '/media/newbuntu/rdfal/NEW AGE/OpenTargets/'

RDF_WRITE_PATH = BASE_PATH + 'RDF_data/'

CSV_WRITE_PATH = BASE_PATH + 'csv_data/'

DATA_BASE_PATH = BASE_PATH + 'Data/'


ENTITIES_DATA_DICTS_LIST = [
            # {'main_entity': 'Target', 'data_path': 'Data/Target/targets', 'name_to_save': 'targets'},
            # {'main_entity': 'Disease', 'data_path': 'Data/Disease_Phenotype/', 'name_to_save': 'diseases'},
            # {'main_entity': 'Drug', 'data_path': 'Data/Drug/', 'name_to_save': 'molecule'},
            # {'main_entity': 'Evidence', 'data_path': 'Data/Target - Disease evidence/evidence/', 'name_to_save': 'evidence'},
            # {'main_entity': 'AssociationByOverallDirect', 'data_path': 'Data/Target - Disease associations/', 'name_to_save': 'associationByOverallDirect'},
            # {'main_entity': 'AssociationByOverallIndirect', 'data_path': 'Data/Target - Disease associations/associationByOverallIndirect', 'name_to_save': 'associationByOverallIndirect'},
            # {'main_entity': 'AssociationByDatasourceDirect', 'data_path': 'Data/Target - Disease associations/associationByDatasourceDirect', 'name_to_save': 'associationByDatasourceDirect'},
            # {'main_entity': 'AssociationByDatasourceIndirect', 'data_path': 'Data/Target - Disease associations/associationByDatasourceIndirect', 'name_to_save': 'associationByDatasourceIndirect'},
            # {'main_entity': 'AssociationByDatatypeDirect', 'data_path': 'Data/Target - Disease associations/associationByDatatypeDirect',  'name_to_save': 'associationByDatatypeDirect'},
            # {'main_entity': 'AssociationByDatatypeIndirect', 'data_path': 'Data/Target - Disease associations/associationByDatatypeIndirect', 'name_to_save': 'associationByDatatypeIndirect'},
            # {'main_entity': 'MolecularInteraction', 'data_path': 'Data/Target/interaction', 'name_to_save': 'interaction'},
            {'main_entity': 'InteractionEvidence', 'data_path': 'Data/Target/interactionEvidence', 'name_to_save': 'interactionEvidence'},
            {'main_entity': 'BaselineExpression', 'data_path': 'Data/Target/baselineExpression', 'name_to_save': 'baselineExpression'},
            {'main_entity': 'GoAnnotation', 'data_path': 'Data/Target/go', 'name_to_save': 'go'},
            {'main_entity': 'MousePhenotype', 'data_path': 'Data/Target/mousePhenotypes', 'name_to_save': 'mousePhenotypes'},
            {'main_entity': 'ClinicalSignsAndSymptoms', 'data_path': 'Data/ClinicalSignsAndSymptoms/', 'name_to_save': 'diseaseToPhenotype'},
            {'main_entity': 'HumanPhenotype', 'data_path': 'Data/Human Phenotype Ontology/', 'name_to_save': 'hpo'},
### DRUGS and annotations
            {'main_entity': 'MechanismOfAction', 'data_path': 'Data/Drug/mechanismOfAction', 'name_to_save': 'mechanismOfAction'},
            {'main_entity': 'Drug', 'data_path': 'Data/Drug/indication', 'name_to_save': 'indication'},
#             {'main_entity': 'SignificantAdverseDrugReactions', 'data_path': 'Data/Drug/significantAdverseDrugReactions', 'name_to_save': 'fda/significantAdverseDrugReactions'},
            {'main_entity': 'DrugWarnings', 'data_path': 'Data/Drug/drugWarnings', 'name_to_save': 'drugWarnings'},

            {'main_entity': 'Reactome', 'data_path': 'Data/Drug/mechanismOfAction', 'name_to_save': 'reactome'},
            {'main_entity': 'TargetsPriorisation', 'data_path': 'Data/Drug/mechanismOfAction', 'name_to_save': 'targetsPriorisation'},
            {'main_entity': 'TargetEssentiality', 'data_path': 'Data/Drug/mechanismOfAction', 'name_to_save': 'targetEssentiality'},
]

# Prefixes for each type of main entity in OpenTargets, Target, Drug and Disease or Phenotype.
TYPE_PREFIXES = {'Drug': ('CHEMBL'),
                 'Disease':   ('EFO_', 'MONDO_', 'GO_', 'DOID_', 'Orphanet_', 'OTAR_', 'HP_'),
                 'Target':   ('ENS')
                 }

# Predicates to exclude prefix conversion to entities when it's used
PREFIX_EXCLUDING_PREDICATES = ['name', 'id']


#### DOWNLOAD DATA FROM OPENTARGETS ####

current_data_version = '23.06'

BASE_FTP_LINK = f'ftp://ftp.ebi.ac.uk/pub/databases/opentargets/platform/{current_data_version}/output/etl/json/'