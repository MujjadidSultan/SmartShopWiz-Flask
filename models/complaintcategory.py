from flask import jsonify
from models.database import Database
import uuid
from SSMSchema.ssmschema import complaintcategoryschema
class ComplaintCategory(object):
    def __init__(self,complaint_name,complaint_id=None):
        self.complaint_id = uuid.uuid4().hex if complaint_id is None else complaint_id
        self.complaint_name = complaint_name
    
    def save_to_mongo(self):
        if complaintcategoryschema.validate([self.json()]):
            Database.insert(collection='complaintcategory',data=self.json())
            result = jsonify({'complaint_id':self.complaint_id})
            return result
        else:
            return "Schema Not Matched"
    

    def json(self):
        return {'complaint_id':self.complaint_id,
            'complaint_name': self.complaint_name
        }

    @staticmethod
    def from_mongo(comp_id):
        return Database.find_one(collection='complaintcategory',query={'complaint_id':comp_id})

    @staticmethod
    def from_mongo_get_all_complaint():
        return Database.find(collection='complaintcategory',query={})
    
    @staticmethod
    def from_mongo_update(comp_id,data_update):
        Database.update(collection='complaintcategory',query={'complaint_id':comp_id},data=data_update)
        return ComplaintCategory.from_mongo(comp_id)

    @staticmethod
    def from_mongo_delete(comp_id):
        return Database.delete_one(collection='complaintcategory',query={'complanit_id':comp_id})

    @staticmethod
    def from_mongo_by_name(name):
        return Database.find_one(collection='complaintcategory',query={'complaint_name':name})