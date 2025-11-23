from ..models.task import Task
from ..services.ai_service import generate_task_summary
# 💡 NEW IMPORT: Import the subtask model's function
from ..models.subtask import Subtask 

def create_task(title, description, priority, tags, due_date, status, user_id):
# ... (Rest of function remains the same)
    new_task = Task(title, description, priority, tags, due_date, status, user_id)
    new_task.save()
    return {'message': 'Task created successfully'}, 201

def get_user_tasks(user_id):
# ... (Rest of function remains the same)
    tasks = Task.find_by_user_id(user_id)
    # Convert ObjectId to string for JSON serialization
    for task in tasks:
        task['_id'] = str(task['_id'])
        task['created_at'] = task['created_at'].isoformat() if task['created_at'] else None
        task['updated_at'] = task['updated_at'].isoformat() if task['updated_at'] else None
    return tasks

def get_task_by_id(task_id):
    task = Task.find_by_id(task_id)
    if task:
        task['_id'] = str(task['_id'])
        task['created_at'] = task['created_at'].isoformat() if task['created_at'] else None
        task['updated_at'] = task['updated_at'].isoformat() if task['updated_at'] else None
    return task

def update_task(task_id, update_data):
# ... (Rest of function remains the same)
    result = Task.update_task(task_id, update_data)
    if result.modified_count > 0:
        return {'message': 'Task updated successfully'}, 200
    return {'error': 'Task not found'}, 404

def delete_task(task_id):
    # 💡 CRITICAL FIX: Delete associated subtasks first
    Subtask.delete_by_parent_id(task_id)
    
    result = Task.delete_task(task_id)
    if result.deleted_count > 0:
        return {'message': 'Task deleted successfully'}, 200
    return {'error': 'Task not found'}, 404
    
def mark_task_completed(task_id):
    return update_task(task_id, {'status': 'Completed'})

def get_alert_tasks(user_id):
# ... (Rest of function remains the same)
    from datetime import datetime, date
    
    all_tasks = get_user_tasks(user_id)
    
    today = date.today()
    # ... (Rest of function remains the same)
    
    overdue_tasks = []
    due_today_tasks = []
    high_priority_tasks = []
    
    for task in all_tasks:
        # Skip completed tasks
        if task['status'] == 'Completed':
            continue
            
        # Check for overdue tasks
        if task['due_date']:
            due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
            if due_date < today:
                overdue_tasks.append(task)
            elif due_date == today:
                due_today_tasks.append(task)
        
        # Check for high priority tasks
        if task['priority'] == 'High':
            high_priority_tasks.append(task)
    
    return {
        'overdueTasks': overdue_tasks,
        'dueTodayTasks': due_today_tasks,
        'highPriorityTasks': high_priority_tasks
    }