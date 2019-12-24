from flask import jsonify
from SSMSchema.ssmschema import customer_idsschema
from models.database import Database
class Customer_ids(object):
    def __init__(self,customer_id,number):
        self.customer_id=customer_id
        self.number=number

    def save_to_mongo(self):
        if customer_idsschema.validate([self.json()]):
            Database.insert(collection='customer_ids',data=self.json())
            result = jsonify({'result': self.customer_id+'number added.'})
            return result
        else:
            return 'Schema Not Matched'

    
    def json(self):
        return {'customer_id': self.customer_id,
            'number': self.number
        }

    @staticmethod
    def from_mongo(customer_id):
        return Database.find_one(collection='customer_ids',query={'customer_id': customer_id})

    @staticmethod
    def from_mongo_update(customer_id,dataupdate):
        Database.update(collection='customer_ids',query={'customer_id':customer_id},data=dataupdate)
        return 

    @staticmethod
    def from_mongo_get_all():
        return Database.find(collection='customer_ids',query={})