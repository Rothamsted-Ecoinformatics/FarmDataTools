import pandas as pandas
import json
import datetime
import re
from service import FarmService

myFarm = FarmService().myFarm()

xl = pandas.ExcelFile("Copy of Electronic farm diary 2020 vRO v2.xlsx")
print(xl.sheet_names)

df = xl.parse('data',index_col=None,header=0,dtype={
    'event_date':str,
    'Field':str,
    'Prop_No':str,
    'Application':str,
    'category':str,
    'Rate_Unit':str,
    'seed dressing':str,
    'direction':str,
    'Notes':str,
    'tractor':str,
    'equipment':str,
    'asssigned_to':str,
    'checked':str,
    'loaded':str,
    '_R_field':str,
    '_R_category':str,
    '_R_tractor':str,
    '_R_equipment':str,
    '_R_person':str,
    '_R_group':str
    })

for index, row in df.iterrows():
    if row['loaded'] == "X":
        print(row['Field'])
        fname = "data/record" + str(index) +".json"
        f = open(fname,"w")

        jsonpayload={}

        #areacodes = row['field_id'].split("-")
        areas = []
        #for a in areacodes:
        areas.append({"id":row["_R_field"],"resource": "taxonomy_term"})

        #e.g. rate_unit: Samurai @3 L/ha + Buffalo elite @1L/ha
        rawru = row['rate_unit']
        ruparts = rawru.split("+")
        
        for p in ruparts:
            p = p.upper()
            apparts = p.split["@"]
            application = apparts[0]
            match = re.search(r"([0-9]*\.?[0-9]*)",apparts[1])
            rate = match.group(1)
            match = re.search(r"[0-9]*\.?[0-9]*([ML]*\/HA)",apparts[1])
            unit = match.group(1)

        jsonpayload["area"] = areas
        if row["_R_group"] != "nan":
            jsonpayload["asset"] = [{"id":row["_R_group"],"resource": "farm_asset"}]
        else:
            jsonpayload["asset"] = []
        #jsonpayload["changed"] = str(int(datetime.datetime.strptime(row['event_date'], "%Y-%m-%d %H:%M:%S BST %Y").timestamp()))
        jsonpayload["created"] = str(int(datetime.datetime.strptime(row['event_date'], "%Y-%m-%d %H:%M:%S").timestamp())) #"%a %b %d %H:%M:%S BST %Y").timestamp()))
        jsonpayload["data"] = ""    
        jsonpayload["done"] = "1"
        equipment = []
        if row["_R_tractor"] != "nan":
            equipment.append({"id":row["_R_tractor"],"resource": "farm_asset"})
        if row["_R_equipment"] != "nan":
            equipment.append({"id":row["_R_equipment"],"resource": "farm_asset"})
        jsonpayload["equipment"] = equipment
        jsonpayload["files"] = []
        jsonpayload["flags"] = []
        categories = []
        propNo = ""
        if row['_R_category'] != "nan":
            categories.append({"id": row["_R_category"],"resource": "taxonomy_term"})
        if row["_R_group"] != "nan":
            categories.append({"id": "280","resource": "taxonomy_term"})
            propNo = row["Prop_No"]
        else:
            categories.append({"id": "261","resource": "taxonomy_term"})
        jsonpayload["log_category"] = categories
        jsonpayload["log_owner"] = [{"id": row["_R_person"],"resource": "user"}] # 16 = Chris
        
        jsonpayload["name"] = row["Application"] + ": " + row['Field'] + " " + propNo
        notes = "<ul>"
        
        if row["direction"] != "nan":
            notes = notes + "<li>Direction thrown: " + row["direction"] + "</li>"
        if row["Notes"] != "nan":
            notes = notes + "<li>Notes: " + row["Notes"] + "</li>"
        notes =  notes + "</ul>"

        jsonpayload["notes"] = {"format":"farm_format","value":notes}

        #quantity = [{"label":"false","measure":"depth","unit":{"id":"238","resource":"taxonomy_term"},"value":"10"}]
        #jsonpayload["quantity"] = quantity
        jsonpayload["timestamp"] = str(int(datetime.datetime.strptime(row['event_date'], "%Y-%m-%d %H:%M:%S").timestamp()))
        jsonpayload["type"] = "farm_activity"

        f.write(json.dumps(jsonpayload, indent=4, sort_keys=True))
    
        f.close()
        with open(fname) as json_file:
            data = json.load(json_file)

            print(myFarm.farm.log.send(data))

