import configparser
from farmOS import farmOS
import csv
import json
import sys
import pandas
import datetime
import re
import datetime as dt

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

export_fieldnames = ["log_id","log_date","log_name","log_name_orig","field_id","field_name","experiment_id","experiment_name","equipment_list","operators","categories","hours","orig_time","time_units","start","finish","crops","seed_rate","dressing","weight","weight_unit","count","depth","depth_unit","direction_thrown", "direction_of_work","irrigation","irrigation_unit","spray_volume","spray_volume_unit","area_sprayed","area_sprayed_unit","material","mapp","rate","rate_unit","wind_speed","weather_desc","temperature","wind_direction","notes","files","raw_notes","raw_quantity"]

def main():
    pass

def decode_staff(people):
    staff_lookup = {"65":"Helen Hague","69":"Mark Gardner","68":"Billy Hoddy-Brown","67":"Maisie Bruce","1":"Admin","38":"Aislinn Pearson","59":"Andrea Arvai","50":"Ben Flannery","16":"Chris Mackay","36":"Ian Shield","37":"Christoph Russell","41":"Tim Hall","20":"Martin Gardner","40":"Rob Copley","43":"Ben Smith","39":"Fred Ledbury","3":"Nick Chichester-Miles","17":"Richard Ostler"}
    ps = ";".join(pandas.Series(people).map(staff_lookup).tolist())
    return ps

def strip_html(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def get_fieldname(id):
    fieldname = ""
    area = farm.area.get(id)["list"]

    if area[0]["area_type"] == "bed":
        parents = area[0]["parent"] 
        fieldname = parents[0]["name"]        
    else:
        fieldname = ""
    return fieldname

def equipment():
    items = farm.asset.get({"type":"Equipment"})["list"]
    return dict((f["id"],f["name"]) for f in items)

def to_date(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp))

def to_24_clock(testtime):
    ntime = testtime
    shours = testtime.split(":")
    ish = int(shours[0])
    if ish in [1, 2, 3, 4, 5, 6, 7]:
        ntime = ":".join([str(ish+12),shours[1]])
    return ntime

def format_count(c):
    mval = ""
    if c["label"]:
        mval = str(c["label"]) + ": " + str(c["value"]) 
    else:
        mval = str(c["value"])
    if "name" in c["unit"]:
        mval = mval + " " +  c["unit"]["name"]
    return mval

def format_hours(h):
    st = 0
    if float(h["value"]):
        if "unit" in h and (h["unit"]["name"] == "min" or h["unit"]["name"] == "minutes (m)"):
            st = float(h["value"])*60 #(to seconds)                                                
        elif "unit" in h and (h["unit"]["name"] == "hours (h)" or h["unit"]["name"] == "hours" or h["unit"]["name"] == "hrs"):
            if float(h["value"]) in [0.01,0.02,0.03,0.04,0.05] or float(h["value"]) == 0.5:
                st = float(h["value"])*60*60 # assume value is hours
            else:
                st = float(h["value"])*60 # assume value is minutes
        else: # this might not be needed
            val = str(h["value"])
            parts = []
            if "." in val:
                parts = val.split(".")
            elif ":" in val:
                parts = val.split(".")
            if len(parts) == 2:
                st = (float(parts[0])*60*60) + (float(parts[1])*60)
            else:
                st = float(val)*60
    return dt.timedelta(seconds=st)

def to_hours(start, finish):
    print(finish + " - " + start)
    return dt.datetime.strptime(finish, '%H:%M') - dt.datetime.strptime(start, '%H:%M')

def tidy_notes(notes):
    return re.sub(r"<\/?[brpuli]+\s?\/?>","",notes).strip().replace("\n","; ").replace("&amp;","and").strip()

def get_planting(id):
    return farm.asset.get(id)

