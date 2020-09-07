import configparser
from farmOS import farmOS
import csv
import json
import sys
import pandas
import datetime
import re

fertilisers = None

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

#fertilisers = fetch_fertilisers_list()

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

def fetch_fertilisers_list():
    items = farm().term.get("farm_materials")["list"]
    return [f for f in items for p in f["parent"] if p["name"] == "FERTILISERS"]

def print_fertilisers_list_csv():
    print_list_csv(fetch_fertilisers_list(),"data/fertiliserList.csv","tid")

def get_log(logId):
    log = farm.log.get(logId)
    print(json.dumps(log, indent=4, sort_keys=True))

def get_planting(logId):
    log = farm().asset.get(logId)
    print(json.dumps(log, indent=4, sort_keys=True))

def get_term(termId):
    return farm().term.get(termId)

def delete_log(logId):
    farm().log.delete(logId)
 
def load_excel_data():
    xl = pandas.ExcelFile("Electronic farm diary 2020 vRO.xlsx")
    
    df = xl.parse("data",index_col=None,header=0,dtype={
        "event_date":str,
        "Field":str,
        "Prop_No":str,
        "Application":str,
        "category":str,
        "rate_unit":str,
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
        "_R_equipment":int,
        "_R_experiment":int,
        "crop":str,
        "variety":str,
        "rate":str,
        "_R_variety":str,
        "_R_crop":str,
        "lot_no":str
        })
    return df

def decode_staff(people_string):
    staff_lookup = {"AA":59,"BF":50,"CM":16,"IS":36,"CR":37,"TH":41,"MG":20,"RC":40,"BS":43,"FL":39,"NC":3}
    people = people_string.split("+")
    return (pandas.Series(people)).map(staff_lookup) 

def decode_fertiliser_materials(materials_string=""):
    materials = []
    ml = materials_string.split("+")
    for ms in ml:
        m = ms.split("@")[0].strip()
        id = [f["tid"] for f in fertilisers if f["name"] == m]
        materials.append({"id":id[0],"name":m, "resource": "taxonomy_term"})

    return materials

def decode_pesticide_materials(materials_string,pesticides):
    materials = []
    ml = materials_string.split("+")
    for ms in ml:
        m = ms.split("@")[0].strip()
        id = [[f["tid"],f["label"]] for f in pesticides if f["name"] == m]
        materials.append({"id":id[0][0],"name":id[0][1], "resource": "taxonomy_term"})

    return materials

def decode_quantities(materials_string):
    quantities = []
    ql = materials_string.split("+")
    for qs in ql:
        q = qs.split("@")
        quantity = {}
        quantity["label"] = q[0].strip()
        quantity["measure"] = "rate"
        if len(q) > 1:
            ru = q[1].strip().lower()
            quantity["value"] = ru.split(" ")[0]
            if ru.endswith("kg/ha"):
                uname = "kg/ha"
                uid = "148"
            elif ru.endswith("tonnes/ha"):
                uname = "tonnes/ha"
                uid = "575"
            elif ru.endswith("ml/ha"):
                uname = "ml/ha"
                uid = "244"
            elif ru.endswith("l/ha"):
                uname = "l/ha"
                uid = "307"
            elif ru.endswith("g/ha"):
                uname = "g/ha"
                uid = "544"
            quantity["unit"] = {"id":uid, "name":uname, "resource": "taxonomy_term"}    
                
        quantities.append(quantity)

    return quantities

def decode_owners(assigned_to):
    owners = []
    if not pandas.isna(assigned_to):
        people = decode_staff(assigned_to)
        for person in people:
            owners.append({"id": person,"resource": "user"})
    return owners

def decode_areas(experiment,field):
    areas = []
    if int(experiment) > 0: #overide area with the experiment if provided
        areas.append({"id":experiment,"resource": "taxonomy_term"})
    else:    
        areas.append({"id":field,"resource": "taxonomy_term"})
    return areas

def decode_equipment(tractor,machine):
    equipment = []
    if int(tractor) > 0:
        equipment.append({"id":tractor,"resource": "farm_asset"})
    if int(machine) > 0:
        equipment.append({"id":machine,"resource": "farm_asset"})
    return equipment

