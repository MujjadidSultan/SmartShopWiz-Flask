import os
from flask import Flask, jsonify, request, json,session,send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail, Message
from flask_login import LoginManager,login_user,login_required, current_user, logout_user
from models.database import Database
from bson.objectid import ObjectId
from datetime import datetime , timedelta
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_pymongo  import PyMongo
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
import smtplib
import random
import json
import qrcode
from werkzeug.utils import secure_filename
from models.address import Address
from models.customer import Customer
from models.employees import Employee
from models.product import Product
from models.category import Category
from models.subcategory import Subcategory
from models.inventory import Inventory
from models.supplier import Supplier
from models.cart import Cart
from models.reservedproduct import ReservedProduct
from models.invoice import Invoice
from models.reviews import Reviews
from models.notification import Notification
from models.tickets import Tickets
from models.tickets_response import TicketsResponse
from models.tickets_feedback import TicketsFeedback
from models.productrating import Productrating
from models.role import Role
from models.complaintcategory import ComplaintCategory
from models.customersearches import CustomerSearches
from models.userguidance import UserGuidance
from models.devicetoken import DeviceToken
from models.customer_ids import Customer_ids
from models.product_ids import Product_ids
from bson import ObjectId
import sys
from bson import json_util
import uuid
import requests
from pandas import DataFrame
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn import metrics
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_score

#Expo push notifications
API_URL = "https://exp.host/--/api/v2/push/send"

def scheduler():
    #print('running'+str(datetime.now()))
    reservedproduct = list(ReservedProduct.from_mongo_get_reserved())
    print(reservedproduct)
    if reservedproduct is None:
        pass
    else:
        for x in reservedproduct:
            now_time = datetime.now()
            print(str(now_time))
            reservation_time = x['reservation_date'] + timedelta(minutes=x['reserved_time'])
            print(str(reservation_time))
            if now_time < reservation_time:
                pass
            elif now_time > reservation_time:
                reservation = ReservedProduct.from_mongo(x['reservation_id'])
                quantity = Inventory.from_mongo(x['product_id'])
                new_quantity = int(quantity['quantity'])+int(x['reserved_quantity'])
                update = { '$set': {'quantity': new_quantity}}
                Inventory.from_mongo_update(x['product_id'],update)
                update = { '$set': {'status': 'Cancelled'}}
                ReservedProduct.from_mongo_update(x['reservation_id'],update)
                device_id = DeviceToken.from_mongo_by_user_id(x['customer_id'])
                product_res = Product.from_mongo(x['product_id'])
                data = {
                    "to": device_id['device_id'],
                    "title":"Reservation Cancelled",
                    "body": product_res['product_name']+" reservation has been cancelled/expired."
                    }
                response = requests.post(API_URL, data)



sched = BackgroundScheduler(daemon=True)
sched.add_job(scheduler,'interval',minutes=15)
sched.start()

app = Flask(__name__)


#Sending Mail Configurations
Database.initialize()
UPLOAD_FOLDER = '.\product_pictures'
UPLOAD_QRCODE_FOLDER = '.\qrcode'
UPLOAD_CATEGORY_FOLDER = '.\category_pictures'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT= 587,
    MAIL_USE_TLS= True,
    MAIL_USERNAME = 'email@gmail.com',
    MAIL_PASSWORD = 'password'
)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/smartshopwizdb'
app.config['SECRET_KEY'] = 'MySecretKey!'
app.config['JWT_SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_QRCODE_FOLDER'] = UPLOAD_QRCODE_FOLDER
app.config['UPLOAD_CATEGORY_FOLDER'] = UPLOAD_CATEGORY_FOLDER