def process_export_fields(log):
    record = {}

    record["log_id"] = "https://rothamstedfarm.farmos.net/log/" + log["id"]
    lname = log["name"]
    record["log_name_orig"] = lname
    lname = lname.replace("Commercial"," commercial area").replace("nan","").strip()
    lname = re.sub(r":\s[A-Z]+\s"," ",lname).strip()
    lname = re.sub(r":\s[A-Z]+\s[A-Z\/\+\,\s0-9]+","",lname).strip()
    lname = re.sub(r"in\s[A-Z\s\/\+0-9]+$"," ",lname).strip()
    lname = re.sub(r":\s[A-Z][a-z]+$"," ",lname).strip()
    lname = re.sub(r":\s[A-Z]+$"," ",lname).strip()
    lname = re.sub(r":\s[A-Z][a-z]+[A-Za-z\/\,\+\s1-7]+[1-7]$"," ",lname).strip()
    record["log_name"] = lname
    
    record["log_date"] = to_date(log["timestamp"])

    record["equipment_list"] = ";".join([a["id"] for a in log["equipment"]])
    
    if "area" in log:
        record["area"] = ";".join([a["id"] for a in log["area"]])
    elif "movement" in log:
        record["area"] = ";".join([a["id"] for a in log["movement"]["area"]])

    record["categories"] = ";".join([a["id"] for a in log["log_category"]])
    record["operators"] = ";".join([a["id"] for a in log["log_owner"]])
    if log["files"]:
        uris = []
        for f in log["files"]:
            uris.append(f["file"]["uri"])
        record["files"] = ";".join(uris)

    notes = log["notes"]
    if "value" in notes:
        notes = notes["value"]
        notes = re.sub(r"<\/?[brpuli]+\s?\/?>","",notes).strip().replace("&amp;","and").strip().replace("\n",";")
        noteParts = notes.split(";")
        cleanNotes = []
        for np in noteParts:
            np = np.replace("Notes:","").strip()
            npt = np.lower()
            if np.startswith("Direction thrown:") or np.startswith("Plough thrown:"):
                record["direction_thrown"] = np.split(":")[1].strip().replace("Thrown","").lower().replace("east","E").replace("south","S").replace("north","N").replace("west","W")
            elif np.startswith("Direction of work"):
                record["direction_of_work"] = np.split(":")[1].strip()
            elif npt.startswith("start time:") or npt.startswith("start:"):
                times = re.findall(r'([0-9]+:[0-9]+)',npt)
                if ("-" in npt):
                    record["start"] = to_24_clock(times[0])
                    record["finish"] = to_24_clock(times[1])
                else:
                    record["start"] = to_24_clock(times[0])
            elif npt.startswith("stop time:") or npt.startswith("finish:") or npt.startswith("finish time:"):
                times = re.findall(r'([0-9]+:[0-9]+)',npt)
                record["finish"] = to_24_clock(times[0])            
            elif np.startswith("Wind:"):
                nps = np.split(" ")
                record["wind_speed"] = " ".join(nps[1:2])
                if len(nps)>3:
                    record["wind_direction"] = nps[3]
            elif np.startswith("Direction:") or np.startswith("wind direction:"):
                record["wind_direction"] = np.split(":")[1].strip()
            elif np.startswith("Wind speed:") or np.startswith("wind speed (mph):"):
                record["wind_speed"] = np.split(":")[1].strip()
            elif np.startswith("Weather:"):
                record["weather_desc"] = np.split(":")[1].strip()
            elif np.startswith("Temperature:") or np.startswith("Temp:") or np.startswith("temperature (C):"):
                record["temperature"] = np.split(":")[1].strip()
            elif np.startswith("start time:") or np.startswith("Start:"):
                record["start"] = to_24_clock(np.split(": ")[1])
            elif np.startswith("stop time:") or np.startswith("Finish:"):
                record["finish"] = to_24_clock(np.split(": ")[1])    
            elif np.startswith("Seed dressing:") or np.startswith("Dressing:"):
                record["dressing"] = np.split(": ")[1]                 
            elif np:
                cleanNotes.append(np)

            if "start" in record and "finish" in record:
                record["hours"] = to_hours(record.get("start"), record.get("finish"))
        record["notes"] = ". ".join(cleanNotes)

    qs =  log["quantity"]
    record["raw_quantity"] = qs

    for q in qs:
        m = q["measure"]
                
        if m == "time":
            record["hours"] = format_hours(q)
            record["orig_time"] = q["value"]
            if "unit" in q:
                record["time_units"] = q["unit"]["name"]
        elif m == "weight":# and q["unit"]["id"] == "262"::
            record["weight"] = q["value"]
            record["weight_unit"] = q["unit"]["name"]
        elif m == "count":
            record["count"] = format_count(q)
        elif m == "length":
            if q["label"] and (q["label"].lower() == "h2o applied" or q["label"].lower() == "h20 applied"):
                record["irrigation"] = q["value"]
                record["irrigation_unit"] = q["unit"]["name"]
            else: 
                record["depth"] = q["value"]
                record["depth_unit"] = q["unit"]["name"]
    return record