def find_logs_for_material_id():
    filters = {
        'type': 'farm_input'
    }
    logs = farm().log.get(filters=filters)["list"]
    
    urls = [log["url"] for log in logs for m in log["material"] if m["id"] == "576"]
    for url in urls:
        print(url)

def find_logs_for_unit_id():
    filters = {
        'type': 'farm_input'
    }
    logs = farm().log.get(filters=filters)["list"]
    
    urls = [log["url"] for log in logs for m in log["material"] if m["id"] == "576"]
    for url in urls:
        print(url)

def find_logs_for_crop_id():
    filters = {
        'type': 'farm_input'
    }
    logs = farm().log.get(filters=filters)["list"]
    
    urls = [log["url"] for log in logs for m in log["material"] if m["id"] == "576"]
    for url in urls:
        print(url)

def find_logs_for_category_id():
    filters = {
        'type': 'farm_input'
    }
    logs = farm().log.get(filters=filters)["list"]
    
    urls = [log["url"] for log in logs for m in log["material"] if m["id"] == "576"]
    for url in urls:
        print(url)

def update_input_log_materials(old, new):
    filters = {
        'type': 'farm_input'
    }
    logs = farm().log.get(filters=filters)["list"]

    new_term = get_term(new)
    old_term = get_term(old)

    logs = [log for log in logs for m in log["material"] if m["id"] == "576"]
    for log in logs:
        print(log["url"])
        newqty = []
        for qty in log["quantity"]:
            if qty["label"] == old_term["name"]:
                qty["label"] = new_term["name"]
            newqty.append(qty)
        newmat = []
        for mat in log["material"]:
            if mat["id"] == old_term["tid"]:
                mat["id"] = new_term["tid"]
                mat["name"] = new_term["name"]
            del mat["uri"]    
            newmat.append(mat)
        data = {}
        data["id"] = log["id"]
        data["quantity"] = newqty
        data["material"] = newmat
        #print(json.dumps(data, indent=4, sort_keys=True))
        print(farm().log.send(data))
        #break

def fix_units():
    filters = {
        'type': 'farm_input'
    }
    logs = farm().log.get(filters=filters)["list"]
    #ids = [log["id"] for log in logs for cat in log["log_category"] if log["input_purpose"] == "Pesticide" and cat["id"]=="157"]
    #b = [i for i in mydict.get('entries', [])]
    
    #lgs = [log["url"] for log in logs if log["input_purpose"] == "Pesticide"]
    
    for lg in logs:
        update = False
        newqty = []
        for qty in lg["quantity"]:
            q = {}
            q["label"] = qty["label"]
            q["measure"] = qty["measure"]
            q["value"] = qty["value"]
            if "unit" in qty:
                q["unit"] = qty["unit"]        
                if qty["unit"]["id"] == "576":# and lg["input_purpose"] == "Pesticide":
                    update = True
                    q["unit"]["id"] = "147"
                    q["unit"]["name"] = "seeds/m2"
                    del q["unit"]["uri"]
            newqty.append(q)
        if update:
            #print(lg["url"] + " : " + str(newqty))
            data = {}
            data["quantity"] = newqty
            data["id"] = lg["id"] #244
            #print(json.dumps(data, indent=4, sort_keys=True))
            print(farm().log.send(data))
            #break

