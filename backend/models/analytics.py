# backend/models/analytics.py
from pymongo import MongoClient
from ..config import Config

_client = MongoClient(Config.MONGO_URI)
_db = _client.get_default_database()
_tasks = _db.tasks

class AnalyticsModel:
    @staticmethod
    def tasks_collection():
        return _tasks

    @staticmethod
    def count_total_tasks(user_filter):
        return _tasks.count_documents(user_filter)

    @staticmethod
    def count_completed_tasks(user_filter):
        return _tasks.count_documents({'$and': [user_filter, {'status': {'$in': ['Completed','completed','COMPLETED']}}]})

    @staticmethod
    def count_pending_tasks(user_filter):
        return _tasks.count_documents({'$and': [user_filter, {'status': {'$in': ['Pending','pending','In Progress','in progress','To Do','todo']}}]})

    @staticmethod
    def find_completed_with_times(user_filter, limit=0):
        proj = {'created_at': 1, 'completed_at': 1}
        if limit and isinstance(limit, int) and limit > 0:
            return _tasks.find({'$and': [user_filter, {'status': {'$in': ['Completed','completed','COMPLETED']}}]}, proj).limit(limit)
        return _tasks.find({'$and': [user_filter, {'status': {'$in': ['Completed','completed','COMPLETED']}}]}, proj)

    @staticmethod
    def aggregate_priority_counts(user_filter):
        pipeline = [
            {'$match': {'$and': [user_filter, {'status': {'$nin': ['Completed','completed','COMPLETED']}}]}},
            {'$group': {'_id': {'$ifNull': ['$priority', 'Medium']}, 'count': {'$sum': 1}}}
        ]
        return list(_tasks.aggregate(pipeline))

    @staticmethod
    def find_tasks_activity_since(user_filter, start_date):
        return _tasks.find({'$and': [user_filter, {'$or': [{'created_at': {'$gte': start_date}}, {'updated_at': {'$gte': start_date}}]}]}, {'created_at': 1, 'updated_at': 1})

    @staticmethod
    def raw_find_completed(user_filter, limit=10):
        return list(_tasks.find({'$and': [user_filter, {'status': {'$in': ['Completed','completed','COMPLETED']}}]}, limit=limit))

    @staticmethod
    def insert_task(doc):
        return _tasks.insert_one(doc)
