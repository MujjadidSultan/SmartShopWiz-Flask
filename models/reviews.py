from flask import jsonify
from models.database import Database
from SSMSchema.ssmschema import reviewsschema
import uuid

class Reviews(object):
    def __init__(self,customer_id,cart_id,review,review_datetime,review_id=None):
        self.review_id = uuid.uuid4().hex if review_id is None else review_id
        self.customer_id = customer_id 
        self.cart_id = cart_id
        self.review = review
        self.review_datetime = review_datetime

    def save_to_mongo(self):
        if reviewsschema.validate([self.json()]):
            Database.insert(collection='reviews',data=self.json())
            res = {'customer_id' : self.customer_id + ' added'}
            result= jsonify({'result' : res})
            return result
        else:
            return "Schema not matched!"
    def json(self):
        return {'review_id': self.review_id,
            'customer_id': self.customer_id,
            'cart_id': self.cart_id,
            'review': self.review,
            'review_datetime': self.review_datetime
        }   
    
    @staticmethod
    def from_mongo(cus_id):
        return Database.find_one(collection='reviews',query={'customer_id':cus_id})
    
    @staticmethod
    def from_mongo_get_all_reviews():
        return [reviews for reviews in Database.find(collection='reviews', query={})]
    
    @staticmethod
    def from_mongo_update(review_id,data_update):
        Database.update(collection='reviews',query={'review_id':review_id},data=data_update)
        return Reviews.from_mongo(review_id)
    
    @staticmethod
    def from_mongo_customer_and_cart(cus_id,cart_id):
        return Database.find_one(collection='reviews',query={'customer_id':cus_id,'cart_id':cart_id})

    @staticmethod
    def from_mongo_cart(cart_id):
        return Database.find_one(collection='reviews',query={'cart_id':cart_id})

    @staticmethod
    def from_mongo_delete(review_id):
        return Database.delete_one(collection='reviews',query={'review_id':review_id})