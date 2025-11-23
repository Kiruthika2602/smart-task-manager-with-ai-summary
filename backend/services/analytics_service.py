from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from bson.objectid import ObjectId
from ..config import Config

# Establish a connection point
client = MongoClient(Config.MONGO_URI)
db = client.get_default_database()
tasks_col = db.tasks

# Helper function to build user filter for safety
def _build_user_filter(user_id):
    """Return a robust MongoDB filter matching user_id."""
    ors = [{'user_id': user_id}]
    try:
        from bson.objectid import ObjectId
        # Check if user_id might be stored as ObjectId
        if len(str(user_id)) == 24:
            ors.append({'user_id': ObjectId(str(user_id))})
    except Exception:
        pass
    return {'$or': ors}

# Helper to map raw date/time fields to a consistent Python datetime object
def _get_datetime(doc, field):
    """Safely retrieve and normalize a datetime field."""
    dt = doc.get(field)
    if isinstance(dt, datetime):
        return dt.replace(tzinfo=None) # Ensure naive datetime for consistency
    return None

def get_core_metrics(user_id):
    """
    Return core KPIs: totalTasks, completedTasks, pendingTasks, completionRate.
    (Removed Avg Completion Time Calculation)
    """
    user_filter = _build_user_filter(user_id)
    
    total_tasks = tasks_col.count_documents(user_filter)
    completed_tasks = tasks_col.count_documents({'$and': [user_filter, {'status': {'$in': ['Completed', 'COMPLETED', 'completed']}}]})
    
    completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0
    pending_tasks = total_tasks - completed_tasks

    return {
        'totalTasks': int(total_tasks),
        'completedTasks': int(completed_tasks),
        'pendingTasks': int(pending_tasks),
        'completionRate': completion_rate
        # 'avgCompletionTimeDays' removed
    }

def get_priority_distribution(user_id):
    """
    Returns counts of active (non-completed) tasks grouped by priority.
    """
    user_filter = _build_user_filter(user_id)
    pipeline = [
        {'$match': {'$and': [user_filter, {'status': {'$nin': ['Completed', 'completed', 'COMPLETED']}}]}},
        {'$group': {'_id': {'$ifNull': ['$priority', 'Medium']}, 'count': {'$sum': 1}}}
    ]
    agg = list(tasks_col.aggregate(pipeline))
    result = {'High': 0, 'Medium': 0, 'Low': 0}
    for row in agg:
        key = str(row.get('_id')).capitalize()
        if key in result:
            result[key] = int(row.get('count', 0))
    return result

def get_weekly_completion_trend(user_id, days=7):
    """
    Returns list of {'date': 'YYYY-MM-DD', 'count': N} for last `days` days.
    """
    user_filter = _build_user_filter(user_id)
    today_utc = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_utc = today_utc - timedelta(days=days - 1)
    
    pipeline = [
        {'$match': {
            '$and': [user_filter, {'status': {'$in': ['Completed', 'completed', 'COMPLETED']}}],
            'updated_at': {'$gte': start_utc} 
        }},
        {'$group': {
            '_id': {'$dateToString': {'format': "%Y-%m-%d", 'date': '$updated_at'}},
            'count': {'$sum': 1}
        }},
        {'$sort': {'_id': 1}}
    ]
    
    result = list(tasks_col.aggregate(pipeline))
    date_counts = {item['_id']: item['count'] for item in result}
    
    trend_data = []
    for i in range(days):
        date = today_utc - timedelta(days=days - 1 - i)
        date_str = date.strftime("%Y-%m-%d")
        
        trend_data.append({
            'date': date.strftime("%b %d"),
            'count': date_counts.get(date_str, 0)
        })
        
    return trend_data


def get_day_of_week_activity(user_id, days=30):
    """
    Return activity counts aggregated by weekday for last `days` days.
    """
    user_filter = _build_user_filter(user_id)
    today_utc = datetime.utcnow()
    start_utc = today_utc - timedelta(days=days)
    
    pipeline = [
        {'$match': {
            '$and': [user_filter, {'$or': [{'created_at': {'$gte': start_utc}}, {'updated_at': {'$gte': start_utc}}]}]
        }},
        {'$project': {
            'dayOfWeek': {'$dayOfWeek': {'$ifNull': ['$updated_at', '$created_at']}} # 1=Sunday, 7=Saturday
        }},
        {'$group': {
            '_id': '$dayOfWeek',
            'count': {'$sum': 1}
        }}
    ]

    agg = list(tasks_col.aggregate(pipeline))
    
    labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    dow_counts = {labels[i]: 0 for i in range(7)}
    
    for row in agg:
        day_index = row['_id'] - 1 
        dow_counts[labels[day_index]] = int(row['count'])
        
    # Reorder starting from Monday
    reordered_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    return {label: dow_counts[label] for label in reordered_labels}