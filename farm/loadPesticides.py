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
    if row['Prop_No'] == 'Commercial' and row['Application'] == 'Ironmax pro @5 kg/ha' and row['loaded'] == "N":
        print(row['Field'])
        fname = "data/record" + str(index) +".json"
        f = open(fname,"w")

        jsonpayload={}
    "changed": "1569345193",
    "created": "1569345193",
    "data": null,
    "date_purchase": null,
    "done": "1",
    "equipment": [
        {
            "id": "95",
            "resource": "farm_asset",
            "uri": "https://rothamstedfarm.farmos.net/farm_asset/95"
        }
    ],
    "files": [],
    "flags": [],
    "geofield": [
        {
            "bottom": "51.804787196106",
            "geo_type": "polygon",
            "geom": "POLYGON ((-0.362608559742167 51.806824961952, -0.362757117471272 51.8063759021319, -0.36057045413106 51.8060926758539, -0.360818809949938 51.8055719945078, -0.360818954924825 51.8055719965284, -0.360818809949938 51.8055719945078, -0.361194660623594 51.8047871961061, -0.361645778500054 51.8048825021602, -0.362112863287858 51.8049815357181, -0.362113008260945 51.8049815377371, -0.36211314997666 51.8049816296307, -0.362113005003573 51.8049816276117, -0.362113146719288 51.8049817195052, -0.3621130017462 51.8049817174862, -0.363968256922268 51.8053752231798, -0.363968401896753 51.8053752251965, -0.363968398643023 51.8053753150712, -0.365424433785678 51.8057108200726, -0.365424437036551 51.805710730198, -0.365424292060885 51.805710728183, -0.365424437036551 51.805710730198, -0.364643074700806 51.8067123653719, -0.364643219679628 51.8067123673878, -0.364643216427085 51.8067124572624, -0.364643219679628
51.8067123673878, -0.364026662326498 51.8075120820193, -0.364026517345156 51.8075120800026, -0.364026514091293 51.8075121698772, -0.36402636910995 51.8075121678604, -0.362739921422818 51.8070586941024, -0.362739769930286 51.8070588718331, -0.362736844283388 51.8070595504632, -0.36273141164681 51.8070613631508, -0.362721561231054 51.8070650026535, -0.362710221938335 51.8070697004663, -0.362699030879567 51.8070743104218, -0.362686215731818 51.8070797070449, -0.362673845290156 51.8070848400982, -0.362660888413085 51.8070901448255, -0.362648943135778 51.8070955535549, -0.362636253416535 51.8071014914381, -0.362622851820683 51.8071070597295, -0.362610491134312 51.8071119231523, -0.362597247538837 51.8071171339611, -0.362583130803716 51.8071224225318, -0.362569877431908 51.8071279029609, -0.36255693355739 51.8071328481785, -0.362543699719991 51.8071377893575, -0.362530456109336 51.8071430001586, -0.362517057745114 51.8071484785631, -0.362503530681827 51.8071535055748, -0.362489716912236 51.8071584386732, -0.362476927771144 51.8071631162768, -0.362463281774402 51.807167422269, -0.362449784012179 51.8071716404038, -0.36243599303018 51.8071759443741, -0.362421473887757 51.8071803281237, -0.36240640739231 51.8071838050515, -0.362391485874764 51.8071872839961, -0.362377575959198 51.8071908669445, -0.362363794735999 51.8071949012827, -0.362350026539007 51.8071985761212, -0.362335974893729 51.8072020671714, -0.362322077998197 51.8072052906151, -0.362306869764026 51.8072086756366, -0.362291990575444 51.8072109861997, -0.3622781392764 51.807212951395, -0.362265635143823 51.8072137663901, -0.362251977683464 51.8072143854836, -0.362238932717632 51.807214113906, -0.362224859860563 51.8072141876925, -0.362212417618084 51.8072132950662, -0.362199115267021 51.8072121207012, -0.36218697601611 51.8072108726122, -0.362177571845394 51.8072102021301, -0.36217323872577 51.8072096921873, -0.362173232210744 51.8072098719363, -0.362172494279495 51.8072102213393, -0.362172639259735 51.8072102233583, -0.36026476449918 51.8069580295568, -0.360264761237902 51.8069581194312, -0.36042436317895 51.8065411379907, -0.362608559742167 51.806824961952))",
            "lat": "51.806130627533",
            "latlon": "51.806130627533,-0.362829801029",
            "left": "-0.365424437037",
            "lon": "-0.362829801029",
            "right": "-0.360264761238",
            "schemaorg_shape": "51.804787196106,-0.365424437037 51.804787196106,-0.360264761238 51.807512169877,-0.360264761238 51.807512169877,-0.365424437037 51.804787196106,-0.365424437037",
            "srid": null,
            "top": "51.807512169877"
        }
    ],
    "id": "195",
    "images": [],
    "input_method": null,
    "input_purpose": "Spraying",
    "input_source": null,
    "inventory": [],
    "log_category": [],
    "log_owner": [
        {
            "id": "17",
            "resource": "user",
            "uri": "https://rothamstedfarm.farmos.net/user/17"
        }
    ],
    "lot_number": null,
    "material": [
        {
            "id": "271",
            "resource": "taxonomy_term",
            "uri": "https://rothamstedfarm.farmos.net/taxonomy_term/271"
        }
    ],
    "movement": {
        "area": [],
        "geometry": null
    },
    "name": "Spraying: slug pellets in GREAT FIELD 1/2",
    "notes": {
        "format": "farm_format",
        "value": "<p>Applied to area before it was ploughed<br />\nRate is dummy value as none stated</p>\n"
    },
    "quantity": [
        {
            "label": "slug pellets",
            "measure": "rate",
            "unit": {
                "id": "148",
                "resource": "taxonomy_term",
                "uri": "https://rothamstedfarm.farmos.net/taxonomy_term/148"
            },
            "value": "5"
        },
        {
            "label": false,
            "measure": "time",
            "unit": {
                "id": "262",
                "resource": "taxonomy_term",
                "uri": "https://rothamstedfarm.farmos.net/taxonomy_term/262"
            },
            "value": false
        }
    ],
    "timestamp": "1565650800",
    "type": "farm_input",
    "uid": {
        "id": "17",
        "resource": "user",
        "uri": "https://rothamstedfarm.farmos.net/user/17"
    },
    "url": "https://rothamstedfarm.farmos.net/log/195"
}

        #areacodes = row['field_id'].split("-")
        areas = []
        #for a in areacodes:
        areas.append({"id":row['_R_field'],"resource": "taxonomy_term"})

        jsonpayload["area"] = areas
        
        jsonpayload["asset"] = []
        #jsonpayload["changed"] = str(int(datetime.datetime.strptime(row['event_date'], "%Y-%m-%d %H:%M:%S BST %Y").timestamp()))
        jsonpayload["created"] = str(int(datetime.datetime.strptime(row['event_date'], "%a %b %d %H:%M:%S BST %Y").timestamp()))
        jsonpayload["data"] = ""    
        jsonpayload["done"] = "1"
        
        jsonpayload["equipment"] = [{"id":row['_R_equipment'],"resource": "farm_asset"},{"id":"12","resource": "farm_asset"}]
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

