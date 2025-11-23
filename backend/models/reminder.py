from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from ..config import Config

# Connect to the same database
client = MongoClient(Config.MONGO_URI)
db = client.get_default_database() # <-- This defines the global 'db' object

class Reminder:
    def __init__(self, user_id, task_id, trigger_time, message, reminder_type='Absolute'):
        self.user_id = user_id
        # Note: task_id is stored as a string initially, converted to ObjectId in save
        self.task_id = task_id  
        self.trigger_time = trigger_time  # datetime object for triggering
        self.message = message
        self.reminder_type = reminder_type
        self.status = 'Pending'  # Can be: Pending, Triggered, Dismissed
        self.created_at = datetime.now()

    def save(self):
        # Convert task_id string to ObjectId before saving if it exists
        task_id_obj = ObjectId(self.task_id) if self.task_id else None
        
        reminder_data = {
            'user_id': self.user_id,
            # Store ObjectId or None
            'task_id': task_id_obj, 
            'trigger_time': self.trigger_time,
            'message': self.message,
            'reminder_type': self.reminder_type,
            'status': self.status,
            'created_at': self.created_at
        }
        return db.reminders.insert_one(reminder_data)

    @staticmethod
    def find_by_user_id(user_id):
        """Finds all reminders for a user, sorted by trigger time."""
        # Uses the global 'db' defined above
        return list(db.reminders.find({'user_id': user_id}).sort('trigger_time', 1))

    @staticmethod
    def find_pending_before(time_now):
        """Finds all pending reminders that are due before the current time."""
        # Uses the global 'db' defined above
        return list(db.reminders.find({
            'status': 'Pending',
            'trigger_time': {'$lte': time_now}
        }))

    @staticmethod
    def update_status(reminder_id, new_status):
        """Updates the status of a specific reminder."""
        # Uses the global 'db' defined above
        return db.reminders.update_one(
            {'_id': ObjectId(reminder_id)},
            {'$set': {'status': new_status}}
        )

    @staticmethod
    def delete_by_id(reminder_id):
        """Deletes a reminder by ID."""
        # Uses the global 'db' defined above
        return db.reminders.delete_one({'_id': ObjectId(reminder_id)})