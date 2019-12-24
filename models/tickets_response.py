from flask import jsonify
from models.database import Database
from SSMSchema.ssmschema import tickets_responseschema
import uuid

class TicketsResponse(object):
    def __init__(self,ticket_id,from_user_id,to_user_id,message,date,res_ticket_id=None):
        self.res_ticket_id = uuid.uuid4().hex if res_ticket_id is None else res_ticket_id 
        self.ticket_id = ticket_id
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.message = message
        self.date = date


    def save_to_mongo(self):
        if tickets_responseschema.validate([self.json()]):
            Database.insert(collection='tickets_response',data=self.json())
            res = {'res_ticket_id' : self.res_ticket_id + ' added'}
            result= jsonify({'result' : res})
            return result
        else:
            return "Schema not matched!"
    

    def json(self):
        return {'res_ticket_id':self.res_ticket_id,
            'ticket_id': self.ticket_id,
            'from_user_id': self.from_user_id,
            'to_user_id': self.to_user_id,
            'message': self.message,
            'date':self.date
        }   
    

    @staticmethod
    def from_mongo(tick_id):
        return Database.find_one(collection='tickets_response',query={'ticket_id':tick_id})

    @staticmethod
    def from_mongo_get_all_by_ticket(tic_id):
        return Database.find(collection='tickets_response',query={'ticket_id':tic_id})
    
    @staticmethod
    def from_mongo_get_all_ticket_responses():
        return Database.find(collection='tickets_response', query={})
    
    @staticmethod
    def from_mongo_update(tick_id,data_update):
        Database.update(collection='tickets_response',query={'ticket_id':tick_id},data=data_update)
        return TicketsResponse.from_mongo(tick_id)
    
    @staticmethod
    def from_mongo_delete(tick_id):
        return Database.delete_one(collection='tickets_response',query={'res_ticket_id':tick_id})
    