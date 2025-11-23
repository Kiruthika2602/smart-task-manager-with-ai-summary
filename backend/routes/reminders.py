from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.reminder_service import (
    add_reminder, 
    get_user_reminders, 
    dismiss_reminder,
    get_triggered_reminders # 💡 ADDED IMPORT for the Alerts page
)

reminder_bp = Blueprint('reminders', __name__)

@reminder_bp.route('/reminders', methods=['POST'])
@jwt_required()
def create_reminder_route():
    """Endpoint to create a new reminder."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    task_id = data.get('task_id') # Optional for general reminders
    trigger_value = data.get('trigger_value') # Absolute datetime or relative hours
    message = data.get('message')
    reminder_type = data.get('reminder_type', 'Absolute')
    
    if not trigger_value:
        return jsonify({'error': 'Trigger time/value is required'}), 400
        
    response, status_code = add_reminder(
        user_id, task_id, trigger_value, message, reminder_type
    )
    return jsonify(response), status_code

@reminder_bp.route('/reminders', methods=['GET'])
@jwt_required()
def get_reminders_route():
    """Endpoint to get all reminders for the current user (for the Reminders page)."""
    user_id = get_jwt_identity()
    reminders = get_user_reminders(user_id)
    return jsonify({'reminders': reminders}), 200

@reminder_bp.route('/reminders/<reminder_id>/dismiss', methods=['POST'])
@jwt_required()
def dismiss_reminder_route(reminder_id):
    """Endpoint to dismiss a triggered reminder."""
    response, status_code = dismiss_reminder(reminder_id)
    return jsonify(response), status_code

@reminder_bp.route('/reminders/triggered', methods=['GET'])
@jwt_required()
def get_triggered_reminders_route():
    """💡 NEW: Endpoint to get all TRIGGERED (active) reminders for the Alerts page."""
    user_id = get_jwt_identity()
    reminders = get_triggered_reminders(user_id)
    return jsonify({'reminders': reminders}), 200