def process_area(record, area, ad):
    ainfo = ad.get(area)
    print(ainfo)
    if ainfo:
        record["experiment_id"] = ainfo.get("exp_id")
        record["experiment_name"] = ainfo.get("exp_name")
        record["field_id"] = ainfo.get("field_id")
        record["field_name"] = ainfo.get("field_name")
    return record

def export_logs():
    ad = area_dict()
    with open("data/logs.csv","w",newline="") as csvfile:
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=export_fieldnames)
        csvwriter.writeheader()
        export_activity_logs(csvwriter,ad)
        export_sowing_logs(csvwriter,ad)
        export_harvest_logs(csvwriter,ad)
        export_observation_logs(csvwriter,ad)
        export_input_logs(csvwriter,ad)

def export_activity_logs(csvwriter,ad):
    logs = farm.log.get(filters={'type': 'farm_activity'})['list']

    for log in logs:
        print(log["id"])
        record = process_export_fields(log)

        # start log specific elements    
        if log["membership"]:
            groups = log["membership"]["group"]
            if groups:
                record["membership"] = ";".join([a["id"] for a in groups])
        # end log specific elements

        areas = record["area"].split(";")
        del record["area"]
        for area in areas:
            record = process_area(record, area, ad)
            csvwriter.writerow(record)

def export_harvest_logs(csvwriter,ad):
    logs = farm.log.get(filters={'type': 'farm_harvest'})['list']

    for log in logs:
        print(log["id"])
        record = process_export_fields(log)

        areas = record["area"].split(";")
        del record["area"]
        for area in areas:
            record = process_area(record, area, ad)
            csvwriter.writerow(record)      
        
def export_observation_logs(csvwriter,ad):
    logs = farm.log.get(filters={'type': 'farm_observation'})['list']

    for log in logs:
        print(log["id"])
        record = process_export_fields(log)

        areas = record["area"].split(";")
        del record["area"]
        for area in areas:
            record = process_area(record, area, ad)
            csvwriter.writerow(record)  

def export_input_logs(csvwriter, ad):
    logs = farm.log.get(filters={'type': 'farm_input'})['list']

    for log in logs:
        print(log["id"])
        record = process_export_fields(log)

        mt = log["material"]
        if mt:
            mt = ";".join([str(m["id"]) + " : " + str(m["name"]) for m in mt])
    
        qs =  log["quantity"]
        quantities = []
        for q in qs:
            m = q["measure"]
            if m == "rate":
                if "unit" in q:
                    quantities.append(str(q["label"]) + "@@" + str(q["value"]) + "@@" + str(q["unit"]["name"]))                    
                else:
                    quantities.append(str(q["label"]))
            elif m == "volume":
                record["spray_volume"] = q["value"] 
                record["spray_volume_unit"] = q["unit"]["name"]
            elif m == "area":
                record["area_sprayed"] = q["value"]
                record["area_sprayed_unit"] = q["unit"]["name"]
        
        quants = ";".join(quantities)
        if ";" not in quants and "False" in quants:
            quants = quants.replace("False",mt.split(":")[1].strip())
        
        areas = record["area"].split(";")
        del record["area"]
        for area in areas:
            record = process_area(record, area, ad)
            for q in quantities:
                #nr = record
                qp = q.split("@@")
                record["material"] = qp[0]
                if len(qp) > 1:
                    record["rate"] = qp[1]
                    record["rate_unit"] = qp[2]
                
                csvwriter.writerow(record)   

