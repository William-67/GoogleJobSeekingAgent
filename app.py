from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import json
from datetime import datetime
import sqlite3
from werkzeug.utils import secure_filename
import tempfile
from job_seeking_agent import JobSeekingAgent

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize AI Agent
agent = None

# @app.before_first_request
@app.before_request
def initialize_agent():
    """Initializes the AI agent before the first request."""
    app.before_request_funcs[None].remove(initialize_agent)
    global agent
    # api_key = os.getenv('OPENAI_API_KEY')
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Warning: GEMINI_API_KEY environment variable not set")
        api_key = "demo-key"  # For demonstration purposes
    agent = JobSeekingAgent(api_key)

# initialize_agent()

@app.route('/')
def index():
    """Returns the web interface."""
    with open('web_interface.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handles chat requests."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Call AI Agent
        response = agent.chat(message)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload_resume', methods=['POST'])
def upload_resume():
    """Handles resume upload and analysis."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.lower().endswith('.pdf'):
            # Save temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                file.save(temp_file.name)
                # Analyze resume
                result = agent.upload_resume(temp_file.name)
                
                # Delete temporary file
                # os.unlink(temp_file.name)
 
                return jsonify({
                    'success': True,
                    'analysis': result['analysis'],
                    'timestamp': datetime.now().isoformat()
                })
        else:
            return jsonify({'error': 'Only PDF format is supported'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search_jobs', methods=['POST'])
def search_jobs():
    """Searches for jobs."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        location = data.get('location', '')
        
        if not query:
            return jsonify({'error': 'Search query cannot be empty'}), 400
        
        # Search for jobs
        results = agent.search_jobs(f"{query} {location}".strip())
        
        return jsonify({
            'success': True,
            'results': json.loads(results),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/match_jobs', methods=['POST'])
def match_jobs():
    """Matches jobs."""
    try:
        data = request.get_json()
        resume_content = data.get('resume_content', '')
        
        if not resume_content:
            return jsonify({'error': 'Resume content cannot be empty'}), 400
        
        # Perform job matching
        matches = agent.match_jobs(resume_content)
        
        return jsonify({
            'success': True,
            'matches': matches,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prepare_interview', methods=['POST'])
def prepare_interview():
    """Prepares for an interview."""
    try:
        data = request.get_json()
        company = data.get('company', '')
        position = data.get('position', '')
        
        if not company or not position:
            return jsonify({'error': 'Company and position information cannot be empty'}), 400
        
        # Prepare interview materials
        preparation = agent.prepare_interview(f"{position} at {company}")
        
        return jsonify({
            'success': True,
            'preparation': preparation,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/track_applications', methods=['GET'])
def track_applications():
    """Tracks job applications."""
    try:
        # View application status
        status = agent.track_application("view")
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_resume_suggestions', methods=['POST'])
def get_resume_suggestions():
    """Gets resume optimization suggestions."""
    try:
        data = request.get_json()
        target_position = data.get('target_position', '')
        current_resume = data.get('current_resume', '')
        
        suggestions = agent.get_resume_suggestions(current_resume, target_position)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/salary_analysis', methods=['POST'])
def salary_analysis():
    """Analyzes salary."""
    try:
        data = request.get_json()
        position = data.get('position', '')
        location = data.get('location', '')
        experience = data.get('experience', 0)
        
        analysis = agent.analyze_salary(position, location, experience)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handling
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large, please upload a file smaller than 16MB'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure necessary directories exist
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Start the application
    app.config['DEBUG'] = True
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting AI Job Seeking Assistant server: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
