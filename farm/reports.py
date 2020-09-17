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


def main():
    pass

def decode_staff(people):
    staff_lookup = {"59":"Andrea Arvai","50":"Ben Flannery","16":"Chris Mackay","36":"Ian Shield","37":"Christoph Russell","41":"Tim Hall","20":"Martin Gardner","40":"Rob","43":"Ben Smith","39":"Fred","3":"Nick Chichester-Miles","17":"Richard Ostler"}
    ps = ";".join(pandas.Series(people).map(staff_lookup).tolist())
    return ps

def areas():
    items = farm.area.get()["list"]
    return dict((f["tid"],f["name"]) for f in items)

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
    if h["unit"]["name"] == "min":
        st = float(h["value"])*60                                                
    else:
        st = float(h["value"])*60*60
    return dt.timedelta(seconds=st)

def to_hours(start, finish):
    print(finish + " - " + start)
    return dt.datetime.strptime(finish, '%H:%M') - dt.datetime.strptime(start, '%H:%M')

def tidy_notes(notes):
    return re.sub(r"<\/?[brpuli]+\s?\/?>","",notes).strip().replace("\n","; ").replace("&amp;","and").strip()

def get_fieldname(id):
    fieldname = ""
    area = farm.area.get(id)["list"]

    if area[0]["area_type"] == "bed":
        parents = area[0]["parent"] 
        fieldname = parents[0]["name"]        
    else:
        fieldname = ""
    return fieldname

def get_planting(id):
    return farm.asset.get(id)

def list_sowing_logs():
    equipmentDict = equipment()
    
    logs = farm.log.get(filters={'type': 'farm_seeding'})['list']
    
    with open("data/report_sowing.csv","w",newline="") as csvfile:
        fieldnames = ["log_id","log_date","log_name","field","areas","crops","equipment_list","operators","raw_operators","categories","hours","rate","notes","raw_notes","raw_quantity"]
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csvwriter.writeheader()
        for log in logs:
            record = {}
            print(log["id"])
            record["log_id"] = "https://rothamstedfarm.farmos.net/log/" + log["id"]
            record["log_name"] = log["name"]
            record["log_date"] = to_date(log["timestamp"])

            eq = [a["id"] for a in log["equipment"]]
            
            planting = get_planting(log["asset"][0]["id"])

            record["crops"] = ";".join([a["name"] for a in planting["crop"]])

            record["equipment_list"] = ";".join((pandas.Series(eq)).map(equipmentDict))
            record["field"] = get_fieldname(planting["location"][0]["id"])
            record["areas"] = ";".join([a["name"] for a in planting["location"]])
            record["categories"] = ";".join([a["name"] for a in log["log_category"]])
            record["operators"] = decode_staff([a["id"] for a in log["log_owner"]])
            record['raw_operators'] = [a["id"] for a in log["log_owner"]]
            notes = log["notes"]
            
            if "value" in notes:
                record["raw_notes"] = notes["value"]
                notes = notes["value"]
                notes = re.sub(r"<\/?[brpuli]+\s?\/?>","",notes).strip().replace("&amp;","and").replace("\n",";").replace("Notes:","")
                record["notes"] = notes

            qs =  log["quantity"]
            record["raw_quantity"] = qs

            for q in qs:
                m = q["measure"]
                if m == "time":
                    record["hours"] = format_hours(q)
                elif m == "rate":
                    record["rate"] = format_count(q)                
     
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

def list_harvest_logs():
    equipmentDict = equipment()
    
    logs = farm.log.get(filters={'type': 'farm_harvest'})['list']
        
    with open("data/report_harvest.csv","w",newline="") as csvfile:
        fieldnames = ["log_id","log_date","log_name","field", "areas","equipment_list","operators","raw_operators","categories","hours","start","finish","weight","weight_unit","count","notes","raw_notes"]
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csvwriter.writeheader()
        for log in logs:
            record = {}
            print(log["id"])
            record["log_id"] = "https://rothamstedfarm.farmos.net/log/" + log["id"]
            record["log_name"] = log["name"]
            record["log_date"] = to_date(log["timestamp"])

            eq = [a["id"] for a in log["equipment"]]
            record["field"] = get_fieldname(log["area"][0]["id"])
            record["equipment_list"] = ";".join((pandas.Series(eq)).map(equipmentDict))
            record["areas"] = ";".join([a["name"] for a in log["area"]])
            record["categories"] = ";".join([a["name"] for a in log["log_category"]])
            record["operators"] = decode_staff([a["id"] for a in log["log_owner"]])
            record['raw_operators'] = [a["id"] for a in log["log_owner"]]
            notes = log["notes"]
            if "value" in notes:
                notes = notes["value"]
                notes = re.sub(r"<\/?[brpuli]+\s?\/?>","",notes).strip().replace("&amp;","and").strip().replace("\n",";")
                
                record["raw_notes"] = notes               
                
                noteParts = notes.split(";")
                cleanNotes = []
                for np in noteParts:
                    np = np.strip()
                    npt = np.lower()
                    if npt.startswith("start time:") or npt.startswith("start:"):
                        times = re.findall(r'([0-9]+:[0-9]+)',npt)
                        if ("-" in npt):
                            record["start"] = to_24_clock(times[0])
                            record["finish"] = to_24_clock(times[1])
                        else:
                            record["start"] = to_24_clock(times[0])
                    elif npt.startswith("stop time:") or npt.startswith("finish:") or npt.startswith("finish time:"):
                        times = re.findall(r'([0-9]+:[0-9]+)',npt)
                        record["finish"] = to_24_clock(times[0])
                    else:
                        cleanNotes.append(np)
                if "start" in record and "finish" in record:
                    print(record.get("start") + " : " + record.get("finish"))
                    record["hours"] = to_hours(record.get("start"),record.get("finish"))
                    
                print(notes)
                record["notes"] = ". ".join(cleanNotes).replace("..",".").replace("Notes:","").strip() 

            qs =  log["quantity"]

            for q in qs:
                m = q["measure"]
                if m == "time":
                    record["hours"] = format_hours(q)
                elif m == "weight":# and q["unit"]["id"] == "262"::
                    record["weight"] = q["value"]
                    record["weight_unit"] = q["unit"]["name"]
                elif m == "count":
                    record["count"] = format_count(q)
            csvwriter.writerow(record)

