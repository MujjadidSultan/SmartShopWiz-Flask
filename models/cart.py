from flask import jsonify
from models.database import Database
from SSMSchema.ssmschema import cartschema
import uuid

class Cart(object):
    def __init__(self,products,total_bill,customer_id,date,status,cart_id=None):
        self.cart_id = uuid.uuid4().hex if cart_id is None else cart_id 
        self.products = products
        self.total_bill = total_bill
        self.customer_id = customer_id
        self.date = date
        self.status = status

    def save_to_mongo(self):
        if cartschema.validate([self.json()]):
            Database.insert(collection='cart',data=self.json())
            res = {'cart_id' : self.cart_id + ' added'}
            result= jsonify({'result' : res})
            return result
        else:
            return "Schema not matched!"
    def json(self):
        return {'cart_id': self.cart_id,
            'products': self.products,
            'total_bill': self.total_bill,
            'customer_id': self.customer_id,
            'date': self.date,
            'status': self.status
            }
    
    @staticmethod
    def from_mongo(cart_id):
        return Database.find_one(collection='cart',query={'cart_id':cart_id})
    
    @staticmethod
    def from_mongo_get_all_cart():
        return Database.find(collection='cart', query={})
    
    @staticmethod
    def from_mongo_all_cart_of_customer(cus_id):
        return Database.find(collection='cart',query={'customer_id':cus_id})

    @staticmethod
    def from_mongo_update(cart_id,data_update):
        Database.update(collection='cart',query={'cart_id':cart_id},data=data_update)
        return Cart.from_mongo(cart_id)
    @staticmethod
    def from_mongo_delete(cart_id):
        return Database.delete_one(collection='cart',query={'cart_id':cart_id})
    
    