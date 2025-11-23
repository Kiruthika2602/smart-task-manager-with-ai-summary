from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.subtask_service import (
    get_subtasks_for_task, generate_subtasks_with_ai, 
    mark_subtask_status, delete_subtask, create_subtask_manual
)
from ..services.task_service import get_task_by_id # Used for task existence check

subtask_bp = Blueprint('subtasks', __name__)

@subtask_bp.route('/tasks/<task_id>/subtasks', methods=['GET'])
@jwt_required()
def get_subtasks(task_id):
    """Fetch all subtasks for a parent task."""
    subtasks = get_subtasks_for_task(task_id)
    return jsonify({'subtasks': subtasks}), 200

@subtask_bp.route('/tasks/<task_id>/subtasks/generate', methods=['POST'])
@jwt_required()
def generate_subtasks(task_id):
    """Trigger AI generation of subtasks for a parent task."""
    user_id = get_jwt_identity()
    
    # 1. Fetch parent task to get the description
    task = get_task_by_id(task_id)
    if not task:
        return jsonify({'error': 'Parent task not found'}), 404
        
    task_description = task.get('description')
    if not task_description:
        return jsonify({'error': 'Task description is empty. Cannot generate subtasks.'}), 400

    # 2. Call the AI service (it handles saving now)
    response, status_code = generate_subtasks_with_ai(task_id, task_description, user_id)
    
    return jsonify(response), status_code

@subtask_bp.route('/subtasks/<subtask_id>/complete', methods=['POST'])
@jwt_required()
def complete_subtask(subtask_id):
    """Mark a subtask as completed."""
    # Assuming the frontend sends status in the body, although the service currently defaults to 'Completed'.
    # For robust REST API, let's read the status from the body if provided.
    data = request.get_json()
    status = data.get('status', 'Completed') 
    return mark_subtask_status(subtask_id, status)

@subtask_bp.route('/subtasks/<subtask_id>', methods=['DELETE'])
@jwt_required()
def remove_subtask(subtask_id):
    """Delete a subtask."""
    return delete_subtask(subtask_id)

@subtask_bp.route('/tasks/<task_id>/subtasks', methods=['POST'])
@jwt_required()
def add_subtask_manual(task_id):
    """Manually add a subtask."""
    user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    
    if not title:
        return jsonify({'error': 'Subtask title is required'}), 400
        
    return create_subtask_manual(task_id, title, user_id, description)