def export_sowing_logs(csvwriter, ad):    
    logs = farm.log.get(filters={'type': 'farm_seeding'})['list']

    for log in logs:
        print(log["id"])
        record = process_export_fields(log)
        
        planting = get_planting(log["asset"][0]["id"])

        record["crops"] = ";".join([a["name"] for a in planting["crop"]])

        qs =  log["quantity"]
        for q in qs:
            m = q["measure"]
            if m == "rate":
                if q["unit"]["id"] == "147" or q["unit"]["id"] == "237":
                    record["seed_rate"] = q["value"]    
                elif q["unit"]["id"] == "148" or q["unit"]["id"] == "751" or q["unit"]["id"] == "769":
                    record["rate"] = q["value"]
                    record["rate_unit"] = q["unit"]["name"]

        areas = record["area"].split(";")
        del record["area"]
        for area in areas:
            record = process_area(record, area, ad)
            csvwriter.writerow(record)

def list_activity_logs():
    equipmentDict = equipment()
    
    logs = farm.log.get(filters={'type': 'farm_activity'})['list']
    
    with open("data/report_activity.csv","w",newline="") as csvfile:
        fieldnames = ["log_id","log_date","log_name","field","areas","equipment_list","operators","raw_operators","categories","hours","count","depth","notes","raw_notes","raw_quantity"]
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csvwriter.writeheader()
        for log in logs:
            record = {}
            print(log["id"])
            record["log_id"] = "https://rothamstedfarm.farmos.net/log/" + log["id"]
            record["log_name"] = log["name"]
            record["log_date"] = to_date(log["timestamp"])

            eq = [a["id"] for a in log["equipment"]]
            
            record["equipment_list"] = ";".join((pandas.Series(eq)).map(equipmentDict))
            record["field"] = get_fieldname(log["area"][0]["id"])
            record["areas"] = ";".join([a["name"] for a in log["area"]])
            record["categories"] = ";".join([a["name"] for a in log["log_category"]])
            record["operators"] = decode_staff([a["id"] for a in log["log_owner"]])
            record['raw_operators'] = [a["id"] for a in log["log_owner"]]
            notes = log["notes"]
            
            print(notes)
            if "value" in notes:
                record["raw_notes"] = notes["value"]
                notes = notes["value"]
                notes = re.sub(r"<\/?[brpuli]+\s?\/?>","",notes).replace("&amp;","and").replace("\n",";").replace("Notes:","")
                record["notes"] = notes

            qs =  log["quantity"]
            record["raw_quantity"] = qs

            for q in qs:
                m = q["measure"]
                if m == "time":
                    record["hours"] = format_hours(q)
                elif m == "count":
                    record["count"] = format_count(q)
                elif m == "length":
                    record["depth"] = format_count(q)
     
            csvwriter.writerow(record)