mongo = PyMongo(app)
mail = Mail(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
login_manager = LoginManager(app)


CORS(app)


@login_manager.user_loader
def load_user(email):
    user = Database.find_one(collection='users',query={'email':email})
    if user:
        if user['role']=='employee' or user['role']=='admin':
            address = Address(user['address']['houseno'],
                user['address']['streetno'],
                user['address']['area'],
                user['address']['city'])
            emp = Employee(user['first_name'],
                user['last_name'],
                user['email'],
                user['password'],
                user['phonenumber'],
                user['age'],
                user['gender'],
                address,
                user['city'],
                user['date'],
                user['role'],
                user['verification_code'],
                user['employeeID'],
                user['cnic'],
                user['hiring_date'],
                user['status'])
            return emp
        elif user['role']=='customer':
            address = Address(user['address']['houseno'],
                user['address']['streetno'],
                user['address']['area'],
                user['address']['city'])
            cust = Customer(user['first_name'],
                user['last_name'],
                user['email'],
                user['password'],
                user['phonenumber'],
                user['age'],
                user['gender'],
                address,
                user['city'],
                user['date'],
                user['role'],
                user['verification_code'],
                user['username'],
                user['customer_id'])
            return cust
    return None



@app.route('/home')
def home():
    return "Wellcome to Flask server"


#File type verification
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


##########################################################################
#Users API's
##########################################################################


#Add Employee API
@app.route('/users/addemployee', methods=['POST'])
@login_required
def addemployee():
    response = Employee.from_mongo(request.get_json()['email'])
    if response is None:
        address = Address(request.get_json()['houseno'],
           request.get_json()['streetno'],
            request.get_json()['area'],
           request.get_json()['city'])
        employee = Employee(request.get_json()['first_name'],
            request.get_json()['last_name'],
           request.get_json()['email'],
            bcrypt.generate_password_hash(request.get_json()['password']).decode('utf-8'),
           request.get_json()['phonenumber'],
            request.get_json()['age'],
            request.get_json()['gender'],
            address,
            request.get_json()['city'],
            datetime.now(),
            request.get_json()['role'],
            None,
            request.get_json()['employeeID'],
           request.get_json()['cnic'],
           datetime.now(),
            request.get_json()['status'])

        result = employee.save_to_mongo()
        return result
    else:
        return 'Already Registed!'


#SignUp Customer API
@app.route('/users/signup_customer', methods=['POST'])
def signup_customer():
    response = Customer.from_mongo_by_email(request.get_json()['email'])
    response2 = Customer.from_mongo_by_username(request.get_json()['username'])
    if ((response is None and response2 is None)):
        address = Address(request.get_json()['houseno'],
            request.get_json()['streetno'],
            request.get_json()['area'],
            request.get_json()['city'])
        customer = Customer(request.get_json()['first_name'],
            request.get_json()['last_name'],
            request.get_json()['email'],
            bcrypt.generate_password_hash(request.get_json()['password']).decode('utf-8'),
            request.get_json()['phonenumber'],
            request.get_json()['age'],
            request.get_json()['gender'],
            address,
            request.get_json()['city'],
            datetime.now(),
            request.get_json()['role'],
            None,
            request.get_json()['username'])

        result = customer.save_to_mongo()
        return result
    elif (response is not None and response2 is not None):
        return 'Email And Username'
    elif (response is not None):
        return 'Customer Already Registered!'
    elif (response2 is not None):
        return 'Username Already Taken!'   
	

#Login API
@app.route('/users/login', methods=['POST'])
def login():
    email = request.get_json()['email']
    username = request.get_json()['email']
    employeeID = request.get_json()['email']
    password = request.get_json()['password']
    result = ""	
    response = Database.find_one(collection='users',query={'email':email})
    if response is None:
        response = Database.find_one(collection='users',query={'username':username})
    elif response is None :
        response = Database.find_one(collection='users',query={'employeeID':employeeID})

    if response:	
        if bcrypt.check_password_hash(response['password'], password):
            if response['role'] == 'employee':
                if response['status']=='inactive':
                    return "Employee Not Allowed"
                elif response['status']=='active':
                    access_token = create_access_token(identity = {
                        'first_name': response['first_name'],
                        'last_name': response['last_name'],
                        'email': response['email'],
                        'phonenumber':response['phonenumber'],
                        'age':response['age'],
                        'gender':response['gender'],
                        'address':response['address'],
                        'city':response['city'],
                        'employeeID': response['employeeID'],
                        'cnic': response['cnic'],
                        'hiring_date': response['hiring_date'],
                        'status': response['status']}
                    )
                    emp = Employee.from_mongo(response['email'])
                    address = Address(emp['address']['houseno'],
                        emp['address']['streetno'],
                        emp['address']['area'],
                        emp['address']['city'])
                    empl = Employee(emp['first_name'],
                        emp['last_name'],
                        emp['email'],
                        emp['password'],
                        emp['phonenumber'],
                        emp['age'],
                        emp['gender'],
                        address,
                        emp['city'],
                        emp['date'],
                        emp['role'],
                        emp['verification_code'],
                        emp['employeeID'],
                        emp['cnic'],
                        emp['hiring_date'],
                        emp['status'])
                    login_user(empl)
                    devicetoken = DeviceToken(emp['employeeID'],
                        request.get_json()['device_id'],
                        datetime.now()
                        )
                    device_res = DeviceToken.from_mongo_by_user_id_and_token_id(current_user.employeeID,devicetoken.device_id)
                    if device_res is None:
                        print([device_res])
                        devicetoken.save_to_mongo()
                    else:
                        print('already exist')
                    result = access_token
            elif response['role'] == 'customer' :
                access_token = create_access_token(identity = {
                    'first_name': response['first_name'],
                    'last_name': response['last_name'],
                    'email': response['email'],
                    'phonenumber':response['phonenumber'],
                    'age':response['age'],
                    'gender':response['gender'],
                    'address':response['address'],
                    'city':response['city'],
                    'username': response['username'],
                    'customer_id': response['customer_id']}
                    )
                cus = Customer.from_mongo_by_email(response['email'])
                address = Address(cus['address']['houseno'],
                    cus['address']['streetno'],
                    cus['address']['area'],
                    cus['address']['city'])
                cust = Customer(cus['first_name'],
                    cus['last_name'],
                    cus['email'],
                    cus['password'],
                    cus['phonenumber'],
                    cus['age'],
                    cus['gender'],
                    address,
                    cus['city'],
                    cus['date'],
                    cus['role'],
                    cus['verification_code'],
                    cus['username'],
                    cus['customer_id'])
                login_user(cust)
                #print('1 '+request.get_json()['device_id'])
                devicetoken = DeviceToken(cus['customer_id'],
                    request.get_json()['device_id'],
                    datetime.now()
                    )
                #print(current_user.customer_id)
                #print(devicetoken.device_id)
                device_res = DeviceToken.from_mongo_by_user_id_and_token_id(devicetoken.user_id,devicetoken.device_id)
                if device_res is None:
                    print([device_res])
                    devicetoken.save_to_mongo()
                else:
                    print('already exist')
                result = access_token
            elif response['role'] == 'admin':
                access_token = create_access_token(identity = {
                    'first_name': response['first_name'],
                    'last_name': response['last_name'],
                    'email': response['email'],
                    'phonenumber':response['phonenumber'],
                    'age':response['age'],
                    'gender':response['gender'],
                    'address':response['address'],
                    'city':response['city'],
                    'employeeID': response['employeeID'],
                    'cnic': response['cnic'],
                    'hiring_date': response['hiring_date'],
                    'status': response['status']}
                   )
                emp = Employee.from_mongo(response['email'])
                address = Address(emp['address']['houseno'],
                    emp['address']['streetno'],
                    emp['address']['area'],
                    emp['address']['city'])
                empl = Employee(emp['first_name'],
                    emp['last_name'],
                    emp['email'],
                    emp['password'],
                    emp['phonenumber'],
                    emp['age'],
                    emp['gender'],
                    address,
                    emp['city'],
                    emp['date'],
                    emp['role'],
                    emp['verification_code'],
                    emp['employeeID'],
                    emp['cnic'],
                    emp['hiring_date'],
                    emp['status'])
                login_user(empl)
                result = access_token
        else:
            result = 'Invalid username and password'            
    else:
        result = 'No results found'
    #device_id = DeviceToken.from_mongo_by_user_id(current_user.customer_id) 
    #data = {
    #    'to': device_id['device_id'],
    #    'title': 'Logged in!',
    #    'body': current_user.first_name + ' ' +current_user.last_name + 'kkkk'}
    #response = requests.post(API_URL, data)
    return result
	

#Update API
@app.route('/users/update', methods=['POST'])
@login_required
def update():
    result = ''
    if current_user.role == 'employee':
        update = {"$set": { 'first_name': request.get_json()['first_name'],
            'last_name':request.get_json()['last_name'],
            'phonenumber':request.get_json()['phonenumber'],
            'age':request.get_json()['age'],
            'gender':request.get_json()['gender'],
            'address': {
                'houseno': request.get_json()['houseno'],
                'streetno':request.get_json()['streetno'],
                'area': request.get_json()['area'],
                'city': request.get_json()['city']
            },
            'city':request.get_json()['city'],
            'cnic':request.get_json()['cnic']}}
        response = Employee.from_mongo_update(current_user.email,update)
        access_token = create_access_token(identity = {
                    'first_name': response['first_name'],
                    'last_name': response['last_name'],
                    'email': response['email'],
                    'phonenumber':response['phonenumber'],
                    'age':response['age'],
                    'gender':response['gender'],
                    'address':response['address'],
                    'city':response['city'],
                    'employeeID': response['employeeID'],
                    'cnic': response['cnic'],
                    'hiring_date': response['hiring_date'],
                    'status': response['status']}
                   )
        result = access_token
    elif current_user.role == 'customer':
        update = {"$set": { 'first_name': request.get_json()['first_name'],
            'last_name':request.get_json()['last_name'],
            'phonenumber':request.get_json()['phonenumber'],
            'age':request.get_json()['age'],
            'gender':request.get_json()['gender'],
            'address': {
                'houseno': request.get_json()['houseno'],
                'streetno':request.get_json()['streetno'],
                'area': request.get_json()['area'],
                'city': request.get_json()['city']
            },
            'city':request.get_json()['city']}}
        response = Customer.from_mongo_update(current_user.customer_id,update)
        access_token = create_access_token(identity = {
                    'first_name': response['first_name'],
                    'last_name': response['last_name'],
                    'email': response['email'],
                    'phonenumber':response['phonenumber'],
                    'age':response['age'],
                    'gender':response['gender'],
                    'address':response['address'],
                    'city':response['city'],
                    'username': response['username']}
                    )
        result = access_token
    elif current_user.role == 'admin':
        update = {"$set": { 'first_name': request.get_json()['first_name'],
            'last_name':request.get_json()['last_name'],
            'phonenumber':request.get_json()['phonenumber'],
            'age':request.get_json()['age'],
            'gender':request.get_json()['gender'],
            'address': {
                'houseno': request.get_json()['houseno'],
                'streetno':request.get_json()['streetno'],
                'area': request.get_json()['area'],
                'city': request.get_json()['city']
            },
            'city':request.get_json()['city'],
            'cnic':request.get_json()['cnic']}}
        query = {'email':current_user.email,'role':'admin'}
        response = Database.update_admin(collection='users',query=query,data=update)
        access_token = create_access_token(identity = {
                    'first_name': response['first_name'],
                    'last_name': response['last_name'],
                    'email': response['email'],
                    'phonenumber':response['phonenumber'],
                    'age':response['age'],
                    'gender':response['gender'],
                    'address':response['address'],
                    'city':response['city'],
                    'employeeID': response['employeeID'],
                    'cnic': response['cnic'],
                    'hiring_date': response['hiring_date'],
                    'status': response['status']}
                   )
        result = access_token
    return result


#View Employee API
@app.route('/users/viewemployeelist', methods=['GET'])
@login_required
def viewemployeelist():
    docs_list  = list(Employee.from_mongo_get_all_employee())
    return json.dumps(docs_list, default=json_util.default)


#View Customer API
@app.route('/users/viewcustomerlist', methods=['GET'])
@login_required
def viewuserlist():
    docs_list  = list(Customer.from_mongo_get_all_customer())
    return json.dumps(docs_list, default=json_util.default)


#Change Password API
@app.route('/users/changepassword', methods=['POST'])
@login_required
def changepassword():
    email = request.get_json()['email']
    password = request.get_json()['password']
    newpassword = bcrypt.generate_password_hash(request.get_json()['newpassword']).decode('utf-8')
    result = ""
    response= Database.find_one(collection='users',query={'email':email})
    if bcrypt.check_password_hash(response['password'], password):
        update = {"$set":{'password':newpassword}}
        Database.update(collection='users',query={'email':email},data=update)
        result = jsonify({'result':"Password Changed"})
    else:
        result = jsonify({'result':"Password Not Changed"})
    return result


#Send Mail API
@app.route('/users/sendemail', methods=['POST'])
def sendemail():
    try:
        users = mongo.db.users
        email = request.get_json()['email']
        response = Database.find_one(collection='users',query={'email' : email})
        if response is None: 
            return ("User not found : " + email + str(response))
        else:
            value = random.randint(1111, 9999)
            msg = "Your verification code is : " + str(value)
            mail.send_message('Code Verification!',sender='smartshopwiz@gmail.com',recipients=[email],body=msg)
            update = {"$set":{'verification_code':value}}
            Database.update(collection='users',query={'email' : email},data=update)
            return ("Email sent successfully")
    except:
        return ("Email failed to send")


#Verify Code API
@app.route('/users/verifyCode', methods=['POST'])
def verifyCode():
    try:
        users = mongo.db.users
        email = request.get_json()['email']
        verifycode= int(request.get_json()['verifycode'])
        response = Database.find_one(collection='users',query={'email' : email})
        result = ''
        value =  random.randint(1111, 9999)
        if response['verification_code']==verifycode :
                update = {"$set":{'verification_code':value}}
                Database.update(collection='users',query={'email' : email},data=update)
                result= "Correct code"
        else : 
                result= "Incorrect code : "+ verifycode
        return result
    except:
        return ("Verification Failed")
 

#Update Password API
@app.route('/users/updatepassword', methods=['POST'])
def updatepassword():
    email = request.get_json()['email']
    newpassword = bcrypt.generate_password_hash(request.get_json()['newpassword']).decode('utf-8')
    result = ""
    response = Database.find_one(collection='users',query={'email' : email})
    update = {"$set":{'password':newpassword}}
    Database.update(collection='users',query={'email' : email},data=update)
    result = jsonify({"result":"Password Updated"})
    return result


#Get one Employee API
@app.route('/users/getemployee/<employee_id>', methods=['GET'])
@login_required
def getemployeebyemail(employee_id):
    docs_list  = Employee.from_mongo(employee_id)
    return json.dumps(docs_list, default=json_util.default) 


#Update Employee API
@app.route('/users/updateemployee', methods=['POST'])
@login_required
def updateemployee():
    result = ''
    response = Employee.from_mongo(request.get_json()['email'])
    if response is None:
        return ("User not Found" + request.get_json()['email']) 
    else :    
        update = {"$set": { 'first_name': request.get_json()['first_name'],
            'last_name':request.get_json()['last_name'],
            'phonenumber':request.get_json()['phonenumber'],
            'age':request.get_json()['age'],
            'gender':request.get_json()['gender'],
            'address': {
                'houseno': request.get_json()['houseno'],
                'streetno':request.get_json()['streetno'],
                'area': request.get_json()['area'],
                'city': request.get_json()['city']
            },
            'city':request.get_json()['city'],
            'cnic':request.get_json()['cnic']}}
        response = Employee.from_mongo_update(request.get_json()['email'],update)
        result = jsonify({'result':"Updated Successfully"})
        return result


#Delete Employee API
@app.route('/users/deleteemployee', methods=['POST'])
@login_required
def deleteemployee():
    email = request.get_json()['email']
    status = request.get_json()['status']
    result = ''
    response = Employee.from_mongo(email)
    if response is None:
        return ("User not Found" + email)
    else :
        update = {"$set":{'status':status}}    
        Employee.from_mongo_update(email,update)
        result = jsonify({'result':"Deleted Successfully"})
        return result


#Log out user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return "Logged Out"


##########################################################################
#Products API's
##########################################################################


#Add Product
@app.route('/products/addproduct', methods=['POST'])
@login_required
def addproduct():
    response = Product.from_mongo_by_name(str(request.form['product_name']))
    if response is None:
        product_image = request.files['product_image']
        if product_image is None:
            return 'No Picture'
        else:
            subcategory_id = ''
            if request.form['subcategory_id'] == '':
                subcategory_id='None'
            else:
                subcategory_id = request.form['subcategory_id']
            product = Product(str(request.form['product_name']),
                str('k'),
                int(request.form['price']),
                str(request.form['description']),
                str(request.form['status']),
                datetime.now(),
                datetime.now(),
                str(request.form['category_id']),
                str(subcategory_id),
                0)
            result = product.save_to_mongo()
            inventory = Inventory(product.product_id,
                request.form['quantity'])
            inventory.save_to_mongo()
            qr = qrcode.make(product.product_id)
            qr_name = secure_filename(product.product_id+"_qrcode.png")
            qr.save(os.path.join(app.config['UPLOAD_QRCODE_FOLDER'],qr_name))
            #qr.save(f'qrcode/{product.product_id}_qrcode.png')
            product_image.filename =  product.product_id+".jpg"
            if allowed_file(product_image.filename):
                product_image.save(os.path.join(app.config['UPLOAD_FOLDER'],product_image.filename))
                update = { '$set': {'product_image': product_image.filename}}
                Product.from_mongo_update(product.product_id,update)
                return result
            else:
                return "Image not allowed."
    else:
        return 'Already Exists!'


#Update Product Quantity
@app.route('/products/updatequantity', methods = ['POST'])
@login_required
def updatequantity():
    update = { '$set': {'quantity': request.get_json()['quantity']}}
    Inventory.from_mongo_update(request.get_json()['product_id'],update)
    return "Quantity Updated Successfully!"


#Update Product
@app.route('/products/updateproduct',methods=['POST'])
@login_required
def updateproduct():
    update = {"$set":{'product_name': request.get_json()['product_name'],
        'price': request.get_json()['price'],
        'description': request.get_json()['description'],
        'status': request.get_json()['status'],
        'expiring_date': request.get_json()['expiring_date'],
        'manufacture_date': request.get_json()['manufacture_date'],
        'category_id': request.get_json()['category_id'],
        'subcategory_id': request.get_json()['subcategory_id']
    }}
    Product.from_mongo_update(request.get_json()['product_id'],update)
    result = jsonify({"result":"Product Updated"})
    return result


#Change status Product
@app.route('/products/updatestatusproduct',methods=['POST'])
@login_required
def updatestatusproduct():
    update = {"$set":{'status': request.get_json()['status']
    }}
    Product.from_mongo_update(request.get_json()['product_id'],update)
    result = jsonify({"result":"Product Status Updated"})
    return result


#Delete Product
@app.route('/products/deleteproduct',methods=['POST'])
@login_required
def deleteproduct():
    Product.from_mongo_delete(request.get_json()['product_id'])
    result =  'Product deleted!'
    return result


#Get One Product
@app.route('/products/getproduct/<product_id>', methods=['GET'])
@login_required
def getproduct(product_id):
    product = Product.from_mongo(product_id)
    product_send = []
    if product is None:
        return "No Product Found"
    else:
        inventory = Inventory.from_mongo(product_id)
        quantity =''
        if inventory is None:
            quantity = ''
        else:
            quantity = inventory['quantity']
        category = Category.from_mongo(product['category_id'])
        categoryname =''
        if category is None:
            categoryname = ''
        else:
            categoryname = category['category_name']
        subcategory = Subcategory.from_mongo(product['subcategory_id'])
        subcategoryname =''
        if subcategory is None:
            subcategoryname = ''
        else:
            subcategoryname = subcategory['subcategory_name']
        new_product = {'product_id': product['product_id'],
            'product_name': product['product_name'],
            'product_image': product['product_image'],
            'price': product['price'],
            'description':product['description'],
            'status': product['status'],
            'expiring_date': product['expiring_date'],
            'manufacture_date':product['manufacture_date'],
            'category_id': product['category_id'],
            'category_name': categoryname,
            'subcategory_id': product['subcategory_id'],
            'subcategory_name': subcategoryname,
            'quantity': quantity, 
            'rating': product['rating']
        }
        product_send.append(new_product)
    return json.dumps(product_send,default=json_util.default)


#Get All Product
@app.route('/products/getallproduct',methods=['GET'])
@login_required
def getallproduct():
    products = Product.from_mongo_get_all_product()
    products_send = []
    for x in products:
        inventory = Inventory.from_mongo(x['product_id'])
        quantity =''
        if inventory is None:
            quantity = ''
        else:
            quantity = inventory['quantity']
        category = Category.from_mongo(x['category_id'])
        categoryname =''
        if category is None:
            categoryname = ''
        else:
            categoryname = category['category_name']
        subcategory = Subcategory.from_mongo(x['subcategory_id'])
        subcategoryname =''
        if subcategory is None:
            subcategoryname = ''
        else:
            subcategoryname = subcategory['subcategory_name']
        new_product = {'product_id': x['product_id'],
            'product_name': x['product_name'],
            'product_image': x['product_image'],
            'price': x['price'],
            'description':x['description'],
            'status': x['status'],
            'expiring_date': x['expiring_date'],
            'manufacture_date':x['manufacture_date'],
            'category_id': x['category_id'],
            'category_name': categoryname,
            'subcategory_id': x['subcategory_id'],
            'subcategory_name': subcategoryname,
            'quantity': quantity, 
            'rating': x['rating']
        }
        products_send.append(new_product)
    return json.dumps(products_send,default=json_util.default)


#Get All Product for customer
@app.route('/products/getallproductforcustomer',methods=['GET'])
def getallproductforcustomer():
    products = Product.from_mongo_get_all_product_for_customer()
    products_send = []
    for x in products:
        category = Category.from_mongo(x['category_id'])
        subcategory = Subcategory.from_mongo(x['subcategory_id'])
        quantity = Inventory.from_mongo(x['product_id'])
        product_detail = {'product_id': x['product_id'],
            'product_name':x['product_name'],
            'product_image':x['product_image'],
            'price':x['price'],
            'description':x['description'],
            'status':x['status'],
            'expiring_date':x['expiring_date'],
            'manufacture_date':x['manufacture_date'],
            'category_id':x['category_id'],
            'category_name':category['category_name'],
            'subcategory_id':x['subcategory_id'],
            'subcategory_name':subcategory['subcategory_name'],
            'rating':x['rating'],
            'product_quantity':quantity['quantity']
        }
        products_send.append(product_detail)
    return json.dumps(products_send,default=json_util.default)


#Get All Recommended Product for customer
@app.route('/products/getallrecommendedproductforcustomer',methods=['GET'])
def getallrecommendedproductforcustomer():
    sns.set()
    df= None
    df = sales()

    df['Customer_Gender'] = df['Customer_Gender'].map({'Male': 1, 'Female': 2})

    df.loc[ df['Customer_Age'] <= 16, 'ageCat'] = 1
    df.loc[(df['Customer_Age'] > 16) & (df['Customer_Age'] <= 32), 'ageCat'] = 2
    df.loc[(df['Customer_Age'] > 32) & (df['Customer_Age'] <= 48), 'ageCat'] = 3
    df.loc[(df['Customer_Age'] > 48) & (df['Customer_Age'] <= 64), 'ageCat'] = 4
    df.loc[ df['Customer_Age'] > 64, 'ageCat']= 5

    df.loc[(df['Product_Price'] > 0) & (df['Product_Price'] < 500), 'Product_PriceCat'] = 1
    df.loc[(df['Product_Price'] >= 500) & (df['Product_Price'] < 1100), 'Product_PriceCat'] = 2
    df.loc[(df['Product_Price'] >= 1100) & (df['Product_Price'] < 2100), 'Product_PriceCat'] = 3
    df.loc[(df['Product_Price'] >= 2100) & (df['Product_Price'] < 10000), 'Product_PriceCat'] = 4
    df.loc[(df['Product_Price'] >= 10000), 'Product_PriceCat']  = 5

    df.loc[(df['Total_Bill'] > 0) & (df['Total_Bill'] < 500), 'Total_BillCat'] = 1
    df.loc[(df['Total_Bill'] >= 500) & (df['Total_Bill'] < 1100), 'Total_BillCat'] = 2
    df.loc[(df['Total_Bill'] >= 1100) & (df['Total_Bill'] < 2100), 'Total_BillCat'] = 3
    df.loc[(df['Total_Bill'] >= 2100) & (df['Total_Bill'] < 10000), 'Total_BillCat'] = 4
    df.loc[(df['Total_Bill'] >= 10000), 'Total_BillCat']  = 5

    X= df.copy() 
    X.drop('Customer_Age',axis=1,inplace=True)
    X.drop('Product_Price',axis=1,inplace=True)
    X.drop('Total_Bill',axis=1,inplace=True)
    X=pd.get_dummies(X,columns=['Customer_City'])
    X.drop_duplicates()

    pred = X.copy()
    
    #Scaling

    scaler = MinMaxScaler()
    new = scaler.fit_transform(X)
    type(new)
    X.columns
    col_names=X.columns
    scaled=pd.DataFrame(columns=col_names,data=new)
    #kmean2 = KMeans(n_clusters=5, random_state=0)
    #kmean2.fit(scaled)
    #pred['kmean2'] = kmean2.labels_

    #Final CLusters K-Mean
    kmean3 = KMeans(n_clusters=7, random_state=0).fit(scaled)
    kmean3.fit(scaled)
    pred['kmean3'] = kmean3.labels_

    cust_id = Customer_ids.from_mongo(current_user.customer_id)
    resp = pred.loc[pred.Customer_No==cust_id['number']]
    a=resp['kmean3'].head(1).to_string(index=False)
    print(a)
    count = 1
    respcluster = pred.loc[pred.kmean3==int(a)]
  #  print(respcluster['Product_No'].tolist())
    temp = respcluster['Product_No'].tolist()
    product_list = []
    for x in temp:
      #  print(x)
        products_id = Product_ids.from_mongo_by_number(int(x))
        product = Product.from_mongo(products_id['product_id'])
        category = Category.from_mongo(product['category_id'])
        subcategory = Subcategory.from_mongo(product['subcategory_id'])
        quantity = Inventory.from_mongo(product['product_id'])
        product_detail = {'product_id': product['product_id'],
                'product_name':product['product_name'],
                'product_image':product['product_image'],
                'price':product['price'],
                'description':product['description'],
                'status':product['status'],
                'expiring_date':product['expiring_date'],
                'manufacture_date':product['manufacture_date'],
                'category_id':product['category_id'],
                'category_name':category['category_name'],
                'subcategory_id':product['subcategory_id'],
                'subcategory_name':subcategory['subcategory_name'],
                'rating':product['rating'],
                'product_quantity':quantity['quantity']
                }
        product_list.append(product_detail)
    print(len(product_list))
    return json.dumps(product_list,default=json_util.default)


#Get Product Images
@app.route('/products/<imagename>')
def send_product_image(imagename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],imagename)


