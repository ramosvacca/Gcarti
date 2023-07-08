#!/usr/bin/env python3

# Import relevant libraries to make HTTP requests and parse JSON response
import requests
import json
import sys

fileNameDRUGS = sys.argv[2]


def encomillar_texto(inputText):
    return '"' + str(inputText) + '"'


base_triple = "{} <urn:demo:healthcare:{}> {} .\n"

healthcare_drugs = []

with open(sys.argv[1], "r") as drugs_toread:
    for line in drugs_toread:
        healthcare_drugs += line.split(", ")

totalcount = len(healthcare_drugs)
basePrefix = "<urn:demo:healthcare:{}>"

# Build query string to get general information about AR and genetic constraint and tractability assessments
query_string = """
query drugLookUp ($chemblId: String!){
  drug(chemblId: $chemblId) {
    name
    id
    isApproved
    hasBeenWithdrawn
    blackBoxWarning
    synonyms
    tradeNames
    description
    linkedDiseases {
      count
      rows {
        id
        name
      }
    }

    mechanismsOfAction {
      rows {
        mechanismOfAction
      actionType
      }
    }

    crossReferences {
      source
      reference
    }

     adverseEvents{
      count
     rows{
      name
      count
      meddraCode
    }
    }

    drugWarnings {
      warningType
      description
      toxicityClass
      meddraSocCode
      year
    }
    indications {
      rows {

        maxPhaseForIndication
        disease {
          id
          name
          therapeuticAreas {
            id
            name
          }
        }
        references {
          ids
          source
        }
      }
    }

    knownDrugs (size: 10000){
      count
      cursor
      rows {
        phase
        status
        urls {
          name
          url
        }
        disease {
          id
          name
        }
        target {
          id
          approvedName
          approvedSymbol
        }
      }
    }
  }
}

"""

# Set variables object of arguments to be passed to endpoint


# Set base URL of GraphQL API endpoint
base_query_url = "https://api.platform.opentargets.org/api/v4/graphql"

file = open(fileNameDRUGS, 'w+')

