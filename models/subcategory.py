from flask import jsonify
import uuid
from models.database import Database
from SSMSchema.ssmschema import subcategoryschema

class Subcategory(object):
    def __init__(self,subcategory_name,description,category_id,subcategory_id=None):
        self.subcategory_id = uuid.uuid4().hex if subcategory_id is None else subcategory_id
        self.subcategory_name = subcategory_name
        self.description = description
        self.category_id = category_id


    def save_to_mongo(self):
        if subcategoryschema.validate([self.json()]):
            Database.insert(collection='subcategories',data=self.json())
            res = {'subcategory_name':self.subcategory_name + " added"}
            result= jsonify({'result' : res})
            return result
        else:
            return "Schema not matched!"

    def json(self):
        return {
            'subcategory_id': self.subcategory_id,
            'subcategory_name': self.subcategory_name,
            'description': self.description,
            'category_id': self.category_id
        }

    @staticmethod
    def from_mongo(cat_id):
        return Database.find_one(collection='subcategories',query={'subcategory_id':cat_id})
    
    @staticmethod
    def from_mongo_get_all_product():
        return [subcategory for subcategory in Database.find(collection='subcategories',query={})]
    
    @staticmethod
    def from_mongo_update(cat_id,data_update):
        Database.update(collection='subcategories',query={'subcategory_id':cat_id},data=data_update)
        return Subcategory.from_mongo(cat_id)
    
    @staticmethod
    def from_mongo_delete(cat_id):
        return Database.delete_one(collection='subcategories',query={'subcategory_id':cat_id})
    
    @staticmethod
    def from_mongo_by_name(name):
        return Database.find_one(collection='subcategories',query={'subcategory_name':name})

    @staticmethod
    def from_mongo_by_name_and_cat(name,cat_id):
        return Database.find_one(collection='subcategories',query={'subcategory_name':name,'category_id':cat_id})
    
    @staticmethod
    def from_mongo_by_id(subcat_id):
        return Database.find_one(collection='subcategories',query={'subcategory_id': subcat_id})
    