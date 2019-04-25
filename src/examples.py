'''
Created on 25 Apr 2019

@author: ostlerr
'''
import configparser
import farmOS
import json

config = configparser.ConfigParser()
config.read('config.ini')
experiment = config['EXPERIMENT']['name']
hostname = config['AUTH']['hostname']
username = config['AUTH']['username']
password = config['AUTH']['password']

# 1. connect
farm = farmOS.farmOS(hostname, username, password)
success = farm.authenticate()
print(success)

# 2. submit a taxonomy term
data = farm.term.send({'name':'Chambo','vocabulary':{'id':'7','resource': 'taxonomy_vocabulary'}})
print(data)

# 3. query a list of plantings and pretty print JSON
plantings = farm.asset.get({'type':'planting'})
print(json.dumps(plantings, indent=4, sort_keys=True))

# 4. query a taxonomy term (farm area in this example) by ID and pretty print JSON
area = farm.term.get(127)
print(json.dumps(area, indent=4, sort_keys=True))