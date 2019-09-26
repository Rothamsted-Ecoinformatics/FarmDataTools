import json
from service import FarmService

myFarm = FarmService().myFarm()



for crop in ['sugar beet','winter oilseed rape','spring barley','grass','spring beans','phacelia','black oats','seed mix','terralife betasola','parkers PS009 mix']:
    #data = farm.term.send({'name':crop,'vocabulary':{'id':'7','resource': 'taxonomy_vocabulary'}})
    #print(data)