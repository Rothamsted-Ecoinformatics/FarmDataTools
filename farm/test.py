import configparser
from farmOS import farmOS
import csv
import json
import sys
import pandas
import datetime

def main():
    config = configparser.ConfigParser()
    config.read("config.ini")

    hostname = config["AUTH"]["host"]
    username = config["AUTH"]["username"]
    password = config["AUTH"]["password"]

    farmOS (
        hostname=hostname,
        username=username,
        password=password,
        client_id="farm", # The default oauth client_id enabled on all farmOS servers.
        config_file="farmos_config.cfg",    
        profile_name="Rothamsted farms"
    )

def farm():
    farm_client = farmOS(
        config_file="farmos_config.cfg",    
        profile_name="Rothamsted farms"
    )
    return farm_client

def print_list_csv(items, filename, idfield):
    csvwriter = None 
    with open(filename,"w",newline="") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter="\t",quotechar="\"", quoting=csv.QUOTE_MINIMAL)
        for i in items:
            csvwriter.writerow([i["name"],i[idfield]])

def print_areas_list_csv():
    items = farm().area.get()["list"]
    print_list_csv(items,"data/areasList.csv","tid")
    
def print_crops_list_csv():
    items = farm().term.get("farm_crops")["list"]
    print_list_csv(items,"data/cropsList.csv","tid")

def print_equipment_list_csv():
    items = farm().asset.get({"type":"Equipment"})["list"]
    print_list_csv(items,"data/equipmentList.csv","id")

def print_categories_list_csv():
    items = farm().term.get("farm_log_categories")["list"]
    print_list_csv(items,"data/categoriesList.csv","tid")

def get_log(logId):
    print(logId)
    log = farm().log.get(logId)
    print(json.dumps(log, indent=4, sort_keys=True))

def load_excel_data():
    xl = pandas.ExcelFile("Electronic farm diary 2020 vRO.xlsx")
    
    df = xl.parse("data",index_col=None,header=0,dtype={
        "event_date":str,
        "Field":str,
        "Prop_No":str,
        "Application":str,
        "category":str,
        "Rate_Unit":str,
        "seed dressing":str,
        "direction":str,
        "Notes":str,
        "tractor":str,
        "equipment":str,
        "asssigned_to":str,
        "checked":str,
        "loaded":str,
        "_R_field":int,
        "_R_category":int,
        "_R_tractor":int,
        "_R_equipment":int
        })
    return df

def decode_staff(people_string):
    staff_lookup = {"AA":59,"BF":50,"CM":16,"IS":36,"CR":37,"TH":41,"MG":20,"RC":40,"BS":43,"FL":39,"NC":3}
    people = people_string.split("+")
    return (pandas.Series(people)).map(staff_lookup) 

def load_activity_log():
    df = load_excel_data()
    print("load activity log")
    for index, row in df.iterrows():
        if (row["_R_category"] == 58 
                and row["_R_field"] == 61 
                and row["loaded"] == "N" 
                and row["checked"] == "Y"):
            print(row["Field"])
            fname = "data/record" + str(index) +".json"
            f = open(fname,"w")

            jsonpayload={}

            areas = []
            areas.append({"id":row["_R_field"],"resource": "taxonomy_term"})

            jsonpayload["area"] = areas
            #if row["_R_group"] != "":
            #    jsonpayload["asset"] = [{"id":row["_R_group"],"resource": "farm_asset"}]
            #else:
            #    jsonpayload["asset"] = []
            jsonpayload["asset"] = []
            jsonpayload["created"] = str(int(datetime.datetime.strptime(row["event_date"], "%Y-%m-%d %H:%M:%S").timestamp())) #"%a %b %d %H:%M:%S BST %Y").timestamp()))
            jsonpayload["data"] = ""    
            jsonpayload["done"] = "1"
            equipment = []
            if not pandas.isna(row["_R_tractor"]):
                equipment.append({"id":row["_R_tractor"],"resource": "farm_asset"})
            if not pandas.isna(row["_R_equipment"]):
                equipment.append({"id":row["_R_equipment"],"resource": "farm_asset"})
            jsonpayload["equipment"] = equipment
            
            jsonpayload["files"] = []
            jsonpayload["flags"] = []
            propno = row["Prop_No"]
            categories = []
            if row["_R_category"] != "":
                categories.append({"id": row["_R_category"],"resource": "taxonomy_term"})
            if propno == "Commercial":
                categories.append({"id": 261,"resource": "taxonomy_term"})
            categories.append({"id":570,"resource":"taxonomy_term"}) #create this for flagging auto added records
            jsonpayload["log_category"] = categories
            
            people = decode_staff(row["assigned_to"])
            owners = []
            for person in people:
                owners.append({"id": person,"resource": "user"})        

            jsonpayload["log_owner"] = owners

            jsonpayload["name"] = row["Application"] + ": " + row["Field"] + " " + propno
            
            notes = "<ul>"
            if not pandas.isna(row["direction"]):
                notes = notes + "<li>Direction thrown: " + str(row["direction"]) + "</li>"
            if not pandas.isna(row["Notes"]):
                notes = notes + "<li>Notes: " + str(row["Notes"]) + "</li>"
            notes = notes + "</ul>"

            jsonpayload["notes"] = {"format":"farm_format","value":notes}

            #quantity = [{"label":"false","measure":"depth","unit":{"id":"238","resource":"taxonomy_term"},"value":"10"}]
            #jsonpayload["quantity"] = quantity
            jsonpayload["timestamp"] = str(int(datetime.datetime.strptime(row["event_date"], "%Y-%m-%d %H:%M:%S").timestamp()))
            jsonpayload["type"] = "farm_activity"

            f.write(json.dumps(jsonpayload, indent=4, sort_keys=True))
        
            f.close()
            with open(fname) as json_file:
                data = json.load(json_file)

                print(farm().log.send(data))
        #if index > 10:
        #    break   

if __name__ == "__main__":
    main()
    if sys.argv[1].startswith("get"):
        globals()[sys.argv[1]](",".join(sys.argv[2:]))
    else:
        print("hello")
        globals()[sys.argv[1]]()