##########################################################################
#Category API's
##########################################################################


#Add Category
@app.route('/categories/addcategory', methods=['POST'])
@login_required
def addcategory():
    response = Category.from_mongo_by_name(request.form['category_name'])
    if response is None:
        category_image = request.files['category_image']
        if category_image is None:
            return 'No Picture'
        else:
            category = Category(request.form['category_name'],
                request.form['description'],
                str('k'))
            result = category.save_to_mongo()
            category_image.filename =  category.category_id+".jpg"
            if allowed_file(category_image.filename):
                category_image.save(os.path.join(app.config['UPLOAD_CATEGORY_FOLDER'],category_image.filename))
                update = { '$set': {'category_image': category_image.filename}}
                Category.from_mongo_update(category.category_id,update)
                return result
            else:
                return "Image not allowed."
    else:
        return 'Already Existed!'


#Update Category
@app.route('/categories/updatecategory',methods=['POST'])
@login_required
def updatecategory():
    update = {"$set":{'category_name': request.get_json()['category_name'],
        'description': request.get_json()['description']
    }}
    Category.from_mongo_update(request.get_json()['category_id'],update)
    result = jsonify({"result":"Category Updated"})
    return result


#Delete Category
@app.route('/categories/deletecategory',methods=['POST'])
@login_required
def deletecategory():
    Category.from_mongo_delete(request.get_json()['category_id'])
    result =  'Category deleted!'
    return result


#Get One Category
@app.route('/categories/getcategory/<category_id>', methods=['GET'])
@login_required
def getcategory(category_id):
    category = [Category.from_mongo(category_id)]
    return json.dumps(category,default=json_util.default)


#Get All Category
@app.route('/categories/getallcategory',methods=['GET'])
@login_required
def getallcategory():
    category = Category.from_mongo_get_all_product()
    return json.dumps(category,default=json_util.default)


