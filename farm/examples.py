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
import datetime as dt

import re

#start="15:00"
#end="16:45"
#start_dt = dt.datetime.strptime(start, '%H:%M')
#end_dt = dt.datetime.strptime(end, '%H:%M')
#diff = (end_dt - start_dt) 
#print(diff)


#s = "start time: 3:15 - finish time: 7:25 (plots 106 &amp"
#times = re.findall(r'([0-9]+:[0-9]+)',s) 
#st2 = .split("-")[2]
#print(times[0])
#print(times[1])

#s = "80"
#st = int(s)*60
#print(dt.timedelta(seconds =st))

mats = "220 : DoubleTop"
quants = "False @ 125 kg/ha"
if ";" not in quants and "False" in quants:
    quants = quants.replace("False",mats.split(":")[1].strip())
print (quants)