for drugN in range(len(healthcare_drugs)):
    # subject = healthcare_drugs[drugN][0]
    variables = {"chemblId": healthcare_drugs[drugN]}
    # Perform POST request and check status code of response
    r = requests.post(base_query_url, json={"query": query_string, "variables": variables})

    # Transform API response from JSON into Python dictionary and file.write in console
    api_response = json.loads(r.text)['data']['drug']

    subject = "<urn:demo:healthcare:Medication:{}>".format(api_response['name'].replace(",", "").replace(" ", "_"))
    print(r.status_code, "Starting drug -> {}".format(subject))

    chemblId = "<https://www.ebi.ac.uk/chembl/compound_report_card/" + api_response['id'] + "/>"
    # print(chemblId)
    ## id and name
    file.write(
        subject + " <urn:demo:healthcare:has_chemblId> " + chemblId + " ; rdfs:label {} ; a <urn:demo:healthcare:Medication> .\n".format(
            encomillar_texto(api_response['name'])) + chemblId + " a <urn:demo:healthcare:externalId> .\n")

    ## comment description
    file.write("{} rdfs:comment {} .\n".format(subject, encomillar_texto(api_response['description'])))

    ##synonyms
    for synonym in api_response['synonyms']:
        file.write(base_triple.format(subject, 'has_synonym', encomillar_texto(synonym)))

    ##tradenames
    for tradename in api_response['tradeNames']:
        file.write(base_triple.format(subject, 'has_tradename', encomillar_texto(tradename)))

    ##isapproved
    file.write(base_triple.format(subject, 'is_approved', encomillar_texto(api_response['isApproved'])))

    ##withdrawn
    file.write(base_triple.format(subject, 'has_been_withdrawn', encomillar_texto(api_response['hasBeenWithdrawn'])))

    ## blackbox warning
    file.write(base_triple.format(subject, 'has_blackbox_warning', encomillar_texto(api_response['blackBoxWarning'])))

    ## linked diseases
    try:
        for row in api_response['linkedDiseases']['rows']:
            mondoId = "<https://www.pgscatalog.org/trait/" + row['id'] + "> "
            file.write(base_triple.format(subject, 'has_linked_disease',
                                          mondoId + " .\n" + mondoId + " a <urn:demo:healthcare:diseaseId> ; rdfs:label " + encomillar_texto(
                                              row['name'])))
    except:
        print('No linked diseases')

    ## mechanism of action

    for row in api_response['mechanismsOfAction']['rows']:
        file.write(base_triple.format(subject, 'has_mechanism_of_action', encomillar_texto(row['mechanismOfAction'])))

    ##Adverse events
    try:
        adv_n = 1
        for row in api_response['adverseEvents']['rows']:
            # print(row)

            rowiri = subject.replace(">", "/pharmacovigilance/" + str(adv_n) + ">")

            file.write(base_triple.format(subject, 'has_adverse_event', rowiri))

            file.write(
                "{} a <urn:demo:healthcare:drugPharmacovigilance> ; rdfs:label {}.\n".format(rowiri, encomillar_texto(row['name'])))

            file.write("{} {} {} .\n".format(rowiri, basePrefix.format("has_count"), row['count']))

            file.write("{} {} <{}> .\n".format(rowiri, basePrefix.format("has_url"),
                                               "https://identifiers.org/meddra:{}".format(row['meddraCode'])))

            file.write("<{}> a {} .\n".format("https://identifiers.org/meddra:{}".format(row['meddraCode']),
                                              basePrefix.format("externalId")))

            adv_n += 1


    except:
        print('no adeverse events')

    ## crossrefence
    try:
        for row in api_response['crossReferences']:
            file.write(
                "{} <http://www.geneontology.org/formats/oboInOwl#hasDbXref> '{}:{}' .\n".format(subject, row['source'],
                                                                                                 row['reference'][0]))
    except:
        print('NO cross references')

    ## KNOWN DRUGS - CLINICAL PRECEDENCE
    try:
        clin_n = 1
        # print("LONGITUD DE LA LISTA "+ str(len(api_response['knownDrugs']['rows'])))

        for row in api_response['knownDrugs']['rows']:
            # print(api_response['indications']['rows'][n])
            rowiri = subject.replace(">", "/knownDrug/" + str(clin_n) + ">")

            file.write("{} a <urn:demo:healthcare:knownDrug> .\n".format(rowiri))

            file.write(base_triple.format(subject, "has_clinical_precedence", rowiri))

            file.write("{} {} {} .\n".format(rowiri, basePrefix.format("has_phase"), row['phase']))

            file.write("{} {} {} .\n".format(rowiri, basePrefix.format("has_status"), encomillar_texto(row['status'])))

            file.write("{} {} {} .\n".format(rowiri, basePrefix.format("related_disease"),
                                             "<https://platform.opentargets.org/disease/{}>".format(
                                                 row['disease']['id'])))

            file.write(
                "<https://platform.opentargets.org/disease/{}> rdfs:label {} ; a <urn:demo:healthcare:diseaseId> .\n".format(
                    row['disease']['id'], encomillar_texto(row['disease']['name'])))

            target_uri = "<https://platform.opentargets.org/target/{}>".format(row['target']['id'])
            file.write("{} {} {} .\n".format(rowiri, basePrefix.format("has_target"), target_uri))

            file.write("{} {} {}; rdfs:label {} .\n".format(target_uri, basePrefix.format("has_approved_symbol"),
                                                            encomillar_texto(row['target']['approvedSymbol']),
                                                            encomillar_texto(row['target']['approvedName'])))

            try:  ### Clinical Precedence - urls
                for url in row['urls']:
                    file.write(
                        "{} {} <{}> ; rdfs:label {} .\n".format(rowiri, basePrefix.format("has_source"), url['url'],
                                                                encomillar_texto(url['name'])))

                    file.write("<{}> a {} .\n".format(url['url'], basePrefix.format("referenceId")))

            # file.write(base_triple.format(subject, 'has_indication', comi(row['mechanismOfAction'])))
            except:
                pass

            # file.write("{} a <urn:demo:healthcare:drugIndication> .\n".format(indicationiri))

            clin_n += 1

    except:
        print('No known drugs')

    ## INDICATIONS
    try:
        ## indications
        n = 1
        # for n in range(len(api_response['indications']['rows'])):
        for row in api_response['indications']['rows']:
            # print(api_response['indications']['rows'][n])
            indicationiri = subject.replace(">", "/indication/" + str(n) + ">")

            file.write("{} a <urn:demo:healthcare:drugIndication> .\n".format(indicationiri))

            file.write(base_triple.format(subject, "has_indication", indicationiri))

            file.write("{} {} {} .\n".format(indicationiri, basePrefix.format("maxPhaseForIndication"),
                                             row['maxPhaseForIndication']))

            file.write("{} {} {} .\n".format(indicationiri, basePrefix.format("related_disease"),
                                             "<https://platform.opentargets.org/disease/{}>".format(
                                                 row['disease']['id'])))

            file.write(
                "<https://platform.opentargets.org/disease/{}> rdfs:label {} ; a <urn:demo:healthcare:diseaseId> .\n".format(
                    row['disease']['id'], encomillar_texto(row['disease']['name'])))

            try:  ## indication - therapeutic areas
                for thera in row['disease']['therapeuticAreas']:
                    thera_id = "<https://platform.opentargets.org/disease/{}>".format(thera['id'])

                    file.write(
                        "{} {} {} .\n".format(indicationiri, basePrefix.format("has_therapeuthic_area"), thera_id))

                    file.write("{} rdfs:label {} ; a <urn:demo:healthcare:diseaseId> .\n".format(thera_id,
                                                                                                 encomillar_texto(thera['name'])))

            except:
                pass

            try:  ### indication - references
                for refer in row['references']:

                    if refer['source'] == "ClinicalTrials":
                        source_url = "<https://www.clinicaltrials.gov/ct2/show/{}>"
                    elif refer['source'] == "DailyMed":
                        source_url = "<http://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={}>"
                    for id in refer['ids']:
                        refer_id = source_url.format(id)

                        file.write(base_triple.format(indicationiri, "has_source", refer_id))

                        file.write("{} a <urn:demo:healthcare:referenceId> .\n".format(refer_id))

            # file.write(base_triple.format(subject, 'has_indication', comi(row['mechanismOfAction'])))
            except:
                pass
            n += 1
    except:
        pass

    print("{} of {}".format(drugN + 1, totalcount))

print("EXECUTION COMPLETE")