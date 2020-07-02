import farmOS
import csv
import json
from farm import service 

myFarm = service.myFarm()

def printAreasCSV():
    items = myFarm.area.get()
    #print(json.dumps(areas, indent=4, sort_keys=True))
    csvwriter = None 
    with open("data/areas.csv","w",newline="") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL)

        for i in items:
            csvwriter.writerow([i["tid"],i["name"]])

def printCropsCSV():
    items = myFarm.farm.term.get('farm_crops')
    #print(json.dumps(areas, indent=4, sort_keys=True))
    csvwriter = None 
    with open("data/crops.csv","w",newline="") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL)

        for i in items:
            csvwriter.writerow([i["tid"],i["name"]])

def printEquipmentCSV():
    items = myFarm.farm.asset.get({'type':'Equipment'})
    print(json.dumps(items, indent=4, sort_keys=True))
    csvwriter = None 
    with open("data/equipemnt.csv","w",newline="") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL)
        for i in items:
            csvwriter.writerow([i["id"],i["name"]])

def printCategoriesCSV():
    items = myFarm.farm.term.get('farm_log_categories')
    print(json.dumps(items, indent=4, sort_keys=True))
    csvwriter = None 
    with open("data/logcategories.csv","w",newline="") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL)

        for i in items:
            csvwriter.writerow([i["tid"],i["name"]])

printCategoriesCSV()