def load_activity_log(category,experiment_filter=-1):
    df = load_excel_data()
    
    for index, row in df.iterrows():
        if ((row["_R_experiment"] == experiment_filter or experiment_filter == -1)
                and row["_R_category"] == category 
                and row["loaded"] == "N" 
                and row["checked"] == "Y"):
            fname = "data/record" + str(index) +".json"
            f = open(fname,"w")

            jsonpayload={}

            jsonpayload["area"] = decode_areas(row["_R_experiment"],row["_R_field"])
            jsonpayload["asset"] = []
            jsonpayload["created"] = str(int(datetime.datetime.strptime(row["event_date"], "%Y-%m-%d %H:%M:%S").timestamp())) #"%a %b %d %H:%M:%S BST %Y").timestamp()))
            jsonpayload["data"] = ""    
            jsonpayload["done"] = "1"
            jsonpayload["equipment"] = decode_equipment(row["_R_tractor"],row["_R_equipment"])
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
            
            owners = []
            if not pandas.isna(row["assigned_to"]):
                people = decode_staff(row["assigned_to"])
                for person in people:
                    owners.append({"id": person,"resource": "user"})        

            jsonpayload["log_owner"] = owners
            jsonpayload["name"] = row["Application"] + ": " + row["Field"] + " " + str(propno)
             
            notes = "<ul>"
            notes = notes + "<li>" + row["Application"] + "</li>"
            if not pandas.isna(row["direction"]):
                notes = notes + "<li>Direction thrown: " + str(row["direction"]) + "</li>"
            if not pandas.isna(row["Notes"]):
                notes = notes + "<li>Notes: " + str(row["Notes"]) + "</li>"
            notes = notes + "</ul>"

            jsonpayload["notes"] = {"format":"farm_format","value":notes}
            jsonpayload["timestamp"] = str(int(datetime.datetime.strptime(row["event_date"], "%Y-%m-%d %H:%M:%S").timestamp()))
            jsonpayload["type"] = "farm_activity"

            f.write(json.dumps(jsonpayload, indent=4, sort_keys=True))
            f.close()
            with open(fname) as json_file:
                data = json.load(json_file)
                print(farm().log.send(data))

def load_fertiliser_log(category,experiment_filter=-1):
    df = load_excel_data()
    
    for index, row in df.iterrows():
        if ((row["_R_experiment"] == experiment_filter or experiment_filter == -1)
                and row["_R_category"] == category 
                and row["loaded"] == "N" 
                and row["checked"] == "Y"):
            print(row["Field"])
            fname = "data/record" + str(index) +".json"
            print(fname)
            f = open(fname,"w")

            jsonpayload={}

            jsonpayload["area"] = decode_areas(row["_R_experiment"],row["_R_field"])
            jsonpayload["asset"] = []
            jsonpayload["created"] = str(int(datetime.datetime.strptime(row["event_date"], "%Y-%m-%d %H:%M:%S").timestamp())) #"%a %b %d %H:%M:%S BST %Y").timestamp()))
            jsonpayload["data"] = ""    
            jsonpayload["done"] = "1"
            jsonpayload["equipment"] = decode_equipment(row["_R_tractor"],row["_R_equipment"])
            jsonpayload["files"] = []
            jsonpayload["flags"] = []
            
            jsonpayload["input_purpose"] = "Fertiliser"
            
            propno = row["Prop_No"]
            categories = []
            if propno == "Commercial":
                categories.append({"id": 261,"resource": "taxonomy_term"})
            categories.append({"id":156,"resource":"taxonomy_term"}) # Fertiliser application
            categories.append({"id":570,"resource":"taxonomy_term"}) # create this for flagging auto added records
            jsonpayload["log_category"] = categories
            
            jsonpayload["log_owner"] = decode_owners(row["assigned_to"])
            
            if not pandas.isna(row["rate_unit"]):
                jsonpayload["material"] = decode_fertiliser_materials(row["rate_unit"])
                jsonpayload["quantity"] = decode_quantities(row["rate_unit"])

            jsonpayload["name"] = row["Application"] + ": " + row["Field"] + " " + str(propno)
             
            notes = "<ul>"
            notes = notes + "<li>" + row["Application"] + "</li>"
            if not pandas.isna(row["Notes"]):
                notes = notes + "<li>Notes: " + str(row["Notes"]) + "</li>"
            notes = notes + "</ul>"

            jsonpayload["notes"] = {"format":"farm_format","value":notes}

            jsonpayload["timestamp"] = str(int(datetime.datetime.strptime(row["event_date"], "%Y-%m-%d %H:%M:%S").timestamp()))
            jsonpayload["type"] = "farm_input"

            f.write(json.dumps(jsonpayload, indent=4, sort_keys=True))
        
            f.close()
            with open(fname) as json_file:
                data = json.load(json_file)
                print(farm().log.send(data))
    
