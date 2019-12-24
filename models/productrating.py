from flask import jsonify
from SSMSchema.ssmschema import productratingschema
from models.database import Database
class Productrating(object):
    def __init__(self,product_id,customer_id,rating):
        self.product_id=product_id
        self.customer_id=customer_id
        self.rating=rating

    def save_to_mongo(self):
        if productratingschema.validate([self.json()]):
            Database.insert(collection='productrating',data=self.json())
            result = jsonify({'result': self.product_id+'rating added.'})
            return result
        else:
            return 'Schema Not Matched'

    
    def json(self):
        return {'product_id': self.product_id,
            'customer_id': self.customer_id,
            'rating': self.rating
        }
    
    @staticmethod
    def from_mongo_by_customer(cus_id):
        return Database.find(collection='productrating',query={'customer_id': cus_id})

    @staticmethod
    def from_mongo_by_product(prod_id):
        return Database.find(collection='productrating',query={'product_id': prod_id})
    
    @staticmethod
    def from_mongo_by_customer_and_product(prod_id,cus_id):
        return Database.find_one(collection='productrating',query={'product_id': prod_id,'customer_id':cus_id})

    @staticmethod
    def from_mongo_update(prod_id,cus_id,dataupdate):
        Database.update(collection='productrating',query={'product_id':prod_id,'customer_id':cus_id},data=dataupdate)
        return 

    @staticmethod
    def from_mongo_get_all():
        return Database.find(collection='productrating',query={})