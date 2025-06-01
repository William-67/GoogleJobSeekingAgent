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

# 初始化AI Agent
agent = None

# @app.before_first_request
@app.before_request
def initialize_agent():

    app.before_request_funcs[None].remove(initialize_agent)
    global agent
    # api_key = os.getenv('OPENAI_API_KEY')
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("警告: 未设置OPENAI_API_KEY环境变量")
        api_key = "demo-key"  # 用于演示
    agent = JobSeekingAgent(api_key)

# initialize_agent()

@app.route('/')
def index():
    """返回Web界面"""
    with open('web_interface.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': '消息不能为空'}), 400
        
        # 调用AI Agent
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
    """处理简历上传和分析"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        if file and file.filename.lower().endswith('.pdf'):
            # 保存临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                file.save(temp_file.name)
                # 分析简历
                result = agent.upload_resume(temp_file.name)
                
                # 删除临时文件
                # os.unlink(temp_file.name)
 
                return jsonify({
                    'success': True,
                    'analysis': result['analysis'],
                    'timestamp': datetime.now().isoformat()
                })
        else:
            return jsonify({'error': '只支持PDF格式'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search_jobs', methods=['POST'])
def search_jobs():
    """搜索职位"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        location = data.get('location', '')
        
        if not query:
            return jsonify({'error': '搜索关键词不能为空'}), 400
        
        # 搜索职位
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
    """职位匹配"""
    try:
        data = request.get_json()
        resume_content = data.get('resume_content', '')
        
        if not resume_content:
            return jsonify({'error': '简历内容不能为空'}), 400
        
        # 进行职位匹配
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
    """面试准备"""
    try:
        data = request.get_json()
        company = data.get('company', '')
        position = data.get('position', '')
        
        if not company or not position:
            return jsonify({'error': '公司和职位信息不能为空'}), 400
        
        # 准备面试材料
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
    """跟踪求职申请"""
    try:
        # 查看申请状态
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
    """获取简历优化建议"""
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
    """薪资分析"""
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

# 错误处理
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': '文件太大，请上传小于16MB的文件'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    # 确保必要的目录存在
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # 启动应用
    app.config['DEBUG'] = True
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"启动AI求职助手服务器，访问地址: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
