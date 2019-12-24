from flask import jsonify
from models.database import Database
from SSMSchema.ssmschema import devicetokenschema
import uuid

class DeviceToken(object):
    def __init__(self,user_id,device_id,datetime,devicetoken_id=None):
        self.devicetoken_id = uuid.uuid4().hex if devicetoken_id is None else devicetoken_id 
        self.user_id = user_id
        self.device_id = device_id
        self.datetime = datetime

    def save_to_mongo(self):
        if devicetokenschema.validate([self.json()]):
            Database.insert(collection='devicetokens',data=self.json())
            res = {'devicetoken_id' : self.devicetoken_id + ' added'}
            result= jsonify({'result' : res})
            return result
        else:
            return "Schema not matched!"
    def json(self):
        return {'devicetoken_id': self.devicetoken_id,
            'user_id':self.user_id,
            'device_id':self.device_id,
            'datetime':self.datetime
            }
    
    @staticmethod
    def from_mongo(devicetoken_id):
        return Database.find_one(collection='devicetokens',query={'devicetoken_id':devicetoken_id})
    
    @staticmethod
    def from_mongo_get_all_devices_token():
        return [devicetoken for devicetoken in Database.find(collection='devicetokens',query={})]
    
    @staticmethod
    def from_mongo_update(devicetoken_id,data_update):
        Database.update(collection='devicetokens',query={'devicetoken_id':devicetoken_id},data=data_update)
        return DeviceToken.from_mongo(devicetoken_id)
    
    @staticmethod
    def from_mongo_delete(devicetoken_id):
        return Database.delete_one(collection='devicetokens',query={'devicetoken_id':devicetoken_id})
    
    @staticmethod
    def from_mongo_by_user_id(user_id):
        return Database.find_one(collection='devicetokens',query={'user_id':user_id})
    
    @staticmethod
    def from_mongo_by_user_id_and_token_id(user_id,device_id):
        return Database.find_one(collection='devicetokens',query={'user_id':user_id,'device_id':device_id})