#Get Category Images
@app.route('/categories/<imagename>')
def send_category_image(imagename):
    return send_from_directory(app.config['UPLOAD_CATEGORY_FOLDER'],imagename)


##########################################################################
#Subcategory API's
##########################################################################


#Add Subcategory
@app.route('/subcategories/addsubcategory', methods=['POST'])
@login_required
def addsubcategory():
    response = Subcategory.from_mongo_by_name_and_cat(request.get_json()['subcategory_name'],request.get_json()['category_id'])
    if response is None:
        subcategory = Subcategory(request.get_json()['subcategory_name'],
            request.get_json()['description'],
            request.get_json()['category_id'])
        result = subcategory.save_to_mongo()
        return result
    else:
        return 'Already Existed!'


#Update Subcategory
@app.route('/subcategories/updatesubcategory',methods=['POST'])
@login_required
def updatesubcategory():
    update = {"$set":{'subcategory_name': request.get_json()['subcategory_name'],
        'description': request.get_json()['description']
    }}
    Subcategory.from_mongo_update(request.get_json()['subcategory_id'],update)
    result = jsonify({"result":"Subcategory Updated"})
    return result


#Delete Subcategory
@app.route('/subcategories/deletesubcategory',methods=['POST'])
@login_required
def deletesubcategory():
    Subcategory.from_mongo_delete(request.get_json()['subcategory_id'])
    result =  'Subcategory deleted!'
    return result


#Get One Subcategory
@app.route('/subcategories/getsubcategory/<subcategory_id>', methods=['GET'])
@login_required
def getsubcategory(subcategory_id):
    subcategory = Subcategory.from_mongo(subcategory_id)
    print(subcategory)
    return json.dumps(subcategory,default=json_util.default)



#Get All Subcategory
@app.route('/subcategories/getallsubcategory',methods=['GET'])
@login_required
def getallsubcategory():
    subcategory = Subcategory.from_mongo_get_all_product()
    subcategory_send = []
    for x in subcategory:
        category = Category.from_mongo(x['category_id'])
        new_subcategory={'subcategory_id': x['subcategory_id'],
            'category_name': category['category_name'],
            'category_id': x['category_id'],
            'subcategory_name': x['subcategory_name'],
            'description': x['description']
        }
        subcategory_send.append(new_subcategory)
    return json.dumps(subcategory_send,default=json_util.default)


##########################################################################
#Supplier API's
##########################################################################


#Add Supplier
@app.route('/suppliers/addsupplier', methods=['POST'])
@login_required
def addsupplier():
    response = Supplier.from_mongo_by_name(request.get_json()['supplier_name'])
    product = Product.from_mongo_by_name(request.get_json()['product_name'])
    if response is None:
        supplier = Supplier(request.get_json()['supplier_name'],
            request.get_json()['supplier_quantity'],
            datetime.now(),
            product['product_id'])
        result = supplier.save_to_mongo()
        return result
    else:
        return 'Already Existed!'


#Update Supplier
@app.route('/suppliers/updatesupplier',methods=['POST'])
@login_required
def updatesupplier():
    update = {"$set":{'supplier_name': request.get_json()['supplier_name'],
        'supplier_quantity': request.get_json()['supplier_quantity'],
        'product_id': request.get_json()['product_id']
    }}
    Supplier.from_mongo_update(request.get_json()['supplier_id'],update)
    result = jsonify({"result":"Supplier Updated"})
    return result


#Delete Supplier
@app.route('/suppliers/deletesupplier',methods=['POST'])
@login_required
def deletesupplier():
    Supplier.from_mongo_delete(request.get_json()['supplier_id'])
    result =  'Supplier deleted!'
    return result


#Get One Supplier
@app.route('/suppliers/getsupplier/<supplier_id>', methods=['GET'])
@login_required
def getsupplier(supplier_id):
    supplier = Supplier.from_mongo(supplier_id)
    productname = Product.from_mongo(supplier['product_id'])
    product_name = ''
    if productname is None:
        product_name = 'Not Found'
    else:
        product_name = productname['product_name']
    new_supplier = {'supplier_id': supplier['supplier_id'],
            'supplier_name': supplier['supplier_name'],
            'supplier_quantity': supplier['supplier_quantity'],
            'supplying_date': supplier['supplying_date'],
            'product_id': supplier['product_id'],
            'product_name': product_name
        }
    return json.dumps(new_supplier,default=json_util.default)


#Get All Supplier
@app.route('/suppliers/getallsupplier',methods=['GET'])
@login_required
def getallsupplier():
    suppliers = Supplier.from_mongo_get_all_supplier()
    suppliers_send = []
    for x in suppliers:
        productname = Product.from_mongo(x['product_id'])
        product_name = ''
        if productname is None:
            product_name = 'Not Found'
        else:
            product_name = productname['product_name']
        new_supplier = {'supplier_id': x['supplier_id'],
            'supplier_name': x['supplier_name'],
            'supplier_quantity': x['supplier_quantity'],
            'supplying_date': x['supplying_date'],
            'product_id': x['product_id'],
            'product_name': product_name
        }
        suppliers_send.append(new_supplier)
    return json.dumps(suppliers_send,default=json_util.default)


##########################################################################
#Cart API's
##########################################################################


#Add Cart
@app.route('/carts/addcart', methods=['POST'])
@login_required
def addcart():
    cart = Cart(request.get_json()['products'],
            request.get_json()['total_bill'],
            str(None),
            datetime.now(),
            'Not Confirmed')
    result = cart.save_to_mongo()
    qr = qrcode.make(cart.cart_id)  
    #qr.save(f'purchase_qrcode/{cart.cart_id}_qrcode.png')
    qr = qrcode.make(cart.cart_id)
    qr_name = secure_filename(cart.cart_id+"_qrcode.png")
    qr.save(os.path.join(app.config['UPLOAD_QRCODE_FOLDER'],qr_name))
    return str(cart.cart_id)


#Cart Confirmation
@app.route('/carts/cartconfirmation',methods=['POST'])
def confirmation():
    update = {"$set":{'customer_id': current_user.customer_id,
        'status': 'Confirmed'
    }}
    Cart.from_mongo_update(request.get_json()['cart_id'],update)
    result = jsonify({"result":"Cart Confirmrd."})
    cart = Cart.from_mongo(request.get_json()['cart_id'])
    for x in cart['products']:
        quantity=Inventory.from_mongo(x['product_id'])
        new_quantity = int(quantity['quantity'])-int(x['product_quantity'])
        update = {"$set":{'quantity': new_quantity
        }}
        Inventory.from_mongo_update(quantity['product_id'],update)
    device_id = DeviceToken.from_mongo_by_user_id(current_user.customer_id)
    data = {
            "to": device_id['device_id'],
            "title":"Purchase Confirmed",
            "body": "Thanks for shopping.Please visit us again!"
        }
    response = requests.post(API_URL, data)
    data = {
            "to": device_id['device_id'],
            "title":"Product Review",
            "body": "Please review purchased products."
        }
    response = requests.post(API_URL, data)
    return result


#Update Cart
@app.route('/carts/updatecart',methods=['POST'])
@login_required
def updatecart():
    update = {"$set":{'products': request.get_json()['products'],
        'total_bill': request.get_json()['total_bill'],
        'customer_id': request.get_json()['customer_id'],
        'date': datetime.now()
    }}
    Cart.from_mongo_update(request.get_json()['cart_id'],update)
    result = jsonify({"result":"Cart Updated"})
    return result


#Delete Cart
@app.route('/carts/deletecart',methods=['POST'])
@login_required
def deletecart():
    Cart.from_mongo_delete(request.get_json()['cart_id'])
    result =  'Cart deleted!'
    return result


#Get Cart for confirmation
@app.route('/carts/getcartforconfirmation/<cart_id>', methods=['GET'])
@login_required
def getcart(cart_id):
    cart = Cart.from_mongo(cart_id)
    products_send = []
    for x in cart['products']:
        product=Product.from_mongo(x['product_id'])
        new_price=int(x['product_quantity'])*int(product['price'])
        new_product = {'product_id': x['product_id'],
            'product_name':product['product_name'],
            'product_price':product['price'],
            'product_quantity':x['product_quantity'],
            'product_total_price':new_price
        }
        products_send.append(new_product)
    cart['products'] = products_send 
    return json.dumps(cart,default=json_util.default)


#Get All Cart
@app.route('/carts/getallcart',methods=['GET'])
@login_required
def getallcart():
    carts = Cart.from_mongo_get_all_cart()
    return json.dumps(carts,default=json_util.default)


#Get All Carts for employee
@app.route('/carts/getallcartsforemployee',methods=['GET'])
@login_required
def getallcartsforemployee():
    cart =Cart.from_mongo_get_all_cart()
    carts_send = []
    for x in cart:
        date_time = str(x['date'])
        date = date_time.rsplit(' ')[0]
        temp = date_time.rsplit(' ')[1]
        time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
        customer = Customer.from_mongo_by_id(x['customer_id'])
        customer_name=''
        #print(customer)
        if customer is None:
            customer_name = 'Not Found'
        else:
            customer_name = customer['first_name']+' '+customer['last_name'] 
        new_cart = {'cart_id': x['cart_id'],
            'customer_id': x['customer_id'],
            'customer_name': customer_name,
            'total_bill': x['total_bill'],
            'date': date,
            'time': time,
            'status': x['status']
        }
        carts_send.append(new_cart)
    return json.dumps(carts_send,default=json_util.default)


#Get All products of a Cart
@app.route('/carts/getcartproducts/<cart_id>',methods=['GET'])
@login_required
def getcartproducts(cart_id):
    cart = Cart.from_mongo(cart_id)
    product_send = []
    for x in cart['products']:
        product = Product.from_mongo(x['product_id'])
        new_product = {'product_id': product['product_id'],
            'product_name': product['product_name']
        }
        product_send.append(new_product)
    return json.dumps(product_send,default=json_util.default) 


#Get all cart of a Customer
@app.route('/carts/getallcartsofcustomer',methods=['GET'])
@login_required
def getallcartsofcustomer():
    carts = Cart.from_mongo_all_cart_of_customer(current_user.customer_id)
    carts_send = []
    for x in carts:
        date_time = str(x['date'])
        date = date_time.rsplit(' ')[0]
        temp = date_time.rsplit(' ')[1]
        time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
        new_cart = {'cart_id': x['cart_id'],
            'products': x['products'],
            'customer_id': x['customer_id'],
            'total_bill': x['total_bill'],
            'date': date,
            'time': time,
            'status': x['status']
        }
        carts_send.append(new_cart)
    carts_send.reverse()
    return json.dumps(carts_send,default=json_util.default)