def list_observation_logs():
    logs = farm.log.get(filters={'type': 'farm_observation'})['list']
    csvwriter = None 
    with open("data/report_observation.csv","w",newline="") as csvfile:
        fieldnames = ["log_id","log_date","log_name","field", "areas","equipment_list","operators","raw_operators","categories","hours","start","finish","weight","weight_unit","count","notes","raw_notes"]
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csvwriter.writeheader()
        for log in logs:
            if log["area"]:
                record = {}
                print(log["id"])
                record["log_id"] = "https://rothamstedfarm.farmos.net/log/" + log["id"]
                record["log_name"] = log["name"]
                record["log_date"] = to_date(log["timestamp"])
                record["field"] = get_fieldname(log["area"][0]["id"])
                record["areas"] = ";".join([a["name"] for a in log["area"]])
                record["categories"] = ";".join([a["name"] for a in log["log_category"]])        
                record["operators"] = decode_staff([a["id"] for a in log["log_owner"]])
                record['raw_operators'] = [a["id"] for a in log["log_owner"]]
                notes = log["notes"]
                if "value" in notes:
                    notes = notes["value"]
                    notes = re.sub(r"<\/?[brpuli]+\s?\/?>","",notes).strip().replace("&amp;","and").strip().replace("\n",";")                
                    record["notes"] = notes

                csvwriter.writerow(record)

def list_input_logs():
    equipmentDict = equipment()
    
    logs = farm.log.get(filters={'type': 'farm_input'})['list']
    
    csvwriter = None 
    with open("data/report_input.csv","w",newline="") as csvfile:
        # Using a dictionary writer as it should take care of column ordering 
        fieldnames = ["log_id","log_date","log_name","field","areas","equipment_list","operators","raw_operators","categories","hours","material_list","quantities","spray_volume","area_sprayed","area_sprayed_unit", "purpose","method","plots","start","finish","wind_speed","wind_direction","temperature","weather_desc","notes","raw_notes"]
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

def list_fields_csv():
    items = farm.area.get(filters={'area_type': 'field'})["list"]
    
    csvwriter = None 
    with open("data/fields.csv","w",newline="") as csvfile:
        # Using a dictionary writer as it should take care of column ordering 
        fieldnames = ["field_id","field_name","field_boundary"]
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csvwriter.writeheader()

        for item in items:
            record = {}
            record["field_id"] = item["tid"]
            record["field_name"] = item["name"]
            if item["geofield"]:
                if item["geofield"][0]["geom"]:
                    record["field_boundary"] = item["geofield"][0]["geom"].replace("MULTI","").replace("POLYGON","").strip()
            csvwriter.writerow(record)

def list_experiments_csv():
    items = farm.area.get(filters={'area_type': 'bed'})["list"]
    
    csvwriter = None 
    with open("data/experiments.csv","w",newline="") as csvfile:
        # Using a dictionary writer as it should take care of column ordering 
        fieldnames = ["experiment_id","experiment_name","field_id","experiment_boundary"]
        csvwriter = csv.DictWriter(csvfile, delimiter=",",quotechar="\"", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        csvwriter.writeheader()

        for item in items:
            record = {}
            print (item["tid"])
            record["experiment_id"] = item["tid"]
            record["experiment_name"] = item["name"]
            #if item["parent"]:
            record["field_id"] = item["parent"][0]["id"]
            if item["geofield"]:
                if item["geofield"][0]["geom"]:
                    record["experiment_boundary"] = item["geofield"][0]["geom"].replace("MULTI","").replace("POLYGON","").strip()
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
    else:
        print("hello")
        globals()[sys.argv[1]]()