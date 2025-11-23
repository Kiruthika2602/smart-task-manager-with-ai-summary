# routes/assistant.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.assistant_service import generate_assistant_response

assistant_bp = Blueprint('assistant', __name__)

@assistant_bp.route('/assistant/chat', methods=['POST'])
@jwt_required()
def chat_route():
    """Receives a new user message and returns an AI response (stateless)."""
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    response, status_code = generate_assistant_response(user_id, user_message)
    return jsonify(response), status_code

@assistant_bp.route('/assistant/history', methods=['GET'])
@jwt_required()
def get_history_route():
    """Stateless mode: return empty history so the frontend can start fresh."""
    return jsonify({'history': []}), 200

@assistant_bp.route('/assistant/clear-history', methods=['POST'])
@jwt_required()
def clear_history_route():
    """Stateless mode: nothing to clear in DB; just return success."""
    return jsonify({'message': 'Stateless mode: no stored history to clear.'}), 200
