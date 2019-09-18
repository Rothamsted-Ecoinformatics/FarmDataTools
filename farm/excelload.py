import pandas as pandas
import json
import datetime
from service import FarmService

myFarm = FarmService().myFarm()

xl = pandas.ExcelFile("Electronic-farm-diary-2020-RO-test-xlsx.xlsx")
print(xl.sheet_names)

df = xl.parse('Sheet1',index_col=None,header=0,dtype={'event_date':str,'Field':str,'field_id':str,'Prop_No':str,'Application':str,'Rate_Unit':str,'Notes':str})


for index, row in df.iterrows():
    #print(row[0])
    if row['Prop_No'] == 'Commercial' and row['Application'] == 'Rolling WOSR' and row['loaded'] == "N":
        print(row['Field'])
        fname = "data/record" + str(index) +".json"
        f = open(fname,"w")

        jsonpayload={}

        areacodes = row['field_id'].split("-")
        areas = []
        for a in areacodes:
            areas.append({"id":a,"resource": "taxonomy_term"})

        jsonpayload["area"] = areas
        
        jsonpayload["asset"] = []
        #jsonpayload["changed"] = str(int(datetime.datetime.strptime(row['event_date'], "%Y-%m-%d %H:%M:%S BST %Y").timestamp()))
        jsonpayload["created"] = str(int(datetime.datetime.strptime(row['event_date'], "%a %b %d %H:%M:%S BST %Y").timestamp()))
        jsonpayload["data"] = ""    
        jsonpayload["done"] = "1"
        jsonpayload["equipment"] = [{"id":"21","resource": "farm_asset"},{"id":"12","resource": "farm_asset"}]
        jsonpayload["files"] = []
        jsonpayload["flags"] = []
        jsonpayload["log_category"] = [{"id": "261","resource": "taxonomy_term"},{"id": "265","resource": "taxonomy_term"}]
        jsonpayload["log_owner"] = [{"id": "16","resource": "user"}] # 16 = Chris
        jsonpayload["name"] = "Rolled WOSR: " + row['Field']
        jsonpayload["notes"] = {"format":"farm_format","value":"Rolling WOSR on commercial field"}

        #quantity = [{"label":"false","measure":"depth","unit":{"id":"238","resource":"taxonomy_term"},"value":"10"}]
        #jsonpayload["quantity"] = quantity
        jsonpayload["timestamp"] = str(int(datetime.datetime.strptime(row['event_date'], "%a %b %d %H:%M:%S BST %Y").timestamp()))
        jsonpayload["type"] = "farm_activity"

        f.write(json.dumps(jsonpayload, indent=4, sort_keys=True))
    
        f.close()
        with open(fname) as json_file:
            data = json.load(json_file)

            print(myFarm.farm.log.send(data))

