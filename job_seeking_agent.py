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
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.setup_database()

    def setup_database(self):
        """Sets up the SQLite database for storing resumes and job positions."""
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
        """Sends a prompt to the Gemini model and returns the response."""
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def upload_resume(self, file_path):
        """Uploads and analyzes a resume from a PDF file."""
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
        """Analyzes the given resume content and provides optimization suggestions."""
        prompt = f"""
You are a senior HR. Please analyze the following resume content and provide optimization suggestions:

Resume Content:
{resume_content}

Please analyze from the following aspects:
1. Resume structure and formatting
2. Skill matching degree
3. Work experience description
4. Education background
5. Suggested additional content
6. Specific optimization suggestions
        """
        return self._ask_gemini(prompt)

    def search_jobs(self, query):
        """Searches for job positions based on the given query."""
        mock_jobs = [
            {
                "title": f"{query} Engineer",
                "company": "Tech Company A",
                "location": "Beijing",
                "description": f"Responsible for {query}-related development",
                "requirements": "Proficient in relevant skills, 3 years of experience"
            },
            {
                "title": f"Senior {query} Development Engineer",
                "company": "Tech Company B",
                "location": "Shanghai",
                "description": f"Participate in {query} system design and development",
                "requirements": "Bachelor's degree or above, 5+ years of experience"
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
        """Matches the resume content with available job positions."""
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM job_positions ORDER BY created_at DESC LIMIT 10')
        jobs = cursor.fetchall()
        conn.close()

        if not jobs:
            return "No job data available. Please search for jobs first."

        jobs_text = "\n".join([f"{job[1]} at {job[2]}: {job[4]}" for job in jobs])
        prompt = f"""
Below is the job seeker's resume content and job information. Please match the 3 most suitable positions and explain the reasons for the match:

Resume Content:
{resume_content}

Job List:
{jobs_text}
        """
        return self._ask_gemini(prompt)

    def prepare_interview(self, company_and_position):
        """Prepares interview advice for a given company and position."""
        prompt = f"""
Please prepare interview advice for the following position: {company_and_position}

Content includes:
1. Company background research
2. Possible interview questions (technical + behavioral)
3. Suggested project cases to prepare
4. Questions to ask
5. Important considerations
        """
        return self._ask_gemini(prompt)

    def track_application(self, action):
        """Tracks job applications."""
        if action != "view":
            return "Other operations are not supported at this time."

        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM job_positions WHERE applied = 1')
        apps = cursor.fetchall()
        conn.close()

        if not apps:
            return "No application records found."

        return "\n".join([f"- {job[1]} at {job[2]}" for job in apps])

    def chat(self, message):
        """Handles general chat messages."""
        return self._ask_gemini(message)
