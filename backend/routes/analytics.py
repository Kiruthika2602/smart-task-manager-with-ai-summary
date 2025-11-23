from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.analytics_service import (
    get_core_metrics,
    get_priority_distribution,
    get_weekly_completion_trend,
    get_day_of_week_activity # 💡 NEW IMPORT
)

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/metrics', methods=['GET'])
@jwt_required()
def get_metrics_route():
    """Fetches core KPIs: Total, Completed, Rate, Avg Time."""
    user_id = get_jwt_identity()
    metrics = get_core_metrics(user_id)
    return jsonify(metrics), 200

@analytics_bp.route('/analytics/distribution', methods=['GET'])
@jwt_required()
def get_distribution_route():
    """Fetches tasks grouped by Priority."""
    user_id = get_jwt_identity()
    priority_dist = get_priority_distribution(user_id)
    return jsonify({'priorityDistribution': priority_dist}), 200

@analytics_bp.route('/analytics/trends', methods=['GET'])
@jwt_required()
def get_trends_route():
    """Fetches task completion counts over the last 7 days."""
    user_id = get_jwt_identity()
    trends = get_weekly_completion_trend(user_id)
    return jsonify({'completionTrends': trends}), 200

@analytics_bp.route('/analytics/activity', methods=['GET']) # 💡 NEW ROUTE
@jwt_required()
def get_activity_route():
    """Fetches Day-of-Week activity for the heatmap/bar chart."""
    user_id = get_jwt_identity()
    activity = get_day_of_week_activity(user_id)
    return jsonify({'dayOfWeekActivity': activity}), 200