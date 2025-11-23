from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.task_service import (
    create_task, get_user_tasks, get_task_by_id, 
    update_task, delete_task, mark_task_completed, get_alert_tasks
)

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks', methods=['POST'])
@jwt_required()
def add_task():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    title = data.get('title')
    description = data.get('description')
    priority = data.get('priority', 'Medium')
    tags = data.get('tags', [])
    due_date = data.get('due_date')
    status = data.get('status', 'Pending')
    
    if not title or not description:
        return jsonify({'error': 'Title and description are required'}), 400
    
    response, status_code = create_task(
        title, description, priority, tags, due_date, status, user_id
    )
    return jsonify(response), status_code

@tasks_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    tasks = get_user_tasks(user_id)
    return jsonify({'tasks': tasks}), 200

@tasks_bp.route('/tasks/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    user_id = get_jwt_identity()
    alert_tasks = get_alert_tasks(user_id)
    return jsonify(alert_tasks), 200

@tasks_bp.route('/tasks/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    task = get_task_by_id(task_id)
    if task:
        return jsonify({'task': task}), 200
    return jsonify({'error': 'Task not found'}), 404

@tasks_bp.route('/tasks/<task_id>', methods=['PUT'])
@jwt_required()
def update_task_route(task_id):
    data = request.get_json()
    response, status_code = update_task(task_id, data)
    return jsonify(response), status_code

@tasks_bp.route('/tasks/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task_route(task_id):
    response, status_code = delete_task(task_id)
    return jsonify(response), status_code

@tasks_bp.route('/tasks/<task_id>/complete', methods=['POST'])
@jwt_required()
def complete_task(task_id):
    response, status_code = mark_task_completed(task_id)
    return jsonify(response), status_code