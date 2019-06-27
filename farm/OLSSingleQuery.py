'''
Created on 21 Jun 2019

@author: ostlerr
'''
import json
from requests import get, utils
import csv
import configparser

csvwriter = None 

headers = {
    'Accept': 'application/json',
}

def run(q):
    response = get(q, headers=headers)
    result = json.loads(response.content)
    return result

def fetchRoleTerms(ontology,shortForm):
    # Get the role term we interested in finding terms for with this role, e.g. chemicals with Fertilizer Role 
    query = "http://www.ebi.ac.uk/ols/api/ontologies/chebi/terms?short_form="+shortForm
    result = run(query)

    # Need to get the graph as this encodes a URL which has roles    
    graphHref = result["_embedded"]["terms"][0]["_links"]["graph"]["href"] 
    graphResult = run(graphHref)

    for edge in graphResult['edges']: # process the edges looking for those with "has role" label
        if edge["label"] == "has role":
            siri = edge["source"]
            esiri = utils.quote(utils.quote(siri,safe=""))
            roleTermResult = run("http://www.ebi.ac.uk/ols/api/terms/"+esiri)
            rtrLabel = roleTermResult["_embedded"]["terms"][0]["label"]
            rtrIri = roleTermResult["_embedded"]["terms"][0]["iri"]
            rtrDesc = roleTermResult["_embedded"]["terms"][0]["description"][0] if roleTermResult["_embedded"]["terms"][0]["description"] else "none"
            csvwriter.writerow([rtrLabel,rtrIri,rtrDesc])
            
if __name__ == "__main__":    
    config = configparser.ConfigParser()
    config.read('config.ini')
    ontology = config['QUERY']['ontology']
    shortForm = config['QUERY']['shortForm'] #e.g. CHEBI_33287
    
    with open("terms.csv","w",newline="") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL)
        fetchRoleTerms(ontology,shortForm)