#Get all details of a Cart
@app.route('/carts/getalldetailofcart/<cart_id>',methods=['GET'])
@login_required
def getalldetailofcart(cart_id):
    cart = Cart.from_mongo(cart_id)
    product_send = []
    for x in cart['products']:
        product = Product.from_mongo(x['product_id'])
        productrating = Productrating.from_mongo_by_customer_and_product(x['product_id'],current_user.customer_id)
        product_rating = ''
        if productrating is None:
            product_rating = 'Not rated'
        else:
            product_rating = productrating['rating']
        new_price = int(x['product_quantity'])*int(product['price'])
        new_product = {'product_id': product['product_id'],
            'product_name': product['product_name'],
            'quantity': x['product_quantity'],
            'price': product['price'],
            'price_total': new_price,
            'rating': product_rating
        }
        product_send.append(new_product)
    invoice = Invoice.from_mongo_by_cart(cart_id)
    review = Reviews.from_mongo_customer_and_cart(current_user.customer_id,cart_id)
    review_send = ''
    if review is None:
        review_send = 'No feedback'
    else:
        review_send = review['review']
    date_time = str(cart['date'])
    date = date_time.rsplit(' ')[0]
    temp = date_time.rsplit(' ')[1]
    time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
    cart_send = [{'cart_id': cart['cart_id'],
            'products': product_send,
            'customer_id': cart['customer_id'],
            'status': cart['status'],
            'date': date,
            'time': time,
            'bill': invoice['bill'],
            'given_cash': invoice['given_cash'],
            'returned_cash': invoice['returned_cash'],
            'feedback': review_send
    }]
    return json.dumps(cart_send,default=json_util.default)


#Get all details of a Cart for employee
@app.route('/carts/getalldetailofcartforemployee/<cart_id>',methods=['GET'])
@login_required
def getalldetailofcartforemployee(cart_id):
    cart = Cart.from_mongo(cart_id)
    #print(cart)
    product_send = []
    for x in cart['products']:
        product = Product.from_mongo(x['product_id'])
        print(x['product_id'])
        productrating = Productrating.from_mongo_by_customer_and_product(x['product_id'],cart['customer_id'])
        product_rating = ''
        if productrating is None:
            product_rating = 'Not rated'
        else:
            product_rating = productrating['rating']
        #print(x['product_quantity'])
        new_price = int(x['product_quantity'])*int(product['price'])
        new_product = {'product_id': product['product_id'],
            'product_name': product['product_name'],
            'quantity': x['product_quantity'],
            'price': product['price'],
            'price_total': new_price,
            'rating': product_rating
        }
        product_send.append(new_product)
    invoice = Invoice.from_mongo_by_cart(cart_id)
    review = Reviews.from_mongo_customer_and_cart(cart['customer_id'],cart_id)
    review_send = ''
    if review is None:
        review_send = 'No feedback'
    else:
        review_send = review['review']
    date_time = str(cart['date'])
    date = date_time.rsplit(' ')[0]
    temp = date_time.rsplit(' ')[1]
    time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
    customer = Customer.from_mongo_by_id(cart['customer_id'])
    customer_name=''
    if customer is None:
        customer_name = 'Not Found'
    else:
        customer_name =customer['first_name']+' '+customer['last_name']
    cart_send = [{'cart_id': cart['cart_id'],
            'products': product_send,
            'customer_id': cart['customer_id'],
            'customer_name': customer_name,
            'status': cart['status'],
            'date': date,
            'time': time,
            'bill': invoice['bill'],
            'given_cash': invoice['given_cash'],
            'returned_cash': invoice['returned_cash'],
            'feedback': review_send
    }]
    print(invoice['bill'])
    return json.dumps(cart_send,default=json_util.default)


#Get QRCode image
@app.route('/carts/<cartqrcodename>')
def send_cart_qrcode_image(cartqrcodename):
    cartqrcode = cartqrcodename+"_qrcode.png"
    return send_from_directory(app.config['UPLOAD_QRCODE_FOLDER'],cartqrcode)


##########################################################################
#Reserved Product API's
##########################################################################


#Add Reserved Product
@app.route('/reservedproducts/addreservedproduct', methods=['POST'])
@login_required
def addreservedproduct():
    reservedproduct = ReservedProduct(request.get_json()['product_id'],
        current_user.customer_id,
        request.get_json()['reserved_quantity'],
        request.get_json()['reserved_time'],
        datetime.now(),
        'Reserved'
        )
    quantity = Inventory.from_mongo(request.get_json()['product_id'])
    new_quantity = int(quantity['quantity'])-int(request.get_json()['reserved_quantity'])
    update = { '$set': {'quantity': new_quantity}}
    Inventory.from_mongo_update(request.get_json()['product_id'],update)
    result = reservedproduct.save_to_mongo()
    device_id = DeviceToken.from_mongo_by_user_id(current_user.customer_id)
    product_res = Product.from_mongo(reservedproduct.product_id)
    data = {
                    "to": device_id['device_id'],
                    "title":"Product Reserved",
                    "body": product_res['product_name']+" has been reserved."
                    }
    response = requests.post(API_URL, data)
    return result


#Update Reserved Product
@app.route('/reservedproducts/updatereservedproduct',methods=['POST'])
@login_required
def updatereservedproduct():
    update = {"$set":{'product_id': request.get_json()['product_id'],
        'customer_id': request.get_json()['customer_id'],
        'reserved_quantity': request.get_json()['reserved_quantity'],
        'reserved_time': request.get_json()['reserved_time']
    }}
    ReservedProduct.from_mongo_update(request.get_json()['reservation_id'],update)
    result = jsonify({"result":"Reserved Product Updated"})
    return result


#Delete Reserved Product
@app.route('/reservedproducts/deletereservedproduct',methods=['POST'])
@login_required
def deletereservedproduct():
    ReservedProduct.from_mongo_delete(request.get_json()['reservation_id'])
    result =  'Reserved Product deleted!'
    return result


#Get One Reserved Product
@app.route('/reservedproducts/getreservedproduct', methods=['GET'])
@login_required
def getreservedproduct():
    reservedproduct = ReservedProduct.from_mongo(request.get_json()['reservation_id'])
    reservedproduct_send = []
    if reservedproduct is None:
        return 'Not Found'
    else:
        product = Product.from_mongo(reservedproduct['product_id'])
        product_name = ''
        if product is None:
            product_name = 'Not Found'
        else:
            product_name = product['product_name']
        customer = Customer.from_mongo_by_id(reservedproduct['customer_id'])
        customer_name = ''
        if customer is None:
            customer_name = 'Not Found'
        else:
            customer_name = customer['first_name']+' '+customer['last_name']
        date_time = str(reservedproduct['reservation_date'])
        date = date_time.rsplit(' ')[0]
        temp = date_time.rsplit(' ')[1]
        time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
        new_reserve = {'reservation_id': reservedproduct['reservation_id'],
            'product_id': reservedproduct['product_id'],
            'product_name': product_name,
            'customer_id': reservedproduct['customer_id'],
            'customer_name': customer_name,
            'reserved_quantity': reservedproduct['reserved_quantity'],
            'reserved_time': reservedproduct['reserved_time'],
            'date': date,
            'time': time,
            'status': reservedproduct['status']
        }
        reservedproduct_send.append(new_reserve)
        return json.dumps(reservedproduct_send,default=json_util.default)


#Get Reserved Products All
@app.route('/reservedproducts/getreserved',methods=['GET'])
@login_required
def getreserved():
    reservedproducts = ReservedProduct.from_mongo_get_reserved()
    reservedproduct_send = []
    if reservedproducts is None:
        return 'Not Found'
    else:
        for x in reservedproducts:
            product = Product.from_mongo(x['product_id'])
            product_name = ''
            if product is None:
                product_name = 'Not Found'
            else:
                product_name = product['product_name']
            customer = Customer.from_mongo_by_id(x['customer_id'])
            customer_name = ''
            if customer is None:
                customer_name = 'Not Found'
            else:
                customer_name = customer['first_name']+' '+customer['last_name']
            date_time = str(x['reservation_date'])
            date = date_time.rsplit(' ')[0]
            temp = date_time.rsplit(' ')[1]
            time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
            new_reserve = {'reservation_id': x['reservation_id'],
                'product_id': x['product_id'],
                'product_name': product_name,
                'customer_id': x['customer_id'],
                'customer_name': customer_name,
                'reserved_quantity': x['reserved_quantity'],
                'reserved_time': x['reserved_time'],
                'date': date,
                'time': time,
                'status': x['status']
            }
            reservedproduct_send.append(new_reserve)
        return json.dumps(reservedproduct_send,default=json_util.default)


#Get All Reserved Product
@app.route('/reservedproducts/getallreservedproduct',methods=['GET'])
@login_required
def getallreservedproduct():
    reservedproducts = ReservedProduct.from_mongo_get_all_reservations()
    reservedproduct_send = []
    if reservedproducts is None:
        return 'Not Found'
    else:
        for x in reservedproducts:
            product = Product.from_mongo(x['product_id'])
            product_name = ''
            if product is None:
                product_name = 'Not Found'
            else:
                product_name = product['product_name']
            customer = Customer.from_mongo_by_id(x['customer_id'])
            customer_name = ''
            if customer is None:
                customer_name = 'Not Found'
            else:
                customer_name = customer['first_name']+' '+customer['last_name']
            date_time = str(x['reservation_date'])
            date = date_time.rsplit(' ')[0]
            temp = date_time.rsplit(' ')[1]
            time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
            new_reserve = {'reservation_id': x['reservation_id'],
                'product_id': x['product_id'],
                'product_name': product_name,
                'customer_id': x['customer_id'],
                'customer_name': customer_name,
                'reserved_quantity': x['reserved_quantity'],
                'reserved_time': x['reserved_time'],
                'date': date,
                'time': time,
                'status': x['status']
            }
            reservedproduct_send.append(new_reserve)
        return json.dumps(reservedproduct_send,default=json_util.default)


#Get All Reserved Product of One Customer
@app.route('/reservedproducts/getallreservedproductofcustomer',methods=['GET'])
@login_required
def getallreservedproductofcustomer():
    reservedproducts = ReservedProduct.from_mongo_by_customer(current_user.customer_id)
    reservedproduct_send = []
    for x in reservedproducts:
        product = Product.from_mongo(x['product_id'])
        date_time = str(x['reservation_date'])
        date = date_time.rsplit(' ')[0]
        temp = date_time.rsplit(' ')[1]
        time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
        new_reserve = {'reservation_id': x['reservation_id'],
            'product_id': x['product_id'],
            'product_name': product['product_name'],
            'customer_id': x['customer_id'],
            'reserved_quantity': x['reserved_quantity'],
            'reserved_time': x['reserved_time'],
            'date': date,
            'time': time,
            'status': x['status']
        }
        reservedproduct_send.append(new_reserve)
    reservedproduct_send.reverse()
    return json.dumps(reservedproduct_send,default=json_util.default)