def list_inputs():
    #equipmentDict = equipment()
    
    logs = farm.log.get(filters={'type': 'farm_input'})['list']
    area_d = area_dict()
    csvwriter = None 
    with open("data/report_input.csv","w",newline="") as csvfile:
        # Using a dictionary writer as it should take care of column ordering 
        fieldnames = ["log_id","log_date","log_name","field","experiment","operators","product","rate","rate_unit","spray_volume","area_sprayed","area_sprayed_unit","categories","hours","purpose","method","plots","start","finish","wind_speed","wind_direction","temperature","weather_desc","notes"]
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csvwriter.writeheader()
        for log in logs:
            record = {}

            print(log["id"])
            record["log_id"] = "https://rothamstedfarm.farmos.net/log/" + log["id"]
            record["log_name"] = log["name"]
            record["log_date"] = to_date(log["timestamp"])
            #record["field"] = get_fieldname(log["area"][0]["id"])

            #eq = [a["id"] for a in log["equipment"]]
            #record["equipment_list"] = ";".join((pandas.Series(eq)).map(equipmentDict))
            #record["areas"] = ";".join([a["name"] for a in log["area"]])
            areas = [a["name"] for a in log["area"]]
            record["categories"] = ";".join([a["name"] for a in log["log_category"]])
            record["purpose"] = log["input_purpose"]
            record["method"] = log["input_method"]
            record["operators"] = decode_staff([a["id"] for a in log["log_owner"]])
            #record['raw_operators'] = [a["id"] for a in log["log_owner"]]
            notes = log["notes"]
            if "value" in notes:
                notes = tidy_notes(notes["value"])
                notes = re.sub(r"<\/?[brpuli]+\s?\/?>","",notes).strip().replace("\n","; ").replace("&amp;","and").strip()
                
                #record["raw_notes"] = notes               
                
                noteParts = notes.split(";")
                cleanNotes = []
                for np in noteParts:
                    np = np.strip()
                    if np.startswith("Wind:"):
                        record["wind_speed"] = np # safest to tidy visually
                    elif np.startswith("Direction:") or np.startswith("wind direction:"):
                        record["wind_direction"] = np.split(":")[1].strip()
                    elif np.startswith("Wind speed"):# or np.startswith("wind speed (mph):") or np.startswith("wind speed (kph):"):
                        record["wind_speed"] = np.split(":")[1].strip()
                    elif np.startswith("Wind speed (mph):"):
                        record["wind_speed"] = np.split(":")[1].strip() + " mph"
                    elif np.startswith("Wind speed (kph):"):
                        record["wind_speed"] = np.split(":")[1].strip() + " kph"
                    elif np.startswith("Weather:"):
                        record["weather_desc"] = np.split(":")[1].strip()
                    elif np.startswith("Temperature:") or np.startswith("Temp:") or np.startswith("temperature (C):"):
                        record["temperature"] = np.split(":")[1].strip()
                    elif np.startswith("start time:") or np.startswith("Start:"):
                        record["start"] = to_24_clock(np.split(": ")[1])
                    elif np.startswith("stop time:") or np.startswith("Finish:"):
                        record["finish"] = to_24_clock(np.split(": ")[1])
                    else:
                        cleanNotes.append(np)
                if "start" in record and "finish" in record:
                    record["hours"] = to_hours(record.get("start"), record.get("finish"))
                    
                print(notes)
                record["notes"] = ". ".join(cleanNotes).replace("..",".").replace("Notes:","").strip() 

            #mt = log["material"]
            #if mt:
            #    mt = ";".join([str(m["id"]) + " : " + str(m["name"]) for m in mt])
            #    record["material_list"] = mt

            qs =  log["quantity"]
            quantities = []
            for q in qs:
                m = q["measure"]
                if m == "time":
                    record["hours"] = format_hours(q)
                elif m == "rate":
                    if "unit" in q:
                        quantities.append(str(q["label"]) + "@@" + str(q["value"]) + "@@" + str(q["unit"]["name"]))                    
                    else:
                        quantities.append(str(q["label"]))
                elif m == "volume":
                    record["spray_volume"] = str(q["value"]) + " " + str(q["unit"]["name"])
                elif m == "area":
                    record["area_sprayed"] = q["value"]
                    record["area_sprayed_unit"] = q["unit"]["name"]
            
            #quants = ";".join(quantities)
            #if ";" not in quants and "False" in quants:
            #    quants = quants.replace("False",mt.split(":")[1].strip())
            #record["quantities"] = quants

            for a in areas:
                for q in quantities:
                    nr = record
                    qp = q.split("@@")
                    nr["product"] = qp[0]
                    if len(qp) > 1:
                        nr["rate"] = qp[1]
                        nr["rate_unit"] = qp[2]
                    a2 = area_d.get(a)
                    print(a2)
                    nr["field"] = a2.get("field_name")
                    nr["experiment"] = a2.get("exp")
                    csvwriter.writerow(record)


def list_fields_csv():
    items = farm.area.get(filters={'area_type': 'field'})["list"]
    
    csvwriter = None 
    with open("data/fields.csv","w",newline="") as csvfile:
        fieldnames = ["field_id","field_name","field_boundary"]
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csvwriter.writeheader()

        for item in items:
            record = {}
            record["field_id"] = item["tid"]
            record["field_name"] = item["name"]
            csvwriter.writerow(record)

