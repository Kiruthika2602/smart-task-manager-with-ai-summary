from flask import Blueprint, request, jsonify, render_template # Note: render_template is used for the assistant page if in this file
from flask_jwt_extended import jwt_required, get_jwt_identity

# Import services
from ..services.ai_service import (
    generate_task_summary, 
    generate_detailed_summary, 
    get_priority_ranking
)
from ..services.task_service import get_task_by_id, update_task
from ..services.subtask_service import generate_subtasks_only

# Import the Conversation model (if used by the assistant page route, which is often in app.py or a different blueprint)
from ..models.conversation import Conversation 

ai_bp = Blueprint('ai', __name__)

# --- 1. Summarize (Concise) ---
@ai_bp.route('/ai/summarize', methods=['POST'])
@jwt_required()
def summarize_task():
    data = request.get_json()
    task_id = data.get('task_id')
    description = data.get('description')
    
    if not description:
        return jsonify({'error': 'Task description is required'}), 400
    
    summary = generate_task_summary(description)
    
    if summary.startswith("Error:") or summary.startswith("API key not configured"):
        return jsonify({'error': summary}), 500
    
    if task_id and task_id != 'temp':
        task = get_task_by_id(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        update_task(task_id, {'summary': summary})
    
    return jsonify({'summary': summary}), 200

# --- 2. Summarize (Detailed/Point-Form) ---
@ai_bp.route('/ai/summarize-detailed', methods=['POST'])
@jwt_required()
def summarize_task_detailed():
    data = request.get_json()
    description = data.get('description')
    
    if not description:
        return jsonify({'error': 'Task description is required'}), 400
    
    summary_points = generate_detailed_summary(description)
    
    if len(summary_points) == 1 and (summary_points[0].startswith("Error:") or summary_points[0].startswith("API key not configured")):
        return jsonify({'error': summary_points[0]}), 500
    
    return jsonify({'summary': summary_points}), 200

# --- 3. Subtask Generation (Sandbox/No DB Save) ---
@ai_bp.route('/ai/generate-subtasks-only', methods=['POST'])
@jwt_required()
def generate_subtasks_sandbox():
    data = request.get_json()
    description = data.get('description')
    
    if not description:
        return jsonify({'error': 'Task description is required'}), 400
        
    response, status_code = generate_subtasks_only(description, get_jwt_identity())
    
    return jsonify(response), status_code

# --- 4. Intelligent Task Prioritization (DEFINED ONCE) ---
@ai_bp.route('/ai/prioritize', methods=['POST'])
@jwt_required()
def prioritize_tasks_route():
    """Endpoint to send user's tasks to AI for priority ranking."""
    data = request.get_json()
    tasks_data = data.get('tasks') 
    
    if not tasks_data or not isinstance(tasks_data, list):
        return jsonify({'error': 'A list of tasks is required for prioritization'}), 400
    
    response, status_code = get_priority_ranking(tasks_data)
    
    if 'error' in response:
        return jsonify({'error': response['error']}), status_code

    return jsonify({'ranking_markdown': response['ranking_markdown'], 'message': response['message']}), status_code

# --- Note: The assistant route is typically handled in a separate blueprint. ---
# If you have assistant routes defined here, they may cause other conflicts.
# Assuming the main rendering route is in app.py and API calls are in assistant.py.