#Cancel Reservation
@app.route('/reservedproducts/cancelreservation',methods=['POST'])
@login_required
def cancelreservation():
    reservation = ReservedProduct.from_mongo(request.get_json()['reservation_id'])
    quantity = Inventory.from_mongo(reservation['product_id'])
    new_quantity = int(quantity['quantity'])+int(reservation['reserved_quantity'])
    update = { '$set': {'quantity': new_quantity}}
    Inventory.from_mongo_update(reservation['product_id'],update)
    update = { '$set': {'status': 'Cancelled'}}
    ReservedProduct.from_mongo_update(request.get_json()['reservation_id'],update)
    result= jsonify({'result' : 'reservation cancel'})
    return result 


#Clear Reservation
@app.route('/reservedproducts/clearreservation',methods=['POST'])
@login_required
def clearreservation():
    reservation = ReservedProduct.from_mongo(request.get_json()['reservation_id'])
    quantity = Inventory.from_mongo(reservation['product_id'])
    new_quantity = int(quantity['quantity'])+int(reservation['reserved_quantity'])
    update = { '$set': {'quantity': new_quantity}}
    Inventory.from_mongo_update(reservation['product_id'],update)
    update = { '$set': {'status': 'Cleared'}}
    ReservedProduct.from_mongo_update(request.get_json()['reservation_id'],update)
    result= jsonify({'result' : 'reservation cleared'})
    return result


##########################################################################
#Invoice API's
##########################################################################


#Add Invoice
@app.route('/invoices/addinvoice', methods=['POST'])
@login_required
def addinvoice():
    response = Invoice.from_mongo(request.get_json()['cart_id'])
    if response is None:
        invoice = Invoice(request.get_json()['cart_id'],
            request.get_json()['bill'],
            request.get_json()['given_cash'],
            request.get_json()['reserved_cash'])
        result = invoice.save_to_mongo()
        return result
    else:
        return 'Already Existed!'


#Update Invoice
@app.route('/invoices/updateinvoice',methods=['POST'])
@login_required
def updateinvoice():
    update = {"$set":{'cart_id': request.get_json()['cart_id'],
        'bill': request.get_json()['bill'],
        'given_cash': request.get_json()['given_cash'],
        'returned_time': request.get_json()['returned_time']
    }}
    Invoice.from_mongo_update(request.get_json()['invoice_id'],update)
    result = jsonify({"result":"Invoice Updated"})
    return result


#Delete Invoice
@app.route('/invoices/deleteinvoice',methods=['POST'])
@login_required
def deleteinvoice():
    Invoice.from_mongo_delete(request.get_json()['invoice_id'])
    result =  'Invoice deleted!'
    return result


#Get One Invoice
@app.route('/invoices/getinvoice', methods=['GET'])
@login_required
def getinvoice():
    invoice = Invoice.from_mongo(request.get_json()['invoice_id'])
    return json.dumps(invoice,default=json_util.default)


#Get All Invoice
@app.route('/invoices/getallinvoice',methods=['GET'])
@login_required
def getallinvoice():
    invoices = Invoice.from_mongo_get_all_invoices()
    return json.dumps(invoices,default = json_util.default)


##########################################################################
#Reviews API's
##########################################################################


#Add Review
@app.route('/reviews/addreview', methods=['POST'])
@login_required
def addreview():
    review = Reviews(current_user.customer_id,
        request.get_json()['cart_id'],
        request.get_json()['review'],
        datetime.now())
    result = review.save_to_mongo()
    for x in request.get_json()['ratings']:
        product_rating = Productrating.from_mongo_by_customer_and_product(x['product_id'],current_user.customer_id)
        if product_rating is None:
            productrating = Productrating(x['product_id'],
                current_user.customer_id,
                x['rating'])
            productrating.save_to_mongo()
        else:
            update = {'$set':{'rating':x['rating']}}
            Productrating.from_mongo_update(x['product_id'],current_user.customer_id,update)
        product_ratings = list(Productrating.from_mongo_by_product(x['product_id']))
        rating_sum = 0
        new_rating = 0
        if product_ratings is None:
            pass
        else:
            for y in product_ratings:
                rating_sum = rating_sum + int(y['rating'])
            new_rating = rating_sum/int(len(product_ratings))
            update = {'$set':{'rating': new_rating}}
            Product.from_mongo_update(x['product_id'],update)

    return result
    

#Update Review
@app.route('/reviews/updatereview',methods=['POST'])
@login_required
def updatereview():
    update = {"$set":{'customer_id': request.get_json()['customer_id'],
        'review': request.get_json()['review']
    }}
    Reviews.from_mongo_update(request.get_json()['review_id'],update)
    result = jsonify({"result":"Review Updated"})
    return result


#Delete Review
@app.route('/reviews/deletereview',methods=['POST'])
@login_required
def deletereview():
    Reviews.from_mongo_delete(request.get_json()['review_id'])
    result =  'Review deleted!'
    return result


#Get One Review
@app.route('/reviews/getreview/<review_id>', methods=['GET'])
@login_required
def getreview(review_id):
    review = Reviews.from_mongo(review_id)
    if review is None:
        return "Not Found!"
    else:
        customer = Customer.from_mongo_by_id(review['customer_id'])
        customer_name = customer['first_name']+' '+customer['last_name'] 
        cart = Cart.from_mongo(review['cart_id'])
        product_send = []
        for x in cart['products']:
            product = Product.from_mongo(x['product_id'])
            productrating = Productrating.from_mongo_by_customer_and_product(x['product_id'],review['customer_id'])
            product_rating = ''
            if productrating is None:
                product_rating = 'Not rated'
            else:
                product_rating = productrating['rating']
            new_product = {'product_id': product['product_id'],
                'product_name': product['product_name'],
                'rating': product_rating
            }
            product_send.append(new_product)
        date_time = str(review['review_datetime'])
        date = date_time.rsplit(' ')[0]
        temp = date_time.rsplit(' ')[1]
        time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
        review_send = [{'review_id': review['review_id'],
                'customer_id': review['customer_id'],
                'customer_name':customer_name,
                'cart_id': review['cart_id'],
                'products': product_send,
                'review': review['review'],
                'date': date,
                'time': time,
        }]
        return json.dumps(review_send,default=json_util.default)


#Get All Review
@app.route('/reviews/getallreview',methods=['GET'])
@login_required
def getallreview():
    reviews = list(Reviews.from_mongo_get_all_reviews())
    reviews_send = []
    if reviews is None:
        return 'No Reviews!'
    else:
        for x in reviews:
            customer = Customer.from_mongo_by_id(x['customer_id'])
            customer_name = ''
            if customer is None:
                customer_name = 'not found'
            else:
                customer_name = customer['first_name'] + ' ' + customer['last_name']
            date_time = str(x['review_datetime'])
            date = date_time.rsplit(' ')[0]
            temp = date_time.rsplit(' ')[1]
            time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
            review_new = {'review_id': x['review_id'],
                'customer_id': x['customer_id'],
                'customer_name': customer_name,
                'cart_id': x['cart_id'],
                'review': x['review'],
                'date': date,
                'time': time
            }
            reviews_send.append(review_new)
        return json.dumps(reviews_send,default = json_util.default)


##########################################################################
#Notification API's
##########################################################################


#Add Notification
@app.route('/notifications/addnotification', methods=['POST'])
@login_required
def addnotification():
    response = Notification.from_mongo(request.get_json()['notification_id'])
    if response is None:
        notification = Notification(request.get_json()['from_user_id'],
            request.get_json()['title'],
            request.get_json()['message'],
            request.get_json()['url'],
            request.get_json()['read_status'],
            request.get_json()['delivery_status'],
            request.get_json()['to_user_id'])
        result = notification.save_to_mongo()
        return result
    else:
        return 'Already Existed!'


#Update Notification
@app.route('/notifications/updatenotification',methods=['POST'])
@login_required
def updatenotification():
    update = {"$set":{'from_user_id': request.get_json()['from_user_id'],
        'title': request.get_json()['title'],
        'message': request.get_json()['message'],
        'url': request.get_json()['url'],
        'read_status': request.get_json()['read_status'],
        'delivery_status': request.get_json()['delivery_status'],
        'to_user_id': request.get_json()['to_user_id']
    }}
    Notification.from_mongo_update(request.get_json()['notification_id'],update)
    result = jsonify({"result":"Notification Updated"})
    return result


#Delete Notification
@app.route('/notifications/deletenotification',methods=['POST'])
@login_required
def deletenotification():
    Notification.from_mongo_delete(request.get_json()['notification_id'])
    result =  'Notification deleted!'
    return result


#Get One Notification
@app.route('/notifications/getnotification', methods=['GET'])
@login_required
def getnotification():
    notification = Notification.from_mongo(request.get_json()['notification_id'])
    return json.dumps(notification,default=json_util.default)


#Get All Notification
@app.route('/notifications/getallnotification',methods=['GET'])
@login_required
def getallnotification():
    notifications = Notification.from_mongo_get_all_notifications()
    return json.dumps(notifications,default = json_util.default)


##########################################################################
#Tickets API's
##########################################################################


#Add Ticket
@app.route('/tickets/addticket', methods=['POST'])
@login_required
def addticket():
    ticket = Tickets(request.get_json()['complaint_id'],
            datetime.now(),
            str(None),
            current_user.customer_id,
            request.get_json()['complaint'],
            'Open',
            'Pending')
    result = ticket.save_to_mongo()
    return result


#Complaint Receive
@app.route('/tickets/receiveticket',methods=['POST'])
@login_required
def receiveticket():
    update = {'$set':{'employee_id':current_user.employeeID,
        'receive_status': 'Received'
        }}
    Tickets.from_mongo_update(request.get_json()['ticket_id'],update)
    result = jsonify({"result":"Complaint Received"})
    return result


#Update Ticket
@app.route('/tickets/updateticket',methods=['POST'])
@login_required
def updateticket():
    update = {"$set":{'complaint': request.get_json()['complaint'],
        'date': datetime.now(),
        'employee_id': request.get_json()['employee_id'],
        'customer_id': request.get_json()['customer_id']
    }}
    Tickets.from_mongo_update(request.get_json()['ticket_id'],update)
    result = jsonify({"result":"Ticket Updated"})
    return result


#Delete Ticket
@app.route('/tickets/deleteticket',methods=['POST'])
@login_required
def deleteticket():
    Tickets.from_mongo_delete(request.get_json()['ticket_id'])
    result =  'Ticket deleted!'
    return result


#Close Ticket
@app.route('/tickets/closeticket/<ticket_id>',methods=['GET'])
@login_required
def closeticket(ticket_id):
    update = {"$set":{'status': 'Closed',
    'receive_status': 'Received'
    }}
    Tickets.from_mongo_update(ticket_id,update)
    result = str(ticket_id)
    ticket_res = Tickets.from_mongo(ticket_id)
    device_id = DeviceToken.from_mongo(ticket_res['customer_id'])
    data = {
            "to": device_id['device_id'],
            "title":"Complaint close",
            "body": "Please provide relevant feedback."
        }
    response = requests.post(API_URL, data)
    return result