def area_dict():
    ad = {}

    items = farm.area.get(filters={'area_type': 'bed'})["list"]    
    for item in items:
        area_id = item["tid"]
        print(area_id)
        exp_name = item["name"]
        if item["parent"]:
            field_id = item["parent"][0]["id"]
            field_name = item["parent"][0]["name"]
        else:
            field_id = ""
            field_name = ""
        ad[area_id] = {"exp_id":area_id,"exp_name":exp_name,"field_id":field_id,"field_name":field_name}

    items = farm.area.get(filters={'area_type': 'field'})["list"]
    for item in items:
        field_id = item["tid"]
        field_name = item["name"]

        ad[field_id] = {"exp_id":"","exp_name":"","field_id":field_id,"field_name":field_name}

    items = farm.area.get(filters={'area_type': 'building'})["list"]
    for item in items:
        field_id = item["tid"]
        field_name = item["name"]

        ad[field_id] = {"exp_id":"","exp_name":"","field_id":field_id,"field_name":field_name}
    return ad

def list_experiments_csv():
    items = farm.area.get(filters={'area_type': 'bed'})["list"]
    
    csvwriter = None 
    with open("data/experiments.csv","w",newline="") as csvfile:
        fieldnames = ["experiment_id","experiment_name","field_id","field_name"]
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csvwriter.writeheader()

        for item in items:
            record = {}
            record["experiment_id"] = item["tid"]
            record["experiment_name"] = item["name"]

            record["field_id"] = item["parent"][0]["id"]
            record["field_name"] = item["parent"][0]["name"]
            csvwriter.writerow(record)

def list_equipment_csv():
    items = farm.asset.get({"type":"Equipment"})["list"]

    csvwriter = None 
    with open("data/equipment.csv","w",newline="") as csvfile:
        # Using a dictionary writer as it should take care of column ordering 
        fieldnames = ["equipment_id","equipment_name","manufacturer","model","serial_number","description"]
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csvwriter.writeheader()

        for item in items:
            record = {}    
            print(item["id"])
            record["equipment_id"] = item["id"]
            record["equipment_name"] = item["name"]
            record["manufacturer"] = item["manufacturer"]
            record["model"] = item["model"]
            record["serial_number"] = item["serial_number"]
            if "value" in item["description"]:
                record["description"] = tidy_notes(item["description"]["value"])
            csvwriter.writerow(record)

def list_crops_csv():
    print("hello again")
    items = farm.term.get("farm_crops")["list"]
    print("hello again again")
    print(json.dumps(items, indent=4, sort_keys=True))
    
    csvwriter = None 
    with open("data/crops.csv","w",newline="") as csvfile:

        # Using a dictionary writer as it should take care of column ordering 
        fieldnames = ["crop_id","crop_name","description"]
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csvwriter.writeheader()

        for item in items:
            if not item["parent"]:
                record = {}    
                record["crop_id"] = item["tid"]
                record["crop_name"] = item["name"]
                record["description"] = strip_html(item["description"]).strip()
                csvwriter.writerow(record)

def list_varieties_csv():
    print("hello again")
    items = farm.term.get("farm_crops")["list"]
    #print(json.dumps(items, indent=4, sort_keys=True))
    
    csvwriter = None 
    with open("data/varieties.csv","w",newline="") as csvfile:

        # Using a dictionary writer as it should take care of column ordering 
        fieldnames = ["variety_id","crop_id","variety_name","description"]
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csvwriter.writeheader()

        for item in items:
            if item["parent"]:
                record = {}    
                record["variety_id"] = item["tid"]
                record["crop_id"] = item["parent"][0]["id"]
                record["variety_name"] = item["name"]
                record["description"] = strip_html(item["description"]).strip()
                csvwriter.writerow(record)
            else:
                pass        

def list_categories_csv():
    items = farm.term.get("farm_log_categories")["list"]
    
    csvwriter = None 
    with open("data/categories.csv","w",newline="") as csvfile:

        # Using a dictionary writer as it should take care of column ordering 
        fieldnames = ["category_id","category_name","description"]
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csvwriter.writeheader()

        for item in items:
            record = {}    
            record["category_id"] = item["tid"]
            record["category_name"] = item["name"]
            record["description"] = strip_html(item["description"])
            csvwriter.writerow(record)
    
