'''
Created on 24 Jun 2019

@author: ostlerr
'''
import configparser
import farmOS

class FarmService(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        config = configparser.ConfigParser()
        config.read('config.ini')
        hostname = config['AUTH']['host']
        username = config['AUTH']['username']
        password = config['AUTH']['password']
        
        # 1. connect
        self.farm = farmOS.farmOS(hostname, username, password)
        success = self.farm.authenticate()
        
        #self.equipment = {}
        #data = self.farm.asset.get({"type":"equipment"})
        #for item in data:
        #    self.equipment[item["id"]] = item["name"]
        #    print(item["id"] + ", " + item["name"])
    
    def myFarm(self):
        return self     
    
    def equipmentItem(self,equipmentId):
        return self.equipment[equipmentId]
    
    