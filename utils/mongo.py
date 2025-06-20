from pymongo import MongoClient

client = MongoClient('mongodb+srv://admin:nikhil@cluster0.yjnzzzx.mongodb.net/')
db = client['cazu_services']

users_col = db['users']
admins_col = db['admins']
bookings_col = db['bookings']
