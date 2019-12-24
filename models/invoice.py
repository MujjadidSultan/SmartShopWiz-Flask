from flask import jsonify
from models.database import Database
from SSMSchema.ssmschema import invoiceschema
import uuid

class Invoice(object):
    def __init__(self,cart_id,bill,given_cash,returned_cash,invoice_id=None):
        self.invoice_id = uuid.uuid4().hex if invoice_id is None else invoice_id 
        self.cart_id = cart_id
        self.bill = bill
        self.given_cash = given_cash       
        self.returned_cash = returned_cash

    def save_to_mongo(self):
        if invoiceschema.validate([self.json()]):
            Database.insert(collection='invoice',data=self.json())
            res = {'invoice_id' : self.invoice_id + ' added'}
            result= jsonify({'result' : res})
            return result
        else:
            return "Schema not matched!"
    def json(self):
        return {'invoice_id': self.invoice_id,
            'cart_id': self.cart_id,
            'bill': self.bill,
            'given_cash': self.given_cash,
            'returned_cash': self.returned_cash
        }   
    
    @staticmethod
    def from_mongo(invoice_id):
        return Database.find_one(collection='invoice',query={'invoice_id':invoice_id})
    
    @staticmethod
    def from_mongo_get_all_invoices():
        return [invoice for invoice in Database.find(collection='invoice', query={})]
    
    @staticmethod
    def from_mongo_by_cart(cart_id):
        return Database.find_one(collection='invoice',query={'cart_id':cart_id})

    @staticmethod
    def from_mongo_update(invoice_id,data_update):
        Database.update(collection='invoice',query={'invoice_id':invoice_id},data=data_update)
        return Invoice.from_mongo(invoice_id)

    @staticmethod
    def from_mongo_delete(invoice_id):
        return Database.delete_one(collection='invoice',query={'invoice_id': invoice_id})
    
    