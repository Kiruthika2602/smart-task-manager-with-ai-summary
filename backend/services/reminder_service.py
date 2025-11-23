from datetime import datetime, timedelta
# CRITICAL FIX: Import the database connection 'db' along with the Reminder model.
from ..models.reminder import Reminder, db 
from ..models.task import Task

def calculate_trigger_time(task_id, trigger_value, reminder_type):
    """Calculates the absolute datetime for the reminder trigger."""
    
    # Check if a task is required and exists
    if task_id:
        task = Task.find_by_id(task_id)
        if not task or not task.get('due_date'):
            raise ValueError("Task not found or task has no due date for relative calculation.")
            
        task_due_dt = datetime.strptime(task['due_date'], '%Y-%m-%d')
    else:
        task_due_dt = None # Only used for Absolute reminders without task context
    
    # Handle the reminder time setting
    if reminder_type == 'Absolute':
        # trigger_value is expected to be a datetime string (YYYY-MM-DD HH:MM)
        return datetime.strptime(trigger_value, '%Y-%m-%dT%H:%M')
        
    elif reminder_type == 'Relative_Hours_Before':
        # trigger_value is hours (e.g., '24')
        hours = int(trigger_value)
        # Assuming due date is midnight on the due date, we must use a placeholder time if not available
        # We will assume a default due time if not explicitly handled in task_form
        if not task_due_dt:
             raise ValueError("Relative reminder requires an associated task with a due date.")
             
        # For simplicity, let's assume the deadline is 5 PM on the due date if no time is specified in the task (for now)
        due_dt = datetime.strptime(task['due_date'], '%Y-%m-%d') + timedelta(hours=17) # 5 PM
        return due_dt - timedelta(hours=hours)

    else: # Default/Error case
        raise ValueError(f"Invalid reminder type: {reminder_type}")


def add_reminder(user_id, task_id, trigger_value, message, reminder_type='Absolute'):
    """Creates and saves a new reminder."""
    try:
        if reminder_type == 'Absolute' and not task_id:
            # Absolute reminder not tied to a task, trigger_value is the full datetime
            final_trigger_time = calculate_trigger_time(None, trigger_value, reminder_type)
            message = message or f"General reminder set for {final_trigger_time.strftime('%Y-%m-%d %H:%M')}."
            
        elif reminder_type == 'Absolute' and task_id:
             # Absolute reminder tied to a task (user overrides the default task reminder)
            final_trigger_time = calculate_trigger_time(None, trigger_value, reminder_type)
            task = Task.find_by_id(task_id)
            message = message or f"Reminder for task: {task['title']} set for {final_trigger_time.strftime('%Y-%m-%d %H:%M')}."
            
        elif reminder_type.startswith('Relative') and task_id:
            # Relative reminder tied to a task
            final_trigger_time = calculate_trigger_time(task_id, trigger_value, reminder_type)
            task = Task.find_by_id(task_id)
            message = message or f"Reminder for task: {task['title']}, {trigger_value} hours before deadline."
        
        else:
             raise ValueError("Missing necessary parameters for reminder calculation.")
             
        
        new_reminder = Reminder(
            user_id=user_id,
            task_id=task_id if task_id else None, # Store ObjectId or None if General
            trigger_time=final_trigger_time,
            message=message,
            reminder_type=reminder_type
        )
        new_reminder.save()
        return {'message': 'Reminder set successfully'}, 201

    except ValueError as e:
        return {'error': str(e)}, 400
    except Exception as e:
        return {'error': f"Internal server error: {e}"}, 500

def get_user_reminders(user_id):
    """Fetches all reminders for a user and formats them."""
    reminders = Reminder.find_by_user_id(user_id)
    
    # Format for JSON
    for reminder in reminders:
        reminder['_id'] = str(reminder['_id'])
        if reminder.get('task_id'):
            reminder['task_id'] = str(reminder['task_id'])
            
        reminder['trigger_time'] = reminder['trigger_time'].isoformat()
        reminder['created_at'] = reminder['created_at'].isoformat()
        
    return reminders

def dismiss_reminder(reminder_id):
    """Marks a reminder as dismissed."""
    result = Reminder.update_status(reminder_id, 'Dismissed')
    if result.modified_count > 0:
        return {'message': 'Reminder dismissed'}, 200
    return {'error': 'Reminder not found'}, 404

def get_triggered_reminders(user_id):
    """Fetches all reminders marked as Triggered for the Alerts page."""
    # The 'db' variable is now correctly imported from the Reminder model.
    reminders = db.reminders.find({ 
        'user_id': user_id, 
        'status': 'Triggered'
    }).sort('trigger_time', 1)
    
    # Format for JSON
    formatted_reminders = []
    for reminder in reminders:
        reminder['_id'] = str(reminder['_id'])
        if reminder.get('task_id'):
            reminder['task_id'] = str(reminder['task_id'])
        reminder['trigger_time'] = reminder['trigger_time'].isoformat()
        formatted_reminders.append(reminder)
        
    return formatted_reminders
    
# --- Background Processor Logic ---

def check_and_trigger_reminders():
    """
    Checks the database for pending reminders that are past due
    and updates their status to 'Triggered'.
    """
    now = datetime.now()
    due_reminders = Reminder.find_pending_before(now)
    
    triggered_count = 0
    for reminder in due_reminders:
        try:
            # Mark the reminder as triggered
            Reminder.update_status(str(reminder['_id']), 'Triggered')
            triggered_count += 1
            # print(f"Reminder triggered: ID {reminder['_id']}, Task ID {reminder['task_id']}") # Logging handled by scheduler.py
        except Exception as e:
            # print(f"Error triggering reminder {reminder['_id']}: {e}") # Logging handled by scheduler.py
            pass
            
    return triggered_count