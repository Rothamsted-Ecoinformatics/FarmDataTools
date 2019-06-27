'''
Created on 25 Apr 2019

@author: ostlerr
'''
import configparser
import farmOS
import json

config = configparser.ConfigParser()
config.read('config.ini')
hostname = config['AUTH']['host']
username = config['AUTH']['username']
password = config['AUTH']['password']

# 1. connect
farm = farmOS.farmOS(hostname, username, password)
success = farm.authenticate()

print(success)

# 2. submit a taxonomy term
#for crop in ['sugar beet','winter oilseed rape','spring barley','grass','spring beans','phacelia','black oats','seed mix','terralife betasola','parkers PS009 mix']:
    #data = farm.term.send({'name':crop,'vocabulary':{'id':'7','resource': 'taxonomy_vocabulary'}})
    #print(data)

# 3. query a list of plantings and pretty print JSON
#plantings = farm.asset.get({'type':'planting'})
#print(json.dumps(plantings, indent=4, sort_keys=True))

# 4. query a taxonomy term (farm area in this example) by ID and pretty print JSON
areas = farm.area.get({'name':'20/WW/1234'})#.term.get(127)
#areas = farm.log.get({'type':'farm_input'})
print(json.dumps(areas, indent=4, sort_keys=True))

farm.area.send(payload)