'''
Created on 25 Apr 2019

@author: ostlerr
'''
import configparser
import farmOS
import json
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd


people = {"a":1,"b":2,"c":3}
px = ["a","c"]
py = (pd.Series(px)).map(people)
print(py)
#config = configparser.ConfigParser()
#config.read('config.ini')
#hostname = config['AUTH']['host']
#username = config['AUTH']['username']
#password = config['AUTH']['password']

# updating
#payload = {"crop_family":{"id":"208"},"tid":"175"}
#headers = {'content-type': 'application/json'}

#s = requests.session()   
#print(s)
##print(s.headers)
#print(s.cookies)
#r = requests.post("https://rothamstedfarm.farmos.net/user/login?name=restws"+username+"&pass="+password+"&form_id=user-login")
#print(r)
#token = json.loads(r.text)['session']
#print(token)
#r = requests.put("https://rothamstedfarm.farmos.net/taxonomy/term/175", auth=("restws"+username, password), params=payload, headers=headers)

# 1. connect
farm = service.myFarm()
#success = farm.authenticate()

#print(success)

# 2. submit a taxonomy term
#for crop in ['sugar beet','winter oilseed rape','spring barley','grass','spring beans','phacelia','black oats','seed mix','terralife betasola','parkers PS009 mix']:
    #data = farm.term.send({'name':crop,'vocabulary':{'id':'7','resource': 'taxonomy_vocabulary'}})
    #print(data)

# 3. query a list of plantings and pretty print JSON
#plantings = farm.asset.get({'type':'planting'})
#print(json.dumps(plantings, indent=4, sort_keys=True))

# 4. query a taxonomy term (farm area in this example) by ID and pretty print JSON
#areas = farm.area.get({'name':'20/WW/1234'})#.term.get(127)
#areas = farm.log.get({'type':'farm_input'})

res = farm.term.get(175)

print(json.dumps(res, indent=4, sort_keys=True))


#farm.term.send(payload)

#res = farm.term.get(175)
#print(json.dumps(res, indent=4, sort_keys=True))