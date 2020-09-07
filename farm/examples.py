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


m = "Silicate of Soda @125 Kg/ha + MOP @250 Kg/ha + TSP"

dic = [{"name": "TSP","tid": "149"},{"name": "MOP","tid": "148"},{"name": "Silicate of Soda","tid": "147"}]

mp = m.split("+")
for p in mp:
    #p = p.replace(" ","")
    mx = p.split("@")[0]

    #return [f for f in items for p in f["parent"] if p["name"] == "FERTILISERS"]

    id = [f["tid"] for f in dic if f["name"] == mx]
    print(id[0] + " " + mx)


