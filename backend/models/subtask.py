from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from ..config import Config

# Connect to the same database
client = MongoClient(Config.MONGO_URI)
db = client.get_default_database()

class Subtask:
    def __init__(self, parent_task_id, title, description, user_id, status='Pending'):
        self.parent_task_id = parent_task_id
        self.title = title
        self.description = description
        self.user_id = user_id
        self.status = status
        self.created_at = datetime.now()
        self.completed_at = None

    def save(self):
        subtask_data = {
            'parent_task_id': ObjectId(self.parent_task_id),
            'title': self.title,
            'description': self.description,
            'user_id': self.user_id,
            'status': self.status,
            'created_at': self.created_at,
            'completed_at': self.completed_at
        }
        return db.subtasks.insert_one(subtask_data)

    @staticmethod
    def find_by_parent_id(parent_task_id):
        return list(db.subtasks.find({'parent_task_id': ObjectId(parent_task_id)}).sort('created_at', 1))

    @staticmethod
    def update_status(subtask_id, status):
        update_data = {'status': status}
        if status == 'Completed':
            update_data['completed_at'] = datetime.now()
        else:
            update_data['completed_at'] = None
            
        return db.subtasks.update_one(
            {'_id': ObjectId(subtask_id)},
            {'$set': update_data}
        )

    @staticmethod
    def delete_by_id(subtask_id):
        return db.subtasks.delete_one({'_id': ObjectId(subtask_id)})

    @staticmethod
    def delete_by_parent_id(parent_task_id):
        # Useful for cleaning up subtasks when the parent task is deleted
        return db.subtasks.delete_many({'parent_task_id': ObjectId(parent_task_id)})