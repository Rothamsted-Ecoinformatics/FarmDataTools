import json
import datetime
from service import FarmService

myFarm = FarmService().myFarm()

if __name__ == "__main__":    
    
    log = myFarm.farm.log.get(181)
    print(json.dumps(log, indent=4, sort_keys=True))
    #f = open("record2.json","w")
    

    

    asset = myFarm.farm.asset.get(98)
    print(json.dumps(asset, indent=4, sort_keys=True)) # works

    #asset = myFarm.farm._get_record_data('user',{'id':'3'}) # works
    #print(json.dumps(asset, indent=4, sort_keys=True))
    #log = myFarm.farm.log.get()  