from flask import jsonify
from models.database import Database
from SSMSchema.ssmschema import ticketsschema
import uuid

class Tickets(object):
    def __init__(self,complaint_id,date,employee_id,customer_id,complaint,status,receive_status,ticket_id=None):
        self.ticket_id = uuid.uuid4().hex if ticket_id is None else ticket_id 
        self.complaint_id = complaint_id
        self.date = date
        self.employee_id = employee_id
        self.customer_id = customer_id
        self.complaint = complaint
        self.status = status
        self.receive_status =receive_status

    def save_to_mongo(self):
        if ticketsschema.validate([self.json()]):
            Database.insert(collection='tickets',data=self.json())
            res = {'ticket_id' : self.ticket_id + ' added'}
            result= jsonify({'result' : res})
            return result
        else:
            return "Schema not matched!"
    def json(self):
        return {'ticket_id': self.ticket_id,
            'complaint_id': self.complaint_id,
            'date': self.date,
            'employee_id': self.employee_id,
            'customer_id': self.customer_id,
            'complaint': self.complaint,
            'status': self.status,
            'receive_status': self.receive_status
        }   
    
    @staticmethod
    def from_mongo(tic_id):
        return Database.find_one(collection='tickets',query={'ticket_id':tic_id})
    
    @staticmethod
    def from_mongo_get_all_tickets():
        return Database.find(collection='tickets', query={})
    
    @staticmethod
    def from_mongo_by_customer(cus_id):
        return Database.find(collection='tickets',query={'customer_id':cus_id})

    @staticmethod
    def from_mongo_by_employee(emp_id):
        return Database.find(collection='tickets',query={'employee_id':emp_id})

    @staticmethod
    def from_mongo_get_all_pending_tickets():
        return Database.find(collection='tickets',query={'employee_id': str(None),'status': 'Open','receive_status':'Pending'})

    @staticmethod
    def from_mongo_update(tic_id,data_update):
        Database.update(collection='tickets',query={'ticket_id':tic_id},data=data_update)
        return Tickets.from_mongo(tic_id)
    
    @staticmethod
    def from_mongo_delete(tick_id):
        return Database.delete_one(collection='tickets',query={'ticket_id':tick_id})