#Get One Ticket
@app.route('/tickets/getticket/<ticket_id>', methods=['GET'])
@login_required
def getticket(ticket_id):
    ticket = Tickets.from_mongo(ticket_id)
    if ticket is None:
        return "No Ticket Found"
    else:
        responses = list(TicketsResponse.from_mongo_get_all_by_ticket(ticket_id))
        responses_send = []
        if responses:
            for x in responses:
                date_time = str(x['date'])
                date = date_time.rsplit(' ')[0]
                temp = date_time.rsplit(' ')[1]
                time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
                new_response = {'res_ticket_id':x['res_ticket_id'],
                    'ticket_id': x['ticket_id'],
                    'from_user_id': x['from_user_id'],
                    'to_user_id': x['to_user_id'],
                    'message': x['message'],
                    'date': date,
                    'time': time
                }
                responses_send.append(new_response)
        feedback = TicketsFeedback.from_mongo(ticket_id)
        feedback_status = ''
        if feedback is None:
            feedback_status = 'Not Submitted'
        else:
            feedback_status = feedback['status']
        #feedback_message = ''
        #feedback_date = ''
        #feedback_time = ''
        #if feedback:
        #    feedback_date_time = str(feedback['date'])
        #    feedback_date = feedback_date_time.rsplit(' ')[0]
        #    feedback_temp = feedback_date_time.rsplit(' ')[1]
        #    feedback_time = feedback_temp.rsplit(':')[0]+':'+feedback_temp.rsplit(':')[1]
        #    feedback_message = feedback['feedback']
        date_time = str(ticket['date'])
        date = date_time.rsplit(' ')[0]
        temp = date_time.rsplit(' ')[1]
        time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
        ticket_send = [{'ticket_id': ticket['ticket_id'],
                'complaint_id': ticket['complaint_id'],
                'employee_id': ticket['employee_id'],
                'customer_id': ticket['customer_id'],
                'complaint': ticket['complaint'],
                'responses': responses_send,
                'date': date,
                'time': time,
                'feedback_status': feedback_status,
                'ticket_status': ticket['status']
        }]
        return json.dumps(ticket_send,default=json_util.default)


#Get All Ticket
@app.route('/tickets/getallticket',methods=['GET'])
@login_required
def getallticket():
    tickets = list(Tickets.from_mongo_get_all_tickets())
    tickets_send = []
    if tickets is None:
        return 'Nothing Found!'
    else:
        for x in tickets:
            complaint = ComplaintCategory.from_mongo(x['complaint_id'])
            complaint_name = ''
            if complaint is None:
                complaint_name = 'Not Found!'
            else:
                complaint_name = complaint['complaint_name']
            customer = Customer.from_mongo_by_id(x['customer_id'])
            customer_name = ''
            if customer is None:
                customer_name='Not Found!'
            else:
                customer_name= customer['first_name'] +" "+customer['last_name']
            date_time = str(x['date'])
            date = date_time.rsplit(' ')[0]
            temp = date_time.rsplit(' ')[1]
            time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
            ticket_feedback = TicketsFeedback.from_mongo(x['ticket_id'])
            #print(ticket_feedback)
            ticket_feedback_send = ''
            if ticket_feedback is None:
                ticket_feedback_send = 'No Feedback'
            else:
                ticket_feedback_send = ticket_feedback['feedback']
            new_ticket = {'ticket_id': x['ticket_id'],
                'complaint_id': x['complaint_id'],
                'complaint_name': complaint_name,
                'employee_id': x['employee_id'],
                'customer_id': x['customer_id'],
                'customer_name': customer_name,
                'complaint': x['complaint'],
                'date': date,
                'time': time,
                'status': x['status'],
                'receive_status': x['receive_status'],
                'feedback': ticket_feedback_send
            }
            tickets_send.append(new_ticket)
        return json.dumps(tickets_send,default = json_util.default)


#Get All Pending Ticket
@app.route('/tickets/getallpendingticket',methods=['GET'])
@login_required
def getallpendingticket():
    tickets = list(Tickets.from_mongo_get_all_pending_tickets())
    tickets_send = []
    if tickets is None:
        return 'Nothing Found!'
    else:
        for x in tickets:
            complaint = ComplaintCategory.from_mongo(x['complaint_id'])
            complaint_name = ''
            if complaint is None:
                complaint_name = 'Not Found!'
            else:
                complaint_name = complaint['complaint_name']
            customer = Customer.from_mongo_by_id(x['customer_id'])
            customer_name = ''
            if customer is None:
                customer_name='Not Found!'
            else:
                customer_name= customer['first_name'] +" "+customer['last_name']
            date_time = str(x['date'])
            date = date_time.rsplit(' ')[0]
            temp = date_time.rsplit(' ')[1]
            time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
            new_ticket = {'ticket_id': x['ticket_id'],
                'complaint_id': x['complaint_id'],
                'complaint_name': complaint_name,
                'employee_id': x['employee_id'],
                'customer_id': x['customer_id'],
                'customer_name': customer_name,
                'complaint': x['complaint'],
                'date': date,
                'time': time,
                'receive_status': x['receive_status']
            }
            tickets_send.append(new_ticket)
        return json.dumps(tickets_send,default = json_util.default)


#Get All Tickets of One Customer
@app.route('/tickets/getallticketsofcustomer',methods=['GET'])
@login_required
def getallticketsofcustomer():
    tickets = list(Tickets.from_mongo_by_customer(current_user.customer_id))
    new_tickets = [] 
    for x in tickets:
        date_time = str(x['date'])
        date = date_time.rsplit(' ')[0]
        temp = date_time.rsplit(' ')[1]
        time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
        new_ticket = {'ticket_id': x['ticket_id'],
            'complaint_id': x['complaint_id'],
            'employee_id': x['employee_id'],
            'customer_id': x['customer_id'],
            'complaint': x['complaint'],
            'date': date,
            'time': time,
            'receive_status': x['receive_status']
        }
        new_tickets.append(new_ticket)
    new_tickets.reverse()
    return json.dumps(new_tickets,default=json_util.default)


#Get All Tickets of One Employee
@app.route('/tickets/getallticketsofemployee',methods=['GET'])
@login_required
def getallticketsofemployee():
    tickets = list(Tickets.from_mongo_by_employee(current_user.employeeID))
    new_tickets = [] 
    for x in tickets:
        date_time = str(x['date'])
        date = date_time.rsplit(' ')[0]
        temp = date_time.rsplit(' ')[1]
        time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
        new_ticket = {'ticket_id': x['ticket_id'],
            'complaint_id': x['complaint_id'],
            'employee_id': x['employee_id'],
            'customer_id': x['customer_id'],
            'complaint': x['complaint'],
            'date': date,
            'time': time
        }
        new_tickets.append(new_ticket)
    return json.dumps(new_tickets,default=json_util.default)


##########################################################################
#Ticket Response API's
##########################################################################


#Add Ticket Response
@app.route('/ticketsresponses/addticketsresponse', methods=['POST'])
@login_required
def addticketsresponse():
    from_user_id = ''
    to_user_id= ''
    ticket = Tickets.from_mongo(request.get_json()['ticket_id'])
    print(current_user.role)
    if current_user.role=='customer':
        from_user_id = ticket['customer_id']
        to_user_id = ticket['employee_id']
    elif current_user.role=='employee':
        print(ticket['employee_id'])
        from_user_id = ticket['employee_id']
        to_user_id = ticket['customer_id']
    elif current_user.role=='admin':                
        print(ticket['employee_id'])
        from_user_id = ticket['employee_id']
        to_user_id = ticket['customer_id']

    if ticket is None:
        return "No Ticket Found"
    else:
        ticketsresponse = TicketsResponse(request.get_json()['ticket_id'],
            from_user_id,
            to_user_id,
            request.get_json()['message'],
            datetime.now())
        result = ticketsresponse.save_to_mongo()
        device_id = DeviceToken.from_mongo_by_user_id(to_user_id)
        if device_id is None:
            pass
        else:
            data = {
                "to": device_id['device_id'],
                "title":"Complaint Response",
                "body": "You have a response on a submitted complaint from the store."
            }
            response = requests.post(API_URL, data)
        return result


#Update Tickets Response
@app.route('/ticketsresponses/updateticketsresponse',methods=['POST'])
@login_required
def updateticketsresponse():
    update = {"$set":{'ticket_id': request.get_json()['ticket_id'],
        'response': request.get_json()['response'],
        'date': datetime.now()
    }}
    TicketsResponse.from_mongo_update(request.get_json()['ticket_id'],update)
    result = jsonify({"result":"Tickets Response Updated"})
    return result


#Delete Tickets Response
@app.route('/ticketsresponses/deleteticketsresponse',methods=['POST'])
@login_required
def deleteticketsresponse():
    TicketsResponse.from_mongo_delete(request.get_json()['ticket_id'])
    result =  'Tickets Response deleted!'
    return result


#Get One Tickets Response
@app.route('/ticketsresponses/getticketsresponse/<ticket_id>', methods=['GET'])
@login_required
def getticketsresponse(ticket_id):
    print(ticket_id)
    ticketsresponse = TicketsResponse.from_mongo_get_all_by_ticket(ticket_id)
    return json.dumps(ticketsresponse,default=json_util.default)


#Get All Tickets Response
@app.route('/ticketsresponses/getallticketsresponse',methods=['GET'])
@login_required
def getallticketsresponse():
    ticketsresponses = TicketsResponse.from_mongo_get_all_ticket_responses()
    return json.dumps(ticketsresponses,default = json_util.default)


##########################################################################
#Ticket Feedback API's
##########################################################################


#Add Ticket Feedback
@app.route('/ticketsfeedbacks/addticketsfeedback', methods=['POST'])
@login_required
def addticketsfeedback():
    response = TicketsFeedback.from_mongo(request.get_json()['ticket_id'])
    if response is None:
        ticketsfeedback = TicketsFeedback(request.get_json()['ticket_id'],
            request.get_json()['feedback'],
            'Submitted',
            datetime.now()
            )
        result = ticketsfeedback.save_to_mongo()
        return result
    else:
        return 'Already Existed!'


#Update Tickets Feedback
@app.route('/ticketsfeedbacks/updateticketsfeedback',methods=['POST'])
@login_required
def updateticketsfeedback():
    update = {"$set":{'feedback': request.get_json()['feedback']
    }}
    TicketsFeedback.from_mongo_update(request.get_json()['ticket_id'],update)
    result = jsonify({"result":"Tickets Feedback Updated"})
    return result


#Delete Tickets Feedback
@app.route('/ticketsfeedbacks/deleteticketsfeedback',methods=['POST'])
@login_required
def deleteticketsfeedback():
    TicketsFeedback.from_mongo_delete(request.get_json()['ticket_id'])
    result =  'Tickets Feedback deleted!'
    return result


