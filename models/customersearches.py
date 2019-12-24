from flask import jsonify
from SSMSchema.ssmschema import customersearchesschema
from models.database import Database
import uuid

class CustomerSearches(object):
    def __init__(self,customer_id,search,date,search_id=None):
        self.search_id = uuid.uuid4().hex if search_id is None else search_id
        self.customer_id = customer_id
        self.search = search
        self.date = date

    def save_to_mongo(self):
        if customersearchesschema.validate([self.json()]):
            Database.insert(collection='customersearches',data=self.json())
            res = {'search_id': self.search_id + "Added"}
            result = jsonify({'result':res})
            return result
        else:
            return "Schema not matched!"
    
    def json(self):
        return {'search_id': self.search_id,
            'customer_id': self.customer_id,
            'search': self.search,
            'date': self.date
        }

    @staticmethod
    def from_mongo(search_id):
        return Database.find_one(collection='customersearches',data=self.json())
    
    @staticmethod
    def from_mongo_all_searches_of_customer(customer_id):
        return Database.find(collection='customersearches',query={'customer_id':customer_id})

    @staticmethod
    def from_mongo_all_searches():
        return Database.find(collection='customersearches',query={})