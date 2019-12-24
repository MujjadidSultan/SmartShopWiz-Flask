from schema import Schema,And,Use, Optional
from datetime import datetime

employeeschema = Schema([{'first_name': And(str, len),
    'last_name': And(str, len),
    'email': And(str, len),
    'password': And(str, len),
    'phonenumber': And(Use(int), lambda n: 3000000000 <= n <= 99999999999),
    'age': And(Use(int), lambda n: 0 <= n <= 99),
    Optional('gender'): And(str, lambda s: s in ('Male', 'Female')),
    'address': {'houseno':And(str, len),'streetno':And(str, len),'area':And(str, len),'city':And(str, len)},
    'city': And(str,len),
    'date': datetime,
    'role': And(str, len),
    'verification_code': And(Use(int), lambda n: 1111 <= n <= 9999),
    'employeeID': And(str, len),
    'cnic': And(Use(int), lambda n: 1000000000000 <= n <= 9999999999999),
    'hiring_date':datetime,
    'status': And(str, len)
}])

customerschema = Schema([{'first_name': And(str, len),
    'last_name': And(str, len),
    'email': And(str, len),
    'password': And(str, len),
    'phonenumber': And(Use(int), lambda n: 3000000000 <= n <= 99999999999), 
    'age': And(Use(int), lambda n: 0 <= n <= 99),
    Optional('gender'): And(str, lambda s: s in ('Male', 'Female')),
    'address': {'houseno':And(str, len),'streetno':And(str, len),'area':And(str, len),'city':And(str, len)},
    'city': And(str,len),
    'date': datetime,
    'role': And(str, len),
    'verification_code': And(Use(int), lambda n: 1111 <= n <= 9999),
    'username': And(str, len),
    'customer_id': And(str , len)   
}])

productschema = Schema([{'product_id': And(str, len),
    'product_name': And(str, len),
    'product_image': And(str, len),
    'price': And(Use(int), lambda n:0 <= 9999999999),
    'description': And(str, len),
    'status': And(str, lambda s: s in ('Available', 'NotAvailable')), 
    'expiring_date': datetime,
    'manufacture_date': datetime,
    'category_id': And(str, len),
    'subcategory_id': And(str, len),
    'rating': And(Use(int), lambda n:0 <= 5)    
}])

categoryschema = Schema([{'category_id': And(str, len),
    'category_name': And(str, len),
    'description': And(str, len),
    'category_image': And(str, len)
}])

subcategoryschema = Schema([{'subcategory_id': And(str, len),
    'subcategory_name': And(str, len),
    'description': And(str, len),
    'category_id': And(str, len)
}])

inventoryschema = Schema([{'product_id': And(str, len),
    'quantity': And(Use(int), lambda n:0 <= 100)
}])

supplierschema = Schema([{'supplier_id': And(str,len),
    'supplier_name': And(str,len),
    'supplier_quantity': And(Use(int), lambda n:0 <= 99),
    'supplying_date': datetime,
    'product_id': And(str,len)
}])

cartschema = Schema([{'cart_id': And(str,len),
    'products': [{'product_id': And(str, len),'product_quantity': And(str, len)}],
    'total_bill': And(Use(int), lambda  n:0 <= 999999999),
    'customer_id': And(str,len),
    'date': datetime,
    'status': And(str, lambda s: s in ('Confirmed', 'Not Confirmed'))
}])

reservedproductschema = Schema([{'reservation_id': And(str, len),
    'product_id': And(str,len),
    'customer_id': And(str,len),
    'reserved_quantity': And(Use(int),lambda n:0 <= 99),
    'reserved_time': And(Use(int),lambda n:0 <= 60),
    'reservation_date': datetime,
    'status': And(str, len)
}])

invoiceschema = Schema([{'invoice_id': And(str,len),
    'cart_id': And(str,len),
    'bill': And(Use(int),lambda n:0 <= 999999999),
    'given_cash': And(Use(int),lambda n:0 <= 999999999),
    'returned_cash': And(Use(int),lambda n:0 <= 999999999)
}])

reviewsschema =Schema([{'review_id': And(str,len),
    'customer_id': And(str,len),
    'cart_id': And(str,len),
    'review': And(str,len),
    'review_datetime': datetime
}])

notificationschema =Schema([{'notification_id':And(str,len),
    'from_user_id': And(str,len),
    'title': And(str,len),
    'message': And(str,len),
    'url': And(str,len),
    'read_status': And(str,len),
    'delivery_status': And(str,len),
    'to_user_id': And(str,len)    
}])

ticketsschema = Schema([{'ticket_id': And(str,len),
    'complaint_id': And(str,len),
    'date': datetime,
    'employee_id': And(str,len),
    'customer_id': And(str,len),
    'complaint': And(str,len),
    'status': And(str,len),
    'receive_status': And(str,len)
}])

tickets_responseschema = Schema([{'res_ticket_id':And(str,len),
    'ticket_id': And(str,len),
    'from_user_id': And(str,len),
    'to_user_id': And(str,len),
    'message': And(str,len),
    'date':datetime
}])

tickets_feedbackschema = Schema([{'ticket_id':And(str,len),
    'feedback': And(str,len),
    'status': And(str,len),
    'date': datetime
}])

roleschema = Schema([{'role_id':And(str,len),
    'role_name':And(str,len)
}])

productratingschema = Schema([{'product_id':And(str,len),
    'customer_id':And(str,len),
    'rating': And(Use(int),lambda n: 1 <= 5)
}])

complaintcategoryschema = Schema([{'complaint_id':And(str,len),
    'complaint_name':And(str,len)
}])

userguidanceschema = Schema([{'guidance_id': And(str,len),
    'guidance_name': And(str,len),
    'video_url': And(str,len),
    'for_user': And(str,len)
}])

customersearchesschema = Schema([{'search_id': And(str,len),
    'customer_id': And(str,len),
    'search': And(str,len),
    'date': datetime
}])

devicetokenschema = Schema([{'devicetoken_id': And(str,len),
    'user_id': And(str,len),
    'device_id': And(str,len),
    'datetime': datetime
}])

product_idsschema = Schema([{'product_id':And(str,len),
    'number':And(Use(int),lambda n:0 <= 999999999)
}])

customer_idsschema = Schema([{'customer_id':And(str,len),
    'number':And(Use(int),lambda n:0 <= 999999999)
}])