def load_pesticide_log(category,experiment_filter=-1):
    df = load_excel_data()

    for index, row in df.iterrows():
        # need a custom pesticides list as FarmOS names include Mapp number, Excel sheet does not
        plst = []
        plst.append({"tid":"275","name":"Sluxx","label":"Sluxx"})
        plst.append({"tid":"240","name":"X-clude","label":"X-clude"})
        plst.append({"tid":"242","name":"Hallmark","label":"Hallmark with Zeon Technology (12629)"})
        plst.append({"tid":"484","name":"Spray fix","label":"Spray-Fix"})
        plst.append({"tid":"521","name":"Axial Pro","label":"Axial Pro"})
        plst.append({"tid":"386","name":"Cello","label":"Cello (18290)"})
        plst.append({"tid":"461","name":"Provalia","label":"Provalia LQM (17846)"})
        plst.append({"tid":"387","name":"Stefes","label":"Stefes CCC 720"})
        plst.append({"tid":"366","name":"Buffalo elite","label":"Buffalo elite"})
        plst.append({"tid":"421","name":"Envoy","label":"Envoy (16297)"})
        plst.append({"tid":"365","name":"Samurai","label":"Samurai (16238)"})
        plst.append({"tid":"414","name":"Cyflamid","label":"Cyflamid (12403)"})
        plst.append({"tid":"272","name":"Ironmax pro","label":"Ironmax pro (17122)"})
        plst.append({"tid":"458","name":"Pontos","label":"Pontos (17811)"})
        plst.append({"tid":"494","name":"Velomax","label":"Velomax"})
        plst.append({"tid":"520","name":"Presite","label":"Presite SX"})
        plst.append({"tid":"520","name":"Presite SX","label":"Presite SX"})
        plst.append({"tid":"485","name":"Starane Hi-Load HL","label":"Starane HI-Load HL (16557)"})
        plst.append({"tid":"485","name":"Starane","label":"Starane HI-Load HL (16557)"})
        plst.append({"tid":"497","name":"Vortex","label":"Vortex (17112)"})
        plst.append({"tid":"464","name":"Refine Max SX","label":"Refine Max SX (15622)"})
        plst.append({"tid":"405","name":"Cintac","label":"Cintac (18222)"})
        plst.append({"tid":"408","name":"Cogent","label":"Cogent"})
        plst.append({"tid":"422","name":"Epic","label":"Epic (16798)"})
        plst.append({"tid":"286","name":"Firestarter","label":"Firestarter (18422)"})
        plst.append({"tid":"452","name":"Nirvana","label":"Nirvana (14256)"})
        plst.append({"tid":"449","name":"Moddus","label":"Moddus (15151)"})
        plst.append({"tid":"388","name":"3C Chlormequat 750","label":"3C Chlormequat 750 (16690)"})
        plst.append({"tid":"491","name":"Toledo","label":"Toledo (18298)"})
        plst.append({"tid":"469","name":"Optio","label":"Optio 500 (17216) - Expired"})
        plst.append({"tid":"469","name":"Optio 500","label":"Optio 500 (17216) - Expired"})
        plst.append({"tid":"471","name":"Bravo","label":"Bravo 500 (14548) - Expired"})
        plst.append({"tid":"443","name":"Laser","label":"Laser (12930) - Expired"})
        plst.append({"tid":"407","name":"Claw","label":"Claw 500 (17332) - Expired"})
        plst.append({"tid":"424","name":"Falcon","label":"Falcon (16459)"})
        plst.append({"tid":"543","name":"Keystone","label":"Keystone (18565)"})
        plst.append({"tid":"437","name":"Jade","label":"Jade (16203)"})
        plst.append({"tid":"581","name":"Clayton Tebucon","label":"Clayton Tebucon"})
        plst.append({"tid":"417","name":"Dymid","label":"Dymid (17585)"})
        plst.append({"tid":"582","name":"Corinth","label":"Corinth"})
        plst.append({"tid":"291","name":"Liberator","label":"Liberator"})
        plst.append({"tid":"583","name":"Mavrik","label":"Mavrik"})
        plst.append({"tid":"584","name":"Palio","label":"Palio"})
        plst.append({"tid":"585","name":"Sprinter","label":"Sprinter"})
        plst.append({"tid":"467","name":"Roundup","label":"Roundup Power Max (16373)"})
        plst.append({"tid":"586","name":"SAN 703","label":"SAN 703"})
        plst.append({"tid":"588","name":"Hexa Mag","label":"Hexa Mag"})
        plst.append({"tid":"587","name":"Tectura","label":"Tectura"})
        plst.append({"tid":"589","name":"Tower","label":"Tower"})
        plst.append({"tid":"590","name":"Troy","label":"Troy"})
        plst.append({"tid":"591","name":"Universal Bio","label":"Universal bio"})
        plst.append({"tid":"592","name":"Scitec","label":"Scitec"})
        plst.append({"tid":"384","name":"Fusilade Max","label":"Fusilade Max (18815)"})

        if ((row["_R_experiment"] == experiment_filter or experiment_filter == -1)
                and row["_R_category"] == category 
                and row["loaded"] == "N" 
                and row["checked"] == "Y"):
            print(row["Field"])
            fname = "data/record" + str(index) +".json"
            print(fname)
            f = open(fname,"w")

            jsonpayload={}

            jsonpayload["area"] = decode_areas(row["_R_experiment"],row["_R_field"])
            jsonpayload["asset"] = []
            jsonpayload["created"] = str(int(datetime.datetime.strptime(row["event_date"], "%Y-%m-%d %H:%M:%S").timestamp())) #"%a %b %d %H:%M:%S BST %Y").timestamp()))
            jsonpayload["data"] = ""    
            jsonpayload["done"] = "1"
            jsonpayload["equipment"] = decode_equipment(row["_R_tractor"],row["_R_equipment"])
            jsonpayload["files"] = []
            jsonpayload["flags"] = []
            jsonpayload["input_purpose"] = "Pesticide"
            propno = row["Prop_No"]
            categories = []
            if propno == "Commercial":
                categories.append({"id": 261,"resource": "taxonomy_term"})
            categories.append({"id":157,"resource":"taxonomy_term"}) # Pesticide application
            categories.append({"id":570,"resource":"taxonomy_term"}) # create this for flagging auto added records
            jsonpayload["log_category"] = categories
            jsonpayload["log_owner"] = decode_owners(row["assigned_to"])
            if not pandas.isna(row["rate_unit"]):
                jsonpayload["material"] = decode_pesticide_materials(row["rate_unit"], plst)
                jsonpayload["quantity"] = decode_quantities(row["rate_unit"])
            jsonpayload["name"] = row["Application"] + ": " + row["Field"] + " " + str(propno)
            notes = "<ul>"
            notes = notes + "<li>" + row["Application"] + "</li>"
            if not pandas.isna(row["Notes"]):
                notes = notes + "<li>Notes: " + str(row["Notes"]) + "</li>"
            notes = notes + "</ul>"
            jsonpayload["notes"] = {"format":"farm_format","value":notes}
            jsonpayload["timestamp"] = str(int(datetime.datetime.strptime(row["event_date"], "%Y-%m-%d %H:%M:%S").timestamp()))
            jsonpayload["type"] = "farm_input"

            f.write(json.dumps(jsonpayload, indent=4, sort_keys=True))
        
            f.close()
            with open(fname) as json_file:
                data = json.load(json_file)
                print(farm().log.send(data))

