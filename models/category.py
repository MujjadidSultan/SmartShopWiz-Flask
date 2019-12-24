from flask import jsonify
import uuid
from models.database import Database
from models.product import Product
from SSMSchema.ssmschema import categoryschema

class Category(object):
    def __init__(self,category_name,description,category_image,category_id=None):
        self.category_id = uuid.uuid4().hex if category_id is None else category_id
        self.category_name = category_name
        self.description = description
        self.category_image = category_image

    def save_to_mongo(self):
        if categoryschema.validate([self.json()]):
            Database.insert(collection='categories',data=self.json())
            res = {'category_name':self.category_name + " added"}
            result= jsonify({'result' : res})
            return result
        else:
            return "Schema not matched!"

    def json(self):
        return {
            'category_id': self.category_id,
            'category_name': self.category_name,
            'description': self.description,
            'category_image': self.category_image
        }

    @staticmethod
    def from_mongo(cat_id):
        return Database.find_one(collection='categories',query={'category_id':cat_id})
    
    @staticmethod
    def from_mongo_get_all_product():
        return [category for category in Database.find(collection='categories',query={})]
    
    @staticmethod
    def from_mongo_update(cat_id,data_update):
        Database.update(collection='categories',query={'category_id':cat_id},data=data_update)
        return Category.from_mongo(cat_id)
    
    @staticmethod
    def from_mongo_delete(cat_id):
        return Database.delete_one(collection='categories',query={'category_id':cat_id})
    
    @staticmethod
    def from_mongo_by_name(name):
        return Database.find_one(collection='categories',query={'category_name':name})