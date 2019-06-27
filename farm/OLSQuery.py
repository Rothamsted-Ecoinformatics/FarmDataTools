import json
from requests import get
import csv
import configparser

csvwriter = None 

headers = {
    'Accept': 'application/json',
}

def fetchChildren(ponto,piri):    
    query = "http://www.ebi.ac.uk/ols/api/ontologies/"+ponto+"/children?iri="+piri+"&size=500"
    response = get(query, headers=headers)
    result = json.loads(response.content)
    terms = result["_embedded"]["terms"]
    
    for term in terms:
        desc = term["description"][0] if term["description"] else "none"
        
        if term["has_children"]:
            tiri = term["iri"]
            desc = term["description"][0] if term["description"] else "none"
            csvwriter.writerow([term["label"],term["iri"],desc])
            if term["has_children"]:
                fetchChildren(ponto,tiri)
        else:
            csvwriter.writerow([term["label"],term["iri"],desc])
                    
if __name__ == "__main__":    
    config = configparser.ConfigParser()
    config.read('config.ini')
    ontology = config['QUERY']['ontology']
    iri = config['QUERY']['iri']
    
    with open("terms.csv","w",newline="") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL)
        fetchChildren(ontology,iri)