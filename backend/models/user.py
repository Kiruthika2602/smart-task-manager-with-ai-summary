from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from ..config import Config

client = MongoClient(Config.MONGO_URI)
db = client.get_default_database()

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
    
    def save(self):
        user_data = {
            'username': self.username,
            'email': self.email,
            'password': self.password_hash
        }
        return db.users.insert_one(user_data)
    
    @staticmethod
    def find_by_email(email):
        return db.users.find_one({'email': email})
    
    @staticmethod
    def check_password(user, password):
        return check_password_hash(user['password'], password)
    
    @staticmethod
    def find_by_id(user_id):
        return db.users.find_one({'_id': ObjectId(user_id)})