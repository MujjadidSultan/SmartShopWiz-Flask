from flask import jsonify
from SSMSchema.ssmschema import inventoryschema
from models.database import Database

class Inventory(object):
    def __init__(self,product_id,quantity):
        self.product_id = product_id
        self.quantity = quantity
    
    def save_to_mongo(self):
        if inventoryschema.validate([self.json()]):
            Database.insert(collection='inventory',data =self.json())
            result = jsonify ({'result':{'product_id':self.product_id + 'added'}})
            return result
        else:
            return "Schema not matched!"
    
    def json(self):
        return {'product_id': self.product_id,
            'quantity': self.quantity
        }

    @staticmethod
    def from_mongo(prod_id):
        return Database.find_one(collection='inventory',query= {'product_id':prod_id})
    
    @staticmethod
    def from_mongo_get_all_quantity():
        return [quantity for quantity in Database.find(collection='inventory',query={})]
    
    @staticmethod
    def from_mongo_update(product_id,data_update):
        Database.update(collection='inventory',query={'product_id':product_id},data=data_update)
        return Inventory.from_mongo(product_id)
    
    @staticmethod
    def from_mongo_delete(product_id):
        return Database.delete_one(collection='inventory',query={'product_id':product_id})
    
    