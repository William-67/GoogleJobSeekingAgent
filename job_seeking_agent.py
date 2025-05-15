from dotenv import load_dotenv
import os
import json
import sqlite3
from datetime import datetime
import google.generativeai as genai

class JobSeekingAgent:
    def __init__(self, gemini_api_key):
        load_dotenv()
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash-001")
        self.setup_database()

    def setup_database(self):
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY,
                content TEXT,
                analysis TEXT,
                created_at TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_positions (
                id INTEGER PRIMARY KEY,
                title TEXT,
                company TEXT,
                location TEXT,
                description TEXT,
                requirements TEXT,
                applied INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _ask_gemini(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def upload_resume(self, file_path):
        import fitz  # PyMuPDF
        with fitz.open(file_path) as doc:
            text = "\n".join(page.get_text() for page in doc)
        analysis = self.analyze_resume(text)
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO resumes (content, analysis, created_at)
            VALUES (?, ?, ?)
        ''', (text, analysis, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return {"status": "success", "analysis": analysis}

    def analyze_resume(self, resume_content):
        prompt = f"""
你是一位资深HR，请分析以下简历内容并提出优化建议：

简历内容：
{resume_content}

请从以下方面进行分析：
1. 简历结构与排版
2. 技能匹配程度
3. 工作经历描述
4. 教育背景
5. 建议补充内容
6. 具体优化建议
        """
        return self._ask_gemini(prompt)

    def search_jobs(self, query):
        mock_jobs = [
            {
                "title": f"{query} 工程师",
                "company": "科技公司A",
                "location": "北京",
                "description": f"负责{query}相关开发",
                "requirements": "熟练掌握相关技能，有3年经验"
            },
            {
                "title": f"高级{query}开发工程师",
                "company": "科技公司B",
                "location": "上海",
                "description": f"参与{query}系统设计与开发",
                "requirements": "本科以上学历，5年以上经验"
            }
        ]
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        for job in mock_jobs:
            cursor.execute('''
                INSERT INTO job_positions (title, company, location, description, requirements, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (job["title"], job["company"], job["location"], job["description"], job["requirements"], datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return json.dumps(mock_jobs, ensure_ascii=False)

    def match_jobs(self, resume_content):
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM job_positions ORDER BY created_at DESC LIMIT 10')
        jobs = cursor.fetchall()
        conn.close()

        if not jobs:
            return "暂无职位数据，请先搜索职位。"

        jobs_text = "\n".join([f"{job[1]} at {job[2]}: {job[4]}" for job in jobs])
        prompt = f"""
以下是求职者简历内容和职位信息，请匹配出最合适的3个岗位并说明匹配理由：

简历内容：
{resume_content}

职位列表：
{jobs_text}
        """
        return self._ask_gemini(prompt)

    def prepare_interview(self, company_and_position):
        prompt = f"""
请为我准备以下职位的面试建议：{company_and_position}

内容包括：
1. 公司背景调研
2. 可能面试问题（技术+行为）
3. 建议准备的项目案例
4. 提问建议
5. 注意事项
        """
        return self._ask_gemini(prompt)

    def track_application(self, action):
        if action != "view":
            return "暂不支持其他操作。"

        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM job_positions WHERE applied = 1')
        apps = cursor.fetchall()
        conn.close()

        if not apps:
            return "暂无申请记录。"

        return "\n".join([f"- {job[1]} at {job[2]}" for job in apps])

    def chat(self, message):
        return self._ask_gemini(message)
