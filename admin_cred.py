from pymongo import MongoClient

client = MongoClient("mongodb+srv://admin:nikhil@cluster0.yjnzzzx.mongodb.net/")
db = client['cazu_services']
admins_col = db['admins']

admins_col.insert_one({'username': 'admin', 'password': 'admin123'})
print("Admin account created.")
