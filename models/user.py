from models.address import Address
import random
class User:
    def __init__(self, fname,lname,email,password,phNo,age,gender,address,city,datetime,role,verification_code):
        self.first_name = fname
        self.last_name = lname
        self.email = email
        self.password = password
        self.phonenumber = phNo
        self.age = age
        self.gender = gender
        self.address = Address(address.houseNo,address.streetNo,address.area,address.city)
        self.city = city
        self.datetime = datetime
        self.role = role
        self.verification_code = verification_code
    def getfirstname(self):
        return self.first_name
    def getlastname(self):
        return self.last_name
    def getemail(self):
        return self.email
    def getpassword(self):
        return self.password
    def getphonenumber(self):
        return self.phonenumber
    def getage(self):
        return self.age
    def getgender(self):
        return self.gender
    def getcity(self):
        return self.city
    def getdate(self):
        return self.datetime
    def getrole(self):
        return self.role
    def gethouseNo(self):
        return self.address.houseNo
    def getstreetNo(self):
        return self.address.streetNo
    def getarea(self):
        return self.address.area
    def generate_verification_code(self):
        value = random.randint(1111, 9999)
        self.verification_code = value
        return self.verification_code