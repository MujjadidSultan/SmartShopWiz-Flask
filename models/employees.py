from flask import jsonify
from flask_login import UserMixin
from models.user import User
from models.database import Database
from SSMSchema.ssmschema import employeeschema
class Employee(UserMixin,User):
    
    def __init__(self, fname,lname,email,password,phNo,age,gender,address,city,datetime,role,verification_code,employeeID,cnic,hiring_date,status):
        User.__init__(self, fname,lname,email,password,phNo,age,gender,address,city,datetime,role,verification_code)
        self.employeeID = employeeID
        self.cnic = cnic
        self.hiring_date=hiring_date
        self.status= status

    def get_id(self):
        return self.getemail()

    def save_to_mongo(self):
        if employeeschema.validate([self.json()]):
            Database.insert(collection='users',data=self.json())
            res = {'email' : self.email + ' registered'}
            result= jsonify({'result' : res})
            return result
        else:
            return "Schema not matched!"
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
            'employeeID':self.employeeID,
            'cnic':self.cnic,
            'hiring_date':self.hiring_date,
            'status':self.status}
    @staticmethod
    def from_mongo(email):
        return Database.find_one(collection='users',query={'email':email})
    
    @staticmethod
    def from_mongo_get_all_employee():
        return Database.find(collection='users', query={'role':'employee','status':'active'})

    @staticmethod
    def from_mongo_by_employeeID(emp_id):
        return Database.find_one(collection='users',query={'employeeID':emp_id})
    
    @staticmethod
    def from_mongo_update(email,data_update):
        Database.update(collection='users',query={'email':email},data=data_update)
        return Employee.from_mongo(email)
    