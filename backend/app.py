import os
import sys
from flask import Flask, render_template, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

# Add the parent directory to the path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import blueprints and configuration (Ensure each is imported ONLY ONCE)
from backend.config import Config
from backend.routes.auth import auth_bp
from backend.routes.tasks import tasks_bp
from backend.routes.ai import ai_bp        # 💡 CLEANED: Import AI blueprint
from backend.routes.subtasks import subtask_bp
from backend.routes.reminders import reminder_bp
from backend.routes.assistant import assistant_bp
from backend.routes.analytics import analytics_bp
# Get the absolute path to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
             static_folder=os.path.join(BASE_DIR, 'frontend', 'static'),
             template_folder='templates')

app.config.from_object(Config)

# Initialize JWT
jwt = JWTManager(app)

# Enable CORS
CORS(app)

# Register blueprints (Ensure each is registered ONLY ONCE)
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(tasks_bp, url_prefix='/api')
app.register_blueprint(ai_bp, url_prefix='/api')        # 💡 CLEANED: Register AI blueprint once
app.register_blueprint(subtask_bp, url_prefix='/api')
app.register_blueprint(reminder_bp, url_prefix='/api')
app.register_blueprint(assistant_bp, url_prefix='/api')
app.register_blueprint(analytics_bp, url_prefix='/api')
@app.route('/')
def index():
    return render_template('tasks/dashboard.html')

@app.route('/signup')
def signup():
    return render_template('auth/signup.html')

@app.route('/login')
def login():
    return render_template('auth/login.html')

@app.route('/tasks')
def tasks():
    return render_template('tasks/task_list.html')

@app.route('/tasks/new')
def new_task():
    return render_template('tasks/task_form.html')

@app.route('/tasks/<task_id>/edit')
def edit_task(task_id):
    return render_template('tasks/task_form.html', task_id=task_id)

@app.route('/tasks/alerts')
def alerts():
    return render_template('tasks/alerts.html')

@app.route('/ai-features')
def ai_features():
    return render_template('tasks/ai_features.html')

@app.route('/tasks/summarization')
def task_summarization():
    return render_template('tasks/task_summarization.html')
    
@app.route('/tasks/subtask-generation')
def task_subtask_generation():
    return render_template('tasks/task_subtask_generation.html')

@app.route('/reminders')
def reminders():
    return render_template('tasks/reminders.html')

@app.route('/tasks/prioritization')
def task_prioritization():
    return render_template('tasks/prioritization.html')

@app.route('/assistant')
def assistant():
    return render_template('tasks/assistant.html')

@app.route('/analytics')
def analytics():
    return render_template('tasks/analytics_dashboard.html') # 💡 NOTE NEW FILENAME

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True)