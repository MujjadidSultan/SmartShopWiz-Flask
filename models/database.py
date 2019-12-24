#from flask_pymongo  import PyMongo
import pymongo
class Database(object):
    URI= "mongodb://localhost:27017"
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['smartshopwizdb']
    @staticmethod
    def insert(collection,data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)
    
    @staticmethod
    def update(collection,query,data):
        return Database.DATABASE[collection].update_one(query,data)
    
    @staticmethod
    def update_admin(collection,query,data):
        Database.DATABASE[collection].update_one(query,data)
        return Database.find_one(collection,query)

    @staticmethod
    def delete_one(collection,query):
        return Database.DATABASE[collection].delete_one(query)

    @staticmethod
    def delete_many(collection,query):
        return Database.DATABASE[collection].delete_many(query)

    @staticmethod
    def save_image(imagename,image):
        return Database.save_file(imagename,image)