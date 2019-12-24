from flask import jsonify
from models.database import Database
from SSMSchema.ssmschema import roleschema
import uuid

class Role(object):
    def __init__(self,role_name,role_id=None):
        self.role_id = uuid.uuid4().hex if role_id is None else role_id 
        self.role_name = role_name

    def save_to_mongo(self):
        if roleschema.validate([self.json()]):
            Database.insert(collection='roles',data=self.json())
            res = {'role_name' : self.role_name + ' added'}
            result= jsonify({'result' : res})
            return result
        else:
            return "Schema not matched!"
    def json(self):
        return {'role_id':self.role_id,
            'role_name': self.role_name
        }   
    
    @staticmethod
    def from_mongo(role_id):
        return Database.find_one(collection='roles',query={'role_id':role_id})
    
    @staticmethod
    def from_mongo_get_all_roles():
        return Database.find(collection='roles', query={})
    
    @staticmethod
    def from_mongo_update(role_id,data_update):
        Database.update(collection='roles',query={'role_id':role_id},data=data_update)
        return Role.from_mongo(role_id)
    