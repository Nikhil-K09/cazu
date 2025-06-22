# utils/mongo.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()  # Load variables from .env

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)

db = client["cazu_services"]  # Replace with your actual DB name if different
users_col = db["users"]
admins_col = db["admins"]
bookings_col = db["bookings"]
