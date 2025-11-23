from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from ..config import Config

client = MongoClient(Config.MONGO_URI)
db = client.get_default_database()

class Task:
    def __init__(self, title, description, priority, tags, due_date, status, user_id, summary=None):
        self.title = title
        self.description = description
        self.priority = priority
        self.tags = tags
        self.due_date = due_date
        self.status = status
        self.user_id = user_id
        self.summary = summary  # Added summary parameter
        self.created_at = datetime.now()
        self.updated_at = None
    
    def save(self):
        task_data = {
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'tags': self.tags,
            'due_date': self.due_date,
            'status': self.status,
            'user_id': self.user_id,
            'summary': self.summary,  # Added summary to task data
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        return db.tasks.insert_one(task_data)
    
    @staticmethod
    def find_by_user_id(user_id):
        return list(db.tasks.find({'user_id': user_id}))
    
    @staticmethod
    def find_by_id(task_id):
        return db.tasks.find_one({'_id': ObjectId(task_id)})
    
    @staticmethod
    def update_task(task_id, update_data):
        update_data['updated_at'] = datetime.now()
        return db.tasks.update_one(
            {'_id': ObjectId(task_id)},
            {'$set': update_data}
        )
    
    @staticmethod
    def delete_task(task_id):
        return db.tasks.delete_one({'_id': ObjectId(task_id)})