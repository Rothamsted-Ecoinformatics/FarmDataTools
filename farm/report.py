import json
from service import FarmService

#import service
#from examples import farm
myFarm = FarmService().myFarm()

class Fertilizer():
    def __init__(self):
        self.id = None
        self.name = None
        self.equipment = None
        self.date = None
        self.timespent = None
        self.fertiliser = None
        self.quantity = None
        self.unit = None
        self.note = None
    
    def __str__(self):
        return ",".join([str(value) for attr, value in self.__dict__.items()])

def getAreaByName(areaName):
    areas = myFarm.area.get({'name':areaName})#.term.get(127)
    print(json.dumps(areas, indent=4, sort_keys=True))

def getFertilizerApplications(plantingId):
    #logs = myFarm.log.get({'type':'farm_input'})
    #logs = myFarm.log.get(#{"input_purpose":"Fertiliser"})
    logs = myFarm.farm.log.get({"asset":[{"id",plantingId}],"input_purpose":"Fertiliser"})
    #print(logs)
    fertilisers = []
    
    for log in logs:
        f = Fertilizer()
        f.id = log["id"]
        f.name = log["name"]
        f.equipment = " + ".join([myFarm.equipmentItem(i["id"]) for i in log["equipment"]]) 
        fertilisers.append(f)
        
       
        print(f)
        
    print("hello hello")
    #logs = myFarm.log.get({"quantity":{"value":"140"}})
    #logs = myFarm.log.get(54)
    #logs = myFarm.log.get({"area":[{"id":"54"}]})
    #if logs == []:
    #    logs = myFarm.log.get()
    return logs

def getExperimentDiary(plantingId):
    logs = myFarm.asset.get(plantingId)
    return(logs)

def getTerms():
    return myFarm.farm.term.get()

if __name__ == "__main__":    
    areaName = "BLACKHORSE"
    #getAreaByName("20/WW/1234")
    #data = getFertilizerApplications(70)
    #data = getExperimentDiary(70)
    data = getTerms()
    for d in data:
        print(d["name"] + " - " + d["vocabulary"]["id"])
    
    #print(json.dumps(data, indent=4, sort_keys=True))