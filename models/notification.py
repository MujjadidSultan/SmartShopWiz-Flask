from flask import jsonify
from models.database import Database
from SSMSchema.ssmschema import notificationschema
import uuid

class Notification(object):
    def __init__(self,from_user_id,title,message,url,read_status,delivery_status,to_user_id,notification_id=None):
        self.notification_id = uuid.uuid4().hex if notification_id is None else notification_id 
        self.from_user_id = from_user_id
        self.title = title
        self.message = message
        self.url = url
        self.read_status = read_status
        self.delivery_status = delivery_status
        self.to_user_id = to_user_id

    def save_to_mongo(self):
        if notificationschema.validate([self.json()]):
            Database.insert(collection='notifications',data=self.json())
            res = {'notification_id' : self.notification_id + ' added'}
            result= jsonify({'result' : res})
            return result
        else:
            return "Schema not matched!"
    def json(self):
        return {'notification_id': self.notification_id,
            'from_user_id': self.from_user_id,
            'title': self.title,
            'message': self.message,
            'url': self.url,
            'read_status': self.read_status,
            'delivery_status': self.delivery_status,
            'to_user_id': self.to_user_id    
        }   
    
    @staticmethod
    def from_mongo(not_id):
        return Database.find_one(collection='notifications',query={'notification_id':not_id})
    
    @staticmethod
    def from_mongo_get_all_notifications():
        return Database.find(collection='notifications', query={})
    
    @staticmethod
    def from_mongo_update(not_id,data_update):
        Database.update(collection='notifications',query={'notification_id':not_id},data=data_update)
        return Notification.from_mongo(not_id)
    
    @staticmethod
    def from_mongo_delete(notif_id):
        return Database.delete_one(collection='notifications',query={'notification_id': notif_id})