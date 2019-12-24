from flask import jsonify
import uuid
from models.database import Database
from SSMSchema.ssmschema  import supplierschema

class Supplier(object):
    def __init__(self,supplier_name,supplier_quantity,supplying_date,product_id,supplier_id=None):
        self.supplier_id = uuid.uuid4().hex if supplier_id is None else supplier_id
        self.supplier_name =supplier_name
        self.supplier_quantity =supplier_quantity
        self.supplying_date = supplying_date
        self.product_id = product_id

    def save_to_mongo(self):
        if supplierschema.validate([self.json()]):
            Database.insert(collection='supplier',data =self.json())
            result = jsonify ({'result':{'supplier_name':self.supplier_name + 'added'}})
            return result
        else:
            return "Schema not matched!"
    
    def json(self):
        return {'supplier_id': self.supplier_id,
            'supplier_name': self.supplier_name,
            'supplier_quantity': self.supplier_quantity,
            'supplying_date': self.supplying_date,
            'product_id': self.product_id
        }

    @staticmethod
    def from_mongo(supplier_id):
        return Database.find_one(collection='supplier',query= {'supplier_id':supplier_id})

    @staticmethod
    def from_mongo_get_all_supplier():
        return [supplier for supplier in Database.find(collection='supplier',query={})]

    @staticmethod
    def from_mongo_update(supplier_id,date_update):
        Database.update(collection='supplier',query={'supplier_id':supplier_id},data = date_update)
        return Supplier.from_mongo(supplier_id)

    @staticmethod
    def from_mongo_delete(supplier_id):
        return Database.delete_one(collection='supplier',query={'supplier_id':supplier_id})
        
    @staticmethod
    def from_mongo_by_name(name):
        return Database.find_one(collection='supplier',query={'supplier_name':name})