def list_area_input_logs():
    equipmentDict = equipment()
    
    logs = farm.log.get(filters={'type': 'farm_input'})['list']
    
    csvwriter = None 
    with open("data/report_input.csv","w",newline="") as csvfile:
        # Using a dictionary writer as it should take care of column ordering 
        fieldnames = ["log_id","log_date","log_name","field","areas","equipment_list","categories","hours","material_list","quantities","spray_volume","area_sprayed","area_sprayed_unit", "purpose","method","plots","start","finish","wind_speed","wind_direction","temperature","weather_desc","notes","raw_notes"]
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csvwriter.writeheader()
        for log in logs:
            record = {}

            print(log["id"])
            record["log_id"] = "https://rothamstedfarm.farmos.net/log/" + log["id"]
            record["log_name"] = log["name"]
            record["log_date"] = to_date(log["timestamp"])
            record["field"] = get_fieldname(log["area"][0]["id"])

            eq = [a["id"] for a in log["equipment"]]
            record["equipment_list"] = ";".join((pandas.Series(eq)).map(equipmentDict))
            record["areas"] = ";".join([a["name"] for a in log["area"]])
            record["categories"] = ";".join([a["name"] for a in log["log_category"]])
            record["purpose"] = log["input_purpose"]
            record["method"] = log["input_method"]
            record["operators"] = decode_staff([a["id"] for a in log["log_owner"]])
            record['raw_operators'] = [a["id"] for a in log["log_owner"]]
            notes = log["notes"]
            if "value" in notes:
                notes = tidy_notes(notes["value"])
                notes = re.sub(r"<\/?[brpuli]+\s?\/?>","",notes).strip().replace("\n","; ").replace("&amp;","and").strip()
                
                record["raw_notes"] = notes               
                
                noteParts = notes.split(";")
                cleanNotes = []
                for np in noteParts:
                    np = np.strip()
                    if np.startswith("Wind:"):
                        nps = np.split(" ")
                        record["wind_speed"] = " ".join(nps[1:2])
                        if len(nps)>3:
                            record["wind_direction"] = nps[3]
                    elif np.startswith("Direction:") or np.startswith("wind direction:"):
                        record["wind_direction"] = np.split(":")[1].strip()
                    elif np.startswith("Wind speed:") or np.startswith("wind speed (mph):"):
                        record["wind_speed"] = np.split(":")[1].strip()
                    elif np.startswith("Weather:"):
                        record["weather_desc"] = np.split(":")[1].strip()
                    elif np.startswith("Temperature:") or np.startswith("Temp:") or np.startswith("temperature (C):"):
                        record["temperature"] = np.split(":")[1].strip()
                    elif np.startswith("start time:") or np.startswith("Start:"):
                        record["start"] = to_24_clock(np.split(": ")[1])
                    elif np.startswith("stop time:") or np.startswith("Finish:"):
                        record["finish"] = to_24_clock(np.split(": ")[1])
                    else:
                        cleanNotes.append(np)
                if "start" in record and "finish" in record:
                    record["hours"] = to_hours(record.get("start"), record.get("finish"))
                    
                print(notes)
                record["notes"] = ". ".join(cleanNotes).replace("..",".").replace("Notes:","").strip() 

            mt = log["material"]
            if mt:
                mt = ";".join([str(m["id"]) + " : " + str(m["name"]) for m in mt])
                record["material_list"] = mt

            qs =  log["quantity"]
            quantities = []
            for q in qs:
                m = q["measure"]
                if m == "time":
                    record["hours"] = format_hours(q)
                elif m == "rate":
                    if "unit" in q:
                        quantities.append(str(q["label"]) + " @ " + str(q["value"]) + " " + str(q["unit"]["name"]))                    
                    else:
                        quantities.append(str(q["label"]))
                elif m == "volume":
                    record["spray_volume"] = str(q["value"]) + " " + str(q["unit"]["name"])
                elif m == "area":
                    record["area_sprayed"] = q["value"]
                    record["area_sprayed_unit"] = q["unit"]["name"]
            
            quants = ";".join(quantities)
            if ";" not in quants and "False" in quants:
                quants = quants.replace("False",mt.split(":")[1].strip())
            record["quantities"] = quants
                           
            csvwriter.writerow(record)

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
    elif sys.argv[1].startswith("list") or sys.argv[1].startswith("export"):
        print([sys.argv[1]])
        globals()[sys.argv[1]]()
    else:
        print("hello")
        globals()[sys.argv[1]]()