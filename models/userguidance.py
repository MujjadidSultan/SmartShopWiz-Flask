from flask import jsonify
from SSMSchema.ssmschema import userguidanceschema
from models.database import Database
import uuid

class UserGuidance(object):
    def __init__(self,guidance_name,video_url,for_user,guidance_id=None):
        guidance_id = uuid.uuid4().hex if guidance_id is None else guidance_id
        guidance_name = guidance_name
        video_url = video_url
        for_user = for_user

    def save_to_mongo(self):
        if userguidanceschema.validate([self.json()]):
            Database.insert(collection='userguidance',data=self.json())
            res = {'guidance_id': self.guidance_id + "Added"}
            result = jsonify({'result':res})
            return result
        else:
            return "Schema not matched!"
    
    def json(self):
        return {'guidance_id': self.guidance_id,
            'guidance_name': self.guidance_name,
            'video_url': self.video_url,
            'for_user': self.for_users
        }

    @staticmethod
    def from_mongo(guidance_id):
        return Database.find_one(collection='userguidance',query={'guidance_id':guidance_id})
    
    @staticmethod
    def from_mongo_all_guidance():
        return Database.find_one(collection='userguidance',query={})

    @staticmethod
    def from_mongo_all_guidance_for_customer():
        return Database.find(collection='userguidance', query={'for_user':'customer'})

    @staticmethod
    def from_mongo_all_guidance_for_employee():
        return Database.find(collection='userguidance', query={'for_user':'employee'})

    @staticmethod
    def from_mongo_update(guidance_id,update):
        Database.update(collection='userguidance',query={'guidance_id':guidance_id},data=update)
        return UserGuidance.from_mongo(guidance_id)
    
    @staticmethod
    def from_mongo_delete(guidance_id):
        return Database.delete_one(collection='userguidance',query={'guidance_id':guidance_id})

    @staticmethod
    def from_mongo_by_name(name):
        return Database.find_one(collection='userguidance',query={'guidance_name':name})