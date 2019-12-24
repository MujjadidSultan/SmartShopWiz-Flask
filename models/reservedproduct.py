from flask import jsonify
from models.database import Database
from SSMSchema.ssmschema import reservedproductschema
import uuid

class ReservedProduct(object):
    def __init__(self,product_id,customer_id,reserved_quantity,reserved_time,reservation_date,status,reservation_id=None):
        self.reservation_id = uuid.uuid4().hex if reservation_id is None else reservation_id 
        self.product_id = product_id
        self.customer_id = customer_id
        self.reserved_quantity = reserved_quantity       
        self.reserved_time =reserved_time
        self.reservation_date = reservation_date
        self.status = status

    def save_to_mongo(self):
        if reservedproductschema.validate([self.json()]):
            Database.insert(collection='reservedproduct',data=self.json())
            res = {'reservation_id' : self.reservation_id + ' added'}
            result= jsonify({'result' : res})
            return result
        else:
            return "Schema not matched!"
            
    def json(self):
        return {'reservation_id': self.reservation_id,
            'product_id': self.product_id,
            'customer_id': self.customer_id,
            'reserved_quantity': self.reserved_quantity,
            'reserved_time': self.reserved_time,
            'reservation_date': self.reservation_date,
            'status': self.status
        }   
    
    @staticmethod
    def from_mongo(res_id):
        return Database.find_one(collection='reservedproduct',query={'reservation_id':res_id})
    

    @staticmethod
    def from_mongo_by_customer(cus_id):
        return Database.find(collection='reservedproduct',query={'customer_id':cus_id})

    @staticmethod
    def from_mongo_get_reserved():
        return Database.find(collection='reservedproduct',query={'status':'Reserved'})

    @staticmethod
    def from_mongo_get_all_reservations():
        return Database.find(collection='reservedproduct', query={})
    
    @staticmethod
    def from_mongo_update(res_id,data_update):
        Database.update(collection='reservedproduct',query={'reservation_id':res_id},data=data_update)
        return ReservedProduct.from_mongo(res_id)

    @staticmethod
    def from_mongo_delete(res_id):
        return Database.delete_one(collection='reservedproduct',query={'reservation_id':res_id})
    
    