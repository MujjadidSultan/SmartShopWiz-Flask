from flask import jsonify
from SSMSchema.ssmschema import product_idsschema
from models.database import Database
class Product_ids(object):
    def __init__(self,product_id,number):
        self.product_id=product_id
        self.number=number

    def save_to_mongo(self):
        if product_idsschema.validate([self.json()]):
            Database.insert(collection='product_ids',data=self.json())
            result = jsonify({'result': self.product_id+'number added.'})
            return result
        else:
            return 'Schema Not Matched'

    
    def json(self):
        return {'product_id': self.product_id,
            'number': self.number
        }

    @staticmethod
    def from_mongo(prod_id):
        return Database.find_one(collection='product_ids',query={'product_id': prod_id})

    @staticmethod
    def from_mongo_by_number(number):
        return Database.find_one(collection='product_ids',query={'number': number})

    @staticmethod
    def from_mongo_update(prod_id,dataupdate):
        Database.update(collection='product_ids',query={'product_id':prod_id},data=dataupdate)
        return 

    @staticmethod
    def from_mongo_get_all():
        return Database.find(collection='product_ids',query={})