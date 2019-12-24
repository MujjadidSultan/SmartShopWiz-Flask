from flask import jsonify
from models.database import Database
from SSMSchema.ssmschema import productschema
import uuid

class Product(object):
    def __init__(self,product_name,product_image,price,description,status,expiring_date,manufacture_date,category_id,subcategory_id,rating,product_id=None):
        self.product_id = uuid.uuid4().hex if product_id is None else product_id 
        self.product_name = product_name
        self.product_image = product_image
        self.price = price
        self.description = description
        self.status = status
        self.expiring_date = expiring_date
        self.manufacture_date = manufacture_date
        self.category_id = category_id
        self.subcategory_id = subcategory_id
        self.rating = rating

    def save_to_mongo(self):
        if productschema.validate([self.json()]):
            Database.insert(collection='products',data=self.json())
            res = {'product_name' : self.product_name + ' added'}
            result= jsonify({'result' : res})
            return result
        else:
            return "Schema not matched!"
    def json(self):
        return {'product_id': self.product_id,
            'product_name':self.product_name,
            'product_image':self.product_image,
            'price':self.price,
            'description':self.description,
            'status':self.status,
            'expiring_date':self.expiring_date,
            'manufacture_date':self.manufacture_date,
            'category_id':self.category_id,
            'subcategory_id': self.subcategory_id,
            'rating':self.rating
            }
    
    @staticmethod
    def from_mongo(product_id):
        return Database.find_one(collection='products',query={'product_id':product_id})
    
    @staticmethod
    def from_mongo_get_all_product():
        return [product for product in Database.find(collection='products',query={})]
    
    @staticmethod
    def from_mongo_get_all_product_for_customer():
        return [product for product in Database.find(collection='products',query={'status':'Available'})]

    @staticmethod
    def from_mongo_update(product_id,data_update):
        Database.update(collection='products',query={'product_id':product_id},data=data_update)
        return Product.from_mongo(product_id)
    
    @staticmethod
    def from_category(cat_id):
        return [product for product in Database.find(collection='products',query={'category_id':cat_id})]
    
    @staticmethod
    def from_mongo_delete(product_id):
        return Database.delete_one(collection='products',query={'product_id':product_id})
    
    @staticmethod
    def from_mongo_by_name(name):
        return Database.find_one(collection='products',query={'product_name':name})