#Get One Tickets Feedback
@app.route('/ticketsfeedbacks/getticketsfeedback/<ticket_id>', methods=['GET'])
@login_required
def getticketsfeedback(ticket_id):
    ticketsfeedback = TicketsFeedback.from_mongo(ticket_id)
    ticketsfeedback_send = []
    date_time = str(ticketsfeedback['date'])
    date = date_time.rsplit(' ')[0]
    temp = date_time.rsplit(' ')[1]
    time = temp.rsplit(':')[0]+':'+temp.rsplit(':')[1]
    new_feedback = {'ticket_id': ticketsfeedback['ticket_id'],
        'feedback': ticketsfeedback['feedback'],
        'status': ticketsfeedback['status'],
        'date': date,
        'time': time
    } 
    ticketsfeedback_send.append(new_feedback)
    return json.dumps(ticketsfeedback_send,default=json_util.default)


#Get All Tickets Feedback
@app.route('/ticketsfeedbacks/getallticketsfeedback',methods=['GET'])
@login_required
def getallticketsfeedback():
    ticketsfeedbacks = TicketsFeedback.from_mongo_get_all_ticket_feedbacks()
    return json.dumps(ticketsfeedbacks,default = json_util.default)


##########################################################################
#Role API's
##########################################################################


#Add Role
@app.route('/roles/addrole', methods=['POST'])
@login_required
def addrole():
    response = Role.from_mongo(request.get_json()['role_id'])
    if response is None:
        role = Role(request.get_json()['role_name'])
        result = role.save_to_mongo()
        return result
    else:
        return 'Already Existed!'


#Update Role
@app.route('/roles/updaterole',methods=['POST'])
@login_required
def updaterole():
    update = {"$set":{'role_name': request.get_json()['role_name']
    }}
    Role.from_mongo_update(request.get_json()['role_id'],update)
    result = jsonify({"result":"Role Updated"})
    return result


#Delete Role
@app.route('/roles/deleterole',methods=['POST'])
@login_required
def deleterole():
    Role.from_mongo_delete(request.get_json()['role_id'])
    result =  'Role deleted!'
    return result


#Get One Role
@app.route('/roles/getrole', methods=['GET'])
@login_required
def getrole():
    role = Role.from_mongo(request.get_json()['role_id'])
    return json.dumps(role,default=json_util.default)


#Get All Roles
@app.route('/roles/getallrole',methods=['GET'])
@login_required
def getallrole():
    roles = Role.from_mongo_get_all_roles()
    return json.dumps(roles,default = json_util.default)


##########################################################################
#Complaint Category API's
##########################################################################


#Add Complaint Category
@app.route('/complaintcategorys/addcomplaintcategory', methods=['POST'])
@login_required
def addcomplaintcategory():
    response = ComplaintCategory.from_mongo_by_name(request.get_json()['complaint_name'])
    if response is None:
        complaintcategory = ComplaintCategory(request.get_json()['complaint_name'])
        result = complaintcategory.save_to_mongo()
        return result
    else:
        return 'Already Existed!'


#Update Complaint Category
@app.route('/complaintcategorys/updatecomplaintcategory',methods=['POST'])
@login_required
def updatecomplaintcategory():
    update = {"$set":{'complaint_name': request.get_json()['complaint_name']
    }}
    ComplaintCategory.from_mongo_update(request.get_json()['complaint_id'],update)
    result = jsonify({"result":"Complaint Updated"})
    return result


#Delete Complaint Category
@app.route('/complaintcategorys/deletecomplaintcategory',methods=['POST'])
@login_required
def deletecomplaintcategory():
    print(request.get_json()['complaint_id'])
    ComplaintCategory.from_mongo_delete(request.get_json()['complaint_id'])
    result =  'Complaint Category deleted!'
    return result


#Get One Complaint Category
@app.route('/complaintcategorys/getcomplaintcategory/<complaint_id>', methods=['GET'])
@login_required
def getcomplaintcategory(complaint_id):
    complaintcategory = ComplaintCategory.from_mongo(complaint_id)
    return json.dumps(complaintcategory,default=json_util.default)


#Get All Complaint Category
@app.route('/complaintcategorys/getallcomplaintcategory',methods=['GET'])
@login_required
def getallcomplaintcategory():
    complaintcategories = list(ComplaintCategory.from_mongo_get_all_complaint())
    return json.dumps(complaintcategories,default = json_util.default)


##########################################################################
#Customer Searches API's
##########################################################################


#Add customer searches
@app.route('/customersearches/addcustomersearches', methods=['POST'])
@login_required
def addcustomersearches():
    customersearches = CustomerSearches(current_user.customer_id,
        request.get_json()['search'],
        datetime.now())
    result = customersearches.save_to_mongo()
    return result


#Get One Search
@app.route('/customersearches/getonesearch/<search_id>', methods=['GET'])
@login_required
def getonesearch(search_id):
    search = CustomerSearches.from_mongo(search_id)
    return json.dumps(search,default=json_util.default)


#Get All Searches of Customer
@app.route('/customersearches/getallsearchesofcustomer',methods=['GET'])
@login_required
def getallsearchesofcustomer():
    searches = CustomerSearches.from_mongo_all_searches_of_customer(current_user.customer_id)
    return json.dumps(searches,default=json_util.default)


#Get All Searches
@app.route('/customersearches/getallsearches',methods=['GET'])
@login_required
def getallsearches():
    searches = CustomerSearches.from_mongo_all_searches()
    return json.dumps(searches,default = json_util.default)


##########################################################################
#User Guidance API's
##########################################################################


#Add User guidance
@app.route('/userguidances/adduserguidance', methods=['POST'])
@login_required
def adduserguidance():
    response = UserGuidance.from_mongo_by_name(request.get_json()['guidance_name'])
    if response is None:
        userguidance = UserGuidance(request.get_json()['guidance_name'],
            request.get_json()['video_url'],
            request.get_json()['for_user'])
        result = userguidance.save_to_mongo()
        return result
    else:
        return 'Already Exists!'


#Update User guidance
@app.route('/userguidances/updateuserguidance',methods=['POST'])
@login_required
def updateuserguidance():
    update = {"$set":{'guidance_name': request.get_json()['guidance_name'],
        'video_url': request.get_json()['video_url'],
        'for_user': request.get_json()['for_user']
    }}
    UserGuidance.from_mongo_update(request.get_json()['guidance_id'],update)
    result = jsonify({"result":"User Guidance Updated"})
    return result


#Delete User guidance
@app.route('/userguidances/deleteuserguidance',methods=['POST'])
@login_required
def deleteuserguidance():
    UserGuidance.from_mongo_delete(request.get_json()['guidance_id'])
    result =  'Complaint Category deleted!'
    return result


#Get User guidance
@app.route('/userguidances/getoneuserguidance/<guidance_id>', methods=['GET'])
@login_required
def getoneuserguidance(guidance_id):
    userguidance = list(UserGuidance.from_mongo(guidance_id))
    return json.dumps(userguidance,default=json_util.default)


#Get All User guidance of Customer
@app.route('/userguidances/getalluserguidanceforcustomer',methods=['GET'])
@login_required
def getalluserguidanceforcustomer():
    userguidances = UserGuidance.from_mongo_all_guidance_for_customer()
    return json.dumps(userguidances,default=json_util.default)


#Get All User guidance of Employee
@app.route('/userguidances/getalluserguidanceforemployee',methods=['GET'])
@login_required
def getalluserguidanceforemployee():
    userguidances = UserGuidance.from_mongo_all_guidance_for_employee()
    return json.dumps(userguidances,default = json_util.default)


#Get All User guidance
@app.route('/userguidances/getalluserguidance',methods=['GET'])
@login_required
def getalluserguidance():
    userguidances = UserGuidance.from_mongo_all_guidance()
    return json.dumps(userguidances,default = json_util.default)


#For production recommendation
def sales():
    sales = list(Cart.from_mongo_get_all_cart())
    Customer_First_Name = []
    Customer_Last_Name = []
    Customer_Email = []
    Customer_Phone_Number = []
    Customer_Age = []
    Customer_Gender = []
    Customer_City = []
    Customer_Username = []
    Customer_Id = []
    Customer_No = []
    Product_Id = []
    Product_No = []
    Product_Name = []
    Product_Description = []
    Product_Price = []
    Product_Quantity = []
    Category_Id = []
    Category_Name = []
    Category_Description = []
    Subcategory_Id = []
    Subcategory_Name = []
    Subcategory_Description = []
    Total_Bill = []

    for x in sales:
        for y in x['products']:
            customer_res = Customer.from_mongo_by_id(x['customer_id'])
            if customer_res is not None:
                Customer_First_Name.append(customer_res['first_name'])
                Customer_Last_Name.append(customer_res['last_name'])
                Customer_Email.append(customer_res['email'])
                Customer_Phone_Number.append(customer_res['phonenumber'])
                Customer_Age.append(int(customer_res['age']))
                Customer_Gender.append(customer_res['gender'])
                Customer_City.append(customer_res['city'])
                Customer_Username.append(customer_res['username'])
                Customer_Id.append(customer_res['customer_id'])
                cust = Customer_ids.from_mongo(customer_res['customer_id'])
                Customer_No.append(cust['number'])
                product_res = Product.from_mongo(y['product_id'])
                Product_Id.append(product_res['product_id'])
                prod = Product_ids.from_mongo(product_res['product_id'])
                Product_No.append(prod['number'])
                Product_Name.append(product_res['product_name'])
                Product_Description.append(product_res['description'])
                Product_Price.append(product_res['price'])
                Product_Quantity.append(int(y['product_quantity']))
                category_res = Category.from_mongo(product_res['category_id'])
                Category_Id.append(category_res['category_id'])
                Category_Name.append(category_res['category_name'])
                Category_Description.append(category_res['description'])
                subcategory_res = Subcategory.from_mongo_by_id(product_res['subcategory_id'])
                Subcategory_Id.append(subcategory_res['subcategory_id'])
                Subcategory_Name.append(subcategory_res['subcategory_name'])
                Subcategory_Description.append(subcategory_res['description'])
                Total_Bill.append(int(x['total_bill']))

    cart = Cart.from_mongo_all_cart_of_customer(current_user.customer_id)
    if cart is None:
        Customer_Age.append(int(current_user.age))
        Customer_Gender.append(current_user.gender)
        Customer_City.append(current_user.city)
        cust_idid = Customer_ids.from_mongo(current_user.customer_id)
        Customer_No.append(cust_idid['number'])
        Product_No.append(0)
        Product_Price.append(0)
        Product_Quantity.append(0)
        Total_Bill.append(0)
    print(len(Customer_No))
    print(len(Product_No))
    print(len(Total_Bill))

    Sales = {'Customer_Age': Customer_Age,
            'Customer_Gender': Customer_Gender,
            'Customer_City': Customer_City,
            'Customer_No': Customer_No,
            'Product_No': Product_No,
            'Product_Price': Product_Price,
            'Product_Quantity': Product_Quantity,
            'Total_Bill': Total_Bill
        }
    df = DataFrame(Sales, columns=['Customer_Age','Customer_Gender','Customer_City','Customer_No',
                    'Product_No','Product_Price','Product_Quantity',
                    'Total_Bill'])
    return df



if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0')