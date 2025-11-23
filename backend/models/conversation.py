from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from ..config import Config

# Connect to the same database (Assuming config.py and MongoDB are running)
client = MongoClient(Config.MONGO_URI)
db = client.get_default_database()

class Conversation:
    def __init__(self, user_id, initial_message, role='user'):
        self.user_id = user_id
        self.history = [{'role': role, 'content': initial_message, 'timestamp': datetime.now()}]
        self.created_at = datetime.now()

    def save(self):
        conversation_data = {
            'user_id': self.user_id,
            'history': self.history,
            'created_at': self.created_at,
        }
        return db.conversations.insert_one(conversation_data)

    @staticmethod
    def find_by_user_id(user_id):
        """Finds the *most recent* conversation for a user."""
        return list(db.conversations.find({'user_id': user_id}).sort('created_at', -1).limit(1))

    @staticmethod
    def append_message(conversation_id, role, content):
        """Appends a new user or assistant message to the history."""
        new_message = {'role': role, 'content': content, 'timestamp': datetime.now()}
        return db.conversations.update_one(
            {'_id': ObjectId(conversation_id)},
            {
                '$push': {'history': new_message},
                '$set': {'updated_at': datetime.now()}
            }
        )
    
    @classmethod
    def delete_by_user_id(cls, user_id):
        """Deletes all conversation history documents for a given user ID (for New Session)."""
        db.conversations.delete_many({'user_id': user_id})
        # Note: Removed print statement for production readiness