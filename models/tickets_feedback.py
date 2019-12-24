from flask import jsonify
from models.database import Database
from SSMSchema.ssmschema import tickets_feedbackschema
import uuid

class TicketsFeedback(object):
    def __init__(self,ticket_id,feedback,status,date):
        self.ticket_id = ticket_id
        self.feedback = feedback
        self.status = status
        self.date = date

    def save_to_mongo(self):
        if tickets_feedbackschema.validate([self.json()]):
            Database.insert(collection='tickets_feedback',data=self.json())
            res = {'ticket_id' : self.ticket_id + ' added'}
            result= jsonify({'result' : res})
            return result
        else:
            return "Schema not matched!"
    def json(self):
        return {'ticket_id': self.ticket_id,
            'feedback': self.feedback,
            'status': self.status,
            'date': self.date
        }   
    
    @staticmethod
    def from_mongo(tick_id):
        return Database.find_one(collection='tickets_feedback',query={'ticket_id':tick_id})
    
    @staticmethod
    def from_mongo_get_all_tickets_feedbacks():
        return Database.find(collection='tickets_feedback', query={})
    
    @staticmethod
    def from_mongo_update(tick_id,data_update):
        Database.update(collection='tickets_feedback',query={'ticket_id':tick_id},data=data_update)
        return TicketsFeedback.from_mongo(tick_id)
    
    @staticmethod
    def from_mongo_delete(ticket_id):
        return Database.delete_one(collection='tickets_feedback', query={'ticket_id':ticket_id})