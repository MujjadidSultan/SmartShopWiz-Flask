from flask import jsonify
from flask_login import UserMixin
from models.user import User
from models.database import Database
import uuid
from SSMSchema.ssmschema import customerschema

class Customer(UserMixin, User):
    def __init__(self, fname,lname,email,password,phNo,age,gender,address,city,datetime,role,verification_code,username,customer_id=None):
        User.__init__(self, fname,lname,email,password,phNo,age,gender,address,city,datetime,role,verification_code)
        self.username = username
        self.customer_id = uuid.uuid4().hex if customer_id is None else customer_id

    def get_id(self):
        return self.getemail()

    def save_to_mongo(self):
        if customerschema.validate([self.json()]):
            Database.insert(collection='users',data=self.json())
            res = {'email' : self.email + ' registered'}
            result= jsonify({'result' : res})
            return result
        else:
            return 'Schema not matched!'

    def json(self):
        return {'first_name': self.getfirstname(),
            'last_name':self.getlastname(),
            'email':self.getemail(),
            'password':self.getpassword(),
            'phonenumber':self.getphonenumber(),
            'age':self.getage(),
            'gender':self.getgender(),
            'address':{'houseno':self.gethouseNo(),'streetno':self.getstreetNo(),'area':self.getarea(),'city':self.getcity()},
            'city':self.getcity(),
            'date':self.getdate(),
            'role':self.getrole(),
            'verification_code':self.generate_verification_code(),
            'username':self.username,
            'customer_id': self.customer_id}
            
    @staticmethod
    def from_mongo_by_email(email):
        return Database.find_one(collection='users',query={'email':email})
    
    @staticmethod
    def from_mongo_by_username(username):
        return Database.find_one(collection='users',query={'username':username})

    @staticmethod
    def from_mongo_by_id(cus_id):
        return Database.find_one(collection='users',query={'customer_id':cus_id})
    
    @staticmethod
    def from_mongo_get_all_customer():
        return Database.find(collection='users',query={'role':'customer'})

    @staticmethod
    def from_mongo_update(customer_id,data):
        Database.update(collection='users',query={'customer_id':customer_id},data=data)
        return Customer.from_mongo_by_id(customer_id)