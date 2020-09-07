import configparser
from farmOS import farmOS
import csv
import json
import sys
import pandas
import datetime
import re

config = configparser.ConfigParser()
config.read("config.ini")

hostname = config["AUTH"]["host"]
username = config["AUTH"]["username"]
password = config["AUTH"]["password"]

# Create the client.
farm = farmOS(
    hostname=hostname,
    client_id = "farm", # Optional. The default oauth client_id "farm" is enabled on all farmOS servers.
    scope="user_access" # Optional. The default scope is "user_access". Only needed if authorizing with a differnt scope.
)

# Authorize the client, save the token.
token = farm.authorize(username, password, scope="user_access")


def main():
    pass

def areas():
    items = farm.area.get()["list"]
    return dict((f["tid"],f["name"]) for f in items)

def equipment():
    items = farm.asset.get({"type":"Equipment"})["list"]
    return dict((f["id"],f["name"]) for f in items)

def is_time(q):
    unit = q["unit"]
    if unit["id"] == "262":
        True
    else:
        False

def list_logs():
    equipmentDict = equipment()
    
    logs = farm.log.get(filters={'type': 'farm_input'})['list']
    #_areas = areas()
    csvwriter = None 
    
    with open("data/report.csv","w",newline="") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL)
        for log in logs:
            eq = [a["id"] for a in log["equipment"]]
            print(eq)
            equipmentNames = ";".join((pandas.Series(eq)).map(equipmentDict))
            areaNames = ";".join([a["name"] for a in log["area"]])
            categoryNames = ";".join([a["name"] for a in log["log_category"]])
            notes = log["notes"]

            #[f for f in items for p in f["parent"] if p["name"] == "FERTILISERS"]
            #urls = [log["url"] for log in logs for m in log["material"] if m["id"] == "576"]
            qs =  log["quantity"]
            if qs:
                hours = [q["value"] for q in qs if is_time(q)]
            else:
                hours = ""
            #hours = [q["value"] for q in qs for u in q["unit"] if u["id"] == "262"]# for u in q["unit"] if u["id"] == "262"]
            #hours = [a["value"] for a in log["quantity"] for u in a["unit"] if u["id"] == "262"]
            
            #logs = farm().log.get(filters=filters)["list"]
    
            
            
            csvwriter.writerow([log["id"],log["name"],areaNames,equipmentNames,categoryNames,notes,hours])




    

if __name__ == "__main__":
    main()
    if sys.argv[1].startswith("get") or sys.argv[1].startswith("delete"):
        globals()[sys.argv[1]](",".join(sys.argv[2:]))
    elif sys.argv[1].startswith("load"):
        print("loading...")
        print(",".join(sys.argv[2:]))
        if len(sys.argv) == 3:
            globals()[sys.argv[1]](int(sys.argv[2]))
        else: 
            # category # experiment
            globals()[sys.argv[1]](int(sys.argv[2]),int(sys.argv[3]))
    elif sys.argv[1].startswith("update"):
        globals()[sys.argv[1]](int(sys.argv[2]),int(sys.argv[3]))
    else:
        print("hello")
        globals()[sys.argv[1]]()