def load_seeding_log(category,experiment_filter=-1):
    df = load_excel_data()
    
    for index, row in df.iterrows():
        if ((row["_R_experiment"] == experiment_filter or experiment_filter == -1)
                and row["_R_category"] == category 
                and row["loaded"] == "N" 
                and row["checked"] == "Y"):
            
            #need to generate a planting first
            fname = "data/record_planting" + str(index) +".json"
            f = open(fname,"w")
            propno = row["Prop_No"]

            jsonpayload={}         
            
            #jsonpayload["area"] = decode_areas(row["_R_experiment"],row["_R_field"])
            #jsonpayload["archived"] = "0"
            #jsonpayload["changed"] = str(int(datetime.datetime.strptime(row["event_date"], "%Y-%m-%d %H:%M:%S").timestamp())) #"%a %b %d %H:%M:%S BST %Y").timestamp()))
            jsonpayload["created"] = str(int(datetime.datetime.strptime(row["event_date"], "%Y-%m-%d %H:%M:%S").timestamp())) #"%a %b %d %H:%M:%S BST %Y").timestamp()))
            crops = []
            if int(row["_R_variety"]) > 0:    
                crops.append({"id":row["_R_variety"],"resource":"taxonomy_term"})
            else:
                crops.append({"id":row["_R_crop"],"resource":"taxonomy_term"})
            jsonpayload["crop"] = crops
            #jsonpayload["data"] = ""  
            #jsonpayload["files"] = []
            #jsonpayload["description"] = []
            #jsonpayload["flags"] = []
            #jsonpayload["geometry"] = ""
            #jsonpayload["images"] = []
            #jsonpayload["location"] = decode_areas(row["_R_experiment"],row["_R_field"])
            if not pandas.isna(row["variety"]): 
                jsonpayload["name"] = "Planting: " + row["variety"] + " " + row["Field"] + " " + str(propno) 
            else:
                jsonpayload["name"] = "Planting: " + row["Crop"] + " " + row["Field"] + " " + str(propno) 
            #jsonpayload["parent"] = []
            #jsonpayload["season"] = []
            jsonpayload["type"] = "planting"
            jsonpayload["uid"] = decode_owners(row["assigned_to"])[0]

            f.write(json.dumps(jsonpayload, indent=4, sort_keys=True))
        
            f.close()
            asset = {}
            with open(fname) as json_file:
                data = json.load(json_file)
                asset = farm().asset.send(data)
                print(asset)

            # Now for the seeding
            fname = "data/record_seeding" + str(index) +".json"
            print("index: "  + str(index))
            f = open(fname,"w")    
            jsonpayload = {}
            jsonpayload["asset"] = [{"id":asset["id"],"resource":"farm_asset"}]
            jsonpayload["created"] = str(int(datetime.datetime.strptime(row["event_date"], "%Y-%m-%d %H:%M:%S").timestamp()))
            jsonpayload["done"] = "1"
            jsonpayload["equipment"] = decode_equipment(row["_R_tractor"],row["_R_equipment"])
            #jsonpayload["files"] = []
            #jsonpayload["flags"] = []
            
            categories = []
            if propno == "Commercial":
                categories.append({"id": 261,"resource": "taxonomy_term"})
            categories.append({"id":1,"resource":"taxonomy_term"}) # planting
            categories.append({"id":570,"resource":"taxonomy_term"}) # create this for flagging auto added records
            jsonpayload["log_category"] = categories
            jsonpayload["log_owner"] = decode_owners(row["assigned_to"])
            if not pandas.isna(row["lot_no"]):
                jsonpayload["lot_number"] = row["lot_no"]
            jsonpayload["movement"] = {"area":decode_areas(row["_R_experiment"],row["_R_field"])}
            if not pandas.isna(row["variety"]):
                name = "Seeding: " + row["Crop"] + " " + row["variety"] + " in " + row["Field"] + " " + str(propno)
            else:
                name = "Seeding: " + row["Crop"] + " in " + row["Field"] + " " + str(propno)
            name = name.strip().replace("  "," ")
            jsonpayload["name"] = name
            notes = "<ul>"
            notes = notes + "<li>" + row["Application"] + "</li>"
            if not pandas.isna(row["Notes"]):
                notes = notes + "<li>Notes: " + str(row["Notes"]) + "</li>"
            if not pandas.isna(row["seed dressing"]):
                notes = notes + "<li>Seed dressing: " + str(row["seed dressing"]) + "</li>"
            notes = notes + "</ul>"
            jsonpayload["notes"] = {"format":"farm_format","value":notes}    
            if not pandas.isna(row["rate"]):
                rateparts = row["rate"].lower().split(" ")
                value = rateparts[0] 
                label = "Seed rate " + row["variety"]
                rid = ""
                if rateparts[1] == "sm2":
                    rid = "237"    
                else:
                    rid = "148"    
                jsonpayload["quantity"] = {"label":label,"measure":"rate","unit":{"id":rid,"resource":"taxonomy_term"},"value":value}
            jsonpayload["timestamp"] = str(int(datetime.datetime.strptime(row["event_date"], "%Y-%m-%d %H:%M:%S").timestamp()))
            jsonpayload["type"] = "farm_seeding"

            f.write(json.dumps(jsonpayload, indent=4, sort_keys=True))
        
            f.close()
            with open(fname) as json_file:
                data = json.load(json_file)
                
                print(farm().log.send(data))

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